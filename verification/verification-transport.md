---
title: "Verification Transport: Do Verifier Judgments Survive Abstraction"
term: "Verification Transport"
description: "In four non-coding benchmarks, 20.3% to 31.0% of correct verifier judgments broke under a synthetic abstraction. Restoring the hidden events recovered 85.5% of them."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - verifier judgment transport
  - abstraction-induced verifier failure
last_reviewed: 2026-11-19
maturity: emerging
---

# Verification Transport: Do Verifier Judgments Survive Abstraction

> Among correct verifier judgments in four non-coding benchmarks, 20.3% to 31.0% broke when the same run was shown through an abstraction.

Verification transport asks whether a verifier's correct judgment of an agent run stays correct when the verifier sees the same run through a composed tool, a delegation boundary, or a compacted history. Sheshanarayana and Goli measured 31.0% failures among native-correct judgments under macro abstraction, 30.9% under delegation, and 20.3% under compaction ([Sheshanarayana and Goli, 2026](https://arxiv.org/abs/2611.18471v1), §5.1 RQ1). Restoring the hidden events recovered 85.5% of those failures and degraded 5.2% of judgments that had survived abstraction (§5.1 RQ3). The 85.5% is a share of broken verdicts, and the 5.2% is a share of verdicts that stayed correct under abstraction.

Limits:

- The abstractions are deterministic rewrites of frozen trajectories. No sub-agent ran, and compaction replaced an earlier region with a boundary marker, not a written summary (§4.1, App. B). The authors say live abstractions may differ (App. G).
- The four benchmarks are AgentProcessBench, ATBench, PlanRewardBench, and AgentDojo, with 250, 758, 441, and 754 eligible instances (§4.1). None is a coding benchmark.
- The pooled 85.5% and 5.2% come with no raw counts, because the paper sums numerators and denominators across cells (§4.2).
- It is a v1 NeurIPS 2026 workshop paper.

## Results by boundary

| Boundary | Failure rate (VTFR) | Recovered (RRR) | Degraded (RDR) |
|---|---|---|---|
| Macro abstraction | 31.0% | 87.9% | 5.3% |
| Delegation | 30.9% | 86.9% | 5.4% |
| Compaction | 20.3% | 79.8% | 4.9% |

The cells pool 7 verifier models at temperature 0 and 4 protocols (§4.1, §5.1).

## How much of the recovery is evidence

Part of it is re-running. In an ablation on AgentProcessBench and ATBench with two models, repeating verification on the same abstracted view recovered 22.5% to 33.1% of failures. Restoring ordered tool identities without arguments or observations recovered 34.0% to 53.9%. Restoring the exact events recovered 73.6% to 82.5% (§5.2). Recovery tracks the fidelity of what you restore.

## Why it works

An abstraction removes the events a verdict depends on, so the verifier decides from what is left. The authors read the recoveries as evidence that failures are "closely tied to the accessibility of execution evidence" (§5.1 RQ3). The paper isolates no model-internal cause.

## Protocols fail differently

Under macro abstraction the direct judge (V-LLM) gave 15.8% wrong verdicts and 0.7% no verdict. The evidence-gated protocol (V-EVIDENCE) gave 10.6% and 24.0%, and the deliberative protocol (V-DELIBERATIVE) 9.4% and 39.9% (App. E.1). On the binary benchmarks, V-LLM had the highest false-certification rate, 41.3% (App. E.2). VTFR counts a no-verdict as a failure, so a lower rate is not always a safer verifier (§5.1).

Reflection does not replace evidence. The deliberative second audit repaired 8.7% of wrong first-stage judgments and degraded 28.5% of correct ones (App. E.2). Letting the verifier request provenance (V-AGENTIC) scored 25.0%, 23.6%, and 18.2% VTFR against V-LLM's 16.4%, 17.3%, and 14.1% (§5.1).

## What to do

1. When a sub-agent, composite tool, or compactor sits between the run and the verifier, persist the replaced events verbatim under a boundary ID.
2. Score a sample of runs on the native trace and on the abstracted view. Count the native-correct verdicts that flip.
3. Restore the exact events for a boundary only when the verifier abstains or the check shows that boundary flipping verdicts. The authors suggest "selectively restorable provenance" (§6).
4. Use a deterministic check where one exists ([Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)).

## When this backfires

- The events are gone. Without the exact events, recovery fell to 34.0% to 53.9% in the lossy condition.
- The input is well formed but the judge misreads it. [Input Assurance Tests](judge-input-assurance-tests.md) cover that case.
- Part of the recovery may be run-to-run judge variance. Re-running recovered 22.5% to 33.1% of failures with no new evidence, and [Measure the Judge Before You Freeze a Gate on It](judge-instrument-stability-check.md) shows how to measure that variance.
- The failure is one argument whose source was cut, which [Reading a Tool-Call Judge's Rejection as an Argument Defect](../patterns/anti-patterns/derivation-gap-tool-call-judges.md) covers.

## Key Takeaways

- Report a transport check as two numbers with two denominators: failures among native-correct judgments, and recovery among failures.
- Compare protocols on wrong verdicts and no-verdict rates separately.
- Re-running the same abstracted view recovered 22.5% to 33.1% of failures in the ablation, so credit evidence only for the gain above that.

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md)
- [Input Assurance Tests for What an LLM Judge Actually Reads](judge-input-assurance-tests.md)
- [Measure the Judge Before You Freeze a Gate on It](judge-instrument-stability-check.md)
- [Reading a Tool-Call Judge's Rejection as an Argument Defect](../patterns/anti-patterns/derivation-gap-tool-call-judges.md)
- [Trajectory Projection: A Flattened View of Agent Traces](../observability/trajectory-projection.md)
- [Per-Type Retention Policy for Agent Compaction](../context-engineering/per-type-retention-under-compaction.md)
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md)
