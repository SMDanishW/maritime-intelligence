"""Port call domain agent — summarizes Finnish port activity."""
from collections import Counter

from app.services.digitraffic import port_call_service


async def fetch_and_summarize() -> tuple[str, dict]:
    raw = await port_call_service.get_port_calls()
    calls = raw.get("portCalls", [])
    updated_at = raw.get("dataUpdatedTime", "unknown")

    if not calls:
        return "No port call data available.", {"total": 0, "calls": []}

    port_counts = Counter(c.get("portToVisit", "UNKNOWN") for c in calls)
    top5_ports = port_counts.most_common(5)

    normalized = []
    for c in calls:
        areas = c.get("portAreaDetails", [])
        first = areas[0] if areas else {}
        normalized.append({
            "port_call_id": c.get("portCallId"),
            "vessel_name": c.get("vesselName"),
            "mmsi": c.get("mmsi"),
            "port": c.get("portToVisit"),
            "arrival_time": first.get("ata") or first.get("eta"),
            "departure_time": first.get("atd") or first.get("etd"),
        })

    top5_str = ", ".join(f"{port} ({count})" for port, count in top5_ports)
    summary = (
        f"{len(calls)} active port calls in Finnish ports (updated {updated_at}).\n"
        f"Busiest ports: {top5_str}.\n"
        f"Sample vessels: "
        + ", ".join(
            c.get("vesselName", "unknown") for c in calls[:5] if c.get("vesselName")
        )
        + "."
    )

    viz = {"total": len(calls), "calls": normalized[:100]}
    return summary, viz
