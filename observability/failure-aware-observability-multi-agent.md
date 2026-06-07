---
title: "Failure-Aware Observability for Multi-Agent LLM Systems"
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
last_reviewed: 2026-06-02
---

# Failure-Aware Observability for Multi-Agent LLM Systems

> A six-signal trace taxonomy that maps recurring multi-agent failure modes to online observability so wasted runs are caught mid-trajectory, not at final-answer eval.

Multi-agent LLM systems burn tokens, tool calls, retries, and code-execution attempts before producing an answer. Final-answer evaluation reveals the endpoint but rarely the moment the trajectory stopped making recoverable progress. Failure-aware observability instruments a fixed set of online trace signals whose patterns precede final-answer failure — turning postmortem grading into mid-run diagnosis ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)).

The framework is taxonomic, not algorithmic: the contribution is the *failure-mode to signal* map, not a stopping rule. Downstream policy — early stop, nudge, escalation, model swap — is the harness's call.

## The Six Signals

The paper defines six online trace signals, each tied to a distinct failure mechanism ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)):

| Failure mode | Observable signal | What it diagnoses |
|---|---|---|
| Tool instability | Tool error rate, retry summaries, latency | Tool calls consume budget without returning usable state |
| Execution failure | Execution success rate, compile/import/timeout classes | Code execution fails without recovery |
| Repeated action loop | Repeated action keys, ABAB cycle labels, cache hits | Computation without strategy change |
| Low information gain | New URLs, extracted fact count, low-gain streaks | Search/retrieval no longer adds task-relevant state |
| Evidence failure | Evidence-present rate, citation consistency, answer-evidence similarity, sentence support | Final answer is unsupported by trajectory artefacts |
| Budget waste | Tokens, tool calls, budget pressure, post-warning remaining budget | Computation budget is being exhausted; intervention window is closing |

Two of the metrics carry concrete formulas in the paper:

- **Tool reliability**: `ToolErr(r) = N_err(r) / N_tool(r)` — error fraction of tool results over a run.
- **Evidence support**: `Support_τ(r) = (1/|S_a|) Σ 𝟙[max cos(f(s), f(c)) ≥ τ]`, with τ = 0.65 — fraction of answer sentences whose embedding has cosine similarity ≥ 0.65 with at least one trajectory citation ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)).

Cost is a weighted sum `C_r = αT_r + βH_r + γR_r + δX_r` over tokens, tool calls, retries, and execution attempts; the paper leaves coefficients un-fixed so the harness can weight by its own marginal cost structure ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)).

## Why It Works

Recurring multi-agent failure modes leave trace-level fingerprints before final-answer failure. Tool instability manifests as a rising error ratio. An orchestration loop produces identical action keys across consecutive steps. Low information gain shows up as a streak of tool calls returning no new URLs or facts. Evidence failure is detectable from cosine similarity between answer sentences and trajectory citations — before the eval grader reads the answer. The paper's GAIA evaluation establishes these fingerprints empirically: across 165 validation traces, failure rates were 41% at Level 1 (22/53), 38% at Level 2 (33/86), and 46% at Level 3 (12/26), with mean token use rising from 8,152 to 16,389 across levels ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)). The framework's job is to make the fingerprints legible while the run still has budget left to course-correct.

Concurrent work reinforces the mechanism: full execution traces improve failure-attribution accuracy by up to 76% over partial-observation baselines ([Zhang et al., arxiv 2604.22708](https://arxiv.org/abs/2604.22708)).

## How It Differs From Single-Signal Stopping

Single-signal mechanisms — iteration caps, edit counters, cost ceilings — answer "when do I stop?". The six-signal framework answers "*why* is this run failing, *now*?". [Circuit Breakers for Agent Loops](circuit-breakers.md) enumerate stopping conditions; [Loop Detection](loop-detection.md) instruments one of them. Failure-aware observability sits a layer up — six classes of failure to six classes of signal, so the harness's policy has structured diagnostic input rather than a single binary trip. In a multi-agent setting, one cost ceiling can trip for six reasons; knowing which is the difference between swapping the model, re-prompting with explicit evidence requirements, and aborting to retry with a smaller goal.

## When This Backfires

Four conditions where the instrumentation cost outweighs the return:

1. **Single-agent or short-trajectory workloads.** The taxonomy was designed for multi-agent, tool-using systems where 16k-token trajectories with consecutive tool failures are the failure surface ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)). A solo-agent harness running fewer than ten tool calls per task surfaces loops and budget overrun at the surface level. [Loop Detection](loop-detection.md) plus [Circuit Breakers for Agent Loops](circuit-breakers.md) cover this regime.

2. **No trace store or intervention path.** The framework produces signals. If the harness has no path to act on them — no mid-run pause, no nudge injection, no early-stop — the signals reduce to postmortem instrumentation no faster than final-answer eval. An [agent-trace data layer](agent-trace-data-layer.md) is the prerequisite.

3. **Highly variable evidence-support baselines.** The cosine-similarity-at-0.65 threshold assumes answer-claim alignment is a tractable similarity signal ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)). Tasks whose ground-truth evidence is non-text (numeric, image, code) or whose claims chain across many sentences misclassify legitimate runs as evidence failures; re-baselining τ per task class adds calibration overhead.

4. **System-level alternatives cover the loop case.** [AgentSight](https://arxiv.org/pdf/2508.02736) detects resource-wasting reasoning loops and multi-agent bottlenecks at the syscall layer via eBPF, with no per-harness instrumentation. When the dominant failure mode is loops rather than evidence failure or low information gain, system-level observation can carry more signal per instrumentation hour.

A steelman of the opposite recommendation: one hard budget cap and one repetition detector. Six signals create six false-positive surfaces; signal correlation — loops imply low information gain — means redundant capacity. Until the trace store and intervention tooling can act on six dimensions independently, two well-tuned signals dominate six noisy ones. This is the right start for small, single-agent harnesses; the full taxonomy earns its complexity once multi-agent failure modes diverge enough that single signals merge passing and failing runs.

## Example

A multi-agent research harness coordinates a planner, two retrieval agents, and a synthesis agent on a GAIA Level 2 task. The harness wires the six signals:

- `ToolErr(r)` per retrieval agent over a rolling window of 10 calls.
- Repeated-action-key counter on `(agent_id, tool, normalised-arg)`.
- New-URL count per retrieval call (low-information-gain proxy).
- `Support_τ(r)` computed when synthesis emits a candidate answer.
- `C_r` weighted by the harness's own per-token and per-tool costs.

At step 18 of 30, retrieval-agent-2 has `ToolErr = 0.7` over the last 10 calls, the repeated-action-key counter shows `(retrieval-2, web_search, "GAIA-paper authors")` firing four times, and new-URL count is zero for the last six calls. The orchestrator nudges the planner: "retrieval-agent-2 is producing low-gain repeats on `GAIA-paper authors`; reassign to retrieval-agent-1 with a reformulated query or skip this evidence requirement". The run completes within budget.

Without the signals, the orchestrator sees a token count climbing and a step counter advancing — both look like progress. The failure becomes visible only when synthesis emits an answer with `Support_τ` below threshold, after the budget is already spent.

## Key Takeaways

- The six trace signals — tool reliability, execution recovery, orchestration loops, evidence availability, information change, budget pressure — map recurring multi-agent failure modes to online observability ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)).
- The framework is a diagnostic taxonomy, not a stopping rule: it tells the harness *why* a run is failing while there is still budget left to intervene.
- The empirical basis is 165 GAIA validation traces with 38–46% per-level failure rates and mean token use rising from 8,152 to 16,389 across difficulty levels ([Li et al., arxiv 2606.01365](https://arxiv.org/abs/2606.01365)).
- The framework presupposes a trace store and an intervention path; without them, the signals reduce to postmortem instrumentation that is no faster than final-answer eval.
- Two signals (loops + budget) dominate six for single-agent harnesses and small trajectories; the full taxonomy earns its complexity once multi-agent failure modes diverge enough that single signals merge passing and failing runs.

## Related

- [Loop Detection](loop-detection.md) — single-signal counterpart focused on repeated file edits; the orchestration-loop signal in this taxonomy generalises that mechanism across multi-agent action keys.
- [Circuit Breakers for Agent Loops](circuit-breakers.md) — stopping-policy enumeration that consumes signals like the ones this framework produces.
- [Trajectory Pre-Filter for Failure Diagnosis (TrajAudit)](trajectory-prefilter-failure-diagnosis.md) — complementary technique for *localising* failure once it has occurred; this page is about detecting it while the run is live.
- [Agent-Trace Data Layer: Storage for Hours-Long Traces](agent-trace-data-layer.md) — the storage tier the framework presupposes; without it, the signals lag the run.
- [Observability Feedback Loop: A 7-Step Debug Runbook](observability-feedback-loop.md) — the broader debugging runbook into which failure-aware signals plug as the early-detection step.
