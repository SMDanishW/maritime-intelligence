from fastapi import APIRouter

from app.services.cache import cache_get, cache_set
from app.services.digitraffic import port_call_service

router = APIRouter()

_CALLS_KEY = "marine:ports:calls"


def _normalize_call(c: dict) -> dict:
    areas = c.get("portAreaDetails", [])
    first = areas[0] if areas else {}
    return {
        "port_call_id": c.get("portCallId"),
        "vessel_name": c.get("vesselName"),
        "mmsi": c.get("mmsi"),
        "imo": c.get("imoLloyds"),
        "port_to_visit": c.get("portToVisit"),
        "nationality": c.get("nationality"),
        "vessel_type_code": c.get("vesselTypeCode"),
        "radio_call_sign": c.get("radioCallSign"),
        "arrival_time": first.get("ata") or first.get("eta"),
        "departure_time": first.get("atd") or first.get("etd"),
        "port_area_name": first.get("portAreaName"),
        "berth_name": first.get("berthName"),
    }


@router.get("/calls")
async def get_port_calls():
    cached = await cache_get(_CALLS_KEY)
    if cached is not None:
        return {**cached, "cached": True}

    raw = await port_call_service.get_port_calls()
    calls = [_normalize_call(c) for c in raw.get("portCalls", [])]

    result = {
        "total": len(calls),
        "updated_at": raw.get("dataUpdatedTime"),
        "calls": calls,
    }
    await cache_set(_CALLS_KEY, result)
    return {**result, "cached": False}
