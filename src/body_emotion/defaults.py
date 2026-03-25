from __future__ import annotations

from typing import Dict

from .schema import BODIES, PhaseState, Profile, State, Traits

# 非 CLI/bootstrap 入口使用（本地面板、无状态 Engine、单测）；运行时须通过命令行传入 agent。
INTERNAL_DEFAULT_AGENT_ID = "internal"
INTERNAL_DEFAULT_NAME = "Internal"


def default_body_constitution() -> Dict[str, PhaseState]:
    """五脏持久状态默认值。"""
    return {
        "liver": PhaseState(baseline=52, current=52, fragility=0.48),
        "heart": PhaseState(baseline=61, current=61, fragility=0.78),
        "spleen": PhaseState(baseline=61, current=61, fragility=0.55),
        "lung": PhaseState(baseline=58, current=58, fragility=0.63),
        "kidney": PhaseState(baseline=59, current=59, fragility=0.72),
    }


def default_state(agent_id: str, name: str) -> State:
    bodies = default_body_constitution()
    assert set(bodies.keys()) == set(BODIES)
    return State(
        profile=Profile(agent_id=agent_id, name=name),
        bodies=bodies,
        traits=Traits(overall_fragility=1.0, attachment_style="dependent_soft", default_expression="gentle"),
    )
