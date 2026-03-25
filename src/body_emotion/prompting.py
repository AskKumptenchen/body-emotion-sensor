from __future__ import annotations

from typing import Any, Dict, List

from .locale_config import LANG_EN, LANG_ZH, normalize_lang
from .prompting_i18n_data import (
    BASELINE_PERSONA_LEVELS_EN,
    BODY_TAG_LEVELS_EN,
    EMOTIONAL_PROMPT_STRINGS,
    TURN_TAG_POOLS_EN,
)
from .schema import AnalysisInput, MappingResult, State

TURN_TAG_POOLS_ZH = {
    "liver": {
        "up": {1: ["有点生气", "开始烦躁"], 2: ["脾气变大", "想发火", "攻击性增强"], 3: ["暴怒", "情绪失控", "极具攻击性"]},
        "down": {1: ["有点压抑", "感到憋屈"], 2: ["感到委屈", "不敢表达", "退缩"], 3: ["极度压抑", "重度郁闷", "完全封闭"]},
    },
    "heart": {
        "up": {1: ["有点激动", "情绪变高"], 2: ["明显兴奋", "话变多", "静不下来"], 3: ["极度亢奋", "狂躁", "注意力涣散"]},
        "down": {1: ["兴致下降", "热情减少"], 2: ["情绪冷淡", "感受不到快乐"], 3: ["极度空虚", "彻底麻木", "毫无兴趣"]},
    },
    "spleen": {
        "up": {1: ["开始多想", "有点焦虑"], 2: ["明显焦虑", "反复纠结", "精神内耗"], 3: ["重度焦虑", "强迫思考", "精神极度疲惫"]},
        "down": {1: ["脑子变慢", "有点懒散"], 2: ["注意力不集中", "不想动脑"], 3: ["大脑空白", "极度疲倦", "思维停滞"]},
    },
    "lung": {
        "up": {1: ["有点难过", "开始发愁"], 2: ["明显悲伤", "情绪低落", "变得消极"], 3: ["极度悲伤", "崩溃易哭", "绝望"]},
        "down": {1: ["情绪变淡", "有点抽离"], 2: ["感到孤独", "情感麻木"], 3: ["极度孤独", "与世界隔离", "无法表达情感"]},
    },
    "kidney": {
        "up": {1: ["胆子变大", "有点急躁"], 2: ["控制欲增强", "好胜心起", "容易冲动"], 3: ["极度冒进", "胆大妄为", "不顾后果"]},
        "down": {1: ["有点犹豫", "缺乏自信"], 2: ["感到害怕", "没有底气", "畏缩"], 3: ["极度恐惧", "高度警觉", "完全不敢做决定"]},
    },
}

BODY_TAG_LEVELS_ZH = {
    "liver": {
        3: "暴怒失控，一点就炸，具有强烈攻击性，容易狂躁顶撞。",
        2: "脾气火爆，经常发火，急躁易怒，控制不住脾气。",
        1: "容易不耐烦，遇事易起急，微有怒意，略显烦躁。",
        0: "情绪稳定，能合理表达不满，不憋屈也不暴躁。",
        -1: "略显压抑，遇事多忍让，偶有叹气，不太愿争辩。",
        -2: "经常委屈，不敢表达，郁闷憋屈，容易内耗。",
        -3: "极度压抑，深陷抑郁，毫无反抗力，情绪完全憋在心里。",
    },
    "heart": {
        3: "狂躁亢奋，严重失眠，注意力彻底涣散，多语不休。",
        2: "异常兴奋，难以平静，话多浮躁，停不下来。",
        1: "容易激动，喜笑不休，静不下来，略显浮躁。",
        0: "喜乐有度，内心充实平静，专注力好。",
        -1: "笑容减少，兴致不高，偶感空虚，热情减退。",
        -2: "情绪淡漠，缺乏快乐，容易心慌，提不起兴趣。",
        -3: "毫无喜悦，彻底提不起兴趣，心如死灰，重度空虚。",
    },
    "spleen": {
        3: "极度焦虑，想太多停不下来，严重内耗，反复纠结，精神极度疲劳。",
        2: "明显焦虑，思虑过重，难以停止想事，常感心累。",
        1: "容易多想，略显焦虑，心思较重，偶尔失眠。",
        0: "思维清晰，专注力好，思考适可而止，不纠结。",
        -1: "略微懒散，不太愿意思考，注意力易分散。",
        -2: "思维迟钝，记忆力减退，懒得想，精神疲惫。",
        -3: "大脑空白，完全无法集中精力，极度倦怠，思维停滞。",
    },
    "lung": {
        3: "极度悲观，情绪极度低落，容易大哭，对外界极度敏感。",
        2: "经常落泪，消极悲伤，对外界敏感，容易崩溃。",
        1: "容易伤感，多愁善感，常有忧虑，情绪偏低落。",
        0: "情感细腻，能自然释怀，不沉溺于悲伤。",
        -1: "情感略淡，不太表露悲伤，略显冷淡。",
        -2: "情感麻木，内在压抑着悲伤，常感孤独。",
        -3: "极度孤独，内心深处充满愁苦与悲伤，难以向外表达，感觉被世界隔离。",
    },
    "kidney": {
        3: "胆大包天，好斗好胜，欲望极强，急躁易上头，行为极度冒进。",
        2: "胆子大，好胜心强，控制欲强，做事容易冲动上头。",
        1: "略显急躁，喜欢竞争，欲望偏强，偶尔冒进。",
        0: "胆气平和，从容不迫，自信且谨慎。",
        -1: "略显胆怯，遇事容易犹豫，信心略显不足。",
        -2: "胆小怕事，缺乏底气，不敢决策，畏首畏尾。",
        -3: "极度畏惧，毫无底气，处于高度警觉和惊恐状态，完全不敢决策。",
    },
}

BASELINE_PERSONA_LEVELS_ZH = {
    "liver": {
        3: "性格极具攻击性，底色暴躁，习惯用愤怒和对抗来掌控局面。",
        2: "性格火爆，直来直去，容易急躁，习惯用强硬态度表达诉求。",
        1: "性格偏急，略带锋芒，遇到不顺心的事容易表现出不耐烦。",
        0: "性格平和，不卑不亢，能合理表达边界，不轻易发火也不过度忍让。",
        -1: "性格温和偏软，习惯退让，不太喜欢与人发生正面冲突。",
        -2: "性格隐忍，习惯把委屈藏在心里，容易在人际关系中内耗。",
        -3: "性格极度压抑，完全没有攻击性，习惯性讨好或自我封闭。",
    },
    "heart": {
        3: "性格极度亢奋，底色狂热，永远处于高能量输出状态，难以安静。",
        2: "性格非常外向，热情洋溢，表现欲强，喜欢成为焦点。",
        1: "性格开朗，比较活跃，容易被外界事物调动起兴致。",
        0: "性格开朗有度，内心充盈，既能享受快乐也能保持专注平静。",
        -1: "性格偏内敛，不太容易兴奋，对外界事物的热情相对有限。",
        -2: "性格冷淡，底色偏凉，很难被逗乐或产生强烈的兴趣。",
        -3: "性格极度淡漠，底色灰暗，对任何事物都提不起兴趣，缺乏生命力。",
    },
    "spleen": {
        3: "性格极度敏感多虑，底色焦虑，习惯把所有事情往最坏处想，停不下来。",
        2: "性格心思极重，容易纠结，习惯反复推敲和过度思考。",
        1: "性格比较细腻，想得比较多，做决定前习惯反复权衡。",
        0: "性格稳重，思维清晰，思考适度，既不盲目也不过度纠结。",
        -1: "性格比较随性，不太喜欢深度思考，习惯顺其自然。",
        -2: "性格比较慵懒，思维偏慢，不喜欢动脑筋，习惯依赖他人决策。",
        -3: "性格极度迟钝，完全缺乏思考主动性，习惯性大脑空白。",
    },
    "lung": {
        3: "性格极度悲观，底色凄凉，习惯从负面视角看待世界，极易被触动落泪。",
        2: "性格多愁善感，底色偏忧郁，对外界事物有着强烈的悲剧共情。",
        1: "性格偏感性，容易伤春悲秋，内心带着一丝淡淡的忧愁。",
        0: "性格情感细腻且有韧性，能感知悲伤但不会沉溺其中，能自然释怀。",
        -1: "性格相对抽离，情感体验偏淡，不太容易产生强烈的悲伤共鸣。",
        -2: "性格比较麻木，习惯压抑或隔离情感，显得有些孤独和冷漠。",
        -3: "性格极度封闭，内心深处充满难以表达的愁苦，与世界存在深深的隔阂。",
    },
    "kidney": {
        3: "性格极度慕强，底色狂妄，欲望极强，行事不计后果，极度冒进。",
        2: "性格好胜心强，控制欲高，胆子大，行事风格大胆且带有冲动色彩。",
        1: "性格比较积极进取，有野心，遇到机会敢于争取，略带急躁。",
        0: "性格从容自信，进退有度，既有底气又懂得谨慎行事。",
        -1: "性格略显胆怯，底气不足，遇到重大决策时容易犹豫不决。",
        -2: "性格胆小怕事，缺乏自信，习惯性退缩，畏首畏尾。",
        -3: "性格极度怯懦，底色充满恐惧与警觉，完全不敢面对任何挑战或决策。",
    },
}

TURN_TAG_POOLS = TURN_TAG_POOLS_ZH
BODY_TAG_LEVELS = BODY_TAG_LEVELS_ZH
BASELINE_PERSONA_LEVELS = BASELINE_PERSONA_LEVELS_ZH

BODY_TAG_BODY_ORDER = ("heart", "spleen", "liver", "lung", "kidney")


def _lang_key(lang: str | None) -> str:
    return LANG_ZH if normalize_lang(lang) == LANG_ZH else LANG_EN


def _turn_pools(lang: str | None) -> Dict[str, Any]:
    return TURN_TAG_POOLS_ZH if _lang_key(lang) == LANG_ZH else TURN_TAG_POOLS_EN


def _body_tag_levels(lang: str | None) -> Dict[str, Any]:
    return BODY_TAG_LEVELS_ZH if _lang_key(lang) == LANG_ZH else BODY_TAG_LEVELS_EN


def _baseline_persona_levels(lang: str | None) -> Dict[str, Any]:
    return BASELINE_PERSONA_LEVELS_ZH if _lang_key(lang) == LANG_ZH else BASELINE_PERSONA_LEVELS_EN


def _body_joiner(lang: str | None) -> str:
    return "；" if _lang_key(lang) == LANG_ZH else "; "


def empty_turn_change_fallback(lang: str | None = LANG_EN) -> str:
    return EMOTIONAL_PROMPT_STRINGS[_lang_key(lang)]["empty_turn_tag"]


def body_tag_line_for_score(organ: str, current: int, lang: str | None = LANG_EN) -> str:
    """Single-organ BODY_TAG line for a current score (used by UI)."""
    level = _state_level(current)
    return _body_tag_levels(lang)[organ][level]


def _intensity_bucket(value: int) -> int:
    magnitude = abs(value)
    if magnitude >= 20:
        return 3
    if magnitude >= 14:
        return 2
    if magnitude >= 8:
        return 1
    return 0


def _state_level(current: int) -> int:
    if current >= 90:
        return 3
    if current >= 80:
        return 2
    if current >= 60:
        return 1
    if current >= 40:
        return 0
    if current >= 20:
        return -1
    if current >= 10:
        return -2
    return -3


def _dedup(items: List[str]) -> List[str]:
    output: List[str] = []
    for item in items:
        if item not in output:
            output.append(item)
    return output


def _pick_tags(pool: Dict[str, Dict[int, List[str]]], value: int) -> List[str]:
    bucket = _intensity_bucket(value)
    if bucket == 0:
        return []
    direction = "up" if value > 0 else "down"
    return pool[direction][bucket]


def build_turn_change_tags(result: MappingResult, lang: str | None = LANG_EN) -> List[str]:
    pools = _turn_pools(lang)
    tags: List[str] = []
    for body in ("heart", "lung", "kidney", "spleen", "liver"):
        change = result.body_state_changes[body]
        tags.extend(_pick_tags(pools[body], change.score))
    if not tags:
        return [EMOTIONAL_PROMPT_STRINGS[_lang_key(lang)]["empty_turn_tag"]]
    return _dedup(tags)[:8]


def _build_body_snapshot(state: State, *, score_field: str) -> Dict[str, int]:
    return {
        body: int(getattr(state.bodies[body], score_field))
        for body in BODY_TAG_BODY_ORDER
    }


def build_body_baseline_vs_current(state: State) -> Dict[str, Dict[str, int]]:
    comparison: Dict[str, Dict[str, int]] = {}
    for body in BODY_TAG_BODY_ORDER:
        slot = state.bodies[body]
        comparison[body] = {
            "baseline": slot.baseline,
            "current": slot.current,
            "delta": slot.current - slot.baseline,
        }
    return comparison


def build_body_tag(state: State, *, score_field: str = "current", lang: str | None = LANG_EN) -> str:
    levels = _body_tag_levels(lang)
    parts: List[str] = []
    for body in BODY_TAG_BODY_ORDER:
        score = int(getattr(state.bodies[body], score_field))
        level = _state_level(score)
        parts.append(levels[body][level])

    return _body_joiner(lang).join(_dedup(parts))


def build_baseline_persona(state: State, lang: str | None = LANG_EN) -> str:
    levels = _baseline_persona_levels(lang)
    parts: List[str] = []
    for body in BODY_TAG_BODY_ORDER:
        score = int(state.bodies[body].baseline)
        level = _state_level(score)
        parts.append(levels[body][level])

    return _body_joiner(lang).join(_dedup(parts))


def build_prompt_output_min(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "TURN_CHANGE_TAGS": list(payload.get("TURN_CHANGE_TAGS", payload.get("turn_change_tags", []))),
        "BODY_TAG": str(payload.get("BODY_TAG", "")),
        "BASELINE_PERSONA": str(payload.get("BASELINE_PERSONA", "")),
    }


def build_emotional_prompt_payload(
    state: State, result: MappingResult, analysis: AnalysisInput, lang: str | None = LANG_EN
) -> Dict[str, object]:
    lk = _lang_key(lang)
    strings = EMOTIONAL_PROMPT_STRINGS[lk]
    turn_change_tags = build_turn_change_tags(result, lang=lang)
    body_tag = build_body_tag(state, lang=lang)
    baseline_persona = build_baseline_persona(state, lang=lang)
    baseline_snapshot = _build_body_snapshot(state, score_field="baseline")
    current_snapshot = _build_body_snapshot(state, score_field="current")
    baseline_vs_current = build_body_baseline_vs_current(state)
    return {
        "system_role": strings["system_role"],
        "state_version": "emotion-prompt-v6",
        "use_mode": "persistent_context",
        "TURN_CHANGE_TAGS": turn_change_tags,
        "BODY_TAG": body_tag,
        "BASELINE_PERSONA": baseline_persona,
        "body_baseline_snapshot": baseline_snapshot,
        "body_current_snapshot": current_snapshot,
        "body_baseline_vs_current": baseline_vs_current,
        "body_compare_instruction": strings["body_compare_instruction"],
        "reply_instruction": strings["reply_instruction"],
    }
