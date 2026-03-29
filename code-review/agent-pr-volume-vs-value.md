---
title: "Agent PR Volume vs. Value: The Productivity Paradox"
description: "Autonomous coding agents dramatically increase PR volume but face lower merge rates than humans — speed and quantity alone do not equal engineering value."
tags:
  - code-review
  - human-factors
  - workflows
---

# Agent PR Volume vs. Value: The Productivity Paradox

> Autonomous coding agents can generate PRs orders of magnitude faster than humans, but acceptance rates are significantly lower — volume amplifies output without guaranteeing value.

## The Finding

The AIDev dataset — 456,535 pull requests from five autonomous coding agents (OpenAI Codex, Devin, GitHub Copilot, Cursor, Claude Code) across 61,453 repositories — provides the first large-scale empirical picture of agent-authored PRs in real-world development ([arXiv:2507.15003](https://arxiv.org/abs/2507.15003)).

The headline numbers reveal a paradox: agents are dramatically faster but measurably less effective at getting code merged.

## Speed vs. Acceptance

| Metric | Human | OpenAI Codex | Devin | GitHub Copilot |
|--------|-------|-------------|-------|----------------|
| Median close time | 3.9 hours | 0.3 hours | — | 17.2 hours |
| Acceptance rate | ~77% | 64% | 49% | 35% |

Codex PRs close ten times faster than human PRs. But the acceptance gap — 13 percentage points below humans for the best-performing agent — indicates that speed does not compensate for quality and relevance shortfalls.

One developer submitted 164 Codex-assisted PRs in three days, nearly matching 176 human-authored PRs produced over 3.5 years. The volume is real. Whether it translates to proportional engineering value is the open question.

## Structural Simplicity

Only 9.1% of Codex-assisted PRs introduced cyclomatic complexity changes, compared to 23.3% for human PRs. Agents gravitate toward simpler, boilerplate-style modifications — routine fixes, documentation, and scaffolding rather than architectural changes.

This is not inherently a problem. Many real engineering tasks are simple. But it means the volume numbers overstate the difficulty of work being completed.

## Task Specialization Across Agents

Agents cluster around different task types:

- **GitHub Copilot**: 42.2% bug fixes (vs. 26.9% for humans)
- **Cursor & Claude Code**: >40% feature development
- **OpenAI Codex & Devin**: balanced across task types

Agents also show distinct language affinities: TypeScript dominates overall (26.4%), but Codex skews toward Python (25.5%) and Copilot toward C# (29.8%).

## Where Agents Outperform

Documentation is the clearest agent strength. Codex (88.6%) and Claude Code (85.7%) exceed human documentation acceptance rates (76.5%). Natural language generation is a core LLM capability, and documentation PRs benefit directly.

## The Review Burden Shift

20% of reviewers on agent PRs are bots, compared to 10% for human PRs. This suggests an emerging pattern: agent-authored code increasingly passes through automated review before (or instead of) human review. Teams adopting agents at scale need a review triage strategy — see [Tiered Code Review](tiered-code-review.md).

## Key Takeaways

- Agent PR volume can increase by 10-50x, but acceptance rates drop 13-42 percentage points below human baselines
- Speed gains are real but skew toward structurally simpler tasks — cyclomatic complexity changes are 2.5x less frequent in agent PRs
- Documentation is the highest-confidence agent task type, with acceptance rates exceeding human baselines
- Review infrastructure must scale with agent output — bot reviewers already handle a disproportionate share of agent PR reviews
- Merge rate, not PR count, is the metric that matters for measuring agent-assisted productivity

## Related

- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — collaboration signals that predict merge success for agent PRs
- [PR Description Style as a Lever](pr-description-style-lever.md) — how description structure affects agent PR merge rates
- [Tiered Code Review](tiered-code-review.md) — routing review effort by risk level
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — designing high-signal review feedback

## Sources

- [arXiv:2507.15003](https://arxiv.org/abs/2507.15003) — Li, Zhang & Hassan (2025): "The Rise of AI Teammates in SE 3.0" — AIDev dataset of 456K agent-authored PRs

## Unverified Claims

- The "SE 3.0" framing as a named paradigm shift appears to originate from the paper authors rather than being an established industry term `[unverified]`
