---
title: "Agent-Authored PR Integration: Collaboration Signals That Determine Merge Success"
description: "Reviewer engagement — not code correctness or iteration count — is the strongest predictor of whether an agent-authored PR gets merged."
term: "Agent-Authored PR Integration"
tags:
  - human-factors
  - agent-design
  - workflows
  - tool-agnostic
  - code-review
last_reviewed: 2026-06-13
maturity: established
---

# Agent-Authored PR Integration: Collaboration Signals That Determine Merge Success

> Reviewer engagement, not code correctness, is the strongest predictor of whether an agent-authored PR gets merged; force pushes are the strongest negative predictor.

## The finding

[arXiv:2602.19441](https://arxiv.org/abs/2602.19441) — "When AI Teammates Meet Code Review: Collaboration Signals Shaping the Integration of Agent-Authored Pull Requests" (Nachuma & Zibran, MSR 2026) — analyzes 33,596 agent-authored PRs across 2,807 repositories with logistic regression. It covers five agents: Claude Code, OpenAI Codex, Devin, GitHub Copilot, and Cursor. The overall merge rate is 71.5% (95% CI: [0.710, 0.720]). Merge rates vary by agent from 43.0% (Copilot) to 82.6% (OpenAI Codex), with Devin at 53.8%.

The study uses repository-clustered standard errors. Functional correctness is necessary but not enough for merge. Once a change is viable, collaboration dynamics determine the outcome.

## Collaboration signals

Reviewer engagement is the strongest positive predictor. At least one substantive review strongly increases the chance of merge. The paper frames this as selective investment: "reviewers selectively invest effort in changes perceived as viable." Engagement is both an outcome signal and a cause — reviewed PRs converge on reviewer expectations. Of 32 PRs with review loops, 30 were merged.

Force pushes are the strongest negative predictor. Rewriting history mid-review breaks shared understanding. Each force push invalidates prior review context and forces reviewers to re-orient, which signals instability and breaks incremental convergence.

Larger change sizes reduce the chance of merge. Larger diffs lower merge likelihood on their own. This compounds with cognitive load: large changesets reduce the chance of [initial reviewer engagement](agent-pr-volume-vs-value.md).

Iteration intensity has limited standalone value. More commits, revisions, or tests do not increase merge likelihood once collaboration signals are in the model. Optimizing for iteration volume yields less than optimizing for review alignment.

Time-to-first-review correlates positively with merge rates. Reviewers choose their battles, so PRs that wait longer for a first review tend to be ones pre-selected as worth engaging with.

## Failure modes

Qualitative analysis of 60 PRs (30 merged, 30 unmerged) identifies five failure categories:

| Failure mode | Cases |
|---|---|
| Design disagreements | 10 |
| Incomplete solutions | 7 |
| Process or policy violations | 3 |
| Coordination breakdown (including force pushes) | 2 |
| CI failures | 2 |

Design disagreements are the dominant failure mode. The agent's architecture diverged from what reviewers would accept, regardless of correctness. No amount of engagement closes a design disagreement if the agent cannot propose an alternative.

## Actionable review loop

The actionable review loop is the dominant success mechanism: specific feedback, targeted changes, convergence toward reviewer expectations:

- scope PRs so reviewers can form a complete opinion on a design in one pass
- make agent responses to review comments targeted and atomic — one commit per coherent change set, not a rebase
- batch reviewer feedback into single review rounds rather than iterating comment by comment

## Structural constraints as a design reference

GitHub Copilot's coding agent cannot force push by design. Branch restrictions and the absence of direct `git push` access [structurally enforce](https://docs.github.com/en/copilot/using-github-copilot/coding-agent/about-assigning-tasks-to-copilot) merge-friendly behavior. Teams building [custom agents](../tools/copilot/custom-agents-skills.md) can treat this as a reference: disabling force push during active review removes the strongest negative predictor.

[GitHub's best practices for Copilot tasks](https://docs.github.com/en/copilot/using-github-copilot/coding-agent/best-practices-for-using-copilot-to-work-on-tasks) converge on the same principles. Well-scoped tasks, pre-validated changes, and batched review comments reduce friction and align with these findings.

## When this backfires

Optimizing for reviewer engagement assumes reviewers are available and their expectations are sound. Five conditions undermine the pattern:

- chronic reviewer scarcity: engagement correlates with merge success because those PRs captured a scarce resource, not because you can manufacture engagement. High-volume agents compete for the same reviewer bandwidth.
- design disagreement without recourse: the dominant failure mode (10 of 30 failed PRs) is architectural divergence. If an agent cannot propose an alternative design, no review loop resolves the disagreement.
- reviewer abandonment after queueing: a long time-to-first-review helps only when reviewers eventually engage. If they abandon a queued PR, wait time becomes noise. Large diffs compound this risk, which [agent-driven PR slicing](agent-driven-pr-slicing.md) is meant to reduce.
- CRA-only review: the pattern assumes human reviewers with discretionary merge authority. Repositories reviewed only by automated agents show much lower merge rates (45% against 68%).
- high comment volume as a correction signal: each extra reviewer comment decreases agentic-PR merge odds by 2.8% (against +2.7% for human PRs), read as required corrections rather than productive alignment ([arXiv:2601.18749](https://arxiv.org/abs/2601.18749)). Related work reports 1 to 10% ghosting after feedback ([arXiv:2601.00753](https://arxiv.org/abs/2601.00753)).

## Example

An agent opens a 200-line PR adding a new webhook handler. The reviewer comments: "This should use the existing `EventBus` abstraction rather than calling handlers directly." The agent replies in a single follow-up commit that reroutes through `EventBus` and updates the test fixture — no rebase, no force push. The reviewer approves in the next pass. This is the actionable review loop: specific feedback, targeted atomic response, convergence. Contrast a failed pattern: the agent reads the same feedback as a signal to rewrite the entire event handling layer, force pushes 600 lines, and the reviewer abandons the thread — losing shared context and triggering the strongest negative predictor.

## Key Takeaways

- Reviewer engagement predicts merge success more strongly than code correctness; task design and PR framing matter as much as code
- Force pushes during active review are the strongest negative predictor; treat this as a hard constraint in agent configuration
- Keep agent PRs small; large diffs reduce reviewer willingness to engage and lower merge probability
- More iterations do not substitute for review alignment; optimize for reviewer expectations over iteration volume
- Design each PR for a reviewer who will comment once. What merges is specific feedback answered by a targeted change, so a PR that cannot converge in a single round rarely converges at all

## Related

- [PR Scope Creep as a Human Review Bottleneck](../patterns/anti-patterns/pr-scope-creep-review-bottleneck.md)
- [Agentic Code Review Architecture](agentic-code-review-architecture.md)
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md)
- [PR Description Style as a Lever for Agent PR Merge Rates](pr-description-style-lever.md)
- [Predicting Reviewable Code](predicting-reviewable-code.md)
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — merge rate gaps and the productivity paradox of high-volume agent PRs
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — empirical data on how reviewer composition (CRA-only vs. human) affects merge rates
- [Human-AI Review Synergy](human-ai-review-synergy.md) — complementary strengths of AI and human reviewers in code review collaboration
