"""
Domain dispatcher node — runs all selected domain agents in parallel.
Each domain agent returns (summary_str, viz_dict). Results are stored in state.
"""
import asyncio
import logging

from app.agents.state import AgentState
from app.agents.domains import ais, port_call, sea_state, aton, winter

logger = logging.getLogger(__name__)

_DOMAIN_MAP = {
    "ais":       ais.fetch_and_summarize,
    "port":      port_call.fetch_and_summarize,
    "sea_state": sea_state.fetch_and_summarize,
    "aton":      aton.fetch_and_summarize,
    "winter":    winter.fetch_and_summarize,
}

_SUMMARY_KEYS = {
    "ais":       "ais_summary",
    "port":      "port_summary",
    "sea_state": "sea_state_summary",
    "aton":      "aton_summary",
    "winter":    "winter_summary",
}

_VIZ_KEYS = {
    "ais":   "ais_viz",
    "port":  "port_viz",
    "aton":  "aton_viz",
    "winter": "winter_viz",
}


async def fetch_domains_node(state: AgentState) -> dict:
    selected = state.get("selected_domains", [])
    errors: list[str] = list(state.get("errors") or [])
    updates: dict = {}

    async def _fetch(domain: str):
        fn = _DOMAIN_MAP.get(domain)
        if fn is None:
            return domain, None, None
        try:
            summary, viz = await fn()
            return domain, summary, viz
        except Exception as exc:
            logger.warning("Domain %s failed: %s", domain, exc)
            errors.append(f"{domain}: {exc}")
            return domain, f"Data unavailable for {domain}: {exc}", None

    results = await asyncio.gather(*[_fetch(d) for d in selected])

    for domain, summary, viz in results:
        summary_key = _SUMMARY_KEYS.get(domain)
        viz_key = _VIZ_KEYS.get(domain)
        if summary_key:
            updates[summary_key] = summary
        if viz_key and viz is not None:
            updates[viz_key] = viz

    updates["errors"] = errors
    return updates
