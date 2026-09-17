# CLAUDE.md

Project: ISC2 Security Congress 2026 workshop, "From Zero to Security Bot: Building and Hardening an AI-Powered Code Review Pipeline." Two-day hands-on workshop, Oct 24-25, 2026, 8 AM to 5 PM each day. Attendees build a laptop-local LLM code review pipeline, wire it into CI, break it on Day 2, and harden it. Everything in this repo is workshop material an attendee will run on their own machine.

## The submission is the contract

`docs/PROPOSAL_AS_SUBMITTED.md` records what ISC2 has published and what Bradley signed off on in May 2026. Check work against it. Anything in this repo that contradicts a published takeaway, module, or deliverable is drift, and drift gets fixed here, not in the submission. If a change genuinely needs the submission to move, say so and name what Bradley has to be told.

Audience level as published: Mid, 4 to 9 years. Track: Engineering/Architecture.

## Who the code is for

- Security engineers who are comfortable in a terminal and have never run a local model.
- Attendee laptops: mostly Windows 11 corporate machines, then macOS on Apple Silicon, some Linux. Baseline assumption: 16 GB RAM, no admin rights.
- Test machines on hand: MacBook Pro M1 16 GB (macOS), Dell XPS 15 32 GB (Windows 11), Kubuntu desktop (Linux).

## Design decisions

Settled May 2026. Revised September 2026 only where measurement contradicted them. A decision here is not reopened on opinion. It is reopened when a test says it is wrong, and the test goes in the commit message.

- Eight modules: (1) The Landscape, (2) Model Deployment, (3) Building the Security Bot, (3.5) Anti-Hallucination Patterns, (4) CI/CD Integration, (5) Day 2 Attacks, (6) Defenses, (7) Production Architecture, (8) Capstone. Day 1 is modules 1 through 4 (including 3.5). Day 2 is modules 5 through 8.
- The attendee path is an open-weight coder model via Ollama, laptop-local. The 120B-class self-hosted tier appears only as the Module 7 scale-up reference architecture.
- **Scanner output is the primary input to the bot.** The published takeaway promises a bot that consumes existing SAST and secret-detection output and turns it into an actionable review comment. Scanner findings in, triaged and explained findings out. Freeform review of raw code is the secondary path, not the headline.
- The input contract is SARIF. Bandit emits it via `bandit-sarif-formatter`, and so do Semgrep, CodeQL, and gitleaks, which is what makes the bot portable to whatever attendees already run at work.
- Grounded retrieval: the bot gets a repo-read tool as a first-class input and fetches the slice of code it asks for. No whole-repo dumps. This is where the model earns its keep, on the BOLA that no scanner catches.
- Three anti-hallucination patterns are taught and enforced in code, not just in prompts: citation-required (every finding cites file and line), chain-of-verification (the model checks its output against the provided context), refuse-over-guess (no findings is a valid, first-class answer).
- Capstone: the same vulnerable codebase reviewed by two bot configurations, diff-only vs diff plus repo-read, scored on planted BOLA bugs.
- No cloud, no API keys, no paid tiers. Docker is never a prerequisite. Note that Docker Desktop was in the prerequisites as submitted, and dropping it makes setup easier rather than breaking a promise. Confirm what ISC2 actually published and tell Bradley if the listing needs the edit.

## Model tiers (measured September 2026, M1 16 GB)

Measured on a Flask sample with five planted bugs, five reps, temperature 0, JSON-schema-constrained decoding. Numbers live in `docs/MODEL_EVAL.md`.

- **Default is `qwen2.5-coder:7b`.** It is the only model tested that meets the definition of done. Cold discovery with scanner evidence supplied: SQL injection 5/5, hardcoded secret 5/5, command injection 5/5. About 60 seconds per full review on the M1.
- **`qwen2.5-coder:3b` is the triage tier, and on the triage path it is not a downgrade.** It is 100 percent reliable at explaining and prioritizing a scanner finding (20/20 calls, correct line preserved every time), matching the 7B exactly while running twice as fast, 30 seconds against 65 for the same four-finding review. Because scanner output is the primary input, a 3B attendee gives up nothing in Modules 3 and 4. It cannot discover vulnerabilities cold: 0/5 on both the SQL injection and the hardcoded secret in every configuration tested, including the q8 quant and a decomposed one-call-per-finding architecture. It is not viable for the capstone.
- **Do not use `qwen3:4b` or any reasoning model.** Thinking tokens make a single review take minutes and fight the schema constraint.
- The 3B versus 7B split is content, not just configuration. The same finding through both models is the Module 2 "what it catches, misses, and hallucinates" lab and the Module 1 model-size discussion.

Hardware honesty for the prerequisites, which go to ISC2 verbatim: 16 GB RAM minimum, no 8 GB machines, GPU or Apple Silicon recommended, model pre-pulled before travel. A CPU-only Windows laptop produces a few tokens per second, so state plainly that a review takes a minute or two there.

Open item: the Dell's 3050 Ti has 4 GB of VRAM and will not hold a 7B fully. As the room fallback server it serves 3B well and 7B poorly. Either accept 3B as the fallback tier or find a bigger-VRAM box before October.

## Standing rules

- Python 3.14 minimum. Always a venv (`python -m venv .venv`). Never system pip. Every setup path and every doc shows venv creation and activation for both bash and PowerShell.
- Cross-platform is a hard requirement: pathlib for paths, no `shell=True`, no bash-isms inside Python, line endings handled. Anything that works on one OS only is a bug.
- Minimal pinned dependencies: requests, bandit, bandit-sarif-formatter, detect-secrets, flask, pytest. Ask before adding anything else.
- Scanners are Bandit for SAST and detect-secrets for secret detection. Both are pip-installable, pure Python, and run on Windows. They are complementary: Bandit caught both planted secrets via B105, detect-secrets caught one of them plus classes Bandit has no rule for. Semgrep is an optional add-on later; verify its native Windows status before it appears in any prerequisite.
- **Call detect-secrets with repo-relative paths, from the repo root.** Given an absolute path it silently returns zero results. This is a real trap and every code path and doc must avoid it.
- LLM access is Ollama's HTTP API called directly with requests. Base URL from `OLLAMA_HOST` (default `http://127.0.0.1:11434`). Model name from `config.toml`, overridable by `REVIEW_MODEL`. Changing the default stays a one-line change.
- Structured output: pass a full JSON schema to Ollama's `format` field, not the string `"json"`. Schema-constrained decoding produced valid output on every run of every model tested, where asking for JSON in the prompt produced malformed arrays and wrong enum casing. Validate in code anyway, and drop anything that fails validation with a logged warning.
- No em dashes anywhere: docs, comments, strings, commit messages. Use commas, colons, or parentheses instead.
- Attendee voice in all docs: short sentences, every command shown for bash and PowerShell, every error message names the fix.
- Git: one commit per deliverable, descriptive messages, no force push, never modify LICENSE. Run the smoke test before any commit that touches code.

## Phase order

Phase 1 is `docs/BUILD_BRIEF.md`. Do not start Phase 2 work unless asked.

Promised in the submission and therefore Phase 2 work, not optional extras:

- GitLab CI template alongside the GitHub Actions one. Both CI systems were promised, on free tier, with templates provided.
- Posting the review back as a comment on the PR or MR. The Module 3 lab as submitted ends with a comment on the PR, not JSON on stdout.
- Practice repositories with planted bugs that attendees push to their own GitHub or GitLab account, so they see findings land in the PR or MR interface rather than only in a terminal.
- A hardening checklist deliverable.
- A TCO model for self-hosted versus commercial, which is the third published takeaway.
