from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .schema import AnalysisInput, BodyStateChange, BODIES, PhaseState

# 五脏偏实 / 偏虚版本：正分=该脏主情绪走向偏实，负分=走向偏虚。
# CLI 回复层默认输出本轮标签、当前 BODY_TAG，以及 baseline/current 对比块。
STIMULUS_TO_BODIES = {
    "negated": {"liver": -1, "heart": -2, "kidney": -1},
    "rejected": {"liver": -1, "heart": -2, "lung": 2, "kidney": -2},
    "pressured": {"liver": 1, "heart": -1, "spleen": 2},
    "distanced": {"heart": -2, "lung": 1, "kidney": -2},
    "humiliated": {"liver": 2, "heart": -2, "spleen": 1, "lung": 2, "kidney": -1},
    "understood": {"liver": 1, "heart": 2, "spleen": -1, "kidney": 1},
    "supported": {"heart": 1, "spleen": -2, "kidney": 1},
    "repaired": {"liver": 1, "heart": 2, "spleen": -2, "lung": -1, "kidney": 1},
    "bounded": {"liver": -1, "heart": -1, "lung": 1},
    "reapproached": {"liver": 1, "heart": 2, "spleen": -1, "kidney": 1},
}

REACTION_TO_BODIES = {
    "tension": {"liver": 1, "spleen": 1, "kidney": 1},
    "contraction": {"liver": -1, "heart": -1, "kidney": -2},
    "surge": {"liver": 1, "heart": 1},
    "stuck": {"liver": -1, "spleen": 2, "lung": 1},
    "sinking": {"heart": -2, "spleen": -1, "lung": 1, "kidney": -1},
    "emptied": {"heart": -2, "spleen": -1, "kidney": -3},
    "burdened": {"spleen": 3, "kidney": -1},
    "blocked": {"spleen": 2, "lung": 1},
    "relaxed": {"liver": -1, "heart": 1, "spleen": -1, "lung": -1, "kidney": 1},
    "warming": {"heart": 2, "spleen": -1, "kidney": 1},
    "settling": {"spleen": -1, "kidney": 1},
    "supported": {"spleen": -2, "kidney": 1},
    "heat_drop": {"heart": -3, "kidney": -1},
}

INTENSITY_MULTIPLIER = {"light": 1, "medium": 2, "strong": 3}
REACTION_WEIGHT = 0.5
WU_XING_RELATIONS = {
    "liver": {"generates": "heart", "constrains": "spleen"},
    "heart": {"generates": "spleen", "constrains": "lung"},
    "spleen": {"generates": "lung", "constrains": "kidney"},
    "lung": {"generates": "kidney", "constrains": "liver"},
    "kidney": {"generates": "liver", "constrains": "heart"},
}
PHASE_CONSTRAIN_DELTAS = {"light": -2, "strong": -4}
PHASE_GENERATE_DELTAS = {"light": 2, "strong": 4}
PHASE_TARGET_DELTA_LIMIT = 6
TURN_SCORE_SCALE = 6.0
CURRENT_OFFSET_SCALE = 15.0
CONSTRAIN_LIGHT_THRESHOLD = 0.55
CONSTRAIN_STRONG_THRESHOLD = 1.0
GENERATE_BALANCE_THRESHOLD = 0.45
GENERATE_STRONG_SOURCE_WINDOW = 0.22
GENERATE_LIGHT_PAIR_WINDOW = 0.55
GENERATE_STRONG_PAIR_WINDOW = 0.22
GENERATE_MIN_TURN_SCORE = 1
GENERATE_STRONG_TURN_SCORE = 2
GENERATE_MIN_CURRENT_OFFSET = 3
GENERATE_STRONG_CURRENT_OFFSET = 4


@dataclass(frozen=True)
class PhaseProfile:
    body: str
    turn_score: int
    current_offset: int
    fragility: float
    phase_power: float


@dataclass(frozen=True)
class PhaseAction:
    source: str
    target: str | None
    mode: str
    level: str | None


def _empty_body_scores() -> Dict[str, int]:
    return {body: 0 for body in BODIES}


def _empty_body_contributors() -> Dict[str, List[str]]:
    return {body: [] for body in BODIES}


def _empty_trace_totals() -> Dict[str, Dict[str, float]]:
    return {
        body: {
            "stimulus_raw": 0.0,
            "stimulus_scaled": 0.0,
            "reaction_raw": 0.0,
            "reaction_scaled": 0.0,
            "total_raw": 0.0,
            "total_scaled": 0.0,
        }
        for body in BODIES
    }


def _normalize_trace_totals(per_body: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, int]]:
    return {
        body: {key: int(round(value)) for key, value in stats.items()}
        for body, stats in per_body.items()
    }


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _build_phase_profile(body: str, turn_score: int, body_state: PhaseState) -> PhaseProfile:
    turn_component = _clamp(turn_score / TURN_SCORE_SCALE, -2.0, 2.0)
    offset_component = _clamp((body_state.current - body_state.baseline) / CURRENT_OFFSET_SCALE, -2.0, 2.0)
    phase_power = turn_component * 0.7 + offset_component * 0.3
    return PhaseProfile(
        body=body,
        turn_score=turn_score,
        current_offset=body_state.current - body_state.baseline,
        fragility=body_state.fragility,
        phase_power=phase_power,
    )


def _build_phase_snapshot(scores: Dict[str, int], body_states: Dict[str, PhaseState]) -> Dict[str, PhaseProfile]:
    return {body: _build_phase_profile(body, scores[body], body_states[body]) for body in BODIES}


def _has_generate_drive(profile: PhaseProfile) -> bool:
    return profile.turn_score >= GENERATE_MIN_TURN_SCORE or profile.current_offset >= GENERATE_MIN_CURRENT_OFFSET


def _has_strong_generate_drive(profile: PhaseProfile) -> bool:
    return profile.turn_score >= GENERATE_STRONG_TURN_SCORE or profile.current_offset >= GENERATE_STRONG_CURRENT_OFFSET


def _decide_phase_action(source: PhaseProfile, snapshot: Dict[str, PhaseProfile]) -> PhaseAction:
    relation = WU_XING_RELATIONS[source.body]
    if source.phase_power >= CONSTRAIN_STRONG_THRESHOLD:
        return PhaseAction(source=source.body, target=relation["constrains"], mode="constrain", level="strong")
    if source.phase_power >= CONSTRAIN_LIGHT_THRESHOLD:
        return PhaseAction(source=source.body, target=relation["constrains"], mode="constrain", level="light")
    if source.phase_power < 0 or abs(source.phase_power) > GENERATE_BALANCE_THRESHOLD or not _has_generate_drive(source):
        return PhaseAction(source=source.body, target=None, mode="silent", level=None)

    child = snapshot[relation["generates"]]
    pair_distance = abs(source.phase_power - child.phase_power)
    if (
        abs(source.phase_power) <= GENERATE_STRONG_SOURCE_WINDOW
        and pair_distance <= GENERATE_STRONG_PAIR_WINDOW
        and _has_strong_generate_drive(source)
    ):
        return PhaseAction(source=source.body, target=child.body, mode="generate", level="strong")
    if pair_distance <= GENERATE_LIGHT_PAIR_WINDOW:
        return PhaseAction(source=source.body, target=child.body, mode="generate", level="light")
    return PhaseAction(source=source.body, target=None, mode="silent", level=None)


def _apply_phase_action(
    action: PhaseAction,
    phase_deltas: Dict[str, int],
    contributors: Dict[str, List[str]],
    actions_trace: List[Dict[str, Any]] | None = None,
) -> None:
    if action.mode == "silent" or action.target is None or action.level is None:
        if actions_trace is not None:
            actions_trace.append({
                "source": action.source,
                "mode": action.mode,
                "level": None,
                "target": None,
                "delta": 0,
            })
        return
    if action.mode == "constrain":
        delta = PHASE_CONSTRAIN_DELTAS[action.level]
    else:
        delta = PHASE_GENERATE_DELTAS[action.level]
    phase_deltas[action.target] = max(
        -PHASE_TARGET_DELTA_LIMIT,
        min(PHASE_TARGET_DELTA_LIMIT, phase_deltas[action.target] + delta),
    )
    contributors[action.target].append(
        f"phase-propagation:{action.source}:{action.mode}:{action.level}:{action.target}:{delta:+d}"
    )
    if actions_trace is not None:
        actions_trace.append({
            "source": action.source,
            "mode": action.mode,
            "level": action.level,
            "target": action.target,
            "delta": delta,
        })


def apply_phase_propagation_with_trace(
    base_scores: Dict[str, int],
    contributors: Dict[str, List[str]],
    body_states: Dict[str, PhaseState],
) -> Tuple[Dict[str, int], Dict[str, Any]]:
    snapshot = _build_phase_snapshot(base_scores, body_states)
    phase_deltas = _empty_body_scores()
    actions_trace: List[Dict[str, Any]] = []
    for body in BODIES:
        action = _decide_phase_action(snapshot[body], snapshot)
        _apply_phase_action(action, phase_deltas, contributors, actions_trace)
    final_scores = {body: base_scores[body] + phase_deltas[body] for body in BODIES}
    trace = {
        "scores_before": dict(base_scores),
        "snapshot": {
            body: {
                "turn_score": profile.turn_score,
                "current_offset": profile.current_offset,
                "fragility": profile.fragility,
                "phase_power": round(profile.phase_power, 4),
                "generates": WU_XING_RELATIONS[body]["generates"],
                "constrains": WU_XING_RELATIONS[body]["constrains"],
            }
            for body, profile in snapshot.items()
        },
        "actions": actions_trace,
        "phase_deltas": dict(phase_deltas),
        "scores_after": dict(final_scores),
    }
    return final_scores, trace


def apply_phase_propagation(
    base_scores: Dict[str, int],
    contributors: Dict[str, List[str]],
    body_states: Dict[str, PhaseState],
) -> Dict[str, int]:
    final_scores, _ = apply_phase_propagation_with_trace(base_scores, contributors, body_states)
    return final_scores


def body_scores_with_trace_from_analysis(
    analysis: AnalysisInput,
    fragility_profile: Dict[str, float] | None = None,
    overall_fragility: float = 1.0,
) -> Tuple[Dict[str, int], Dict[str, List[str]], Dict[str, Any]]:
    scores = _empty_body_scores()
    contributors = _empty_body_contributors()

    fragility_profile = fragility_profile or {body: 0.5 for body in BODIES}
    per_body = _empty_trace_totals()
    stimulus_steps: List[Dict[str, Any]] = []
    reaction_steps: List[Dict[str, Any]] = []

    def apply_fragility(body: str, delta: float) -> int:
        fragility = fragility_profile.get(body, 0.5)
        scaled = delta * (1 + (fragility - 0.5) * 0.8) * overall_fragility
        return int(round(scaled))

    for item in analysis.semantic_stimuli:
        mapping = STIMULUS_TO_BODIES.get(item.id, {})
        for body, base in mapping.items():
            raw_delta = base * INTENSITY_MULTIPLIER[item.intensity]
            delta = apply_fragility(body, raw_delta)
            scores[body] += delta
            per_body[body]["stimulus_raw"] += raw_delta
            per_body[body]["stimulus_scaled"] += delta
            per_body[body]["total_raw"] += raw_delta
            per_body[body]["total_scaled"] += delta
            contributors[body].append(f"stimulus:{item.id}:{item.intensity}:{delta:+d}:frag={fragility_profile.get(body,0.5):.2f}")
            stimulus_steps.append({
                "id": item.id,
                "intensity": item.intensity,
                "body": body,
                "base": base,
                "raw_delta": int(round(raw_delta)),
                "scaled_delta": delta,
                "fragility": fragility_profile.get(body, 0.5),
                "evidence": item.evidence,
            })

    for item in analysis.body_reactions:
        mapping = REACTION_TO_BODIES.get(item.id, {})
        for body, base in mapping.items():
            raw_delta = base * INTENSITY_MULTIPLIER[item.intensity] * REACTION_WEIGHT
            delta = apply_fragility(body, raw_delta)
            scores[body] += delta
            per_body[body]["reaction_raw"] += raw_delta
            per_body[body]["reaction_scaled"] += delta
            per_body[body]["total_raw"] += raw_delta
            per_body[body]["total_scaled"] += delta
            contributors[body].append(
                f"reaction:{item.id}:{item.intensity}:{delta:+d}:weight={REACTION_WEIGHT:.2f}:frag={fragility_profile.get(body,0.5):.2f}"
            )
            reaction_steps.append({
                "id": item.id,
                "intensity": item.intensity,
                "body": body,
                "base": base,
                "raw_delta": int(round(raw_delta)),
                "scaled_delta": delta,
                "fragility": fragility_profile.get(body, 0.5),
                "weight": REACTION_WEIGHT,
                "reason": item.reason,
            })

    trace = {
        "base_mapping": {
            "stimulus_steps": stimulus_steps,
            "reaction_steps": reaction_steps,
            "per_body": _normalize_trace_totals(per_body),
            "scores_before_phase": dict(scores),
        }
    }
    return scores, contributors, trace


def body_scores_from_analysis(
    analysis: AnalysisInput,
    fragility_profile: Dict[str, float] | None = None,
    overall_fragility: float = 1.0,
) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    scores, contributors, _ = body_scores_with_trace_from_analysis(
        analysis,
        fragility_profile=fragility_profile,
        overall_fragility=overall_fragility,
    )
    return scores, contributors


def body_state_changes_from_scores(scores: Dict[str, int]) -> Dict[str, BodyStateChange]:
    changes: Dict[str, BodyStateChange] = {}
    for body in BODIES:
        score = scores[body]
        if abs(score) <= 1:
            changes[body] = BodyStateChange.stable()
            continue
        trend = "up" if score > 0 else "down"
        changes[body] = BodyStateChange(trend=trend, score=score)
    return changes
