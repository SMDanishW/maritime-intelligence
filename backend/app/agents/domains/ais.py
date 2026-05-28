"""AIS domain agent — fetches vessel locations and returns a concise summary for the LLM."""
from app.services.digitraffic import ais_service

# navStat codes (AIS standard)
_NAV_STATUS = {
    0: "underway (engine)",
    1: "at anchor",
    2: "not under command",
    3: "restricted manoeuvrability",
    5: "moored",
    8: "sailing",
    15: "undefined",
}


async def fetch_and_summarize() -> tuple[str, dict]:
    """Returns (text_summary, viz_data)."""
    raw = await ais_service.get_vessel_locations()
    features = raw.get("features", [])
    updated_at = raw.get("dataUpdatedTime", "unknown")

    if not features:
        return "No AIS vessel data available.", {"vessel_count": 0, "sample_vessels": []}

    # Build minimal vessel list for viz (limit to 500 for frontend map)
    vessels = []
    for f in features:
        coords = (f.get("geometry") or {}).get("coordinates", [None, None])
        props = f.get("properties", {})
        vessels.append({
            "mmsi": f.get("mmsi") or props.get("mmsi"),
            "lon": coords[0],
            "lat": coords[1],
            "sog": props.get("sog"),
            "cog": props.get("cog"),
            "heading": props.get("heading"),
            "nav_status": props.get("navStat"),
        })

    # Stats for summary
    total = len(vessels)
    status_counts: dict[int, int] = {}
    speeds = []
    for v in vessels:
        ns = v["nav_status"]
        if ns is not None:
            status_counts[ns] = status_counts.get(ns, 0) + 1
        if v["sog"] is not None:
            speeds.append((v["sog"], v["mmsi"]))

    speeds.sort(reverse=True)
    top5 = speeds[:5]

    status_lines = ", ".join(
        f"{_NAV_STATUS.get(k, f'status {k}')}: {n}"
        for k, n in sorted(status_counts.items(), key=lambda x: -x[1])[:5]
    )

    summary = (
        f"{total:,} vessels active in Finnish waters (updated {updated_at}).\n"
        f"Navigation status breakdown: {status_lines}.\n"
        f"Top 5 speeds (knots): "
        + ", ".join(f"{sog:.1f} (MMSI {mmsi})" for sog, mmsi in top5)
        + "."
    )

    viz = {"vessel_count": total, "sample_vessels": vessels[:500]}
    return summary, viz
