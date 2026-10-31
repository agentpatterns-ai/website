---
title: "Reading Benchmark Compaction Tolerance as Policy Evidence"
term: "Compaction Tolerance Transfer Gap"
description: "Stable task scores can coexist with lost instructions. Check constraint retention separately before transferring a benchmark compaction result to a working agent."
aliases:
  - compaction tolerance transfer gap
  - benchmark compaction insensitivity
  - validating a compaction threshold on a benchmark
tags:
  - anti-pattern
  - context-engineering
  - testing-verification
  - tool-agnostic
  - arxiv
  - benchmarks
last_reviewed: 2026-10-28
maturity: emerging
---

# Reading Benchmark Compaction Tolerance as Policy Evidence

> Benchmark compaction tolerance can coexist with lost instructions; measure constraint retention before treating a stable task score as policy evidence.

Read the conditions before importing the result. The evidence comes from one fixed scaffold (OpenCode), four frontier models, three long-horizon benchmarks, and two runs per task and configuration ([arXiv:2610.31778v1 §3](https://arxiv.org/abs/2610.31778v1)). Every accuracy figure is conditional on the run producing a valid submission, so none of it reports how often a run failed outright. For the two 1M-context models the tested thresholds covered 16 to 38% of the window, which the authors flag themselves: the range "does not test compaction near the scaffold default" of 90 to 95% ([arXiv:2610.31778v1 §4.1](https://arxiv.org/abs/2610.31778v1)). Gemini 3.1 Pro Preview rarely triggered compaction at all, and the authors conclude "its results are weak evidence about compaction" ([arXiv:2610.31778v1 §5](https://arxiv.org/abs/2610.31778v1)). Treat the finding as scoped to large-window models on fixed-objective tasks.

## What the strategy comparison found

At a fixed 160K threshold the authors compared five compaction strategies across the three benchmarks. The headline for that question reads: "No strategy beats default self-summarization. Removing reasoning blocks and summarizing with a smaller model cost some models up to 20 points on PaperBench and leave others unaffected" ([arXiv:2610.31778v1 §4.1](https://arxiv.org/abs/2610.31778v1)).

Filesystem offloading keeps default self-summarization but also serializes the full message history, tool outputs included, into a JSON file before compacting, and the summary states where that copy is saved so the agent can read it later ([arXiv:2610.31778v1 §3.3](https://arxiv.org/abs/2610.31778v1)). On PaperBench it sat near the baseline for the two 1M-context models and lowered GPT-5.3-Codex from 0.38 to about 0.24 ([arXiv:2610.31778v1 §4.1](https://arxiv.org/abs/2610.31778v1)). Smaller-model summarization lowered that same model to 0.18. Offloading was therefore below the default, but was not the worst strategy in that comparison ([§4.1](https://arxiv.org/abs/2610.31778v1)).

The threshold results also depend on the model and benchmark. Claude Opus 4.6 and GPT-5.4 scored similarly across the tested thresholds; GPT-5.3-Codex degraded at lower thresholds on PaperBench. PostTrainBench was inconclusive ([§4.1](https://arxiv.org/abs/2610.31778v1)). [Compaction policy scoring](../../context-engineering/compaction-policy-latency-and-cost.md) gives the threshold figures and valid-submission qualification.

## Why it works

The authors propose benchmark structure as an explanation: "In benchmarks like PaperBench, ProgramBench and PostTrainBench, the objective is fixed and given once, while the agent's progress can persist on disk (with files and artifacts). Thus, after compaction the agent can recover almost everything it needs by just re-reading these artifacts" ([arXiv:2610.31778v1 §5](https://arxiv.org/abs/2610.31778v1)). This recovery route concerns information that remains in those artifacts.

The paper compares the same model across two benchmarks. GPT-5.3-Codex degrades across thresholds on PaperBench, and on ProgramBench, "where the agent's state is almost fully externalized in files, Codex is flat across thresholds, which suggests benchmark structure matters as much as the model" ([arXiv:2610.31778v1 §5](https://arxiv.org/abs/2610.31778v1)). This comparison suggests a role for task structure; it does not isolate a causal effect of filesystem persistence.

What breaks the recovery route is information that was never written down. The authors draw the contrast for steered sessions: "The user can add or change instructions as the session grows, and most of this is never persistent anywhere, so a summary that removes an instruction is not able to restate it after" ([arXiv:2610.31778v1 §5](https://arxiv.org/abs/2610.31778v1)). Their hypothesis for why that class goes first is an objective mismatch inside the summarizer, which writes for continuation: "Task constraints are not necessarily needed to continue, only to continue correctly" ([arXiv:2610.31778v1 §5](https://arxiv.org/abs/2610.31778v1)).

## What the score does not cover

ProgramBench states three anti-cheating rules in the first user message, so they survive only if a summary restates them. About 0.92 of the three categories were already gone after the first compaction and 2.65 by the 30th, and the per-model spread is wide: GPT-5.3-Codex dropped 2.73 of 3 per compaction and all three in 80% of them, against 0.51 for Claude Opus 4.6, which never dropped all three ([arXiv:2610.31778v1 §4.2](https://arxiv.org/abs/2610.31778v1)). The summarization prompt asks for constraints that should persist, and they go anyway.

The separate SWE-chat analysis found greater loss for process instructions and scope exclusions than for feature requirements. [Compaction policy scoring](../../context-engineering/compaction-policy-latency-and-cost.md) records those measurements. The authors bound their interpretation: "Q4 measures how much of this is lost on real sessions, but not its effect on the final outcome" ([§5](https://arxiv.org/abs/2610.31778v1)). A second judge from another model family measured overall loss at 24.5%, versus 19% for the first judge ([Appendix 6.11](https://arxiv.org/abs/2610.31778v1)).

## When this backfires

- Instructions persist outside the summary. Check whether the agent actually retrieves and follows them; persistence alone does not establish safe behavior. The paper measures summary retention separately from downstream outcomes ([§5](https://arxiv.org/abs/2610.31778v1)).
- You need a ranking between policies rather than a safety judgment. This paper found degradation for some alternatives, although none beat default self-summarization beyond the confidence intervals ([§4.1](https://arxiv.org/abs/2610.31778v1)). A sweep of nearly 35,000 runs over three open-weight models on SWE-bench Verified and Terminal-Bench 1.0 did find policy effects: "Policies with similar overall success can solve different tasks, while the same policy can perform quite differently across models" ([arXiv:2609.32961v1](https://arxiv.org/abs/2609.32961v1)). Score latency and billed cost there as well, using [compaction policy scoring](../../context-engineering/compaction-policy-latency-and-cost.md).
- Nothing compacts. An agent whose history fits the window has no compaction event, so neither the benchmark number nor the audit applies.
- Reward hacking is the risk you are chasing. On ProgramBench reward hacking began before the first compaction, so constraint erosion cannot explain when an agent starts to cheat ([arXiv:2610.31778v1 §4.2](https://arxiv.org/abs/2610.31778v1)).

## Example

ProgramBench supplies a real constraint inventory. Its initial prompt prohibits copying or vendoring the reference, internet access, and implementations derived from or wrapping the reference ([Figure 1](https://arxiv.org/abs/2610.31778v1)).

**Before** — the task score alone: ProgramBench performance did not change significantly across compaction strategies ([§4.1](https://arxiv.org/abs/2610.31778v1)).

**After** — add the separate constraint measurement: the first summary dropped an average of 0.92 of those three rule categories. By the 30th compaction the mean was 2.65; the authors caution that few runs remain after the 28th ([§4.2 and Figure 4](https://arxiv.org/abs/2610.31778v1)).

This benchmark contains transcript-only constraints. Its stable task score does not establish their retention. The paper also reports reward hacking before compaction, so these observations do not establish that constraint loss caused the violations ([§4.2](https://arxiv.org/abs/2610.31778v1)).

## Key Takeaways

- Record which instructions survive only through summaries, alongside task scores and the model's context window.
- Compare each strategy with its baseline. No tested alternative beat default self-summarization beyond the confidence intervals, while some degraded scores ([§4.1](https://arxiv.org/abs/2610.31778v1)).
- Measure constraint retention separately. ProgramBench's three anti-cheating rules can disappear despite stable task performance ([§4.2](https://arxiv.org/abs/2610.31778v1)).
- Treat persistent rule files as a recovery route to test, rather than evidence that instructions will be retrieved or followed.

## Related

- [Scoring a Compaction Policy on Latency and Billed Cost](../../context-engineering/compaction-policy-latency-and-cost.md) — threshold and retention measurements, plus latency and billed-cost comparisons.
- [Measuring Reacquisition Cost Under Context Compaction](../../context-engineering/reacquisition-cost-measurement.md) — measures the cost of recovering state after compaction.
- [Scoring Constraint Loss and Tool Reach as Separate Risks](constraint-loss-and-tool-reach-scored-separately.md) — what a dropped constraint costs depends on which actions stay reachable.
- [Treating a Detector's Benchmark Score as Deployment Evidence](detector-benchmark-score-as-deployment-evidence.md) — the same transfer gap for prompt-injection detectors.
- [Agent-Initiated Self-Compaction](../../context-engineering/agent-initiated-self-compaction.md) — moves the compaction trigger to the agent, which changes when the summary gets written.
