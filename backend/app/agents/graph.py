"""
LangGraph StateGraph for the Finnish Marine Traffic Intelligence agent.

Flow:
  START → guardrail → [out-of-scope: END] → supervisor
        → fetch_domains → risk_agent → visualization → response_writer → END
"""
from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.guardrail import guardrail_node
from app.agents.supervisor import supervisor_node
from app.agents.fetch_domains import fetch_domains_node
from app.agents.risk_agent import risk_agent_node
from app.agents.visualization import visualization_node
from app.agents.response_writer import response_writer_node


def _route_after_guardrail(state: AgentState) -> str:
    return "supervisor" if state.get("in_scope") else END


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("guardrail",       guardrail_node)
    graph.add_node("supervisor",      supervisor_node)
    graph.add_node("fetch_domains",   fetch_domains_node)
    graph.add_node("risk_agent",      risk_agent_node)
    graph.add_node("visualization",   visualization_node)
    graph.add_node("response_writer", response_writer_node)

    graph.add_edge(START,             "guardrail")
    graph.add_conditional_edges("guardrail", _route_after_guardrail)
    graph.add_edge("supervisor",      "fetch_domains")
    graph.add_edge("fetch_domains",   "risk_agent")
    graph.add_edge("risk_agent",      "visualization")
    graph.add_edge("visualization",   "response_writer")
    graph.add_edge("response_writer", END)

    return graph


# Compiled graph — imported by the chat route
marine_graph = build_graph().compile()
