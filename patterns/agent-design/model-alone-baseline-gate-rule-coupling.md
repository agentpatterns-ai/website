---
title: "Model-Alone Baseline Gate for Rule-Coupled Harnesses"
term: "Model-Alone Baseline Gate"
description: "Decide whether rules belong behind the model by running a model-alone arm first. Model strength and workload decide whether the hybrid wins on accuracy."
tags:
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - is a hybrid needed
  - model-alone arm
  - rule engine break-even
last_reviewed: 2026-11-01
maturity: emerging
---

# Model-Alone Baseline Gate for Rule-Coupled Harnesses

> Run a model-alone baseline before coupling rules; model capability and workload determine whether the hybrid improves accuracy.

A model-alone baseline gate is one measurement you take before moving policy out of the prompt and into executable rules. Run the same cases with the model applying the rules itself. Keep that arm. Adopt the coupling only when a named condition says it wins.

The comparison often goes the other way. A thirteen-pattern catalog of model-plus-rules couplings opens its own decision guide by conceding ground: "A model alone was the better or equal choice in four measured situations, and the guide says so first" ([Handschuh et al., arXiv:2610.40036v1, §10.1](https://arxiv.org/abs/2610.40036v1)).

## What makes the rules worth their cost

Six conditions justify the coupling, and any one is enough ([§10.1](https://arxiv.org/abs/2610.40036v1)):

- The decision must carry a proof or audit trail.
- The model acts, and some actions must never happen.
- The rules are many or the process is long, "from about 64 rules applied in one conversation in our runs".
- The answer aggregates over many objects.
- A weaker or cheaper model must do the work.
- The rules change, and the change must be checked first.

Name which one applies to your harness. If none does, the guide's own preference is "the simplest coupling that meets the requirement" ([§10](https://arxiv.org/abs/2610.40036v1)).

Two conditions carry numbers worth quoting at a design review ([§4.2](https://arxiv.org/abs/2610.40036v1)). On rule count, a hybrid decided all 770 runs correctly across synthetic protocols of 4 to 96 questions. The same model applying the same rules in the conversation "fell to 39 of 60 at 64 questions and 31 of 60 at 96, with 45 of its 50 errors unsafe".

On capability, "no model up to 70 billion parameters reached the criterion as a pure model, while a 9-billion model sufficed for the hybrid in single decisions".

## Why it works

Section 4.2 reports the measured decline. The model alone scored 39 of 60 at 64 questions and 31 of 60 at 96. The hybrid decided every run correctly. It does not name a cause for the decline. The gap opens at a threshold rather than everywhere.

The guarantee is inherited from the check, not from the pairing. The paper follows Kambhampati et al. (2024) that correctness comes from the sound check. A check nothing reads therefore inherits nothing ([§10.3](https://arxiv.org/abs/2610.40036v1)).

The second benefit is diagnostic rather than statistical. In a head-to-head on 14 simulated callers "a model alone was first more accurate (274 of 280 against 243 of 280)". The hybrid's errors had one cause, located in its recorded verdicts. One correction in the judge raised it to 278 of 280 ([§4.2](https://arxiv.org/abs/2610.40036v1)). The coupling bought a fixable error, not a lower error rate.

## When this backfires

- Under the threshold with a strong model. On a clean five-document review the model alone "decided 12 of 12 runs correctly, at 0.28 instead of 0.72 cents and in a third of the time", and up to 48 questions per conversation it was "not measurably less accurate than the hybrid" ([§10.1](https://arxiv.org/abs/2610.40036v1)).
- An acceptance rule the reader cannot satisfy. With an 8-billion-parameter open model, "the strict quote rule refused correct values and made extraction worse than the model alone", 45% against 60% ([§3.1](https://arxiv.org/abs/2610.40036v1)). A second group reports the same model dependence on a different engine, where one of three local models was negative on typed constraints ([arXiv:2606.27281v1](https://arxiv.org/abs/2606.27281v1), abstract).
- Cost used as the justification. The authors retire their own cost argument: "Once a provider's discount on cached input is priced, the hybrid's cost advantage in conversations disappears; at 64 and 96 questions the two cost about the same" ([§10.1](https://arxiv.org/abs/2610.40036v1)).
- Too few queries per extraction. Where rules won decisively on exhaustive lists, 10 of 10 against 0 of 6 at low effort, setup cost dominated: "43.6 cents once against 1.2 cents per question for the model alone" ([§3.1](https://arxiv.org/abs/2610.40036v1)).

## Example

This page's procedure for a hook-gate decision, with the paper's figures as the reference point:

1. Take one set of real cases for the decision, such as tool calls the gate must allow or deny.
2. Run arm A: the model reads the rule text and decides each case.
3. Run arm B: the same cases pass through the executable rules.
4. Score both arms against the same labels, and count unsafe errors apart from the rest.
5. Repeat at the rule count and model capability you expect in production.

If arm A matches arm B, keep the model-alone design and rerun the comparison when the rules grow. If arm A falls behind, or a never-happen action is in scope, adopt the coupling.

## Three failure patterns that survive review

Each of these resembles a working coupling closely enough to pass a design review, which is why the authors name them. Five are listed; these three apply directly to an agent harness.

| Failure pattern | What it looks like | What it breaks |
|---|---|---|
| Prose Policy | "The policy that decides exists only as sentences in a prompt." | Nothing tests it; no answer can show which sentence it followed |
| Decorative Check | "A check is computed and recorded, but nothing depends on it" | No acceptance rule reads the field, so the control changes no outcome |
| Silent Rule Override | "Code outside the rules changes a verdict before the rules see it" | The proof omits the step that decided |

All three are quoted from [§8](https://arxiv.org/abs/2610.40036v1). The invariant they break says a statement "is accepted on evidence the rules can check, such as a quote found in the source", and the caution beside it is to "never gate by the model's own confidence" ([§2.2 and §10.2](https://arxiv.org/abs/2610.40036v1)).

## Treat the numbers as one engine's

The patterns are transferable and the figures are not: "We drew the catalogue from one engine and its applications and then checked it against the literature", and "Most measurements use synthetic protocols and one model family" ([§11](https://arxiv.org/abs/2610.40036v1)). Use the break-even as the shape of the comparison to run on your own workload, not as a threshold to adopt.

The measured workloads are document review, intake protocols and telephone triage, not agent harnesses. The conditions still map. A hook that must refuse a denied action is the never-happen case. A gate whose verdict a reviewer must reconstruct is the audit-trail case. Both hold at any rule count, so neither waits on a break-even.

## Key Takeaways

- Keep the model-alone arm after you ship the coupling. It is how you notice that the condition which justified the rules no longer holds.
- Two of the six conditions hold at any rule count, audit trail and never-happen actions. The other four are thresholds you have to measure on your own workload.
- Fit the acceptance rule to the reader's ability to satisfy it. A strict quote rule made an 8B extractor worse than no rule at all.
- Review the rules with code. Static checks over rules "found every seeded structural fault at every size at no model cost", while model reviews "found an unreachable rule in only 2 or 3 of 10 artefacts at 64 rules" ([§3.2](https://arxiv.org/abs/2610.40036v1)).

## Related

- [Minimum-Sufficient Control Ladder: Escalate by Failure Mode](minimum-sufficient-control-ladder.md) — the same "no rung without a named failure" argument, applied across control mechanisms rather than to rule coupling alone
- [Schema-Checked Rule Extraction for Tool-Call Gates](schema-checked-rule-extraction.md) — what to verify once you have decided the rules belong and a model writes them
- [Solver-Externalized Constraint Reasoning (MaxSAT/SMT Encoding)](solver-externalized-constraint-reasoning.md) — one coupling in detail, where the external core is a solver rather than a rule engine
- [Splitting the Drift Judge from the Advisor (LivePlan)](judge-advisor-split.md) — a worked split where the always-on half runs without a model call
- [Learning Execution Guardrails from Agent Failure Traces](trace-learned-execution-guardrails.md) — where the rules come from when no policy text exists to translate

## Sources

- [Handschuh, Wiegand, Raichle — Hybrid AI Patterns: Thirteen Ways to Couple Language Models with Rules, and How to Choose Among Them (arXiv:2610.40036v1)](https://arxiv.org/abs/2610.40036v1)
- [Resource-Aware Neuro-Symbolic Reasoning for Local Small Language Models (arXiv:2606.27281v1)](https://arxiv.org/abs/2606.27281v1)
