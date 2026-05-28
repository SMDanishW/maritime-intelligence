"""Sea state domain agent — returns structured placeholder (MQTT-only data)."""


async def fetch_and_summarize() -> tuple[str, dict]:
    summary = (
        "Sea state measurement data is only available via Digitraffic MQTT stream "
        "(wss://meri.digitraffic.fi/mqtt, topic: meri-aton/#). "
        "No REST API endpoint exists for sea state. "
        "REST-based sea state data is unavailable in this session."
    )
    viz: dict = {}
    return summary, viz
