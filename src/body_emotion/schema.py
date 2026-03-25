from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from .locale_config import LANG_EN
from .schema_errors import (
    body_reactions_min,
    missing_keys,
    must_be_array,
    must_be_non_empty,
    must_be_one_of,
    semantic_stimuli_min,
)

BODIES = ["liver", "heart", "spleen", "lung", "kidney"]
INTENSITY_LEVELS = {"light", "medium", "strong"}
BODY_TRENDS = {"up", "down", "mixed", "stable"}
SEMANTIC_STIMULUS_IDS = {
    "negated",
    "rejected",
    "pressured",
    "distanced",
    "humiliated",
    "understood",
    "supported",
    "repaired",
    "bounded",
    "reapproached",
}
BODY_REACTION_IDS = {
    "tension",
    "contraction",
    "surge",
    "stuck",
    "sinking",
    "emptied",
    "burdened",
    "blocked",
    "relaxed",
    "warming",
    "settling",
    "supported",
    "heat_drop",
}


def _require_keys(data: dict, keys: List[str], label: str, lang: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(missing_keys(lang, label, missing))


def _require_choice(value: str, choices: set[str], label: str, lang: str) -> str:
    if value not in choices:
        raise ValueError(must_be_one_of(lang, label, choices, value))
    return value


def _require_list(value: Any, label: str, lang: str) -> list:
    if not isinstance(value, list):
        raise ValueError(must_be_array(lang, label))
    return value


def _require_non_empty_string(value: Any, label: str, lang: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(must_be_non_empty(lang, label))
    return text


@dataclass
class PhaseState:
    baseline: int
    current: int
    fragility: float


def _phase_state_from_dict(v: dict) -> PhaseState:
    """兼容旧 state 中可能存在的 recovery_rate 等已废弃字段。"""
    return PhaseState(
        baseline=int(v["baseline"]),
        current=int(v.get("current", v["baseline"])),
        fragility=float(v["fragility"]),
    )


@dataclass
class Traits:
    overall_fragility: float = 1.0
    attachment_style: str = "balanced"
    default_expression: str = "natural"


@dataclass
class Profile:
    agent_id: str
    name: str


@dataclass
class State:
    profile: Profile
    bodies: Dict[str, PhaseState]
    traits: Traits = field(default_factory=Traits)
    last_body_note: str = ""
    last_prompt_tags: List[str] = field(default_factory=list)
    history: List[dict] = field(default_factory=list)

    def to_snapshot_dict(self) -> dict:
        """持久化到主 state 文件：profile / bodies / traits / last_*，不含 history。"""
        return {
            "profile": asdict(self.profile),
            "bodies": {k: asdict(v) for k, v in self.bodies.items()},
            "traits": asdict(self.traits),
            "last_body_note": self.last_body_note,
            "last_prompt_tags": list(self.last_prompt_tags),
        }

    def to_dict(self) -> dict:
        return {
            **self.to_snapshot_dict(),
            "history": list(self.history),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "State":
        raw = data.get("bodies")
        if raw is None:
            raw = data.get("organs")
        if raw is None:
            from .defaults import default_body_constitution

            bodies = default_body_constitution()
        else:
            bodies = {k: _phase_state_from_dict(v) for k, v in raw.items()}
        return cls(
            profile=Profile(**data["profile"]),
            bodies=bodies,
            traits=Traits(**data.get("traits", {})),
            last_body_note=data.get("last_body_note", ""),
            last_prompt_tags=data.get("last_prompt_tags", []),
            history=data.get("history", []),
        )


@dataclass
class ContextSummary:
    current_turn_focus: str

    @classmethod
    def from_dict(cls, data: dict, lang: str = LANG_EN) -> "ContextSummary":
        _require_keys(data, ["current_turn_focus"], "context_summary", lang)
        return cls(
            current_turn_focus=_require_non_empty_string(data["current_turn_focus"], "context_summary.current_turn_focus", lang),
        )


@dataclass
class SemanticStimulus:
    id: str
    intensity: str
    evidence: str

    @classmethod
    def from_dict(cls, data: dict, lang: str = LANG_EN) -> "SemanticStimulus":
        _require_keys(data, ["id", "intensity", "evidence"], "semantic_stimulus", lang)
        return cls(
            id=_require_choice(
                _require_non_empty_string(data["id"], "semantic_stimulus.id", lang),
                SEMANTIC_STIMULUS_IDS,
                "semantic_stimulus.id",
                lang,
            ),
            intensity=_require_choice(str(data["intensity"]), INTENSITY_LEVELS, "semantic_stimulus.intensity", lang),
            evidence=str(data["evidence"]),
        )


@dataclass
class BodyReaction:
    id: str
    intensity: str
    reason: str

    @classmethod
    def from_dict(cls, data: dict, lang: str = LANG_EN) -> "BodyReaction":
        _require_keys(data, ["id", "intensity", "reason"], "body_reaction", lang)
        return cls(
            id=_require_choice(
                _require_non_empty_string(data["id"], "body_reaction.id", lang),
                BODY_REACTION_IDS,
                "body_reaction.id",
                lang,
            ),
            intensity=_require_choice(str(data["intensity"]), INTENSITY_LEVELS, "body_reaction.intensity", lang),
            reason=str(data["reason"]),
        )


@dataclass
class AnalysisInput:
    analysis_target: str
    context_summary: ContextSummary
    semantic_stimuli: List[SemanticStimulus]
    body_reactions: List[BodyReaction]

    @classmethod
    def from_dict(cls, data: dict, lang: str = LANG_EN) -> "AnalysisInput":
        _require_keys(
            data,
            [
                "analysis_target",
                "context_summary",
                "semantic_stimuli",
                "body_reactions",
            ],
            "analysis_input",
            lang,
        )
        semantic_stimuli = [
            SemanticStimulus.from_dict(item, lang=lang)
            for item in _require_list(data["semantic_stimuli"], "semantic_stimuli", lang)
        ]
        body_reactions = [
            BodyReaction.from_dict(item, lang=lang) for item in _require_list(data["body_reactions"], "body_reactions", lang)
        ]
        if not semantic_stimuli:
            raise ValueError(semantic_stimuli_min(lang))
        if not body_reactions:
            raise ValueError(body_reactions_min(lang))
        return cls(
            analysis_target=_require_non_empty_string(data["analysis_target"], "analysis_target", lang),
            context_summary=ContextSummary.from_dict(data["context_summary"], lang=lang),
            semantic_stimuli=semantic_stimuli,
            body_reactions=body_reactions,
        )

    def to_dict(self) -> dict:
        return {
            "analysis_target": self.analysis_target,
            "context_summary": asdict(self.context_summary),
            "semantic_stimuli": [asdict(item) for item in self.semantic_stimuli],
            "body_reactions": [asdict(item) for item in self.body_reactions],
        }


@dataclass
class BodyStateChange:
    trend: str
    score: int

    @classmethod
    def stable(cls) -> "BodyStateChange":
        return cls(trend="stable", score=0)

    def to_dict(self) -> dict:
        return {
            "trend": _require_choice(self.trend, BODY_TRENDS, "body_state_change.trend", LANG_EN),
            "score": self.score,
        }


@dataclass
class MappingResult:
    analysis_target: str
    context_summary: ContextSummary
    semantic_stimuli: List[SemanticStimulus]
    body_reactions: List[BodyReaction]
    body_contributors: Dict[str, List[str]]
    body_scores: Dict[str, int]
    body_state_changes: Dict[str, BodyStateChange]
    turn_change_tags: List[str]
    body_tag: str
    emotional_prompt_payload: Dict[str, Any]
    updated_bodies: Dict[str, int]
    turn_trace: Dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "analysis_target": self.analysis_target,
            "context_summary": asdict(self.context_summary),
            "semantic_stimuli": [asdict(item) for item in self.semantic_stimuli],
            "body_reactions": [asdict(item) for item in self.body_reactions],
            "body_contributors": {name: list(items) for name, items in self.body_contributors.items()},
            "body_scores": dict(self.body_scores),
            "body_state_changes": {name: change.to_dict() for name, change in self.body_state_changes.items()},
            "TURN_CHANGE_TAGS": list(self.turn_change_tags),
            "BODY_TAG": self.body_tag,
            "emotional_prompt_payload": dict(self.emotional_prompt_payload),
            "updated_bodies": dict(self.updated_bodies),
            "turn_trace": dict(self.turn_trace),
        }
