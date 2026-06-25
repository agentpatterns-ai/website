---
title: "Source Code Minification for State-in-Context Agents"
term: "Source Code Minification"
description: "Minifying source code fed to coding agents cuts input tokens up to 42% but drops SWE-bench resolution rate by 12 percentage points — measure the trade before applying."
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-02
maturity: emerging
---

# Source Code Minification for State-in-Context Agents

> Source code minification cuts agent input tokens 42% on SWE-bench Verified but drops resolution rate from 50% to 38% — measure the trade before applying.

**Related lesson:** [Measure Before You Optimize](https://learn.agentpatterns.ai/context-engineering/measure-before-you-optimize/) — this concept features in a hands-on lesson with quizzes.

Source code minification — removing comments, collapsing whitespace, shortening identifiers, and stripping docstrings — is a measured trade-off. On SWE-bench Verified with GPT-5-mini and the DirectSolve state-in-context agent, cumulative minification cut average input tokens 42% (from ~90,500 to ~52,800 per task) while dropping pass@1 resolution rate from 50.0% to 38.0% — a 12-percentage-point absolute regression, ~24% of baseline ([Hrubec & Cito, 2026](https://arxiv.org/abs/2606.01326)). The technique is viable when a workload can absorb accuracy loss for token savings; it is the wrong default for production agents that land code.

## Apply Only Under These Conditions

The evidence supports minification only when all four conditions hold:

1. **Token cost dominates run economics.** The agent reads large code corpora repeatedly — long-running state-in-context agents, batch evaluation, or fleet-wide inference where the 42% saving compounds across thousands of runs.
2. **A measurable accuracy regression is acceptable.** A 24% relative drop means roughly one in four previously-solved tasks now fails. Workflows that surface failures cheaply (human review, retry budgets, low-stakes generation) can absorb this; auto-merge pipelines cannot.
3. **The accuracy cost is measured on the target workload, not assumed from this paper.** Hrubec & Cito test one agent (DirectSolve), one benchmark (SWE-bench Verified), and primarily one model (GPT-5-mini). Transferring the trade-off without re-measuring is unsupported.
4. **The accuracy budget is spent in one place.** Combining minification with other token-saving compressions ([Validating Token-Optimized Formats](validate-token-optimized-formats-in-agentic-loops.md), aggressive pruning, log compression) stacks accuracy losses; each compression must be priced separately.

## What Was Tested

Hrubec & Cito apply four token-reducing transformations cumulatively to the source code in the agent's context:

| Transformation | What is removed | Token impact source |
|----------------|----------------|---------------------|
| Comment removal | Inline and block comments | High in commented code |
| Whitespace elimination | Indentation, blank lines, extra spaces | Moderate, depends on style |
| Identifier shortening | Long variable and function names → short forms | High in domain-rich code |
| Docstring removal | Function and module docstrings | High in libraries with API docs |

The headline 42% / -12pp figure is the cumulative effect of all four applied together. The paper does not provide a clean per-technique accuracy decomposition, so practitioners cannot reliably pick "just remove comments" from this study and expect a fractional accuracy cost.

## Why It Works

Source code carries information through two channels: structural (AST, control flow) and lexical (identifiers, comments, docstrings). Minification strips the lexical channel on the assumption that structure carries the meaning. Independent measurement contradicts that assumption: removing the naming channel "severely degrades intent-level tasks" and causes "consistent reductions on execution tasks that should depend only on structure," because current LLMs use identifier names as a primary semantic channel rather than a redundant gloss on the AST ([Liu et al., 2025](https://arxiv.org/abs/2510.03178)).

The token savings are real, but the lost channel forces a compensating cost. A controlled experiment on log-format compression showed the same dynamic: aggressive compression cut input tokens 17% but raised *total* session cost 67%, because the model spent reasoning tokens reconstructing what was removed ([Ustynov, 2026](https://arxiv.org/abs/2604.07502)). On SWE-bench the lost capacity surfaces as failed tasks rather than longer chains, but the underlying mechanism is the same — minification trades a readable channel for token savings, and the channel was load-bearing.

## When This Backfires

The trade-off inverts under five conditions:

1. **Production code-modification agents.** A 12pp resolution-rate drop is a 24% relative regression; for any workflow that opens or merges PRs, the cost dominates.
2. **Single-shot or low-volume usage.** The 42% saving is small in absolute terms per run; without thousands of compounding runs, the accuracy hit dominates.
3. **Frontier models on unmeasured tasks.** The paper measures GPT-5-mini; effects on different model classes are unknown. Transferring across model tiers is unjustified ([Hrubec & Cito, 2026](https://arxiv.org/abs/2606.01326)).
4. **Domain-rich codebases.** Code where identifiers encode business semantics — financial, medical, legal — degrades hardest when names are shortened ([Liu et al., 2025](https://arxiv.org/abs/2510.03178)).
5. **Iterative multi-turn agents.** Agents that re-read code across turns compound the accuracy loss each turn rather than absorbing it once.

For most production stacks the right baseline is unminified code plus orthogonal levers — prompt caching, structural transforms that preserve semantics ([Token-Efficient Code Generation](token-efficient-code-generation.md)), and field projection at tool boundaries — which buy tokens without the accuracy gamble.

## Example

An evaluation plan before applying minification to a production agent:

**Before** — token-count benchmark only:

```
1. Take 100 source files. Apply cumulative minification.
2. Measure token reduction. See 42%. Ship the change.
```

This is the failure mode — the test measures token cost in isolation and misses the resolution-rate regression.

**After** — measure on the actual workload:

```
1. Replay 100 production tasks with three configs:
   a. No minification (baseline)
   b. Comment + whitespace only (lower-risk subset)
   c. Full cumulative minification
2. Measure: total tokens per task, end-to-end task success rate,
   and cost per successful task (tokens times price divided by success).
3. Decide per workload. Cost-per-success is the only metric that
   captures the token-vs-accuracy trade in one number.
```

The decoupled measurement reveals which side of the Pareto frontier the workload sits on; token-count-only evaluation cannot.

## Key Takeaways

- Cumulative source-code minification cuts SWE-bench Verified input tokens 42% but drops pass@1 resolution rate from 50% to 38% on GPT-5-mini with the DirectSolve agent ([Hrubec & Cito, 2026](https://arxiv.org/abs/2606.01326)).
- The 12-percentage-point absolute regression is a ~24% relative drop in solved tasks — unacceptable for production code-modification agents.
- LLMs use identifier names as a primary semantic channel; stripping them removes load-bearing input, not redundant gloss ([Liu et al., 2025](https://arxiv.org/abs/2510.03178)).
- Token savings are real but a compensating cost surfaces — either as failed tasks or as extra reasoning tokens reconstructing what was removed ([Ustynov, 2026](https://arxiv.org/abs/2604.07502)).
- Default to unminified code; measure cost-per-successful-task on replayed production traces before applying minification.

## Related

- [Token-Efficient Code Generation](token-efficient-code-generation.md) — AST-preserving structural transforms that cut tokens without removing semantic content, a lower-risk alternative on the generation side.
- [Semantic Density Optimization](semantic-density-optimization.md) — The compression paradox: removing semantic content shifts cost from input tokens to reasoning, explaining the mechanism behind the SWE-bench regression.
- [Token Preservation Backfire](../anti-patterns/token-preservation-backfire.md) — A related anti-pattern: instructing the agent to "be efficient" creates a competing objective that degrades work in similar ways.
- [Validating Token-Optimized Formats Inside Agentic Loops](validate-token-optimized-formats-in-agentic-loops.md) — A parallel input-side compression trade-off in tool-schema notation, with the same input-vs-end-to-end measurement gap.
- [Prompt Compression](prompt-compression.md) — Compressing instruction prose for the same goal at a different layer; lower accuracy risk than code minification.
- [Context Budget Allocation](context-budget-allocation.md) — Distributing the token budget across sources; minification is one lever, but not the only one.
