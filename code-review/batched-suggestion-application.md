---
title: "Batched Suggestion Application: Bulk-Apply Agent Fixes on PRs"
term: "Batched Suggestion Application"
description: "Cluster mechanical agent suggestions and apply them as a single commit, with category-bounded batches and audit-trail discipline that prevent the workflow from becoming a rubber stamp."
tags:
  - code-review
  - workflows
  - tool-agnostic
aliases:
  - bulk apply agent suggestions
  - batched remediation on pull requests
  - fix all batch action
last_reviewed: 2026-06-13
maturity: established
---

# Batched Suggestion Application

> Cluster each mechanical agent suggestion by rule, severity, and file scope, then apply the batch as one reviewed commit with a per-finding audit manifest.

## The primitive

A reviewer with thirty open agent suggestions on a PR has two options. Walk each one — open, read, accept or dismiss, repeat — and pay the context-switching cost thirty times. Or cluster the suggestions, evaluate the rule once per batch, and apply each batch in a single commit.

GitHub's [code-scanning batch apply](https://github.blog/changelog/2026-04-07-code-scanning-batch-apply-security-alert-suggestions-on-pull-requests) (April 2026, GA) ships this primitive for security alerts: reviewers add alert fixes to a batch in the **Files changed** tab and apply them in one commit. GitHub frames the CI side directly — "batching changes into a single commit means you'll run one scan instead of a separate one for each alert." Cursor's [Bugbot](https://cursor.com/changelog) ships a bulk-apply workflow for actionable review suggestions, applying all Bugbot findings in a single pass.

## Why it works

Reviewer attention has a fixed per-decision cost dominated by context-switching: open the file, read the surrounding code, simulate the change, decide. When N suggestions share a rule and fix template, the cost spreads out — the reviewer evaluates the rule once and the per-instance check collapses to "does this fix match the template?" The mechanism breaks when batch members are heterogeneous: the per-rule cost no longer spreads out but the commit still applies in bulk — the worst of both modes.

## Cluster boundaries are the whole game

A bulk-apply button is not the pattern. The cluster-construction rules are. Without them, batching turns a careful reviewer into a rubber stamp. Vendor implementations encode boundary discipline:

- Dependabot grouped security updates consolidate fixes [per ecosystem, never across ecosystems](https://github.blog/changelog/2024-08-19-dependabot-grouped-security-updates-public-beta/) — pip and npm stay in separate PRs.
- Dependabot grouped version updates require [pattern-matching with `exclude-patterns`](https://github.blog/changelog/2023-06-30-grouped-version-updates-for-dependabot-public-beta/) — explicit boundary declarations rather than "everything in one batch".

Apply the same discipline at the PR surface. Cluster on `(rule × severity × file scope)`:

- One rule per batch. A SQL-injection batch and a CSRF batch are separate. Understanding one fix template does not transfer to the other.
- One severity tier per batch. High-severity findings get individual review; medium and low can batch.
- Bounded file scope. Ten files in one module is reviewable; ten files across six modules has lost the locality that made the cost spread.
- Cap batch size. Beyond ~10 fixes, the diff stops fitting working memory. SmartBear/Cisco's code-review study (cited in [diff-based review](diff-based-review.md)) found defect detection peaks at 200–400 lines and degrades sharply beyond.

## Failure modes

Rubber-stamp risk. [Empirical data on 278,790 AI-reviewed PRs](https://arxiv.org/abs/2603.15911) shows AI suggestions adopted at 16.6% versus 56.5% for humans, with "over half of unadopted suggestions from AI agents are either incorrect or addressed through alternative fixes." A meaningful fraction should not be applied at all. Batch-apply makes it cheaper to act on the mechanical majority — and cheaper to apply the wrong ones if boundaries are loose.

Audit-trail collapse. One commit applying 30 fixes loses the per-finding decision trail compliance reviewers need. Fix this by structuring the commit message as a per-finding manifest with alert IDs.

Cross-cutting fixes that look mechanical. Suggestions that change a shared sanitizer, schema field, or interface look trivial line-by-line but change global behavior when summed. [Diff-only review](diff-based-review.md) already has this blind spot; batching amplifies it. Exclude shared utilities and interface boundaries from auto-batch eligibility.

Uncalibrated suggestion source. A new bot or rule pack has no false-positive history. Batching before the source has earned a track record imports an unknown error rate as a per-PR commit cost.

## Guardrails

- Require a diff preview before commit. The batch UI surfaces the full consolidated diff, not just a count.
- Set per-category caps. Security: 5; lint autofix: 20; formatter: unbounded. Refuse to construct above the cap.
- Re-run CI on the batched commit, enforced by branch protection. GitHub's "one scan instead of N" only works if that one scan is mandatory.
- Attribute each finding in the commit message. Manifest format with alert ID, file, and line range.
- Exclude architectural seams (auth, schema, public APIs) from batch apply at the repo policy level.

## When this backfires

- High-stakes monorepos where one bad fix costs more than 50 good ones save.
- Audit-sensitive paths that need per-finding sign-off.
- Heterogeneous suggestion sources where one reviewer pass cannot calibrate to a shared rule.
- Architecturally cross-cutting fixes where the sum of mechanical changes is not mechanical.

## Example

A reviewer faces a PR with 12 open code-scanning alerts: 8 instances of `js/missing-rate-limiting`, 3 instances of `js/sql-injection`, and 1 instance of `js/path-injection` flagged High.

Per-finding workflow: 12 individual review-and-apply cycles, ~3 minutes each, ~36 minutes total.

Batched workflow with cluster discipline:

1. Batch A (rate limiting, 8 fixes, all medium severity, all in `routes/`). The reviewer reads the suggested middleware addition once, scans the 8 instances to confirm the template match, and applies as one commit. ~6 minutes.
2. Batch B (SQL injection, 3 fixes, all medium severity, all parameterized-query rewrites in `db/`). Same pattern, ~4 minutes.
3. Individual review for the High-severity path-injection finding. It stays on the per-finding path because the severity threshold excludes it from auto-batch. ~3 minutes.

Total: ~13 minutes. Audit trail preserved via two commit-message manifests:

```
fix(security): batch resolve js/missing-rate-limiting [8 alerts]

Applies CodeQL suggestions for:
- routes/users.ts:42 (alert #2104)
- routes/users.ts:78 (alert #2105)
- routes/admin.ts:31 (alert #2106)
[...]
Resolves: 2104, 2105, 2106, 2107, 2108, 2109, 2110, 2111
```

CI re-runs once on the batched commit, confirming no new alerts introduced. The High-severity finding gets the per-finding commit it deserves.

## Key Takeaways

- The pattern is the cluster boundary, not the bulk-apply button — `(rule × severity × file scope)` with capped batch size keeps amortization safe
- Vendor implementations encode boundary discipline: Dependabot refuses to group across ecosystems; GitHub's code-scanning batch operates within the **Files changed** tab; Cursor's Fix All applies only to actionable Bugbot suggestions
- The 16.6% AI suggestion adoption rate means a meaningful fraction of suggestions should not be applied — batching makes it cheaper to apply the wrong ones if boundaries are loose
- Mandatory CI re-run on the batched commit and per-finding commit-message manifests preserve the verification and audit properties that per-finding workflow gave for free
- Encode the exclusions as repo policy, not reviewer discipline. A batch boundary that depends on someone remembering it fails on exactly the busy PR where batching is most tempting

## Related

- [Diff-Based Review](diff-based-review.md) — review fatigue scales with output size; batching is the throughput-side counterpart
- [Learned Review Rules](learned-review-rules.md) — Cursor Bugbot Fix All operates on top of learned-rule extraction
- [Agentic Code Review Architecture](agentic-code-review-architecture.md) — agentic review produces the suggestion volume that makes batching necessary
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — high suggestion volume without signal discipline is what batching tries to make survivable
- [Tiered Code Review](tiered-code-review.md) — severity-based routing is a precondition for safe batch boundaries
- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — reviewer engagement is the strongest predictor of merge; batching shifts the unit of engagement
- [Human-AI Review Synergy](human-ai-review-synergy.md) — empirical adoption-rate data that bounds the rubber-stamp risk
- [Inline Suggestion Attachment](inline-suggestion-attachment.md) — the upstream decision: which findings should carry an applicable patch at all
