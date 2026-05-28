"""
Supervisor agent — decides which data domains are needed to answer the question.
Returns selected_domains and a query_intent summary.
"""
from pydantic import BaseModel, field_validator

from app.agents.state import AgentState, ALL_DOMAINS
from app.agents.llm import get_llm

_SUPERVISOR_PROMPT = """You are the routing agent for a Finnish Marine Traffic Intelligence system.

Given the user's question, select which data domains are needed to answer it.

Available domains:
- "ais"        : AIS vessel positions, vessel count, speed, course, density
- "port"       : Port calls, arrivals, departures, port schedules
- "sea_state"  : Sea conditions (NOTE: only MQTT — REST data unavailable)
- "aton"       : AtoN faults — broken buoys, unlit beacons, navigation aid failures
- "winter"     : Winter navigation, icebreaker activity, ice dirways

Question: {question}

Return JSON with:
- "domains": list of relevant domain names (can be multiple)
- "intent": one sentence describing what the user wants to know"""


class _SupervisorResult(BaseModel):
    domains: list[str]
    intent: str

    @field_validator("domains")
    @classmethod
    def validate_domains(cls, v: list[str]) -> list[str]:
        return [d for d in v if d in ALL_DOMAINS] or ["ais"]


async def supervisor_node(state: AgentState) -> dict:
    llm = get_llm().with_structured_output(_SupervisorResult)
    result: _SupervisorResult = await llm.ainvoke(
        _SUPERVISOR_PROMPT.format(question=state["question"])
    )
    return {
        "selected_domains": result.domains,
        "query_intent": result.intent,
    }
