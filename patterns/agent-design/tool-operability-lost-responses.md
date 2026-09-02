---
title: "Tool Operability: Interfaces That Survive a Lost Response"
term: "Tool Operability"
description: "A lost response leaves committed and uncommitted state indistinguishable to an agent. Expose lifecycle identity, durable state, and effect semantics so it can continue."
aliases:
  - Agent-First Tooling
  - callability versus operability
  - operable tool interfaces
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-26
maturity: emerging
---

# Tool Operability: Interfaces That Survive a Lost Response

> Tool operability is whether a tool interface lets an agent continue safely after a lost response leaves committed and uncommitted state indistinguishable.

Callability is whether the agent can form a valid call. Operability is whether it can decide what to do next once that call has returned, or failed to. The gap opens when an external effect commits and the response never arrives: the world where the payment went through and the world where it did not "may become indistinguishable to the agent even though they require different continuation actions" ([Wang, arXiv:2608.23628v1](https://arxiv.org/abs/2608.23628v1)). Retry and duplicate the charge, or abort and strand it. The schema was fine either way.

## When this pays

Three conditions have to hold together before any of this is worth building.

- Your tools commit effects outside the agent's process. Payments, deployments, ticket creation, outbound messages.
- The agent continues without a human approving each write. A confirmation prompt resolves the ambiguity for free.
- You own the server. Resumable invocation and durable state are server-side work; a team consuming third-party tools can add postcondition checks and a client-side idempotency key, and nothing else on this list.

Miss one and you are paying tokens and build time against a failure you cannot reach or cannot fix.

## What the interface has to expose

Wang's Agent-First Tooling set names seven mechanisms. Five carry the study's strong evidence; observable execution and structured outputs get "weaker independent efficacy evidence" and should not be presented as equally supported ([arXiv:2608.23628v1](https://arxiv.org/abs/2608.23628v1)).

| Mechanism | What the interface adds |
|---|---|
| Selective capability discovery | Compact metadata and scoped schemas, so the tool list does not eat the context window |
| Resumable invocation | Stable invocation identity, status retrieval, continuation without re-execution |
| Durable execution state | Recovery handles and reconciliation semantics that outlive the calling process |
| Effect semantics | Declared idempotency, preconditions, commit point, authority, compensation |
| Postcondition verification | Authoritative evidence that the claimed outcome actually happened |

MCP's Tasks extension is resumable invocation shipped in a protocol: "a server can answer `tools/call` with a task handle, and the client drives it with `tasks/get`, `tasks/update`, and `tasks/cancel`" ([MCP 2026-07-28 release candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)). The handle is what makes a lost response recoverable, because the agent can ask what happened instead of guessing.

Effect semantics have a shipped form too, and a sharper edge. MCP's `idempotentHint` answers "Can you safely call it again with the same arguments?", but "annotations are not guaranteed to faithfully describe tool behavior, and clients must treat them as untrusted unless they come from a trusted server" ([MCP, Tool Annotations as Risk Vocabulary](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/)). A wrong idempotency declaration is worse than a missing one, because it authorizes the retry that duplicates the effect. The same trust caveat governs [hint-driven concurrency](../../tool-engineering/read-only-hint-concurrency.md).

## Why it works

An interface can cut the ambiguity two ways, and conflating them costs you the choice between them. It can distinguish state by exposing evidence such as an authoritative lifecycle status, "so that previously indistinguishable histories produce different observations". Or it can stabilize continuation: idempotency and guarded writes "make the same continuation safe across multiple possible hidden states without revealing which state actually holds" ([arXiv:2608.23628v1](https://arxiv.org/abs/2608.23628v1)). One route buys information. The other buys indifference to it. The mechanisms do not map one-to-one onto the routes — "verification primarily improves state distinction; idempotency and guarded effect semantics primarily stabilize continuation; lifecycle and recovery mechanisms may do both". What holds across all of them is the conclusion: "reliable autonomous tool use depends on whether the interface preserves or stabilizes the action-relevant distinctions needed to choose what to do next", not on model strength.

## What the numbers say, and do not

In AFT-Bench "the task, backend state, failure, controller, model, and execution budget remain fixed, while the interface semantics exposed to the agent change", across three model families and 2,385 result rows ([arXiv:2608.23628v1](https://arxiv.org/abs/2608.23628v1)). Resumable invocation and durable execution state each improved recovery by 100 percentage points, at a confidence interval of [1.0000, 1.0000] over 72 matched pairs. Read that ceiling the way the paper does: the effects "should not be read as claims that either mechanism guarantees recovery under arbitrary failures", but as showing "that the two mechanisms are decisive under the specific failure classes they are designed to address". The design is "for mechanism identification rather than for estimating how often the corresponding failures occur in deployed agent systems", so 100 pp is not a production forecast.

The unsaturated numbers travel better. Declared effect semantics cut duplicate effects by 56.9 pp and unsafe commits by 50.0 pp, and there the safe outcome is often refusal rather than the requested write: "guarded execution can turn what would have been a stale or unauthorized mutation into a safe abort or refusal". Selective discovery removed about 4,013 tokens of tool context while capability recall stayed inside a 0.10 non-inferiority margin.

Postcondition verification cut incorrect terminal claims by 27.8 pp overall, and the average conceals a split. Utility was 0.3542 for Qwen and 0.4792 for DeepSeek, and 0 for GPT, because that model "already avoids the targeted incorrect claims" under a more conservative reporting policy. Model behavior substituted for the interface mechanism, so measure on the model you ship before budgeting for the check.

## When this backfires

- No unattended external effects. With read-only tools, or a human on every write, lifecycle handles and effect metadata buy nothing and cost context.
- Third-party tool surfaces. Resumable invocation and durable state have to be built into a server you do not run, so they are unavailable exactly where integration failures concentrate.
- Untrusted self-declared semantics. MCP annotation adoption is uneven and the protocol enforces nothing; the guidance is to "keep your actual safety guarantees in deterministic controls", not in a boolean ([MCP, Tool Annotations as Risk Vocabulary](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/)).
- Legacy backends. Operational semantics "are not always recoverable automatically from legacy systems", so someone authors idempotency scope, authority, and compensation by hand, per tool ([arXiv:2608.23628v1](https://arxiv.org/abs/2608.23628v1)).
- Metadata that fights its own budget. Effect-semantics fields on every tool grow the surface selective discovery exists to shrink, and the same study measured about 4,013 tokens of tool context removed by shrinking it ([arXiv:2608.23628v1](https://arxiv.org/abs/2608.23628v1)).

The mechanisms are not new. Idempotency is already protocol vocabulary, as the `idempotentHint` above shows. What the paper adds is a controlled measurement of what changes when the caller is a model rather than a retry loop you wrote.

## Key Takeaways

- A valid call is not a usable outcome. When a committed effect and an uncommitted one produce the same observation, no stronger model can pick the right continuation.
- Choose the route deliberately: expose lifecycle evidence so the agent can distinguish the states, or declare effect semantics so both states take the same safe continuation.
- Treat the 100 pp recovery figures as evidence that two mechanisms are decisive under the failure classes they target, not as an expected production gain.
- Verify postcondition checking against your own model. It returned zero marginal benefit for one of the three families tested, so its value is a property of your model as much as your interface.

## Related

- [Idempotent Agent Operations: Safe to Retry](idempotent-agent-operations.md) — the caller-side half; this page covers what the tool must expose so the caller knows a re-run is the right move.
- [Informed Abstention as a Tool-Boundary Runtime Gate](informed-abstention-tool-boundary-gate.md) — blocks the call before it happens on a missing precondition, where this page handles the unreadable outcome after.
- [Observation Contract Preservation in Tool-Augmented Agents](observation-contract-preservation.md) — the other way a valid-looking call chain breaks on tool output the agent mishandled.
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md) — the agent-side escalation ladder these interface mechanisms feed.
- [Designing for Agent Consumers (Agent Experience)](../../tool-engineering/designing-for-agent-consumers.md) — the surface-design discipline covering discovery and invocation correctness.
