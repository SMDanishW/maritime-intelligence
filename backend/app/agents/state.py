from typing import TypedDict

REFUSAL_MESSAGE = (
    "I can only answer questions related to Finnish marine traffic using the available "
    "marine traffic data. You can ask about vessels, port calls, sea state, AtoN faults, "
    "winter navigation, or marine traffic risk.\n\n"
    "Would you like example questions to get an idea of the scope?"
)

ALL_DOMAINS = ["ais", "port", "sea_state", "aton", "winter"]


class AgentState(TypedDict, total=False):
    # ── Input ──────────────────────────────────────────────────────────────
    question: str
    session_id: str | None

    # ── Guardrail ──────────────────────────────────────────────────────────
    in_scope: bool

    # ── Supervisor ─────────────────────────────────────────────────────────
    selected_domains: list[str]   # subset of ALL_DOMAINS
    query_intent: str             # brief description of what user wants

    # ── Domain text summaries (fed to LLM; never raw API data) ─────────────
    ais_summary: str | None
    port_summary: str | None
    sea_state_summary: str | None
    aton_summary: str | None
    winter_summary: str | None

    # ── Minimal structured data for visualization only ─────────────────────
    ais_viz: dict | None      # {vessel_count, sample_vessels: []}
    port_viz: dict | None     # {total, calls: []}
    aton_viz: dict | None     # {total, open, faults: []}
    winter_viz: dict | None   # {vessels: [], active_dirways}

    # ── Risk ───────────────────────────────────────────────────────────────
    risk_score: float | None
    risk_level: str | None
    risk_components: list[dict]

    # ── Visualization output ───────────────────────────────────────────────
    map_data: dict       # {markers: [], zones: []}
    chart_data: dict     # {bar: [], line: [], pie: []}
    table_data: list     # [{title, columns, rows}]

    # ── Final answer ───────────────────────────────────────────────────────
    answer: str | None

    # ── Error log ──────────────────────────────────────────────────────────
    errors: list[str]
