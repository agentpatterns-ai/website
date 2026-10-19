---
title: "Per-Stage Model Assignment in a Generate-Repair-Refine Pipeline"
term: "Per-Stage Model Assignment"
description: "Profile each candidate model separately at generation, repair, and refinement, because the best generator is often not the best repairer — and check the gap is worth the second contract."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
  - model-routing
aliases:
  - stage-wise model routing
  - cross-model debugging
  - per-stage LLM selection
last_reviewed: 2026-10-18
maturity: emerging
---

# Per-Stage Model Assignment in a Generate-Repair-Refine Pipeline

> Your best generator may be your worst repairer, so profile each pipeline stage. Expect the correctness gain to narrow as models strengthen.

Measure each candidate model once per pipeline stage rather than once overall. Generation accuracy and repair accuracy are separate numbers, and they reorder. On Python, the model with the highest generation pass@1 placed last at repair: "In debugging, Claude achieves the highest fix@1 for both languages (Python: 97.56%; Rust: 80.49%), while GPT-4o, the top Python generator, ranks last among debuggers" ([Chen et al., arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)). A single leaderboard rank gives you one of those two placements and hides the other.

## When this pays

The condition is how much headroom your strongest single model has left. PerfOrch, the system behind this evidence, was re-run with all five candidate models replaced by current-generation successors, and most of the correctness advantage went away: "On eight of the ten multilingual columns, its margin is at most 0.61 pp, and six are ties." The authors name the reason — "The strongest baselines are near the correctness ceiling on the other languages, limiting the possible absolute gains" ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)).

Three conditions survived that upgrade.

- Hard task distributions. Where no model was near saturation the margins held: 10.97 percentage points on BigCodeBench and 8.70 on APPS, both over MapCoder as the strongest baseline ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)).
- Low-resource languages. Rust kept a 2.44 pp lead on HumanEval-X and 7.14 pp on EffiBench-X, while six of the ten multilingual columns tied.
- Execution-performance work rather than correctness. This metric did not flatten: "Unlike correctness, refinement does not saturate with the stronger pool." Execution-time optimization coverage ran 31.85% to 89.70% against 23.60% to 61.59% for the best single-model configuration per column ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)).

Outside those three, one current frontier model running the whole pipeline is the baseline to beat, and on saturated work it is not beaten by enough to notice.

## Build the profile first

The profile is the artifact; the pipeline just reads it. Build the table first: pass rate per model, per stage, per language. The reversal is not a Python curiosity. It recurred at five models across five languages and ten algorithmic categories, where "a model's ranking can change substantially between stages": "Grok 3 leads Java generation in most categories" and "ranks fourth or fifth in Java fixing for the same categories" ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)).

Two design choices transfer. Candidates are tried in rank order and the search stops at the first one that clears the stage, which cost 7% to 40% of querying every model at every stage. Advancement is decided by execution, not by a model's opinion: "a debugging candidate must pass the tests, and a refinement candidate must preserve correctness and exceed the improvement threshold for the target performance metric" ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)). Five candidates was the knee, since "adding more models beyond five incurs extra cost with minimal return on correctness".

## Why it works

Writing code and critiquing code are separable abilities, and the repair stage depends on the second one. Olausson et al. tested this by setting a weaker model as the generator and a separate stronger model as the feedback source. The result: "on APPS, both Code Llama and GPT-3.5 now beat out both their baselines (dark green, gray) and their respective self-repair modes (purple, red)", read as evidence that "self-repair is bottlenecked by the model's ability to provide feedback on its own code" ([Olausson et al., arXiv:2306.09896v5](https://arxiv.org/abs/2306.09896v5)). Swapping the model at the repair stage replaces the critic instead of re-asking the author.

The difference comes partly from training exposure. PerfOrch's authors cite Baltaji et al. identifying Rust as a low-resource language whose limited public code constrains model performance, "consistent with the lower generation and debugging rates we observe for Rust than for Python". They also cite Ding et al.'s SemCoder, trained to reason about execution behavior, as evidence that the training objective shapes repair ability in particular ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)).

The two findings agree on the split and disagree about its shape. Olausson's is a ladder, where a stronger critic helps a weaker author. PerfOrch's Python profile is not monotonic, since GPT-4o held the top generation score and the bottom repair score at once. Treat "stronger model for the hard stage" as the weaker version of the pattern and the measured table as the real one.

## When this backfires

- You cannot run tests at every stage. The pattern needs an oracle at each hop: "PerfOrch requires test cases to validate generated code at each pipeline stage" ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)). Without one, nothing accepts or rejects a candidate and the rank order becomes a guess.
- The work is repository-scale rather than function-level. The category vocabulary that drives routing did not transfer. On a SWE-Bench Pro pilot, "the ten algorithmic categories leave 60.0–66.7% without an applicable label", and the authors place inference-time labeling and category-aware routing there in future work ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)).
- Low volume against profile upkeep. The paper's maintenance plan is annual full re-profiling with cheaper updates between runs, and those updates read optimistic: incremental estimates "exceed the fully measured pass@1 values by 1.70–4.51 pp because they carry forward predecessor successes without testing for regressions" ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)). A stale table routes confidently to the wrong model.
- A task mix with many unsolvable items. Retries on work that never lands dominate the bill. On BigCodeBench, "The 223 unsolved tasks exhaust the generate–debug retry budget. These tasks average 13,442 tokens each, compared with 1,112 for the 917 solved tasks" ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)).
- The repair stage may not earn its budget at all. This is the strongest objection and PerfOrch never tests it, because its baselines are fixed-model pipelines and two other multi-agent systems, never matched-token resampling from its own best generator. Olausson et al. found that "when the cost of carrying out repair is taken into account, performance gains are often modest, vary a lot between subsets of the data, and are sometimes not present at all", and that the competition is worst where repair looks best: "stronger models have higher repair success rates on easier tasks—but at the same time, the chance of getting a correct program by resampling also increases the easier a task is" ([arXiv:2306.09896v5](https://arxiv.org/abs/2306.09896v5)). See [Blind Resampling Over Self-Repair](../../loop-engineering/blind-resampling-over-self-repair.md).
- Every added model is an added boundary, and the general prior runs against adding them. Cemri et al. report that "Despite enthusiasm for Multi-Agent LLM Systems (MAS), their performance gains on popular benchmarks are often minimal" ([arXiv:2503.13657v3](https://arxiv.org/abs/2503.13657v3)).

## Example

HumanEval-X Python/130 asks for the terms of a Tribonacci-like sequence in which odd-indexed terms depend on the next even term. Claude generated code that mishandled index 0 and referenced a value not yet computed. Asked to repair its own output, Claude fixed the base case and broke the recurrence relation instead, and the paper's reading is that "The two Claude attempts stay within the same family of partial fixes." Routed to Grok, the same faulty code got a different strategy: pre-allocate the array, compute the even terms, then fill the odd terms by calculating the next even value on the fly. That passed ([arXiv:2510.01379v3](https://arxiv.org/abs/2510.01379v3)).

The authors generalize it as a change of strategy rather than a change of skill: "In both debugging examples, the original model retains an incorrect solution strategy, while switching models produces a successful repair."

Note what the example does not show. Claude held the highest Python repair score at language level, and the profile still routed this problem elsewhere, because routing reads the per-category row. Ranking first on the language average did not let it repair its own output here.

## Key Takeaways

- Build the per-stage table before you build the pipeline. Two numbers per model, generation and repair, on your own language and task mix.
- Read your table's spread against what the one published trial bought. Six ties and a 0.61 pp ceiling was its result on saturated work with a current model pool.
- Spend the effort on the execution-performance stage first. It was the one metric that did not flatten when every candidate model was replaced.
- No test oracle at a stage means no routing at that stage. The rank order is only worth what the execution check behind it is worth.
- Price the alternative before adding the second vendor: same tokens, more samples, one model.
- Re-profile on a schedule and treat the cheap incremental update as an optimistic estimate, not a measurement.

## Related

- [Role Orchestration on a Single Model](role-orchestration-single-model.md) — the same generate-repair-refine role split run on one frozen model under a hardware constraint; it names heterogeneous per-role routing as the stronger baseline, and this page is the evidence for that claim.
- [Model Rankings Reverse Across Agent Harnesses](model-rankings-reverse-across-harnesses.md) — rankings also reorder when the harness changes, so a stage profile measured under one harness may not hold under another.
- [Blind Resampling Over Self-Repair](../../loop-engineering/blind-resampling-over-self-repair.md) — the matched-budget case for skipping the repair stage rather than reassigning it.
- [Per-Task Agent Routing Across Coding Harnesses](per-task-agent-routing.md) — routes whole tasks on measured cost and failure profile, where this page routes stages inside one task.
- [Routing Break-Even: When a Cheaper Model Actually Pays](routing-break-even.md) — the arithmetic for whether a routing decision covers its own overhead.
