from __future__ import annotations

from pathlib import Path


def resolve_state_path(state: str | None, workspace: str | None, agent_id: str) -> Path:
    if state:
        return Path(state).expanduser().resolve()
    if workspace:
        return Path(workspace).expanduser().resolve() / 'body-emotion-state' / f'{agent_id}.json'
    return Path('state') / f'{agent_id}.json'
