"""
Visualization agent — converts domain viz data into frontend-ready JSON.

Output shape (stored in state):
  map_data:   {markers: [{lat, lon, type, label, data}], zones: []}
  chart_data: {bar: [{name, value}], line: [], pie: [{name, value}]}
  table_data: [{title, columns, rows}]
"""
from collections import Counter

from app.agents.state import AgentState


def _build_vessel_markers(ais_viz: dict) -> list[dict]:
    markers = []
    for v in (ais_viz.get("sample_vessels") or [])[:300]:
        if v.get("lat") is None or v.get("lon") is None:
            continue
        markers.append({
            "lat": v["lat"],
            "lon": v["lon"],
            "type": "vessel",
            "label": str(v.get("mmsi", "")),
            "data": {"mmsi": v.get("mmsi"), "sog": v.get("sog"), "heading": v.get("heading")},
        })
    return markers


def _build_fault_markers(aton_viz: dict) -> list[dict]:
    markers = []
    for f in (aton_viz.get("faults") or []):
        if f.get("lat") is None or f.get("lon") is None:
            continue
        if f.get("state") != "Open":
            continue
        markers.append({
            "lat": f["lat"],
            "lon": f["lon"],
            "type": "aton_fault",
            "label": f.get("aton_name") or f"AtoN {f.get('aton_id')}",
            "data": {"fault_type": f.get("fault_type"), "aton_type": f.get("aton_type")},
        })
    return markers


def _port_bar_chart(port_viz: dict) -> list[dict]:
    calls = port_viz.get("calls") or []
    counts = Counter(c.get("port") for c in calls if c.get("port"))
    return [{"name": port, "value": n} for port, n in counts.most_common(10)]


def _fault_type_chart(aton_viz: dict) -> list[dict]:
    faults = [f for f in (aton_viz.get("faults") or []) if f.get("state") == "Open"]
    counts = Counter(f.get("fault_type") for f in faults if f.get("fault_type"))
    return [{"name": t, "value": n} for t, n in counts.most_common(8)]


def _vessel_table(ais_viz: dict) -> dict | None:
    vessels = sorted(
        [v for v in (ais_viz.get("sample_vessels") or []) if v.get("sog") is not None],
        key=lambda v: v["sog"],
        reverse=True,
    )[:10]
    if not vessels:
        return None
    return {
        "title": "Top 10 Fastest Vessels",
        "columns": ["MMSI", "Speed (kn)", "Course (°)", "Heading (°)"],
        "rows": [
            [v.get("mmsi"), v.get("sog"), v.get("cog"), v.get("heading")]
            for v in vessels
        ],
    }


def _port_call_table(port_viz: dict) -> dict | None:
    calls = (port_viz.get("calls") or [])[:15]
    if not calls:
        return None
    return {
        "title": "Recent Port Calls",
        "columns": ["Vessel", "Port", "Arrival", "Departure"],
        "rows": [
            [c.get("vessel_name"), c.get("port"), c.get("arrival_time"), c.get("departure_time")]
            for c in calls
        ],
    }


def _fault_table(aton_viz: dict) -> dict | None:
    open_faults = [f for f in (aton_viz.get("faults") or []) if f.get("state") == "Open"][:15]
    if not open_faults:
        return None
    return {
        "title": "Open AtoN Faults",
        "columns": ["AtoN Name", "Type", "Fault Type", "Reported"],
        "rows": [
            [
                f.get("aton_name"),
                f.get("aton_type"),
                f.get("fault_type"),
                (f.get("entry_timestamp") or "")[:10],
            ]
            for f in open_faults
        ],
    }


async def visualization_node(state: AgentState) -> dict:
    ais_viz = state.get("ais_viz") or {}
    port_viz = state.get("port_viz") or {}
    aton_viz = state.get("aton_viz") or {}

    markers = _build_vessel_markers(ais_viz) + _build_fault_markers(aton_viz)

    bar_charts = []
    if port_viz:
        bar_charts.extend(_port_bar_chart(port_viz))
    pie_charts = []
    if aton_viz:
        pie_charts.extend(_fault_type_chart(aton_viz))

    tables = [
        t for t in [
            _vessel_table(ais_viz),
            _port_call_table(port_viz),
            _fault_table(aton_viz),
        ]
        if t is not None
    ]

    return {
        "map_data":   {"markers": markers, "zones": []},
        "chart_data": {"bar": bar_charts, "line": [], "pie": pie_charts},
        "table_data": tables,
    }
