---
title: "Recover the Six Measurement Choices Behind an Attack Success Rate"
term: "ASR Comparability Audit"
description: "Attack success rate is a family of metrics set by six design choices, and across 259 agentic-security papers 65.3% report neither a variance estimate nor repeated runs."
tags:
  - testing-verification
  - evals
  - security
  - tool-agnostic
  - arxiv
aliases:
  - ASR comparability audit
  - attack success rate measurement axes
  - six axes of ASR divergence
last_reviewed: 2026-09-24
maturity: emerging
---

# Recover the Six Measurement Choices Behind an Attack Success Rate

> An attack success rate is set by six choices the paper usually leaves out, and four of them can reverse a ranking.

Before you carry an attack success rate from one paper into a comparison with another, recover the six measurement choices that produced it. Pathade et al. argue that ASR "is not a single quantity but a family of metrics parameterized by six design choices", and their meta-analysis of 259 agentic-security papers found that most papers state few of them ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1)). Two numbers set by different choices are two different quantities. Subtract them and you get a gap that describes the measurement rather than the defense.

## The condition this applies under

This is a rule about numbers lifted across harnesses. It does not apply to two results from one run of one harness, where the unit, the task set, the oracle, and the run count are held constant by construction. [AgentDojo](https://arxiv.org/abs/2406.13352v3) is the common example, a shared environment carrying "97 realistic tasks" and "629 security test cases" in which attacks and defenses are measured side by side.

Two limits on the evidence, which the authors state themselves. The corpus-wide 65.3% comes from automatic coding and "should be read as an automated estimate consistent with the sampled one, not as an independent confirmation of it"; hand-coding a random sample of 50 papers gives 58.0%, with a 95% Wilson interval of 44.2 to 70.6. And the ranking-inversion results below are analytical: "we report no empirical ranking inversion; that experiment is the natural next step" ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1)).

## The six choices

| Axis | What varies | Can reorder a ranking |
|---|---|---|
| A1 Unit of analysis | Injection attempts, tasks, or trajectories as the denominator | Yes |
| A2 Success oracle | String match, LLM judge, environment state, human adjudication | Yes |
| A3 Trials and non-determinism | Runs per configuration, temperature, top-p, seeds | No |
| A4 Attacker adaptivity | A static template set, or an adaptive attacker under a query budget | Yes |
| A5 Attacker knowledge of the defense | Unaware, aware a defense is present, or holding its prompt, classifier, or policy | Yes |
| A6 Binarization of partial success | How partial completion and refused-then-retried trajectories score | No |

All six choices shift ASR. The four marked yes are the ones the paper argues shift it in a system-dependent way; it declines to extend that stronger claim to A3 and A6 ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1)).

## How often each is stated

Table II covers all 259 papers, dated 2025-02-27 to 2026-09-17 ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1)).

| Practice | Share of papers |
|---|---|
| Neither variance nor repeated runs | 65.3% |
| Any decoding information (temperature, greedy, or seed) | 30.9% |
| Uses an LLM judge (lower bound) | 24.7% |
| Of those, validated against human labels | 29.7% |
| Adaptive attacker considered | 30.5% |
| Attack budget stated | 10.8% |
| Attacker knowledge of the defense stated | 16.2% |
| Partial success addressed | 2.3% |
| Benign-task utility reported | 37.8% |

Detector agreement with the adjudicator on the hand-coded sample was kappa 0.75 overall ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1)).

## Running the audit

Read the methods section for the six axes and write down what you find, blanks included. Then apply the resolution check. A 100-instance benchmark "cannot resolve differences below roughly 18 percentage points at conventional power", two defenses truly separated by 5 points "are ranked backwards about 21% of the time", and at a 2-point separation "about 38% of the time, which is close to a coin flip" ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1)). The abstract puts the minimum detectable difference at 100 instances at 18.2 percentage points. Those figures assume a binomial model with independent units, 80% power at alpha 0.05, computed at ASR 30% and 60%.

Blanks are the normal result, and they are a finding rather than a failure of the audit. When the unit or the oracle goes unstated, no amount of rereading recovers the comparison. Say so and stop. The paper then becomes a source of attack ideas for a harness you control, not a rank.

For evaluations you run yourself, the paper's ten-item checklist is the reporting contract: publish each of the six axes, an interval estimate, benign-task utility under the same defense, and no claim of an improvement smaller than the minimum detectable difference ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1)).

## Why it works

A measurement choice that shifted every system's ASR by the same amount would be harmless, because a reader consumes the ordering and a constant offset cancels in the difference. The paper's claim is that four of the six do not behave that way. For "the unit of analysis (A1), the oracle (A2), attacker adaptivity (A4) and defense-awareness (A5) but not for trial count (A3) or partial-success binarization (A6)", the authors hold that "the shift is system-dependent, so the induced ranking is not invariant to the measurement choice" ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1)). A system-dependent shift survives the subtraction that was supposed to remove it.

The unit-of-analysis case shows the size. Take a benchmark whose tasks each carry k injection points, against an attacker that reliably succeeds at exactly one injection per task. That attacker scores 1/k per-injection and 1.0 per-task, a factor of k between two readings of identical behavior ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1), §III-A). Neither denominator is wrong. Per-injection estimates how reliable an attack primitive is; per-task estimates how likely a session is compromised, which is usually the security question, since one success is enough.

## When this backfires

- Both numbers came from one harness. In-harness comparison pins the unit, the task set, and the oracle already, so the audit costs reading time and changes no decision.
- The gap dwarfs the benchmark's resolution. A defense taking ASR from 90% to 5% on 100 instances clears the 18.2-point minimum by a wide margin, and no plausible axis difference reverses it. Demanding the full ten items first is a gate that cannot change the answer.
- The paper states none of the axes. At the rates in the table above the audit often terminates in unknowns, and the only exit is re-running, which needs artifacts most papers do not release.
- You apply the checklist to your own evals on every change. Repeated runs mean repeated agent trajectories with live tool calls, and that spend buys nothing until a decision turns on a small gap.
- You treat the checklist as settled practice. The authors do not: "the checklist is proposed, not validated. We have not shown that adopting it improves cross-paper comparability, only that each item corresponds to a gap we measured" ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1)).

One objection deserves naming, because it is the stronger one. The adjacent adversarial-robustness literature locates the problem in the evaluation itself rather than in how it is written up. Carlini et al. open on the claim that "Correctly evaluating defenses against adversarial examples has proven to be extremely difficult", cite defenses "that withstand adaptive attacks" as the thing few papers achieve, and spend the paper on methodological foundations and best practices ([arXiv:1902.06705v2](https://arxiv.org/abs/1902.06705v2)). Read that way, the attacker-specification item carries most of the weight and the other nine are bookkeeping. The audit still earns its place for a reader who cannot re-run anything.

## Key Takeaways

- Six choices set an ASR, and four of them (unit, oracle, adaptivity, defense-awareness) shift it system-dependently, so they reorder rankings rather than offset them ([arXiv:2609.25173v1](https://arxiv.org/abs/2609.25173v1)).
- Expect the axes to be missing. Across 259 papers, 65.3% report neither variance nor repeated runs by automated coding, 58.0% in a hand-coded sample of 50.
- On a 100-instance benchmark, treat any claimed gap under 18.2 points as unresolved at conventional power.
- An unrecoverable axis ends the comparison. Take the attack ideas and measure the ranking in a harness you control.

## Related

- [Audit the Noise Floor Before Trusting a Benchmark Gap](benchmark-noise-floor-audit.md) — the rerun and prompt-rewording floors a gap has to clear once two numbers are comparable at all.
- [Seed-Variance Reporting and Measurable-Range Eval Design](seed-variance-reporting.md) — what to publish for the trials axis, and when a cell sits too near a bound to carry a verdict.
- [Measure the Judge Before You Freeze a Gate on It](judge-instrument-stability-check.md) — the oracle axis, for the case where the oracle is an LLM judge.
- [Action-Graded Severity for Agent Red-Team Outcomes](action-graded-severity-red-team-outcomes.md) — a graded harm scale in place of the binary outcome that the partial-success axis collapses.
- [Covert Success Rate for Indirect Prompt Injection](../security/covert-success-rate-injection.md) — one further split of the same metric, on whether a successful injection left a trace in the agent's reply.
