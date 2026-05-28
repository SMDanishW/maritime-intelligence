"""
Phase 2 route tests — runs against real Digitraffic + live Redis.
Requires: docker run -d -p 6379:6379 redis:7-alpine
Run: pytest tests/test_routes_phase2.py -v
"""
import pytest
import httpx


@pytest.fixture
async def client():
    from app.main import app
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["redis"] is True


@pytest.mark.asyncio
async def test_live_vessels_shape(client):
    r = await client.get("/api/vessels/live?limit=10")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] > 0
    assert data["returned"] <= 10
    assert len(data["vessels"]) <= 10
    v = data["vessels"][0]
    assert "mmsi" in v and "lat" in v and "lon" in v


@pytest.mark.asyncio
async def test_live_vessels_cached_second_call(client):
    await client.get("/api/vessels/live?limit=5")
    r = await client.get("/api/vessels/live?limit=5")
    assert r.json()["cached"] is True


@pytest.mark.asyncio
async def test_port_calls_shape(client):
    r = await client.get("/api/ports/calls")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert isinstance(data["calls"], list)
    if data["calls"]:
        c = data["calls"][0]
        assert "vessel_name" in c
        assert "port_to_visit" in c


@pytest.mark.asyncio
async def test_aton_faults_shape(client):
    r = await client.get("/api/aton/faults")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] > 0
    assert "open_count" in data
    f = data["faults"][0]
    assert "aton_id" in f and "state" in f


@pytest.mark.asyncio
async def test_winter_navigation_shape(client):
    r = await client.get("/api/winter-navigation")
    assert r.status_code == 200
    data = r.json()
    assert "active_dirways" in data
    assert "vessels" in data
    assert isinstance(data["vessels"], list)


@pytest.mark.asyncio
async def test_sea_state_placeholder(client):
    r = await client.get("/api/sea-state")
    assert r.status_code == 200
    assert r.json()["available"] is False


@pytest.mark.asyncio
async def test_risk_summary_shape(client):
    r = await client.get("/api/risk/summary")
    assert r.status_code == 200
    data = r.json()
    assert 0 <= data["score"] <= 100
    assert data["level"] in ("Low", "Medium", "High", "Critical")
    assert len(data["components"]) == 5


@pytest.mark.asyncio
async def test_dashboard_summary_shape(client):
    r = await client.get("/api/dashboard/summary")
    assert r.status_code == 200
    data = r.json()
    assert "vessels" in data
    assert "port_calls" in data
    assert "aton_faults" in data
    assert "winter_navigation" in data
    assert "risk" in data
    assert 0 <= data["risk"]["score"] <= 100
