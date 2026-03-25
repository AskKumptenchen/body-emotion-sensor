from __future__ import annotations

from .locale_config import LANG_EN, LANG_ZH, normalize_lang


def _lg(lang: str | None) -> str:
    return normalize_lang(lang)


def missing_keys(lang: str, label: str, missing: list[str]) -> str:
    lg = _lg(lang)
    keys = ", ".join(missing)
    if lg == LANG_ZH:
        return f"{label} 缺少字段: {keys}"
    return f"{label} missing keys: {keys}"


def must_be_one_of(lang: str, label: str, choices: set[str], value: str) -> str:
    lg = _lg(lang)
    opts = ", ".join(repr(x) for x in sorted(choices))
    if lg == LANG_ZH:
        return f"{label} 必须是 [{opts}] 之一，当前是 {value!r}"
    return f"{label} must be one of [{opts}], got {value!r}"


def must_be_array(lang: str, label: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return f"{label} 必须是数组"
    return f"{label} must be an array"


def must_be_non_empty(lang: str, label: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return f"{label} 不能为空"
    return f"{label} must be non-empty"


def semantic_stimuli_min(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "semantic_stimuli 至少需要 1 项"
    return "semantic_stimuli must contain at least 1 item"


def body_reactions_min(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "body_reactions 至少需要 1 项"
    return "body_reactions must contain at least 1 item"
