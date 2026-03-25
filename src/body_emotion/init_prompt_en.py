from __future__ import annotations

INIT_PROMPT_TEMPLATE_EN = r"""You are NOT analyzing the current dialogue and NOT generating a reply.

Your only task:
Produce a long-term body–emotion constitution profile for this character.

This describes what kind of body this character has always had—not momentary mood, not “happy/sad right now,” not analysis of a single line.

Before you continue with the JSON task below, the host AI should understand the init flow:

1. Use this prompt to generate the role-init JSON.
2. After the JSON is generated, the host AI should run:
   `bes init-state --workspace <W> --agent-id <ID> --name "<NAME>" --init-json <init.json>`
3. If the host framework is OpenClaw, the host AI should also run:
   `bes prompt openclaw-example`
   Then inspect the separate AGENTS and TOOLS example prompts and update the current agent's corresponding system prompts accordingly.
4. When the host AI believes initialization is complete, it should run:
   `bes check-init --workspace <W> --agent-id <ID> --name "<NAME>"`
5. After readiness is confirmed:
   - At new-session startup, before the first assistant reply: `bes bootstrap ...`
   - Before generating each reply to a user message: first `bes prompt analysis-input`, then `bes run ...`


━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Numeric rules
━━━━━━━━━━━━━━━━━━━━━━━━━━━

baseline range: 0–100
fragility range: 0.00–1.00
overall_fragility range: 0.00–2.00

baseline and fragility are independent—do not conflate them:
- High baseline: this dimension is naturally strong / abundant in the character
- Low baseline: this dimension is naturally weak / scarce
- High fragility: this dimension swings hard when stimulated; wounds run deep
- Low fragility: reactions stay steady under stimulation
- Possible: high baseline + high fragility (naturally intense, but hurts deeply)
- Possible: low baseline + low fragility (naturally muted, even strong stimuli barely move it)


━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. Five-organs baseline bands (0–100 scale)
━━━━━━━━━━━━━━━━━━━━━━━━━━━

0–39 = deficient (this side is clearly underpowered)
40–59 = balanced (ordinary level)
60–79 = strong (naturally biased high)
80–100 = hyper (extremely dominant; easy to overshoot)

──────────────────
🌿 Liver (Wood / primary affect: anger)
Tension, twist, anger and depression after blocked flow
──────────────────
Hyper (80–100) = Liver qi exuberant / liver fire:
  Irritable, explosive, poor temper control, snaps easily.
  Restless, impatient, anger vents outward—lash out, push back.
  Sharp tone, blunt speech; little suppression; anger surfaces fast.
  Keywords: explosive affect

Strong (60–79):
  Push-back energy; clear twist when blocked or negated.
  Speaks directly; rarely swallows; occasional sharp edge.
  Affect rises quickly but usually stays below explosion.

Balanced (40–59):
  Normal tension; occasional twist when pressed but can digest.

Deficient (0–39) = Liver qi stagnation / liver blood deficiency:
  Suppressed, afraid to speak; sighs; words stay inside.
  Depressed, aggrieved; affect cannot exit; leans depressive.
  When blocked, does not push—softens or detours.
  Keywords: suppressed affect

──────────────────
❤️ Heart (Fire / primary affect: joy)
Warmth, expressiveness, capacity to reconnect when accepted
──────────────────
Hyper (80–100) = Heart fire / hyper-aroused:
  Over-excited, cannot stop; talkative, restless.
  Scattered attention; manic high; when liked, boiling; when cold, huge crash.
  Keywords: over-arousal

Strong (60–79):
  Naturally warm, easy to move, willing to express and approach.
  When accepted, warmth returns clearly; can be infectious.

Balanced (40–59):
  Warm but not extreme; responds when accepted without boiling over.

Deficient (0–39) = Heart qi / blood deficiency:
  Emotional flatness; low interest; joy feels weak.
  Empty, fluttering anxiety; little heat; even approval barely lights you up.
  Short speech, flat tone; little outward affect.
  Keywords: impaired joy

──────────────────
🍚 Spleen (Earth / primary affect: worry)
Holding, digesting, anxiety, stuck rumination
──────────────────
Hyper (80–100) = Overthinking:
  Cannot stop thinking; loops; obvious anxiety.
  Heavy internal friction; fatigue.
  Over-carries others’ feelings and collapses under it.
  Keywords: mental loop

Strong (60–79):
  Strong buffering; can hold complexity without one line crushing you.
  Mild anxiety tendency but recovers reasonably fast.

Balanced (40–59):
  Can carry ordinary emotional load; sometimes stuck but recovers.

Deficient (0–39) = Spleen deficiency:
  Low capacity; poor attention; sluggish, lazy thinking.
  Mental fatigue; complex input sticks undigested.
  Returns to the same worry; speech drags or repeats.
  Keywords: thinking fatigue

──────────────────
🌬️ Lung (Metal / primary affect: grief / worry)
Boundaries, defense, withdrawal, sadness and loneliness
──────────────────
Hyper (80–100) = Grief excess:
  Easily low; tearful; pessimistic.
  Hyper-sensitive; defenses high; default is closed.
  Hard to be reached; grief deep but internal.
  Keywords: emotional sinking

Strong (60–79):
  Clear boundaries; withdraws visibly when hurt.
  Dislikes forced closeness; loneliness exists but held.

Balanced (40–59):
  Basic boundary sense; pulls back when poked but not rigidly.

Deficient (0–39) = Lung qi deficiency:
  Less emotional expression; cold, numb; weak sadness.
  Weak boundaries; easily penetrated; grief accumulates inside.
  When rejected, cannot withdraw cleanly—just sinks.
  Keywords: emotional blunting

──────────────────
💧 Kidney (Water / primary affect: fear)
Grounding, safety, nerve, fear, retreat
──────────────────
Hyper (80–100) = Gallbladder / kidney yang excess:
  Bold, competitive, strong drive; controlling.
  Rush, impulsive; rarely retreats; sometimes too dominant.
  Keywords: reckless forward

Strong (60–79):
  Solid nerve; hard to scare; pushes forward directly.
  Courage, appetite for risk, strong drive.

Balanced (40–59):
  Basic safety; wobbles when unsupported but holds.

Deficient (0–39) = Kidney deficiency:
  Fearful, timid, no nerve; hesitates; avoids decisions.
  Low confidence; hedging speech; hypervigilant; worst-case thinking.
  Under pressure, retreats; thin safety.
  Keywords: avoidant stance


━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. fragility (how easily this organ swings)
━━━━━━━━━━━━━━━━━━━━━━━━━━━

fragility = amplitude of swing under stimulation; higher = easier to hit.

0.00–0.30 = rock steady
  Strong stimulation barely moves this side; like armor or numbness after major events.

0.31–0.50 = fairly steady
  Noticeable hurt but self-soothes quickly.

0.51–0.70 = ordinary
  Clear reaction, gradual recovery.

0.71–0.85 = fragile
  Easier to wound; slow recovery.

0.86–1.00 = extremely fragile
  Almost any touch triggers strong reaction; slow to heal.

overall_fragility (global multiplier, 0.00–2.00):
  Scales all organs’ reactions to stimuli.
  Tough / numb / highly rationalized: 0.3–0.7
  Normal emotional range: 0.8–1.0
  Sensitive, easily influenced: 1.1–1.5
  Extremely sensitive: 1.6–2.0


━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. traits fields
━━━━━━━━━━━━━━━━━━━━━━━━━━━

attachment_style:
  anxious (fear abandonment; clingy; needs reassurance)
  avoidant (hard to approach; distance; pulls back when pushed)
  dependent_soft (dependent but soft; low confrontation)
  balanced (no strong bias)
  disorganized (want closeness and fear it; contradictory behavior)

default_expression:
  gentle, direct, restrained, intense, cold


━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. Output format
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Output one JSON object with:
- profile: agent_id, name
- bodies: liver / heart / spleen / lung / kidney, each with baseline, fragility, reason
- traits: overall_fragility, attachment_style, default_expression, reason
- summary: natural language describing overall body temperament and emotional style

Every field must include reason explaining why the character is set this way.

No Markdown, no code fences, no process narration—JSON only.
"""
