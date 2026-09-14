---
title: "Agent Approval Authority in Code Review"
term: "Agent Approval Authority"
description: "Once an admin enables it, an AI reviewer's approval counts toward the required-approvals rule — scope which repositories, paths, and change classes it may clear before turning it on."
aliases:
  - AI reviewer approval authority
  - agent approving pull requests
  - reviewer agent merge authority
tags:
  - code-review
  - testing-verification
  - human-factors
  - copilot
last_reviewed: 2026-09-02
maturity: emerging
---

# Agent Approval Authority in Code Review

> Once an admin enables it, an AI reviewer's approval counts toward the required-approvals rule, so scope what it may clear first.

A commenting reviewer produces a signal a human reads; an approving reviewer discharges a merge precondition. GitHub moved Copilot code review across that line on 1 September 2026, and the setting stays off until an admin turns it on.

## What shipped

Every review now carries an approval assessment in its overview comment, and the assessment is advisory: "An approval assessment alone does not count toward merge requirements" ([GitHub Changelog, 2026-09-01](https://github.blog/changelog/2026-09-01-copilot-code-review-can-now-approve-pull-requests/)).

An admin can separately authorize a real approving review: "When enabled, Copilot can submit an approval that counts toward the repository's required-approvals rule" (same source). That is the behavior that puts the agent on the merge path. It ships "off by default", in public preview for the Pro, Pro+, Max, Business, and Enterprise plans (same source).

## Two conditions decide whether to enable it

Answer both before you touch the setting.

Is the required-approvals rule the only thing between the diff and `main`? Where status checks, a merge queue, and CI already gate the branch, the approval slot is one control among several. Where it is the whole gate, enabling agent approval removes the gate.

Did the approving agent read a change it did not write? An approval counts as a second read only when the approver is not the producer. The changelog names three configuration levels and, at repository level, a file-path restriction. Authorship is not among the dials it lists. So a coding agent can open a pull request, a review agent can approve it, and that approval counts toward the rule with no independent reader in the loop.

Where both answers run against you, keep a human in the required slot for that repository. If neither does, the agent approval costs little.

## What each dial bounds

| Level | What the admin sets | What it does not bound |
|---|---|---|
| Enterprise | Approvals off enterprise-wide, or organizations decide | Anything, once the decision is delegated |
| Organization | On org-wide, delegated to repository admins, on for named repositories, or off | Which changes inside an enabled repository |
| Repository | On or off, plus which file paths the agent may approve | Risk that is not path-shaped, and who authored the change |

All three rows come from the [changelog's configuration list](https://github.blog/changelog/2026-09-01-copilot-code-review-can-now-approve-pull-requests/).

One hole is already closed: "If new commits are pushed after Copilot approves, its approval is dismissed just like a human reviewer's" (same source). A later push cannot carry an approval the agent never saw.

## Why it works

Branch protection counts approvals. It does not ask whether anyone read the diff. Before this change a Copilot review produced comments, and only a human approval counted toward the required-approvals rule, so a second reader was invoked on every protected merge. After it, an approval from the same class of system that wrote the change counts toward it. That is why the placement has to be chosen rather than inherited.

The case for keeping a reader somewhere is reviewer composition, not tool quality. Across 3,109 pull requests, agent-only reviewed PRs merged at 45.20% against 68.37% for human-only, and 12 of 13 review agents averaged signal ratios below 60% ([arXiv:2604.03196v1](https://arxiv.org/abs/2604.03196v1)). Per-comment [reception data](agentic-review-comment-acceptance.md) points the same way. A framework proposal for agentic review keeps humans "at key decision points to preserve judgment, accountability, and team-level understanding" rather than at every stage ([arXiv:2605.17548v2](https://arxiv.org/abs/2605.17548v2)).

## When this backfires

Insisting on a human in the required slot is not free, and in four cases it buys nothing.

- No second human exists. On a solo-maintainer repository the rule blocks merges rather than adding review. Most AI-generated pull requests already receive no review at all, and those that do are largely reviewed by agents ([arXiv:2605.02273v1](https://arxiv.org/abs/2605.02273v1)).
- The human approval is already a signature rather than a read. Across 400 repeat reviewers and 11,429 reviews, within-reviewer approval rates rose from 30.1% to 36.8% while inline comment volume fell 22% ([arXiv:2606.22721v1](https://arxiv.org/abs/2606.22721v1)). [Reviewer habituation](reviewer-habituation-decay.md) covers the diagnosis.
- Risk in your codebase is not path-shaped. A one-line change to an allowlisted config file can outrank a large change in a denied directory, so a path allowlist trusted as a risk control mis-sorts.
- Review is the binding constraint. In that same population review latency grew 3.5 times ([arXiv:2606.22721v1](https://arxiv.org/abs/2606.22721v1)), so the required slot is mostly queue. A gate that is mostly queue gets routed around: self-approval, admin bypass, or the rule switched off entirely. [Author-to-reviewer role inversion](../human/author-to-reviewer-role-inversion.md) covers the staffing response.

The strongest published objection goes further. Monperrus argues that "the naive integration in which agents write code and humans remain the mandatory reviewers is a dead end because it neither provides meaningful assurance nor scales with AI-assisted throughput" ([arXiv:2606.13175v1](https://arxiv.org/abs/2606.13175v1)). If you accept that, do not leave the human slot nominally filled. Spend the gate budget on checks that do not habituate: tests, static analysis, and a merge queue.

## Key Takeaways

- The approval assessment and the approving review are separate features. Only the second counts toward required approvals, and only the second needs a gating decision.
- Enable it per repository, not org-wide, unless every repository in the org answers both conditions the same way.
- Treat an agent approval on an agent-authored PR as zero reads, not one. No configuration level checks authorship.
- Stale approvals are handled: a push after approval dismisses it. Do not build policy around a hole the vendor already closed.
- Audit on approving reviewer, not on merges. A repository where the agent is the sole approver on most merged PRs has moved its gate without anyone deciding to.

## Related

- [Tiered Code Review](tiered-code-review.md) — routes review depth by path criticality while humans stay the only approvers; this page covers what changes when they are not
- [Risk-Score Threshold Calibration for Auto-Approval](risk-score-threshold-calibration.md) — a learned diff-risk score deciding whether a human reviews at all, the bespoke counterpart to a vendor path allowlist
- [Agent-Assisted Code Review](agent-assisted-code-review.md) — the commenting posture this feature departs from
- [Agent-Resolved Review Threads](agent-resolved-review-threads.md) — the conversation-resolution rule clearing the same way, with no admin setting to decide first
- [Reviewer Habituation in Agent PR Review](reviewer-habituation-decay.md) — why the human approval slot decays into a signature over repeat exposure
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — the reviewer-composition evidence behind keeping a reader in the loop
