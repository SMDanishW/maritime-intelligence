import asyncio
from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.services.cache import cache_get, cache_set
from app.services.digitraffic import ais_service, port_call_service, aton_fault_service, winter_navigation_service
from app.services.risk_service import compute_risk, RiskComponents

router = APIRouter()

_DASH_KEY = "marine:dashboard:summary"


@router.get("/summary")
async def get_dashboard_summary():
    cached = await cache_get(_DASH_KEY)
    if cached is not None:
        return {**cached, "cached": True}

    ais_raw, port_raw, aton_raw, wn_raw, dirways_raw = await asyncio.gather(
        ais_service.get_vessel_locations(),
        port_call_service.get_port_calls(),
        aton_fault_service.get_aton_faults(),
        winter_navigation_service.get_vessels(),
        winter_navigation_service.get_dirways(),
    )

    # ── Vessels ───────────────────────────────────────────────────────────────
    ais_features = ais_raw.get("features", [])
    sample_vessels = []
    nav_status_counts: dict[str, int] = {}
    for f in ais_features:
        coords = (f.get("geometry") or {}).get("coordinates", [None, None])
        props = f.get("properties", {})
        nav_stat = str(props.get("navStat", "15"))
        nav_status_counts[nav_stat] = nav_status_counts.get(nav_stat, 0) + 1
        if len(sample_vessels) < 500 and coords[0] is not None and coords[1] is not None:
            sample_vessels.append({
                "mmsi": f.get("mmsi") or props.get("mmsi"),
                "lat": coords[1],
                "lon": coords[0],
                "sog": props.get("sog", 0),
                "heading": props.get("heading", 0),
                "nav_status": nav_stat,
            })

    # ── Port calls ────────────────────────────────────────────────────────────
    port_calls = port_raw.get("portCalls", [])
    port_counts = Counter(c.get("portToVisit", "UNKNOWN") for c in port_calls)
    recent_calls = []
    for c in port_calls[:50]:
        areas = c.get("portAreaDetails", [])
        first = areas[0] if areas else {}
        recent_calls.append({
            "vessel_name": c.get("vesselName"),
            "port": c.get("portToVisit"),
            "arrival_time": first.get("ata") or first.get("eta"),
            "departure_time": first.get("atd") or first.get("etd"),
        })

    # ── AtoN faults ───────────────────────────────────────────────────────────
    aton_features = aton_raw.get("features", [])
    faults = []
    fault_type_counts: dict[str, int] = {}
    open_fault_count = 0
    for f in aton_features:
        props = f.get("properties", {})
        coords = (f.get("geometry") or {}).get("coordinates", [None, None])
        fault_type = props.get("type") or "Unknown"
        state = props.get("state", "Unknown")
        fixed = bool(props.get("fixed", False))
        if not fixed and state == "Open":
            open_fault_count += 1
        fault_type_counts[fault_type] = fault_type_counts.get(fault_type, 0) + 1
        if coords[0] is not None and coords[1] is not None:
            faults.append({
                "aton_id": props.get("aton_id") or props.get("id"),
                "aton_name": props.get("aton_name_fi") or props.get("aton_name_sv") or "Unknown",
                "state": state,
                "lat": coords[1],
                "lon": coords[0],
                "fault_type": fault_type,
                "aton_type": props.get("aton_type") or "Unknown",
                "fixed": fixed,
            })

    # ── Winter navigation ─────────────────────────────────────────────────────
    wn_vessels_raw = wn_raw.get("vessels", [])
    wn_vessels = []
    active_icebreakers = 0
    for v in wn_vessels_raw:
        activities = v.get("activities", [])
        current = activities[0] if activities else None
        active = current is not None and current.get("type") != "STOP"
        if active:
            active_icebreakers += 1
        wn_vessels.append({
            "name": v.get("name") or "Unknown",
            "mmsi": v.get("mmsi"),
            "vessel_type_code": v.get("vesselTypeCode") or 0,
            "active": active,
            "current_activity": current.get("type") if current else None,
        })
    active_dirways = len(dirways_raw.get("features", []))

    # ── Risk ──────────────────────────────────────────────────────────────────
    components = RiskComponents(
        vessel_count=len(ais_features),
        port_call_count=len(port_calls),
        open_aton_faults=open_fault_count,
        active_winter_assistances=active_icebreakers,
        active_dirways=active_dirways,
    )
    weights = {
        "vessel_density":    settings.risk_weight_vessel_density,
        "port_congestion":   settings.risk_weight_port_congestion,
        "sea_state":         settings.risk_weight_sea_state,
        "aton_faults":       settings.risk_weight_aton_faults,
        "winter_navigation": settings.risk_weight_winter_navigation,
    }
    risk = compute_risk(components, weights)

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vessels": {
            "total": len(ais_features),
            "by_nav_status": nav_status_counts,
            "sample": sample_vessels,
            "updated_at": ais_raw.get("dataUpdatedTime"),
        },
        "port_calls": {
            "total": len(port_calls),
            "by_port": dict(port_counts.most_common(20)),
            "recent": recent_calls,
            "updated_at": port_raw.get("dataUpdatedTime"),
        },
        "aton_faults": {
            "total": len(aton_features),
            "open": open_fault_count,
            "by_type": fault_type_counts,
            "faults": faults,
            "updated_at": aton_raw.get("lastUpdated"),
        },
        "winter_navigation": {
            "vessels": wn_vessels,
            "active_dirways": active_dirways,
            "active_icebreakers": active_icebreakers,
            "updated_at": wn_raw.get("lastUpdated"),
        },
        "sea_state": {
            "available": False,
            "reason": "Sea state measurements are only available via Digitraffic MQTT stream.",
            "mqtt_broker": "wss://meri.digitraffic.fi/mqtt",
            "topic_pattern": "meri-aton/#",
        },
        "risk": risk,
    }

    await cache_set(_DASH_KEY, result)
    return {**result, "cached": False}
