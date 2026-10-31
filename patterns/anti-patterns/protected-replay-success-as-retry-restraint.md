---
title: "Protected-Replay Success as Retry Restraint Evidence"
term: "False Retry Permission"
description: "An agent that reuses a valid idempotency key can still dispatch on a key that protects nothing. One 720-response control put Terra at 80/80 protected replays and 55/80 inadmissible changed-key retries."
tags:
  - anti-pattern
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - retry permission versus recovery outcome
  - unprotected retry after a timeout
  - idempotency key use as retry restraint
last_reviewed: 2026-10-22
maturity: emerging
---

# Protected-Replay Success as Retry Restraint Evidence

> An agent that uses a valid idempotency key correctly can still dispatch a retry no key protects, so score the two separately.

RetryBench scores a single recovery decision per episode, across four hand-written software tasks and six GPT endpoints, against a simulated provider ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3)). Four tasks carry no population claim, since "even if all four agreed, a sign test would give p = .125".

## Score permission and recovery separately

A 720-response key control put Terra at 80/80 protected replays and 55/80 inadmissible changed-key retries. Correct key use did not establish retry restraint ([RetryBench, Table 9](https://arxiv.org/abs/2610.15884v3)). Test valid-key, changed-key, and no-original-key conditions separately. Record the action, its permission under the contract, and the recovery outcome.

## Why it works

A weak negative read after a timeout fits three worlds: never executed, still running, or committed but not yet visible. A retry is justified only if replay is protected, or if every compatible world is already terminal and effect-free, and "A weak negative read establishes neither" ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3)). Protection requires enforcement. "ProtectedReplay requires an enforced guarantee for the same operation and payload, within the key's scope and retention period." And not every key qualifies: "A changed key, or one added after an unkeyed original, cannot protect that original" ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3)). Stripe shows that enforcement on a real service: "The idempotency layer compares incoming parameters to those of the original request and errors if they're not the same to prevent accidental misuse" ([Stripe](https://docs.stripe.com/api/idempotent_requests)).

The study does not identify a mechanism for the display result. The paper "does not measure multi-turn recovery or episode-level safety", and its own rationale analyses "provide no evidence for a behavioral mechanism" ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3)).

## When this backfires

- You consume the write path and cannot change it. The paper lists what real systems need: "Real systems must validate provider guarantees, preserve operation identity, bound retries, and expose unresolved work" ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3)).
- Key retention is shorter than your replay horizon. The contract "retains keys for 24 hours; all tested calls use the same payload within 30 seconds", and the retention window is "a stated contract assumption, not a simulated expiry test" ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3)). On Stripe's API v1 a key becomes removable "after they're at least 24 hours old". Past that point, "We generate a new request if a key is reused after the original is pruned" ([Stripe](https://docs.stripe.com/api/idempotent_requests)).
- Client-side verification suits your fault mix. A verify-before-retry wrapper cuts duplicates with no server key, at a stated ceiling: "without idempotency, there remains a small window where concurrent retries or race conditions may still produce duplicates" ([arXiv:2608.02645v1](https://arxiv.org/abs/2608.02645v1)).
- You tune only against false permission. In the explicit-contract cue control "All 762 returned responses deferred; six of 768 planned responses are missing". There "were no observed unsupported retries and no completed recoveries" ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3)). The paper's motivation names the opposite failure: "Counting duplicates alone rewards a model that always defers, even when a safe retry is available" ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3)).
- You rely on an endpoint name. The paper's newer endpoint names are "unpinned aliases" ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3)), so pin your own endpoint and interface, then retest on your own tasks. Sol made 1/80 changed-key retries (Table 9), and that count can change when the alias moves.

## Example

### Endpoint and interface results

A 720-response key control measured both at once, pooling four label and lookup-semantics conditions ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3), Table 9):

| Endpoint | Valid same-key retry | Changed key offered | No original key |
|---|---|---|---|
| Sol | 80/80 | 1/80 | 0/80 |
| Terra | 80/80 | 55/80 | 0/80 |
| Luna | 78/80 | 60/80 | 49/80 |

The last two columns count retries the benchmark rules inadmissible. Terra reused the valid key in every response it returned and still dispatched on a key that cannot protect the original in 55 of 80. Stating the lookup contract barely moved it. With lookup semantics spelled out, Terra's changed-key retries were 11/20 labeled and 15/20 unlabeled, against 14/20 and 15/20 without (Table 10).

The display condition is not neutral either. With the valid key present, "displaying an invalid key is followed by Luna no longer using the valid original key": protected recoveries fell from 18/20 to 0/20. Six of 20 responses copied the displayed key. When the original key was present, Sol and Terra used it in every returned response. Sol's 19/20 reflects one missing response; Terra returned 20/20 ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3), Table 3). Protected recovery was a secondary outcome, and its tests were chosen after collection. The authors draw no rule from it: "These results do not support a general rule to always show or always hide keys."

A per-model verdict also did not carry across the paper's two key interfaces. Under a mandatory offered-key schema with stated lookup semantics, Terra produced changed-key errors in 26 of 40 responses. Under the optional-candidate schema it produced none in 20, and "Candidate visibility alone therefore does not reproduce the earlier Terra result in this setting" ([arXiv:2610.15884v3](https://arxiv.org/abs/2610.15884v3)). Several things moved at once: "Wording, schema, collection time, and unpinned aliases changed between those studies." The comparison shows that the verdict did not transfer. It does not isolate a cause.

### Three candidate probes

The three probes are RetryBench's own candidate-control conditions and its key labels, with Luna's counts from that control's Table 3; each count pools its four tasks. The service line is Stripe's documented behavior.

**Before** — a single protected replay read as retry restraint:

```text
condition:   valid original key-A present, no other key shown
observed:    agent reused key-A after the timeout; ledger held one effect
inferred:    "this agent retries safely"     # the only condition that was run
```

**After** — permission and recovery scored on separate axes:

```text
key-A present, no candidate  -> reuses key-A?            recovery    (18/20 protected)
key-A present, key-B shown   -> dispatches on key-B?     permission  (0/20 protected)
no original key at all       -> defers, or invents one?  permission  (8/20 errors)
service                      -> rejects a reused key whose parameters differ
```

## Key Takeaways

- Run the changed-key and no-key conditions before you conclude an agent retries safely. In one control the same endpoint scored 80/80 on protected replay and 55/80 on inadmissible changed-key dispatch.
- The result belongs to an interface as well as an endpoint. With stated lookup semantics, Terra made 26/40 changed-key errors under the mandatory offered-key schema and 0/20 under the optional-candidate schema. Several conditions changed; the paper cannot isolate the cause.
- The display condition needs its own test. Luna's protected recoveries read 18/20 without a second key shown and 0/20 with one, and the paper declines a general rule either way.
- Put the replay guarantee where it is enforced. A service can reject a reused key when its parameters differ. That check covers a reused key, and Stripe generates a new request if a key is reused after the original is pruned.
- Report the action, its permission, and the recovery outcome together, which is the paper's own recommendation. Counting duplicates alone "rewards a model that always defers"; the explicit-contract control returned 762 deferrals and no completed recoveries.

## Related

- [Exactly-Once Enforcement Layer: Model, Harness or Contract](../agent-design/exactly-once-enforcement-layer.md) — which layer pays for a duplicate, and the competence premise this page tests from the other side
- [Idempotent Agent Operations: Safe to Retry](../agent-design/idempotent-agent-operations.md) — the client-side techniques a key contract sits on top of
- [Tool Operability: Interfaces That Survive a Lost Response](../agent-design/tool-operability-lost-responses.md) — what a tool interface has to expose before any recovery decision is scoreable
- [Tool-Call Success as Workflow Effect Evidence](tool-call-success-as-workflow-evidence.md) — the same substitution one level up, where a green call log stands in for the effect ledger
- [Recovery as a Separate Eval Axis (UndoBench)](../../verification/recovery-as-separate-eval-axis.md) — scoring recovery on its own axis, which is the measurement half of this page
