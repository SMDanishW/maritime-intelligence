"""
Phase 1 service tests — hit real Digitraffic APIs.
No mocking: tests validate live API contract and response shapes.
Run: pytest tests/test_services.py -v
"""
import pytest

from app.services.digitraffic import (
    ais_service,
    vessel_service,
    port_call_service,
    aton_fault_service,
    winter_navigation_service,
    sea_state_service,
)


# ---------------------------------------------------------------------------
# AIS — GeoJSON FeatureCollection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ais_locations_shape():
    data = await ais_service.get_vessel_locations()
    assert isinstance(data, dict), "Expected GeoJSON FeatureCollection dict"
    assert "features" in data
    assert isinstance(data["features"], list)
    assert len(data["features"]) > 0, "Expected at least one vessel"


@pytest.mark.asyncio
async def test_ais_feature_has_coords_and_props():
    data = await ais_service.get_vessel_locations()
    feature = data["features"][0]
    assert "mmsi" in feature
    assert feature.get("geometry", {}).get("type") == "Point"
    coords = feature["geometry"]["coordinates"]
    assert len(coords) == 2  # [lon, lat]
    props = feature.get("properties", {})
    assert "sog" in props  # speed over ground
    assert "cog" in props  # course over ground


# ---------------------------------------------------------------------------
# Vessel details — plain list
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_vessel_details_is_list():
    data = await vessel_service.get_vessel_details()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_vessel_detail_has_identity_fields():
    data = await vessel_service.get_vessel_details()
    if not data:
        pytest.skip("Vessel details list is empty (API may return only recently-active vessels)")
    v = data[0]
    assert "mmsi" in v
    assert "name" in v


# ---------------------------------------------------------------------------
# Port calls — wrapped dict
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_port_calls_shape():
    data = await port_call_service.get_port_calls()
    assert isinstance(data, dict)
    assert "portCalls" in data
    assert isinstance(data["portCalls"], list)


@pytest.mark.asyncio
async def test_port_call_has_vessel_and_port():
    data = await port_call_service.get_port_calls()
    calls = data["portCalls"]
    if not calls:
        pytest.skip("No port calls in current API window")
    call = calls[0]
    assert "vesselName" in call
    assert "portToVisit" in call


# ---------------------------------------------------------------------------
# AtoN faults — GeoJSON FeatureCollection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_aton_faults_shape():
    data = await aton_fault_service.get_aton_faults()
    assert isinstance(data, dict)
    assert "features" in data
    assert isinstance(data["features"], list)


@pytest.mark.asyncio
async def test_aton_fault_feature_has_properties():
    data = await aton_fault_service.get_aton_faults()
    if not data["features"]:
        pytest.skip("No active AtoN faults")
    props = data["features"][0].get("properties", {})
    assert "aton_id" in props
    assert "type" in props
    assert "state" in props


# ---------------------------------------------------------------------------
# Winter navigation — v2
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_winter_vessels_shape():
    data = await winter_navigation_service.get_vessels()
    assert isinstance(data, dict)
    assert "vessels" in data
    assert isinstance(data["vessels"], list)


@pytest.mark.asyncio
async def test_winter_dirways_is_geojson():
    data = await winter_navigation_service.get_dirways()
    assert isinstance(data, dict)
    assert "features" in data
    # 0 features is valid outside winter season


# ---------------------------------------------------------------------------
# Sea state — MQTT-only, service returns structured placeholder
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sea_state_returns_placeholder():
    data = await sea_state_service.get_sea_state()
    assert isinstance(data, dict)
    assert data["available"] is False
    assert "mqtt_broker" in data
