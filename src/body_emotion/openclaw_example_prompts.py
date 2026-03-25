from __future__ import annotations

from .locale_config import LANG_ZH, normalize_lang

OPENCLAW_AGENTS_EXAMPLE_ZH = r"""# 示例：OpenClaw `AGENTS.md` 约定（中文）

这是一个给 OpenClaw 用的参考示例。把其中的 `<...>` 占位符替换成你的实际值后，再写入当前智能体自己的系统提示词。

## 作用

定义 OpenClaw 智能体必须如何：

1. 在新会话开始时执行 body-emotion-sensor 的启动流程。
2. 在每条用户消息到来后执行 AnalysisInput 流程。

## 新会话启动流程（首条 assistant 回复之前）

1. 按你自己的工作区约定先读取必要文件，例如 identity、memory、tools 等。
2. 在输出第一条 assistant 回复之前，运行：

```bash
bes bootstrap \
  --workspace <AGENT_WORKSPACE> \
  --agent-id <AGENT_ID> \
  --name "<DISPLAY_NAME>"
```

3. 不要直接读取原始 state JSON 来替代 bootstrap。
4. 从 bootstrap 的 stdout 中读取这些顶层字段：
   - `TURN_CHANGE_TAGS`
   - `BODY_TAG`
   - `BASELINE_PERSONA`
5. 启动阶段不需要 AnalysisInput JSON，不要在新会话启动时调用 `bes run`。

## 固定运行约定

- 运行时只使用安装后的 CLI：`bes`
- 不要在运行时直接读取仓库里的 `.py` 提示词文件
- 不要把仓库文档路径当成运行时依赖

## 每条用户消息的固定流程

每次用户发来新消息、且你要生成 assistant 回复前：

1. 先运行 `bes prompt analysis-input`
2. 把输出的提示词交给上游分析模型，产出一份 AnalysisInput JSON
3. 再运行：

```bash
bes run \
  --workspace <AGENT_WORKSPACE> \
  --agent-id <AGENT_ID> \
  --name "<DISPLAY_NAME>" \
  --json '<AnalysisInput-JSON>'
```

4. 默认 stdout 会返回一个简化 JSON，包含：
   - `TURN_CHANGE_TAGS`
   - `BODY_TAG`
   - `BASELINE_PERSONA`
5. 先让回复遵循 `BODY_TAG`，再把 `TURN_CHANGE_TAGS` 作为本轮变化方向的补充信号；`BASELINE_PERSONA` 用来维持角色长期人格底色。
6. 除非你的工程明确升级了协议，否则不要只靠原始 state 文件、遗留字段，或单独一份 `--full` 输出去决定语气层。"""

OPENCLAW_TOOLS_EXAMPLE_ZH = r"""# 示例：OpenClaw `TOOLS.md` 约定（中文）

这是一个给 OpenClaw 用的参考示例。它应该是一份简短速查表，而不是长教程。

## 这个文件应该告诉 AI 什么

- OpenClaw 的主工作区路径
- 当前 agent 的工作区路径
- body-emotion-sensor 的持久化 state 存放位置
- body-emotion-sensor skill 或安装位置
- 运行时应该使用哪些 CLI 命令
- 怎么打印内置 prompt

## 建议记录的路径示例

- 主工作区：`~/.openclaw/workspace`
- 当前 agent 工作区：`~/.openclaw/workspace/agents/<AGENT_ID>`
- 长期情绪状态文件：`~/.openclaw/workspace/agents/<AGENT_ID>/body-emotion-state/<AGENT_ID>.json`
- skill 目录：`~/.openclaw/workspace/skills/body-emotion-sensor`

## body-emotion-sensor 运行摘要

- 运行入口：`bes`
- 查看分析 prompt：`bes prompt analysis-input`
- 查看初始化 prompt：`bes prompt init`
- 查看 OpenClaw 示例：`bes prompt openclaw-example`
- 新会话启动：`bes bootstrap --workspace <W> --agent-id <ID> --name "<NAME>"`
- 每条用户消息前运行：`bes run --workspace <W> --agent-id <ID> --name "<NAME>" --json '<AnalysisInput-JSON>'`
- 初始化检查：`bes check-init --workspace <W> --agent-id <ID> --name "<NAME>"`
- 推荐安装：`pip install body-emotion-sensor` 或 `pip install -e <REPO_ROOT>`

## 默认 stdout 协议

`bes bootstrap` 和默认模式下的 `bes run` 都会输出这些字段：

- `TURN_CHANGE_TAGS`
- `BODY_TAG`
- `BASELINE_PERSONA`

## 运行时限制

- 不要把仓库路径当成运行时 prompt 来源
- 不要直接调用仓库里的其他 `.py` 文件作为临时入口
- 按照当前安装的 `bes` 命令来运行"""

OPENCLAW_AGENTS_EXAMPLE_EN = r"""# Example: OpenClaw `AGENTS.md` conventions

This is a reference example for OpenClaw. Replace the `<...>` placeholders with your real values before writing it into the current agent's system prompt.

## Purpose

Define how an OpenClaw agent must:

1. Run the body-emotion-sensor startup flow at the beginning of a new session.
2. Run the AnalysisInput flow for every user message.

## New-session startup flow (before the first assistant reply)

1. Read your required workspace files first, such as identity, memory, and tools.
2. Before the first assistant reply, run:

```bash
bes bootstrap \
  --workspace <AGENT_WORKSPACE> \
  --agent-id <AGENT_ID> \
  --name "<DISPLAY_NAME>"
```

3. Do not substitute the raw state JSON for bootstrap.
4. From bootstrap stdout, read these top-level fields:
   - `TURN_CHANGE_TAGS`
   - `BODY_TAG`
   - `BASELINE_PERSONA`
5. Startup does not require AnalysisInput JSON. Do not call `bes run` during new-session boot.

## Fixed runtime rules

- Use only the installed `bes` CLI at runtime
- Do not read raw repository `.py` prompt files at runtime
- Do not rely on repository doc paths as runtime dependencies

## Per-user-message flow

For every new user message, before you produce the assistant reply:

1. Run `bes prompt analysis-input`
2. Feed that prompt to your upstream analysis model and produce an AnalysisInput JSON
3. Then run:

```bash
bes run \
  --workspace <AGENT_WORKSPACE> \
  --agent-id <AGENT_ID> \
  --name "<DISPLAY_NAME>" \
  --json '<AnalysisInput-JSON>'
```

4. Default stdout returns a compact JSON object containing:
   - `TURN_CHANGE_TAGS`
   - `BODY_TAG`
   - `BASELINE_PERSONA`
5. Let the reply follow `BODY_TAG` first, use `TURN_CHANGE_TAGS` as the current-turn adjustment signal, and keep `BASELINE_PERSONA` as the long-term personality color.
6. Unless your project upgrades that contract explicitly, do not rely on the raw state file, legacy fields, or a `--full` dump alone as the tone source."""

OPENCLAW_TOOLS_EXAMPLE_EN = r"""# Example: OpenClaw `TOOLS.md` conventions

This is a reference example for OpenClaw. It should stay a short cheat sheet instead of becoming a long tutorial.

## What this file should tell the AI

- The main OpenClaw workspace path
- The current agent workspace path
- Where the persistent body-emotion state is stored
- Where the body-emotion-sensor skill or install lives
- Which CLI commands are canonical at runtime
- How to print built-in prompts

## Suggested path examples

- Main workspace: `~/.openclaw/workspace`
- Current agent workspace: `~/.openclaw/workspace/agents/<AGENT_ID>`
- Long-term emotion state: `~/.openclaw/workspace/agents/<AGENT_ID>/body-emotion-state/<AGENT_ID>.json`
- Skill directory: `~/.openclaw/workspace/skills/body-emotion-sensor`

## body-emotion-sensor runtime summary

- Runtime entry point: `bes`
- Show analysis prompt: `bes prompt analysis-input`
- Show init prompt: `bes prompt init`
- Show OpenClaw examples: `bes prompt openclaw-example`
- New-session bootstrap: `bes bootstrap --workspace <W> --agent-id <ID> --name "<NAME>"`
- Per-message run: `bes run --workspace <W> --agent-id <ID> --name "<NAME>" --json '<AnalysisInput-JSON>'`
- Init check: `bes check-init --workspace <W> --agent-id <ID> --name "<NAME>"`
- Recommended install: `pip install body-emotion-sensor` or `pip install -e <REPO_ROOT>`

## Default stdout contract

Both `bes bootstrap` and the default output of `bes run` contain:

- `TURN_CHANGE_TAGS`
- `BODY_TAG`
- `BASELINE_PERSONA`

## Runtime constraints

- Do not use repository paths as runtime prompt sources
- Do not invoke other repository `.py` files as ad-hoc entry points
- Use the installed `bes` command for runtime integration"""


def get_openclaw_example_text(lang: str | None = None) -> str:
    lg = normalize_lang(lang)
    if lg == LANG_ZH:
        agents = OPENCLAW_AGENTS_EXAMPLE_ZH
        tools = OPENCLAW_TOOLS_EXAMPLE_ZH
    else:
        agents = OPENCLAW_AGENTS_EXAMPLE_EN
        tools = OPENCLAW_TOOLS_EXAMPLE_EN
    return (
        "[AGENTS EXAMPLE]\n"
        f"{agents}\n\n"
        "[TOOLS EXAMPLE]\n"
        f"{tools}"
    )
