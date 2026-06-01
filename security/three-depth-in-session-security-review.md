---
title: "Three-Depth In-Session Security Review"
description: "Layer in-session security review at three depths — a deterministic per-edit pattern match, a fresh-context end-of-turn diff review, and an agentic commit-time review — so each layer earns its cost and false-positive budget."
tags:
  - security
  - code-review
  - tool-agnostic
aliases:
  - depth-ladder security review
  - layered in-session security review
  - per-edit end-of-turn commit security review
last_reviewed: 2026-05-30
---

# Three-Depth In-Session Security Review

> Stack three security checks at three depths — per-edit pattern, end-of-turn diff, commit-time agentic — so each layer's false-positive budget matches its frequency.

A mature in-session security-review surface is a depth ladder, not one heavy reviewer that runs everywhere. Each rung trades model cost against contextual reach: the cheapest fires most often; the most expensive fires rarely and clears with high confidence. Anthropic's [security-guidance plugin](https://code.claude.com/docs/en/security-guidance) ships this structure as a working reference; the architecture generalises to any harness with the matching hook events.

## The Three Rungs

| Layer | Fires on | Cost | What it catches |
|-------|----------|------|-----------------|
| **Per-edit pattern match** | `PostToolUse` on `Edit`, `Write`, `NotebookEdit` | Zero model cost — regex/substring | Known risky calls: `eval(`, `os.system`, `child_process.exec`, `pickle`, `dangerouslySetInnerHTML`, edits under `.github/workflows/` ([docs](https://code.claude.com/docs/en/security-guidance)) |
| **End-of-turn diff review** | `Stop` hook | Background model call per file-changing turn | Semantic issues a string match cannot see: authorization bypass, IDOR, injection, SSRF, weak crypto; up to 30 changed files per turn ([docs](https://code.claude.com/docs/en/security-guidance)) |
| **Commit-time agentic review** | `PostToolUse` on `Bash`, filtered to `git commit` / `git push` | Agentic SDK call that reads callers, sanitisers, related files | Cross-file vulnerabilities that need surrounding code to confirm; false positives dismissed before reporting ([docs](https://code.claude.com/docs/en/security-guidance)) |

Each layer is independently disablable (`ENABLE_PATTERN_RULES`, `ENABLE_STOP_REVIEW`, `ENABLE_COMMIT_REVIEW`) so an operator tunes the ladder without uninstalling it ([docs](https://code.claude.com/docs/en/security-guidance)).

## Why It Works

Cost and false-positive profile scale with depth together. A per-edit string match has near-zero cost but high false-positive risk, so it leans on flood control (covered below) to stay readable. End-of-turn review costs a model call but sees semantic context. Commit-time review costs the most but reads surrounding code, so patterns that look dangerous in isolation but are safe in this codebase are dismissed before reporting ([docs](https://code.claude.com/docs/en/security-guidance)).

The mechanism for the model-backed layers depends on **separating writer from grader**. Both reviews run as a separate Claude call with a fresh context and a security-focused prompt; the reviewer has no investment in the original approach. LLMs evaluating their own output exhibit a documented [self-enhancement bias](https://arxiv.org/abs/2306.05685) — fresh-context reviewers make different decisions than the writer would about its own code.

## Flood Control Is Part of the Pattern

Without per-layer caps the review surface becomes the noise source. Each rung carries its own limit ([docs](https://code.claude.com/docs/en/security-guidance)):

- **Per-edit** fires once per pattern per file per session.
- **End-of-turn** fires at most three times in a row before yielding to the user.
- **Commit-time** is capped at 20 reviews per rolling hour; findings that duplicate the end-of-turn review do not re-prompt the writer, so a clean commit produces no visible output.

The caps are layer-specific because the failure mode is layer-specific: per-edit floods on legitimate risky calls, end-of-turn loops when fixes introduce new findings, commit-time duplicates work already done at end-of-turn.

## Mapping to Other Harnesses

Any harness that exposes `PostToolUse(Edit|Write)`, `Stop`, and `PostToolUse(Bash)` can replicate the ladder. Three design decisions move with the architecture, not the tool:

- **Pick the cheapest tool for each layer.** Per-edit is a regex; end-of-turn a small/fast model; commit-time the most capable. `SECURITY_REVIEW_MODEL` and `SG_AGENTIC_MODEL` split for this exact reason ([docs](https://code.claude.com/docs/en/security-guidance)).
- **Layer flood controls separately.** Each layer's noise profile differs; one global rate limit produces either flooding or silence.
- **Keep findings advisory.** None of the layers blocks writes or commits in the reference implementation; pair with deterministic hooks for hard enforcement ([docs](https://code.claude.com/docs/en/security-guidance)).

The depth ladder is **in-session, advisory**. Adjacent patterns at other scopes: [Tunable Effort Levels](../code-review/tunable-review-effort.md) is the single-layer dial at PR time; [Tiered Code Review](../code-review/tiered-code-review.md) is risk routing across reviewers; [Always-On Agentic PR Security Review](always-on-pr-security-review.md) covers the temporal axis with a scheduled scanner. The ladder addresses what these miss: vulnerabilities that land before any PR-time gate fires.

## When This Backfires

The ladder adds engineering surface and three flood-control budgets. It is the wrong default in several conditions:

- **Solo developer, small repo, fast iteration.** Three layers compound friction; one well-tuned linter plus PR-time review is cheaper. The ladder pays off when in-session edits land before PR review can run.
- **Non-git workflows.** The end-of-turn and commit layers diff against git state and skip silently outside a repository ([docs](https://code.claude.com/docs/en/security-guidance)); the ladder collapses to its per-edit rung.
- **Cost-sensitive engagements.** The commit-time review is agentic and may take several model turns. At the default Opus-class model and 20 reviews/hour cap, a commit-heavy session spends non-trivial usage on review alone. Configure `SG_AGENTIC_MODEL` to a smaller model first.
- **Same-model writer and reviewer.** If both run the same model, [self-enhancement bias](https://arxiv.org/abs/2306.05685) reduces the fresh-context advantage. Mix model classes across writer and reviewer layers.
- **Legitimate use of risky patterns** (compilers, embedded scripting). The per-edit layer floods even with the once-per-pattern-per-file cap; custom `exclude_paths` becomes mandatory.

A single well-tuned end-of-turn reviewer with tool-calling and clustering is a viable alternative — GitHub Copilot's PR review runs that shape, [silent on 29% of reviews and actionable on 71% after clustering](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/). The ladder is not the only shape; it is the shape that pays back when edits accumulate inside a turn before any other gate fires.

## Key Takeaways

- The three rungs match three different cost and false-positive profiles — one reviewer cannot occupy all three positions.
- Flood control is per-layer; the failure mode at each rung differs.
- Separating writer from grader through a fresh model context is what makes the model-backed layers earn their cost.
- All layers stay advisory; pair with deterministic hooks for hard enforcement.
- Skip the ladder when a single reviewer already operates at adequate depth, outside git, or when usage cost dominates the review budget.

## Related

- [Always-On Agentic PR Security Review](always-on-pr-security-review.md) — the temporal-axis counterpart: PR-time plus scheduled scanner for resident risk
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — broader layered-defense framing the depth ladder fits inside
- [Inline Safety Harness with Cascade Verification (FinHarness)](inline-lifecycle-safety-harness.md) — per-tool-call cascade routing, the runtime-action analogue of the review-time depth ladder
- [Lifecycle-Integrated Security Architecture for Agent Harnesses](lifecycle-security-architecture.md) — defense placement across the agent execution lifecycle
- [Tunable Effort Levels for Code Review Agents](../code-review/tunable-review-effort.md) — the single-layer effort-dial alternative at PR time
