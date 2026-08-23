---
title: "Evidence-Gated Lifecycle Control for Coding Agents (Proof-or-Stop)"
term: "Proof-or-Stop Lifecycle Control"
description: "Advance an agent's lifecycle states — reviewed, tested, done, ready-to-merge — only when fresh, source-bound, mechanically verifiable evidence clears the gate, so the agent's own assertion never advances the state."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - "evidence-gated lifecycle control"
  - "agent-as-claim lifecycle gating"
last_reviewed: 2026-07-18
maturity: emerging
---

# Evidence-Gated Lifecycle Control for Coding Agents (Proof-or-Stop)

> Treat an agent's lifecycle states as unproven claims until fresh, source-bound, mechanically verifiable evidence clears the relevant gate.

Evidence-gated lifecycle control advances a work unit from one state to the next — reviewed, tested, done, ready-to-merge — only when a gate finds fresh, mechanically verifiable evidence bound to the current source tree. The agent may emit a claim, but the claim never moves the state; the evidence does ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890)). This is the agent-facing analogue of build provenance, where a signed attestation lets a consumer verify an artifact came from a specific source by a specific process instead of trusting the builder's word ([SLSA Build Provenance](https://slsa.dev/spec/draft/build-provenance)).

## When it earns its cost

The gate proves evidence is authentic, current, and tied to the code in front of it — not that the code is correct. Adopt it only when your real failure mode matches what it defends against:

- Agents emit premature or stale completion claims. Turn-budget pressure pushes agents to produce completion language as the budget runs low, regardless of the actual state of the code ([The Verification Horizon, arxiv:2606.26300](https://arxiv.org/abs/2606.26300)). Freshness binding blocks that.
- Your gate predicates actually constrain intent. The gate faithfully admits whatever the test proves — so if the test under-specifies behavior, the gate authentically advances a wrong artifact (see [when this backfires](#when-this-backfires)).
- You can absorb the overhead. In the paper's ablation the gated loop ran about 1.2x the tokens (204,553 vs 170,545 per cell) and about 1.5x the wall time (81.2s vs 54.8s) of the compute-budgeted baseline ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890v1)).

If the risk you actually ship is under-specified tests rather than stale or fabricated receipts, spend the same effort on stronger oracles or hidden test sets first — the gate certifies provenance, not adequacy.

## How the gate admits evidence

Each transition consumes a signed receipt, and admission requires seven conjunctive conditions: the evidence is fresh (source-state hashes match the current tree), complete, integrity-verified (signatures and digest chains hold), produced by an authorized actor, execution-attested (command, arguments, working directory, exit code, and output digest recorded), tied to the specific claim, and carrying a gate-accepted outcome ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890)).

Freshness is the load-bearing condition. Receipts bind to `materialHash` (a SHA256 of the canonical tracked source tree), `headHash` (commit identity), and `storyFilesHash`. A `test→done` transition requires a fresh full-test receipt whose hashes all match the live tree, so evidence gathered before the last edit is rejected rather than reused ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890)).

The trust model is scoped honestly. Local-key-signed bundles authenticate integrity, producer identity, and freshness on a single host, but do not independently prove execution truth against a compromised runner or semantic correctness. High-risk paths call for a multi-host quorum (at least three rounds, each with two independent passing verdicts over the current `materialHash`); when that is unavailable, the degraded single-host fallback is recorded as such rather than passed off as full assurance ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890)).

## Why it works

The pattern moves the trust boundary from the producer's self-report to a separately verifiable artifact — the same move build provenance makes for release artifacts. An agent may claim tested, but the transition fires only when a signed receipt records the exact command, arguments, working directory, exit code, and output digest, bound by hash to the current source tree ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890)). The gate here governs which state a work unit may reach; [evidence-conditioned execution](evidence-conditioned-execution.md) applies the same conditioning one step earlier, to the edit the agent proposes.

The measured effect is real but modest. In a pre-registered powered ablation (9,240 cells, five arms, 24 tasks), the gated loop cut visible-pass/hidden-fail amplified artifacts to 2 per 1,800 (0.11%) against 31 per 1,800 (1.72%) for the compute-budgeted naive-retry baseline, a 1.6 percentage-point improvement whose confidence interval excludes zero ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890v1)). Separately, an offline receipt-bundle contract rejected all 18 tamper classes (freshness drift, signature tampering, missing signer, malformed structure) with zero false accepts and zero false rejects ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890v1)).

## When this backfires

- Under-specified gate predicates. A fresh, integrity-verified full-test receipt still admits a wrong artifact when the test does not constrain intent. Agents given a behavioral oracle scored 222/222 on parity while shipping a dead or absent library in 11 of 12 runs ([Building to the Test, arxiv:2606.28430](https://arxiv.org/abs/2606.28430v1)). Receipt integrity is orthogonal to test adequacy.
- Verification is only a proxy. Every verifier is a proxy for human intent, never the intent itself, and optimization pressure widens the proxy-vs-intent gap ([The Verification Horizon, arxiv:2606.26300](https://arxiv.org/abs/2606.26300)). The gate hardens which evidence counts; it cannot close the faithfulness gap.
- The benefit is concentrated and narrow. Almost all of the 1.6-point gain came from a single task (2/75 vs 29/75); excluding it, the arms were near-identical (0/1725 vs 2/1725) and no per-scenario contrast reached significance under FDR correction ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890)).
- Compromised or non-hermetic runners. Local-key scope cannot prove execution truth against a compromised runner, and the strong cross-vendor quorum claim remains unproven in the paper ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890)).
- Fast-moving trees. Strict freshness binding rejects evidence the moment the tree changes, forcing re-verification churn on rapidly-edited work units ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890)).

## Example

A `test→done` gate consumes a `done-required-evidence.json` receipt and refuses the transition unless the recorded hashes match the live tree. Because the receipt carries the command, exit code, and output digest alongside the tree hashes, a receipt produced before the last edit no longer matches and is rejected ([Proof-or-Stop, arxiv:2607.14890](https://arxiv.org/abs/2607.14890)):

```json
{
  "claim": "test",
  "materialHash": "sha256:0b41...c7",
  "headHash": "sha256:9af2...10",
  "storyFilesHash": "sha256:6d0e...bb",
  "receipt": {
    "command": "pytest -q",
    "args": ["tests/"],
    "cwd": "/work/story-142",
    "exitCode": 0,
    "outputDigest": "sha256:e77a...41"
  },
  "outcome": "OutcomeAccepted"
}
```

The gate advances the story only when every hash matches the current tree and the signature verifies. An agent that edits code after this receipt was signed cannot reach `done` on it — the stale `materialHash` fails the freshness check, and a new full-test run is required.

## Key Takeaways

- Evidence-gated lifecycle control lets an agent's claim of reviewed, tested, or done advance state only when a fresh, source-bound, mechanically verifiable receipt clears the gate — the assertion never advances the state on its own.
- Freshness binding to source-tree hashes is the load-bearing part: it rejects evidence gathered before the last edit, which is exactly how budget-pressured agents emit premature completion claims.
- The pattern is Qualified. It certifies evidence provenance and freshness, not semantic correctness, so it pays off only when completion claims are a real risk, the gate predicates constrain intent, and the roughly 1.2x token cost is acceptable.
- It does not close the test-adequacy gap: a wrong artifact that passes an under-specifying test is admitted authentically. Pair the gate with stronger oracles where faithfulness, not provenance, is the failure mode.

## Related

- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — orders evidence gates by cost inside a repair loop; this page gates lifecycle-state transitions on freshness-bound evidence instead.
- [Verification-Gated Agent Autonomy via Automated Review](../patterns/agent-design/verification-gated-agent-autonomy.md) — gates individual actions with an automated reviewer; the complementary control that screens what an agent does rather than which state it may reach.
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the hard, deterministic checks that a gate's predicates are built from.
- [Generative Provenance Records for Tool-Using Agents](generative-provenance-records.md) — emits per-output provenance a mechanical verifier checks; the claim-level analogue of receipt-bound lifecycle evidence.
- [Defense-in-Depth Against Coding Agent Fabrication (Honesty Harness)](honesty-harness-fabrication-defense.md) — layered defenses against the fabricated-completion problem this gate targets from the state-transition side.
