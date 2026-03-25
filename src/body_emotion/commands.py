from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import cli_strings as CS
from .builtin_prompts import get_prompt_text
from .defaults import default_state
from .engine import BodyEmotionEngine
from .locale_config import LANG_EN, LANG_ZH, normalize_lang, resolve_language, set_user_language, user_config_path
from .prompting import (
    BODY_TAG_BODY_ORDER,
    build_baseline_persona,
    build_body_baseline_vs_current,
    build_body_tag,
    build_prompt_output_min,
    empty_turn_change_fallback,
)
from .schema import AnalysisInput, BODIES, State
from .store import load_state, save_state
from .workspace import resolve_state_path


def _prog_name(default: str = "bes") -> str:
    argv0 = Path(sys.argv[0]).name.strip()
    return argv0 or default


def _require_agent_identity(parser: argparse.ArgumentParser, agent_id: Any, name: Any, lang: str) -> tuple[str, str]:
    if agent_id is None or not str(agent_id).strip():
        parser.error(CS.err_agent_id_required(lang))
    if name is None or not str(name).strip():
        parser.error(CS.err_name_required(lang))
    return str(agent_id).strip(), str(name).strip()


def _require_workspace(parser: argparse.ArgumentParser, workspace: Any, lang: str) -> str:
    if workspace is None or not str(workspace).strip():
        parser.error(CS.err_workspace_required(lang))
    return str(workspace).strip()


def _state_from_init_json(payload: dict[str, Any], agent_id: str, name: str) -> State:
    base = default_state(agent_id=agent_id, name=name)
    if "profile" in payload:
        base.profile.agent_id = payload["profile"].get("agent_id", agent_id)
        base.profile.name = payload["profile"].get("name", name)
    if "traits" in payload:
        for key, value in payload["traits"].items():
            if hasattr(base.traits, key):
                setattr(base.traits, key, value)
    slot_payload = payload.get("bodies") or payload.get("organs")
    if slot_payload:
        for key, values in slot_payload.items():
            if key in base.bodies:
                organ = base.bodies[key]
                organ.baseline = int(values.get("baseline", organ.baseline))
                organ.current = int(values.get("current", values.get("baseline", organ.current)))
                organ.fragility = float(values.get("fragility", organ.fragility))
    return base


def _load_json_payload(
    file_path: str | None, json_string: str | None, label: str, lang: str
) -> dict[str, Any]:
    try:
        if file_path:
            return json.loads(Path(file_path).read_text(encoding="utf-8"))
        return json.loads(json_string or "")
    except json.JSONDecodeError as exc:
        source = file_path if file_path else "(inline JSON string)"
        print(CS.json_parse_error_lines(lang, label, source, str(exc)), file=sys.stderr)
        raise SystemExit(1) from exc


def _hint_missing_analysis_input(
    *,
    prog: str,
    state_path: Path,
    workspace: str | None,
    agent_id: str,
    name: str,
    just_created_default_state: bool,
    lang: str,
) -> str:
    return CS.hint_missing_analysis_input(
        prog=prog,
        state_path=state_path,
        workspace=workspace,
        agent_id=agent_id,
        name=name,
        just_created_default_state=just_created_default_state,
        lang=lang,
    )


def _bootstrap_turn_change_tags(state: State, lang: str) -> list[str]:
    if state.last_prompt_tags:
        return list(state.last_prompt_tags)
    if state.history:
        latest = state.history[-1]
        tags = latest.get("TURN_CHANGE_TAGS")
        if not isinstance(tags, list) or not tags:
            tags = latest.get("turn_change_tags")
        if isinstance(tags, list) and tags:
            return [str(item) for item in tags]
    return [empty_turn_change_fallback(lang)]


def _resolve_state_args(args: argparse.Namespace, parser: argparse.ArgumentParser, lang: str) -> tuple[Path, str, str]:
    agent_id, name = _require_agent_identity(parser, args.agent_id, args.name, lang)
    path = resolve_state_path(args.state, args.workspace, agent_id)
    return path, agent_id, name


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _check_item(name: str, ok: bool, detail: str) -> dict[str, Any]:
    return {
        "name": name,
        "ok": ok,
        "detail": detail,
    }


def _is_writable_directory(path: Path) -> bool:
    return path.exists() and path.is_dir() and os.access(path, os.W_OK)


def _cmd_init_prompt(args: argparse.Namespace, _: argparse.ArgumentParser) -> int:
    print(get_prompt_text("init", args.language))
    return 0


def _cmd_prompt(args: argparse.Namespace, _: argparse.ArgumentParser) -> int:
    print(get_prompt_text(args.prompt_name, args.language))
    return 0


def _cmd_init_state(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    lang = args.language
    path, agent_id, name = _resolve_state_args(args, parser, lang)
    if args.init_json or args.init_json_string:
        payload = _load_json_payload(args.init_json, args.init_json_string, CS.label_role_init_json(lang), lang)
        state = _state_from_init_json(payload, agent_id=agent_id, name=name)
        save_state(state, path)
        print(CS.msg_initialized_from_json(lang, path))
        return 0

    state = default_state(agent_id=agent_id, name=name)
    save_state(state, path)
    print(CS.msg_initialized(lang, path))
    return 0


def _cmd_bootstrap(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    lang = args.language
    path, agent_id, name = _resolve_state_args(args, parser, lang)
    if path.exists():
        state = load_state(path)
    else:
        state = default_state(agent_id=agent_id, name=name)
        save_state(state, path)

    payload = build_prompt_output_min(
        {
            "TURN_CHANGE_TAGS": _bootstrap_turn_change_tags(state, lang),
            "BODY_TAG": build_body_tag(state, lang=lang),
            "BASELINE_PERSONA": build_baseline_persona(state, lang=lang),
            "body_baseline_snapshot": {body: state.bodies[body].baseline for body in BODY_TAG_BODY_ORDER},
            "body_current_snapshot": {body: state.bodies[body].current for body in BODY_TAG_BODY_ORDER},
            "body_baseline_vs_current": build_body_baseline_vs_current(state),
        }
    )
    _print_json(payload)
    return 0


def _cmd_run(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    lang = args.language
    path, agent_id, name = _resolve_state_args(args, parser, lang)

    state_just_created = False
    if not path.exists():
        state_just_created = True
        state = default_state(agent_id=agent_id, name=name)
        save_state(state, path)

    if not args.input and not args.json:
        hint = _hint_missing_analysis_input(
            prog=_prog_name(),
            state_path=path,
            workspace=args.workspace,
            agent_id=agent_id,
            name=name,
            just_created_default_state=state_just_created,
            lang=lang,
        )
        print(hint, file=sys.stderr)
        return 1

    payload = _load_json_payload(args.input, args.json, CS.label_analysis_input_json(lang), lang)
    state = load_state(path)
    engine = BodyEmotionEngine(state)
    interpretation = engine.process(payload, lang=lang)
    save_state(engine.state, path)
    output = interpretation.to_dict()
    if args.full:
        _print_json(output)
    else:
        emotional_payload = output.get("emotional_prompt_payload") or {}
        _print_json(build_prompt_output_min(emotional_payload))
    return 0


def _cmd_check_init(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    lang = args.language
    workspace = _require_workspace(parser, args.workspace, lang)
    path, agent_id, name = _resolve_state_args(args, parser, lang)
    workspace_path = Path(workspace).expanduser().resolve()

    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    ready = True

    workspace_exists = workspace_path.exists()
    workspace_is_dir = workspace_path.is_dir()
    checks.append(
        _check_item(
            "workspace_exists",
            workspace_exists and workspace_is_dir,
            (
                f"工作区目录可用：{workspace_path}"
                if lang == LANG_ZH
                else f"Workspace directory is available: {workspace_path}"
            )
            if workspace_exists and workspace_is_dir
            else (
                f"工作区目录不存在或不是目录：{workspace_path}"
                if lang == LANG_ZH
                else f"Workspace path is missing or not a directory: {workspace_path}"
            ),
        )
    )
    ready = ready and workspace_exists and workspace_is_dir

    state_parent = path.parent
    writable_target = state_parent if state_parent.exists() else workspace_path
    writable_ok = _is_writable_directory(writable_target)
    checks.append(
        _check_item(
            "state_parent_writable",
            writable_ok,
            (
                f"状态目录可写：{writable_target}"
                if lang == LANG_ZH
                else f"State directory is writable: {writable_target}"
            )
            if writable_ok
            else (
                f"状态目录不可写或不存在：{writable_target}"
                if lang == LANG_ZH
                else f"State directory is not writable or does not exist: {writable_target}"
            ),
        )
    )
    ready = ready and writable_ok

    prompt_names = ["init", "analysis-input", "openclaw-example"]
    for prompt_name in prompt_names:
        try:
            prompt_text = get_prompt_text(prompt_name, lang)
            ok = bool(prompt_text.strip())
            checks.append(
                _check_item(
                    f"prompt_{prompt_name}",
                    ok,
                    (
                        f"内置提示词可用：{prompt_name}"
                        if lang == LANG_ZH
                        else f"Built-in prompt is available: {prompt_name}"
                    )
                    if ok
                    else (
                        f"内置提示词为空：{prompt_name}"
                        if lang == LANG_ZH
                        else f"Built-in prompt is empty: {prompt_name}"
                    ),
                )
            )
            ready = ready and ok
        except Exception as exc:
            checks.append(
                _check_item(
                    f"prompt_{prompt_name}",
                    False,
                    (
                        f"内置提示词不可用：{prompt_name}，错误：{exc}"
                        if lang == LANG_ZH
                        else f"Built-in prompt is unavailable: {prompt_name}; error: {exc}"
                    ),
                )
            )
            ready = False

    state_exists = path.exists()
    checks.append(
        _check_item(
            "state_exists",
            state_exists,
            (
                f"状态文件存在：{path}"
                if lang == LANG_ZH
                else f"State file exists: {path}"
            )
            if state_exists
            else (
                f"状态文件不存在：{path}"
                if lang == LANG_ZH
                else f"State file does not exist: {path}"
            ),
        )
    )

    if not state_exists:
        ready = False
        warnings.append(
            (
                "尚未发现初始化后的状态文件；请先生成初始化 JSON 并执行 `bes init-state`。"
                if lang == LANG_ZH
                else "No initialized state file was found; generate the init JSON and run `bes init-state` first."
            )
        )
    else:
        try:
            state = load_state(path)
            checks.append(
                _check_item(
                    "state_loadable",
                    True,
                    (
                        "状态文件可读取且结构合法"
                        if lang == LANG_ZH
                        else "State file is readable and structurally valid"
                    ),
                )
            )
            profile_ok = state.profile.agent_id == agent_id and state.profile.name == name
            checks.append(
                _check_item(
                    "state_profile_matches_args",
                    profile_ok,
                    (
                        f"状态中的 profile 与当前参数一致：{agent_id} / {name}"
                        if lang == LANG_ZH
                        else f"State profile matches current arguments: {agent_id} / {name}"
                    )
                    if profile_ok
                    else (
                        f"状态中的 profile 与当前参数不一致：state=({state.profile.agent_id}, {state.profile.name})"
                        if lang == LANG_ZH
                        else f"State profile does not match current arguments: state=({state.profile.agent_id}, {state.profile.name})"
                    ),
                )
            )
            ready = ready and profile_ok

            bodies_ok = set(state.bodies.keys()) == set(BODIES)
            checks.append(
                _check_item(
                    "state_bodies_complete",
                    bodies_ok,
                    (
                        "五脏状态字段完整"
                        if lang == LANG_ZH
                        else "Body-state fields are complete"
                    )
                    if bodies_ok
                    else (
                        "五脏状态字段不完整"
                        if lang == LANG_ZH
                        else "Body-state fields are incomplete"
                    ),
                )
            )
            ready = ready and bodies_ok
        except Exception as exc:
            checks.append(
                _check_item(
                    "state_loadable",
                    False,
                    (
                        f"状态文件无法读取或结构不合法：{exc}"
                        if lang == LANG_ZH
                        else f"State file cannot be loaded or is invalid: {exc}"
                    ),
                )
            )
            ready = False

    if ready:
        next_step_prompt = CS.check_init_ready_prompt(_prog_name(), workspace, agent_id, name, lang)
    else:
        next_step_prompt = CS.check_init_not_ready_prompt(_prog_name(), workspace, agent_id, name, lang)

    payload = {
        "ready": ready,
        "workspace": str(workspace_path),
        "state_path": str(path),
        "checks": checks,
        "warnings": warnings,
        "next_step_prompt": next_step_prompt,
    }
    _print_json(payload)
    return 0


def _cmd_language(args: argparse.Namespace, _: argparse.ArgumentParser) -> int:
    if getattr(args, "lang_code", None) is not None:
        code = normalize_lang(args.lang_code)
        path = set_user_language(code)
        print(CS.language_set_ok(args.language, code, path))
        return 0
    eff = resolve_language(cli_override=getattr(args, "cli_language", None))
    print(CS.language_show_text(args.language, eff, user_config_path()))
    return 0


def _cmd_panel(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    lang = args.language
    if args.state:
        state_path = Path(args.state).expanduser().resolve()
    elif args.workspace or args.agent_id:
        workspace = _require_workspace(parser, args.workspace, lang)
        if args.agent_id is None or not str(args.agent_id).strip():
            parser.error(CS.err_agent_id_required(lang))
        state_path = resolve_state_path(None, workspace, str(args.agent_id).strip())
    else:
        state_path = None

    missing = [name for name in ("streamlit", "plotly") if importlib.util.find_spec(name) is None]
    if missing:
        print(CS.err_viz_dependencies_missing(lang, missing), file=sys.stderr)
        return 1

    panel_path = Path(__file__).with_name("panel.py")
    cmd = [sys.executable, "-m", "streamlit", "run", str(panel_path)]
    if args.host:
        cmd.extend(["--server.address", str(args.host)])
    if args.port is not None:
        cmd.extend(["--server.port", str(args.port)])
    if args.headless:
        cmd.extend(["--server.headless", "true"])

    env = os.environ.copy()
    env["BES_PANEL_UI_LANG"] = lang
    if state_path is not None:
        env["BES_PANEL_STATE_PATH"] = str(state_path)

    return int(subprocess.call(cmd, env=env))


def _build_main_parser(prog: str, lang: str) -> tuple[argparse.ArgumentParser, dict[str, argparse.ArgumentParser]]:
    parser = argparse.ArgumentParser(
        prog=prog,
        description=CS.main_description(lang),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=CS.main_epilog(prog, lang),
    )
    parser.add_argument(
        "-L",
        "--language",
        dest="cli_language",
        choices=[LANG_EN, LANG_ZH],
        default=None,
        help=CS.help_language_flag(lang),
    )
    parser_map: dict[str, argparse.ArgumentParser] = {}
    subparsers = parser.add_subparsers(dest="command")

    help_parser = subparsers.add_parser("help", help=CS.help_help(lang))
    help_parser.add_argument(
        "topic",
        nargs="?",
        choices=CS.help_topics_list(lang),
        help=CS.help_help_topic(lang),
    )
    parser_map["help"] = help_parser

    prompt_parser = subparsers.add_parser("prompt", help=CS.help_prompt(lang))
    prompt_parser.add_argument(
        "prompt_name",
        choices=["analysis-input", "init", "openclaw-example"],
        help=CS.help_prompt_name(lang),
    )
    prompt_parser.set_defaults(handler=_cmd_prompt)
    parser_map["prompt"] = prompt_parser

    init_state_parser = subparsers.add_parser("init-state", help=CS.help_init_state(lang))
    init_state_parser.add_argument("--state", help=CS.help_state(lang))
    init_state_parser.add_argument("--workspace", help=CS.help_workspace(lang))
    init_state_parser.add_argument("--agent-id", default=None, help=CS.help_agent_id(lang))
    init_state_parser.add_argument("--name", default=None, help=CS.help_name(lang))
    init_state_group = init_state_parser.add_mutually_exclusive_group()
    init_state_group.add_argument("--init-json", help=CS.help_init_json(lang))
    init_state_group.add_argument("--init-json-string", help=CS.help_init_json_string(lang))
    init_state_parser.set_defaults(handler=_cmd_init_state)
    parser_map["init-state"] = init_state_parser

    check_init_parser = subparsers.add_parser("check-init", help=CS.help_check_init(lang))
    check_init_parser.add_argument("--state", help=CS.help_state(lang))
    check_init_parser.add_argument("--workspace", help=CS.help_workspace(lang))
    check_init_parser.add_argument("--agent-id", default=None, help=CS.help_agent_id(lang))
    check_init_parser.add_argument("--name", default=None, help=CS.help_name(lang))
    check_init_parser.set_defaults(handler=_cmd_check_init)
    parser_map["check-init"] = check_init_parser

    bootstrap_parser = subparsers.add_parser("bootstrap", help=CS.help_bootstrap(lang))
    bootstrap_parser.add_argument("--state", help=CS.help_state(lang))
    bootstrap_parser.add_argument("--workspace", help=CS.help_workspace(lang))
    bootstrap_parser.add_argument("--agent-id", default=None, help=CS.help_agent_id(lang))
    bootstrap_parser.add_argument("--name", default=None, help=CS.help_name(lang))
    bootstrap_parser.set_defaults(handler=_cmd_bootstrap)
    parser_map["bootstrap"] = bootstrap_parser

    run_parser = subparsers.add_parser("run", help=CS.help_run(lang))
    run_parser.add_argument("--state", help=CS.help_state(lang))
    run_parser.add_argument("--workspace", help=CS.help_workspace(lang))
    run_parser.add_argument("--agent-id", default=None, help=CS.help_agent_id(lang))
    run_parser.add_argument("--name", default=None, help=CS.help_name(lang))
    input_group = run_parser.add_mutually_exclusive_group()
    input_group.add_argument("--input", help=CS.help_input(lang))
    input_group.add_argument("--json", help=CS.help_json_inline(lang))
    run_parser.add_argument(
        "--full",
        action="store_true",
        help=CS.help_full(lang),
    )
    run_parser.set_defaults(handler=_cmd_run)
    parser_map["run"] = run_parser

    panel_parser = subparsers.add_parser("panel", help=CS.help_panel(lang))
    panel_parser.add_argument("--state", help=CS.help_state(lang))
    panel_parser.add_argument("--workspace", help=CS.help_workspace(lang))
    panel_parser.add_argument("--agent-id", default=None, help=CS.help_agent_id(lang))
    panel_parser.add_argument("--host", default=None, help=CS.help_host(lang))
    panel_parser.add_argument("--port", type=int, default=None, help=CS.help_port(lang))
    panel_parser.add_argument(
        "--headless",
        action="store_true",
        help=CS.help_headless(lang),
    )
    panel_parser.set_defaults(handler=_cmd_panel)
    parser_map["panel"] = panel_parser

    language_parser = subparsers.add_parser("language", help=CS.help_language_cmd(lang))
    language_parser.add_argument(
        "lang_code",
        nargs="?",
        choices=[LANG_EN, LANG_ZH],
        default=None,
        metavar="en|zh",
        help=CS.help_language_code(lang),
    )
    language_parser.set_defaults(handler=_cmd_language)
    parser_map["language"] = language_parser

    return parser, parser_map


def _run_help_command(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    parser_map: dict[str, argparse.ArgumentParser],
) -> int:
    if args.topic:
        parser_map[args.topic].print_help()
    else:
        print(CS.ai_workflow_header(_prog_name(), args.language))
        print()
        parser.print_help()
    return 0


def main(argv: list[str] | None = None) -> int:
    prog = _prog_name()
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("-L", "--language", dest="cli_language", choices=[LANG_EN, LANG_ZH], default=None)
    pre_args, rest = pre.parse_known_args(argv)
    ui_lang = resolve_language(cli_override=pre_args.cli_language)
    parser, parser_map = _build_main_parser(prog, ui_lang)
    args = parser.parse_args(rest)
    args.language = resolve_language(cli_override=pre_args.cli_language)

    if not args.command:
        parser.print_help()
        return 0
    if args.command == "help":
        return _run_help_command(args, parser, parser_map)
    return int(args.handler(args, parser))


def legacy_cli_main(argv: list[str] | None = None) -> int:
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("-L", "--language", dest="cli_language", choices=[LANG_EN, LANG_ZH], default=None)
    pre_args, rest = pre.parse_known_args(argv)
    ui_lang = resolve_language(cli_override=pre_args.cli_language)
    parser = argparse.ArgumentParser(
        prog="body-emotion",
        description=CS.legacy_description(ui_lang),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=CS.legacy_epilog(ui_lang),
    )
    parser.add_argument(
        "-L",
        "--language",
        dest="cli_language",
        choices=[LANG_EN, LANG_ZH],
        default=None,
        help=CS.help_language_flag(ui_lang),
    )
    parser.add_argument("--state", help=CS.help_state(ui_lang))
    parser.add_argument("--workspace", help=CS.help_workspace(ui_lang))
    parser.add_argument("--agent-id", default=None, help=CS.legacy_help_agent_id(ui_lang))
    parser.add_argument("--name", default=None, help=CS.legacy_help_name(ui_lang))
    parser.add_argument("--init", action="store_true", help=CS.legacy_help_init_flag(ui_lang))
    parser.add_argument("--print-init-prompt", action="store_true", help=CS.legacy_help_print_init(ui_lang))
    parser.add_argument("--init-json", help=CS.help_init_json(ui_lang))
    parser.add_argument("--init-json-string", help=CS.help_init_json_string(ui_lang))
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--input", help=CS.help_input(ui_lang))
    input_group.add_argument("--json", help=CS.help_json_inline(ui_lang))
    parser.add_argument("--full", action="store_true", help=CS.help_full(ui_lang))
    args = parser.parse_args(rest)
    args.language = resolve_language(cli_override=pre_args.cli_language or args.cli_language)

    if args.print_init_prompt:
        print(get_prompt_text("init", args.language))
        return 0
    if args.init or args.init_json or args.init_json_string:
        return _cmd_init_state(args, parser)
    return _cmd_run(args, parser)


def legacy_bootstrap_main(argv: list[str] | None = None) -> int:
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("-L", "--language", dest="cli_language", choices=[LANG_EN, LANG_ZH], default=None)
    pre_args, rest = pre.parse_known_args(argv)
    ui_lang = resolve_language(cli_override=pre_args.cli_language)
    parser = argparse.ArgumentParser(
        prog="body-emotion-bootstrap",
        description=CS.legacy_bootstrap_description(ui_lang),
    )
    parser.add_argument(
        "-L",
        "--language",
        dest="cli_language",
        choices=[LANG_EN, LANG_ZH],
        default=None,
        help=CS.help_language_flag(ui_lang),
    )
    parser.add_argument("--state", help=CS.help_state(ui_lang))
    parser.add_argument("--workspace", help=CS.help_workspace(ui_lang))
    parser.add_argument("--agent-id", default=None, help=CS.help_agent_id(ui_lang))
    parser.add_argument("--name", default=None, help=CS.help_name(ui_lang))
    args = parser.parse_args(rest)
    args.language = resolve_language(cli_override=pre_args.cli_language or args.cli_language)
    return _cmd_bootstrap(args, parser)


if __name__ == "__main__":
    raise SystemExit(main())
