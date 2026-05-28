"""
Guardrail agent — determines whether the user question is within scope.

Strategy:
  1. Keyword fast-path for obvious marine topics (no LLM call needed).
  2. Keyword fast-path for obvious off-topic queries.
  3. LLM classification for edge cases.

The refusal message is always a fixed string — never LLM-generated.
"""
from pydantic import BaseModel

from app.agents.state import AgentState
from app.agents.llm import get_llm

# Unambiguously marine single words — matched at word boundaries only (no substring)
_MARINE_WORDS = {
    "vessel", "vessels", "ship", "ships", "boat", "boats", "ferry", "ferries",
    "cargo", "tanker", "tankers", "fleet", "tug", "tugboat",
    "ais", "mmsi", "maritime", "nautical",
    "harbour", "harbours", "harbor", "harbors", "berth", "berths",
    "fairway", "fairways", "waterway", "buoy", "buoys", "beacon", "beacons",
    "aton", "icebreaker", "icebreakers", "ibnet", "dirway", "dirways",
    "digitraffic", "fintraffic",
    "sog", "cog", "navstat",
    "portcall", "portcalls",
}

# Multi-word marine phrases — substring matched against the full question
_MARINE_PHRASES = {
    "port call", "port calls", "aids to navigation",
    "winter navigation", "ice navigation",
    "gulf of finland", "finnish waters", "finnish ports",
    "sea state", "wave height", "wave conditions",
    "vessel traffic", "marine traffic",
    "aton fault", "aton faults", "navigation aid",
}

# Unambiguously off-topic — matched at word boundaries only
_OUTOFSCOPE_WORDS = {
    "election", "elections", "parliament", "president", "chancellor",
    "bitcoin", "ethereum", "crypto", "cryptocurrency", "forex", "nasdaq",
    "symptoms", "diagnosis", "treatment", "prescription", "hospital",
    "highway", "motorway", "railway", "tram", "metro",
    "recipe", "ingredient", "restaurant", "cookbook",
    "joke", "poem", "lyrics", "chess",
    "debug", "programming", "javascript", "python",
}

_CLASSIFY_PROMPT = """You are a scope classifier for a Finnish marine traffic assistant.

Answer ONLY with JSON: {{"in_scope": true}} or {{"in_scope": false}}

The assistant can answer questions about:
- Finnish vessel AIS positions and movements
- Port calls and schedules in Finnish ports
- Sea state and wave conditions
- AtoN (Aids to Navigation) faults
- Winter navigation and icebreaker activity
- Marine traffic risk in Finnish waters

Question: {question}"""


class _ScopeResult(BaseModel):
    in_scope: bool


def _word_tokens(text: str) -> set[str]:
    """Lowercase word tokens, stripping punctuation at word edges."""
    import re
    return set(re.sub(r"[^\w]", " ", text.lower()).split())


async def guardrail_node(state: AgentState) -> dict:
    question = state["question"]
    q_lower = question.lower()
    tokens = _word_tokens(q_lower)

    # Fast-path IN-SCOPE: unambiguous marine single words (word-boundary only)
    if tokens & _MARINE_WORDS:
        return {"in_scope": True}

    # Fast-path IN-SCOPE: multi-word marine phrases (substring is safe here)
    if any(phrase in q_lower for phrase in _MARINE_PHRASES):
        return {"in_scope": True}

    # Fast-path OUT-OF-SCOPE: unambiguous off-topic words (word-boundary only)
    if tokens & _OUTOFSCOPE_WORDS:
        return {"in_scope": False}

    # Edge case — LLM classification
    llm = get_llm().with_structured_output(_ScopeResult)
    result: _ScopeResult = await llm.ainvoke(_CLASSIFY_PROMPT.format(question=question))
    return {"in_scope": result.in_scope}
