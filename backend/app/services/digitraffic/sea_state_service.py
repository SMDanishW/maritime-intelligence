from typing import Any

# Digitraffic sea-state measurements (smart buoy data) are NOT available via REST.
# Real-time values are streamed over MQTT: wss://meri.digitraffic.fi/mqtt
# Topic: vessels-v2/<mmsi>/location  (includes sea-state fields for buoy-equipped AtoNs)
# This service returns a structured placeholder so callers handle the gap gracefully.


async def get_sea_state() -> dict[str, Any]:
    return {
        "available": False,
        "reason": "Sea state measurements are only available via Digitraffic MQTT stream.",
        "mqtt_broker": "wss://meri.digitraffic.fi/mqtt",
        "topic_pattern": "meri-aton/#",
        "data": [],
    }
