---
title: "Agent PR Volume vs. Value: The Productivity Paradox"
term: "Agent PR Volume vs. Value"
description: "Autonomous coding agents dramatically increase PR volume but face lower merge rates than humans — speed and quantity alone do not equal engineering value."
tags:
  - code-review
  - human-factors
  - workflows
  - tool-agnostic
last_reviewed: 2026-06-18
maturity: established
---

# Agent PR Volume vs. Value: The Productivity Paradox

> Autonomous coding agents can generate PRs orders of magnitude faster than humans, but acceptance rates are significantly lower — volume amplifies output without guaranteeing value.

## The finding

The AIDev dataset gives the first large-scale picture of agent-authored PRs in real projects: 456,535 pull requests from five autonomous coding agents (OpenAI Codex, Devin, GitHub Copilot, Cursor, Claude Code) across 61,453 repositories ([arXiv:2507.15003](https://arxiv.org/abs/2507.15003)).

The headline numbers show a paradox. Agents are much faster, but they get measurably less code merged.

## Speed versus acceptance

| Metric | Human | OpenAI Codex | Devin | GitHub Copilot |
|--------|-------|-------------|-------|----------------|
| Median close time | 3.9 hours | 0.3 hours | — | 17.2 hours |
| Acceptance rate | ~77% | 64% | 49% | 35% |

Codex PRs close ten times faster than human PRs. But the best-performing agent still trails humans by 13 percentage points on acceptance. Speed does not make up for shortfalls in quality and relevance.

One developer submitted 164 Codex-assisted PRs in three days, nearly matching the 176 human-authored PRs produced over 3.5 years. The volume is real. Whether it delivers proportional engineering value is the open question.

## Structural simplicity

Only 9.1% of Codex-assisted PRs changed cyclomatic complexity, compared with 23.3% for human PRs. Agents tend toward simpler, boilerplate-style changes — routine fixes, documentation, and scaffolding rather than architectural work.

This is not a problem in itself. Many real engineering tasks are simple. But the 9.1%-versus-23.3% complexity gap means the volume numbers overstate how hard the completed work was.

## Task specialization across agents

Agents cluster around different task types:

- GitHub Copilot: 42.2% bug fixes, against 26.9% for humans
- Cursor and Claude Code: more than 40% feature development
- OpenAI Codex and Devin: balanced across task types

Agents also favor different languages. TypeScript leads overall (26.4%), but Codex skews toward Python (25.5%) and Copilot toward C# (29.8%).

## Where agents outperform

Documentation is the clearest agent strength. Codex (88.6%) and Claude Code (85.7%) beat the human documentation acceptance rate (76.5%). Natural language generation is a core LLM strength, and documentation PRs benefit directly.

## The review burden shift

Bots make up 20% of reviewers on agent PRs, compared with 10% for human PRs. This points to an emerging pattern: agent-authored code increasingly passes through automated review before, or instead of, human review. Teams adopting agents at scale need a review triage strategy — see [tiered code review](tiered-code-review.md).

As volume rises, the value shifts from writing code to judging it. [Addy Osmani argues that code review becomes the highest-value engineering skill](https://addyo.substack.com/p/agentic-code-review) as agent output grows, because deciding what to merge increasingly outweighs writing the change.

Tooling vendors are responding to the same fixed-reviewer-capacity problem. Linear built a dedicated diff and review surface, [Linear Diffs](https://linear.app/blog/linear-diffs), to make review fast enough to keep pace with agent-generated PRs — a tooling-side answer to the review bottleneck this page describes.

## Why acceptance rates lag

The AIDev study blames the acceptance gap on structural and contextual factors. Agent PRs cluster around simpler tasks that reviewers may deprioritize. Agents also lack the ambient project context that shapes which changes are worth making at a given moment. They cannot see unwritten priorities — roadmap direction, or [tribal knowledge](../anti-patterns/implicit-knowledge-problem.md) about which subsystems are frozen. So they optimize for correctness in a local scope rather than relevance across the broader work queue ([arXiv:2507.15003](https://arxiv.org/abs/2507.15003)).

A second study of agent-authored fixes adds failure-mode detail. Reviewers rejected 46.41% of the studied fixes, and the authors sort the reasons into a taxonomy of 14 rejection reasons across four categories ([arXiv:2606.13468](https://arxiv.org/abs/2606.13468)). That taxonomy points reviewers at the specific ways agent fixes fail, not just the aggregate shortfall.

## When this backfires

Volume-first agent deployment underperforms when:

- Scope is poorly defined: agents without clear, bounded task specifications produce PRs that are technically valid but strategically irrelevant. The 49% acceptance rate for Devin reflects this failure mode.
- Review capacity is fixed: 10× more PRs at lower acceptance rates consumes reviewer time without proportional throughput. Bot pre-screening, already 20% of agent PR reviews, is a partial mitigation, not a solution.
- Complexity is the real bottleneck: if the backlog is dominated by architectural changes (cyclomatic complexity), agent output skewed toward simpler tasks adds little to velocity. Only 9.1% of agent PRs change complexity, versus 23.3% for humans.
- Integration friction is ignored: a separate analysis of 142K agent-authored PRs reports a 27.67% merge-conflict rate, with wide variation across agents ([arXiv:2604.03551](https://arxiv.org/abs/2604.03551)). Higher PR volume raises conflict exposure, so raw throughput gains erode once rebase and resolution costs are counted.
- Merge is treated as success: a study of 1,210 merged agent-generated bug-fix PRs found that merge success does not reliably reflect post-merge code quality. Code smells, especially at critical and major severities, dominate the defects introduced ([arXiv:2601.20109](https://arxiv.org/abs/2601.20109)). Acceptance rate alone over-reports value unless paired with downstream quality signals.

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
- [Human-AI Review Synergy](human-ai-review-synergy.md) — empirical evidence on complementary strengths of human and AI reviewers
- [Agent-Assisted Code Review](agent-assisted-code-review.md) — using agents as a mechanical first pass before human review
- [Predicting Which AI-Generated Functions Will Be Deleted](predicting-reviewable-code.md) — structural signals that predict which agent-generated code survives review
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — empirical merge rate gap (45% vs 68%) when CRAs review without human involvement
- [Interaction-Pattern Evaluation for Agentic PRs](interaction-pattern-evaluation.md) — the interaction-signal complement to these outcome rates, since merge/reject labels misclassify most rejected agentic PRs

## Sources

- [arXiv:2507.15003](https://arxiv.org/abs/2507.15003) — Li, Zhang & Hassan (2025): "The Rise of AI Teammates in SE 3.0" — AIDev dataset of 456K agent-authored PRs
- [arXiv:2604.03551](https://arxiv.org/abs/2604.03551) — "AgenticFlict: A Large-Scale Dataset of Merge Conflicts in AI Coding Agent Pull Requests on GitHub" — 27.67% conflict rate across 142K agent PRs
- [arXiv:2601.20109](https://arxiv.org/abs/2601.20109) — "Beyond Bug Fixes: An Empirical Investigation of Post-Merge Code Quality Issues in Agent-Generated Pull Requests" — merge success does not reliably reflect post-merge code quality
- [arXiv:2606.13468](https://arxiv.org/abs/2606.13468) — empirical study of agent-authored fixes: 46.41% rejected, with a taxonomy of 14 rejection reasons across four categories
- [Agentic Code Review (Addy Osmani)](https://addyo.substack.com/p/agentic-code-review) — review becomes the highest-leverage engineering skill as agent output volume rises

> Headline acceptance-rate figures derive primarily from the AIDev snapshot. Treat them as initial benchmarks corroborated by independent integration and post-merge-quality evidence, not as settled industry averages.

