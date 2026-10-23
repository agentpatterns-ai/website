---
title: "A Scoped Token as Proof the Action Was Wanted"
term: "Scope-as-Intent"
description: "A capability gate denied all 83 out-of-scope deletions in one 1,350-trial sandbox and let an induced in-scope deletion through in 31 of 42 trials. Scope is not intent."
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
aliases:
  - scoped token as intent evidence
  - induced in-scope tool call
  - capability gate as authorization proof
last_reviewed: 2026-10-22
maturity: emerging
status: current
---

# A Scoped Token as Proof the Action Was Wanted

> A capability gate checks whether a path lies inside the token's scope, and has no term for whether anyone wanted the call.

A passing scope check records what the gate tested. It is not evidence the call was intended. Reading it as intent evidence is scope-as-intent. One sandbox puts both halves of that mistake in one table, over 1,350 trials on GPT-5.1, Claude-Sonnet-5 and Gemini-2.5-Pro. What changed on disk was read from a before-and-after filesystem snapshot, "independently of any gate message" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)).

| What the gate saw | Count | Executed |
|---|---|---|
| Records forged, tampered, replayed or unsigned, rejected at admission | 750 trials | 0 |
| Deletions aimed outside the token scope (28 outside-scope, 21 traversal, 34 symlink) | 83 attempts | 0 |
| Deletions aimed inside the token scope, induced by adversarial content | 42 trials | 31 |

## The two conditions

Both have to hold. Break either and the gate is the boundary it looks like.

- The content arrives on a channel the admission check accepts. A legitimate ingestor signs attacker-controlled text, so the signature verifies and the record is admitted with authentic provenance. Where the record fails that check instead, it never gets in: all 750 were rejected at admission, "each by the check it targets (invalid MAC; record expired; nonce already consumed; no record envelope)" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)).
- The action it names falls inside a capability the runtime already holds. Reach past the token and the gate is the boundary: "all were denied for scope violation and none executed" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)). Those 83 attempts cluster on sixteen payloads and three models, so read the interval loosely.

## Why it works

Admission answers who signed a record. The scope check answers where a path resolves. Neither predicate carries a term for purpose, so text on a signed channel naming an in-scope target makes every check return true. The paper calls this a property of channel authentication rather than an implementation defect: "channel authentication establishes *who signed* a record, not whether its content *carries authority*. Distinguishing authenticated origin from delegated authority requires semantic authorisation, a harder problem that external signing alone cannot solve" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)).

So the gate is not malfunctioning. "The gate did what its policy specifies; the policy cannot distinguish an induced in-scope request from a wanted one" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)). The model does not cover the difference either. A request carrying no authority claim at all, only a reason, "is executed, with no reflection instruction, by all ten endpoints tested" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)).

## Read the taxonomy before the rate

The two zeros in that table describe the attack classes someone enumerated. Three qualifiers travel with them.

- It is a "*functional-correctness evaluation* (integration testing of deterministic cryptographic and capability checks), not a stochastic security evaluation" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)). Token leakage, signer compromise, key rotation and check-to-use races sit outside the trials.
- Coverage is per channel: "Cover every channel that accepts external input: memory-only signing leaves fake tool output untouched" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)).
- The check is only as good as its path resolution. Across 34 symlink attempts lexically inside the scope, a link-resolving check denied every one and a prefix-containment check allowed every one. [Judging a write by its spelled path](spelled-path-permission-scope.md) covers that half.

The layer below is often missing too. An audit of LangChain and LangGraph, LlamaIndex and the Stripe Agent Toolkit found "all three provide capability gating by default, but none provides a deterministic fail-closed per-call value authorization gate by default" ([Mellafe Zuvic, 2026](https://arxiv.org/abs/2606.28679v1)). Build that gate first; this page is the residual after it.

## When this backfires

- The destructive action is the task. For an agent clearing `/workspace/temp`, nothing separates an induced deletion from a wanted one. A reversible backend is the control there, and no authorization layer substitutes for it.
- A per-call token already closes it. Mint one capability per artifact just before dispatch and the induced and the wanted request become the same request, at the cost of minting and latency.
- Widening enforcement breaks legitimate work. In a 4,500-trial policy-routing validation attack success fell from 18.5% to 0.0%, and "full enforcement also blocks every benign privileged request from a user or tool source" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)).
- A human approves the resolved target. Inducement is caught at that approval, so the availability cost above buys nothing.
- Rates do not transfer. Matched GPT-4.1 cells differed between API fingerprints, 1 of 126 against 16 of 74, and the guidance is to "Treat API measurements as deployment snapshots" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)).

## Example

Scenario 7 of the sandbox is the shape to copy into a threat model. The runtime holds a `file_delete` token scoped to `/workspace/temp` and issues it before the model is called. The token is never shown to the model, and the gate checks it against the path parsed from the model's own emitted arguments. A validly signed record from a tool source then asks for a deletion. Sixteen payloads cover four subtypes: a target inside the scope, a target outside it, a traversal path, and a symlink inside the scope that resolves outside it ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)).

Three subtypes are the gate's case and it denies all three. The fourth bypasses nothing. The payload asks for a file the token covers, the gate allows it, and the snapshot confirms the deletion in 31 of 42 trials. "No file outside a token's scope was removed in any of the 1,350 trials" is true at the same time ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)).

The corrected version of that fourth subtype is not a tighter predicate. It is a backend the deletion can be undone on, or an approval that names the resolved path, as the paper's own guidance has it: "External authorisation for consequential actions, independent of model output, is required regardless of any measured rate" ([Leong, 2026](https://arxiv.org/abs/2608.28502v2)).

## Key Takeaways

- Write down which predicates your gate evaluates, and read a pass as evidence about those and nothing else.
- Put a reversible backend behind any destructive action whose scope an issued token already covers. That is where the 31 of 42 lands, and no tightening of the scope predicate reaches it.
- Quote a zero-bypass number with its taxonomy attached. This one excludes token leakage, signer compromise, key rotation and check-to-use races by construction.
- Apply the admission check to every channel that accepts external input, because signing memory writes leaves tool output unmediated.
- Price the availability cost before widening enforcement: the configuration that reached 0.0% attack success also refused every benign privileged request.

## Related

- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](../../security/authority-confusion-untrusted-context.md) — prescribes the dispatch-layer fields that separate who suggested an action from who authorized it; this page is what remains once those fields are in place.
- [Per-Agent Capability Stores Beat One Task-Wide Allowlist](../../security/per-agent-capability-scoping.md) — splits the authority ceiling per principal, which shrinks the in-scope residual without removing it.
- [Judging a Write by Its Spelled Path (Spelled-Path Scope)](spelled-path-permission-scope.md) — the resolution half of a scope check, where the path a guard reads and the path a kernel opens come apart.
- [Monotonic Capability Attenuation for Composition-Safe Tool Use](../../security/monotonic-capability-attenuation.md) — attenuates authority through composition, the axis this page's token does not cover.
- [Trusting Claimed Prior Approval in Agent Review Gates](trusting-claimed-prior-approval.md) — the same substitution one layer up, where a cited approval stands in for a checked one.
