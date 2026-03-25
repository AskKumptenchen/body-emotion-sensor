# Body Emotion Sensor

给你的 AI Agent 接入一套可持久化的情感系统，基于中医五脏与五行模型。

[English](https://github.com/AskKumptenchen/body-emotion-sensor/blob/main/README.md)

## 它能做什么

`body-emotion-sensor` 会把单轮结构化情感分析 JSON 转成：

- 可持久化的五脏状态更新
- 给回复层直接使用的精简提示载荷
- 便于调试的 state/history 轨迹数据

它明确区分：

- `baseline`：角色原始体质与长期人格底色
- `current`：最新一轮更新后的身体状态

## 安装

```bash
pip install body-emotion-sensor
```

如果要使用可视化面板，请安装：

```bash
pip install body-emotion-sensor[viz]
```

安装后可直接使用：

```bash
bes help
body-emotion-sensor help
```

## CLI 总览

```bash
bes help
bes init-prompt
bes prompt analysis-input
bes init-state --workspace /path/to/workspace --agent-id my-agent --name "My Agent"
bes init-state --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --init-json /path/to/init.json
bes bootstrap --workspace /path/to/workspace --agent-id my-agent --name "My Agent"
bes run --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --input /path/to/analysis-input.json
bes run --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --json '{"analysis_target":"...", "...":"..."}'
```

## 推荐使用流程

1. 先打印角色体质初始化提示词。
2. 让上游模型产出角色初始化 JSON。
3. 写入长期状态。
4. 每一轮先让上游模型生成 `AnalysisInput` JSON。
5. 再执行 `bes run`，把输出结果接到回复层。

示例：

```bash
bes init-prompt
bes init-state --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --init-json /path/to/init.json
bes prompt analysis-input
bes run --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --input /path/to/analysis-input.json
```

## 默认输出契约

`bes bootstrap` 和 `bes run` 默认 stdout 包含：

- `TURN_CHANGE_TAGS`
- `BODY_TAG`
- `BASELINE_PERSONA`

如果你需要完整 `MappingResult`，请使用：

```bash
bes run --full ...
```

## 运行时提示词获取

安装包不会把仓库里的 `docs/`、`prompts/` 等 Markdown 作为运行时资源分发。

如果你在 `pip install` 后还需要提示词文本，请直接通过命令输出：

```bash
bes init-prompt
bes prompt analysis-input
```

这样运行时集成就不需要依赖安装目录遍历。

## 开发使用

本地开发可这样安装：

```bash
pip install -e .
python -m body_emotion help
```

可视化面板：

```bash
bes panel --workspace /path/to/workspace --agent-id my-agent
```

以下文档保留在源码仓库中，主要面向仓库开发与集成参考：

- `docs/五脏情绪映射全表.md`
- `docs/五脏情绪七阶状态表.md`
- `docs/example-openclaw-agents.md`
- `docs/example-openclaw-tools.md`

## License

MIT，见仓库根目录 `LICENSE`。
