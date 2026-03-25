<h1 align="center">🫀 Body Emotion Sensor</h1>

<p align="center">
  Give your AI agent a persistent emotional system based on the TCM Five Zang and Five Elements model.
</p>

<p align="center">
  <strong>"We believe that General AI Agents should possess true emotions. Our vision is to create an emotional system for agents that mirrors the authentic structure of the human body."</strong>
</p>

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue" />
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-brightgreen" />
  <img alt="GitHub stars" src="https://img.shields.io/github/stars/AskKumptenchen/body-emotion-sensor?style=flat" />
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#what-happens">What Happens</a> ·
  <a href="#how-it-works">How It Works</a> ·
  <a href="./docs/README.zh-CN.md">简体中文</a>
</p>

<img src="./docs/cover_web.webp" alt="Body Emotion Sensor Cover" width="100%" />

## Why Body Emotion Sensor? 💖

Do you ever feel that AI agents lack a true sense of "self"? They might simulate emotions in text, but they don't have a persistent internal state that carries over between conversations. 

**Body Emotion Sensor is here to change that.**

<a id="quick-start"></a>

## Quick Start 🚀

Send this to your AI Agent, such as OpenClaw:

📥 **Install:**

```text
Please install Body Emotion Sensor for me: pip install body-emotion-sensor && bes help
```

<a id="what-happens"></a>

## What happens when an Agent integrates Body Emotion Sensor? 🧩

1. **Self-Generated Identity:** The agent automatically calls `bes init-state` to create a persistent set of "Five Zang" (internal organ) parameters that match its unique personality and constitution.
2. **Emotional Context Awareness:** During every turn, the agent identifies how the conversation affects its internal state based on its persona and the context of the interaction.
3. **Dynamic Body Updates:** By calling `bes run`, the agent updates its internal "health" and emotional balance using TCM-inspired logic. These changes map directly to emotional cues, making the agent's replies feel authentic and deeply felt.
4. **Emotional Continuity:** The agent's state is saved persistently. Even when starting a new session, it remembers its previous "physical" and emotional condition, preventing "emotional amnesia."

<a id="how-it-works"></a>

## How It Works (Simplified) ✨

Body Emotion Sensor does not "guess" emotions; it simulates a biological feedback loop:

- **The Five Zang System:** We map emotions to five core "body axes," establishing a correspondence between the Five Elements, Five Zang, and emotions:

| Element | Organ (Zang) | Core Emotion | Deficiency (Weak) | Balance | Excess (Strong) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Wood** | Liver | Anger / Depression | Grievance, Depression, Repression | Stable, Smooth Flow | Irritability, Rage, Out of Control |
| **Fire** | Heart | Joy / Shock | Emptiness, Apathy, Despair | Calm, Moderate Joy | Hyperexcitement, Loquacity, Mania |
| **Earth** | Spleen | Pensiveness / Anxiety | Lassitude, Stagnation, Blank Mind | Clear Thinking, Focused | Anxiety, Overthinking, Entrenchment |
| **Metal** | Lung | Grief / Sorrow | Numbness, Loneliness, Deep Sorrow | Delicate, Natural Release | Sadness, Pessimism, Extreme Grief |
| **Water** | Kidney | Fear / Fright | Fear, Cowering, Hyper-vigilance | Composed, Confident | Recklessness, Impulsivity, Audacity |
- **The Input:** Every interaction is broken down into "Stimuli" (what happened) and "Reactions" (how the body felt).
- **The Calculation:** 
    - **Emotional Mapping & Impact:** Each stimulus adds or subtracts points from specific organs based on predefined weights.
        - **Fragility & Persona:** Each agent has a unique Fragility coefficient tied to its persona. For instance, a "tough" agent has lower fragility and smaller emotional swings, while a "sensitive" or "fragile-hearted" agent has higher fragility, reacting more intensely to stimuli with greater state fluctuations.
    - **Interaction:** Like real organs, they affect each other based on TCM and BaZi principles: **"Excess leads to restriction; Balance leads to generation."**
        - **Excess (Restriction Over Generation):** When an organ's energy is too high (Excess), it prioritizes "restricting" its target organ over "generating" its successor. *Example: Overactive Liver (Wood) will fiercely restrict the Spleen (Earth) while failing to nourish the Heart (Fire).*
        - **Balance (Generation Over Restriction):** When an organ is balanced or weak, it prioritizes "generating" and nourishing its successor. *Example: A balanced Liver gently nourishes the Heart (Fire) without attacking the Spleen.*
    - **Damping:** The body naturally tries to return to its "Baseline" (its healthy state) over time. Fragility also influences the recovery speed; high fragility means the body finds it harder to recover from an imbalanced state.
- **The Output:** These numbers are converted into "Tags" (e.g., `[Slightly Irritable]`, `[Calm and Focused]`) that the agent uses to shape its next reply.

## Visualization Panel 📊

Body Emotion Sensor provides an intuitive visualization panel to help you monitor and debug the agent's body state in real-time.

<img src="./docs/panel.webp" alt="Visualization Panel" width="100%" />

To launch the panel:

```bash
bes panel --workspace /path/to/workspace --agent-id my-agent
```

## Roadmap 🛠️

- **SillyTavern Plugin**: Integration with the SillyTavern ecosystem to bring TCM-based emotion systems to local roleplay.
- **Affection/Relationship System**: Mapping the depth of relationships to long-term impacts on the Five Zang states.
- **Temporal Evolution**: Body states naturally evolve over time even between conversations (e.g., recovery of energy or calming of emotions).
- **Advanced TCM Logic**: Introducing deeper principles like "Tonify the Mother for Deficiency, Drain the Child for Excess" (虚则补其母，实则泄其子) to further refine energy flow and organ interactions.
- **Video Generation**: Exploring ways to drive short video or dynamic sticker generation directly from body-emotion states.

## Contributing 🤝

Pull requests are welcome.

If you want to improve Body Emotion Sensor, whether through new ideas, better integrations, docs, prompts, adapters, or workflow refinements, feel free to open an issue or submit a PR.

## License 📄

This project is released under the `MIT` license in the repository `LICENSE`.
