# Contributing

Thank you for your interest in contributing to Body Emotion Sensor.

Body Emotion Sensor is an open-source Python project for giving AI agents a persistent body-emotion state based on the TCM Five Zang and Five Elements model. Contributions of many kinds are welcome, including code, documentation, examples, bug reports, UX improvements, prompt design, visualization improvements, and design discussions.

## Ways To Contribute

You can contribute by:

- opening an issue to report a bug or suggest an improvement
- submitting a pull request for a focused fix or feature
- improving documentation, examples, or onboarding material
- refining body-emotion mapping logic, prompt outputs, or state transitions
- improving the CLI workflow, storage format, or visualization panel
- proposing better integrations for agent frameworks and related tooling

## Before You Start

For small fixes and docs improvements, feel free to open a pull request directly.

For larger features, data-model changes, CLI redesigns, or behavior changes that affect prompt contracts or stored state, opening an issue first is recommended so the direction can be discussed before implementation.

## Development Setup

For local development:

```bash
pip install -e .
bes help
```

If you are working on the visualization panel, also test the Streamlit interface locally:

```bash
bes panel --workspace /path/to/workspace --agent-id my-agent
```

## Pull Request Guidelines

Please try to keep pull requests:

- focused on a single improvement or a clearly related set of changes
- easy to review, with minimal unrelated edits
- consistent with the existing project structure and naming
- documented when behavior, CLI usage, prompts, or stored data contracts change

When opening a pull request, include:

- a short summary of what changed
- why the change is helpful
- any important usage notes, compatibility notes, or follow-up ideas
- tests or manual verification steps when relevant

## Issue Guidelines

When opening an issue, it helps to include:

- what problem you are seeing
- what behavior you expected instead
- reproduction steps, sample input, or screenshots when available
- environment details such as Python version and platform when relevant
- any proposed direction if you already have one in mind

## Areas Especially Welcome

Contributions are especially welcome in these areas:

- body-emotion mapping quality and state transition design
- prompt payload clarity and output consistency
- CLI ergonomics and developer workflow
- visualization and history inspection
- documentation clarity and first-time onboarding
- test coverage, reliability, and packaging quality
- compatibility with more agent workflows and integration scenarios

## Community Expectations

Please be respectful, constructive, and collaborative in issues and pull requests.

Clear communication, reproducible reports, and focused changes are valued more than perfect first drafts.

## License

By contributing to this repository, you agree that your contributions will be licensed under the same `MIT` license as the project.
