from fastapi import APIRouter

from app.services.cache import cache_get, cache_set
from app.services.digitraffic import aton_fault_service

router = APIRouter()

_FAULTS_KEY = "marine:aton:faults"


def _normalize_fault(f: dict) -> dict:
    props = f.get("properties", {})
    coords = (f.get("geometry") or {}).get("coordinates", [None, None])
    return {
        "id": props.get("id"),
        "aton_id": props.get("aton_id"),
        "aton_name": props.get("aton_name_fi") or props.get("aton_name_sv"),
        "aton_type": props.get("aton_type"),
        "fault_type": props.get("type"),
        "state": props.get("state"),
        "fixed": props.get("fixed", False),
        "lon": coords[0] if coords else None,
        "lat": coords[1] if coords else None,
        "fairway_name": props.get("fairway_name_fi"),
        "entry_timestamp": props.get("entry_timestamp"),
        "fixed_timestamp": props.get("fixed_timestamp"),
    }


@router.get("/faults")
async def get_aton_faults():
    cached = await cache_get(_FAULTS_KEY)
    if cached is not None:
        return {**cached, "cached": True}

    raw = await aton_fault_service.get_aton_faults()
    faults = [_normalize_fault(f) for f in raw.get("features", [])]
    open_count = sum(1 for f in faults if not f["fixed"] and f["state"] == "Open")

    result = {
        "total": len(faults),
        "open_count": open_count,
        "updated_at": raw.get("lastUpdated"),
        "faults": faults,
    }
    await cache_set(_FAULTS_KEY, result)
    return {**result, "cached": False}
