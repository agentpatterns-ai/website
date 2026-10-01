---
title: "The Agent-on-Agent Maintenance Penalty"
term: "Agent-on-Agent Maintenance Penalty"
description: "Agents resolve fewer tasks on code another agent wrote. Cyclomatic complexity, Halstead volume and line counts do not predict which code causes the drop."
tags:
  - anti-pattern
  - tool-agnostic
  - arxiv
aliases:
  - agent code maintainability
  - building on agent code
  - input error contract drift
last_reviewed: 2026-09-30
maturity: emerging
---

# The Agent-on-Agent Maintenance Penalty

> An agent extending agent-written code resolves fewer tasks than one extending human code, and the inherited code's maintainability metrics do not predict the penalty.

Across four frontier agents and four benchmarks, downstream resolve rate fell by "up to 13.1%" when the inherited patch came from an agent, not a human ([Patel et al., 2026](https://arxiv.org/abs/2606.21804v2)). An agent did the follow-on work throughout. When people evolved AI-co-developed code, a 151-participant experiment "revealed no significant differences in subsequent evolution with respect to completion time or code quality" ([Borg et al., 2026](https://arxiv.org/abs/2507.00788v3)).

## How big the effect is

The 13.1-point figure is one model on one benchmark: GLM 4.7 on SWE-Bench Pro. Four of the sixteen pairs match or beat the human baseline, and the paper discounts three on sample size or a weak ceiling. Refactoring is worst hit at 8.21 points on average; bug fixing least at 4.05 ([Patel et al., 2026](https://arxiv.org/abs/2606.21804v2)).

## The signal that predicts it

Cyclomatic complexity, cognitive complexity and Halstead volume separate nothing at either step: "static maintainability metrics show near-identical distributions on HA wins and AA wins". HA is the chain that inherited a human patch. AA is the one that inherited an agent patch. Two features do separate the 405 cases where the chains disagreed: downstream patch size and task difficulty.

The third sits in the inherited code: the agent changed input validation or error handling relative to the human's. An added gating check, a swapped default, a new exception type. Where that drift is present, the odds the human chain is the one to resolve are 1.83 times those of the agent chain (95% CI 1.15 to 2.92, p = 0.011); a second judge model reproduces it at 1.70 ([Patel et al., 2026](https://arxiv.org/abs/2606.21804v2)).

## Why it works

The drift persists into the follow-on task. The follow-on patch leaves the agent's drift unchanged on 85.9% of the 262 human-chain wins, and rewrites the divergent function on 6.9% ([Patel et al., 2026](https://arxiv.org/abs/2606.21804v2)).

## When this backfires

- Your maintainers are people. That case is out of scope, and the nearest evidence found nothing ([Borg et al., 2026](https://arxiv.org/abs/2507.00788v3)).
- You answer it with a complexity gate. Those metrics showed no separation, and a SonarQube comparison on the same class of proxy found LLM code "has fewer bugs and requires less effort to fix them overall" ([Molison et al., 2025](https://arxiv.org/abs/2508.00700v1)).
- You diagnose every failure this way. The drift is confirmed as the cause on 20.6% of those instances; 74.4% "fail for reasons we have not isolated" ([Patel et al., 2026](https://arxiv.org/abs/2606.21804v2)).
- You extrapolate to long chains. The setup is two pull requests deep; compounding is untested ([Patel et al., 2026](https://arxiv.org/abs/2606.21804v2)).

## Example

One of the paper's five worked cases is removed input gating. The human implementation rejects a call made with two list arguments. The agent's implementation of the same function accepts them and builds a result instead. The follow-on task then edits a different function and never touches the divergence, "so the test that expects the call to be rejected fails" ([Patel et al., 2026](https://arxiv.org/abs/2606.21804v2)).

## Key Takeaways

- Read the penalty as an agent-to-agent effect. It is not evidence that people will struggle with agent code.
- Review the input and error contract of an agent's patch against what the codebase already did: gating checks added or removed, defaults swapped, exception types changed.
- Complexity metrics are the wrong gate here. Cyclomatic complexity, cognitive complexity and Halstead volume showed near-identical distributions across the two groups.
- Weight review toward refactoring, where the measured drop is largest (8.21 points on average).
- Most of the gap stays unexplained (the regression recovers a McFadden R-squared of 0.069), so treat contract drift as one cause to check rather than the diagnosis.

## Related

- [Shadow Tech Debt](shadow-tech-debt.md) — the architectural half of the same problem, drift no single agent PR looks responsible for
- [The Reasoning-Complexity Trade-off](reasoning-complexity-tradeoff.md) — stronger models producing more coupled code, a second route from capability to maintenance cost
- [Density-Normalized Quality Metrics Mask AI-Driven Code Growth](density-normalized-quality-metric.md) — another standard code metric reporting the wrong story about agent output
- [Conceptual Integrity Erosion in Agent-Built Codebases](conceptual-integrity-erosion.md) — what happens to design coherence once the cost of a change collapses
- [Code Health as a Signal for Agent-Generated Test Quality](../../verification/code-health-agent-generated-tests.md) — the same metrics pointed the other way, at the code an agent is asked to test
