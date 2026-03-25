# Example: OpenClaw `TOOLS.md` conventions (English)

This document is a **reference example** in English. It mirrors the summary block added to `asks-chat/TOOLS.md` for local path and CLI entry expectations. Replace placeholders when you adapt it.

---

## What belongs in `TOOLS.md`

A short cheat sheet the agent should read for:

- OpenClaw workspace roots
- Where **persistent body-emotion state** is stored
- Where the **skill** is installed
- Which installed **CLI commands** are canonical
- How to print built-in runtime prompts

Avoid long tutorials; keep paths and commands copy-paste friendly.

---

## Example workspace paths

| Item | Example |
|------|---------|
| Main OpenClaw workspace | `~/.openclaw/workspace` |
| This agent’s workspace | `~/.openclaw/workspace/agents/<AGENT_ID>` |
| Long-term emotion state (engine persistence) | `~/.openclaw/workspace/agents/<AGENT_ID>/body-emotion-state/<AGENT_ID>.json` |
| Skill directory | `~/.openclaw/workspace/skills/body-emotion-sensor` |

Optional: list non-runtime drafts under your repo (e.g. init/output JSON snapshots) if they help debugging — mark them as **not required at runtime**.

---

## body-emotion-sensor (summary)

| Item | Value |
|------|--------|
| Runtime entry point | `bes` |
| Analysis prompt export | `bes prompt analysis-input` |
| Init prompt export | `bes prompt init` |
| Bootstrap (session start) | `bes bootstrap` (+ fixed `--workspace` / `--agent-id` / `--name`) |
| Main sensor (each user message) | `bes run` (+ same fixed args + `--json` or `--input`) |
| Recommended one-time setup | `pip install body-emotion-sensor` or `pip install -e <REPO_ROOT>` |

Default stdout contract for both bootstrap and CLI:

- `TURN_CHANGE_TAGS`
- `BODY_TAG`
- `BASELINE_PERSONA`

**Do not** use repository file paths as runtime prompt sources, and do not invoke other `.py` files as ad-hoc entry points; follow `skill/body-emotion-sensor/SKILL.md`.

---

## Optional constraints section

You can add agent-specific constraints (e.g. “no image pipeline yet”, “no `send.py`”) in the same file so the model does not assume unconfigured tools exist.

---

*This file is documentation only; the binding paths for `asks-chat` live in `asks-chat/TOOLS.md`.*
