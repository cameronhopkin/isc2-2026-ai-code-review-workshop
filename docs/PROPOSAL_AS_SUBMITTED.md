# Proposal as submitted

## Provenance, read this first

This file is a **reconstruction from session notes**, not the verbatim text submitted to ISC2. It was assembled in September 2026 from a summary of the accepted proposal and the May 2026 correspondence with Bradley. It is accurate in substance and should be treated as the contract, but it is not a quotation.

Replace this file with the actual submitted text when it is to hand, and delete this section when you do.

## Locked with Bradley, May 2026

- Title, two-day format.
- Audience level: Mid, 4 to 9 years.
- Track: Engineering/Architecture.

## Published takeaways

1. Deploy an open-weight model via Ollama, build a review bot that consumes existing SAST and secret-detection output, and integrate it into GitHub Actions or GitLab CI on the free tier, with provided templates.
2. Red-team the bot and harden it.
3. Build a TCO model for self-hosted versus commercial.

## Module plan as submitted

**Day 1**

1. Landscape.
2. Model Deployment. Lab: a model running on your own machine.
3. Building the Bot. Lab: reads scan results, summarizes via LLM, posts comments to the PR or MR.
4. CI/CD Integration. Lab: bot runs in a live pipeline on a commit with planted vulnerabilities, non-blocking.

**Day 2**

5. Attacking Your Own Bot. Prompt injection via comments and commit messages, false-negative manipulation, exfiltration, resource exhaustion. Lab: attendees attack each other's bots.
6. Enterprise Hardening. Input isolation, output validation for hallucinated findings, secret management, network segmentation, audit logging, rate limiting.
7. Production Architecture. Scaling, model update strategy, monitoring, cost modeling.
8. Capstone. Hardened bot against a realistic vulnerable codebase, group comparison of outputs.

## Deliverables promised

- Working code.
- Deployment templates for both CI systems.
- A hardening checklist.

## Prerequisites as submitted

**Unverified, and nothing here is published.** This list comes from the source summary, not from any ISC2 page. See reconciliation item 2.

- 16 GB RAM minimum, 32 GB recommended.
- Docker Desktop. (Unconfirmed, and contradicted by Cameron's recollection.)
- GitHub or GitLab free tier account.
- Python 3.11 or newer.

## Model story as submitted

February: "smaller GPT-OSS variant." May: Bradley was told the workshop was moving to a 1B to 8B model with GPT-OSS as the scale-up reference, and he received the edited takeaway wording.

The September 2026 decision to default to `qwen2.5-coder:7b` sits inside the 1B to 8B range that Bradley signed off on. No coordination needed.

## Reconciliation items

Open gaps between this document and the current repo. Each needs a decision.

1. ~~**Python version.**~~ **Resolved September 2026.** The published prerequisite is 3.11 or newer, and the repo now matches it. Attendee docs say 3.11 or newer. CI tests the 3.11 floor on all three operating systems and also tests 3.14. Dev machines run 3.14. No coordination with Bradley needed.
2. **Docker Desktop, and prerequisites generally.** **Checked September 2026: ISC2 publishes no prerequisites for this workshop at all.** The public listing is one descriptive paragraph. There is no technical requirements section, no Docker, no Python version, no hardware floor. Verified against the ISC2 pre-conference workshops page and the Cvent registration page; the EventScribe agenda returns 403 and was not readable.

   The claim above that Docker Desktop was a submitted prerequisite originates from this document's source summary and could not be confirmed anywhere. Cameron does not recall submitting it. **Treat it as unproven and do not act on it.** Nothing needs to be corrected with ISC2, because nothing was published.

   The consequence matters more than the correction: the Prerequisites section of `README.md` is not reconciling against a published list, it **is** the list. It is the only prerequisites document in existence, so it is what attendees get told. Nothing in the workshop needs a container runtime. If a later module ever does, it will use Podman, which is rootless, has no daemon, and raises no licensing question on a work machine.

3. ~~**Module 3.5.**~~ **Resolved September 2026.** Folded into Module 3 as its second part, "making the bot trustworthy". Eight whole-numbered modules, four per day, matching the submitted plan. Citation-required and refuse-over-guess are enforced in `review.py`, which is what Module 3 builds, so they belong in that session rather than in one of their own.
4. **Posting to the PR or MR.** The submitted Module 3 lab ends with a comment posted to the PR or MR. Phase 1 ends with JSON on stdout. This is a promised behavior, so it is Phase 2 work rather than an optional extra.
5. **GitLab CI.** Templates for both CI systems were promised. Phase 1 is GitHub Actions only, so the GitLab template is required Phase 2 work.
6. **TCO model.** The third published takeaway has no home in the current build plan. It belongs in Module 7.
