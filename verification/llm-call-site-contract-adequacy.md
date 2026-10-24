---
title: "Auditing LLM Call Sites Against Their Expected Contract"
term: "Call-Site Contract Audit"
description: "Across 496 LLM call sites, 82% were checked in code on both sides of the call and 5.3% met their whole contract. Audit coverage rather than presence."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - call-site contract audit
  - contract adequacy for LLM calls
  - expected versus implemented call-site contract
last_reviewed: 2026-10-21
maturity: emerging
---

# Auditing LLM Call Sites Against Their Expected Contract

> Write down what an LLM call site's reply must satisfy, then diff that against what the code checks. Counting guards answers a different question.

A call-site contract audit enumerates a system's LLM calls and ranks them by where their output goes. For the call sites that rank, it derives from the call's job what its reply must satisfy, then diffs that against the checks the code runs. The two measures separate hard. Weng et al. examined 496 LLM call sites across 40 open-source agentic systems in four languages and 13.4 MLOC, and found that "82% of call sites check in code before and after the call, yet only 5.3% satisfy their whole expected contract, and the median call site satisfies one third" ([arXiv:2610.24545v1](https://arxiv.org/abs/2610.24545v1)). The authors call that distance the study's central result.

## When the audit pays, and when to stop

Three conditions carry it. Stop at the first one that fails.

- Some output reaches control flow or execution. 48% of outputs did, and 73% of those were consumed only by the program or by another model, with no person in between.
- You can follow each output to its consumer. Consumer type is what makes the audit affordable: all nine critical-severity mechanisms the authors scored "sit at control-flow, machine-value, or execution consumers, so the consumer type (Table 2) is a cheap triage rule" ([arXiv:2610.24545v1](https://arxiv.org/abs/2610.24545v1)).
- You intend to stop at the threat chain. 63% of expected constraints were unmet, but "17% of the gaps are technically exploitable, the missing constraint lies on the threat chain for 7% (114 gaps), and 38 of the 60 mechanisms behind them trigger" ([arXiv:2610.24545v1](https://arxiv.org/abs/2610.24545v1)). Driving the 63% to zero spends the budget on gaps that sit off the threat chain.

## Record three phases and an assurance level

This is design by contract applied to a callee the caller cannot verify, and the authors build it on Hoare logic and Meyer's formulation directly ([arXiv:2610.24545v1](https://arxiv.org/abs/2610.24545v1)). The contract splits by when it applies: pre-conditions on the inputs and the decision to call at all, prompt constraints on how the request is shaped, and post-conditions on which replies the program accepts. Each constraint also carries how strongly the program holds it, on a ladder of prompt-only, code-checked, and capability-bound. The bottom rung is a request, not a guarantee: "A prompt-only constraint is stated to the model and never verified." The top rung is the one teams skip, and only 25% of the constraints that required a capability boundary had one.

One call site can need two contracts. 22% produced both a decision-relevant output and an ordinary one, so the row to audit is a call site paired with one responsibility.

## Where the gaps sit

After the call, which is where the code looks strongest. Post-conditions were 97% code-checked and still covered least: "The gap rate is 72% for post-conditions, 62% for pre-conditions, and 47% for prompt constraints" ([arXiv:2610.24545v1](https://arxiv.org/abs/2610.24545v1)). Stakes did not predict protection either, and 18 of the 23 systems with enough constraints to compare protected their decision-relevant call sites no better than the rest. No system was clean: the median missed 64% of its expected constraints, the best 33%.

## Why it works

Post-call code that recovers from a bad reply gets a feedback signal, and post-call code that judges whether a reply is admissible does not. A missing parser announces itself as a crash, so someone writes it. A well-formed but inadmissible reply flows downstream in silence, so nobody writes the allow-list. The mechanism counts show that asymmetry: "extraction and normalization (557) and error handling and retry (479) are the most common mechanisms, while allow-list and range checks appear only 114 times" ([arXiv:2610.24545v1](https://arxiv.org/abs/2610.24545v1)). A guard count reads recovery code and validation code as the same guard, so it cannot see which of the two a call site got.

The repairs are small, which is what makes the audit hours worth spending. Patches of 1 to 366 lines stopped the original exploit for all 38 mechanisms that triggered at runtime, and closed 23 completely.

## When this backfires

- Few call sites, none decision-relevant. With every output bound for a display, consumer-type triage returns nothing to rank.
- Treating the gap rate as a target. The yardstick is a judgment call and the authors say so: "The expected contract is a normative reconstruction, so other analysts might admit slightly different constraints" ([arXiv:2610.24545v1](https://arxiv.org/abs/2610.24545v1)). A 63% measured against a reconstruction is a map of where to look, not a defect count.
- Latency-bound call sites with no cheap post-condition. A meaning-level check needing a second model call serializes into the critical path. Where the check reduces to schema conformance, [semantic validation](semantic-validation-schema-valid-output.md) is the narrower move.
- Failing closed everywhere. Every checker fault then stalls legitimate work, and practitioner guidance treats fail-open against fail-closed as a per-guardrail choice, with service continuity as the reason to fail open on low-severity checks ([Splunk](https://www.splunk.com/en_us/blog/learn/implementing-ai-guardrails.html)). Find the gates that cannot deny at all instead.
- Reading an exploit rate into the result. Trigger tests used one substitute model and at most ten framings, so a mechanism is shown capable of firing, not likely to.

## Example

The audit's characteristic finding is a gate that asks the right question and then cannot act on the answer. In Gemini CLI's opt-in policy enforcer, a model is asked whether a proposed tool call complies with a security policy and must answer allow, deny, or ask the user. When the tool carries no policy, the code judges the call against an empty one. It returns ALLOW when the reply is empty, when the reply does not parse, and when the request fails: "Five of the six return paths allow the call, and only a reply that parses can deny it." Two downstream guards fail closed when their checker throws, and neither ever fires, because the enforcer has already turned the failure into an ordinary approval. The authors' summary of the shape is the finding to carry into your own audit: "the model is asked the right question, and the program does not enforce the answer" ([arXiv:2610.24545v1](https://arxiv.org/abs/2610.24545v1)).

A guard-presence audit records this call site as checked, because a check is present on both sides of the call. Ask instead which replies this code refuses, and the list holds one case: a reply that parses and says deny.

## Key Takeaways

- Guard presence and contract coverage are different measurements, and the authors treat the distance between them as their central result.
- Triage by where the output goes. Control-flow, execution, and machine-value consumers held every critical-severity mechanism the authors scored.
- Audit the call site paired with one responsibility, because 22% of call sites served a decision-relevant role and an ordinary one at once.
- Expect the gaps after the call, where 97% code coverage coexisted with a 72% gap rate.
- Record each constraint's assurance level alongside the constraint. Constraints enforced in code hold across models and a model's refusal may not.
- Stop at the threat chain. 7% of gaps sat on one, and that subset is what the fixes were validated against.

## Related

- [Semantic Validation for Schema-Valid Agent Output](semantic-validation-schema-valid-output.md) — the post-condition this audit most often finds missing, written as a standalone technique
- [Test Adequacy of LLM-Dependent Harness Code](llm-dependent-harness-test-adequacy.md) — the same adequacy question asked of the test suite rather than the contract
- [Zero Violations Is Not Evidence Your Hook Works](enforcement-liveness-evidence.md) — how to tell a gate that never needed to fire from one that cannot
- [Stochastic-Deterministic Boundary as First-Class Contract](../patterns/agent-design/stochastic-deterministic-boundary.md) — the design pattern that places a verifier at each boundary; this page asks whether the verifier covers the call site's needs
- [Restraint Rules Need External Enforcement](../instructions/restraint-rules-need-external-enforcement.md) — the prompt-only rung of the assurance ladder, argued on its own evidence
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — why a check that runs beats an instruction that asks
