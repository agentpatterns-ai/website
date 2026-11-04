---
title: "Evidence-Guided Recovery After an Ambiguous Tool Outcome"
term: "Evidence-Guided Recovery"
description: "A timeout leaves failed, committed, and in-flight indistinguishable. Run one admissibility check over every state the evidence still permits, and keep certifiable apart from done."
aliases:
  - admissibility check for recovery
  - evidence-guided task recovery
  - certified completion versus goal satisfaction
tags:
  - agent-design
  - testing-verification
  - reliability
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-03
maturity: emerging
---

# Evidence-Guided Recovery After an Ambiguous Tool Outcome

> After a timeout, what you may safely do next follows from the provider's contract and the evidence of its effects, not the missing return value.

A timeout tells you a response is missing. It does not tell you whether the write failed, committed, or is still in flight. Where no valid key already covers the operation, recovery starts by listing the states the public evidence still permits, then refusing every next action that is unsafe in any one of them. The grounding predates agents, in Birrell and Nelson's RPC failure semantics and the end-to-end argument: "These foundations explain why an HTTP error alone is not a negative effect certificate" ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)).

## The conditions that make this worth building

Two things have to be true before any of this earns its cost.

The operation is not already protected by a valid key. Where the provider honors an atomic same-key contract, "a repeat attempt can be allowed when it cannot append another effect" ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)) and your recovery is a retry loop. The check is for what falls outside that: an expired key, a provider with no key at all, an append you cannot deduplicate.

You can write the provider contract down, because the check consumes declared capabilities rather than guesses: the key's validity interval, a query's scope and authority, whether a trustworthy commit bound exists, whether a response certifies settlement or only receipt, the reversible effect class, and when authority is checked. Without those answers there is no check to run, and the paper concedes its own inputs give "substantially more predictive information than a normal capability declaration" ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)).

## One check in front of five actions

The action set is small: "query, write, wait, compensate, and handoff" ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)). Each one passes the same admissibility check first. That check covers four concerns, and they are the portable part of the paper.

| Concern | What it rejects |
|---|---|
| Key expiry | A retry under a key the provider no longer honors. "An expired key does not justify a retry." |
| Authorization timing | A write authorized at acceptance that expires before commit, where the provider enforces at commit. |
| Dependencies | Compensating a predecessor while a dependent effect exists or is still pending. |
| Residual effects | A non-idempotent attempt while an earlier request may still land. "A query can report the current count accurately while an older request remains in flight." |

Compensation is no exit from a residual effect. It is an ordinary effectful call carrying its own ambiguity: "A timeout during compensation therefore creates another evidence problem, not a successful rollback marker."

## Keep certifiable apart from done

Collapsing two verdicts into one produces the false "completed". One asks whether the goal holds, the other whether public evidence supports safe completion, and they come apart measurably. Across the paper's 37-assignment enumeration, "Each active arm has 30 assignments whose private goal is satisfied at the deadline but only 28 safe certified completions" ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)). The two missing tasks fail for unlike reasons. In one, the effect did land and the evidence could not show it: "The controller cannot turn adjudicator knowledge into a certificate." In the other, "the provider does not enforce commit-time authorization: the effect occurs after authority has expired and is an absolute violation." So a satisfied goal is not uniformly good news. "The second case is unsafe, rather than merely missing evidence."

So unresolved has to be a terminal state your system can return, kept "separate from task completion, successful compensation, and a merely plausible success message". Waiting does not convert it: "The executor never advances that sentinel into a concrete commit, even after waiting."

## Why it works

The rejection does not depend on which world is actual, and that is the mechanism. Because the check tests every state still compatible with the evidence, a duplicate-producing action is refused whether or not the first write landed. Probability buys no exception: "Probabilities guide selection; they cannot turn a low-probability prohibited transition into an admissible action" ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)).

Planner advice improves recovery under a shared check. In the preregistered model comparison, advice certifies 30/58 paired episodes versus 9/58 with evidence prompting. The difference is 36.2 percentage points (registered family test, p=0.0078). The comparison covers two local model bundles under a supplied known provider model. With advice, "Rejected unsafe proposals fall from 317 to 123 and false completion claims from 218 to 76". These are proposal counts; the shield blocks unsafe proposals in both conditions. The paper attributes zero recovery-introduced checked violations in the recorded arms to the common execution contract. It attributes completion and proposal differences to the advice interface ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)).

## When this backfires

- Search adds computation without improving completion in the separate deterministic study. "Verify–wait rules, capability rules, greedy selection, and joint planning each achieve 28 certified safe completions out of 37 assignments" ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)). Selection totals 9.53 seconds for joint planning versus 0.14 for capability rules, measured on a shared host. These development results do not compare advice interfaces for a model. The model study bundles advice with its computation: "search-versus-rule advice requires a separate matched comparison". Neither recommendation grounding nor multi-step search is isolated as a causal mechanism.
- Durable execution leaves external-call guarantees to the caller. The Diagrid FAQ states, "Catalyst does not guarantee exactly-once for external API calls." It directs callers to "implement idempotency keys or reconciliation" ([Diagrid Catalyst FAQ](https://www.diagrid.io/faq/durable-execution/how-does-diagrid-catalyst-handle-side-effects-like-payment-or-email-api-calls-that-must-be)). A receiver-side atomic same-key contract permits safe repetition within its validity interval ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)).
- A read-back can help after a trusted settlement bound. A negative query can still be insufficient while an older request remains pending ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)). Check which fault class [exactly-once enforcement](exactly-once-enforcement-layer.md) covers before treating a read as decisive.
- The frame is small, and an omission is silent. A task is capped at "at most twelve operations and at most 4,096 initial support combinations", shared mutable targets are rejected outright, and opaque batch calls sit outside the profile. Worse, "an unobservable omitted alternative can still invalidate retention and safety assumptions" ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)).

## Example

What the handoff carries when the check refuses to certify. The paper specifies the payload: "A practical handoff should contain the bound logical requests, known effects, unresolved alternatives, remaining obligations, permitted next actions, and resources already consumed" ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)). Field names are whatever your own harness writes.

```json
{
  "request": {"op": "create_invoice", "key": "inv-8841", "key_valid_until": "expired"},
  "known_effects": ["notify_customer committed at 14:02"],
  "unresolved": ["create_invoice: failed | committed | in-flight"],
  "remaining_obligations": ["update_record (blocked: depends on create_invoice)"],
  "permitted_next": ["query_invoice (non-authoritative, 60s visibility delay)"],
  "consumed": {"calls": 4, "deadline_remaining_s": 95}
}
```

Three fields do work a status code cannot. `unresolved` names the alternatives rather than picking one, `permitted_next` is the output of the admissibility check rather than the full API surface, and `key_valid_until` is why a retry is absent from that list. An operator can act on this. "Completed with errors" is not actionable.

## Key Takeaways

- Treat an error return and a negative read as compatible with a commit. Neither is a certificate that another non-idempotent attempt is safe.
- Run one check before every recovery action, covering key expiry, authorization timing, dependencies, and residual in-flight effects.
- Report certifiable completion and goal satisfaction separately. The paper's enumeration had 30 goals satisfied against 28 certified, so the gap shows up even at small scale.
- Give your system an unresolved terminal state with a handoff payload. Waiting does not resolve an unknown settlement time.
- Keep the common check and compare advice methods under it. The model result supports planner advice over evidence prompting; choosing search over rule-derived advice needs a matched comparison.
- Inspect task-family results before transferring the advice interface. Eight families account for 21 net additional completions; eleven tie at 9/30. Removing any whole family leaves a positive descriptive difference of 28.8–38.9 percentage points ([Zhu et al., arXiv:2610.41453v1](https://arxiv.org/abs/2610.41453v1)).

## Related

- [Tool Operability: Interfaces That Survive a Lost Response](tool-operability-lost-responses.md) — the prior question, which is what a tool interface must expose before a caller can decide anything
- [Exactly-Once Enforcement Layer](exactly-once-enforcement-layer.md) — whether the model, the harness, or the write contract should carry the duplicate once you know which fault class you are in
- [Idempotent Agent Operations: Safe to Retry](idempotent-agent-operations.md) — the design that makes most of this check unnecessary, plus the authority recheck a retry needs
- [Residual Completion for Stateful Agent Handoffs (CFRC)](residual-completion-stateful-handoffs.md) — the opposite starting point, where the predecessor's committed frontier is known and can be frozen
- [Durable Turn Log for Agent Crash Recovery](durable-turn-log-crash-recovery.md) — the local record that resumes a turn and still cannot fence an opaque remote write
