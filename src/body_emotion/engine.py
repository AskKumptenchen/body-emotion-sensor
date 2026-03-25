from __future__ import annotations

from dataclasses import replace
from typing import Dict

from .defaults import INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME, default_state
from .interpreter import (
    apply_phase_propagation_with_trace,
    body_scores_with_trace_from_analysis,
    body_state_changes_from_scores,
)
from .locale_config import LANG_EN
from .prompting import build_emotional_prompt_payload, build_prompt_output_min
from .schema import AnalysisInput, MappingResult, BODIES, State


class BodyEmotionEngine:
    def __init__(self, state: State | None = None):
        self.state = state or default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)

    def _body_persistent_delta(self, raw_score: int, fragility: float) -> int:
        scaled = raw_score / 2 * (1 + (fragility - 0.5) * 0.25) * self.state.traits.overall_fragility
        return int(round(scaled))

    def _body_recovery_delta(self, current: int, baseline: int) -> int:
        drift = baseline - current
        if drift == 0:
            return 0
        recovery_rate = 0.15 if abs(current - baseline) >= 20 else 0.10
        return int(round(drift * recovery_rate))

    def _apply_persistent_saturation(self, current: int, delta: int) -> int:
        if delta > 0:
            if current >= 90:
                return int(round(delta * 0.35))
            if current >= 80:
                return int(round(delta * 0.60))
        if delta < 0 and current <= 20:
            return int(round(delta * 0.60))
        return delta

    def _update_bodies_with_trace(self, body_scores: Dict[str, int]) -> tuple[Dict[str, int], Dict[str, dict]]:
        updated: Dict[str, int] = {}
        trace: Dict[str, dict] = {}
        for body in BODIES:
            ostate = self.state.bodies[body]
            before = ostate.current
            recovery_delta = self._body_recovery_delta(ostate.current, ostate.baseline)
            persistent_delta = self._body_persistent_delta(body_scores[body], ostate.fragility)
            saturated_delta = self._apply_persistent_saturation(ostate.current, persistent_delta)
            next_score = max(0, min(100, ostate.current + recovery_delta + saturated_delta))
            self.state.bodies[body] = replace(ostate, current=next_score)
            updated[body] = next_score
            trace[body] = {
                "baseline": ostate.baseline,
                "current_before": before,
                "recovery_delta": recovery_delta,
                "persistent_delta": persistent_delta,
                "saturated_delta": saturated_delta,
                "current_after": next_score,
                "total_applied_delta": next_score - before,
                "fragility": ostate.fragility,
            }
        return updated, trace

    def _update_bodies(self, body_scores: Dict[str, int]) -> Dict[str, int]:
        updated, _ = self._update_bodies_with_trace(body_scores)
        return updated

    def process(self, analysis_input: AnalysisInput | dict, lang: str = LANG_EN) -> MappingResult:
        analysis = (
            analysis_input
            if isinstance(analysis_input, AnalysisInput)
            else AnalysisInput.from_dict(analysis_input, lang=lang)
        )
        body_fragility = {body: self.state.bodies[body].fragility for body in BODIES}
        base_scores, body_contributors, mapping_trace = body_scores_with_trace_from_analysis(
            analysis,
            fragility_profile=body_fragility,
            overall_fragility=self.state.traits.overall_fragility,
        )
        body_scores, phase_trace = apply_phase_propagation_with_trace(base_scores, body_contributors, self.state.bodies)
        body_state_changes = body_state_changes_from_scores(body_scores)
        updated_bodies, persistent_trace = self._update_bodies_with_trace(body_scores)
        payload_stub = MappingResult(
            analysis_target=analysis.analysis_target,
            context_summary=analysis.context_summary,
            semantic_stimuli=analysis.semantic_stimuli,
            body_reactions=analysis.body_reactions,
            body_contributors=body_contributors,
            body_scores=body_scores,
            body_state_changes=body_state_changes,
            turn_change_tags=[],
            body_tag="",
            emotional_prompt_payload={},
            updated_bodies=updated_bodies,
            turn_trace={},
        )
        emotional_prompt_payload = build_emotional_prompt_payload(self.state, payload_stub, analysis, lang=lang)
        turn_change_tags = emotional_prompt_payload["TURN_CHANGE_TAGS"]
        body_tag = emotional_prompt_payload["BODY_TAG"]
        turn_trace = {
            "input": analysis.to_dict(),
            "base_mapping": mapping_trace["base_mapping"],
            "phase_propagation": phase_trace,
            "persistent_update": persistent_trace,
            "prompt_output": {
                **build_prompt_output_min(emotional_prompt_payload),
                "emotional_prompt_payload": emotional_prompt_payload,
            },
        }

        self.state.last_body_note = body_tag
        self.state.last_prompt_tags = turn_change_tags
        self.state.history.append(
            {
                "analysis_target": analysis.analysis_target,
                "context_summary": analysis.context_summary.current_turn_focus,
                "semantic_stimuli": [item.id for item in analysis.semantic_stimuli],
                "body_reactions": [item.id for item in analysis.body_reactions],
                "body_contributors": body_contributors,
                "body_scores": body_scores,
                "body_state_changes": {name: change.to_dict() for name, change in body_state_changes.items()},
                "TURN_CHANGE_TAGS": turn_change_tags,
                "BODY_TAG": body_tag,
                "emotional_prompt_payload": emotional_prompt_payload,
                "updated_bodies": updated_bodies,
                "turn_trace": turn_trace,
            }
        )

        return MappingResult(
            analysis_target=analysis.analysis_target,
            context_summary=analysis.context_summary,
            semantic_stimuli=analysis.semantic_stimuli,
            body_reactions=analysis.body_reactions,
            body_contributors=body_contributors,
            body_scores=body_scores,
            body_state_changes=body_state_changes,
            turn_change_tags=turn_change_tags,
            body_tag=body_tag,
            emotional_prompt_payload=emotional_prompt_payload,
            updated_bodies=updated_bodies,
            turn_trace=turn_trace,
        )
