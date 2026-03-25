# Body Emotion Sensor

Give your AI agent a persistent emotional system based on the TCM Five Zang and Five Elements model.

[简体中文](https://github.com/AskKumptenchen/body-emotion-sensor/blob/main/docs/README.zh-CN.md)

## What It Does

`body-emotion-sensor` converts one turn of structured emotional analysis JSON into:

- persistent body-axis state updates
- a compact prompt payload for reply shaping
- traceable state/history data for debugging

It distinguishes between:

- `baseline`: the agent's native constitution and long-term personality color
- `current`: the body state after the latest turn

## Install

```bash
pip install body-emotion-sensor
```

For the visualization panel:

```bash
pip install body-emotion-sensor[viz]
```

After installation you can use either command:

```bash
bes help
body-emotion-sensor help
```

## CLI Overview

```bash
bes help
bes prompt init
bes prompt openclaw-example
bes prompt analysis-input
bes init-state --workspace /path/to/workspace --agent-id my-agent --name "My Agent"
bes init-state --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --init-json /path/to/init.json
bes check-init --workspace /path/to/workspace --agent-id my-agent --name "My Agent"
bes bootstrap --workspace /path/to/workspace --agent-id my-agent --name "My Agent"
bes run --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --input /path/to/analysis-input.json
bes run --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --json '{"analysis_target":"...", "...":"..."}'
bes panel --workspace /path/to/workspace --agent-id my-agent
```

## Recommended Flow

1. Print the constitution initialization prompt.
2. Use your upstream model to generate the role init JSON.
3. Write the long-term state.
4. If the host is OpenClaw, print the OpenClaw examples and update AGENTS / TOOLS separately.
5. Run `bes check-init` to confirm the code-level setup is ready.
6. For each new session, run `bes bootstrap` before the first assistant reply.
7. For each turn, generate `AnalysisInput` JSON upstream.
8. Run one update and use the returned prompt payload in your reply layer.

Example:

```bash
bes prompt init
bes init-state --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --init-json /path/to/init.json
bes prompt openclaw-example
bes check-init --workspace /path/to/workspace --agent-id my-agent --name "My Agent"
bes bootstrap --workspace /path/to/workspace --agent-id my-agent --name "My Agent"
bes prompt analysis-input
bes run --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --input /path/to/analysis-input.json
```

## Output Contract

The default stdout of `bes bootstrap` and `bes run` contains:

- `TURN_CHANGE_TAGS`
- `BODY_TAG`
- `BASELINE_PERSONA`

Use `bes run --full` when you need the complete `MappingResult`.

## Runtime Prompt Access

The package does not ship internal repository docs such as `docs/` or `prompts/` as install-time resources.

If you need the built-in prompt texts after `pip install`, use:

```bash
bes prompt init
bes prompt openclaw-example
bes prompt analysis-input
```

This keeps runtime integrations independent from repository directory traversal.

## Development

For local development:

```bash
pip install -e .
python -m body_emotion help
```

Optional visualization panel:

```bash
bes panel --workspace /path/to/workspace --agent-id my-agent
```

Repository-only docs remain in the source repo, for example:

- `docs/五脏情绪映射全表.md`
- `docs/五脏情绪七阶状态表.md`
- `prompts/example-openclaw-agents.md`
- `prompts/example-openclaw-tools.md`

## License

MIT. See `LICENSE`.
