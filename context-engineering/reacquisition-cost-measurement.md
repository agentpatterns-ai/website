---
title: "Measuring Reacquisition Cost Under Context Compaction"
term: "Reacquisition Cost"
description: "Judge a compaction setting by whether the agent spends extra retrieval calls rebuilding dropped state, because task-completion rate can stay flat while interaction cost triples."
aliases:
  - reacquisition cost measurement
  - interaction cost of context compression
  - retrieval and execution call decomposition
tags:
  - context-engineering
  - cost-performance
  - arxiv
  - tool-agnostic
last_reviewed: 2026-08-18
maturity: emerging
---

# Measuring Reacquisition Cost Under Context Compaction

> Compaction that drops state an agent can only get by asking makes it spend its turn budget asking again, while completion rate stays flat.

Reacquisition cost is the extra retrieval work an agent does to rebuild state that compaction removed. Measure it by splitting the agent's tool calls into retrieval and execution, then comparing both counts across compression settings at a fixed turn budget. In a controlled study under a 24-turn horizon, retrieval calls rose in all six model and task-regime comparisons at 5x compression while execution calls stayed approximately stable in five of the six, and completion changed significantly in none of them ([Liu, arXiv:2608.16370v1](https://arxiv.org/abs/2608.16370v1)).

## Check these conditions first

The measurement reads non-zero only where all three of these hold.

- Your agent's execution-relevant state is obtainable by asking rather than by looking again: a task graph, dependency ordering, resource holds, prior failure counts. In an ALFWorld probe where the relevant state could be re-observed through ordinary interaction actions, sliding compression produced a paired retrieval-like delta of −0.13 and no completion difference ([arXiv:2608.16370v1](https://arxiv.org/abs/2608.16370v1)).
- Your tools split cleanly into reading and acting. The decomposition attributes each call to its tool schema rather than to intent, so a tool that both reads and mutates cannot be classified.
- Tool calls are the currency you pay in. If your constraint is the provider bill on a cache-heavy coding agent, count dollars instead. Prompt-cache creation and reads dominate measured input-side cost, and token reduction correlated only weakly with cost reduction at Pearson r = 0.15 ([Weinberger and Hozez, arXiv:2607.12161v5](https://arxiv.org/abs/2607.12161v5)).

## Split the calls, then compare

Classify each tool as retrieval or execution, run paired trials at full context and at each compression setting under the same turn budget, then report all three counts together ([arXiv:2608.16370v1](https://arxiv.org/abs/2608.16370v1)). The signature to look for is a retrieval count that climbs while the execution count sits still, which says the agent is re-acquiring information rather than doing more work. A completion cell that does not move is a result about the metric, not evidence that the setting was free.

## Confirm the cause by restoring the state

Correlating severity with retrieval count is weak evidence. The controlled version injects one class of dropped state back into a compressed run and measures the difference. Restoring the queryable task state at 5x compression cut tool calls from 72.9 to 35.8, a 51% reduction at paired p = .002, and recovered completion from 66% to 80% ([arXiv:2608.16370v1](https://arxiv.org/abs/2608.16370v1)).

The same intervention tells you what is worth keeping. Selecting finely among real, task-relevant state atoms bought little over random selection. Replacing retained atoms with fabricated out-of-universe content raised retrieval 57% (p < .001) with completion statistically unchanged at p = 0.41 ([arXiv:2608.16370v1](https://arxiv.org/abs/2608.16370v1)). Whether what survives compaction is still true matters more than the ranking that chose it.

## Why it works

An agent under a bounded horizon has slack. When compaction removes state it still needs, it spends that slack on retrieval, finishes anyway, and the completion metric never registers what happened. The decomposition exposes the spend because the two call types move independently: retrieval calls account for almost all of the added interaction while execution calls remain approximately stable in five of the six comparisons ([arXiv:2608.16370v1](https://arxiv.org/abs/2608.16370v1)). Restoring the dropped state removes half that overhead, which is what makes the account causal rather than correlational. A separate team measuring provider-billed cost on Claude Code reports the same trajectory inflation from another direction, finding that compression "can alter agent trajectories through additional retrieval, diagnosis, testing, and turns, offsetting local token savings" ([arXiv:2607.12161v5](https://arxiv.org/abs/2607.12161v5)).

## When this backfires

- The environment lets the agent look again. ALFWorld showed no retrieval surge under the same compression operator, so the reacquisition signature is environment-dependent rather than an intrinsic consequence of shortening context ([arXiv:2608.16370v1](https://arxiv.org/abs/2608.16370v1)). Instrumenting there measures nothing.
- You quote the magnitudes as effect sizes. Every figure above comes from bounded, synthetic-adjacent environments under a fixed 24-turn horizon with ten seeds and three model families, and the author declines to generalize the magnitudes. Treat the shape as transferable and the numbers as local.
- You read a flat completion cell as proof of safety. The flat cells sit at the 5x comparison point, and DeepSeek showed a significant completion drop at 10x compression ([arXiv:2608.16370v1](https://arxiv.org/abs/2608.16370v1)). A non-significant completion change is a finding about the metric, not a null result about compression.
- One model's reading settles the setting for you. Qwen in the high regime showed a retrieval increase of only 2.9 calls at p = .088, the single comparison that does not survive correction ([arXiv:2608.16370v1](https://arxiv.org/abs/2608.16370v1)).

## Example

The clearest reported cell, showing what the decomposition surfaces that a completion table hides. Both columns cover the same agent and tasks under different compression severity.

| Measurement | Full context | 5x compression |
|---|---|---|
| Completion | 80% | 85% (p = 1.0) |
| Retrieval calls | 21.0 | 63.9 (p = .002) |
| Execution calls | reference | change of approximately zero |

Read alone, the completion row says the setting is safe and possibly better. The retrieval row says the agent tripled its retrieval calls to get there ([arXiv:2608.16370v1](https://arxiv.org/abs/2608.16370v1)).

## Key Takeaways

- Ask which execution-relevant state the agent would pay to fetch again, and keep that state reachable, instead of searching for a compression ratio that is safe.
- Report retrieval count, execution count, and completion in one table. A compaction change reviewed on completion alone has not been reviewed.
- Prove causation by restoring one class of dropped state into a compressed run and re-measuring, not by correlating severity with call counts.
- Check whether your environment has query-only state before building the instrumentation, because re-observable state produces no signal to read.

## Related

- [Context Compression Strategies: Offloading and Summarization](context-compression-strategies.md) — the compaction mechanisms this measurement evaluates.
- [Addressable Recall Compaction: Compact to Citations, Not Summaries](addressable-recall-compaction.md) — keeping dropped observations recoverable by ID instead of losing them.
- [Choosing a Compression Budget for Agent Control Context](control-context-compression-budget.md) — setting compression severity from environment-verified success rather than a ratio.
- [Token Reduction Mistaken for Cost Reduction](../patterns/anti-patterns/token-reduction-not-cost-reduction.md) — the same misjudgement measured in billed dollars rather than tool calls.
- [Context Budget Allocation](context-budget-allocation.md) — deciding what occupies the window before compaction has to remove any of it.
