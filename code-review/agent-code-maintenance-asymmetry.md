---
title: "Agent-Generated Code Maintenance Asymmetry"
description: "AI-generated files receive about half the commit frequency of human-authored files, and the modification mix shifts toward feature additions instead of bug fixes — a maintenance footprint that requires its own ownership and review policy."
term: "Agent-Generated Code Maintenance Asymmetry"
tags:
  - code-review
  - human-factors
  - arxiv
  - tool-agnostic
aliases:
  - Agent Code Maintenance Footprint
  - Agent-Generated Code Lifecycle
last_reviewed: 2026-06-02
maturity: emerging
---

# Agent-Generated Code Maintenance Asymmetry

> AI-generated files get about half the commit frequency of human-authored ones, and their changes skew toward features over bug fixes — a distinct maintenance footprint.

## The evidence

An empirical study measured how AI-generated and human-authored files diverge after merge. It tracked 508 AI-generated files and 1,543 modifying commits across 100 GitHub repositories in the AIDev dataset ([arXiv:2605.06464](https://arxiv.org/abs/2605.06464)). Three asymmetries appear in a file's first six months.

### Frequency

AI-generated files receive roughly half the commit frequency of human-authored files in the first month, with activity declining further over the subsequent two months. The magnitude of each modification is also smaller — fewer lines touched per commit ([arXiv:2605.06464](https://arxiv.org/abs/2605.06464)).

A line-level replication on a separate AIDev sample finds the same direction with statistical significance: AI-authored lines have a 16% lower hazard of modification (HR = 0.842, p < 0.001) and a 15.8 percentage-point lower modification rate ([arXiv:2601.16809](https://arxiv.org/abs/2601.16809)).

### Modification mix

The composition of changes inverts between origins.

| Modification type | AI-generated | Human-authored |
|-------------------|-------------:|---------------:|
| Feature addition | 21.78% | — |
| Refactoring | 14.19% | — |
| Bug fix | 11.73% | 16.76% |
| Documentation | — | 16.22% |

For AI-generated files, feature additions lead. For human-authored files, bug fixes lead ([arXiv:2605.06464](https://arxiv.org/abs/2605.06464)).

### Who maintains

Humans perform 83.21% of maintenance commits on AI-generated files. On human-authored files the share is 92.98%. The agent that wrote the file rarely returns to maintain it ([arXiv:2605.06464](https://arxiv.org/abs/2605.06464)).

## Two readings of the same data

The authors flag the ambiguity directly: lower modification rates "might suggest superior code quality, yet developers may avoid modifying AI-generated code due to difficulty in comprehending it" ([arXiv:2605.06464](https://arxiv.org/abs/2605.06464)).

The second reading has separate support. A study of 302,600 AI-authored commits across 6,299 repositories found 22.7% of AI-introduced issues survive to the repository's latest version, with code smells accounting for 89.3% ([arXiv:2603.28592](https://arxiv.org/abs/2603.28592)). Lower commit volume is not the same as fewer defects.

## Why the mix shifts to features

The Sawada et al. paper offers one reading: "generated files may lack sufficient coverage of requirements" — agents under-deliver on scope, leaving humans to add the missing capability after merge ([arXiv:2605.06464](https://arxiv.org/abs/2605.06464)). This fits the wider pattern that agents skew simpler. Codex-assisted PRs change cyclomatic complexity 9.1% of the time, against 23.3% for human PRs ([arXiv:2507.15003](https://arxiv.org/abs/2507.15003)).

## Practical implications

Treat AI-authored regions as a distinct maintenance category. The 83/17 split means the team that ships an AI-authored file maintains it, rarely with help from the agent that wrote it.

Do not read low commit frequency as a quality signal. Two mechanisms produce the same observation. Pair the metric with defect-survival or comprehension-test scores before you treat stability as cleanliness.

Audit for missing scope, not just bugs. Feature additions dominate post-merge maintenance, so ask "what did the agent leave out?" rather than "what did it get wrong?"

Modification timing tracks organizational factors. Predicting when AI-authored code gets touched scores Macro F1 = 0.285 on textual features alone. Review depth, ownership, and comprehension shape timing more than code structure does ([arXiv:2601.16809](https://arxiv.org/abs/2601.16809)).

## Key Takeaways

- Read the modification mix, not the commit count. Frequency alone (roughly half, at smaller per-commit magnitude) is consistent with both better quality and avoidance, so it settles nothing on its own
- The modification mix inverts: AI files are dominated by feature additions (21.78%) and refactoring (14.19%); human files are dominated by bug fixes (16.76%) and documentation (16.22%)
- Humans perform 83.21% of maintenance on AI-generated files; agents return for only 16.79%
- Lower modification rates have two competing explanations — better quality or comprehension-driven avoidance — and the data does not distinguish them
- Feature-addition dominance suggests AI-generated files under-cover requirements at merge time

## When this pattern does not apply

The 6-month observation window and the 100-repository AIDev sample limit how far these findings generalize. The asymmetries are unlikely to hold in three contexts:

- Throwaway scaffolding: prototypes, spike branches, and generated boilerplate that no one was going to maintain regardless of authorship
- Highly specified ticket workflows: narrow, fully specified tasks (for example, "implement this DTO") where low post-merge modification reflects spec stability, not avoidance or quality
- Closed-loop AI authoring and maintenance: pipelines where an agent both writes and maintains code (for example, agentic refactor jobs on cron) collapse the human-versus-agent maintenance split and invalidate the 83/17 ratio

One caveat on that last context: routing maintenance back to agents does not make the lower-volume reading safe. Agents introduce fewer breaking changes when generating new code (3.45% against 7.40% for humans) but more during maintenance — 6.72% on refactoring, 9.35% on chore changes — a "Confidence Trap" where highly confident agentic PRs still break callers ([arXiv:2603.27524](https://arxiv.org/abs/2603.27524)).

## Related

- [Shadow Tech Debt](../patterns/anti-patterns/shadow-tech-debt.md) — the architectural-incoherence mechanism that produces issues agents do not return to fix
- [Comprehension Debt](../patterns/anti-patterns/comprehension-debt.md) — the human-side mechanism for why developers avoid modifying code they did not author
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — pre-merge counterpart: agents author at high volume but lower acceptance, and skew structurally simpler
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — review-side mechanism by which AI-authored work makes it through merge despite missing scope
- [Predicting Reviewable Code](predicting-reviewable-code.md) — predictive signals for AI-generated functions likely to be deleted, complementary to maintenance-survival data

## Sources

- [arXiv:2605.06464](https://arxiv.org/abs/2605.06464) — Sawada, Shirai, Kashiwa, Yamaguchi, Iwata, Iida: "To What Extent Does Agent-generated Code Require Maintenance? An Empirical Study"
- [arXiv:2601.16809](https://arxiv.org/abs/2601.16809) — "Will It Survive? Deciphering the Fate of AI-Generated Code in Open Source" — line-level survival analysis on a separate AIDev sample
- [arXiv:2603.28592](https://arxiv.org/abs/2603.28592) — "Debt Behind the AI Boom: A Large-Scale Empirical Study of AI-Generated Code in the Wild"
- [arXiv:2507.15003](https://arxiv.org/abs/2507.15003) — AIDev dataset paper
- [arXiv:2603.27524](https://arxiv.org/abs/2603.27524) — "Safer Builders, Risky Maintainers: A Comparative Study of Breaking Changes in Human vs Agentic PRs" — agents are safer at generation but riskier during maintenance (the "Confidence Trap")
