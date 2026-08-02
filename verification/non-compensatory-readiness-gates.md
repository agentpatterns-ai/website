---
title: "Non-Compensatory Readiness Gates Before Agent Release"
term: "Non-Compensatory Readiness Gate"
description: "Gate an agent's release on several evidence axes at once, aggregated so a hard failure on one axis cannot be averaged away by strong scores on the others."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - "non-compensatory release gate"
  - "multi-axis agent readiness gate"
  - "ProofAgent Index"
last_reviewed: 2026-08-02
maturity: emerging
---

# Non-Compensatory Readiness Gates Before Agent Release

> Score an agent's release evidence on several independent axes so a failure on one cannot be averaged away by strong scores on the others.

A non-compensatory readiness gate evaluates an agent on separate axes of deployment evidence — how it behaved under adversarial testing, how well its operating context is engineered, whether required controls have evidence behind them, and whether an owner and a rollback path exist — then combines them under a rule that refuses trade-offs between axes. A named instance is the ProofAgent Index, which scores Evaluation, Context, Compliance, and Governance, aggregates them with a weighted geometric mean, and lets any of eight hard-block conditions cap the result below the release threshold outright ([arxiv:2607.27677v1](https://arxiv.org/abs/2607.27677v1)).

## When this earns its cost

The gate is worth its overhead under a narrow set of conditions. Outside them it measures paperwork.

- Someone outside the building team scores the axes. Compliance and Governance are largely attest-and-document axes, and when assessments rest on qualitative judgment rather than objective evidence, "aggregated scores obscure real risks and misstate true progress" ([CDO Magazine](https://www.cdomagazine.tech/opinion-analysis/why-data-governance-maturity-models-can-create-false-confidence-around-ai-readiness)).
- All four axes are real for your deployment. An internal coding agent with no regulator has no meaningful Compliance axis; two of the four axes then get filled in by assertion, and the aggregate reports on documentation quality instead of readiness.
- Your floors come from your own incidents. The published defect rates are trap-conditional and adversarial by design — the source paper states they "should not be interpreted as expected production failure rates" ([arxiv:2607.27677v1](https://arxiv.org/abs/2607.27677v1)).
- You gate on the per-axis floors, not on the composite number. The scalar is the least defensible part of the design; see [when this backfires](#when-this-backfires).

## The four axes

| Axis | What it scores | Evidence it consumes |
|------|----------------|----------------------|
| Evaluation | Observed behavior under adversarial and expected conditions | Task success, hallucination resistance, safety, instruction following, manipulation resistance, tool use |
| Context | Quality of the operating environment the agent runs inside | Role clarity, instructions, grounding, memory, tool schemas, guardrails, injection hardening, token efficiency |
| Compliance | Whether observed behavior and artifacts satisfy applicable controls | Control-mapped evidence, where missing evidence is not treated as satisfied evidence |
| Governance | Organizational capability around the agent | Ownership, scope, approval, monitoring, incident response, rollback, evidence retention, lifecycle control |

Source: [arxiv:2607.27677v1](https://arxiv.org/abs/2607.27677v1).

The blocking half is a fixed list, not a threshold on the mean: prohibited use, critical safety failure, hallucination resistance below a required floor, tool use breach, critical technical finding, missing mandatory compliance evidence, unresolved governance finding, or insufficient capability for the deployment risk tier ([arxiv:2607.27677v1](https://arxiv.org/abs/2607.27677v1)).

## Why it works

Non-compensation holds by construction, independently of the empirical study. A geometric mean lets a near-zero axis drag the aggregate down far harder than an arithmetic mean would, and a hard block "caps the readiness score and prevents a positive release verdict even if the aggregate score would otherwise appear acceptable" ([arxiv:2607.27677v1](https://arxiv.org/abs/2607.27677v1)).

Why capability alone answers the wrong question is measured rather than argued. Context condition moved the defect rate further than model tier did: 65.74% to 17.84% between the weakest and strongest context conditions, against 75.28% to 24.91% across weak, mid, and strong capability tiers. A mid-tier agent produced 0.54% defects under the strong context condition and 49.79% under the weak one ([arxiv:2607.27677v1](https://arxiv.org/abs/2607.27677v1)). A capability benchmark measures the axis that explained less of the variance.

## When this backfires

- The composite number is the weak part. Weights are asserted rather than fitted — "unless otherwise specified, all dimensions receive equal weight" — with no sensitivity analysis ([arxiv:2607.27677v1](https://arxiv.org/abs/2607.27677v1)). For a composite index "for which existing theory and practice provides little or no guidance to its design", meaning, interpretation, and robustness are often unclear, and what needs scrutiny is "the sensitivity of the implied rankings to changing the data and weights" ([Ravallion 2012](https://academic.oup.com/wbro/article-abstract/27/1/1/1726529)).
- Collapsing the axes may be the wrong move entirely. A synthesis of 373 evaluation studies argues that capability, behavioral robustness, and governance disclosure "should be reported as separate evidence layers rather than collapsed into a single safety score" ([arxiv:2606.30219v4](https://arxiv.org/abs/2606.30219v4)), which is the composite-index literature's dashboard alternative of monitoring the components separately ([Ravallion 2012](https://academic.oup.com/wbro/article-abstract/27/1/1/1726529)). You can adopt the blocking rules and never compute an index.
- Compliance claims leaning on behavioral results do not hold. Behavioral evaluation and red-teaming reach observable outputs only, so a Compliance axis that asserts a latent property on the strength of the Evaluation axis has an evidential chain that does not support the claim — the audit gap ([arxiv:2605.15164](https://arxiv.org/abs/2605.15164)).
- The score becomes the target. Under optimization pressure, benchmark and safety metrics improve while the properties they represent stay uncertain ([arxiv:2606.30219v4](https://arxiv.org/abs/2606.30219v4)). Once a team is measured on the index, the hard-block list becomes the test to pass and anything absent from it goes unmeasured.
- The supporting evidence is thin and vendor-authored. The reported held-out AUC of 0.98 rests on 12 configurations with one tied boundary case, no production deployment was studied, and the author declares affiliation with the company that develops both the index and its harness ([arxiv:2607.27677v1](https://arxiv.org/abs/2607.27677v1)).

## Example

The reference implementation runs the gate from a CI-shaped command and exits 0 to pass, 1 to review, 2 to block ([ProofAgent-ai/proofagent-harness](https://github.com/ProofAgent-ai/proofagent-harness)):

```bash
proof run agent.py --context-dir ./my_agent/context --turns 15
```

Its scorecard reports the axes separately before it reports any aggregate, and a blocked run shows the cap doing the work rather than the mean ([ProofAgent-ai/proofagent-harness](https://github.com/ProofAgent-ai/proofagent-harness)):

```
 PAI  49.0 / 100   F · Critical   BLOCKED
   uncapped 52.9 → capped by Critical-floor breach
```

The uncapped 52.9 is what averaging produced; the 49.0 and the BLOCKED verdict come from a floor breach on one axis. Read every scorecard that way — the release decision belongs to the floors and the block list, and the aggregate is what you put in the report.

## Key Takeaways

- Adopt the aggregation rule, not the number: refuse compensation between evidence axes and keep a hard-block list that vetoes release regardless of the aggregate.
- Score the axes independently of the team that built the agent, or the attest-and-document axes will inflate.
- Set per-axis floors from your own incident history; adversarial trap rates are not production failure rates.
- Treat the composite score as reporting, not as the gate. Its weights are asserted, and its validation is vendor-authored.

## Related

- [Evidence-Gated Lifecycle Control for Coding Agents (Proof-or-Stop)](evidence-gated-lifecycle-control.md) — gates each lifecycle transition on a fresh, source-bound receipt rather than gating a release on several axes at once.
- [Risk-Based Shipping: Review by Risk Matrix, Not by Default](risk-based-shipping.md) — decides how much oversight a change needs; this pattern decides whether the agent producing it is releasable.
- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — orders cheap evidence ahead of expensive evidence inside a repair loop.
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — the measurement gaps that keep an Evaluation axis from certifying what a Compliance axis asserts.
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the runtime counterpart to a release-time gate.
