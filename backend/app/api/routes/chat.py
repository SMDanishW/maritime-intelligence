from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.state import REFUSAL_MESSAGE

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class AgentTrace(BaseModel):
    node: str
    output: dict[str, Any]


class ChatResponse(BaseModel):
    answer: str
    in_scope: bool
    risk: dict | None = None
    map_data: dict | None = None
    chart_data: dict | None = None
    table_data: list | None = None
    errors: list[str] | None = None
    trace: list[AgentTrace] | None = None


def _sanitize(value: Any, max_list: int = 5, max_str: int = 400) -> Any:
    """Truncate large values so trace stays readable in the developer view."""
    if isinstance(value, list):
        clipped = [_sanitize(v, max_list, max_str) for v in value[:max_list]]
        if len(value) > max_list:
            clipped.append(f"…({len(value) - max_list} more items)")
        return clipped
    if isinstance(value, dict):
        return {k: _sanitize(v, max_list, max_str) for k, v in value.items()}
    if isinstance(value, str) and len(value) > max_str:
        return value[:max_str] + f"…({len(value) - max_str} more chars)"
    return value


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    from app.agents.graph import marine_graph

    trace: list[AgentTrace] = []
    state: dict[str, Any] = {}

    try:
        async for chunk in marine_graph.astream(
            {"question": request.message, "session_id": request.session_id, "errors": []},
            stream_mode="updates",
        ):
            for node_name, node_output in chunk.items():
                trace.append(AgentTrace(node=node_name, output=_sanitize(node_output)))
                state.update(node_output)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}")

    if not state.get("in_scope"):
        return ChatResponse(in_scope=False, answer=REFUSAL_MESSAGE, trace=trace)

    risk = None
    if state.get("risk_score") is not None:
        risk = {
            "score": state["risk_score"],
            "level": state["risk_level"],
            "components": state.get("risk_components", []),
        }

    return ChatResponse(
        in_scope=True,
        answer=state.get("answer") or "I was unable to generate a response.",
        risk=risk,
        map_data=state.get("map_data"),
        chart_data=state.get("chart_data"),
        table_data=state.get("table_data"),
        errors=state.get("errors") or None,
        trace=trace,
    )
