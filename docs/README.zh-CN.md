<h1 align="center">🫀 Body Emotion Sensor</h1>

<p align="center">
  给你的 AI Agent 接入一套可持久化的情感系统，基于中医五脏与五行模型。
</p>

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue" />
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-brightgreen" />
  <img alt="GitHub stars" src="https://img.shields.io/github/stars/AskKumptenchen/body-emotion-sensor?style=flat" />
</p>

<p align="center">
  <a href="#quick-start">快速开始</a> ·
  <a href="#features">核心功能</a> ·
  <a href="#how-it-works">工作原理</a> ·
  <a href="../README.md">English</a>
</p>

## 为什么需要 Body Emotion Sensor？ 💖

你是否觉得，现在的 AI 智能体缺乏真正的“内在自我”？它们或许能在文字中模拟情绪，但并没有一个能在多次对话中延续的内部状态。

**Body Emotion Sensor 旨在改变这一点：**

- **持久化状态：** 赋予 AI 一个长期的身心情志体质（baseline），并让它自然演化。
- **五脏五行模型：** 基于中医五行（金、木、水、火、土）理论，将复杂的情绪状态映射到五脏系统中。
- **逐轮状态更新：** 将结构化的情感分析转化为实时的身体状态更新，从而潜移默化地影响智能体的回复风格。

<a id="quick-start"></a>

## 快速开始 🚀

📥 **安装：**

```bash
pip install body-emotion-sensor
```

默认安装已包含可视化面板依赖。安装后可直接使用 CLI：

```bash
bes help
body-emotion-sensor help
```

🔄 **推荐使用流程：**

1. 打印体质初始化提示词：`bes init-prompt`
2. 初始化状态：`bes init-state --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --init-json /path/to/init.json`
3. 检查是否就绪：`bes check-init --workspace /path/to/workspace --agent-id my-agent --name "My Agent"`
4. 启动新会话：`bes bootstrap --workspace /path/to/workspace --agent-id my-agent --name "My Agent"`
5. 执行单轮更新：`bes run --workspace /path/to/workspace --agent-id my-agent --name "My Agent" --input /path/to/analysis-input.json`

<a id="features"></a>

## 核心功能 🧩

- **状态持久化：** 按工作区和智能体 ID 存储长期的身心情绪状态。
- **会话引导（Bootstrap）：** 在新会话开始前，生成 `TURN_CHANGE_TAGS`、`BODY_TAG` 和 `BASELINE_PERSONA`。
- **精简提示载荷：** 为回复层提供轻量级的提示词注入，不占用过多上下文窗口。
- **可追溯历史：** 保留完整的 state/history 轨迹数据，便于调试与可视化。
- **可视化面板：** 运行 `bes panel` 直观查看智能体的情感变化轨迹。

<img src="./panel.png" alt="可视化面板" width="600" />

<a id="how-it-works"></a>

## 工作原理 ✨

`body-emotion-sensor` 明确区分两个核心概念：
- **`baseline`**：角色的原始体质与长期人格底色。
- **`current`**：最新一轮更新后的身体状态，受近期交互影响。

它会把单轮结构化情感分析 JSON 转成可持久化的五脏状态更新，以及给回复层直接使用的精简提示载荷。

## 开发使用 🛠️

本地开发可这样安装：

```bash
pip install -e .
bes help
```

启动可视化面板：

```bash
bes panel --workspace /path/to/workspace --agent-id my-agent
```

以下文档保留在源码仓库中，主要面向仓库开发与集成参考：
- `docs/五脏情绪映射全表.md`
- `docs/五脏情绪七阶状态表.md`
- `docs/example-openclaw-agents.md`
- `docs/example-openclaw-tools.md`

## License 📄

本项目使用仓库根目录 `LICENSE` 中的 `MIT` 协议。
