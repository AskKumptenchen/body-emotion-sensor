from __future__ import annotations

from pathlib import Path

from .locale_config import LANG_EN, LANG_ZH, normalize_lang


def _lg(lang: str | None) -> str:
    return normalize_lang(lang)


def main_description(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "五脏情绪传感器统一命令行。"
    return "Unified Body Emotion Sensor CLI."


def main_epilog(prog: str, lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return f"""
常用命令:
  {prog} help
  {prog} prompt init
  {prog} prompt openclaw-example
  {prog} prompt analysis-input
  {prog} init-state --workspace <W> --agent-id <ID> --name "<NAME>" --init-json <init.json>
  {prog} check-init --workspace <W> --agent-id <ID> --name "<NAME>"
  {prog} bootstrap --workspace <W> --agent-id <ID> --name "<NAME>"
  {prog} run --workspace <W> --agent-id <ID> --name "<NAME>" --input <analysis-input.json>
  {prog} panel --workspace <W> --agent-id <ID>
""".strip()
    return f"""
Common commands:
  {prog} help
  {prog} prompt init
  {prog} prompt openclaw-example
  {prog} prompt analysis-input
  {prog} init-state --workspace <W> --agent-id <ID> --name "<NAME>" --init-json <init.json>
  {prog} check-init --workspace <W> --agent-id <ID> --name "<NAME>"
  {prog} bootstrap --workspace <W> --agent-id <ID> --name "<NAME>"
  {prog} run --workspace <W> --agent-id <ID> --name "<NAME>" --input <analysis-input.json>
  {prog} panel --workspace <W> --agent-id <ID>
""".strip()


def help_language_flag(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "界面与输出语言：en 或 zh（覆盖 BES_LANGUAGE 与配置文件）。"
    return "UI and output language: en or zh (overrides BES_LANGUAGE and config file)."


def help_help(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "显示主帮助或子命令帮助"
    return "Show main help or subcommand help"


def help_help_topic(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "要查看帮助的子命令"
    return "Subcommand to show help for"


def help_init_prompt(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "打印角色体质初始化提示词"
    return "Print the role initialization prompt"


def help_prompt(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "打印内置运行时提示词"
    return "Print a built-in runtime prompt"


def help_prompt_name(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "提示词名称：analysis-input、init、openclaw-example"
    return "Prompt name: analysis-input, init, or openclaw-example"


def help_init_state(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "初始化或覆盖持久化状态"
    return "Initialize or overwrite persistent state"


def help_bootstrap(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "根据当前状态输出最小提示载荷 JSON"
    return "Print the minimal prompt payload for current state"


def help_run(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "处理一条 AnalysisInput 并更新状态"
    return "Process one AnalysisInput payload and update state"


def help_check_init(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "检查初始化是否就绪（参数、路径、state 结构）"
    return "Check whether initialization is ready (args, paths, and state)"


def help_state(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "显式 state 文件路径"
    return "Explicit state file path"


def help_workspace(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "智能体工作区根目录"
    return "Agent workspace root"


def help_agent_id(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "智能体 ID（必填）"
    return "Agent ID (required)"


def help_name(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "展示名（必填）"
    return "Display name (required)"


def help_init_json(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "角色初始化 JSON 文件路径"
    return "Role init JSON file path"


def help_init_json_string(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "内联角色初始化 JSON 字符串"
    return "Inline role init JSON string"


def help_input(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "AnalysisInput JSON 文件路径"
    return "AnalysisInput JSON file path"


def help_json_inline(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "内联 AnalysisInput JSON 字符串"
    return "Inline AnalysisInput JSON string"


def help_full(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "输出完整解释 JSON，而非最小提示载荷"
    return "Print the full interpretation JSON instead of the minimal prompt payload"


def help_language_cmd(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "查看当前语言；或提供 en/zh 写入用户默认语言"
    return "Show current language, or pass en/zh to persist as default"


def help_language_code(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "可选：en 或 zh，写入配置文件作为默认语言"
    return "Optional: en or zh — save as default language in config file"


def help_panel(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "启动可视化调试面板（需要安装 viz 额外依赖）"
    return "Launch the visualization debug panel (requires the viz extra)"


def help_host(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "面板监听地址，默认使用 Streamlit 默认值"
    return "Panel bind address; defaults to Streamlit's default"


def help_port(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "面板端口，默认使用 Streamlit 默认值"
    return "Panel port; defaults to Streamlit's default"


def help_headless(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "无头模式启动，不自动打开浏览器"
    return "Run in headless mode without opening a browser"


def help_topics_list(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return ["prompt", "init-state", "check-init", "bootstrap", "run", "panel", "language"]
    return ["prompt", "init-state", "check-init", "bootstrap", "run", "panel", "language"]


def err_agent_id_required(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "必须提供非空的 --agent-id（与智能体 id 一致，例如 asks-chat）。"
    return "Non-empty --agent-id is required (same as agent id, e.g. asks-chat)."


def err_name_required(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "必须提供非空的 --name（展示名）。"
    return "Non-empty --name (display name) is required."


def err_workspace_required(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "必须提供非空的 --workspace（智能体工作区根目录）。"
    return "Non-empty --workspace (agent workspace root) is required."


def json_parse_error_lines(lang: str, label: str, source: str, exc: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return (
            f"[body_emotion] {label} 无法解析。\n"
            f"来源：{source}\n"
            f"解析错误：{exc}\n"
            "请修正 JSON 后再执行。"
        )
    return (
        f"[body_emotion] Failed to parse {label}.\n"
        f"Source: {source}\n"
        f"Parse error: {exc}\n"
        "Fix the JSON and try again."
    )


def label_role_init_json(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "体质初始化 JSON"
    return "role init JSON"


def label_analysis_input_json(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "结构化情感分析 JSON"
    return "AnalysisInput JSON"


def hint_missing_analysis_input(
    *,
    prog: str,
    state_path: Path,
    workspace: str | None,
    agent_id: str,
    name: str,
    just_created_default_state: bool,
    lang: str,
) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        lines = [
            "[body_emotion] 本步缺少：结构化情感分析 JSON（AnalysisInput）。",
            "",
            "请补其一：",
            '  --input "<analysis-input.json 路径>"',
            "  或",
            '  --json \'<单行或转义后的 JSON 字符串>\'',
            "",
            f"当前状态文件（已解析）：{state_path}",
        ]
        if just_created_default_state:
            lines.extend(
                [
                    "说明：本调用前状态文件不存在，已写入默认体质；若要角色定制体质，请先生成初始化提示词并写入角色体质。",
                    f"  {prog} prompt init",
                    f'  {prog} init-state --workspace ... --agent-id {agent_id} --name "{name}" --init-json <init.json>',
                ]
            )
        else:
            lines.extend(
                [
                    "若尚未做过角色体质初始化，可先：",
                    f"  {prog} prompt init",
                    f'  {prog} init-state --workspace ... --agent-id {agent_id} --name "{name}" --init-json <init.json>',
                ]
            )
        if workspace:
            lines.append("当前已传 --workspace，状态路径由 workspace + agent-id 决定。")
        lines.extend(
            [
                "",
                f"结构化情感分析提示词：{prog} prompt analysis-input",
                f"完整用法：{prog} help",
            ]
        )
        return "\n".join(lines)
    lines = [
        "[body_emotion] This step requires structured AnalysisInput JSON.",
        "",
        "Provide one of:",
        '  --input "<path-to-analysis-input.json>"',
        "  or",
        '  --json \'<single-line or escaped JSON string>\'',
        "",
        f"Resolved state file: {state_path}",
    ]
    if just_created_default_state:
        lines.extend(
            [
                "Note: state file did not exist; default constitution was written. "
                "For a custom profile, generate the init prompt and write role constitution first.",
                f"  {prog} prompt init",
                f'  {prog} init-state --workspace ... --agent-id {agent_id} --name "{name}" --init-json <init.json>',
            ]
        )
    else:
        lines.extend(
            [
                "If you have not initialized the role constitution yet:",
                f"  {prog} prompt init",
                f'  {prog} init-state --workspace ... --agent-id {agent_id} --name "{name}" --init-json <init.json>',
            ]
        )
    if workspace:
        lines.append("With --workspace, the state path is workspace + agent-id.")
    lines.extend(
        [
            "",
            f"Analysis prompt: {prog} prompt analysis-input",
            f"Full usage: {prog} help",
        ]
    )
    return "\n".join(lines)


def msg_initialized(lang: str, path: Path) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return f"initialized: {path}"
    return f"initialized: {path}"


def msg_initialized_from_json(lang: str, path: Path) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return f"initialized_from_json: {path}"
    return f"initialized_from_json: {path}"


def ai_workflow_header(prog: str, lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return f"""
给 AI 的接入流程说明

这个工具用于给智能体维护长期身体-情绪状态，并在运行时输出一份可直接用于回复塑形的最小 prompt 载荷。

初始化阶段：
1. 先查看初始化提示词：`{prog} prompt init`
2. 让上游模型生成角色初始化 JSON
3. 写入长期状态：`{prog} init-state --workspace <W> --agent-id <ID> --name "<NAME>" --init-json <init.json>`
4. 如果宿主框架是 OpenClaw，再查看：`{prog} prompt openclaw-example`
   然后分别根据其中的 AGENTS 示例和 TOOLS 示例修改当前智能体对应的系统提示词
5. 初始化完成后，检查是否就绪：`{prog} check-init --workspace <W> --agent-id <ID> --name "<NAME>"`

运行阶段：
1. 新会话启动、首条 assistant 回复前：`{prog} bootstrap --workspace <W> --agent-id <ID> --name "<NAME>"`
2. 每次用户发来新消息，在生成回复前：
   - 先查看分析提示词：`{prog} prompt analysis-input`
   - 让上游模型产出 AnalysisInput JSON
   - 再运行：`{prog} run --workspace <W> --agent-id <ID> --name "<NAME>" --json '<AnalysisInput-JSON>'`

`bootstrap` 和默认模式下的 `run` 会输出这些顶层字段：
- `TURN_CHANGE_TAGS`
- `BODY_TAG`
- `BASELINE_PERSONA`
""".strip()
    return f"""
AI integration flow

This tool maintains a persistent body-emotion state for the agent and returns a compact runtime prompt payload for reply shaping.

Initialization:
1. Show the init prompt: `{prog} prompt init`
2. Let an upstream model generate the role-init JSON
3. Write the long-term state: `{prog} init-state --workspace <W> --agent-id <ID> --name "<NAME>" --init-json <init.json>`
4. If the host framework is OpenClaw, also inspect: `{prog} prompt openclaw-example`
   Then update the current agent's AGENTS and TOOLS system prompts separately according to those examples
5. When initialization is done, verify readiness: `{prog} check-init --workspace <W> --agent-id <ID> --name "<NAME>"`

Runtime:
1. At new-session startup, before the first assistant reply: `{prog} bootstrap --workspace <W> --agent-id <ID> --name "<NAME>"`
2. For every user message, before generating the reply:
   - Show the analysis prompt: `{prog} prompt analysis-input`
   - Let the upstream model produce AnalysisInput JSON
   - Then run: `{prog} run --workspace <W> --agent-id <ID> --name "<NAME>" --json '<AnalysisInput-JSON>'`

`bootstrap` and the default mode of `run` output these top-level fields:
- `TURN_CHANGE_TAGS`
- `BODY_TAG`
- `BASELINE_PERSONA`
""".strip()


def check_init_ready_prompt(prog: str, workspace: str, agent_id: str, name: str, lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return (
            "代码层初始化检查已通过。"
            f"新会话启动时先运行：{prog} bootstrap --workspace {workspace} --agent-id {agent_id} --name \"{name}\"。"
            f"每次用户消息开始前，先运行：{prog} prompt analysis-input；生成 AnalysisInput JSON 后再运行："
            f"{prog} run --workspace {workspace} --agent-id {agent_id} --name \"{name}\" --json '<AnalysisInput-JSON>'。"
            "如果当前宿主是 OpenClaw，请你自行确认：是否已经分别按 `bes prompt openclaw-example` 中的 AGENTS 和 TOOLS 示例修改了对应系统提示词。"
        )
    return (
        "Code-level initialization checks passed. "
        f"At new-session startup, first run: {prog} bootstrap --workspace {workspace} --agent-id {agent_id} --name \"{name}\". "
        f"Before each reply to a user message, first run: {prog} prompt analysis-input; after AnalysisInput JSON is ready, run: "
        f"{prog} run --workspace {workspace} --agent-id {agent_id} --name \"{name}\" --json '<AnalysisInput-JSON>'. "
        "If the host is OpenClaw, confirm for yourself that you have updated the AGENTS and TOOLS system prompts separately according to `bes prompt openclaw-example`."
    )


def check_init_not_ready_prompt(prog: str, workspace: str, agent_id: str, name: str, lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return (
            f"请先执行：{prog} prompt init，生成角色初始化 JSON 后运行："
            f"{prog} init-state --workspace {workspace} --agent-id {agent_id} --name \"{name}\" --init-json <init.json>。"
            "如果宿主是 OpenClaw，再执行 `bes prompt openclaw-example`，分别修改 AGENTS 和 TOOLS 系统提示词。"
            f"完成后重新执行：{prog} check-init --workspace {workspace} --agent-id {agent_id} --name \"{name}\"。"
        )
    return (
        f"First run: {prog} prompt init, then generate the role-init JSON and run: "
        f"{prog} init-state --workspace {workspace} --agent-id {agent_id} --name \"{name}\" --init-json <init.json>. "
        "If the host is OpenClaw, also run `bes prompt openclaw-example` and update the AGENTS and TOOLS system prompts separately. "
        f"After that, rerun: {prog} check-init --workspace {workspace} --agent-id {agent_id} --name \"{name}\"."
    )


def language_show_text(lang: str, effective: str, config_path: Path) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return (
            f"当前语言：{effective}\n"
            f"配置文件：{config_path}\n"
            "优先级：命令行 --language > 环境变量 BES_LANGUAGE > 用户配置 > 默认 en"
        )
    return (
        f"Effective language: {effective}\n"
        f"Config file: {config_path}\n"
        "Precedence: CLI --language > BES_LANGUAGE env > user config > default en"
    )


def language_set_ok(lang: str, code: str, path: Path) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return f"已设置默认语言为 {code}，已写入：{path}"
    return f"Default language set to {code}. Written to: {path}"


def err_viz_dependencies_missing(lang: str, packages: list[str]) -> str:
    lg = _lg(lang)
    joined = ", ".join(packages)
    if lg == LANG_ZH:
        return (
            "可视化依赖未安装："
            f"{joined}\n"
            "请先安装：pip install body-emotion-sensor[viz]"
        )
    return (
        "Visualization dependencies are missing: "
        f"{joined}\n"
        "Install them first: pip install body-emotion-sensor[viz]"
    )


def legacy_description(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "旧版 body_emotion 命令行兼容封装。"
    return "Legacy compatibility wrapper for the old body_emotion CLI."


def legacy_epilog(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return """
推荐改用:
  bes prompt init
  bes init-state --workspace <W> --agent-id <ID> --name "<NAME>" --init-json <init.json>
  bes run --workspace <W> --agent-id <ID> --name "<NAME>" --input <analysis-input.json>
""".strip()
    return """
Recommended replacement:
  bes prompt init
  bes init-state --workspace <W> --agent-id <ID> --name "<NAME>" --init-json <init.json>
  bes run --workspace <W> --agent-id <ID> --name "<NAME>" --input <analysis-input.json>
""".strip()


def legacy_bootstrap_description(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "旧版 bootstrap 命令兼容封装。"
    return "Legacy compatibility wrapper for the old bootstrap command."


def legacy_help_agent_id(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "智能体 ID（使用 --print-init-prompt 时除外为必填）"
    return "Agent ID (required except with --print-init-prompt)"


def legacy_help_name(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "展示名（使用 --print-init-prompt 时除外为必填）"
    return "Display name (required except with --print-init-prompt)"


def legacy_help_print_init(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "仅打印初始化提示词"
    return "Print initialization prompt only"


def legacy_help_init_flag(lang: str) -> str:
    lg = _lg(lang)
    if lg == LANG_ZH:
        return "初始化状态（默认体质）"
    return "Initialize state (default constitution)"
