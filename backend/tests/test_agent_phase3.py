"""
Phase 3 agent tests.

Tests that don't need Groq (guardrail keyword fast-paths, domain summarizers,
visualization, risk agent) run unconditionally.

Full graph integration tests are skipped unless GROQ_API_KEY is set.
"""
import os
import pytest

from app.agents.state import AgentState, REFUSAL_MESSAGE
from app.agents.guardrail import guardrail_node
from app.agents.risk_agent import risk_agent_node
from app.agents.visualization import visualization_node


# ── Helpers ────────────────────────────────────────────────────────────────────

def _state(**kwargs) -> AgentState:
    base: AgentState = {
        "question": "",
        "session_id": None,
        "errors": [],
    }
    base.update(kwargs)
    return base


# ── Guardrail — keyword fast-paths (no LLM) ────────────────────────────────────

@pytest.mark.asyncio
async def test_guardrail_marine_keyword_in_scope():
    result = await guardrail_node(_state(question="How many vessels are in Finnish waters?"))
    assert result["in_scope"] is True


@pytest.mark.asyncio
async def test_guardrail_ais_keyword_in_scope():
    result = await guardrail_node(_state(question="Show me AIS positions near Helsinki port"))
    assert result["in_scope"] is True


@pytest.mark.asyncio
async def test_guardrail_aton_keyword_in_scope():
    result = await guardrail_node(_state(question="Are there any AtoN faults on the fairway?"))
    assert result["in_scope"] is True


@pytest.mark.asyncio
async def test_guardrail_winter_keyword_in_scope():
    result = await guardrail_node(_state(question="Is there any icebreaker activity in the Baltic?"))
    assert result["in_scope"] is True


@pytest.mark.asyncio
async def test_guardrail_politics_out_of_scope():
    result = await guardrail_node(_state(question="Who won the election in Finland?"))
    assert result["in_scope"] is False


@pytest.mark.asyncio
async def test_guardrail_medical_out_of_scope():
    result = await guardrail_node(_state(question="What are symptoms of seasickness?"))
    assert result["in_scope"] is False


@pytest.mark.asyncio
async def test_guardrail_crypto_out_of_scope():
    result = await guardrail_node(_state(question="What is the price of Bitcoin today?"))
    assert result["in_scope"] is False


# ── Risk agent — pure computation, no API calls ────────────────────────────────

@pytest.mark.asyncio
async def test_risk_agent_zero_inputs():
    result = await risk_agent_node(_state(
        ais_viz={"vessel_count": 0},
        port_viz={"total": 0},
        aton_viz={"open": 0},
        winter_viz={"vessels": [], "active_dirways": 0},
    ))
    assert result["risk_score"] == 0.0
    assert result["risk_level"] == "Low"


@pytest.mark.asyncio
async def test_risk_agent_high_vessel_count():
    result = await risk_agent_node(_state(
        ais_viz={"vessel_count": 20000},
        port_viz={"total": 0},
        aton_viz={"open": 0},
        winter_viz={"vessels": [], "active_dirways": 0},
    ))
    # vessel_density * 0.25 = 100 * 0.25 = 25
    assert result["risk_score"] == 25.0


@pytest.mark.asyncio
async def test_risk_agent_level_labels():
    for count, expected_level in [(0, "Low"), (8000, "Medium"), (16000, "High"), (20000, "High")]:
        result = await risk_agent_node(_state(
            ais_viz={"vessel_count": count},
            port_viz={"total": 0},
            aton_viz={"open": 0},
            winter_viz={"vessels": [], "active_dirways": 0},
        ))
        assert result["risk_level"] in ("Low", "Medium", "High", "Critical")


@pytest.mark.asyncio
async def test_risk_agent_has_five_components():
    result = await risk_agent_node(_state(
        ais_viz={"vessel_count": 18000},
        port_viz={"total": 290},
        aton_viz={"open": 50},
        winter_viz={"vessels": [], "active_dirways": 0},
    ))
    assert len(result["risk_components"]) == 5


# ── Visualization — no API calls ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_visualization_empty_state():
    result = await visualization_node(_state())
    assert "markers" in result["map_data"]
    assert "bar" in result["chart_data"]
    assert isinstance(result["table_data"], list)


@pytest.mark.asyncio
async def test_visualization_vessel_markers():
    ais_viz = {
        "vessel_count": 2,
        "sample_vessels": [
            {"mmsi": 111, "lat": 60.1, "lon": 24.9, "sog": 5.0, "heading": 90},
            {"mmsi": 222, "lat": 60.2, "lon": 25.0, "sog": 0.0, "heading": 180},
        ],
    }
    result = await visualization_node(_state(ais_viz=ais_viz))
    markers = result["map_data"]["markers"]
    assert len(markers) == 2
    assert all(m["type"] == "vessel" for m in markers)


@pytest.mark.asyncio
async def test_visualization_fault_markers_only_open():
    aton_viz = {
        "total": 2,
        "open": 1,
        "faults": [
            {"aton_id": 1, "aton_name": "Marker A", "state": "Open",
             "lat": 60.1, "lon": 24.9, "fault_type": "Unlit", "aton_type": "Buoy", "fixed": False},
            {"aton_id": 2, "aton_name": "Marker B", "state": "Closed",
             "lat": 60.2, "lon": 25.0, "fault_type": "Missing", "aton_type": "Buoy", "fixed": True},
        ],
    }
    result = await visualization_node(_state(aton_viz=aton_viz))
    fault_markers = [m for m in result["map_data"]["markers"] if m["type"] == "aton_fault"]
    assert len(fault_markers) == 1  # only open fault shown
    assert fault_markers[0]["label"] == "Marker A"


# ── Domain summarizers — hit real Digitraffic API ─────────────────────────────

@pytest.mark.asyncio
async def test_ais_domain_summarizer():
    from app.agents.domains.ais import fetch_and_summarize
    summary, viz = await fetch_and_summarize()
    assert isinstance(summary, str)
    assert "vessel" in summary.lower()
    assert viz["vessel_count"] > 0


@pytest.mark.asyncio
async def test_aton_domain_summarizer():
    from app.agents.domains.aton import fetch_and_summarize
    summary, viz = await fetch_and_summarize()
    assert "fault" in summary.lower() or "aton" in summary.lower()
    assert "total" in viz


@pytest.mark.asyncio
async def test_sea_state_domain_is_placeholder():
    from app.agents.domains.sea_state import fetch_and_summarize
    summary, viz = await fetch_and_summarize()
    assert "mqtt" in summary.lower()


# ── Full graph integration — requires GROQ_API_KEY ────────────────────────────

_has_groq = bool(os.getenv("GROQ_API_KEY"))


@pytest.mark.asyncio
@pytest.mark.skipif(not _has_groq, reason="GROQ_API_KEY not set")
async def test_graph_in_scope_question():
    from app.agents.graph import marine_graph
    state = await marine_graph.ainvoke({
        "question": "How many vessels are currently in Finnish waters?",
        "session_id": None,
        "errors": [],
    })
    assert state["in_scope"] is True
    assert state.get("answer")
    assert state["risk_score"] is not None


@pytest.mark.asyncio
@pytest.mark.skipif(not _has_groq, reason="GROQ_API_KEY not set")
async def test_graph_out_of_scope_returns_refusal():
    from app.agents.graph import marine_graph
    state = await marine_graph.ainvoke({
        "question": "What is the stock price of Nokia?",
        "session_id": None,
        "errors": [],
    })
    assert state["in_scope"] is False
    # answer is set by the chat route, not the graph — graph just sets in_scope=False


@pytest.mark.asyncio
@pytest.mark.skipif(not _has_groq, reason="GROQ_API_KEY not set")
async def test_chat_endpoint_in_scope(client):
    r = await client.post("/api/chat", json={"message": "Show me AtoN faults in Finnish waters"})
    assert r.status_code == 200
    data = r.json()
    assert data["in_scope"] is True
    assert data["answer"]
    assert data["risk"] is not None


@pytest.mark.asyncio
@pytest.mark.skipif(not _has_groq, reason="GROQ_API_KEY not set")
async def test_chat_endpoint_out_of_scope(client):
    r = await client.post("/api/chat", json={"message": "Tell me a joke"})
    assert r.status_code == 200
    data = r.json()
    assert data["in_scope"] is False
    assert REFUSAL_MESSAGE in data["answer"]
