"""AtoN fault domain agent — summarizes navigation aid faults."""
from collections import Counter

from app.services.digitraffic import aton_fault_service


async def fetch_and_summarize() -> tuple[str, dict]:
    raw = await aton_fault_service.get_aton_faults()
    features = raw.get("features", [])
    updated_at = raw.get("lastUpdated", "unknown")

    if not features:
        return "No AtoN fault data available.", {"total": 0, "open": 0, "faults": []}

    faults = []
    for f in features:
        props = f.get("properties", {})
        coords = (f.get("geometry") or {}).get("coordinates", [None, None])
        faults.append({
            "id": props.get("id"),
            "aton_id": props.get("aton_id"),
            "aton_name": props.get("aton_name_fi") or props.get("aton_name_sv"),
            "fault_type": props.get("type"),
            "state": props.get("state"),
            "fixed": props.get("fixed", False),
            "lon": coords[0] if coords else None,
            "lat": coords[1] if coords else None,
            "entry_timestamp": props.get("entry_timestamp"),
            "aton_type": props.get("aton_type"),
        })

    open_faults = [f for f in faults if not f["fixed"] and f["state"] == "Open"]
    type_counts = Counter(f["fault_type"] for f in open_faults if f["fault_type"])
    top_types = type_counts.most_common(5)

    top_types_str = ", ".join(f"{t} ({n})" for t, n in top_types)
    summary = (
        f"{len(faults)} AtoN faults total, {len(open_faults)} currently open "
        f"(updated {updated_at}).\n"
        f"Open fault types: {top_types_str}.\n"
        f"Recent open faults: "
        + ", ".join(
            f["aton_name"] or f"AtoN {f['aton_id']}"
            for f in open_faults[:5]
            if f.get("aton_name") or f.get("aton_id")
        )
        + "."
    )

    viz = {"total": len(faults), "open": len(open_faults), "faults": faults}
    return summary, viz
