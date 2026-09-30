---
title: "Exactly-Once Enforcement Layer: Model, Harness or Contract"
term: "Exactly-Once Enforcement Layer"
description: "Which layer must enforce exactly-once depends on whether a read-back can reveal what happened. Frontier models handle a lost acknowledgement; an in-flight request needs the write contract unless the service documents a short in-flight bound to wait out."
aliases:
  - duplicate side effects in agents
  - where exactly-once lives
  - layer attribution for duplicate writes
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-27
maturity: emerging
---

# Exactly-Once Enforcement Layer: Model, Harness or Contract

> Which layer must enforce exactly-once depends on the fault: the model when a read-back can settle it, the tool contract when nothing can.

Split your ambiguous write failures into two classes before deciding where to spend. In the first, an immediate read-back reveals whether the effect landed, and a capable model recovers on its own. In the second it does not. The read-back is either too early or never prompted. Closing the gap needs either a documented bound on in-flight time to wait out or a change to the write contract. A September 2026 benchmark of 25,930 graded agent episodes puts it plainly: "the answer depends on the failure" ([Li, arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)).

## Which conditions have to hold

Three things have to be true at once before the decision is even reachable.

- Your agent issues writes whose effects commit outside its process, and it continues without a human confirming each one.
- You can change, or can lobby the owner to change, at least some of those write contracts. Adding an idempotency-key argument is server-side work.
- A duplicate costs more than the latency you would spend avoiding it. Every remedy below trades time or server work for that.

Miss the second and only the client-side half is left, and it has a measured ceiling. The evidence is also narrower than the conclusion. The study's services "are simulated, although their semantics follow documented production conventions", and it identifies which mechanism fixes which fault rather than how often each fault fires in your stack ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)).

## Two fault classes, two layers

| Fault | What the agent sees | Can a read-back settle it? | Layer that decides |
|---|---|---|---|
| Acknowledgement lost, misleading 500, partial batch | Timeout or error, effect already visible | Yes | Model |
| Request still in flight (late commit) | Timeout, effect not yet visible | No, the read precedes the effect | Tool contract |
| Transport delivered the write twice | Success | No, nothing prompts a check | Tool contract |

On the first row frontier models are close to correct. They "almost never duplicate a write whose acknowledgement was lost", at 0.5% of episodes, while two weaker models duplicated in 18% of the same worlds. There the model "accounts for 53% of the explained variance and the contract for 30%", so buying a better model works ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)).

On the other two rows the same models collapse. They "duplicate in 56% of late-commit and 74% of redelivery episodes", and the attribution inverts: "the contract accounts for 81% and the model for 8%" ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)). A model upgrade buys 8% of the explained variance in a class where two thirds of episodes duplicate.

## Why it works

The classes differ in whether there is evidence to gather, and the second holds none. A timeout is observation-equivalent across three hidden states: never executed, executed with the response lost, and still in flight. The paper draws the limit for any policy: "A recovery policy therefore cannot condition on the outcome state directly; it can only gather evidence (by reading, waiting, or asking a human) or choose actions that are safe under every equivalent state" ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)). [Tool operability](tool-operability-lost-responses.md) is the interface-side attack on the same indistinguishability.

So the second class is a proof, not a tendency. Completing the task where the write never executed requires re-issuing it. So a policy acting only on observations also re-issues where the original is still in flight, whenever the in-flight delay exceeds its deadline plus the read path's lag. It duplicates there with probability one. The paper states this for a non-idempotent write with no key support and for policies "whose actions depend only on observations" ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)).

A key removes the need to distinguish anything: "Every execution of r, including the in-flight original and any redelivered copy, carries the same key, so at most one execution has an effect" ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)). Frontier models attached a key where the contract accepted one in 98% of committed-fault episodes without being told to. Extending keys to every write dropped the duplicate rate from 28% to 4% with no other change.

## Waiting versus keys

Waiting is the one client-side escape from a late commit, and its cost tracks the delay distribution rather than your effort. Under a fixed 90-second in-flight delay, waiting 120 seconds before verifying reached 99% exactly-once success at 3.8 simulated minutes per episode against 2.9 for the baseline. Under a heavy-tailed delay drawn between 40 seconds and 2 hours, waiting an hour reached 84% at 49.9 minutes per episode. The keys-everywhere contract reached 92% at 0.9 minutes with no wrapper at all ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)). Wait where a service documents a short in-flight bound. Where it does not, waiting is an expensive partial fix.

Keys pay only when they stay stable across attempts. Under that same keys-everywhere contract, of 432 late-commit re-issues that reused the original key, 0% duplicated. The 56 whose first attempt carried no key duplicated in 68% of cases, and both of the 2 that appended a suffix such as `-retry1` duplicated ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)). One key per intent, pinned by whatever owns the transport.

## What the harness owns

Almost nothing, and one thing it should stop doing. In the native contract, three production command-line harnesses and a minimal scaffold running the same models duplicated at 27%, 29%, 30% and 26% under identical faults. Transparent retries are the active harm: "sdk-retry lowers exactly-once success from 72% to 50% and raises the duplicate rate to 50%, because every lost acknowledgement becomes a duplicate before the model sees anything" ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)).

That leaves two jobs: pin the key, and carry unresolved outcomes into the final report. Across 1,279 episodes that produced at least one duplicate, "the agent finished with status completed in 90%", and in 80% it listed no operation as uncertain ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)). Nobody investigates an incident the report says did not happen.

## When this backfires

- You consume the write path and cannot change it. In the study's own native contract "only two of the eleven non-idempotent write paths accept one—a ratio that, if anything, flatters many real APIs" ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)). For a third-party API the contract layer is somebody else's lever.
- Middleware that advertises verification. Announcing it would verify before any identical retry moved one strong model off escalating. Its late-commit duplicates rose from 50% to 71%, because the wrapper's read-back cannot see an in-flight request either. "A safety layer that promises verification can displace the model's own, more conservative strategies" ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)).
- A read path that lags. Writes with no read-back path at all "are duplicated less often (13%) than writes that can be read back", because agents escalated to an operator instead of trusting a stale read ([arXiv:2609.29095v1](https://arxiv.org/abs/2609.29095v1)).
- Key retention shorter than your replay horizon. Gunnar Morling notes that "it is not possible to guarantee exactly-once delivery of messages. What is possible though is *exactly-once processing*", and that once a stored key ages out "neither the producer of the message nor the consumer will have any indication of the duplicated processing in that case" ([On Idempotency Keys](https://www.morling.dev/blog/on-idempotency-keys/)).
- Late commits and redelivery are rare on your transport. A concurrent study reports a client-side wrapper of postcondition verification, verify-before-retry logic and idempotency keys that "significantly reduces duplicate actions, while maintaining comparable task success rates" ([arXiv:2608.02645v1](https://arxiv.org/abs/2608.02645v1)). Start there instead.

## Key Takeaways

- Ask whether a read-back can settle the fault before you ask which model you are running. That answer, not the model tier, decides which layer you pay: the attribution flips from 53% model to 81% contract across the two classes.
- Against a late commit no observation-only policy is exactly-once without a known bound on in-flight time. It is a proof, so no model upgrade retires it, and few APIs publish such a bound.
- Add the idempotency-key argument before you write any prompt guidance. Agents attach a key unprompted once the contract offers one, so the server-side change is most of the win on its own.
- Pin one key per intent in whatever owns the transport, and never let a retry mint a fresh one.
- Turn off transparent retries of non-idempotent writes, and treat an agent's completion report as unverified until the effect ledger agrees with it.

## Related

- [Tool Operability: Interfaces That Survive a Lost Response](tool-operability-lost-responses.md) — the catalog of what a tool interface should expose, where this page decides which layer to spend on
- [Idempotent Agent Operations: Safe to Retry](idempotent-agent-operations.md) — the client-side techniques, including why a check-before-act guard is not enough under concurrency
- [Tool-Call Success as Workflow Effect Evidence](../anti-patterns/tool-call-success-as-workflow-evidence.md) — the anomaly catalog behind the reporting gap a green call log hides
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md) — the wider recovery vocabulary an ambiguous write failure sits inside
- [Observation Contract Preservation](observation-contract-preservation.md) — the other way a second call to the same tool goes wrong, through mutated tool output rather than a lost response
