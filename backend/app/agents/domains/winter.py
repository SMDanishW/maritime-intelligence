"""Winter navigation domain agent — icebreaker status and ice dirways."""
import asyncio

from app.services.digitraffic import winter_navigation_service


async def fetch_and_summarize() -> tuple[str, dict]:
    vessels_raw, dirways_raw = await asyncio.gather(
        winter_navigation_service.get_vessels(),
        winter_navigation_service.get_dirways(),
    )

    vessels = vessels_raw.get("vessels", [])
    dirways = dirways_raw.get("features", [])
    updated_at = vessels_raw.get("lastUpdated", "unknown")

    normalized = []
    for v in vessels:
        activities = v.get("activities", [])
        current = activities[0] if activities else None
        active = current is not None and current.get("type") != "STOP"
        normalized.append({
            "name": v.get("name"),
            "mmsi": v.get("mmsi"),
            "type": v.get("type"),
            "call_sign": v.get("callSign"),
            "active": active,
            "current_activity": current.get("type") if current else None,
            "activity_end_time": current.get("endTime") if current else None,
        })

    active_count = sum(1 for v in normalized if v["active"])
    vessel_lines = ", ".join(
        f"{v['name']} ({'active' if v['active'] else v['current_activity'] or 'STOP'})"
        for v in normalized
    )

    if active_count == 0 and not dirways:
        season_note = "Current season appears to be summer — no active ice navigation."
    else:
        season_note = f"{active_count} icebreakers actively assisting, {len(dirways)} dirways open."

    summary = (
        f"Finnish icebreaker fleet ({updated_at}): {vessel_lines}.\n"
        f"{season_note}"
    )

    viz = {"vessels": normalized, "active_dirways": len(dirways)}
    return summary, viz
