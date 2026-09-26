---
title: "Path-Scoped Write Contracts for Shared Agent State"
term: "Path-Scoped Write Contracts"
description: "A schema check proves a worker's output is well formed. It does not say which role owns which field, and that gap admitted 52% of unauthorized writes."
aliases:
  - role-scoped state write contracts
  - schema-grounded state mutation
  - validated patch coordination
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-25
maturity: emerging
---

# Path-Scoped Write Contracts for Shared Agent State

> A path-scoped write contract names which role may mutate which field of shared state, so the runtime refuses a schema-valid write from the wrong worker.

A path-scoped write contract is the list of state paths one agent role may add to or replace, checked by the runtime before any mutation commits. Give every worker such a contract, route all writes through one validator, and an out-of-role proposal is logged instead of applied. Zhang and colleagues built this as PatchBoard: an Architect agent writes the schema and contracts once, then a deterministic kernel becomes the only component that can mutate committed state ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2)).

## When this applies

The evidence covers a narrow box, and three conditions decide whether the machinery earns its cost.

1. The task's state factors into named fields. ALFWorld's object-and-receptacle state maps onto a JSON schema almost for free, and the authors expect open-ended settings such as software engineering or long-form generation to "require richer schemas and more complex validation" ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2)).
2. Attribution and replay are requirements, not nice-to-haves. The paper calls its own design "most suitable when auditability, attribution, and state integrity are central requirements" ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2), Limitations).
3. Agent count stays moderate. A single validating writer is the same central controller that Mao and Mirhoseini measure going wrong at scale: "As the number of subtasks grows, this controller becomes a communication and integration bottleneck" ([arXiv:2606.10662v1](https://arxiv.org/abs/2606.10662v1)).

Outside that box, keep messages.

## What a schema check leaves open

[Typed schemas at agent boundaries](typed-schemas-at-agent-boundaries.md) validate the shape of what one agent hands another. Shape is one control and ownership is a second, and the fault-injection table separates them. Over 200 injections per fault type, three designs contaminated committed state at these rates ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2), Table 1):

| Injected fault | Plain blackboard | Structured JSON | Contracts + kernel |
|---|---|---|---|
| Invalid JSON | 0.81 | 0.23 | 0.00 |
| Bad path or type | 0.76 | 0.18 | 0.00 |
| Unauthorized write | 0.68 | 0.52 | 0.00 |
| False claim | 0.70 | 0.66 | 0.43 |
| Cycle halt (higher is better) | 0.12 | 0.39 | 0.96 |

The third row is the whole point. That blackboard already had the schema, and it still took 52% of unauthorized writes, because no type check says who owns `/claims/*/status`. The fourth row sets the ceiling: false claims survive at 0.43, so this is an integrity control and never a truth control.

## Why it works

Two mechanisms, and the paper isolates each with its own control.

One component owns the write. The kernel applies a candidate patch to a temporary copy first. It then checks operation syntax, path authorization against the proposing role's contract, schema validity of the resulting state, and the invariants the blueprint registered. It commits transactionally only when every check passes, and logs a failed patch with the stage that rejected it ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2), §3.4). Later workers therefore condition only on state that already passed those checks, which drove the top three contamination rows to zero. Over 630 matched ALFWorld episodes it solved 84.6% against 30.8% for a LangGraph supervisor and 61.6% for Flock, at 45.5k tokens per success against 368.3k and 64.2k.

The read side carries as much of it. The same kernel builds each worker's view from its read contract and a character budget, summarizing lower-priority collections down to identifiers and provenance. Removing that slicing cost about as much success as removing the patch interface, and of the budgets tested (1k, 2k and 4k characters) the smallest won on success and cost together. The authors read that as "exposing more state to workers can introduce irrelevant context without improving local decision quality" ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2)).

The overhead is small where it was measured. In one 40.3k-token trajectory the schema fragments, views and patch-format instructions came to 0.6k tokens, 1.5% of the run, against 26.1k for actor calls ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2), Appendix D).

## When this backfires

- Factual correctness is the goal. A schema-valid claim can still be false, and on the paper's own 240-example HotpotQA diagnostic the Flock baseline had the lowest unsupported-claim rate. The authors include that appendix "to mark a limitation, not to claim transfer improvement" ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2)).
- The blueprint is wrong. A sparse schema can block useful progress and a permissive one weakens the role isolation the design exists for. Generated task-specific schemas beat fixed ones on both success and cost, so schema quality is a failure surface, not a setup detail ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2)).
- Workers need reasoning headroom. Every output becomes a constrained patch, and Tam and colleagues report "a significant decline in LLMs reasoning abilities under format restrictions" ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3)).
- The fleet improves from experience over a long deployment. A central store "collapsing agent diversity" is the case for the opposite design, which beat the strongest centralized memory baseline by up to 23.8% average accuracy at up to 49% fewer tokens ([arXiv:2605.22721v1](https://arxiv.org/abs/2605.22721v1)).
- The collaboration is short. Schema construction, slicing, validation and transaction logging are stated engineering overhead ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2)), and a one-shot task has nothing to amortize them against.
- Nobody governs the log. Transaction logs "can contain sensitive intermediate information", so the paper asks deployments for access control, retention policies and redaction ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2)).

One limit on all of it. The comparison runs one model at temperature 0 in one environment under a 20-step cap, and the LangGraph baseline called three subagents per turn to reach its 368.3k tokens per success. Treat the direction as measured and the margin as unreplicated.

## Example

The contract lives in the blueprint, one entry per role, listing the paths that role may write. The paper's evidence pipeline splits three roles over one claim record ([arXiv:2605.29313v2](https://arxiv.org/abs/2605.29313v2), §3.2 and §3.3):

```json
{
  "collector": { "write": ["/evidence/-"] },
  "extractor": { "write": ["/claims/-"] },
  "verifier":  { "write": ["/claims/*/status"] }
}
```

The extractor may append a draft claim and can never mark one verified. The verifier may flip a status and can never invent the claim it is judging. A patch that reaches outside its role's list fails authorization before the kernel touches committed state, and the rejection is logged with the path that was refused.

## Key Takeaways

- Sort your shared state by which role writes each region, then write the contract as paths. A type check cannot infer ownership.
- Make one component the only writer, and have it validate on a copy before it commits. Rejected proposals stay in the log rather than in the state.
- Budget the read side too. The smallest view tested beat the larger ones on success and cost at the same time.
- Stop at integrity. False claims passed validation at 0.43, and a blackboard beat this design on unsupported claims in a question-answering setting.
- Before adopting, check the scaling assumption nobody has tested here: a single validating kernel is a central controller, and agent count was never varied.

## Related

- [Typed Schemas at Agent Boundaries for Multi-Agent Systems](typed-schemas-at-agent-boundaries.md) — the shape half of the same problem, validating what crosses a boundary without assigning ownership
- [Pre-Write Change Intent Admission (Claim Plane)](pre-write-change-intent-admission.md) — the same admit-before-write posture applied to repository files rather than shared task state
- [Context-Graph Shared Memory for Multi-Agent Systems](context-graph-shared-memory.md) — shared state as typed triples, optimized for retrieval rather than for authorized mutation
- [Decentralized Memory for Self-Evolving Multi-Agent Systems](decentralized-memory-multi-agent.md) — the counter-case, which argues a central store collapses agent diversity
- [Field-Change Intent Instead of Model-Written Diffs](../agent-design/field-change-intent-over-generated-diffs.md) — field-path intent instead of generated bytes, for a single agent editing config
