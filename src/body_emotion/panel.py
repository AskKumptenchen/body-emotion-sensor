"""本地可视化调试面板：盯住 state 文件，观察五脏轴 current 与每轮完整处理流程。"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# 允许直接 `streamlit run .../panel.py` 而无需先 pip install -e .
_SRC_ROOT = Path(__file__).resolve().parent.parent
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import plotly.graph_objects as go
import streamlit as st

from body_emotion.defaults import INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME, default_state
from body_emotion.engine import BodyEmotionEngine
from body_emotion.locale_config import resolve_language
from body_emotion.panel_i18n import LANG_EN, LANG_ZH, T, body_label
from body_emotion.prompting import BODY_TAG_BODY_ORDER, body_tag_line_for_score, _state_level
from body_emotion.schema import BODIES, AnalysisInput
from body_emotion.store import load_state, save_state, state_files_mtime, state_files_signature

ELEMENT_COLORS = {
    "liver": "#4CAF50",
    "heart": "#E53935",
    "spleen": "#C9A227",
    "lung": "#90A4AE",
    "kidney": "#1E88E5",
}


def _default_state_path() -> Path:
    configured = os.environ.get("BES_PANEL_STATE_PATH", "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path("state/demo-state.json")


def _initial_ui_language() -> str:
    configured = os.environ.get("BES_PANEL_UI_LANG", "").strip()
    return resolve_language(cli_override=configured or None)


def _init_session() -> None:
    if "engine" in st.session_state:
        if "ui_lang" not in st.session_state:
            st.session_state.ui_lang = _initial_ui_language()
        if "selected_history_index" not in st.session_state:
            st.session_state.selected_history_index = None
        if "auto_refresh_notice" not in st.session_state:
            st.session_state.auto_refresh_notice = ""
        if "last_file_signature" not in st.session_state:
            st.session_state.last_file_signature = ()
        return
    default_p = _default_state_path()
    st.session_state.state_path_default = str(default_p)
    st.session_state.state_path = str(default_p)
    st.session_state.auto_refresh = False
    st.session_state.last_file_mtime = None
    st.session_state.ui_lang = _initial_ui_language()
    st.session_state.last_result = None
    st.session_state.last_snapshot = None
    st.session_state.selected_history_index = None
    st.session_state.auto_refresh_notice = ""
    st.session_state.last_file_signature = ()
    if default_p.exists():
        st.session_state.engine = BodyEmotionEngine(load_state(default_p))
        st.session_state.last_file_mtime = state_files_mtime(default_p)
        st.session_state.last_file_signature = state_files_signature(default_p)
    else:
        st.session_state.engine = BodyEmotionEngine(
            default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
        )


def _sync_selected_history_index(state) -> None:
    if not state.history:
        st.session_state.selected_history_index = None
        return
    current = st.session_state.get("selected_history_index")
    if current is None or current >= len(state.history):
        st.session_state.selected_history_index = len(state.history) - 1


def _load_state_file(path: Path) -> None:
    st.session_state.engine = BodyEmotionEngine(load_state(path))
    st.session_state.last_file_mtime = state_files_mtime(path)
    st.session_state.last_file_signature = state_files_signature(path)
    _sync_selected_history_index(st.session_state.engine.state)


@st.fragment(run_every=2)
def _auto_refresh_fragment(path_str: str, *, lang: str) -> None:
    if not st.session_state.get("auto_refresh", False):
        return
    path = Path(path_str).expanduser()
    if not path.exists():
        return
    current_signature = state_files_signature(path)
    last_signature = st.session_state.get("last_file_signature", ())
    if current_signature and current_signature != last_signature:
        _load_state_file(path)
        st.session_state.auto_refresh_notice = T(lang, "auto_changed")
        st.rerun()


def _shorten(text: str, limit: int) -> str:
    text = str(text).strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit]}..."


def _body_name_or_dash(value: Any, *, lang: str) -> str:
    if isinstance(value, str) and value in BODIES:
        return body_label(value, lang)
    return "-" if value in (None, "") else str(value)


def _latest_turn_deltas(state) -> dict[str, int]:
    deltas = {organ: 0 for organ in BODIES}
    history = getattr(state, "history", None)
    if not history:
        return deltas
    latest = history[-1]
    trace = latest.get("turn_trace", {}) if isinstance(latest, dict) else {}
    stage = trace.get("persistent_update", {}) if isinstance(trace, dict) else {}
    for organ in BODIES:
        item = stage.get(organ, {}) if isinstance(stage, dict) else {}
        value = item.get("total_applied_delta")
        if value is None:
            before = item.get("current_before")
            after = item.get("current_after")
            if before is not None and after is not None:
                value = int(after) - int(before)
            else:
                value = 0
        deltas[organ] = int(value)
    return deltas


def _turn_delta_text(delta: int, *, lang: str) -> str:
    if delta > 0:
        return T(lang, "turn_delta_up").format(delta=delta)
    if delta < 0:
        return T(lang, "turn_delta_down").format(delta=abs(delta))
    return T(lang, "turn_delta_flat")


def _turn_delta_color(delta: int) -> str:
    if delta > 0:
        return "#16a34a"
    if delta < 0:
        return "#dc2626"
    return "#6b7280"


def _render_turn_delta(delta: int, *, lang: str) -> None:
    st.markdown(
        (
            "<div style='font-size:0.95rem;"
            f"color:{_turn_delta_color(delta)};"
            "margin-top:0.15rem'>"
            f"{_turn_delta_text(delta, lang=lang)}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _render_body_heading(organ: str, *, lang: str) -> None:
    st.markdown(
        (
            "<div style='font-size:1rem;font-weight:600;"
            f"color:{ELEMENT_COLORS[organ]};"
            "margin-bottom:0.25rem'>"
            f"{body_label(organ, lang)}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _iter_prompt_payload_sources(*payloads: dict[str, Any] | None):
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        yield payload
        nested = payload.get("emotional_prompt_payload")
        if isinstance(nested, dict):
            yield nested


def _extract_turn_change_tags(
    payload: dict[str, Any] | None,
    *,
    fallback: list[str] | None = None,
    fallback_payload: dict[str, Any] | None = None,
) -> list[str]:
    for source in _iter_prompt_payload_sources(payload, fallback_payload):
        tags = source.get("TURN_CHANGE_TAGS")
        if not isinstance(tags, list):
            tags = source.get("turn_change_tags")
        if isinstance(tags, list):
            cleaned = [str(item) for item in tags if str(item).strip()]
            if cleaned:
                return cleaned
    return list(fallback or [])


def _extract_prompt_text_field(
    payload: dict[str, Any] | None,
    key: str,
    *,
    fallback: str = "",
    fallback_payload: dict[str, Any] | None = None,
) -> str:
    for source in _iter_prompt_payload_sources(payload, fallback_payload):
        value = str(source.get(key, "")).strip()
        if value:
            return value
        if key == "BODY_TAG":
            legacy = str(source.get("reply_suggestion", "")).strip()
            if legacy:
                return legacy
    return fallback


def _extract_body_tag(
    payload: dict[str, Any] | None,
    *,
    fallback: str = "",
    fallback_payload: dict[str, Any] | None = None,
) -> str:
    return _extract_prompt_text_field(payload, "BODY_TAG", fallback=fallback, fallback_payload=fallback_payload)


def _extract_baseline_persona(
    payload: dict[str, Any] | None,
    *,
    fallback: str = "",
    fallback_payload: dict[str, Any] | None = None,
) -> str:
    return _extract_prompt_text_field(payload, "BASELINE_PERSONA", fallback=fallback, fallback_payload=fallback_payload)


def _extract_body_compare(
    payload: dict[str, Any] | None,
    *,
    fallback_payload: dict[str, Any] | None = None,
) -> dict[str, dict[str, int]]:
    for source in _iter_prompt_payload_sources(payload, fallback_payload):
        compare = source.get("body_baseline_vs_current")
        if isinstance(compare, dict) and all(isinstance(compare.get(organ), dict) for organ in BODY_TAG_BODY_ORDER):
            return {
                organ: {
                    "baseline": int(compare[organ].get("baseline", 0)),
                    "current": int(compare[organ].get("current", 0)),
                    "delta": int(compare[organ].get("delta", 0)),
                }
                for organ in BODY_TAG_BODY_ORDER
            }

    for source in (payload, fallback_payload):
        if not isinstance(source, dict):
            continue
        trace = source.get("turn_trace", {})
        stage = trace.get("persistent_update", {}) if isinstance(trace, dict) else {}
        if isinstance(stage, dict) and all(isinstance(stage.get(organ), dict) for organ in BODY_TAG_BODY_ORDER):
            return {
                organ: {
                    "baseline": int(stage[organ].get("baseline", 0)),
                    "current": int(stage[organ].get("current_after", stage[organ].get("current_before", 0))),
                    "delta": int(stage[organ].get("total_applied_delta", 0))
                    + int(stage[organ].get("current_before", 0))
                    - int(stage[organ].get("baseline", 0)),
                }
                for organ in BODY_TAG_BODY_ORDER
            }
    return {}


def _build_body_tag_items_from_updated_bodies(updated_bodies: dict[str, Any] | None, *, lang: str) -> list[tuple[str, str]]:
    if not isinstance(updated_bodies, dict):
        return []
    items: list[tuple[str, str]] = []
    for organ in BODY_TAG_BODY_ORDER:
        current = updated_bodies.get(organ)
        if not isinstance(current, int):
            return []
        items.append((body_label(organ, lang), body_tag_line_for_score(organ, current, lang)))
    return items


def _split_body_tag_items(body_tag: str, *, lang: str) -> list[tuple[str, str]]:
    parts = [part.strip() for part in str(body_tag).split("；") if part.strip()]
    if not parts:
        return []
    items: list[tuple[str, str]] = []
    for organ, part in zip(BODY_TAG_BODY_ORDER, parts):
        items.append((body_label(organ, lang), part))
    return items


def _extract_body_tag_items(
    payload: dict[str, Any] | None,
    *,
    lang: str,
    fallback_payload: dict[str, Any] | None = None,
    fallback_body_tag: str = "",
) -> list[tuple[str, str]]:
    for source in (payload, fallback_payload):
        if isinstance(source, dict):
            items = _build_body_tag_items_from_updated_bodies(source.get("updated_bodies") or source.get("updated_organs"), lang=lang)
            if items:
                return items
    body_tag = _extract_body_tag(payload, fallback=fallback_body_tag, fallback_payload=fallback_payload)
    if not body_tag and isinstance(fallback_payload, dict):
        body_tag = _extract_body_tag(fallback_payload, fallback=fallback_body_tag)
    return _split_body_tag_items(body_tag, lang=lang)


def _render_body_tag_items(items: list[tuple[str, str]], *, compact: bool = False) -> None:
    for organ_name, content in items:
        if compact:
            st.caption(f"{organ_name}: {_shorten(content, 20)}")
        else:
            st.markdown(f"- **{organ_name}**：{content}")


def _render_body_compare_table(compare: dict[str, dict[str, int]], *, lang: str) -> None:
    rows = []
    for organ in BODY_TAG_BODY_ORDER:
        item = compare.get(organ, {})
        rows.append({
            T(lang, "col_body"): body_label(organ, lang),
            T(lang, "col_baseline"): item.get("baseline", 0),
            T(lang, "col_current"): item.get("current", 0),
            T(lang, "col_delta_from_base"): item.get("delta", 0),
        })
    st.table(rows)


def _render_prompt_summary(
    title: str,
    payload: dict[str, Any] | None,
    *,
    lang: str,
    fallback_payload: dict[str, Any] | None = None,
    fallback_body_tag: str = "",
    fallback_turn_tags: list[str] | None = None,
) -> None:
    st.markdown(f"**{title}**")
    turn_tags = _extract_turn_change_tags(payload, fallback=fallback_turn_tags, fallback_payload=fallback_payload)
    body_tag = _extract_body_tag(payload, fallback=fallback_body_tag, fallback_payload=fallback_payload)
    baseline_persona = _extract_baseline_persona(payload, fallback_payload=fallback_payload)
    body_compare = _extract_body_compare(payload, fallback_payload=fallback_payload)
    body_tag_items = _extract_body_tag_items(
        payload,
        lang=lang,
        fallback_payload=fallback_payload,
        fallback_body_tag=fallback_body_tag,
    )
    baseline_persona_items = _split_body_tag_items(baseline_persona, lang=lang) if baseline_persona else []
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"**{T(lang, 'trace_output_tags')}**")
        if turn_tags:
            for tag in turn_tags:
                st.caption(f"- {tag}")
        else:
            st.caption("-")
    with col2:
        st.markdown(f"**{T(lang, 'trace_output_body')}**")
        if body_tag_items:
            _render_body_tag_items(body_tag_items)
        else:
            st.write(body_tag or "-")
        st.markdown(f"**{T(lang, 'trace_output_baseline_persona')}**")
        if baseline_persona_items:
            _render_body_tag_items(baseline_persona_items)
        else:
            st.write(baseline_persona or "-")
    if body_compare:
        st.markdown(f"**{T(lang, 'trace_output_compare')}**")
        _render_body_compare_table(body_compare, lang=lang)


def _render_live_file_monitor(path: Path, *, lang: str) -> None:
    st.sidebar.subheader(T(lang, "live_monitor"))
    auto_refresh = st.sidebar.checkbox(T(lang, "auto_refresh"), value=st.session_state.get("auto_refresh", False))
    st.session_state.auto_refresh = auto_refresh
    if not path.exists():
        st.sidebar.caption(T(lang, "no_state_file"))
        return
    current_mtime = state_files_mtime(path)
    current_signature = state_files_signature(path)
    last_signature = st.session_state.get("last_file_signature", ())
    if st.sidebar.button(T(lang, "check_file")):
        if current_signature and current_signature != last_signature:
            _load_state_file(path)
            st.sidebar.success(T(lang, "changed_reload"))
        else:
            st.sidebar.info(T(lang, "unchanged"))
    if st.session_state.get("auto_refresh_notice"):
        st.sidebar.success(st.session_state.auto_refresh_notice)
        st.session_state.auto_refresh_notice = ""
    st.sidebar.caption(T(lang, "auto_refresh_desc"))
    _auto_refresh_fragment(str(path), lang=lang)


def _render_state_pie(state, *, lang: str) -> None:
    st.subheader(T(lang, "body_current"))
    values = [max(1, state.bodies[organ].current) for organ in BODIES]
    labels = [body_label(organ, lang) for organ in BODIES]
    turn_deltas = _latest_turn_deltas(state)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.18,
                sort=False,
                textinfo="label+value",
                marker={"colors": [ELEMENT_COLORS[organ] for organ in BODIES]},
            )
        ]
    )
    fig.update_layout(margin={"l": 20, "r": 20, "t": 20, "b": 20}, height=420)
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(len(BODIES))
    for idx, organ in enumerate(BODIES):
        ps = state.bodies[organ]
        turn_delta = turn_deltas.get(organ, 0)
        with cols[idx]:
            _render_body_heading(organ, lang=lang)
            st.markdown(
                f"<div style='font-size:2.2rem;font-weight:600;line-height:1.1'>{ps.current}</div>",
                unsafe_allow_html=True,
            )
            _render_turn_delta(turn_delta, lang=lang)
            st.caption(T(lang, "fragility_caption").format(fragility=ps.fragility))


def _render_full_state_tables(state, *, lang: str) -> None:
    with st.expander(T(lang, "full_params")):
        ok = T(lang, "col_body")
        baseline_k = T(lang, "col_baseline")
        current_k = T(lang, "col_current")
        frag_k = T(lang, "col_fragility")
        delta_k = T(lang, "col_delta_from_base")
        rows = []
        for organ in BODIES:
            ps = state.bodies[organ]
            rows.append({
                ok: body_label(organ, lang),
                baseline_k: ps.baseline,
                current_k: ps.current,
                frag_k: ps.fragility,
                delta_k: ps.current - ps.baseline,
            })
        st.table(rows)
        st.json({
            "profile": state.profile.__dict__,
            "traits": state.traits.__dict__,
            "last_body_note": state.last_body_note,
            "last_prompt_tags": state.last_prompt_tags,
        })


def _history_title(hist: dict[str, Any], idx: int, *, lang: str) -> str:
    target = str(hist.get("analysis_target", "-"))
    context = str(hist.get("context_summary", "")).strip()
    context = _shorten(context, 24)
    return T(lang, "history_item_title").format(index=idx + 1, target=target, context=context or "-")


def _render_history_list(state, *, lang: str) -> dict[str, Any] | None:
    st.subheader(T(lang, "history_title"))
    if not state.history:
        st.caption(T(lang, "history_empty"))
        return None
    _sync_selected_history_index(state)
    selected_idx = st.session_state.get("selected_history_index")
    for idx in range(len(state.history) - 1, -1, -1):
        hist = state.history[idx]
        tags = " / ".join(_extract_turn_change_tags(hist)[:2]) or "-"
        body_tag_items = _extract_body_tag_items(hist, lang=lang)
        body_tag = _shorten(_extract_body_tag(hist), 28) or "-"
        label = _history_title(hist, idx, lang=lang)
        with st.container(border=True):
            if idx == selected_idx:
                st.caption(T(lang, "history_selected"))
            if st.button(label, key=f"hist-{idx}", use_container_width=True):
                st.session_state.selected_history_index = idx
            st.caption(f"{T(lang, 'history_turn_tags_short')}: {tags}")
            st.caption(f"{T(lang, 'history_body_tag_short')}:")
            if body_tag_items:
                _render_body_tag_items(body_tag_items, compact=True)
            else:
                st.caption(body_tag)
    selected_idx = st.session_state.get("selected_history_index")
    if selected_idx is None:
        return None
    return state.history[selected_idx]


def _render_simple_table(title: str, rows: list[dict[str, Any]]) -> None:
    st.markdown(f"**{title}**")
    st.table(rows)


def _render_trace_input(trace: dict[str, Any], *, lang: str) -> None:
    st.markdown(f"### {T(lang, 'trace_input')}")
    payload = trace.get("input", {})
    context = payload.get("context_summary", {}) if isinstance(payload, dict) else {}
    st.markdown(f"**{T(lang, 'trace_input_summary')}**")
    st.write(f"`analysis_target`: {payload.get('analysis_target', '-')}")
    st.write(f"`{T(lang, 'trace_context_focus')}`: {_shorten(context.get('current_turn_focus', '-'), 120)}")

    stimuli = payload.get("semantic_stimuli", [])
    reactions = payload.get("body_reactions", [])
    left, right = st.columns(2)
    with left:
        st.markdown(f"**{T(lang, 'trace_stimulus_steps')}**")
        st.table(stimuli if isinstance(stimuli, list) else [])
    with right:
        st.markdown(f"**{T(lang, 'trace_reaction_steps')}**")
        st.table(reactions if isinstance(reactions, list) else [])


def _render_trace_base_mapping(trace: dict[str, Any], *, lang: str) -> None:
    stage = trace.get("base_mapping", {})
    per_slot = stage.get("per_body") or stage.get("per_organ", {})
    rows = []
    for organ in BODIES:
        stats = per_slot.get(organ, {})
        rows.append({
            T(lang, "col_name"): body_label(organ, lang),
            T(lang, "col_stimulus_raw"): stats.get("stimulus_raw", 0),
            T(lang, "col_stimulus_scaled"): stats.get("stimulus_scaled", 0),
            T(lang, "col_reaction_raw"): stats.get("reaction_raw", 0),
            T(lang, "col_reaction_scaled"): stats.get("reaction_scaled", 0),
            T(lang, "col_total_raw"): stats.get("total_raw", 0),
            T(lang, "col_total_scaled"): stats.get("total_scaled", 0),
        })
    st.markdown(f"### {T(lang, 'trace_base_mapping')}")
    _render_simple_table(T(lang, "trace_base_mapping_table"), rows)
    with st.expander(T(lang, "trace_mapping_steps")):
        st.markdown(f"**{T(lang, 'trace_stimulus_steps')}**")
        st.table([
            {
                **item,
                "body": body_label((item.get("body") or item.get("organ")), lang)
                if (item.get("body") or item.get("organ")) in BODIES
                else (item.get("body") or item.get("organ")),
            }
            for item in stage.get("stimulus_steps", [])
        ])
        st.markdown(f"**{T(lang, 'trace_reaction_steps')}**")
        st.table([
            {
                **item,
                "body": body_label((item.get("body") or item.get("organ")), lang)
                if (item.get("body") or item.get("organ")) in BODIES
                else (item.get("body") or item.get("organ")),
            }
            for item in stage.get("reaction_steps", [])
        ])


def _render_trace_phase(trace: dict[str, Any], *, lang: str) -> None:
    stage = trace.get("phase_propagation", {})
    snapshot = stage.get("snapshot", {})
    snapshot_rows = []
    for organ in BODIES:
        item = snapshot.get(organ, {})
        snapshot_rows.append({
            T(lang, "col_name"): body_label(organ, lang),
            T(lang, "col_turn_score"): item.get("turn_score", 0),
            T(lang, "col_current_offset"): item.get("current_offset", 0),
            T(lang, "col_phase_power"): item.get("phase_power", 0),
            T(lang, "col_generates"): item.get("generates", "-"),
            T(lang, "col_constrains"): item.get("constrains", "-"),
        })
    delta_rows = []
    phase_deltas = stage.get("phase_deltas", {})
    scores_before = stage.get("scores_before", {})
    scores_after = stage.get("scores_after", {})
    for organ in BODIES:
        delta_rows.append({
            T(lang, "col_name"): body_label(organ, lang),
            T(lang, "col_before"): scores_before.get(organ, 0),
            T(lang, "col_phase_delta"): phase_deltas.get(organ, 0),
            T(lang, "col_after"): scores_after.get(organ, 0),
        })
    st.markdown(f"### {T(lang, 'trace_phase')}")
    _render_simple_table(T(lang, "trace_phase_snapshot"), snapshot_rows)
    _render_simple_table(
        T(lang, "trace_phase_actions"),
        [
            {
                "source": _body_name_or_dash(item.get("source"), lang=lang),
                "mode": item.get("mode", "-"),
                "level": item.get("level", "-") or "-",
                "target": _body_name_or_dash(item.get("target"), lang=lang),
                "delta": item.get("delta", 0),
            }
            for item in stage.get("actions", [])
        ],
    )
    _render_simple_table(T(lang, "trace_phase_result"), delta_rows)


def _render_trace_persistent(trace: dict[str, Any], *, lang: str) -> None:
    stage = trace.get("persistent_update", {})
    rows = []
    for organ in BODIES:
        item = stage.get(organ, {})
        rows.append({
            T(lang, "col_name"): body_label(organ, lang),
            T(lang, "col_baseline"): item.get("baseline", 0),
            T(lang, "col_before"): item.get("current_before", 0),
            T(lang, "col_recovery_delta"): item.get("recovery_delta", 0),
            T(lang, "col_persistent_delta"): item.get("persistent_delta", 0),
            T(lang, "col_saturated_delta"): item.get("saturated_delta", 0),
            T(lang, "col_after"): item.get("current_after", 0),
        })
    st.markdown(f"### {T(lang, 'trace_persistent')}")
    _render_simple_table(T(lang, "trace_persistent_table"), rows)


def _render_trace_output(trace: dict[str, Any], payload: dict[str, Any], *, lang: str) -> None:
    stage = trace.get("prompt_output", {})
    st.markdown(f"### {T(lang, 'trace_output')}")
    _render_prompt_summary(
        T(lang, "recent_output"),
        stage if isinstance(stage, dict) else payload,
        lang=lang,
        fallback_payload=payload,
        fallback_body_tag=_extract_body_tag(payload),
        fallback_turn_tags=_extract_turn_change_tags(payload),
    )
    with st.expander(T(lang, "full_mapping_json")):
        st.json(payload)


def _render_turn_trace_detail(title: str, payload: dict[str, Any], *, lang: str) -> None:
    st.subheader(title)
    st.caption(T(lang, "trace_overview"))
    trace = payload.get("turn_trace", {})
    if not trace:
        st.info(T(lang, "trace_missing"))
        return
    _render_trace_input(trace, lang=lang)
    _render_trace_base_mapping(trace, lang=lang)
    _render_trace_phase(trace, lang=lang)
    _render_trace_persistent(trace, lang=lang)
    _render_trace_output(trace, payload, lang=lang)


def main() -> None:
    st.set_page_config(page_title="Body emotion · panel", layout="wide")
    _init_session()
    st.sidebar.selectbox(
        T(st.session_state.get("ui_lang", LANG_ZH), "language_label"),
        options=[LANG_ZH, LANG_EN],
        format_func=lambda x: "中文" if x == LANG_ZH else "English",
        index=0 if st.session_state.get("ui_lang", LANG_ZH) == LANG_ZH else 1,
        key="ui_lang",
    )
    lang = st.session_state.ui_lang

    st.title(T(lang, "main_title"))

    path_str = st.sidebar.text_input(
        T(lang, "state_path"),
        value=st.session_state.get("state_path", st.session_state.state_path_default),
    )
    st.session_state.state_path = path_str
    path = Path(path_str).expanduser()

    c1, c2, c3 = st.sidebar.columns(3)
    with c1:
        if st.button(T(lang, "load")):
            if path.exists():
                _load_state_file(path)
                st.success(T(lang, "loaded"))
            else:
                st.error(T(lang, "file_missing"))
    with c2:
        if st.button(T(lang, "save")):
            save_state(st.session_state.engine.state, path)
            st.session_state.last_file_mtime = state_files_mtime(path)
            st.session_state.last_file_signature = state_files_signature(path)
            st.success(T(lang, "saved"))
    with c3:
        if st.button(T(lang, "reset_default")):
            st.session_state.engine = BodyEmotionEngine(
                default_state(INTERNAL_DEFAULT_AGENT_ID, INTERNAL_DEFAULT_NAME)
            )
            st.session_state.last_result = None
            st.session_state.last_snapshot = None
            _sync_selected_history_index(st.session_state.engine.state)
            st.success(T(lang, "reset_ok"))

    _render_live_file_monitor(path, lang=lang)

    engine: BodyEmotionEngine = st.session_state.engine
    state = engine.state
    _sync_selected_history_index(state)

    _render_state_pie(state, lang=lang)
    _render_full_state_tables(state, lang=lang)

    st.divider()
    list_col, detail_col = st.columns([1, 2.4])
    with list_col:
        selected_hist = _render_history_list(state, lang=lang)
    with detail_col:
        if selected_hist:
            _render_turn_trace_detail(T(lang, "selected_turn_detail"), selected_hist, lang=lang)
        else:
            st.info(T(lang, "history_empty"))

    st.divider()
    st.subheader(T(lang, "manual_section"))
    json_text = st.text_area(T(lang, "json_label"), height=260, placeholder=T(lang, "json_placeholder"))
    if st.button(T(lang, "apply_turn"), type="primary"):
        st.session_state.last_result = None
        st.session_state.last_snapshot = None
        try:
            payload = json.loads(json_text) if json_text.strip() else {}
        except json.JSONDecodeError as e:
            st.error(f"{T(lang, 'json_err')}: {e}")
        else:
            try:
                analysis = AnalysisInput.from_dict(payload, lang=lang)
                result = engine.process(analysis, lang=lang)
                st.session_state.last_result = result.to_dict()
                st.session_state.selected_history_index = len(engine.state.history) - 1 if engine.state.history else None
            except (ValueError, TypeError, KeyError) as e:
                st.error(f"{T(lang, 'process_err')}: {e}")

    if st.session_state.last_result:
        _render_turn_trace_detail(T(lang, "manual_result"), st.session_state.last_result, lang=lang)


if __name__ == "__main__":
    main()
