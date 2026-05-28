"""
Phase 1 — Digitraffic Marine API probe.
Hits every confirmed endpoint, saves truncated sample JSON to docs/sample-responses/.
Run from backend/: python scripts/probe_apis.py
"""
import asyncio
import json
import sys
from pathlib import Path

import httpx

BASE_URL = "https://meri.digitraffic.fi"
SAMPLES_DIR = Path(__file__).parent.parent.parent / "docs" / "sample-responses"
TIMEOUT = 20

HEADERS = {
    "Accept": "application/json",
    "Digitraffic-User": "marine-intelligence/0.1",
}

# (label, path, params, note)
ENDPOINTS = [
    ("AIS Locations",       "/api/ais/v1/locations",                    None,                  None),
    ("Vessel Details",      "/api/port-call/v1/vessel-details",         None,                  None),
    ("Port Calls",          "/api/port-call/v1/port-calls",             None,                  None),
    ("Ports",               "/api/port-call/v1/ports",                  None,                  None),
    ("AtoN Faults",         "/api/aton/v1/faults",                      {"language": "en"},    "GeoJSON FeatureCollection"),
    ("Winter Dirways",      "/api/winter-navigation/v2/dirways",        None,                  None),
    ("Winter Vessels",      "/api/winter-navigation/v2/vessels",        None,                  "Wrapped: {lastUpdated, vessels:[]}"),
]

NOT_AVAILABLE = [
    ("Sea State", "No REST endpoint — only available via Digitraffic MQTT stream (wss://meri.digitraffic.fi/mqtt, topic: meri-aton/#)"),
]


def count_records(data) -> str:
    if isinstance(data, list):
        return str(len(data))
    if isinstance(data, dict):
        for key in ("features", "vessels", "portCalls", "ports"):
            if key in data and isinstance(data[key], list):
                return f"{len(data[key])} ({key})"
        return "dict"
    return "?"


def truncate(data, n=3):
    if isinstance(data, list):
        return data[:n]
    if isinstance(data, dict):
        for key in ("features", "vessels", "portCalls"):
            if key in data and isinstance(data[key], list):
                copy = dict(data)
                copy[key] = data[key][:n]
                return copy
    return data


async def probe():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    print("Probing Digitraffic Marine APIs...\n")
    failures = []

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT, headers=HEADERS, follow_redirects=True) as client:
        for name, path, params, note in ENDPOINTS:
            slug = name.lower().replace(" ", "_")
            try:
                r = await client.get(path, params=params)
                r.raise_for_status()
                data = r.json()
                records = count_records(data)
                sample = truncate(data)
                (SAMPLES_DIR / f"{slug}.json").write_text(
                    json.dumps(sample, indent=2, ensure_ascii=False)
                )
                suffix = f"  [{note}]" if note else ""
                print(f"  [OK]  {name:<22} records={records:<15} -> {slug}.json{suffix}")

            except httpx.HTTPStatusError as exc:
                failures.append(name)
                print(f"  [HTTP {exc.response.status_code}] {name:<22} {path}")
            except httpx.TimeoutException:
                failures.append(name)
                print(f"  [TIMEOUT] {name:<22} {path}")
            except Exception as exc:
                failures.append(name)
                print(f"  [ERROR] {name:<22} {exc}")

    print()
    for name, reason in NOT_AVAILABLE:
        slug = name.lower().replace(" ", "_")
        placeholder = {"available": False, "reason": reason}
        (SAMPLES_DIR / f"{slug}.json").write_text(json.dumps(placeholder, indent=2))
        print(f"  [N/A] {name:<22} -> {slug}.json (MQTT only — placeholder saved)")

    ok = len(ENDPOINTS) - len(failures)
    print(f"\n{ok}/{len(ENDPOINTS)} REST endpoints reachable. {len(NOT_AVAILABLE)} MQTT-only.")

    if failures:
        print(f"Failed: {', '.join(failures)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(probe())
