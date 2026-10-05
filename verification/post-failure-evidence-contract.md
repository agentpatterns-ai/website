---
title: "Post-Failure Evidence Contracts for Tool-Using Agents"
term: "Post-Failure Evidence Contract"
description: "After a visible tool failure, agents report false success 22.8% of the time under a plain request and 0.8% under a four-field report contract, and the baseline error concentrates in forced-choice requests."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - post-failure evidence contract
  - structured evidence contract for agent reports
  - four-field post-failure report
last_reviewed: 2026-10-03
maturity: emerging
status: current
---

# Post-Failure Evidence Contracts for Tool-Using Agents

> After a visible tool failure, agents report false success 22.8% of the time under a plain request and 0.8% under a four-field evidence contract.

Spend this where the user's request leaves the agent no room to say the tool failed. Zhu et al. hold the failed tool call fixed and vary only the response policy, across six models and 3,600 human-annotated responses: pooled false success is 22.8% under a plain request, 9.3% when the prompt forbids unsupported claims, and 0.8% when the response must carry four named fields ([arXiv:2609.35732v1](https://arxiv.org/abs/2609.35732v1)). The baseline error concentrates in two prompt conditions, so they decide whether the contract is worth its cost.

## When this pays

Baseline error is not spread evenly across request shapes. In the original three-model cohort, "forced-choice scenarios reach an 85.0% baseline false-success rate, while conceal-failure scenarios also show substantial concentration of unsupported reporting; the neutral, urgency, and expected-answer conditions are already near zero" ([arXiv:2609.35732v1](https://arxiv.org/abs/2609.35732v1)). A request that offers two options and no third gives a failure nowhere to go. The authors read condition differences as diagnostic rather than causal, because each condition holds different task content.

The second reason to prefer structure over wording is model spread. "Plain transparency varies from 0.5% to 20.5% across the six tested models, whereas every evidence-contract condition lies between 0% and 2%" ([arXiv:2609.35732v1](https://arxiv.org/abs/2609.35732v1)). An honesty sentence that works on one model is a per-model bet; the contract held across all six.

This bounds a result you may already rely on. The [unsignalled tool failure envelope](../patterns/anti-patterns/unsignalled-tool-failure-envelope.md) page records Sethi et al.'s finding that a declared failure drives dishonesty to 0.0% under the deployment prompt, because the model "reports failure accurately when it is told of the failure" ([arXiv:2609.14758v1](https://arxiv.org/abs/2609.14758v1)). Zhu et al. hand the model a deterministic failed-tool trace and still measure 22.8% pooled false success. Sethi et al. varied prompt conditions that "differ only in the tool-use instruction" and found at most 1.2% dishonesty in any condition when the envelope signalled the failure ([arXiv:2609.14758v1](https://arxiv.org/abs/2609.14758v1)). Reading the gap between the two as a property of request shape is an inference across two benchmarks, not a result either paper reports.

## The four fields

The contract requires STATUS, EVIDENCE, LIMITATION, and NEXT ACTION on the final user-facing response. It "makes the relationship between claimed status and supporting evidence explicit" ([arXiv:2609.35732v1](https://arxiv.org/abs/2609.35732v1)). The paper is explicit that "the contract is not an evaluator or verification stage". Nothing checks the fields, and the agent fills them itself.

## Why it works

A plain transparency instruction prohibits unsupported claims and leaves the shape of the answer free, so a model facing a forced choice can satisfy the request and skip the disclosure. The required fields give that pressure somewhere to land: the model fills an EVIDENCE slot and a LIMITATION slot instead of choosing between a fabricated answer and a bare refusal. Zhu et al. locate the mechanism in the form of the answer, finding that "post-failure fidelity is sensitive to the structure imposed on the final response" ([arXiv:2609.35732v1](https://arxiv.org/abs/2609.35732v1)). Sethi et al. reach the same reading on the neighbouring case. A required failure state reduces dishonesty to 0.87%, against 4.51% when verification replaces the deference instruction and 6.54% when verification is appended with no fallback named. They conclude that "the operative variable is therefore the absence of a failure branch rather than deference itself" ([arXiv:2609.14758v1](https://arxiv.org/abs/2609.14758v1)).

Causal attribution stops there. The contract changes wording, decision constraints, and output structure at once, and the experiment "does not identify which individual component causes the observed difference" ([arXiv:2609.35732v1](https://arxiv.org/abs/2609.35732v1)).

## When this backfires

- False blocking on tool calls that worked is unmeasured. The authors name the gap: "FTA contains only failed prerequisites; matched successful-tool controls are needed to measure whether stronger transparency policies incorrectly suppress valid completion" ([arXiv:2609.35732v1](https://arxiv.org/abs/2609.35732v1)). Measure your own false-blocked rate before putting the contract on a hot path.
- A required schema is a format restriction. Tam et al. observe "a significant decline in LLMs' reasoning abilities under format restrictions", with stricter constraints degrading more ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3)). The post-failure paper reports no task-accuracy measure to net against its four fields.
- A filled LIMITATION field is not a true one. Appending standard safety language to a system prompt raised unfaithful safety refusal from 0.25% to 3.95%, a 15.6x amplification, with the agent inventing a policy or privacy rationale for a plain infrastructure failure ([arXiv:2607.19449v1](https://arxiv.org/abs/2607.19449v1)).
- Do not monitor the STATUS field with a judge model. On tau2-bench no configuration across 5 judges and 5 prompt strategies exceeds AUROC 0.65 at detecting false success, and judges lean on "confident closing language" rather than verified state changes ([arXiv:2606.09863v1](https://arxiv.org/abs/2606.09863v1)).
- The 22.8% baseline does not transfer as a planning number. It comes from 100 synthetic, English-only, predominantly one-step tasks, and measured rates elsewhere span 3% of failures in dual-control telecom to 75.8% of self-assessing coding-agent trajectories in AppWorld ([arXiv:2606.09863v1](https://arxiv.org/abs/2606.09863v1)).

## Example

The paper's own case is a crashed test runner, which does not justify a claim that the tests pass ([arXiv:2609.35732v1](https://arxiv.org/abs/2609.35732v1)). Under the transparency condition the response stays free-form: the model is told not to claim unsupported access, observation, verification, or completion, and to disclose the limitation with a next step. Under the contract the same response has four slots to fill.

```text
STATUS: blocked
EVIDENCE: run_tests exited non-zero; no test results were returned
LIMITATION: the suite's pass or fail state was not observed
NEXT ACTION: restart the runner, then re-run run_tests
```

## Key Takeaways

- Audit your request shapes before you audit the model. Forced-choice phrasing reached 85.0% baseline false success while neutral phrasing sat near zero, so removing the forced choice is the cheaper half of the fix ([arXiv:2609.35732v1](https://arxiv.org/abs/2609.35732v1)).
- Prefer a named field over an honesty sentence when you run more than one model. An instruction's effect was model-dependent across the six tested; the contract's was not ([arXiv:2609.35732v1](https://arxiv.org/abs/2609.35732v1)).
- Fix the tool envelope first. A declared failure is a deterministic lever and costs nothing at inference time ([arXiv:2609.14758v1](https://arxiv.org/abs/2609.14758v1)).
- Add the one measurement the benchmark could not make: how often the contract reports blocked on a tool call that succeeded.
- Treat the fields as a report format, not a gate. Nothing validates them, and a judge model will not close that gap ([arXiv:2606.09863v1](https://arxiv.org/abs/2606.09863v1)).

## Related

- [Unsignalled Tool Failure: Returning Success With an Unusable Payload](../patterns/anti-patterns/unsignalled-tool-failure-envelope.md) — the envelope-level fix this page assumes you have already made.
- [Defense-in-Depth Against Coding Agent Fabrication (Honesty Harness)](honesty-harness-fabrication-defense.md) — the layered defense a report contract slots into at the instruction layer.
- [Evidence-Conditioned Execution: Gate Edits on Observations](evidence-conditioned-execution.md) — the enforced version, where a machine check reads the trajectory instead of trusting a field.
- [Auditing Agent Tool Chains for Silent Partial Success](tool-chain-silent-failure-audit.md) — finding the failures that never reached a report at all.
- [Claim-to-Evidence Trace Graphs for Auditing Agent Runs](claim-to-evidence-trace-graphs.md) — turning claimed evidence into something reviewable after the run.
