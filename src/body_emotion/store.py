from __future__ import annotations

import json
from pathlib import Path

from .schema import State


def _history_path(state_path: Path) -> Path:
    """与主 state 同目录下 history/<basename>.json，仅存放 history 数组。"""
    return state_path.parent / "history" / f"{state_path.stem}.json"


def state_files_signature(path: str | Path) -> tuple[tuple[str, int, int], ...]:
    """主 state 与 history 侧文件的稳定签名；用于更稳健的热更新检测。"""
    p = Path(path).expanduser().resolve()
    entries: list[tuple[str, int, int]] = []
    if p.is_file():
        stat = p.stat()
        entries.append((str(p), int(stat.st_mtime_ns), int(stat.st_size)))
    hp = _history_path(p)
    if hp.is_file():
        stat = hp.stat()
        entries.append((str(hp), int(stat.st_mtime_ns), int(stat.st_size)))
    return tuple(entries)


def state_files_mtime(path: str | Path) -> float | None:
    """主 state 与 history 侧文件变更时间的较大值；用于外部进程只改其一时的热更新检测。"""
    p = Path(path).expanduser().resolve()
    times: list[float] = []
    if p.is_file():
        times.append(p.stat().st_mtime)
    hp = _history_path(p)
    if hp.is_file():
        times.append(hp.stat().st_mtime)
    if not times:
        return None
    return max(times)


def save_state(state: State, path: str | Path) -> None:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(state.to_snapshot_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    hp = _history_path(p)
    hp.parent.mkdir(parents=True, exist_ok=True)
    hp.write_text(json.dumps(state.history, ensure_ascii=False, indent=2), encoding="utf-8")


def load_state(path: str | Path) -> State:
    p = Path(path).expanduser().resolve()
    raw = json.loads(p.read_text(encoding="utf-8"))
    inline = raw.get("history")
    data = {k: v for k, v in raw.items() if k != "history"}
    state = State.from_dict({**data, "history": []})
    hp = _history_path(p)
    if hp.is_file():
        hist_raw = json.loads(hp.read_text(encoding="utf-8"))
        state.history = list(hist_raw) if isinstance(hist_raw, list) else []
    elif inline is not None:
        state.history = list(inline) if isinstance(inline, list) else []
    return state
