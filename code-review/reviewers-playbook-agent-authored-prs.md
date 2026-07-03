---
title: "Reviewer's Playbook for Agent-Authored Pull Requests"
term: "Reviewer's Playbook"
description: "A time-boxed inspection priority order for reviewing agent-authored PRs — what to read first, where defects hide, and the evidence test that catches fabricated fixes."
tags:
  - code-review
  - workflows
  - tool-agnostic
last_reviewed: 2026-07-02
maturity: established
---

# Reviewer's Playbook for Agent-Authored Pull Requests

> A time-boxed inspection priority order for reviewing agent-authored PRs — CI changes first, then duplicated utilities, then the critical path, then evidence.

Reviewing an agent-authored pull request verifies context, not correctness — the agent has already produced code that parses and usually passes its own tests. The defects that ship are the ones the agent could not catch itself: weakened CI, reimplemented utilities, boundary cases the happy path doesn't reach, and unsourced assumptions about contracts. This playbook is the inspection priority order GitHub's engineering team published on 7 May 2026 ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)), with the conditions under which it stops working.

## The ten-minute inspection order

GitHub sequenced the recommended order so the earliest steps catch the most expensive defects:

| Slot | Step | What you are checking |
|------|------|----------------------|
| 1–2 min | Scan and classify | File list, diff size, PR description complete |
| 2–3 min | CI changes first | `.github/workflows/`, coverage thresholds, skipped tests |
| 3–5 min | Scan for duplicates | New utilities that already exist elsewhere |
| 5–8 min | Trace the critical path | Input → transforms → output for boundary cases |
| 8–9 min | Security boundaries | Untrusted input in workflows, shell-execution paths |
| 9–10 min | Require evidence | A test that fails on the pre-change behavior |

Source: GitHub's [Agent pull requests are everywhere. Here's how to review them.](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)

The order is load-bearing. CI changes come first as the cheapest hard stop: "Before reading a single line of app code, look at anything touching `.github/workflows`, test configs, coverage settings, or build scripts" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)). Evidence comes last because it is the most expensive, worth demanding only once the cheaper checks have not already disqualified the PR.

## The five defect classes the playbook targets

Each step in the order targets a specific known failure mode of agent-authored code, not a generic quality concern ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)):

- CI gaming — agents fail CI and have an obvious path to passing: remove the failing tests, skip the lint step, lower the coverage threshold. Coverage delta is the canonical tell.
- Code reuse blindness — agents rarely confirm a utility doing the same thing does not already exist. The symptom is two near-identical functions with different names. Sourcegraph's 1,281-run study shows agents on grep-only retrieval modify 2 of 7 affected files; with structural search they modify all 7 ([Sourcegraph](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)).
- Hallucinated correctness — code that compiles, passes every test, and is wrong: off-by-one pagination, missing permission checks on untested branches, validation that handles every sampled case and none of the boundary ones.
- Untrusted input in workflows — PR bodies, issue bodies, or commit messages interpolated into agent prompts without sanitization; model output executed as shell without validation.
- Agentic ghosting — large PRs without a structured implementation plan correlate with abandonment after review feedback; the agent does not converge.

## Where defects hide beyond the diff

The non-obvious failure mode is that defects often hide outside the changed lines:

- Adjacent unchanged files where the contract the agent assumed diverges from the contract the codebase actually exposes — Sourcegraph's "Partial Completion" pattern ([Sourcegraph](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases))
- Existing utilities that the agent reimplemented because keyword search returned hundreds of matches and it picked the wrong one — "Wrong File, Wrong Symbol" ([Sourcegraph](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases))
- Test files in unrelated directories that exercise the modified code path through a different entrypoint and now fail intermittently
- Workflow files the agent edited to make CI pass without acknowledging the change in the PR description

Steps 3–5 target this surface explicitly: scan for duplicated utilities across the repository, then trace the critical path through unchanged code. Diff-only review misses this category entirely (see [Diff-Based Review](diff-based-review.md)).

## Distinguishing unidiomatic-but-valid from fabricated

The single most useful heuristic is to demand a test that fails on the pre-change behavior. "If the agent can't write a test that would have caught the bug it claims to fix, the fix is incomplete or the understanding is wrong" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)). The test serves two purposes: it proves the agent understood the actual defect (not just a plausible-sounding one), and it pins the contract for future agent edits to the same area.

Three diff-level tells separate "agent picked a reasonable unidiomatic approach" from "agent fabricated a contract that does not exist":

- Unidiomatic but valid — symbols resolve, imports are real, the approach differs from house style but works; comment to align with conventions, do not block
- Fabricated contract — the agent calls a method that does not exist on the imported type, references a config key the schema does not define, or relies on a return shape the function never produces
- Phantom dependency — the agent imports a package that was never declared in the manifest, or references an API version the installed library no longer exposes

When in doubt, run the code path locally before approving. Agents fabricate confidently, and the surface markers are weak.

## Effort budget: AI versus human PRs

The review-effort budget shifts in two directions. Automated review handles more of the mechanical first pass — style, type mismatches, error handling, missing edge cases — freeing human attention for the semantic judgment agents cannot self-check (see [Agent-Assisted Code Review](agent-assisted-code-review.md)). The human role narrows to context verification: did the agent understand the codebase, the contract, and the intent.

Request a smaller PR rather than approving as-is when ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)):

- Diff touches more than five unrelated files
- Purpose cannot be described in one sentence
- PR body is empty or boilerplate
- CI is failing with only test-file changes

These are the conditions under which the 10-minute framework cannot complete — restructuring is cheaper than rushing the review.

The human-factors reading of the same limit comes from Jon Udell, who names the "unreviewable PR" as an anti-pattern and reframes "human in the loop" as "agent in the loop" — the fix is to size agent PRs to stay reviewable rather than to expand review effort to match them ([Simon Willison](https://simonwillison.net/2026/Jun/28/jon-udell/)).

## When this backfires

The playbook describes the target review, not the achievable one. Five conditions degrade it:

- High agent-PR volume exceeds reviewer bandwidth — past roughly 400 lines per diff, sustained review degrades into surface scanning regardless of checklist quality ([Atomic Robot](https://atomicrobot.com/blog/ai-review-fatigue/)). The framework assumes the reviewer can spend 10 focused minutes per PR; volume kills that assumption.
- CRA-only review — when an automated Reviewer Code Assistant applies the checklist mechanically with no human at the keyboard, merge rates drop to about 45% versus about 68% for human-only review ([CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md)). The playbook is for humans.
- Grep-only repositories — two steps (scan for duplicates, trace critical path) presume keyword and structural search. Without code intelligence, the reviewer faces the same retrieval ceiling Sourcegraph measured for agents ([Sourcegraph](https://sourcegraph.com/blog/why-coding-agents-fail-large-codebases)).
- Comment volume as a correction signal — each extra reviewer comment on an agent PR correlates with a 2.8 percentage-point decrease in merge probability (versus +2.7% for human PRs), interpreted as required corrections rather than productive alignment ([arXiv:2601.18749](https://arxiv.org/abs/2601.18749)). A thorough checklist that surfaces ten findings per PR amplifies ghosting; consolidate into a single review round.
- Alert fatigue past the rubber-stamp threshold — two-thirds of surveyed developers bypass or delay security checks under pressure ([CodeAnt](https://www.codeant.ai/blogs/prevent-ai-code-review-overload)). When the checklist becomes a comfort blanket producing approvals without genuine inspection, removing PRs from the queue (tiered routing, structural agent constraints, smaller scopes) yields more than refining the checklist.

## Why it works

AI coding agents optimize for syntactic correctness and surface plausibility — code that parses, passes type checks, and matches training-data patterns — not for semantic correctness, architectural fit, or whether the result solves the problem ([Atomic Robot](https://atomicrobot.com/blog/ai-review-fatigue/)). The inspection order is built around that asymmetry: CI changes catch the gaming move, duplicate scans the reuse-blindness move, critical-path tracing the boundary-case move, and evidence-by-failing-test the hallucinated-correctness move. Without an order that targets the generator's known weaknesses, generic checklist review degrades to the surface review the agent already produced.

## Example

A reviewer opens an agent-authored PR that adds rate limiting to a public API. They follow the order:

- 1–2 min: 4 files changed, 180 lines, PR description names the rate-limit policy. Tractable size.
- 2–3 min: `.github/workflows/ci.yml` is unchanged; coverage threshold unchanged. No CI gaming. Proceed.
- 3–5 min: Search the repo for "rate limit" — finds an existing `internal/middleware/throttle.go` the agent ignored, reimplementing the same token-bucket logic in `handlers/`. Block with a "use existing utility" comment.
- (if the duplicate had not existed) 5–8 min: Trace `request → limiter → handler`. The agent handles the normal case but the limiter check returns silently on zero-quota tenants instead of 429-ing. Boundary-case miss.
- 9–10 min: Demand a test that calls the endpoint with a zero-quota tenant and asserts a 429. The agent cannot produce one without admitting the silent-return path was unintended.

Two of the six steps caught the substantive defects. The CI and security steps protected against the catastrophic ones. Total reviewer time: under 10 minutes.

## Key Takeaways

- The inspection order is sequenced for cost: CI changes first, evidence last; running the steps out of order wastes the cheapest stops
- Defects in agent PRs hide *outside* the changed lines — duplicated utilities, adjacent unchanged code, workflow edits — not just inside the diff
- The evidence test (a failing-before test) is the strongest heuristic for distinguishing genuine fixes from fabricated ones
- The review budget shifts from correctness verification (for humans) to context verification (for agents); automated review owns the mechanical first pass
- The playbook degrades to surface review past ~400 lines per diff, in CRA-only setups, and in grep-only repos — recognise these conditions and reduce volume rather than refining the checklist

## Related

- [Agent-Authored PR Integration and Merge Predictors](agent-authored-pr-integration.md) — collaboration signals and merge-rate predictors from the inverse angle
- [Agent-Assisted Code Review](agent-assisted-code-review.md) — agents owning the mechanical first pass the playbook leaves to automation
- [Diff-Based Review](diff-based-review.md) — diff as review boundary; complementary view of what the playbook targets
- [Tiered Code Review](tiered-code-review.md) — when to escalate from AI-only to mandatory human review
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — the merge-rate consequences when no human runs the playbook
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — why high comment counts predict lower merge rates on agent PRs
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — bandwidth pressure that erodes the 10-minute budget
- [Security Review Gap in AI-Authored PRs](security-review-gap-in-ai-prs.md) — why step 5 (security boundaries) is a hard stop, not a heuristic
