from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

LANG_EN = "en"
LANG_ZH = "zh"


def normalize_lang(value: str | None) -> str:
    if value is None:
        return LANG_EN
    v = str(value).strip().lower().replace("_", "-")
    if v in ("zh", "zh-cn", "zh-hans", "chs"):
        return LANG_ZH
    if v in ("en", "en-us", "en-gb"):
        return LANG_EN
    return LANG_EN


def user_config_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / "bes"
        return Path.home() / "AppData" / "Roaming" / "bes"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "bes"
    return Path.home() / ".config" / "bes"


def user_config_path() -> Path:
    return user_config_dir() / "config.json"


def _read_config_file() -> dict[str, Any]:
    path = user_config_path()
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _language_from_file() -> str | None:
    lang = _read_config_file().get("language")
    if lang is None:
        return None
    return normalize_lang(str(lang))


def set_user_language(lang: str) -> Path:
    """Persist language to user config. Returns path written."""
    code = normalize_lang(lang)
    if code not in (LANG_EN, LANG_ZH):
        code = LANG_EN
    d = user_config_dir()
    d.mkdir(parents=True, exist_ok=True)
    path = user_config_path()
    data = _read_config_file()
    data["language"] = code
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def resolve_language(*, cli_override: str | None = None) -> str:
    """Order: CLI > BES_LANGUAGE env > user config file > default en."""
    if cli_override is not None and str(cli_override).strip():
        return normalize_lang(cli_override)
    env = os.environ.get("BES_LANGUAGE")
    if env is not None and str(env).strip():
        return normalize_lang(env)
    from_file = _language_from_file()
    if from_file is not None:
        return from_file
    return LANG_EN
