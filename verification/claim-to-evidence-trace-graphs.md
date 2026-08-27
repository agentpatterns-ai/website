---
title: "Claim-to-Evidence Trace Graphs for Auditing Agent Runs"
term: "Claim-to-Evidence Trace Graph"
description: "Rebuild a finished agent session as a layered graph with typed edges so a reviewer can traverse backward from a claim to the artifacts and checks behind it."
aliases:
  - claim-to-evidence trace graph
  - claim-support graph
  - layered trace graph
  - evidence trace graph
tags:
  - testing-verification
  - observability
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-23
maturity: emerging
---

# Claim-to-Evidence Trace Graphs for Auditing Agent Runs

> A claim-to-evidence trace graph reorganizes a finished agent session so a reviewer starts at a claim and walks back to its evidence.

A claim-to-evidence trace graph is a review layer built over an agent session after it ends. It preserves the raw execution records, groups them into evidence units and workflow phases, turns artifacts into nodes, and joins those nodes with typed edges. A reviewer starts at a reported conclusion and follows support edges back to the work behind it ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)).

## When this is worth building

Build one when all four hold.

- Sessions run long enough that reconstruction costs reviewer time. The graph amortizes effort that "grows with session length and complexity" ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)). Below that, reading the log is cheaper.
- The agent emits lifecycle hooks and a session transcript. LEDGER's prototype hooks session, prompt, pre-tool, post-tool, permission, and stop events, and keeps the copied transcript as the source of truth. The authors note the approach "is not specific to Codex" ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)).
- The raw records stay inspectable beneath the graph, which indexes artifacts rather than replacing them.
- The claims you check depend on objects outside the message stream: a generated figure, a changed source file, a saved result table.

## The layers and the trust boundary

Three layers sit above the captured session. Trace Records preserve messages, tool calls, results, and links back to the transcript. Evidence Nodes group related records into one inspectable work unit. Workflow Nodes group those into phases labeled `context`, `plan`, `inspect`, `execute`, `validate`, or `claim` ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)).

| Edge | Relation it records |
|------|---------------------|
| `frames` | A plan or constraint sets context |
| `uses` | A work unit takes an artifact as input |
| `produces` | A work unit creates or changes an artifact |
| `informs` | A result shapes a later analysis or action |
| `checked_by` | A validation step checks a change or result |
| `supports` | Evidence justifies a claim or committed choice |

Edge types, from Table 3 of [Kim, Miao and Liu (2026)](https://arxiv.org/abs/2608.18398v1).

Conflating the layers is how this pattern misleads. Trace Records "come from deterministic transcript parsing", while the Evidence and Workflow layers "are produced by the tracer agent reading those records". The paper draws the line itself: "The Trace Records therefore stand on their own, while the structure built over them is an interpretation" ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)).

## Why it works

Review is evidence-centered and runs backward: which artifact holds the evidence, which action produced it, what check validated it. A chronological log "can show what happened without showing which events matter for checking a particular conclusion", so every review reconstructs those relations by hand ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)). Typed edges make the relation a stored property of the record instead.

Ordinary provenance bookkeeping cannot supply those edges. An independent survey gives the reason: agent execution introduces "semantic relations such as Support and Contradict, which depend on comparing the content of evidence and claims rather than only on bookkeeping about how artifacts were produced" ([Wang et al., 2026](https://arxiv.org/abs/2606.04990v4)). Something must read the content to add a `supports` edge, which is why that edge can be wrong.

The one measured effect comes from a separate group. Five domain experts rated a structured execution graph 4.29 for usability on a five-point scale across seven cases; reading "raw dialogues, execution logs, and source code" instead, they rated it 2.51 ([Gao et al., 2026](https://arxiv.org/abs/2606.15116v1)).

## When this backfires

- The inferred layer is wrong and nobody notices. LEDGER says the graph above the record layer "is not fully deterministic" and the tracer's choices "can be incomplete, unstable, or wrong" ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)). The repeated-run studies it calls for have not been run.
- Edge accuracy is imperfect even when measured. Graph of Trace reports an overall edge correctness ratio of 0.96 ([Gao et al., 2026](https://arxiv.org/abs/2606.15116v1)), and a wrong `supports` edge is a false pass on the claim you were checking.
- Long sessions blur the vocabulary. The edge types "are useful for review, but their boundaries can blur in long sessions" ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)), so value and failure mode scale together.
- The reviewer reads the graph instead of the artifacts. LEDGER treats it "as an audit aid rather than a source of truth" ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)); anyone who stops there inherits the tracer's inference errors.
- Retention and disclosure cost dominates. Fine-grained provenance "increases storage cost, privacy exposure, annotation burden, and system complexity" ([Wang et al., 2026](https://arxiv.org/abs/2606.04990v4)); traces carrying file contents are themselves a disclosure surface.
- You own the harness and can instrument deterministically. PROV-AGENT extends W3C PROV and captures lineage at execution time through decorators on agent tools ([Souza et al., 2025](https://arxiv.org/abs/2508.02866v3)). LEDGER's future work favors "deterministic or independently verifiable structure wherever possible" ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)).
- You need evidence the approach works. None exists yet: "no benchmark family provides strong end-to-end coverage" of the provenance capabilities involved ([Wang et al., 2026](https://arxiv.org/abs/2606.04990v4)).

## Example

LEDGER's second case study asked an agent to add a shortest-path utility to NetworkX that visits intermediate nodes in a given order. The first implementation passed its test run. Only afterward did the agent check how existing shortest-path functions handle missing nodes, then apply a guard patch, add a regression test, and run a second focused test ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)).

The final diff collapses that history. As the authors put it: "In the final diff these two stages are one function. In the trace they are separate phases with separate evidence, so a reviewer can tell which behavior came from the design and which came from an edge case the agent raised after the fact" ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)).

The completion claim collapses it further. One passing run is reported, while the trace records which check covered which behavior, so "a reviewer can therefore read the extent of the support behind the claim rather than only that support exists" ([Kim, Miao and Liu, 2026](https://arxiv.org/abs/2608.18398v1)).

## Key Takeaways

- Keep the deterministic record layer and the inferred graph layer visibly separate; a reviewer who cannot tell which is which cannot calibrate how far to trust the graph.
- Treat `supports` edges as leads to follow, not verdicts. Open the artifact an edge points at before accepting the claim.
- Reach for this above the session length where hand reconstruction actually costs you, and only where the agent emits hooks and a transcript to build from.
- If you own the harness, price deterministic instrumentation against post-hoc inference; the instrumented path removes the layer you would otherwise audit first.
- Ask what a claim's support covers, not whether support exists. One passing run reported as a single number hides which behavior each check exercised.

## Related

- [Verification Ledger for Tracking Agent Output Quality](verification-ledger.md) — records whether each check ran; the graph records what those checks are connected to
- [Evidence-Chain Run Logs: Bracket the Reported Symptom](evidence-chain-run-logs.md) — per-run proof that the reported symptom moved, scoped to one change rather than a whole session
- [Generative Provenance Records for Tool-Using Agents](generative-provenance-records.md) — the in-loop counterpart, emitted per sentence during generation instead of reconstructed afterward
- [Agent-Trace Data Layer: Storage for Hours-Long Traces](../observability/agent-trace-data-layer.md) — the storage tier holding the records a trace graph is built over
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — stage scoring across an eval corpus, the aggregate view rather than one session's audit path
