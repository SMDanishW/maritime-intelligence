import asyncio
from fastapi import APIRouter, Query

from app.services.cache import cache_get, cache_set
from app.services.digitraffic import ais_service, vessel_service

router = APIRouter()

_LIVE_KEY = "marine:vessels:live"
_DETAIL_KEY = "marine:vessels:details"


def _normalize_feature(f: dict) -> dict:
    coords = f.get("geometry", {}).get("coordinates", [None, None])
    props = f.get("properties", {})
    return {
        "mmsi": f.get("mmsi") or props.get("mmsi"),
        "lon": coords[0],
        "lat": coords[1],
        "sog": props.get("sog"),
        "cog": props.get("cog"),
        "heading": props.get("heading"),
        "nav_status": props.get("navStat"),
        "timestamp_ms": props.get("timestampExternal"),
    }


@router.get("/live")
async def get_live_vessels(limit: int = Query(500, ge=1, le=20_000, description="Max vessels to return")):
    cached = await cache_get(_LIVE_KEY)
    if cached is not None:
        vessels = cached["vessels"][:limit]
        return {**cached, "vessels": vessels, "returned": len(vessels), "cached": True}

    raw = await ais_service.get_vessel_locations()
    features = raw.get("features", [])
    vessels = [_normalize_feature(f) for f in features]

    result = {
        "total": len(vessels),
        "updated_at": raw.get("dataUpdatedTime"),
        "vessels": vessels,
    }
    await cache_set(_LIVE_KEY, result)

    sliced = vessels[:limit]
    return {**result, "vessels": sliced, "returned": len(sliced), "cached": False}


@router.get("/details")
async def get_vessel_details():
    cached = await cache_get(_DETAIL_KEY)
    if cached is not None:
        return {**cached, "cached": True}

    raw = await vessel_service.get_vessel_details()
    vessels = raw if isinstance(raw, list) else []

    result = {"total": len(vessels), "vessels": vessels}
    await cache_set(_DETAIL_KEY, result)
    return {**result, "cached": False}
