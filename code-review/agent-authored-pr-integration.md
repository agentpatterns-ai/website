---
title: "Agent-Authored PR Integration and Merge Predictors"
description: "Reviewer engagement — not code correctness or iteration count — is the strongest predictor of whether an agent-authored PR gets merged."
tags:
  - human-factors
  - agent-design
  - workflows
---

# Agent-Authored PR Integration: Collaboration Signals That Determine Merge Success

> Reviewer engagement — not code correctness or iteration count — is the strongest predictor of whether an agent-authored PR gets merged; force pushes and large changesets are the strongest negative predictors.

## The Finding

[arXiv:2602.19441](https://arxiv.org/abs/2602.19441) — "When AI Teammates Meet Code Review: Collaboration Signals Shaping the Integration of Agent-Authored Pull Requests" (Nachuma & Zibran, MSR 2026) — presents a logistic regression analysis of 33,596 agent-authored PRs across 2,807 repositories, covering five agents: Claude Code, OpenAI Codex, Devin, GitHub Copilot, and Cursor. The overall merge rate is 71.5% (95% CI: [0.710, 0.720]), but merge rates vary by agent from 43.0% (Copilot) to 82.6% (OpenAI Codex), with Devin at 53.8%.

The study uses repository-clustered standard errors. Functional correctness is necessary but insufficient for merge — once viability is established, collaboration dynamics determine outcome.

## Collaboration Signals

**Reviewer engagement is the strongest positive predictor.** Receiving at least one substantive review strongly increases merge likelihood. The paper frames this as selective investment: "reviewers selectively invest effort in changes perceived as viable." Engagement is both an outcome signal and a causal mechanism — reviewed PRs converge on reviewer expectations. Qualitatively, 30 of 32 PRs with review loops were merged.

**Force pushes are the strongest negative predictor.** Rewriting history mid-review disrupts shared understanding. Each force push invalidates prior review context, forcing reviewers to re-orient — signaling instability and breaking incremental convergence.

**Larger change sizes reduce merge probability.** Larger diffs lower merge likelihood independently. This compounds with cognitive load: large changesets reduce the probability of initial reviewer engagement.

**Iteration intensity has limited standalone value.** More commits, revisions, or tests do not independently increase merge likelihood once collaboration signals are in the model. Optimizing for iteration volume without targeting reviewer expectations yields less than optimizing for review alignment.

**Time-to-first-review correlates positively with merge rates.** Reviewers choose battles, and PRs that wait longer for initial review tend to be ones pre-selected as worth engaging with.

## Failure Modes

Qualitative analysis of 60 PRs (30 merged, 30 unmerged) identifies five failure categories:

| Failure Mode | Cases |
|---|---|
| Design disagreements | 10 |
| Incomplete solutions | 7 |
| Process/policy violations | 3 |
| Coordination breakdown (incl. force pushes) | 2 |
| CI failures | 2 |

Design disagreements are the dominant failure mode — the agent's architecture diverged from what reviewers would accept, regardless of correctness. No amount of engagement closes a design disagreement if the agent cannot propose an alternative.

## Actionable Review Loop

The "actionable review loop" is the dominant success mechanism: specific feedback, targeted changes, convergence toward reviewer expectations. Structurally:

- PRs should be scoped so that reviewers can form a complete opinion on a design in one pass
- Agent responses to review comments should be targeted and atomic — one commit per coherent change set, not a rebase
- Reviewers should batch feedback into single review rounds rather than iterating comment-by-comment

## Structural Constraints as Design Reference

GitHub Copilot's coding agent cannot force push by design — branch restrictions and the absence of direct `git push` access [structurally enforce](https://docs.github.com/en/copilot/using-github-copilot/coding-agent/about-assigning-tasks-to-copilot) merge-friendly behavior. Teams building [custom agents](../tools/copilot/custom-agents-skills.md) can treat this as a reference: disabling force push during active review removes the strongest negative predictor.

[GitHub's best practices for Copilot tasks](https://docs.github.com/en/copilot/using-github-copilot/coding-agent/best-practices-for-using-copilot-to-work-on-tasks) converge on the same principles: well-scoped tasks, pre-validated changes, and batched review comments reduce friction and align with these findings.

## Example

An agent opens a 200-line PR adding a new webhook handler. The reviewer comments: "This should use the existing `EventBus` abstraction rather than calling handlers directly." The agent replies in a single follow-up commit that reroutes through `EventBus` and updates the test fixture -- no rebase, no force push. The reviewer approves in the next pass. This is the actionable review loop: specific feedback, targeted atomic response, convergence. Contrast with a failed pattern: the agent interprets the same feedback as a signal to rewrite the entire event handling layer, force pushes 600 lines, and the reviewer abandons the thread -- losing shared context and triggering the strongest negative predictor.

## Key Takeaways

- Reviewer engagement predicts merge success more strongly than code correctness; task design and PR framing matter as much as code
- Force pushes during active review are the strongest negative predictor; treat this as a hard constraint in agent configuration
- Keep agent PRs small; large diffs reduce reviewer willingness to engage and lower merge probability
- More iterations do not substitute for review alignment; optimize for reviewer expectations over iteration volume
- The actionable review loop — specific feedback, targeted response, convergence — is the dominant success mechanism

## Related

- [PR Scope Creep as a Human Review Bottleneck](../anti-patterns/pr-scope-creep-review-bottleneck.md)
- [Agentic Code Review Architecture](agentic-code-review-architecture.md)
- [Human-in-the-Loop Placement](../workflows/human-in-the-loop.md)
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md)
- [PR Description Style as a Lever for Agent PR Merge Rates](pr-description-style-lever.md)
- [Predicting Reviewable Code](predicting-reviewable-code.md)
- [Cognitive Load, AI Fatigue, and Sustainable Agent Use](../human/cognitive-load-ai-fatigue.md) — cognitive costs of sustained review and oversight that compound with large changesets
- [Agent-Assisted Code Review](agent-assisted-code-review.md)
- [Review-Then-Implement Loop](review-then-implement-loop.md)
- [Diff-Based Review](diff-based-review.md)
- [Tiered Code Review](tiered-code-review.md)
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — merge rate gaps and the productivity paradox of high-volume agent PRs
- [Human-AI Review Synergy](human-ai-review-synergy.md) — complementary strengths of AI and human reviewers in code review collaboration
- [Committee Review Pattern](committee-review-pattern.md)
