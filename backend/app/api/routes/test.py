from fastapi import APIRouter, HTTPException
import httpx

from app.services.digitraffic import (
    ais_service,
    vessel_service,
    port_call_service,
    sea_state_service,
    aton_fault_service,
    winter_navigation_service,
)

router = APIRouter()


def _handle_error(exc: Exception) -> HTTPException:
    if isinstance(exc, httpx.TimeoutException):
        return HTTPException(status_code=504, detail="Digitraffic API timeout")
    if isinstance(exc, httpx.HTTPStatusError):
        return HTTPException(status_code=exc.response.status_code, detail=str(exc))
    return HTTPException(status_code=502, detail=f"Upstream error: {exc}")


@router.get("/ais")
async def test_ais():
    try:
        # Response: GeoJSON FeatureCollection {type, dataUpdatedTime, features: [{mmsi, geometry, properties}]}
        data = await ais_service.get_vessel_locations()
        features = data.get("features", []) if isinstance(data, dict) else data
        return {
            "ok": True,
            "vessel_count": len(features),
            "data_updated": data.get("dataUpdatedTime"),
            "sample": features[:3],
        }
    except Exception as exc:
        raise _handle_error(exc)


@router.get("/vessels")
async def test_vessels():
    try:
        # Response: plain list [{vesselId, mmsi, name, imoLloyds, vesselDimensions, ...}]
        data = await vessel_service.get_vessel_details()
        vessels = data if isinstance(data, list) else data.get("vessels", [])
        return {"ok": True, "vessel_count": len(vessels), "sample": vessels[:3]}
    except Exception as exc:
        raise _handle_error(exc)


@router.get("/port-calls")
async def test_port_calls():
    try:
        # Response: {dataUpdatedTime, portCalls: [{portCallId, vesselName, portToVisit, ...}]}
        data = await port_call_service.get_port_calls()
        calls = data.get("portCalls", []) if isinstance(data, dict) else data
        return {
            "ok": True,
            "record_count": len(calls),
            "data_updated": data.get("dataUpdatedTime") if isinstance(data, dict) else None,
            "sample": calls[:3],
        }
    except Exception as exc:
        raise _handle_error(exc)


@router.get("/sea-state")
async def test_sea_state():
    # Sea state is MQTT-only — no REST endpoint on Digitraffic
    data = await sea_state_service.get_sea_state()
    return {"ok": False, "available": False, "data": data}


@router.get("/aton-faults")
async def test_aton_faults():
    try:
        # Response is GeoJSON FeatureCollection: {"type", "lastUpdated", "features": [...]}
        data = await aton_fault_service.get_aton_faults()
        features = data.get("features", []) if isinstance(data, dict) else data
        return {"ok": True, "fault_count": len(features), "last_updated": data.get("lastUpdated"), "sample": features[:3]}
    except Exception as exc:
        raise _handle_error(exc)


@router.get("/winter-navigation")
async def test_winter_navigation():
    try:
        dirways = await winter_navigation_service.get_dirways()
        vessels = await winter_navigation_service.get_vessels()
        vessel_list = vessels.get("vessels", []) if isinstance(vessels, dict) else vessels
        return {
            "ok": True,
            "dirways_sample": dirways[:3] if isinstance(dirways, list) else dirways,
            "vessel_count": len(vessel_list),
            "vessels_sample": vessel_list[:3],
        }
    except Exception as exc:
        raise _handle_error(exc)
