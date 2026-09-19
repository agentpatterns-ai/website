---
title: "Aggregation Bounds for Agent Authorization"
term: "Aggregation Bound"
description: "Every access in an agent workflow can be authorized and the synthesized answer still not be. What a per-call gate cannot see, and the three parts of it you can build."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - aggregation inference
  - workflow-scoped authorization bound
  - mosaic effect for agents
last_reviewed: 2026-09-18
maturity: emerging
---

# Aggregation Bounds for Agent Authorization

> Every access in an agent workflow can be authorized and the synthesized answer still not be. A per-call gate never evaluates the set.

An aggregation bound is a policy over which combinations of resources one principal may have synthesized, enforced before the result is returned. It answers a question no per-access check asks. Given authorized accesses to several resources and a synthesis over them, "the synthesis of results may produce information that no individual access would expose" ([Tallam, 2026, §5.2.2](https://arxiv.org/abs/2605.05440v1)). A narrative review screening 89 primary sources from roughly 180 candidates reaches the same place four months later by a different method, naming "runtime enforcement and aggregation bounds as the principal unresolved gaps" in the field ([Surapani et al., 2026](https://arxiv.org/abs/2609.15906v1)).

Read this as a gap with three buildable parts, not as a control you can finish. Tallam's paper "does not solve aggregation inference in the general case" ([§9.4](https://arxiv.org/abs/2605.05440v1)), and the review lists the gap as unresolved rather than closed.

## When this recommendation applies

The three parts below repay their cost only where all of these hold:

- A per-call authorization gate already runs. An aggregation bound reads the record of authorized accesses, so it sits on top of per-call enforcement rather than replacing it. An audit of LangChain/LangGraph, LlamaIndex and the Stripe Agent Toolkit found "all three provide capability gating by default, but none provides a deterministic fail-closed per-call value authorization gate by default" ([Mellafe Zuvic, 2026](https://arxiv.org/abs/2606.28679v1)). Build that first.
- Every access reaches the resource through the instrumented boundary, and the harness emits a workflow-scoped trace. Per-call logs record each decision and never the set.
- The workflow spans several resources. Aggregation inference is a workflow-level property ([Tallam, 2026, §5](https://arxiv.org/abs/2605.05440v1)), so a single-resource task has no synthesis to constrain.
- Someone can name the combinations that are out of bounds. The policy is an enumeration, and a resource space discovered at run time gives it nothing to enumerate over.

Outside these conditions, spend the effort on the per-call gate instead. Pre-action authorization cut social-engineering success from 74.6% under a permissive policy to 0% across 879 attempts under a restrictive one ([Uchibeke, 2026](https://arxiv.org/abs/2603.20953v1)).

## Why a correct per-call gate misses it

Authorization is evaluated per access. Disclosure is produced by the synthesis. Nothing in the first evaluation reaches the second.

Write the workflow as authorized accesses to resources `d1` through `dj` and a synthesis `f(d1, …, dj) → r`. The open question is whether `r` is authorized for the requesting principal, and no per-access decision has asked it ([Tallam, 2026, §5.2.2](https://arxiv.org/abs/2605.05440v1)). The classical models inherit the same shape. ABAC "treats each access decision independently" and "cannot express constraints on the aggregation of individually authorized accesses", while XACML obligation policies "are evaluated per-access, not per-workflow" ([Tallam, 2026, §6.2](https://arxiv.org/abs/2605.05440v1)). ReBAC comes closest and still has "no native concept of workflow-scoped authorization that binds a set of accesses together and constrains their aggregation" (§6.3).

An attacker therefore does not defeat a check. Decomposing the request into individually benign subtasks satisfies every check honestly. Tallam reports the Semantic Intent Fragmentation attack doing exactly this at "a 71% success rate across 14 enterprise scenarios" (§5.2.2).

The older statistical-disclosure answers do not port, because the synthesis function "is a neural network whose behavior is not formally specified" and "the set of accessed resources may not be known in advance" (§5.2.2). No adversary is required either. Tallam's production evidence is that "ordinary system behavior, not only adversarial action, already produces the failures this model predicts" ([Tallam, 2026](https://arxiv.org/abs/2605.05440v1)).

## The three parts you can build

Tallam names what is architecturally addressable while the general problem stays open ([Tallam, 2026, §5.2.2](https://arxiv.org/abs/2605.05440v1)).

| Part | What it gives you | What it does not give you |
|---|---|---|
| Make the contributing resource set inspectable after the fact | A reviewer can ask which resources produced this answer | Nothing at decision time; the result has already been returned |
| Define policy boundaries limiting which resource combinations are permitted | A denial before the synthesized result is returned | Coverage of any combination nobody enumerated |
| Track causal dependencies through the synthesis graph | The path from each access to the returned value | A bound on what the model inferred rather than read |

The first and third produce evidence. Only the second denies anything: "the system must be able to define constraints on which resource combinations are permitted for a given principal, and enforce those constraints before synthesized results are returned" ([Tallam, 2026, §8](https://arxiv.org/abs/2605.05440v1)). A stack with per-call logs but no workflow identifier can do none of the three, because every part reads a trace that binds accesses to one workflow.

## Why it works

The bound works because it moves the decision to the only point where the whole set exists. Each access decision sees one resource and the principal's authority over it. The synthesis sees all of them, so the policy question that was unanswerable at each access becomes answerable there. That is also why the review places both its remaining gaps at the enforcement layer rather than in the credential or audit layers. Credential lifecycle, delegation propagation, injection defense and audit each cover a fragment, "while giving little attention to the authorization decision point itself" ([Surapani et al., 2026](https://arxiv.org/abs/2609.15906v1)).

A good audit trail does not substitute, and the review's own completeness test is why. It asks that an agent action be "traceable to a human principal, bounded by what that human actually delegated, and contestable after the fact", and reports that "few documented deployments satisfy all three properties reliably and end to end" ([Surapani et al., 2026](https://arxiv.org/abs/2609.15906v1)). A log delivers traceability and contestability. Boundedness has to be enforced before the result leaves, and aggregation is where it currently is not.

## When this backfires

- The effect never passes your boundary. A shell-out, a script the agent wrote in an earlier turn, an embedded SDK call, or cached state leaves no entry in the trace the bound reads. "Tool-call guardrails miss system actions that bypass the tool layer", which is why ActPlane moves enforcement into the kernel and reports compliance gains "on indirect execution paths that tool-call interception cannot observe" ([Zheng et al., 2026](https://arxiv.org/abs/2606.25189v2)).
- The channel is inference rather than disclosure. A combination policy bounds which resources may be read together and bounds nothing about what a model derives from the ones it may. Measuring its own boundary, the OBPE team found answers that "reconstructed a value that never entered context or used filtered row counts as an oracle", and concluded that "shaping one execution is not noninterference" ([Millstone et al., 2026](https://arxiv.org/abs/2608.27646v1)).
- Legitimate synthesis is the product. The same OBPE trials that cut trace failure from 57.6% to 0.2% cut fulfillment from 79.1% to 60.9% ([Millstone et al., 2026](https://arxiv.org/abs/2608.27646v1)). The denial is also hard to explain, because no single access was wrong.
- You treat the enumeration as coverage. The policy is a denylist over a space the agent may extend at run time, so an unlisted combination is permitted by construction. Tallam is explicit that the paper "does not solve aggregation inference in the general case" ([Tallam, 2026, §9.4](https://arxiv.org/abs/2605.05440v1)), and OBPE scopes the question out of its evaluation: "temporal and aggregate policies lie outside this evaluation" ([Millstone et al., 2026](https://arxiv.org/abs/2608.27646v1)).
- The members were never checked. Where no per-call gate re-authorizes argument values, and by default none of the three audited frameworks does ([Mellafe Zuvic, 2026](https://arxiv.org/abs/2606.28679v1)), the bound constrains which unverified results may combine. That is a compliance artifact rather than a boundary.

One caution on the sourcing. The review that names the gap is a version 1 preprint with no full-text rendition, so it supports the framing and nothing at the level of a mechanism or a number.

## Key Takeaways

- Per-access authorization and workflow-level disclosure are different questions. A stack can answer the first correctly for every call and never ask the second.
- The classical models cannot express the constraint. ABAC evaluates each access independently, XACML obligations fire per-access, and ReBAC has no workflow-scoped binding over a set of accesses.
- Decomposition is the exploit, and it is honest. Individually benign subtasks pass every check, at a reported 71% success across 14 enterprise scenarios, and ordinary non-adversarial behavior produces the same failures.
- Three parts are buildable: an inspectable contributing set, a permitted-combination policy, and causal dependency tracking. Only the second denies anything, and only over combinations someone enumerated.
- Build the per-call gate first. Most frameworks still ship without one.

## Related

- [Monotonic Capability Attenuation for Composition-Safe Tool Use](monotonic-capability-attenuation.md) — composition safety for explicit flows, where budgets on values intersect through tool chains; aggregation inference falls outside its stated precondition, because the leak is in the synthesized result rather than in a value the proxy can read
- [Authorization Continuity Across Agent Mutation](authorization-continuity-across-agent-mutation.md) — bounds what authority may become active when the agent changes, where an aggregation bound constrains what a set of accesses may produce
- [Per-Caller Identity: Who an Agent's Tool Call Acts As](per-caller-identity-for-agent-tool-calls.md) — picks the principal each call acts as, which is the input an aggregation policy is written against
- [Context-Fractured Decomposition Attacks on Tool-Using Agents](context-fractured-decomposition-attacks.md) — decomposition across tools and time as a content-harm problem rather than a disclosure one
- [Provenance-Aware Decision Auditing](provenance-aware-decision-auditing.md) — the trace machinery the first and third parts depend on
