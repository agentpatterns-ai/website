---
title: "State-Conditioned Evidence Selection for Mid-Task Retrieval"
term: "State-Conditioned Evidence Selection"
description: "Subtract the source units an agent has already read, then judge what remains as a combination rather than a ranked list. Worth the controller cost only when the next decision needs several facts together."
aliases:
  - minimal sufficient evidence recovery
  - complement retrieval
  - set-level decision-time retrieval
tags:
  - context-engineering
  - rag
  - arxiv
  - tool-agnostic
last_reviewed: 2026-09-19
maturity: emerging
---

# State-Conditioned Evidence Selection for Mid-Task Retrieval

> Subtract the evidence the agent has already read, then score what remains as a set, worth it when one decision needs several facts.

State-conditioned evidence selection scores retrieval against what an agent's next decision still lacks, given what its trajectory has already established. The observed set comes out first, and a set counts only when it covers every requirement the decision leaves open.

## When it pays

Three conditions. Check the first before the other two.

The decision needs several facts at once. SERBench's held-out split holds 500 states from 45 repositories. On the 149 needing three or more evidence groups, the set-level policy gained 14.09 points of complete-set recovery. On the 216 single-group states it gained 7.41. At a single returned item it does not separate from a similarity-ranked control: −1.40 points, with an interval of [−3.26, +1.05] ([Feng et al., arXiv:2609.20050v1, §6.2 and §6.5](https://arxiv.org/abs/2609.20050v1)).

Your harness records observations at source-unit granularity. The method builds the observed set by aligning captured tool outputs to repository units. By that rule, "a file path named in a plan therefore enters the observed set only after source confirmation" ([Feng et al., arXiv:2609.20050v1, §4.1](https://arxiv.org/abs/2609.20050v1)). So a log of tool names without outputs cannot produce that alignment.

Discovery already works. Agent Retrieval Bench reports that "logged trajectories also miss every gold file on 27-35 percent of samples" ([Qin and Xie, arXiv:2607.24882v1](https://arxiv.org/abs/2607.24882v1)). In the paper's gold-blind track, a complete requirement set was reachable for 333 of 500 states inside the shared BM25 top-1,000 pool. The lead fell from 11.60 points on recall-complete pools to 5.00 ([Feng et al., arXiv:2609.20050v1, §6.2 and §6.4](https://arxiv.org/abs/2609.20050v1)).

## How the selection works

Record which repository units the agent has read, then write the decision's open requirements as groups. Sources substitute inside a group; separate groups must all be covered, so more of one fact cannot stand in for another. Score a returned set on whether it completes every group; partial coverage gets zero credit ([Feng et al., arXiv:2609.20050v1, §3](https://arxiv.org/abs/2609.20050v1)).

The reference implementation spends three semantic calls over a fused candidate ranking: propose a jointly sufficient set, search the remaining candidates for support it lacks, then finalize 4 to 8 intact source units under a 6,144-token ceiling. Expansion and finalization both read the current selection, which lets a stage ask what is missing instead of what is similar ([Feng et al., arXiv:2609.20050v1, §5.2](https://arxiv.org/abs/2609.20050v1)).

## Why it works

Re-delivering a unit the agent has already read "costs budget without adding certificate coverage", and coverage per requirement is an indicator with all required groups multiplied together ([Feng et al., arXiv:2609.20050v1, §3](https://arxiv.org/abs/2609.20050v1)). A per-passage relevance score carries neither fact, and an ordering built from independent scores cannot express a constraint that only the whole set satisfies.

Redundancy is measurable outside this paper. ContextBench defines a per-step redundancy ratio: the share of each new retrieval that appeared in earlier steps. It records 0.487 for GPT-5 and 0.708 for Claude Sonnet 4.5 ([Li et al., arXiv:2602.05892v3, Table 5](https://arxiv.org/abs/2602.05892v3)). Work on the generator side agrees: duplicate and paraphrased documents "does not significantly improve answer correctness", while documents differing in form improve it by 17% to 47% ([Ross et al., arXiv:2608.13956v1](https://arxiv.org/abs/2608.13956v1)).

The gain sits in the policy rather than in the extra calls. A matched control with the same three calls and source ceiling, ranking by independent similarity, reaches 66.60% against 73.00% ([Feng et al., arXiv:2609.20050v1, §6.5](https://arxiv.org/abs/2609.20050v1)).

## When this backfires

- Total token spend rises. On 2,496 long-trajectory questions the answer prompt shrank 76.2% and accuracy rose 2.08 points. The controller burned 29.62K tokens per question: 33.57K online total against a baseline agent's 13.95K, 2.4 times the spend ([Feng et al., arXiv:2609.20050v1, Table 3](https://arxiv.org/abs/2609.20050v1)).
- A cheap diversity penalty recovers none of it. Maximal marginal relevance at its calibrated coefficient of 1.0 reproduced the reranker's ordering, scoring the same 61.40 and 72.40 ([Feng et al., arXiv:2609.20050v1, Table 1](https://arxiv.org/abs/2609.20050v1)).
- The downstream gain depends on the executor. Repair-localization precision improved 12.87 points under one model, [+5.39, +20.36], and 4.09 under another, [−1.89, +10.29] — an interval that includes zero ([Feng et al., arXiv:2609.20050v1, §6.3](https://arxiv.org/abs/2609.20050v1)).
- Retrieval scaffolding has a poor record. ContextBench found, across four frontier models and five coding agents, that "sophisticated agent scaffolding yields only marginal gains in context retrieval" ([Li et al., arXiv:2602.05892v3](https://arxiv.org/abs/2602.05892v3)).
- The end-to-end evidence is thin. The executed-test cohort holds 23 tasks: the method resolved 8 against the reranked baseline's 6, and every paired interval reaches zero ([Feng et al., arXiv:2609.20050v1, §6.3](https://arxiv.org/abs/2609.20050v1)).

## Example

Hold the evidence count fixed and remove one required group's alternatives from an otherwise complete set. Group recall stays at 48.27%, so close to half the requirements are still covered, and repair-localization precision falls 12.28 points under one executor and 11.11 under the other. On executed repository tests, the same removal costs three of eleven fail-to-pass resolutions and drops the condition back to the eight that BM25 already reached ([Feng et al., arXiv:2609.20050v1, §6.3](https://arxiv.org/abs/2609.20050v1)).

Partial coverage of a conjunction behaves like no coverage, and no metric averaging per-item relevance can see it.

## Key Takeaways

- Log what the agent read, at the granularity of the units you retrieve. Without that record none of this is available to you.
- State the decision's open requirements as groups, and accept a returned set only when it completes all of them.
- Expect the benefit where three or more facts must land together. A single-fact decision separates from plain ranking by nothing.
- Budget for the controller. A 76.2% smaller answer prompt here came with 2.4 times the total token spend.
- Check discovery first. Where the corpus never surfaced a required unit, no selection policy recovers anything.

## Related

- [Gate Generation on Retrieval Sufficiency, Not Model Confidence](retrieval-sufficiency-gate.md) — scores whether retrieval covers the query before generating, without subtracting what the agent already read
- [Coverage-Aware Skill Selection Under a Token Budget](coverage-aware-skill-selection.md) — the same set-level argument applied to skill loadouts, fitted from pass/fail run logs
- [Per-Object Context Allocation](per-object-context-allocation.md) — caps repeated views of one code object, the within-corpus half of the redundancy problem
- [Measuring Reacquisition Cost Under Context Compaction](reacquisition-cost-measurement.md) — measures the retrieval calls an agent spends rebuilding state it has lost
- [Exhaustive Retrieval for Listing Questions](exhaustive-retrieval-for-listing-questions.md) — the other case where ranked top-k truncates a set-shaped answer
