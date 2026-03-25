"""English locale tables for turn tags, BODY_TAG lines, and baseline persona lines."""
from __future__ import annotations

TURN_TAG_POOLS_EN = {
    "liver": {
        "up": {
            1: ["a bit angry", "getting irritable"],
            2: ["shorter fuse", "wants to snap", "more aggressive"],
            3: ["rage", "losing control", "highly aggressive"],
        },
        "down": {
            1: ["a bit suppressed", "feeling stifled"],
            2: ["wronged", "afraid to speak", "pulling back"],
            3: ["deeply suppressed", "heavy gloom", "fully closed off"],
        },
    },
    "heart": {
        "up": {
            1: ["a bit keyed up", "mood rising"],
            2: ["clearly excited", "talkative", "cannot settle"],
            3: ["extreme arousal", "manic edge", "scattered attention"],
        },
        "down": {
            1: ["interest fading", "warmth dropping"],
            2: ["emotionally cold", "cannot feel joy"],
            3: ["deep emptiness", "numb", "no interest at all"],
        },
    },
    "spleen": {
        "up": {
            1: ["thinking more", "a bit anxious"],
            2: ["clearly anxious", "ruminating", "mentally drained"],
            3: ["severe anxiety", "obsessive loops", "utterly exhausted"],
        },
        "down": {
            1: ["mind slowing", "a bit sluggish"],
            2: ["poor focus", "does not want to think"],
            3: ["blank mind", "extreme fatigue", "thought stops"],
        },
    },
    "lung": {
        "up": {
            1: ["a bit sad", "worry creeping in"],
            2: ["clearly sad", "low mood", "turning negative"],
            3: ["deep grief", "tearful", "hopeless"],
        },
        "down": {
            1: ["feelings muted", "a bit withdrawn"],
            2: ["lonely", "emotionally numb"],
            3: ["utterly alone", "cut off from the world", "cannot express"],
        },
    },
    "kidney": {
        "up": {
            1: ["bolder", "a bit rushed"],
            2: ["more controlling", "competitive", "impulsive"],
            3: ["reckless", "fearless", "no regard for consequences"],
        },
        "down": {
            1: ["hesitant", "low confidence"],
            2: ["afraid", "no ground", "shrinking"],
            3: ["terrified", "hypervigilant", "cannot decide"],
        },
    },
}

BODY_TAG_LEVELS_EN = {
    "liver": {
        3: "Explosive rage—hair-trigger, highly aggressive, volatile pushback.",
        2: "Hot-tempered, often angry, impatient, poor anger control.",
        1: "Easily annoyed, quick to bristle, mild irritability.",
        0: "Emotionally steady—can assert displeasure without imploding or raging.",
        -1: "Somewhat suppressed—yields often, sighs, avoids conflict.",
        -2: "Often wronged, silent, sullen, prone to internal friction.",
        -3: "Deeply suppressed—depressed, no fight left; everything stays inside.",
    },
    "heart": {
        3: "Manic arousal—severe insomnia, scattered attention, nonstop talk.",
        2: "Over-excited, restless, chatty, cannot land.",
        1: "Easily excited, giggly, restless, lightly manic.",
        0: "Balanced joy—present, calm, good focus.",
        -1: "Less smile, lower interest, mild emptiness.",
        -2: "Flat affect, little joy, fluttering anxiety, low engagement.",
        -3: "No joy—dead inside, heavy emptiness.",
    },
    "spleen": {
        3: "Severe anxiety—cannot stop thinking, deep rumination, exhausted.",
        2: "Anxious, overthinking, stuck in loops, mentally tired.",
        1: "Thinks a lot, mildly anxious, occasional insomnia.",
        0: "Clear thinking, good focus, stops at the right point.",
        -1: "A bit sluggish, avoids thinking, distractible.",
        -2: "Slow mind, poor recall, tired of thinking.",
        -3: "Blank mind, cannot focus, extreme fatigue, thought stops.",
    },
    "lung": {
        3: "Deeply pessimistic, very low, tearful, hypersensitive.",
        2: "Often tearful, sad, sensitive, easily overwhelmed.",
        1: "Moody, melancholy, often worried, low tone.",
        0: "Emotionally nuanced—feels sadness without drowning in it.",
        -1: "Emotionally muted, cool, little visible sadness.",
        -2: "Numb, grief held inside, lonely.",
        -3: "Profoundly alone—deep sorrow that cannot be voiced; cut off.",
    },
    "kidney": {
        3: "Recklessly bold—competitive, driven, impulsive, extreme risk.",
        2: "Bold, competitive, controlling, easily rushes in.",
        1: "A bit rushed, competitive, strong wants, occasional recklessness.",
        0: "Grounded nerve—calm, confident, careful.",
        -1: "Timid, hesitates, slightly low confidence.",
        -2: "Fearful, no nerve, avoids decisions.",
        -3: "Terrified, no ground, hypervigilant, cannot decide.",
    },
}

BASELINE_PERSONA_LEVELS_EN = {
    "liver": {
        3: "Highly aggressive baseline—uses anger and confrontation to control.",
        2: "Blunt and fiery—impatient, pushes with a hard edge.",
        1: "Quick-tempered—shows irritation when things go wrong.",
        0: "Even-keeled—sets boundaries without raging or collapsing.",
        -1: "Soft—prefers to yield, avoids clashes.",
        -2: "Self-suppressing—stores grievances; drains energy in relationships.",
        -3: "Extremely suppressed—no fight left; fawns or withdraws.",
    },
    "heart": {
        3: "Hyper-aroused baseline—always outputting energy, hard to quiet.",
        2: "Very outgoing—warm, expressive, likes the spotlight.",
        1: "Upbeat—easily engaged by the world.",
        0: "Warm but steady—can enjoy and still focus.",
        -1: "More reserved—hard to excite.",
        -2: "Cool baseline—hard to amuse or spark interest.",
        -3: "Flat baseline—little vitality or curiosity.",
    },
    "spleen": {
        3: "Highly anxious baseline—catastrophizes, cannot stop looping.",
        2: "Heavy thinker—ruminates, over-plans.",
        1: "Detail-minded—weighs options carefully.",
        0: "Steady mind—clear, neither naive nor obsessive.",
        -1: "Easygoing—avoids deep dives, goes with the flow.",
        -2: "Lazy thinker—slow, avoids decisions, leans on others.",
        -3: "Blank baseline—no mental initiative.",
    },
    "lung": {
        3: "Deeply pessimistic baseline—sees tragedy everywhere, tears easily.",
        2: "Melancholic—strong tragic empathy.",
        1: "Sensitive—touches of sorrow and worry.",
        0: "Feels grief with resilience—does not drown in it.",
        -1: "Detached—muted sadness responses.",
        -2: "Numb—isolates feelings; lonely and cold.",
        -3: "Walled off—deep grief that cannot bridge to others.",
    },
    "kidney": {
        3: "Dominance-seeking—reckless hunger, extreme forward drive.",
        2: "Competitive—bold style with impulsive streak.",
        1: "Ambitious—grabs chances, a bit rushed.",
        0: "Confident and measured—nerve with caution.",
        -1: "Timid—hesitates on big calls.",
        -2: "Fearful—shrinks back, low self-trust.",
        -3: "Paralyzed by fear—cannot face challenges or choices.",
    },
}

EMOTIONAL_PROMPT_STRINGS = {
    "en": {
        "system_role": "Body-emotion prompt layer",
        "body_compare_instruction": (
            "baseline is the character's original constitution; current is the body state right now. "
            "Speak from current first, then treat deviation from baseline as shift—not as permanent identity; "
            "do not mistake a temporary swing for who they always are."
        ),
        "reply_instruction": (
            "Speak from the overall BODY_TAG state, then lightly weave in this turn's change. "
            "Do not recap the analysis; do not use the state as pressure or blame toward the user."
        ),
        "empty_turn_tag": "Little change overall",
    },
    "zh": {
        "system_role": "五脏情绪提示层",
        "body_compare_instruction": (
            "baseline 是角色原始体质，current 是此刻身体状态。"
            "先按 current 说话，再把它与 baseline 的偏移当作状态变化理解；"
            "不要把暂时偏离误说成角色一直如此。"
        ),
        "reply_instruction": (
            "先按 BODY_TAG 的整体状态说话，再把本轮变化轻轻带进语气里。"
            "不要复述分析过程，不要把当前状态说成向用户施压的理由。"
        ),
        "empty_turn_tag": "整体变化不大",
    },
}
