---
title: "Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses"
term: "Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses"
description: "Test out-of-band prompt-injection defenses with defense-aware adaptive attacks before trusting their numbers — static benchmarks like AgentDojo overstate robustness, the same way they did for in-band defenses that adaptive attacks broke at 90%+ ASR."
tags:
  - security
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - adaptive evaluation of agent defenses
  - defense-aware prompt injection evaluation
  - out-of-band defense red-teaming
last_reviewed: 2026-06-29
maturity: emerging
status: current
---

# Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses

> Out-of-band defenses look strong on AgentDojo, but adaptive attacks broke twelve in-band defenses at 90%+ ASR — test before you trust the numbers.

Adaptive evaluation is the discipline of attacking a prompt-injection defense with an adversary that knows the defense exists and optimizes against it, instead of replaying a fixed attack distribution the defense was tuned against. The out-of-band class — CaMeL, FIDES, Progent, RTBAS, FORGE — reports near-elimination of attacks on AgentDojo, but only Progent has been tested under an adaptive attack at all, and the rest carry numbers chosen before the defense existed [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479v1)]. The lesson the field already paid for: twelve in-band defenses that reported near-zero attack success collapsed above 90% under defense-aware adaptive attacks [Source: [Nasr, Carlini et al., 2025](https://arxiv.org/abs/2510.09023v1)].

## The in-band collapse is the empirical precedent

Static benchmarks measure how a defense performs against a fixed attack distribution chosen before the defense was built. They cannot measure how it performs against an attacker who reads the defense paper and optimizes against the specific enforcement mechanism. The gap between the two is the difference between near-zero and 90%+ for in-band defenses [Source: [Nasr, Carlini et al., 2025](https://arxiv.org/abs/2510.09023v1)].

The twelve in-band defenses Nasr, Carlini et al. broke spanned the standard taxonomy — instruction-hierarchy training, spotlighting, sandwiching, attention-based detectors, structured-format constraints. Under gradient-based, reinforcement-learning, random-search, and human red-teaming adaptive attacks, prompting-based defenses collapsed to 95–99% attack success and training-based methods to 96–100% [Source: [Nasr, Carlini et al., 2025](https://arxiv.org/abs/2510.09023v1)]. A parallel evaluation of eight AgentDojo-specific defenses reached the same verdict under adaptive attack [Source: [Zhan et al., 2025](https://aclanthology.org/2025.findings-naacl.395/)]. [AutoDojo](https://arxiv.org/abs/2606.15057v2) reaches the same conclusion against indirect-prompt-injection defenses on AgentDojo specifically — a cheap black-box adaptive attack raises ASR well above static baselines against nearly every evaluated defense, including a filter that admitted 28% of adaptive attacks overall and 64% on action-open tasks despite blocking all static ones [Source: [Ma et al., 2026](https://arxiv.org/abs/2606.15057v2)]. Out-of-band defenses have not yet faced this test.

## Why out-of-band defenses are a more promising target

Out-of-band defenses move enforcement outside the model. Where in-band defenses train the model to refuse, systems like [CaMeL](camel-control-data-flow-injection.md), FIDES, Progent, RTBAS, and FORGE wrap the agent in a deterministic policy layer that decides whether an action is permitted regardless of what the model was talked into [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479)]. The class instantiates classical integrity protection — Biba's Low-Water-Mark and Star Integrity, plus Anderson's reference monitor — realized through five different enforcement mechanisms (capability labels, taint with confidentiality, symbolic per-call rules, IFC screeners, Datalog policies) [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479) §2-3]. The shared structure is what makes the class a coherent evaluation target.

## What an adaptive evaluation must cover

A defense-aware evaluation goes beyond replaying AgentDojo's `important_instructions` baseline. Five components are load-bearing:

1. A defense-aware attack template, not a generic one. The attacker designs the injection around the specific enforcement mechanism — for a capability-labeled interpreter, attacks that target label propagation; for a policy-LLM, attacks that target the policy generator [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479) §11].
2. The policy-LLM component as a high-value target. Out-of-band defenses that include a model in the enforcement path — Progent's policy generator is the canonical example — keep one in-band failure mode inside an otherwise deterministic system. The Buchwald authors target this directly [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479) §11].
3. In-the-loop tasks where the agent must act on untrusted content. Action mediation works when the agent ignores injected actions; it does not work when the workflow ("read this email; if meeting request, add to calendar") requires the agent to act on attacker-controlled content. A principled account of which in-the-loop tasks are securable does not yet exist [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479) §8.3].
4. Side channels and implicit flows. [CaMeL excludes them from its guarantee](camel-control-data-flow-injection.md) by design — indirect dependencies, attacker-triggered exceptions, and timing channels escape taint-label propagation. Adaptive evaluation surfaces these where the defense paper conceded the gap [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479) §8.5].
5. Text-to-text harms the action layer cannot reach. Mediation protects actions, not payloads — a poisoned summary leaves no tool-call trace, so action-level evaluation cannot see it ([CaMeL residual risk](camel-control-data-flow-injection.md)) [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479) §8.4].

Provenance assignment ties the components together. Every out-of-band defense rests on the assumption that the primary user's input is trusted, but real systems have headers, spans, and delegated contexts where trust assignment is contested. The trusted computing base is under-specified in the literature, and deployments will fail at the assignment boundary before they fail at the enforcement boundary [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479) §8.2].

## Why it works

A deterministic enforcement layer makes Biba's Star Integrity invariant mechanical rather than learned — a subject that has read untrusted data cannot authorize a high-integrity action regardless of what the model was prompted to do, because the interpreter or Datalog evaluator is not differentiable through prompt engineering [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479v1) §3]. The same structural difference is why adaptive evaluation is necessary rather than optional: a guarantee whose strength is mechanical must have its scope precisely characterized, because the failure modes are at the boundary, not in the core. Empirically, Progent reduced mean attack success roughly sixfold against AgentDojo's standard injections (25.8% to 4.2%) and the adaptive template did not raise success rates — the scope caveats sit in *When this backfires* below.

## When this backfires

Adaptive evaluation is not free, and it is not always the highest-leverage investment.

- The enforcement layer is fully deterministic with no model in the policy path. CaMeL's Python interpreter with capability labels set at task boot has no LLM component for an adaptive attacker to manipulate; FORGE's Datalog evaluator has the same shape. The maxim "test adaptively" still applies, but the marginal payoff is low and evaluation budget is better spent on provenance assignment, side channels, and text-to-text harms [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479) §8.5].
- The agent has no untrusted-content path. An agent whose only inputs are the user prompt and trusted code carries no indirect-injection surface — there is nothing for an adaptive injection to ride on. Trust-boundary auditing using the [lethal-trifecta threat model](lethal-trifecta-threat-model.md) is the right control instead of adaptive evaluation.
- The task surface is single-task and read-only. In the Buchwald paper, the workspace suite showed 0% undefended attack success across all conditions because the read-only task structure gave the injected multi-step actions nowhere to land. Pushing adaptive evaluation onto a narrow agent surfaces no signal — the defense is not what is keeping the attack rate at zero [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479v1) §11].
- The defense, policy, or tool catalog is still in flux. Adaptive evaluation needs a fixed target — an attacker who optimizes against today's policy file tells you nothing about tomorrow's deployment. Pre-production prototypes should validate the structural design first and defer adaptive testing until the enforcement surface is stable.
- The agent runs a weak model on tiny task subsamples. The Buchwald results are explicitly labeled "one small-scale data point on a weak model" — Qwen2.5-7B with eight tasks per suite. Adaptive evaluation on weak models or narrow samples does not extrapolate to production agents on frontier models, and treating those numbers as defense verdicts is the same false-confidence trap static benchmarks created [Source: [Buchwald et al., 2026](https://arxiv.org/abs/2606.26479) §11].

## Key Takeaways

- Out-of-band defenses report near-elimination of attacks on AgentDojo, but the same static-benchmark methodology hid a 90%+ adaptive-attack collapse in in-band defenses — treat current numbers as upper bounds until adaptive evaluation closes the gap.
- A defense-aware evaluation must cover the policy-LLM component (Progent's weak link), in-the-loop tasks that require acting on untrusted content, side channels and implicit flows, text-to-text harms the action layer cannot reach, and provenance assignment at the trusted-computing-base boundary (Buchwald et al., 2026).
- The structural reason out-of-band is more promising is the same structural reason adaptive evaluation is necessary: the security guarantee is mechanical, so its scope has to be precisely characterized.
- Skip adaptive evaluation when the enforcement path is fully deterministic with no model component, when the agent has no untrusted-content surface, or when the policy and tool catalog are still in flux — invest the budget in provenance, side channels, and text-to-text harms instead.
- Weak-model, small-sample adaptive results do not extrapolate; treating them as class verdicts repeats the false-confidence trap static benchmarks created.

## Related

- [Control/Data-Flow Separation for Prompt Injection Defense (CaMeL)](camel-control-data-flow-injection.md) — One of the five out-of-band defenses; this page documents the evaluation discipline, not the mechanism.
- [Five-Stage Policy Layer Typology for Generalist Agents](policy-as-code-layer-typology.md) — Adjacent policy-as-code typology; three of its five stages inherit LLM-classifier brittleness that adaptive evaluation surfaces.
- [Dual-Graph Alignment for Indirect Prompt Injection Defense (AuthGraph)](authgraph-dual-graph-injection-defense.md) — Reports 0.01 ASR / 0.69 UR on AgentDojo with documented bounds on same-observation pollution and multi-agent gaps — an example of bound-stating adaptive evaluation extends.
- [Discovering Indirect Injection Vulnerabilities in Your Agent](indirect-injection-discovery.md) — Companion: how to find the injection surface adaptive evaluation will then test.
- [Single-Layer Prompt Injection Defense](../patterns/anti-patterns/single-layer-injection-defence.md) — The anti-pattern adaptive evaluation forces practitioners to confront when one layer's static numbers turn out to be illusory.
