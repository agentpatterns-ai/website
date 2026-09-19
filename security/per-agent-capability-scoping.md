---
title: "Per-Agent Capability Stores Beat One Task-Wide Allowlist"
term: "Per-Agent Capability Scoping"
description: "A task-wide allowlist must grant the union of every subtask's needs, handing that authority to whichever sub-agent read the poisoned file; a separate attenuated store per principal cut executed injections from 33/75 to 3/75 at equal task success."
aliases:
  - CapScope
  - per-principal capability store
  - attenuated capability delegation
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-09
maturity: emerging
---

# Per-Agent Capability Stores Beat One Task-Wide Allowlist

> A task-wide allowlist must grant the union of every subtask's needs, so split the ceiling into one capability store per agent.

Giving each sub-agent its own attenuated capability store, rather than sharing one task-scoped policy, cut executed prompt injections from 33 of 75 runs to 3 of 75 with task success unchanged at 68/75 ([Bouras et al., 2026v1](https://arxiv.org/abs/2609.08371v1)). The load-bearing comparison there is against a task-specific policy generated for that same run, the control most hardened harnesses already have. Ambient authority admitted 47/75 and a static global denylist 46/75, so the denylist bought one run out of seventy-five.

## When this is worth the cost

Four conditions decide whether the split pays. Where any one fails, the measured gain either does not apply or is bought at a cost the paper also measures.

- More than one principal. The measured delta is the split itself, so a single-agent workflow has no union to divide and collapses back into the task-global policy.
- A typed, mediated tool catalog. Exec scope is a parsed argument-vector prefix, so it can permit `pytest` and refuse `curl`. A wildcard `bash` tool makes every Exec grant a wildcard grant, the same limit that bounds [monotonic capability attenuation](monotonic-capability-attenuation.md).
- Slack in the latency budget. Mean wall-clock time was 145 s under ambient authority, 194 s under the task-global policy, and 316 s under the split. Read the mean with its tail: the split's median is 208 s, and five runs hit the 900 s timeout ([Bouras et al., 2026v1](https://arxiv.org/abs/2609.08371v1)).
- A threat model about unauthorized action rather than disclosure. The authors state the non-goal plainly: "CapScope is not a confidentiality mechanism. A permitted read followed by a permitted write can still move data, and an injection can misuse authority deliberately granted to its reader" ([Bouras et al., 2026v1](https://arxiv.org/abs/2609.08371v1)).

## What a store holds

Each capability pairs an effect type with a scope predicate ([Bouras et al., 2026v1](https://arxiv.org/abs/2609.08371v1)). Read and Write scopes are canonicalized path prefixes; Exec scopes are argument-vector prefixes. The stores sit host-side, one per principal, outside the model's context, so text the model reads later cannot widen them. At dispatch the harness needs a capability matching the effect type and a predicate that accepts the concrete arguments; an uncovered proposal returns a refusal instead of a tool result.

## Why it works

The union property is the whole mechanism. Whatever a single allowlist covers reaches every principal, including the one reading attacker-controlled text. The paper puts it directly: "Because one policy is shared by every principal, it must grant the union of everything the task needs—reads, a source write, the test commands—just to let the repair finish, and that broad authority then reaches _every_ sub-agent, the runner that reads the poisoned output included" ([Bouras et al., 2026v1](https://arxiv.org/abs/2609.08371v1)). Split the ceiling and the runner that read the injection can still run the tests but cannot write source, so the backdoor never lands while the patcher keeps the write that finishes the repair ([Bouras et al., 2026v1](https://arxiv.org/abs/2609.08371v1)). That the payload looks ordinary is the point: the paper's own injected request names no `.env` and no `curl`, so no deny rule would flag it. The model still proposed the injected action in 34 of 75 runs; only 3 were permitted to run. Nothing had to recognize the text as malicious, which is why this survives attacks that defeat [detection-based defenses](prompt-injection-resistant-agent-design.md).

## When this backfires

- Scoping is not per-call authorization. An audit of LangChain/LangGraph, LlamaIndex, and the Stripe Agent Toolkit found all three gate which tool an agent may call and none re-authorizes concrete argument values; a correctly scoped agent still executed an unauthorized payout ([Mellafe Zuvic, 2026v1](https://arxiv.org/abs/2606.28679v1)). A store bounds the effect type, never the amount.
- The preflight can under-grant. Two of the seven task failures came from it omitting a required source-write capability. Freezing the ceiling before repository contents are read trades availability for containment, and file-tree names will not always predict what the work needs.
- Sub-agent instruction files stay inside the ceiling. All three residual executions arrived through one surface: "Under C, all three executed attacks occur through AGENTS.md; the other four surfaces admit none" ([Bouras et al., 2026v1](https://arxiv.org/abs/2609.08371v1)). README, skill file, source comment and tool output each fell to 0/15. [Workspace topology](workspace-topology-injection-attack-vector.md) covers the cheap levers for that surface.
- The evidence base is small. Five Python repairs, one model, three trials per cell. The authors put large refactors, dependency migrations, and long-running workflows outside what the corpus represents.
- A hermetic runner may already cover it. Where a throwaway container holds no production credentials, the store's marginal gain shrinks while the preflight's availability cost and the typed catalog's authorship cost stay. Reach for [blast radius containment](blast-radius-containment.md) first.

## Key takeaways

- The task-scoped authority ceiling most hardening advice stops at is the weak link, because one shared policy must be the union of every subtask's needs.
- Splitting that ceiling per principal took executed injections from 33/75 to 3/75 at identical task success, with the model still proposing the injected action 34 times ([Bouras et al., 2026v1](https://arxiv.org/abs/2609.08371v1)).
- The cost is a mean of 316 s against 194 s, though the split's median is 208 s and five runs timed out, plus two task failures from a preflight that under-granted.
- It is not a confidentiality control and it does not authorize argument values ([Mellafe Zuvic, 2026v1](https://arxiv.org/abs/2606.28679v1)). Pair it with per-call value checks where money or destructive scope is in reach.
- `AGENTS.md`-shaped files remain the residual surface; treat them as untrusted content no store can help with.

## Related

- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — fixes the issuer of task authority before runtime content is read; this page argues that one such ceiling for the whole task is still too wide.
- [Revocable Resource-and-Effect Capabilities for Coding Agents (PORTICO)](revocable-resource-effect-capabilities.md) — scopes a capability across a subgoal's lifetime with revocation on closure; per-agent stores scope across principals within one task and never revoke.
- [Monotonic Capability Attenuation for Composition-Safe Tool Use](monotonic-capability-attenuation.md) — scopes a value's budget across composition, the third axis alongside time and principal.
- [Intent-Governed Tool Authorization for AI Agents (IGAC)](intent-governed-tool-authorization.md) — narrows a static manifest per request; the narrowing here is per principal instead.
- [Workspace Topology as an Indirect Injection Attack Vector](workspace-topology-injection-attack-vector.md) — the residual `AGENTS.md` surface, and the cheap levers that reduce it.
- [Aggregation Bounds for Agent Authorization](aggregation-bounds-agent-authorization.md) — the question left after every call is authorized: whether the set of accesses may be synthesized for this principal.
