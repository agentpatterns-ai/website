---
title: "Query-Conditioned Reuse of Retrieved Agent Trajectories"
term: "Query-Conditioned Reuse"
description: "Retrieval finds a past trajectory; reuse decides what the agent is handed. A four-field note carries the procedure without the source run's stale values."
aliases:
  - query-conditioned reuse
  - post-retrieval reuse stage
  - target-bound reuse note
tags:
  - context-engineering
  - memory
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-15
maturity: emerging
---

# Query-Conditioned Reuse of Retrieved Agent Trajectories

> Retrieval names a past trajectory; reuse decides what the agent is handed. A four-field target-bound note carries procedure without stale values.

Query-conditioned reuse replaces a retrieved trajectory with a short note written against the task the agent is about to attempt. The note records the procedure that transfers, the values the agent has to re-obtain for itself, the conditions under which the procedure applies, and the check that proved the original run finished. Retrieval and reuse are separate stages, and a pipeline that built only the first one hands the acting agent the source run's entities, paths, and identifiers for a target where they no longer resolve ([arxiv 2608.12847v1](https://arxiv.org/abs/2608.12847v1)).

## When this is worth building

The measured advantage concentrates in two situations. Check your traces before adding a distillation pass.

Long source traces are one. Measured as utility over a no-memory baseline, injecting the full trajectory falls from +18.4 points on traces of 5 to 10 actions to +2.9 points past 35 actions, while the note holds from +21.9 to +13.2 ([arxiv 2608.12847v1](https://arxiv.org/abs/2608.12847v1)).

Large binding shift is the other. When the target's entities, paths, dates, and identifiers have moved away from the source run's, full-trajectory injection retains +2.2 points against the note's +20.1. With no binding shift the two sit at +26.9 and +29.6.

Cost points the same way: 9.4k online tokens against 18.4k for direct injection, and 16.7 API calls against 21.9.

## The four fields

| Field | What it records |
|-------|-----------------|
| Workflow invariant | "Tool order, decision rule, and prior validation step" |
| Bindings to re-obtain | "Entities, paths, dates, users, record identifiers, and parameters" |
| Applicability conditions | "Source preconditions, constraints, and branch conditions" |
| Verification guardrail | "The source check that established completion" |

Those definitions are the paper's own, and the note is target-bound rather than a general summary of the source run, so one trajectory yields different notes for different tasks ([arxiv 2608.12847v1](https://arxiv.org/abs/2608.12847v1)). The split between the first two fields is where the technique lives: the procedure is copied forward, and every value it touched becomes an obligation to look that value up again.

## Why it works

Trace length is where the gap opens, and the paper is careful about why. Full-trajectory support retains 15.8% of its short-trace utility on the longest traces against 60.3% for the note ([arxiv 2608.12847v1](https://arxiv.org/abs/2608.12847v1)). Length is not all that separates those groups: no-memory success falls from 55.2% on short traces to 18.9% on very long ones, so they "differ substantially in task difficulty" too. §5.6 reads the result as "an association under the registered construction rather than a causal estimate of length alone".

Stale binding is the half the paper does state as a mechanism. A trajectory carries the source run's values inline, so the agent copies them into a target where they have moved: under large binding shift the stale-binding error rate is 46.9% for full-trajectory injection against 10.9% for the note. The paper frames this as a reduction, not a cure: the method "does not make binding shift disappear; it reduces the rate at which stale source values displace current-task evidence" (§5.7). Separating the procedure from the values it used is what the four fields buy.

The direction holds outside this paper. A study of feedback placement in multi-turn agents reports that "grounded, action-relevant feedback at meaningful points consistently outperforms indiscriminate use of longer or richer context" ([arxiv 2605.19447v1](https://arxiv.org/abs/2605.19447v1)), and Memp finds that trajectories distilled into step-by-step instructions and script-like abstractions stay useful when moved to a weaker model ([arxiv 2508.06433v4](https://arxiv.org/abs/2508.06433v4)).

## Where the remaining headroom is

Retrieval was close to saturated in this setup. Summary reranking selected a reusable memory for 94.8% of targets, putting end-task success within 1.8 points of an oracle reusable selector ([arxiv 2608.12847v1](https://arxiv.org/abs/2608.12847v1)). Closing that selection gap entirely is worth 1.8 points against that oracle, which is why the paper puts the remaining loss elsewhere and why reuse earns its own stage and metric. That balance is a property of the three benchmarks measured, not a general claim about retrieval quality.

## When this backfires

Short traces in a stable environment are the clearest case against it. You buy the margin above at the price of a second inference pass, and the note is a lossy artifact nobody can audit against the material it discarded.

Invalidated source experience is worse than aged experience. TEPA measured append-only memory at 0.210 under full reversal against 0.309 for a no-memory baseline ([arxiv 2608.07429v2](https://arxiv.org/abs/2608.07429v2)), so reusing superseded experience scored below reusing nothing. Applicability conditions are written from the source at authoring time, and a condition nobody thought to record is never checked at reuse time.

Agents also read the re-obtain instruction and use the stale value anyway. "Memory-augmented agents can know that a user's stored state is outdated and still plan around the old value" ([arxiv 2608.01619v1](https://arxiv.org/abs/2608.01619v1)), and "relying solely on symbolic instructions can introduce a text-action disconnect, frequently failing to activate the internal representations necessary for correct task execution" ([arxiv 2606.29824v1](https://arxiv.org/abs/2606.29824v1)). Make the verification guardrail a check your harness runs rather than a sentence the agent is asked to honor.

Then there is everything the evaluation never entered: 2,391 instances across WebArena, WorkArena, and AppWorld, all with successful source trajectories, one selected memory per target, and one model (DeepSeek-V4-Pro) doing every rollout, ranking, and execution ([arxiv 2608.12847v1](https://arxiv.org/abs/2608.12847v1)). Partial-failure notes, conflicting notes, and a second model family are untested.

## Key Takeaways

- Instrument retrieval and reuse as two stages with two metrics. A good ranker feeding a bad handoff is indistinguishable from a bad ranker.
- Write the note against the target task rather than storing one general summary per source run.
- Keep concrete values out of the note and record what has to be re-obtained in their place.
- Make the verification guardrail something the harness executes. An instruction to re-check is a request the agent can decline.
- Skip the note where traces are short and bindings are stable; the measured gap there is under three points.

## Related

- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md) — the retrieval half of the pipeline this technique sits downstream of
- [Memory Synthesis: Extracting Lessons from Execution Logs](../patterns/agent-design/memory-synthesis-execution-logs.md) — distilling execution traces at write time, where query-conditioned reuse distills at read time
- [Addressable Recall Compaction](addressable-recall-compaction.md) — keeping the raw record recoverable by ID instead of compressing it away
- [Evolving Playbooks](evolving-playbooks.md) — accumulating strategy deltas rather than rewriting a monolithic instruction block
- [PEEK: Orientation Cache for Recurring-Context Agents](peek-orientation-cache.md) — a constant-sized orientation artifact, distinguished from trajectory replay
