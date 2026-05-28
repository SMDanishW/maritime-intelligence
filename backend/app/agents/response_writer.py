"""
Response writer agent — produces the final natural-language answer using Groq LLM.
Only summaries (not raw data) are passed to the LLM.
"""
from app.agents.state import AgentState
from app.agents.llm import get_llm

_WRITER_PROMPT = """You are an expert Finnish Marine Traffic Intelligence assistant.

Answer the user's question using ONLY the data summaries provided below.
Be specific — cite actual numbers from the data. Be concise (2-4 paragraphs).
Do not invent information not present in the summaries.
If a domain shows unavailable data, mention it briefly and move on.

User question: {question}

Intent understood: {intent}

--- Data summaries ---
{summaries}

Risk assessment: {risk_score}/100 — {risk_level}

Write your response now:"""


async def response_writer_node(state: AgentState) -> dict:
    domain_labels = {
        "ais_summary":       "AIS Vessel Data",
        "port_summary":      "Port Calls",
        "sea_state_summary": "Sea State",
        "aton_summary":      "AtoN Faults",
        "winter_summary":    "Winter Navigation",
    }

    summaries_parts = []
    for key, label in domain_labels.items():
        val = state.get(key)
        if val:
            summaries_parts.append(f"[{label}]\n{val}")

    summaries = "\n\n".join(summaries_parts) if summaries_parts else "No domain data was fetched."

    prompt = _WRITER_PROMPT.format(
        question=state.get("question", ""),
        intent=state.get("query_intent", "answer the user's question"),
        summaries=summaries,
        risk_score=state.get("risk_score", "N/A"),
        risk_level=state.get("risk_level", "Unknown"),
    )

    llm = get_llm(temperature=0.3)
    response = await llm.ainvoke(prompt)
    return {"answer": response.content}
