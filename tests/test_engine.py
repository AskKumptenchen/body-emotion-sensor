import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from body_emotion.commands import main as commands_main
from body_emotion.defaults import INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME, default_state
from body_emotion.engine import BodyEmotionEngine
from body_emotion.locale_config import LANG_EN, LANG_ZH
from body_emotion.interpreter import apply_phase_propagation
from body_emotion.prompting import _intensity_bucket, _state_level, build_body_tag
from body_emotion.schema import AnalysisInput, BODIES, State
from body_emotion.store import load_state, save_state


def sample_payload() -> dict:
    return {
        "analysis_target": "乙",
        "context_summary": {
            "current_turn_focus": "甲在持续互相贬低的对抗语境里，再次对乙作出能力压低和表达价值否定",
        },
        "semantic_stimuli": [
            {
                "id": "negated",
                "intensity": "strong",
                "evidence": "甲直接否定乙的表达深度和理解价值",
            },
            {
                "id": "humiliated",
                "intensity": "medium",
                "evidence": "当前轮不只是反驳，而是带轻蔑地压低乙的水平",
            },
            {
                "id": "pressured",
                "intensity": "light",
                "evidence": "整段对话呈持续压迫式互顶，不断逼迫对方回击",
            },
        ],
        "body_reactions": [
            {
                "id": "surge",
                "intensity": "strong",
                "reason": "持续对抗语境下，最直接的身体反应是顶回去",
            },
            {
                "id": "tension",
                "intensity": "medium",
                "reason": "被连续压低后会进入防御和绷住状态",
            },
            {
                "id": "stuck",
                "intensity": "medium",
                "reason": "不是单纯受伤，而是拧着、卡着、不舒展",
            },
        ],
    }


def support_payload() -> dict:
    return {
        "analysis_target": "乙",
        "context_summary": {
            "current_turn_focus": "甲明确表达修复和靠近，乙感到被托住、关系明显回暖",
        },
        "semantic_stimuli": [
            {
                "id": "supported",
                "intensity": "strong",
                "evidence": "甲明确表示会站在乙这边，愿意继续接住乙",
            },
            {
                "id": "reapproached",
                "intensity": "medium",
                "evidence": "关系从拉远转为再次靠近",
            },
        ],
        "body_reactions": [
            {
                "id": "warming",
                "intensity": "strong",
                "reason": "身体层面首先表现为热度回来",
            },
            {
                "id": "settling",
                "intensity": "medium",
                "reason": "紧绷感退一些，底部开始安定",
            },
        ],
    }


class EngineTests(unittest.TestCase):
    def test_analysis_input_parses_b_mode_json(self):
        analysis = AnalysisInput.from_dict(sample_payload())
        self.assertEqual(analysis.analysis_target, "乙")
        self.assertEqual(
            analysis.context_summary.current_turn_focus,
            "甲在持续互相贬低的对抗语境里，再次对乙作出能力压低和表达价值否定",
        )
        self.assertEqual(len(analysis.semantic_stimuli), 3)
        self.assertEqual(analysis.semantic_stimuli[0].id, "negated")

    def test_engine_maps_json_to_bodies(self):
        engine = BodyEmotionEngine(default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME))
        result = engine.process(sample_payload(), lang=LANG_ZH)
        self.assertEqual(result.body_state_changes["liver"].trend, "stable")
        self.assertEqual(result.body_state_changes["heart"].trend, "down")
        self.assertEqual(result.body_state_changes["lung"].trend, "up")
        self.assertEqual(result.turn_change_tags, ["兴致下降", "热情减少"])
        self.assertTrue(result.body_tag)
        self.assertIn("body_contributors", result.to_dict())
        self.assertTrue(result.body_contributors["liver"])
        self.assertIn("phase-propagation:lung:constrain:light:liver:-2", result.body_contributors["liver"])

    def test_engine_updates_bodies_with_estimated_delta(self):
        engine = BodyEmotionEngine(default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME))
        prev_liver = engine.state.bodies["liver"].current
        prev_heart = engine.state.bodies["heart"].current
        result = engine.process(sample_payload(), lang=LANG_ZH)
        self.assertEqual(result.updated_bodies["liver"], prev_liver)
        self.assertLess(result.updated_bodies["heart"], prev_heart)
        self.assertEqual(result.updated_bodies["liver"], engine.state.bodies["liver"].current)
        self.assertTrue(engine.state.history)
        self.assertIn("updated_bodies", engine.state.history[-1])
        self.assertNotIn("phase_levels", result.to_dict())
        self.assertIn("BODY_TAG", result.to_dict())
        self.assertIn("updated_bodies", result.to_dict())
        self.assertIn("turn_trace", result.to_dict())

    def test_turn_trace_contains_full_pipeline_sections(self):
        engine = BodyEmotionEngine(default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME))
        result = engine.process(sample_payload(), lang=LANG_ZH)

        trace = result.turn_trace
        self.assertIn("input", trace)
        self.assertIn("base_mapping", trace)
        self.assertIn("phase_propagation", trace)
        self.assertIn("persistent_update", trace)
        self.assertIn("prompt_output", trace)
        self.assertEqual(trace["phase_propagation"]["scores_after"], result.body_scores)
        self.assertEqual(trace["prompt_output"]["BODY_TAG"], result.body_tag)
        self.assertEqual(trace["prompt_output"]["TURN_CHANGE_TAGS"], result.turn_change_tags)
        self.assertIn("BASELINE_PERSONA", trace["prompt_output"])
        self.assertNotIn("body_baseline_vs_current", trace["prompt_output"])
        self.assertIn("body_baseline_vs_current", trace["prompt_output"]["emotional_prompt_payload"])

    def test_turn_trace_is_written_to_history(self):
        engine = BodyEmotionEngine(default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME))
        engine.process(sample_payload(), lang=LANG_ZH)

        history_turn = engine.state.history[-1]
        self.assertIn("turn_trace", history_turn)
        self.assertIn("base_mapping", history_turn["turn_trace"])
        self.assertIn("phase_propagation", history_turn["turn_trace"])
        self.assertIn("persistent_update", history_turn["turn_trace"])

    def test_cli_exits_without_agent_identity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            with self.assertRaises(SystemExit):
                commands_main(["run", "--state", str(state_path)])

    def test_cli_help_command_lists_subcommands(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = commands_main(["-L", "zh", "help"])
        self.assertEqual(exit_code, 0)
        help_text = stdout.getvalue()
        self.assertIn("给 AI 的接入流程说明", help_text)
        self.assertNotIn("init-prompt", help_text)
        self.assertIn("prompt", help_text)
        self.assertIn("init-state", help_text)
        self.assertIn("check-init", help_text)
        self.assertIn("bootstrap", help_text)
        self.assertIn("run", help_text)
        self.assertIn("panel", help_text)

    def test_cli_help_check_init_outputs_subcommand_help(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = commands_main(["help", "check-init"])
        self.assertEqual(exit_code, 0)
        help_text = stdout.getvalue()
        self.assertIn("check-init", help_text)
        self.assertIn("--workspace", help_text)
        self.assertIn("--agent-id", help_text)

    def test_cli_help_panel_outputs_subcommand_help(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = commands_main(["help", "panel"])
        self.assertEqual(exit_code, 0)
        help_text = stdout.getvalue()
        self.assertIn("panel", help_text)
        self.assertIn("--workspace", help_text)
        self.assertIn("--agent-id", help_text)
        self.assertIn("--headless", help_text)

    def test_cli_prompt_analysis_input_outputs_builtin_prompt(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = commands_main(["-L", "zh", "prompt", "analysis-input"])
        self.assertEqual(exit_code, 0)
        prompt_text = stdout.getvalue()
        self.assertIn("语义刺激-身体反应识别器", prompt_text)
        self.assertIn('"semantic_stimuli"', prompt_text)
        self.assertIn("Few-Shot（精简版）", prompt_text)
        self.assertIn("示例 4：AI 先冒犯，用户反击", prompt_text)

    def test_cli_prompt_analysis_input_outputs_full_english_prompt(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = commands_main(["-L", "en", "prompt", "analysis-input"])
        self.assertEqual(exit_code, 0)
        prompt_text = stdout.getvalue()
        self.assertIn("AnalysisInput Structured Emotion Analysis Prompt", prompt_text)
        self.assertIn("Few-shot (condensed)", prompt_text)
        self.assertIn("Example 4: the AI offended first, then the user strikes back", prompt_text)

    def test_cli_prompt_init_outputs_template(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = commands_main(["-L", "zh", "prompt", "init"])
        self.assertEqual(exit_code, 0)
        self.assertIn("长期身体-情绪体质初始化设定", stdout.getvalue())
        self.assertIn("bes prompt openclaw-example", stdout.getvalue())

    def test_cli_prompt_openclaw_example_outputs_two_sections_in_zh(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = commands_main(["-L", "zh", "prompt", "openclaw-example"])
        self.assertEqual(exit_code, 0)
        prompt_text = stdout.getvalue()
        self.assertIn("[AGENTS EXAMPLE]", prompt_text)
        self.assertIn("[TOOLS EXAMPLE]", prompt_text)
        self.assertIn("每条用户消息的固定流程", prompt_text)

    def test_cli_prompt_openclaw_example_outputs_two_sections_in_en(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = commands_main(["-L", "en", "prompt", "openclaw-example"])
        self.assertEqual(exit_code, 0)
        prompt_text = stdout.getvalue()
        self.assertIn("[AGENTS EXAMPLE]", prompt_text)
        self.assertIn("[TOOLS EXAMPLE]", prompt_text)
        self.assertIn("Per-user-message flow", prompt_text)

    def test_cli_init_state_writes_default_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = commands_main(
                    [
                        "init-state",
                        "--state",
                        str(state_path),
                        "--agent-id",
                        "test-agent",
                        "--name",
                        "Test Agent",
                    ]
                )
            self.assertEqual(exit_code, 0)
            self.assertTrue(state_path.exists())
            self.assertIn("initialized:", stdout.getvalue())

    def test_cli_accepts_json_file_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_path = tmp_path / "input.json"
            state_path = tmp_path / "state.json"
            input_path.write_text(json.dumps(sample_payload(), ensure_ascii=False, indent=2), encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = commands_main(
                    [
                        "run",
                        "--state",
                        str(state_path),
                        "--agent-id",
                        "test-agent",
                        "--name",
                        "Test Agent",
                        "--input",
                        str(input_path),
                        "--full",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertIn("body_state_changes", payload)
            self.assertNotIn("total_delta", payload)
            self.assertIn("body_scores", payload)
            self.assertIn("updated_bodies", payload)

    def test_cli_accepts_json_string_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            state_path = tmp_path / "state.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = commands_main(
                    [
                        "run",
                        "--state",
                        str(state_path),
                        "--agent-id",
                        "test-agent",
                        "--name",
                        "Test Agent",
                        "--json",
                        json.dumps(sample_payload(), ensure_ascii=False),
                        "--full",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["analysis_target"], "乙")
            self.assertIn("TURN_CHANGE_TAGS", payload)

    def test_cli_panel_launches_streamlit_with_resolved_state_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir).resolve()
            captured: dict[str, object] = {}

            def fake_find_spec(name: str):
                if name in ("streamlit", "plotly"):
                    return object()
                return None

            def fake_subprocess_call(cmd, env=None):
                captured["cmd"] = cmd
                captured["env"] = env
                return 0

            with (
                patch("body_emotion.commands.importlib.util.find_spec", side_effect=fake_find_spec),
                patch("body_emotion.commands.subprocess.call", side_effect=fake_subprocess_call),
            ):
                exit_code = commands_main(
                    [
                        "-L",
                        "zh",
                        "panel",
                        "--workspace",
                        str(workspace),
                        "--agent-id",
                        "test-agent",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "8501",
                        "--headless",
                    ]
                )

            self.assertEqual(exit_code, 0)
            cmd = captured["cmd"]
            env = captured["env"]
            self.assertEqual(cmd[:4], [sys.executable, "-m", "streamlit", "run"])
            self.assertIn("--server.address", cmd)
            self.assertIn("--server.port", cmd)
            self.assertIn("--server.headless", cmd)
            self.assertEqual(env["BES_PANEL_UI_LANG"], "zh")
            self.assertEqual(
                env["BES_PANEL_STATE_PATH"],
                str(workspace / "body-emotion-state" / "test-agent.json"),
            )

    def test_cli_default_output_only_contains_ai_reply_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            state_path = tmp_path / "state.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = commands_main(
                    [
                        "run",
                        "--state",
                        str(state_path),
                        "--agent-id",
                        "test-agent",
                        "--name",
                        "Test Agent",
                        "--json",
                        json.dumps(sample_payload(), ensure_ascii=False),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(
                set(payload.keys()),
                {
                    "TURN_CHANGE_TAGS",
                    "BODY_TAG",
                    "BASELINE_PERSONA",
                },
            )
            self.assertTrue(payload["TURN_CHANGE_TAGS"])
            self.assertTrue(payload["BODY_TAG"])
            self.assertTrue(payload["BASELINE_PERSONA"])

    def test_cli_full_outputs_complete_interpretation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            state_path = tmp_path / "state.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = commands_main(
                    [
                        "run",
                        "--state",
                        str(state_path),
                        "--agent-id",
                        "test-agent",
                        "--name",
                        "Test Agent",
                        "--json",
                        json.dumps(sample_payload(), ensure_ascii=False),
                        "--full",
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["analysis_target"], "乙")
            self.assertIn("body_state_changes", payload)
            self.assertIn("emotional_prompt_payload", payload)

    def test_bootstrap_default_output_only_contains_ai_reply_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            state_path = tmp_path / "state.json"
            engine = BodyEmotionEngine(default_state(agent_id="asks-chat", name="小陪聊"))
            engine.process(sample_payload(), lang=LANG_ZH)

            from body_emotion.store import save_state

            save_state(engine.state, state_path)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = commands_main(
                    ["-L", "zh", "bootstrap", "--state", str(state_path), "--agent-id", "asks-chat", "--name", "小陪聊"]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(
                set(payload.keys()),
                {
                    "TURN_CHANGE_TAGS",
                    "BODY_TAG",
                    "BASELINE_PERSONA",
                },
            )
            self.assertTrue(payload["TURN_CHANGE_TAGS"])
            self.assertTrue(payload["BODY_TAG"])
            self.assertTrue(payload["BASELINE_PERSONA"])

    def test_bootstrap_initializes_missing_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            state_path = tmp_path / "missing-state.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = commands_main(
                    ["-L", "zh", "bootstrap", "--state", str(state_path), "--agent-id", "asks-chat", "--name", "小陪聊"]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(
                set(payload.keys()),
                {
                    "TURN_CHANGE_TAGS",
                    "BODY_TAG",
                    "BASELINE_PERSONA",
                },
            )
            self.assertEqual(payload["TURN_CHANGE_TAGS"], ["整体变化不大"])
            self.assertTrue(state_path.exists())

    def test_check_init_reports_not_ready_when_state_is_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = commands_main(
                    [
                        "-L",
                        "zh",
                        "check-init",
                        "--workspace",
                        tmpdir,
                        "--agent-id",
                        "asks-chat",
                        "--name",
                        "小陪聊",
                    ]
                )
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ready"])
            self.assertTrue(any(item["name"] == "state_exists" and not item["ok"] for item in payload["checks"]))
            self.assertIn("init-state", payload["next_step_prompt"])

    def test_check_init_reports_invalid_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            state_dir = workspace / "body-emotion-state"
            state_dir.mkdir(parents=True, exist_ok=True)
            state_path = state_dir / "asks-chat.json"
            state_path.write_text('{"bad": true}', encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = commands_main(
                    [
                        "-L",
                        "zh",
                        "check-init",
                        "--workspace",
                        str(workspace),
                        "--agent-id",
                        "asks-chat",
                        "--name",
                        "小陪聊",
                    ]
                )
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertFalse(payload["ready"])
            self.assertTrue(any(item["name"] == "state_loadable" and not item["ok"] for item in payload["checks"]))

    def test_check_init_reports_ready_for_matching_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            state_path = workspace / "body-emotion-state" / "asks-chat.json"
            save_state(default_state("asks-chat", "小陪聊"), state_path)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = commands_main(
                    [
                        "-L",
                        "zh",
                        "check-init",
                        "--workspace",
                        str(workspace),
                        "--agent-id",
                        "asks-chat",
                        "--name",
                        "小陪聊",
                    ]
                )
            self.assertEqual(exit_code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertTrue(payload["ready"])
            self.assertTrue(any(item["name"] == "state_profile_matches_args" and item["ok"] for item in payload["checks"]))
            self.assertIn("OpenClaw", payload["next_step_prompt"])

    def test_analysis_input_rejects_unknown_stimulus_name(self):
        payload = sample_payload()
        payload["semantic_stimuli"][0]["id"] = "unknown_id"
        with self.assertRaises(ValueError):
            AnalysisInput.from_dict(payload)

    def test_emotional_prompt_payload_exists(self):
        engine = BodyEmotionEngine(default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME))
        result = engine.process(sample_payload(), lang=LANG_ZH)
        result_dict = result.to_dict()
        self.assertIn("emotional_prompt_payload", result_dict)
        self.assertNotIn("safety_constraints", result_dict)
        payload = result_dict["emotional_prompt_payload"]
        self.assertIn("TURN_CHANGE_TAGS", payload)
        self.assertIn("BODY_TAG", payload)
        self.assertIn("BASELINE_PERSONA", payload)
        self.assertIn("body_baseline_snapshot", payload)
        self.assertIn("body_current_snapshot", payload)
        self.assertIn("body_baseline_vs_current", payload)
        self.assertIn("body_compare_instruction", payload)
        self.assertNotIn("safety_constraints", payload)
        self.assertNotIn("reply_prompt_text", payload)
        self.assertNotIn("overall_body_state", payload)
        self.assertNotIn("turn_feeling_adjustment", payload)

    def test_fragility_affects_scores(self):
        low = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        high = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        low.bodies["heart"].fragility = 0.2
        high.bodies["heart"].fragility = 1.0
        low.traits.overall_fragility = 0.8
        high.traits.overall_fragility = 1.2
        low_result = BodyEmotionEngine(low).process(sample_payload(), lang=LANG_ZH)
        high_result = BodyEmotionEngine(high).process(sample_payload(), lang=LANG_ZH)
        self.assertLessEqual(high_result.body_scores["heart"], low_result.body_scores["heart"])

    def test_phase_propagation_liver_strongly_constrains_spleen_without_generating_heart(self):
        state = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        base_scores = {slot: 0 for slot in BODIES}
        contributors = {slot: [] for slot in BODIES}
        base_scores["liver"] = 9

        final_scores = apply_phase_propagation(base_scores, contributors, state.bodies)

        self.assertEqual(final_scores["spleen"], -4)
        self.assertEqual(final_scores["heart"], 0)
        self.assertIn("phase-propagation:liver:constrain:strong:spleen:-4", contributors["spleen"])
        self.assertFalse(any(item.startswith("phase-propagation:liver:generate") for item in contributors["heart"]))

    def test_phase_propagation_liver_lightly_constrains_spleen(self):
        state = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        base_scores = {slot: 0 for slot in BODIES}
        contributors = {slot: [] for slot in BODIES}
        base_scores["liver"] = 5

        final_scores = apply_phase_propagation(base_scores, contributors, state.bodies)

        self.assertEqual(final_scores["spleen"], -2)
        self.assertIn("phase-propagation:liver:constrain:light:spleen:-2", contributors["spleen"])

    def test_phase_propagation_balanced_liver_strongly_generates_heart(self):
        state = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        state.bodies["liver"] = replace(state.bodies["liver"], current=56)
        state.bodies["heart"] = replace(state.bodies["heart"], current=64)
        base_scores = {slot: 0 for slot in BODIES}
        contributors = {slot: [] for slot in BODIES}
        base_scores["liver"] = 1
        base_scores["heart"] = 1

        final_scores = apply_phase_propagation(base_scores, contributors, state.bodies)

        self.assertEqual(final_scores["heart"], 5)
        self.assertIn("phase-propagation:liver:generate:strong:heart:+4", contributors["heart"])
        self.assertFalse(any(item.startswith("phase-propagation:liver:constrain") for item in contributors["spleen"]))

    def test_phase_propagation_uses_frozen_snapshot_for_same_turn_decisions(self):
        state = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        base_scores = {slot: 0 for slot in BODIES}
        contributors = {slot: [] for slot in BODIES}
        base_scores["liver"] = 9
        base_scores["spleen"] = 2

        final_scores = apply_phase_propagation(base_scores, contributors, state.bodies)

        self.assertEqual(final_scores["spleen"], -2)
        self.assertEqual(final_scores["lung"], 2)
        self.assertIn("phase-propagation:liver:constrain:strong:spleen:-4", contributors["spleen"])
        self.assertIn("phase-propagation:spleen:generate:light:lung:+2", contributors["lung"])

    def test_history_split_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "agent.json"
            s = default_state("roundtrip-agent", "Roundtrip")
            s.history.append({"analysis_target": "x", "turn": 1})
            save_state(s, state_path)
            main_raw = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertNotIn("history", main_raw)
            hist_path = state_path.parent / "history" / "agent.json"
            self.assertTrue(hist_path.is_file())
            self.assertEqual(json.loads(hist_path.read_text(encoding="utf-8")), s.history)
            loaded = load_state(state_path)
            self.assertEqual(loaded.history, s.history)
            self.assertEqual(loaded.profile.agent_id, "roundtrip-agent")

    def test_load_history_inline_migration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "legacy.json"
            snap = default_state("legacy", "Legacy").to_snapshot_dict()
            snap["history"] = [{"legacy_turn": True}]
            state_path.write_text(json.dumps(snap, ensure_ascii=False), encoding="utf-8")
            loaded = load_state(state_path)
            self.assertEqual(loaded.history, [{"legacy_turn": True}])

    def test_state_from_dict_migrates_missing_bodies(self):
        data = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME).to_dict()
        del data["bodies"]
        state = State.from_dict(data)
        self.assertEqual(set(state.bodies.keys()), {"liver", "heart", "spleen", "lung", "kidney"})
        self.assertEqual(state.bodies["liver"].current, 52)

    def test_update_bodies_recovers_toward_baseline_without_new_scores(self):
        state = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        state.bodies["heart"] = replace(state.bodies["heart"], current=91)
        engine = BodyEmotionEngine(state)

        updated = engine._update_bodies({slot: 0 for slot in BODIES})

        self.assertLess(updated["heart"], 91)
        self.assertGreater(updated["heart"], state.bodies["heart"].baseline)
        self.assertEqual(updated["heart"], engine.state.bodies["heart"].current)

    def test_high_scores_are_damped_near_upper_bound(self):
        state = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        state.bodies["heart"] = replace(state.bodies["heart"], current=85)
        engine = BodyEmotionEngine(state)

        undamped = engine._body_persistent_delta(18, state.bodies["heart"].fragility)
        updated = engine._update_bodies({slot: 18 if slot == "heart" else 0 for slot in BODIES})
        actual_gain = updated["heart"] - 85

        self.assertLess(actual_gain, undamped)
        self.assertGreater(actual_gain, 0)

    def test_repeated_support_rises_but_does_not_stick_at_peak(self):
        engine = BodyEmotionEngine(default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME))
        payload = support_payload()

        for _ in range(6):
            engine.process(payload, lang=LANG_ZH)

        heart_peak = engine.state.bodies["heart"].current
        kidney_peak = engine.state.bodies["kidney"].current
        self.assertLess(heart_peak, 100)
        self.assertLess(kidney_peak, 100)

        for _ in range(4):
            engine._update_bodies({slot: 0 for slot in BODIES})

        self.assertLess(engine.state.bodies["heart"].current, heart_peak)
        self.assertLess(engine.state.bodies["kidney"].current, kidney_peak)

    def test_intensity_bucket_uses_8_14_20_thresholds(self):
        self.assertEqual(_intensity_bucket(7), 0)
        self.assertEqual(_intensity_bucket(8), 1)
        self.assertEqual(_intensity_bucket(13), 1)
        self.assertEqual(_intensity_bucket(14), 2)
        self.assertEqual(_intensity_bucket(19), 2)
        self.assertEqual(_intensity_bucket(20), 3)
        self.assertEqual(_intensity_bucket(-20), 3)

    def test_state_level_uses_seven_absolute_bands(self):
        self.assertEqual(_state_level(95), 3)
        self.assertEqual(_state_level(85), 2)
        self.assertEqual(_state_level(60), 1)
        self.assertEqual(_state_level(40), 0)
        self.assertEqual(_state_level(39), -1)
        self.assertEqual(_state_level(19), -2)
        self.assertEqual(_state_level(9), -3)

    def test_body_tag_uses_absolute_current_state(self):
        state = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        state.bodies["heart"] = replace(state.bodies["heart"], current=95)
        state.bodies["spleen"] = replace(state.bodies["spleen"], current=35)
        state.bodies["liver"] = replace(state.bodies["liver"], current=52)
        state.bodies["lung"] = replace(state.bodies["lung"], current=12)
        state.bodies["kidney"] = replace(state.bodies["kidney"], current=82)

        body_tag = build_body_tag(state, lang=LANG_ZH)

        self.assertIn("狂躁亢奋", body_tag)
        self.assertIn("略微懒散", body_tag)
        self.assertIn("情绪稳定", body_tag)
        self.assertIn("情感麻木", body_tag)
        self.assertIn("胆子大", body_tag)

    def test_body_tag_english_locale_uses_semicolon_and_english(self):
        state = default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        state.bodies["heart"] = replace(state.bodies["heart"], current=95)
        body_tag = build_body_tag(state, lang=LANG_EN)
        self.assertIn("; ", body_tag)
        self.assertIn("Manic arousal", body_tag)


if __name__ == "__main__":
    unittest.main()
