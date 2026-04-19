---
title: "Convergence Detection in Iterative Agent Refinement"
description: "Monitor change velocity, output size, and content similarity across passes to detect when further refinement yields diminishing returns and stop mechanically."
tags:
  - agent-design
  - workflows
  - technique
  - tool-agnostic
aliases:
  - stopping criteria for iterative refinement
  - iteration stopping criteria
  - refinement termination detection
---

# Convergence Detection in Iterative Agent Refinement

> Monitor three observable signals across refinement passes to replace intuition-based stopping with a mechanical criterion.

## The Problem

Iterative refinement loops — plan polishing, critique passes, bead polishing, documentation drafts — have no natural stopping point. Agents and developers either stop too early (leaving unresolved issues) or over-refine (wasting compute on passes that change nothing). "It looks good enough" is not a stopping criterion.

For tasks with a test harness, this is solved: tests pass → stop. For prose, specs, and design documents, no such machine-checkable gate exists. Convergence detection fills that gap.

## The Three Signals

Monitor these signals across consecutive refinement passes:

| Signal | Converging | Diverging |
|--------|-----------|-----------|
| **Change velocity** | Rate of modifications slows — pass N changes 30%, pass N+3 changes 2% | Rate stays high or accelerates |
| **Output size** | Size stabilises or shrinks — additive passes are exhausted | Size grows — indicates scope creep, not refinement |
| **Content similarity** | Diff between consecutive passes shrinks toward zero | Diff stays large — substantive issues remain unresolved |

When all three signals converge simultaneously, further passes yield diminishing returns. When any signal diverges, issues remain unresolved and more passes are warranted.

## Failure Patterns

Three patterns indicate a restart is needed rather than continued iteration:

- **Oscillation** — output alternates between two versions across passes; the agent cannot resolve a trade-off without external input
- **Expansion** — output grows each pass instead of shrinking; scope is drifting rather than stabilising
- **Low-quality plateau** — all three signals converge but output quality remains poor; the approach needs redesign, not more passes

## Five-Pass Blunder Hunt

For critical outputs — major design specs, agent system prompts, architectural decisions — run the identical critique prompt five consecutive times against the same output. Each pass surfaces issues that previous passes normalised over. A single critique pass produces false confidence; repeated identical passes force examination of progressively subtler problems.

This technique applies the convergence signals: if pass 4 and pass 5 produce nearly identical critiques with no new issues, content similarity has converged and the output is stable.

## Relationship to Other Stopping Mechanisms

| Mechanism | When to use |
|-----------|------------|
| Convergence detection | Prose, specs, design docs — no test harness available |
| PASS/FAIL from evaluator | Code tasks with executable tests — machine-checkable |
| Max round limit | Fallback for all loops — prevents runaway iteration |
| Model self-declaration | Low-cost tasks where precision matters less |

Convergence detection complements the [evaluator-optimizer pattern](evaluator-optimizer.md)'s max-round fallback: the evaluator-optimizer terminates on PASS or round limit; convergence detection tells you when to set that round limit or when to stop early without a formal evaluator.

## Example

A developer is running critique passes on a system prompt for a coding agent. After each pass they compare the new version against the previous.

**Pass 1 → Pass 2:** 40% of lines changed. Output grew by 200 words. Clear convergence signal: diverging.

**Pass 3 → Pass 4:** 15% of lines changed. Output size stable. Partial convergence.

**Pass 4 → Pass 5:** 3% of lines changed (minor phrasing only). Output size unchanged. Diff near-zero. All three signals converge: stop.

Running a sixth pass would likely produce cosmetic changes that may degrade quality by introducing unnecessary variation.

## When Signal Convergence Misleads

Convergence signals measure whether the output is *stabilising*, not whether it is *correct*. Lee et al., [RefineBench: Evaluating Refinement Capability of Language Models via Checklists](https://arxiv.org/abs/2511.22173) (2025), evaluated Gemini 2.5 Pro, GPT-5, and DeepSeek-R1 on 1,000 problems across 11 domains and found that self-refinement without external feedback yielded gains of +1.8 percentage points or less over five iterations, while guided refinement approached near-perfect scores — and that models routinely halt early due to overconfidence even when errors remain. When signals converge without an external evaluator, the stable state may reflect self-bias, not quality. For high-stakes outputs, pair convergence detection with an external checker (tests, a second model, a human reviewer) rather than relying on the signals alone.

## Key Takeaways

- Three signals — change velocity, output size, content similarity — replace intuitive stopping with observable criteria
- Oscillation, expansion, and low-quality plateau are failure patterns that require a restart, not more passes
- The [five-pass blunder hunt](../verification/five-pass-blunder-hunt.md) applies convergence detection to critique loops: when consecutive passes produce near-identical critiques, the output has stabilised
- Convergence detection fills the gap for prose and design tasks where no test harness exists; use PASS/FAIL from tests for code
- Always pair with a hard max-round limit as a cost fallback

## Sources

- Madaan et al., [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651) (2023) — demonstrates iterative LLM refinement with quantitative stopping criteria based on feedback scores; underpins the convergence-signal approach
- Lee et al., [RefineBench: Evaluating Refinement Capability of Language Models via Checklists](https://arxiv.org/abs/2511.22173) (2025) — counter-evidence that self-refinement without external feedback is unreliable and that frontier models halt prematurely

## Related

- [Evaluator-Optimizer Pattern](evaluator-optimizer.md) — external evaluator that complements convergence signals
- [Agent Self-Review Loop](agent-self-review-loop.md) — self-review as a convergence signal source
- [Five-Pass Blunder Hunt](../verification/five-pass-blunder-hunt.md) — applied convergence on critique loops
- [Ralph Wiggum Loop](ralph-wiggum-loop.md) — fixed-prompt iteration that benefits from convergence stopping
- [Failure-Driven Iteration](../workflows/failure-driven-iteration.md) — failure signals that override convergence
- [Loop Strategy Spectrum](loop-strategy-spectrum.md) — accumulated vs fresh context across iteration loops
- [Agentic Flywheel](agentic-flywheel.md) — convergence signals applied to self-improvement cycles
- [Agent Loop Middleware](agent-loop-middleware.md) — middleware hooks for instrumenting stopping logic
