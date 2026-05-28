import asyncio
from fastapi import APIRouter

from app.core.config import settings
from app.services.cache import cache_get, cache_set
from app.services.digitraffic import ais_service, port_call_service, aton_fault_service, winter_navigation_service
from app.services.risk_service import compute_risk, RiskComponents

router = APIRouter()

_RISK_KEY = "marine:risk:summary"


@router.get("/summary")
async def get_risk_summary():
    cached = await cache_get(_RISK_KEY)
    if cached is not None:
        return {**cached, "cached": True}

    ais_raw, port_raw, aton_raw, wn_raw, dirways_raw = await asyncio.gather(
        ais_service.get_vessel_locations(),
        port_call_service.get_port_calls(),
        aton_fault_service.get_aton_faults(),
        winter_navigation_service.get_vessels(),
        winter_navigation_service.get_dirways(),
    )

    aton_features = aton_raw.get("features", [])
    wn_vessels = wn_raw.get("vessels", [])

    components = RiskComponents(
        vessel_count=len(ais_raw.get("features", [])),
        port_call_count=len(port_raw.get("portCalls", [])),
        open_aton_faults=sum(
            1 for f in aton_features
            if not f.get("properties", {}).get("fixed") and f.get("properties", {}).get("state") == "Open"
        ),
        active_winter_assistances=sum(
            1 for v in wn_vessels
            if v.get("activities") and v["activities"][0].get("type") != "STOP"
        ),
        active_dirways=len(dirways_raw.get("features", [])),
    )

    weights = {
        "vessel_density":    settings.risk_weight_vessel_density,
        "port_congestion":   settings.risk_weight_port_congestion,
        "sea_state":         settings.risk_weight_sea_state,
        "aton_faults":       settings.risk_weight_aton_faults,
        "winter_navigation": settings.risk_weight_winter_navigation,
    }

    result = compute_risk(components, weights)
    await cache_set(_RISK_KEY, result)
    return {**result, "cached": False}
