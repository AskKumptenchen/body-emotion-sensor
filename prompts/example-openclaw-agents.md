# Example: OpenClaw `AGENTS.md` conventions (English)

This document is a **reference example** in English. It mirrors the structure and rules used in `asks-chat/AGENTS.md` after the body-emotion-sensor workflow update. Replace placeholders (`<...>`) when you copy it for another agent or machine.

---

## Purpose

Define how an OpenClaw agent must:

1. **Bootstrap** a new session.
2. On **every user message**, run the **AnalysisInput** pipeline via **`bes`**.

---

## Session boot (first reply of a new session)

1. Read workspace files in your agreed order (e.g. soul, identity, user, tools, memory).
2. **Before** the first assistant line, run **bootstrap**.
3. Run:

   ```bash
   bes bootstrap \
     --workspace <AGENT_WORKSPACE> \
     --agent-id <AGENT_ID> \
     --name "<DISPLAY_NAME>"
   ```

4. Do not substitute reading the raw state JSON for bootstrap.

5. From bootstrap stdout, read:

   - `TURN_CHANGE_TAGS`
   - `BODY_TAG`
   - `BASELINE_PERSONA`

6. Bootstrap does **not** require AnalysisInput JSON. Do not call `bes run` during startup.

---

## Fixed paths (example layout)

| Role | Example path |
|------|----------------|
| Skill bundle | `~/.openclaw/workspace/skills/body-emotion-sensor` (contains `SKILL.md`) |
| Installed CLI | `bes` |
| Analysis prompt | `bes prompt analysis-input` |
| Persistent state | `<AGENT_WORKSPACE>/body-emotion-state/<AGENT_ID>.json` |

**Runtime rule:** use the installed `bes` CLI only. Do not read prompt files from repository paths or invoke random `.py` files inside the repo.

---

## Mandatory arguments for every sensor run

Always pass:

- `--workspace <AGENT_WORKSPACE>`
- `--agent-id <AGENT_ID>`
- `--name "<DISPLAY_NAME>"`

---

## Per-message flow (after boot)

For **each** user message:

1. Run `bes prompt analysis-input` and feed that text to your upstream analysis model.
2. Produce **AnalysisInput JSON** (matches `schema.AnalysisInput`).
3. Run:

   ```bash
   bes run \
     --workspace <AGENT_WORKSPACE> \
     --agent-id <AGENT_ID> \
     --name "<DISPLAY_NAME>" \
     --json '<AnalysisInput-JSON>'
   ```

   Default stdout is a small JSON object with `TURN_CHANGE_TAGS`, `BODY_TAG`, and `BASELINE_PERSONA`. For debugging or tooling that needs the full `MappingResult`, add `--full`.

4. From CLI stdout, for reply shaping use these top-level fields:

   - `TURN_CHANGE_TAGS`
   - `BODY_TAG`
   - `BASELINE_PERSONA`

5. Treat `BASELINE_PERSONA` as the agent's long-term personality color. Let the reply follow `BODY_TAG` first, and use `TURN_CHANGE_TAGS` as the current-turn adjustment signal.

6. Do not use the raw state file, a `--full` JSON dump alone, or legacy fields as the sole source for tone unless your project explicitly upgrades to that contract.

---

## Reply principles (summary)

- Long-term bodily / comfort layer dominates; current-turn stimulus adjusts, not overrides.
- Do not inflate one turn into the whole emotional story.

---

*This file is documentation only; the binding workspace rules for `asks-chat` live in `asks-chat/AGENTS.md`.*
