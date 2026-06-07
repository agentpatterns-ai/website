---
title: "Code Cleanliness as an Agent Cost Lever"
description: "Cleaner code does not change a coding agent's pass rate but cuts token use 7-8% and file revisitations 34% in a controlled minimal-pair study — an operational cost lever, not a capability fix."
tags:
  - workflows
  - cost-performance
  - code-review
  - arxiv
  - tool-agnostic
  - agent-design
last_reviewed: 2026-06-03
---

# Code Cleanliness as an Agent Cost Lever

> Cleaner code left agent pass rate unchanged but cut token use 7-8% and file revisitations 34% — a cost lever, not a capability fix.

Code cleanliness as an agent cost lever is the operational claim — backed by [Trivedi and Schmitt's minimal-pair study](https://arxiv.org/abs/2605.20049) — that reducing static-analysis violations and cognitive complexity in a codebase lowers token consumption and navigation hops for coding agents working in it, without changing whether they finish the task. The effect is real and measurable, but small enough that it only pays off when the cleanup is cheap and the codebase is large enough for navigation cost to matter.

## The Empirical Result

Trivedi and Schmitt (SonarSource, 2026) built six pairs of Java repositories — Apache Commons BCEL, Netflix Genie, and four others — where each pair shares architecture, dependencies, and external behavior but differs on SonarQube Cloud rule violations and cognitive complexity scores. They ran Claude Code across 33 tasks per repository, 660 trials in total, and constructed the pairs bidirectionally (degrading clean code *and* cleaning messy code) so the result is not an artifact of one starting direction ([arxiv:2605.20049](https://arxiv.org/abs/2605.20049)).

| Metric | Clean vs messy | Direction |
|--------|----------------|-----------|
| Task pass rate | Statistically indistinguishable | Cleanliness does not change correctness |
| Token consumption per task | 7-8% lower on cleaner code | Direct dollar cost lever |
| File revisitations per task | 34% lower on cleaner code | Fewer navigation hops, shorter loops |

The pass-rate finding is as load-bearing as the cost finding: agents do not "fail more" on messy code, so the cleanup justification has to live in the operational column, not the capability column ([arxiv:2605.20049](https://arxiv.org/abs/2605.20049)).

## Why It Works

Lower cognitive complexity and fewer rule violations make the relevant code for a task locatable from file and function names on the first attempt, so the agent spends fewer turns disambiguating where logic lives ([arxiv:2605.20049](https://arxiv.org/abs/2605.20049)). Token budget spent on irrelevant files is token budget not spent on reasoning — the same mechanism Anthropic's context-engineering work identifies for harness design and just-in-time loading ([Anthropic — Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). The 34% file-revisitation drop is the direct measurement of this navigation efficiency; the 7-8% token saving is its downstream consequence.

The cleanliness metric in the study is operationalized as SonarQube Cloud rule violations plus cognitive complexity scores ([arxiv:2605.20049](https://arxiv.org/abs/2605.20049)) — both measurable in CI, neither subjective. The page does not extend to claims about naming, comments, or architectural coherence, which the study did not isolate.

## When This Backfires

The minimal-pair study compared agents on already-clean versus already-messy code. It did not measure the engineering cost of moving a codebase from messy to clean, which is where the recommendation breaks down in practice:

- **The cleanup is more expensive than the savings**: a 7-8% token reduction on $100/seat/month is roughly $7-8/month per developer. Twenty engineer-hours of refactoring to shave that off a single module pays back over years, not weeks. The study did not measure cleanup ROI ([arxiv:2605.20049](https://arxiv.org/abs/2605.20049)).
- **Small or tightly-scoped codebases**: in repositories where every relevant file already fits in context, file-revisit count is bounded by file count. A 34% reduction on three revisits is meaningless ([arxiv:2605.20049](https://arxiv.org/abs/2605.20049)).
- **Agents themselves re-introduce mess**: a longitudinal MSR 2026 study of 806 Cursor-adopting repositories versus 1,380 controls found static-analysis warnings rise ~30% and code complexity rises ~42% after adoption, persisting six-plus months and surviving any velocity gains ([He et al., MSR 2026](https://arxiv.org/abs/2511.04427)). Cleaning a codebase for agent ergonomics without continuous quality gates is a treadmill — the same agents that benefit from cleanliness erode it.
- **Cognitive complexity is a partial proxy**: SonarQube cognitive complexity measures intra-function branching depth, not cross-cutting concerns, hidden global state, or naming inconsistency. The 7-8% headline may underweight or overweight different aspects of "cleanliness" depending on the codebase's actual pathology ([arxiv:2605.20049](https://arxiv.org/abs/2605.20049)).
- **Larger levers are available**: 7-8% token reduction sits below the variance of model-version pricing changes and well below what context engineering, prompt caching, or moving from a frontier to a mid-tier model can deliver. Treating cleanliness as the primary cost lever inverts the value chain.

The defensible position is narrow: existing maintainability investment — linters, complexity budgets, refactoring time the team would have spent anyway — also benefits agent runs as a measurable side effect. Cleaning up *for the agent specifically* requires the navigation cost to be a top-three line item in your agent spend.

## Example

A team running Claude Code over a 200-file Java service spends roughly $1,200/month on agent API costs. Their SonarQube dashboard shows several hundred open rule violations and an above-threshold cognitive complexity score on roughly a quarter of functions — the same kind of cleanliness gap the [Trivedi & Schmitt minimal pairs](https://arxiv.org/abs/2605.20049) were constructed to measure.

Two cleanup paths to evaluate against the [Trivedi & Schmitt baseline](https://arxiv.org/abs/2605.20049):

**Path A — Opportunistic cleanup as part of regular work:**

```yaml
# .github/workflows/quality-gate.yml — block PRs that raise complexity
- name: Cognitive complexity ceiling
  run: |
    # Fail when any function exceeds 15 (SonarQube default complexity rule)
    sonar-scanner -Dsonar.qualitygate.wait=true
```

Cost: zero incremental engineering — the gate runs on PRs the team would already write. Expected payoff: the codebase drifts toward cleaner over months, capturing the 7-8% token reduction as a byproduct.

**Path B — Dedicated refactoring sprint specifically to reduce agent token use:**

Cost: ~80 engineer-hours at $150/hour = $12,000. Annual token saving at 7.5%: $1,200 × 12 × 0.075 = $1,080. Payback period: ~11 years, ignoring re-erosion by agents.

Path A is the recommended posture: capture the cost lever from work the team would do anyway, and treat the 7-8% number as evidence that maintainability investment pays operationally — not as justification to refactor for agents specifically.

## Key Takeaways

- Cleaner code does not change agent pass rate but reduces token use by 7-8% and file revisitations by 34% on a controlled minimal-pair study ([Trivedi & Schmitt, 2026](https://arxiv.org/abs/2605.20049))
- The mechanism is navigation efficiency — fewer hops to locate the right file, fewer tokens spent disambiguating
- The cost lever is real but small; cleanup justified specifically for agent ergonomics rarely pays back within a year
- Pair the cleanliness side-effect with quality gates that prevent agents from re-introducing complexity, otherwise the savings decay ([He et al., MSR 2026](https://arxiv.org/abs/2511.04427))
- Cognitive complexity and rule violations are the operationalized metrics — measurable in CI, not subjective

## Related

- [The Velocity-Quality Asymmetry: Why AI Speed Gains Fade](velocity-quality-asymmetry.md) — the inverse finding: agents themselves degrade quality faster than velocity gains persist
- [Shadow Tech Debt Created by Autonomous AI Agent Commits](../anti-patterns/shadow-tech-debt.md) — the compounding-mess risk that the cleanliness cost lever does not address on its own
- [Entropy Reduction Agents: Automated Codebase Hygiene](entropy-reduction-agents.md) — scheduled background cleanup that captures the cleanliness side-effect without dedicated refactor sprints
- [Agent-Generated Code Maintenance Asymmetry](../code-review/agent-code-maintenance-asymmetry.md) — the maintenance footprint that determines whether your cleanup decays or holds
- [Comprehension Debt from AI-Generated Code Velocity](../anti-patterns/comprehension-debt.md) — the human-side debt that maintainability metrics do not capture
