import asyncio
from fastapi import APIRouter

from app.services.cache import cache_get, cache_set
from app.services.digitraffic import winter_navigation_service

router = APIRouter()

_WN_KEY = "marine:winter:navigation"


def _normalize_vessel(v: dict) -> dict:
    activities = v.get("activities", [])
    current = activities[0] if activities else None
    active = current is not None and current.get("type") != "STOP"
    return {
        "name": v.get("name"),
        "mmsi": v.get("mmsi"),
        "imo": v.get("imo"),
        "call_sign": v.get("callSign"),
        "shortcode": v.get("shortcode"),
        "type": v.get("type"),
        "active": active,
        "current_activity": current.get("type") if current else None,
        "activity_end_time": current.get("endTime") if current else None,
        "planned_assistances": len(v.get("plannedAssistances", [])),
    }


@router.get("")
async def get_winter_navigation():
    cached = await cache_get(_WN_KEY)
    if cached is not None:
        return {**cached, "cached": True}

    vessels_raw, dirways_raw = await asyncio.gather(
        winter_navigation_service.get_vessels(),
        winter_navigation_service.get_dirways(),
    )

    vessels = [_normalize_vessel(v) for v in vessels_raw.get("vessels", [])]
    dirways = dirways_raw.get("features", [])
    active_count = sum(1 for v in vessels if v["active"])

    result = {
        "active_dirways": len(dirways),
        "active_vessels": active_count,
        "total_vessels": len(vessels),
        "vessels": vessels,
        "updated_at": vessels_raw.get("lastUpdated"),
    }
    await cache_set(_WN_KEY, result)
    return {**result, "cached": False}
