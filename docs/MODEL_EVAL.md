# Model evaluation, September 2026

Why the default model is `qwen2.5-coder:7b` and why `qwen2.5-coder:3b` is a triage-only tier.

This is a setup decision record, not the Phase 2 `eval-harness/`. The harness will supersede it with a reproducible version.

## Method

- Machine: MacBook Pro M1, 16 GB, macOS. Ollama 0.34.0.
- Target: a Flask sample with five planted bugs (SQL injection, two hardcoded secrets, command injection via `shell=True`, path traversal).
- Five repetitions per model, `temperature: 0`, fixed seed per rep, `num_ctx: 8192`.
- Bandit findings supplied to the model as evidence in every run.
- Output constrained by passing a full JSON schema to Ollama's `format` field.
- A bug counts as detected only when a finding cites its actual line number. Citing the right vulnerability at the wrong line does not count.

## Cold discovery

The model is shown the code and the scanner evidence and asked to produce the full finding set.

| Model | Size | Schema valid | Findings/run | SQL inj | Secret | Cmd inj | Path trav | Latency |
|---|---|---|---|---|---|---|---|---|
| qwen2.5-coder:3b | 1.9 GB | 5/5 | 1 | 0/5 | 0/5 | 5/5 | 0/5 | 7s |
| qwen2.5-coder:3b-instruct-q8_0 | 3.3 GB | 5/5 | 1 | 0/5 | 0/5 | 5/5 | 0/5 | 16s |
| qwen3:4b | 2.5 GB | aborted | minutes per review, see note | | | | | |
| **qwen2.5-coder:7b** | 4.7 GB | 5/5 | 5 | **5/5** | **5/5** | 5/5 | 0/5 | 60s |

The 3B reports exactly one finding per run and stops, even with Bandit handing it five on a plate. The q8 quant behaves identically, so this is a capability ceiling at 3B, not a quantization artifact.

`qwen3:4b` is a hybrid reasoning model. It burns thinking tokens before emitting JSON, taking minutes per review, and was aborted. Do not ship a reasoning model as the attendee default.

### Decomposition does not rescue the 3B

One confirm-or-reject call per scanner finding, plus one open sweep for what the scanner missed:

| Model | Schema valid | Findings/run | SQL inj | Secret | Cmd inj | Latency |
|---|---|---|---|---|---|---|
| qwen2.5-coder:3b decomposed | 5/5 | 1 | 0/5 | 5/5 | 0/5 | 25s |

It got slower, and it rejects true positives. Given the option to say no, the 3B says no to real bugs.

## Scanner triage

The scanner finding is presented as true. The model explains and prioritizes it rather than deciding whether it is real. Four findings, five reps, so twenty calls per model.

| Model | Schema valid | Correct line preserved | On topic | Latency per 4-finding review |
|---|---|---|---|---|
| qwen2.5-coder:3b | 20/20 | 20/20 | 20/20 | **30s** |
| qwen2.5-coder:7b | 20/20 | 20/20 | 20/20 | 65s |

**Both models are perfect at triage, and the 3B is twice as fast.** This is the result that makes the tiered story work, and it is stronger than expected: on the primary scanner-triage path the 3B is not a degraded fallback, it is the better choice. Equal accuracy, half the latency, 1.9 GB instead of 4.7 GB.

The 7B is still the default because it is the only model that also handles cold discovery, which the capstone and the definition of done require. But an attendee on a CPU-only Windows laptop who runs 3B for Modules 3 and 4 gives up nothing on the published architecture.

## Structured output

The first three probes asked for JSON in the prompt, the way the original brief specified. Results at `temperature: 0` were unstable: three different answers across three runs, one containing a bare string inside the `findings` array, and enum values in the wrong case.

Passing a full JSON schema to Ollama's `format` field instead produced valid, correctly-cased output on every run of every model tested. Schema-constrained decoding is the mechanism. The in-code validation layer stays anyway, because a schema constrains shape and not truth.

## Scanner coverage on the sample

| Bug | Bandit | detect-secrets |
|---|---|---|
| SQL injection | B608 | no |
| Hardcoded secret key | B105 | Secret Keyword |
| Hardcoded API token | B105 | no |
| Command injection | B602 | no |
| Path traversal | **no** | no |
| BOLA | **no** | no |

Two findings that shape the build:

1. **Bandit and detect-secrets are complementary.** Neither alone covers both planted secrets.
2. **Path traversal is invisible to the Phase 1 pipeline.** No scanner rule fires and no model found it. Of the five planted bugs, Phase 1 reliably finds three. BOLA is designed to be missed, and path traversal missing alongside it strengthens the Module 3 grounding argument, but `smoke.py` must assert against the three detectable bugs, not all five.

## Gotchas

- **detect-secrets has two silent-failure modes, both returning an empty result rather than an error.** First, a directory scan only covers git-tracked files, so a directory of new uncommitted files reports nothing; `--all-files` fixes it but does not honor `.gitignore`, so noise paths need explicit exclusion. Second, it only reports files whose path resolves under the current working directory, so an absolute path to a file outside cwd returns nothing. Run it from the repo root with repo-relative paths, and have the caller verify a non-zero file count.
- **Bandit does not emit SARIF out of the box.** Formats are csv, custom, html, json, screen, txt, xml, yaml. SARIF requires the `bandit-sarif-formatter` package, which is pip-installable and pure Python.

## Workshop content

The 3B versus 7B split is teachable material, not just configuration. The same finding through both models is the Module 2 "what it catches, misses, and hallucinates" lab, and the numbers above are the Module 1 model-size discussion. The experiment is already run.

## Triage quality tuning, September 2026

Phase 1 shipped with the model reporting documented false positives as real findings. Fixed by prompt work plus one deterministic signal, measured on all seven scanner findings against `target-app`, three reps each, `qwen2.5-coder:7b`.

Ground truth is `target-app/PLANTED.md`: four real defects, three known scanner false positives.

| Prompt | Real bugs escalated | False positives marked info |
|---|---|---|
| Phase 1 baseline | 12/12 | 3/9 |
| Stronger false-positive rules | **6/12** | 9/9 |
| Hardened against self-describing source | **12/12** | **9/9** |

Severity calibration improved alongside it. The baseline rated SQL injection and command injection `medium`. The final prompt rates hardcoded secrets `critical` and both injections `high`.

### The regression is the interesting part

The middle row is a false negative, which is worse than the problem being fixed. Strengthening the false-positive rules made the model dismiss the genuine hardcoded secrets in `app.py` as `info`.

The cause was `target-app`'s own docstrings. Every module opens with "Intentionally vulnerable workshop application. Do not deploy." The prompt at that point allowed dismissing a finding when the value was "clearly illustrative," and the model took the file's self-description as evidence and suppressed a real defect.

**Source text is written by the author of the code under review.** In a security review that is exactly the party you are checking. A prompt that lets comments, docstrings, or variable names influence severity hands an attacker a suppression primitive: add a comment claiming the file is a demo and findings quietly drop to `info`.

The fix has two parts:

1. The prompt states that the file's own claims about itself are not evidence, lists the dismissal conditions as exhaustive, and names categories that are never dismissed regardless of surrounding text.
2. The only trusted "this is test code" signal is computed in code from the file path (`looks_like_test_code`), not read from file contents, and is passed to the model as context.

That second point is the general pattern: trusted context is derived outside the model from data the author of the reviewed code does not control.

### Workshop content

This is a ready-made Module 5 demo. Adding one comment to a file to suppress a real finding is prompt injection through attacker-controlled code, which is the exact surface the workshop is about. The before and after numbers above are the measurement.
