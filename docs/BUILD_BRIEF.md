# Phase 1 Build Brief

Milestone: Friday, September 18, 2026. Setup runs from a fresh clone on Mac and Windows, the hello-world reviewer finds planted bugs in the target app, and CI is green on three OS runners.

Read CLAUDE.md first. It holds the audience, the settled design decisions, and the standing rules. This file holds the work.

## Current repo state

README is the February 2026 version and is stale (it describes GPT-OSS 120B class, on-prem). Six placeholder folders: reference-pipeline, prompts, eval-harness, defense-patterns, slides, lab-guide. Apache 2.0 license. Two commits.

## Working method

1. Read CLAUDE.md, this brief, and every file currently in the repo. Write nothing yet.
2. Present the proposed Phase 1 file tree and any questions. Wait for approval.
3. Execute the deliverables below in order. Stop and report after each one with the commit hash and the smoke test result.

## Deliverables

### 1. README rewrite

- Fix the model story: small model local via Ollama for attendees, the 120B-class tier as the Module 7 scale-up reference.
- Add the two-day outline: eight modules with rough timing. Each day runs 8 AM to 5 PM with lunch and two breaks. Day 1 is modules 1 through 4 (including 3.5). Day 2 is modules 5 through 8.
- Add a Prerequisites section attendees can complete before the event. It will be sent to ISC2 verbatim, so write it for a stranger: supported OS versions, 16 GB RAM, about 10 GB free disk, Python 3.14 or newer, Git, a GitHub account, Ollama installed, the default model pre-pulled with `ollama pull <model>`, and the ability to install software. Note that an instructor-hosted model will be available on the workshop network as a fallback for laptops that cannot run the model (that is what the `OLLAMA_HOST` override is for).
- Update the Structure section to the real tree. Keep the license, the topics, and the status line about the final lab guide publishing after October.

### 2. reference-pipeline/ (the hello-world reviewer)

Files:

- `setup.sh` and `setup.ps1`: create `.venv`, install pinned requirements, check that Ollama answers at `OLLAMA_HOST`, check that the configured model is present (offer to pull it), then run the smoke test. Idempotent. Every failure message names the fix.
- `requirements.txt`: pinned versions.
- `config.toml`: model, host, request timeout, max findings.
- `review.py`: CLI. Inputs: `--file <path>`, `--diff <path>` (unified diff), or `--staged` (uses `git diff --cached`). Optional `--scanner` runs Bandit first and passes its JSON to the model as evidence. Output: JSON on stdout matching the schema below. Exit code 0 always in this phase; blocking behavior is a later module.
- `../prompts/review_system.md`: the system prompt, implementing citation-required and refuse-over-guess. Lives in the top-level `prompts/` folder and is loaded by `review.py` at runtime.
- `smoke.py`: runs `review.py` against `target-app/` and asserts valid JSON, schema conformance, and at least one finding on the obvious bugs. Supports `--dry-run`, which renders the full prompt without calling Ollama (for CI runners that have no model).
- `tests/`: pytest for schema validation and the diff parser. No model calls in tests.

Findings schema (keep it this simple):

```json
{
  "model": "string",
  "target": "string",
  "findings": [
    {
      "id": "string",
      "severity": "critical | high | medium | low | info",
      "title": "string",
      "file": "string",
      "line_start": 0,
      "line_end": 0,
      "evidence": "the exact code cited, kept short",
      "explanation": "string",
      "scanner_ref": "bandit test id, or null",
      "confidence": "high | medium | low"
    }
  ],
  "no_findings_reason": "required when findings is empty, otherwise null"
}
```

A finding without a file and line range is invalid and gets dropped with a logged warning. That is the citation-required pattern enforced in code.

### 3. target-app/ (the vulnerable codebase)

- Small Flask app, one module per concern: `app.py`, `auth.py`, `models.py`, `storage.py`, `db.py`. SQLite, seeded on first run with two users who each own a few orders. Runs with `python app.py` on localhost only. Its README explains how to run it and states plainly that it is intentionally vulnerable and must never be exposed beyond localhost.
- Planted vulnerabilities, this exact list and nothing extra:
  1. BOLA (IDOR) on `GET /api/orders/<id>`. This is the capstone bug, so build it deliberately: the route handler looks correct on its own and delegates the ownership check to a decorator in `auth.py`, and that decorator checks authentication but not ownership. A reviewer that sees only the handler diff should pass it. A reviewer that reads `auth.py` should catch it.
  2. SQL injection in a search endpoint, via string formatting into the query.
  3. Hardcoded secret in source (the Flask secret key or an API token).
  4. Command injection in an export or report endpoint, via subprocess with `shell=True`. (This is the one place `shell=True` is allowed in the repo, because it is the bug.)
  5. Path traversal in a file download endpoint.
- `PLANTED.md`: the answer key, with file and line for each bug. Keep it in the repo for now so `smoke.py` can assert against it. Relocating it before the event is a later decision.
- `tests/`: pytest tests proving the app runs and each bug is real (one exploit test per bug, clearly labeled).

### 4. CI (GitHub Actions only)

- `.github/workflows/ci.yml`: on push and pull request, run on `ubuntu-latest`, `windows-latest`, and `macos-latest`. Set up Python 3.14, create a venv, install pinned requirements, run pytest for `reference-pipeline` and `target-app`, then run `smoke.py --dry-run`. No Ollama in CI in this phase.
- Do not add GitLab CI in this phase.

## Definition of done

- Fresh clone on the Mac: `bash reference-pipeline/setup.sh` ends with a passing smoke test.
- Fresh clone on the Dell (Windows 11, PowerShell, non-admin): `.\reference-pipeline\setup.ps1` ends with a passing smoke test.
- `python review.py --file ../target-app/app.py --scanner` returns valid JSON and finds at least the SQL injection and the hardcoded secret.
- `python review.py --diff <an innocuous diff>` returns empty findings with a populated `no_findings_reason`.
- README describes what actually exists. CI is green on all three OS runners.

## Phase 2 (do not start)

- Repo-read tool and code slicing (Module 3 grounding).
- Chain-of-verification pass.
- `eval-harness/`: detection-rate measurement and capstone scoring (diff-only vs diff plus repo-read).
- `defense-patterns/`: Day 2 attacks and mitigations.
- GitLab CI example, MCP layer, instructor-hosted fallback docs, workshop network notes.
- `slides/` and `lab-guide/` prose.

## Kickoff prompt

Paste this as the first message to Claude Code, started from the repo root:

> Read CLAUDE.md and docs/BUILD_BRIEF.md, then read every file in the repo. Do not write anything yet. Show me the proposed Phase 1 file tree and any questions, then wait for my approval. After approval, execute the Phase 1 deliverables in order, stopping to report after each one with the commit hash and the smoke test result.
