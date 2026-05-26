# AI-Augmented Code Review Pipelines

Workshop materials for the ISC2 Security Congress 2026 hands-on workshop on building production AI-augmented code review pipelines.

**Status:** Workshop preparation in progress. Final lab guide published after October 2026.

## What this is

A reference implementation and lab guide for security engineers building LLM-assisted code review into their CI pipelines. Built around self-hosted, on-premise LLM patterns (GPT-OSS 120B class models) rather than third-party API dependencies.

## What attendees will leave with

- A working reference pipeline they can fork into their own GitLab or GitHub setup
- Prompt patterns for code review that account for context window limits and tool-use constraints
- Evaluation harness for measuring review quality over time
- A defense pattern catalog for the prompt injection surface introduced by reading attacker-controlled code

## Structure (planned)

- `reference-pipeline/` — Working GitLab CI / GitHub Actions example
- `prompts/` — Prompt templates with documentation
- `eval-harness/` — Quality measurement tooling
- `defense-patterns/` — Prompt injection mitigations specific to code review context
- `slides/` — Workshop slides (post-delivery)
- `lab-guide/` — Step-by-step workshop instructions (post-delivery)

## Talk details

ISC2 Security Congress 2026, October. Workshop session details to be added.

## License

Apache 2.0
