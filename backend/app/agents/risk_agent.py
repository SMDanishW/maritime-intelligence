"""Risk scoring agent — computes risk from domain viz data already in state."""
from app.agents.state import AgentState
from app.core.config import settings
from app.services.risk_service import compute_risk, RiskComponents


async def risk_agent_node(state: AgentState) -> dict:
    ais_viz = state.get("ais_viz") or {}
    port_viz = state.get("port_viz") or {}
    aton_viz = state.get("aton_viz") or {}
    winter_viz = state.get("winter_viz") or {}

    components = RiskComponents(
        vessel_count=ais_viz.get("vessel_count", 0),
        port_call_count=port_viz.get("total", 0),
        open_aton_faults=aton_viz.get("open", 0),
        active_winter_assistances=sum(
            1 for v in winter_viz.get("vessels", []) if v.get("active")
        ),
        active_dirways=winter_viz.get("active_dirways", 0),
    )

    weights = {
        "vessel_density":    settings.risk_weight_vessel_density,
        "port_congestion":   settings.risk_weight_port_congestion,
        "sea_state":         settings.risk_weight_sea_state,
        "aton_faults":       settings.risk_weight_aton_faults,
        "winter_navigation": settings.risk_weight_winter_navigation,
    }

    risk = compute_risk(components, weights)
    return {
        "risk_score":      risk["score"],
        "risk_level":      risk["level"],
        "risk_components": risk["components"],
    }
