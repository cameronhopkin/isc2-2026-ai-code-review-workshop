# CLAUDE.md

Project: ISC2 Security Congress 2026 workshop, "From Zero to Security Bot: Building and Hardening an AI-Powered Code Review Pipeline." Two-day hands-on workshop, Oct 24-25, 2026, 8 AM to 5 PM each day. Attendees build a laptop-local LLM code review pipeline, wire it into CI, break it on Day 2, and harden it. Everything in this repo is workshop material an attendee will run on their own machine.

## Who the code is for

- Security engineers who are comfortable in a terminal and have never run a local model.
- Attendee laptops: mostly Windows 11 corporate machines, then macOS on Apple Silicon, some Linux. Baseline assumption: 16 GB RAM, no admin rights.
- Test machines on hand: MacBook Pro M1 16 GB (macOS), Dell XPS 15 32 GB (Windows 11), Kubuntu desktop (Linux).

## Design decisions (settled May 2026, do not reopen)

- Eight modules: (1) The Landscape, (2) Model Deployment, (3) Building the Security Bot, (3.5) Anti-Hallucination Patterns, (4) CI/CD Integration, (5) Day 2 Attacks, (6) Defenses, (7) Production Architecture, (8) Capstone. Day 1 is modules 1 through 4 (including 3.5). Day 2 is modules 5 through 8.
- The attendee path is a small open-weight coder model via Ollama, laptop-local. The 120B-class self-hosted tier appears only as the Module 7 scale-up reference architecture.
- Grounded retrieval: the bot gets a repo-read tool as a first-class input and fetches the slice of code it asks for. No whole-repo dumps.
- Three anti-hallucination patterns are taught and enforced in code, not just in prompts: citation-required (every finding cites file and line), chain-of-verification (the model checks its output against the provided context), refuse-over-guess (no findings is a valid, first-class answer).
- Capstone: the same vulnerable codebase reviewed by two bot configurations, diff-only vs diff plus repo-read, scored on planted BOLA bugs.
- No cloud, no API keys, no paid tiers. Docker is never a prerequisite.

## Standing rules

- Python 3.14 minimum. Always a venv (`python -m venv .venv`). Never system pip. Every setup path and every doc shows venv creation and activation for both bash and PowerShell.
- Cross-platform is a hard requirement: pathlib for paths, no `shell=True`, no bash-isms inside Python, line endings handled. Anything that works on one OS only is a bug.
- Minimal pinned dependencies: requests, bandit, flask, pytest. Ask before adding anything else.
- Scanner is Bandit (pip-installable, pure Python, runs on Windows). Semgrep is an optional add-on later; verify its native Windows status before it appears in any prerequisite.
- LLM access is Ollama's HTTP API called directly with requests. Base URL from `OLLAMA_HOST` (default `http://127.0.0.1:11434`). Model name from `config.toml`, overridable by `REVIEW_MODEL`. Default model `qwen2.5-coder:3b`; verify it pulls, note any clearly better 3-4B coder model in the commit message, and keep the default a one-line change. Config is TOML read with stdlib `tomllib`.
- Structured output: request JSON from the model, validate it in code anyway, drop anything that fails validation with a logged warning.
- No em dashes anywhere: docs, comments, strings, commit messages. Use commas, colons, or parentheses instead.
- Attendee voice in all docs: short sentences, every command shown for bash and PowerShell, every error message names the fix.
- Git: one commit per deliverable, descriptive messages, no force push, never modify LICENSE. Run the smoke test before any commit that touches code.
- Do not start Phase 2 work (listed in docs/BUILD_BRIEF.md) unless asked.
