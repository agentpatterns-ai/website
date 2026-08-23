---
title: "Failure-Aware Observability for Multi-Agent LLM Systems"
term: "Failure-Aware Observability"
description: "A six-signal trace taxonomy — tool reliability, execution recovery, orchestration loops, evidence availability, information change, budget pressure — that maps recurring multi-agent failure modes to online instrumentation so wasted runs are diagnosed mid-trajectory instead of at final-answer eval."
tags:
  - observability
  - multi-agent
  - tool-agnostic
  - arxiv
aliases:
  - failure-aware trace instrumentation
  - multi-agent failure signal taxonomy
  - early diagnosis of wasted agent computation
last_reviewed: 2026-06-13
maturity: emerging
---

# Failure-Aware Observability for Multi-Agent LLM Systems

> A six-signal trace taxonomy that maps recurring multi-agent failure modes to online observability so wasted runs are caught mid-trajectory, not at final-answer eval.

Multi-agent LLM systems consume tokens, tool calls, retries, and code-execution attempts before producing an answer. Final-answer evaluation reveals the endpoint but rarely the moment the trajectory stopped making recoverable progress. Failure-aware observability instruments a fixed set of online trace signals whose patterns precede final-answer failure, so postmortem grading becomes mid-run diagnosis ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)).

The framework is taxonomic, not algorithmic. The contribution is the failure-mode-to-signal map, not a stopping rule. Downstream policy — early stop, nudge, escalation, model swap — belongs to the harness.

## The six signals

The paper defines six online trace signals, each tied to a distinct failure mechanism ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)):

| Failure mode | Observable signal | What it diagnoses |
|---|---|---|
| Tool instability | Tool error rate, retry summaries, latency | Tool calls consume budget without returning usable state |
| Execution failure | Execution success rate, compile/import/timeout classes | Code execution fails without recovery |
| Repeated action loop | Repeated action keys, ABAB cycle labels, cache hits | Computation without strategy change |
| Low information gain | New URLs, extracted fact count, low-gain streaks | Search/retrieval no longer adds task-relevant state |
| Evidence failure | Evidence-present rate, citation consistency, answer-evidence similarity, sentence support | Final answer is unsupported by trajectory artifacts |
| Budget waste | Tokens, tool calls, budget pressure, post-warning remaining budget | Computation budget is being exhausted; intervention window is closing |

Two metrics carry concrete formulas, and cost is a weighted sum ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)):

- Tool reliability: `ToolErr(r) = N_err(r) / N_tool(r)` — the error fraction of tool results over a run.
- Evidence support: `Support_τ(r) = (1/|S_a|) Σ 𝟙[max cos(f(s), f(c)) ≥ τ]`, τ = 0.65 — the fraction of answer sentences whose embedding has cosine similarity ≥ 0.65 with at least one trajectory citation.
- Cost: `C_r = αT_r + βH_r + γR_r + δX_r` over tokens, tool calls, retries, and execution attempts. The coefficients stay open so the harness weights by its own marginal cost.

## Why it works

Recurring failure modes leave trace-level fingerprints before final-answer failure: tool instability as a rising error ratio, an orchestration loop as identical action keys, low information gain as a streak of calls returning no new URLs or facts, evidence failure as low answer-citation cosine similarity — all readable before the grader sees the answer. The paper's GAIA evaluation confirms them empirically: across 165 traces, failure rates were 41% at Level 1 (22/53), 38% at Level 2 (33/86), and 46% at Level 3 (12/26), with mean token use rising from 8,152 to 16,389 ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)). Concurrent work reinforces the mechanism: full execution traces improve failure-attribution accuracy by up to 76% over partial-observation baselines ([Chen et al., arxiv 2604.22708](https://arxiv.org/abs/2604.22708v1)).

## How it differs from single-signal stopping

Single-signal mechanisms — iteration caps, edit counters, cost ceilings — answer "when do I stop?". This framework answers "why is this run failing, and why now?". [Circuit Breakers for Agent Loops](circuit-breakers.md) enumerate stopping conditions and [Loop Detection](loop-detection.md) instruments one of them; failure-aware observability sits a layer up, mapping six failure classes to six signal classes. One cost ceiling can trip for six reasons, and knowing which separates swapping the model from re-prompting with explicit evidence requirements from aborting to retry with a smaller goal.

## When this backfires

Four conditions where instrumentation cost outweighs return:

1. Single-agent or short-trajectory workloads. The taxonomy targets multi-agent systems where 16k-token trajectories with consecutive tool failures are the failure surface ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)); a solo harness under ten tool calls per task surfaces loops and budget overrun directly. [Loop Detection](loop-detection.md) plus [Circuit Breakers for Agent Loops](circuit-breakers.md) cover this regime.

2. No trace store or intervention path. Without a way to act on the signals — mid-run pause, nudge injection, early-stop — they reduce to postmortem instrumentation no faster than final-answer eval. An [agent-trace data layer](agent-trace-data-layer.md) is the prerequisite.

3. Highly variable evidence-support baselines. The cosine-similarity-at-0.65 threshold assumes answer-claim alignment is a tractable similarity signal ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)). Non-text ground truth (numeric, image, code) or claims chained across many sentences misclassify legitimate runs as evidence failures; re-baselining τ per task class adds calibration overhead.

4. System-level alternatives cover the loop case. [AgentSight](https://arxiv.org/pdf/2508.02736) detects resource-wasting reasoning loops and multi-agent bottlenecks at the syscall layer via eBPF, with no per-harness instrumentation. When loops dominate over evidence failure or low information gain, that can carry more signal per instrumentation hour.

The steelman: one hard budget cap plus one repetition detector. Six signals create six false-positive surfaces, and correlation — loops imply low information gain — means redundant capacity; until the trace store and intervention tooling act on six dimensions independently, two well-tuned signals beat six noisy ones.

## Example

A multi-agent research harness coordinates a planner, two retrieval agents, and a synthesis agent on a GAIA Level 2 task. It wires the six signals: `ToolErr(r)` per retrieval agent over a rolling window of 10 calls; a repeated-action-key counter on `(agent_id, tool, normalized-arg)`; new-URL count per retrieval call (low-gain proxy); `Support_τ(r)` on each candidate answer; and `C_r` weighted by the harness's own per-token and per-tool costs.

At step 18 of 30, retrieval-agent-2 has `ToolErr = 0.7` over the last 10 calls, `(retrieval-2, web_search, "GAIA-paper authors")` has fired four times, and new-URL count is zero for the last six calls. The orchestrator nudges the planner to reassign that evidence requirement to retrieval-agent-1 with a reformulated query, and the run completes within budget. Without the signals it sees only a token count climbing and a step counter advancing — both look like progress — and the failure surfaces only when synthesis emits an answer with `Support_τ` below threshold, after the budget is spent.

## Key Takeaways

- Six trace signals — tool reliability, execution recovery, orchestration loops, evidence availability, information change, budget pressure — map recurring multi-agent failure modes to online observability ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)).
- It is a diagnostic taxonomy, not a stopping rule: it tells the harness *why* a run is failing while budget remains to intervene.
- The empirical basis is 165 GAIA validation traces with 38–46% per-level failure rates and mean token use rising from 8,152 to 16,389 ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)).
- Without a trace store and an intervention path, the signals reduce to postmortem instrumentation no faster than final-answer eval.
- For single-agent harnesses and short trajectories, two signals (loops + budget) dominate six.

## Related

- [Loop Detection](loop-detection.md) — single-signal counterpart focused on repeated file edits; the orchestration-loop signal in this taxonomy generalizes that mechanism across multi-agent action keys.
- [Circuit Breakers for Agent Loops](circuit-breakers.md) — stopping-policy enumeration that consumes signals like the ones this framework produces.
- [Trajectory Pre-Filter for Failure Diagnosis (TrajAudit)](trajectory-prefilter-failure-diagnosis.md) — complementary technique for *localizing* failure once it has occurred; this page is about detecting it while the run is live.
- [Agent-Trace Data Layer: Storage for Hours-Long Traces](agent-trace-data-layer.md) — the storage tier the framework presupposes; without it, the signals lag the run.
- [Observability Feedback Loop: A 7-Step Debug Runbook](observability-feedback-loop.md) — the broader debugging runbook into which failure-aware signals plug as the early-detection step.
