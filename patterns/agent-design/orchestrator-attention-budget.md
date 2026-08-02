---
title: "The Orchestrator's Attention Budget: Delegating to Protect Context"
term: "Orchestrator Attention Budget"
description: "Justify a sub-agent by what it keeps out of the orchestrator's context rather than by time saved — imported tokens charge attention on every remaining turn."
tags:
  - agent-design
  - context-engineering
  - multi-agent
  - tool-agnostic
aliases:
  - the orchestrator's tax
  - orchestrator context pollution
  - cognitive locality partitioning
last_reviewed: 2026-07-31
maturity: emerging
---

# The Orchestrator's Attention Budget: Delegating to Protect Context

> Delegate to keep work out of the orchestrator's context, not to run it faster — imported tokens charge attention rent on every remaining turn.

## When this framing applies

The attention argument holds under three conditions.

- The session has many turns left. This cost is rent, charged over the turns that follow. Delegating near the end leaves little to charge, so the roughly 15x token multiplier [Anthropic measured](https://www.anthropic.com/engineering/multi-agent-research-system) dominates.
- The subtasks are genuinely independent. Anthropic excludes domains "that require all agents to share the same context or involve many dependencies between agents".
- The orchestrator respects the boundary it created. Isolation the main thread later reverses buys nothing.

Otherwise a single-threaded agent with compaction is safer. Cognition argues the stronger case: decision-making "ends up being too dispersed and context isn't able to be shared thoroughly enough between the agents" ([Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)).

## Two costs that behave differently

Garg puts the asymmetry as "Tokens are spent once. Context shapes every decision that follows" ([The Orchestrator's Tax, 16 July 2026](https://martinfowler.com/articles/orchestrator-tax.html)). Anything left in the window is re-read every subsequent turn, whether or not it still matters.

Dilution is therefore a different failure from overflow. Overflow is a capacity problem — [the window fills before the orchestrator can reason over what its workers returned](agent-composition-patterns.md) — which compaction or reference pointers fix. Dilution needs no shortage of room: it starts at the first irrelevant token, and a larger window only gives the noise more space ([Garg](https://martinfowler.com/articles/orchestrator-tax.html)).

## The orchestrator undoes its own isolation

Garg's session shows the main thread can undo the boundary it created. An offhand "check on the agents" prompt made the status tool import a background agent's full raw transcript — twice. The payload was "tens of thousands of tokens of JSONL, intermediate reasoning, and tool output". Four workers had run in isolation; two status checks undid it.

Answer a status question from what the orchestrator already knows, and never fetch a full transcript to answer a lightweight question. A worker should return the distilled result, not the trace — see [what to return from sub-agents](../multi-agent/sub-agents-fan-out.md).

## Partition by shared mental model

Splitting by task rather than by the knowledge each task needs makes workers rebuild the same understanding. Two of Garg's four workers touched different files in the same response pipeline, and each reconstructed its architecture and testing conventions before starting. He calls the corrective cognitive locality: tasks needing the same mental model should stay together, and overlapping file ownership signals consolidation.

This differs from [cohesion-aware task partitioning](../multi-agent/cohesion-aware-task-partitioning.md), which cuts the static code-dependency graph to minimize context transfer. Cognitive locality asks what understanding a task requires, binding files the dependency graph leaves unconnected.

## Why it works

The mechanism is dilution, not exhaustion. LLMs have an "attention budget" they draw on when parsing large volumes of context ([Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). Every new token "depletes this budget by some amount", because for n tokens there are n² pairwise relationships to spread across.

Chroma evaluated 18 models on tasks "deliberately controlled to isolate the impact of context length alone," and found performance degrades as input grows ([Context Rot](https://research.trychroma.com/context-rot)). Degradation tracks input length itself, not task difficulty or a full window.

A sub-agent is the admission control. It spends tens of thousands of tokens in a context that is discarded, returning "a condensed, distilled summary of its work (often 1,000-2,000 tokens)" ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

## When this backfires

- Dependency-dense work. Isolated workers act on assumptions nobody stated, and conflicts surface at integration: "Actions carry implicit decisions, and conflicting decisions carry bad results" ([Cognition](https://cognition.ai/blog/dont-build-multi-agents)).
- Lossy summaries. A worker that drops detail the orchestrator later needs forces a re-fetch, reimporting the tokens isolation excluded.
- Concurrent repository-wide operations. One of Garg's agents ran `git stash` and `git stash pop` while siblings wrote in the same tree. Nothing broke, but he notes such operations "become much harder to justify the moment multiple writers are active at once".
- Governance overcorrection. Garg's first instinct, a confirm-before-spawn gate, solved a problem he had no evidence of. His replacement heuristic: ask whether a competent orchestrator would decide correctly knowing the one missing fact. If so, state the fact, not a procedure.
- Unmeasured ranking. Garg calls the claim that polling cost more than the duplication tax "the orchestrator grading its own mistake," with no per-call token accounting. Treat that ordering as a hypothesis.

## Example

Standing instruction files are where this becomes enforceable, because the orchestrator reloads them every session. That is also why Garg compressed the incident into four rules rather than a policy document. Each states a fact to check rather than a procedure to run:

```markdown
1. Prefer two to four agents in one wave. If the orchestrator wants five or
   more, it should first ask whether tasks sharing files or conventions
   ought to be merged.
2. Do not poll background agents for status when the answer can be given
   from what is already known. Do not fetch a full transcript to answer a
   lightweight question.
3. Do not allow repository-wide git operations inside concurrent agent prompts.
4. Treat overlapping file ownership as a consolidation signal, not a cue to
   spawn more agents.
```

Garg calibrated the two-to-four threshold against Claude Sonnet 5 and one workload, and warns against reading it as a constant: treat the numbers as a sample to re-derive, and the four questions as the transferable part.

## Key Takeaways

- Justify a sub-agent by what it keeps out of the orchestrator's context; parallelism is a secondary benefit that does not by itself pay the cost.
- Tokens are spent once, context charges rent every turn — that asymmetry, not the token bill, is what makes imported worker output expensive.
- Attention dilution begins well before the window fills, so a larger context window does not fix it ([Chroma](https://research.trychroma.com/context-rot)).
- The orchestrator can breach the isolation it bought: status polls that import worker transcripts undo the delegation that paid for it.
- Partition by the mental model a task needs, not by the task list — overlapping ownership is a signal to consolidate.
- The framing is conditional: dependency-dense work and short sessions favor a single thread at roughly 15x fewer tokens ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)).

## Related

- [Sub-Agents for Fan-Out Research and Context Isolation](../multi-agent/sub-agents-fan-out.md)
- [Agent Composition Patterns for Multi-Agent Workflows](agent-composition-patterns.md)
- [Context Budget Allocation: Spending Every Token Wisely](../../context-engineering/context-budget-allocation.md)
- [Cohesion-Aware Task Partitioning for Multi-Agent Coding](../multi-agent/cohesion-aware-task-partitioning.md)
- [The Delegation Decision: When to Use an Agent vs Do It Yourself](delegation-decision.md)
