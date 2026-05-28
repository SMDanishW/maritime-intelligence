from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class RiskComponents:
    vessel_count: int
    port_call_count: int
    open_aton_faults: int
    active_winter_assistances: int
    active_dirways: int


def _vessel_density_score(vessel_count: int) -> float:
    # Finnish waters: ~20k vessels at peak = max score
    return min(vessel_count / 20_000 * 100, 100.0)


def _port_congestion_score(port_call_count: int) -> float:
    # 400+ simultaneous port calls = max congestion
    return min(port_call_count / 400 * 100, 100.0)


def _sea_state_score() -> float:
    # Digitraffic sea state is MQTT-only — no REST data
    return 0.0


def _aton_fault_score(open_faults: int) -> float:
    # 200+ open faults = maximum risk signal
    return min(open_faults / 200 * 100, 100.0)


def _winter_navigation_score(active_assistances: int, active_dirways: int) -> float:
    raw = (active_assistances * 20.0) + (active_dirways * 10.0)
    return min(raw, 100.0)


def _level(score: float) -> str:
    if score <= 25:
        return "Low"
    if score <= 50:
        return "Medium"
    if score <= 75:
        return "High"
    return "Critical"


def compute_risk(components: RiskComponents, weights: dict[str, int]) -> dict:
    vd = _vessel_density_score(components.vessel_count)
    pc = _port_congestion_score(components.port_call_count)
    ss = _sea_state_score()
    af = _aton_fault_score(components.open_aton_faults)
    wn = _winter_navigation_score(components.active_winter_assistances, components.active_dirways)

    w_vd = weights["vessel_density"] / 100
    w_pc = weights["port_congestion"] / 100
    w_ss = weights["sea_state"] / 100
    w_af = weights["aton_faults"] / 100
    w_wn = weights["winter_navigation"] / 100

    score = round(vd * w_vd + pc * w_pc + ss * w_ss + af * w_af + wn * w_wn, 1)

    return {
        "score": score,
        "level": _level(score),
        "components": [
            {
                "name": "Vessel Density",
                "score": round(vd, 1),
                "weight": w_vd,
                "weighted": round(vd * w_vd, 1),
                "note": f"{components.vessel_count:,} AIS vessels",
            },
            {
                "name": "Port Congestion",
                "score": round(pc, 1),
                "weight": w_pc,
                "weighted": round(pc * w_pc, 1),
                "note": f"{components.port_call_count} active port calls",
            },
            {
                "name": "Sea State",
                "score": ss,
                "weight": w_ss,
                "weighted": ss * w_ss,
                "note": "No REST data — MQTT only",
            },
            {
                "name": "AtoN Faults",
                "score": round(af, 1),
                "weight": w_af,
                "weighted": round(af * w_af, 1),
                "note": f"{components.open_aton_faults} open faults",
            },
            {
                "name": "Winter Navigation",
                "score": round(wn, 1),
                "weight": w_wn,
                "weighted": round(wn * w_wn, 1),
                "note": f"{components.active_winter_assistances} active icebreakers, {components.active_dirways} dirways",
            },
        ],
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
