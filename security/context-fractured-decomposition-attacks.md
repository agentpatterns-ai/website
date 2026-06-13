---
title: "Context-Fractured Decomposition Attacks on Tool-Using Agents"
term: "Context-Fractured Decomposition Attacks"
description: "Cross-context jailbreaks split benign tool actions across modules and time; artifact provenance gaps recompose them downstream, lifting attack success by up to 28.3 percentage points."
tags:
  - security
  - agent-design
  - anti-pattern
  - tool-agnostic
  - arxiv
aliases:
  - context-fractured decomposition attack
  - CFD attack
  - artifact provenance gap exploitation
  - cross-context multi-step jailbreak
last_reviewed: 2026-06-12
maturity: emerging
---

# Context-Fractured Decomposition Attacks on Tool-Using Agents

> Defenders inspecting a single contiguous conversation miss attacks decomposed across tools, modules, and time — artifact provenance gaps recompose them downstream.

Context-Fractured Decomposition (CFD) is a family of cross-context multi-step jailbreaks that preserve benign-looking intermediate artifacts from an early interaction and elicit harmful behavior much later — potentially in a different agent instance or workflow stage — via individually innocuous tool actions whose risk emerges only under delayed artifact-mediated composition ([Lin et al., 2026](https://arxiv.org/abs/2606.09084)). The anti-pattern is shipping an agent defense that only inspects one contiguous conversation; the structural failure is **artifact provenance gaps** — the workspace files, logs, and persisted state that carry attack state across boundaries no single checkpoint sees.

## The Failure Mode

Tool-using agents persist state in artifacts: workspace files, transcripts, logs, memory entries, retrieval indexes. Most existing defenses — including multi-turn jailbreaks like Crescendo and Tree of Attacks — assume a single contiguous conversation visible to the defender ([Lin et al., 2026](https://arxiv.org/abs/2606.09084)). That assumption breaks in real agent pipelines, where enforcement is fragmented across tools, modules, and time, and where artifact provenance is often not tracked.

CFD exploits three structural properties:

| Property | Why it matters |
|---|---|
| **Fragmented enforcement** | A check on the planner's reasoning cannot see what a downstream tool reads from disk; a check on the tool call cannot see how the artifact was authored. |
| **Cross-instance reuse** | Artifacts persist across agent instances and workflow stages — payload staged in one session triggers in another. |
| **Untracked provenance** | The defender at the trigger site cannot tell whether a benign-looking artifact carries attacker-influenced spans. |

CFD raises attack success rate **by up to 28.3 percentage points** over state-of-the-art multi-turn baselines, even against strong single-turn judges ([Lin et al., 2026](https://arxiv.org/abs/2606.09084)).

## Why It Works

Language-model defenders cannot reason about state they cannot see. When an agent's enforcement boundary is a single contiguous conversation, attacks decomposed across tools, modules, or time slip through because the defender never observes the full composition — each individual step is benign by construction, and the harmful end-state emerges only when artifacts are recomposed downstream ([Lin et al., 2026](https://arxiv.org/abs/2606.09084)). The mitigation direction the paper proposes is **provenance lineage tagging**: every artifact carries a tag tracing the source spans that influenced it, and the wrapper around the model uses the tag to refuse actions whose lineage traces back to untrusted upstream artifacts — even when the current call looks benign. Independent corroboration exists in [MemLineage](https://arxiv.org/abs/2605.14421), which attaches cryptographic provenance and derivation lineage to every agent memory entry, and in execution-provenance approaches like [Agent-Sentry](https://arxiv.org/abs/2603.22868). The mechanism is structural: refusal training and data-centric defenses do not close it because the unsafe composition only exists at the trigger site.

## When This Backfires

Provenance instrumentation is not a free defense. Skip or downscope it when:

- **Single-conversation, single-tool deployments.** A chatbot with no persistent workspace, no cross-session artifacts, and no tool chains has no CFD surface; lineage tagging is pure overhead.
- **The provenance graph is built by the same model under attack.** When the LLM doing the tagging is the one being manipulated by injected content, the resulting graph faithfully encodes the attacker's view — a known failure mode of LLM-graphed provenance defenses, also called out in the [AuthGraph dual-graph approach](authgraph-dual-graph-injection-defense.md). Use an isolated builder or pair with another control.
- **Strong capability sandboxing already constrains blast radius.** When the agent cannot write executable config, has no egress, and holds no production credentials — see [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — CFD's "later trigger" cannot reach anything dangerous, and lineage tagging duplicates a binding control.
- **High-throughput, low-latency workflows.** Tagging every tool call and every workspace write has a per-step cost; in cost-sensitive batch agents the gate cost exceeds the long-tail risk.

Provenance tagging is *necessary* when artifacts cross enforcement boundaries, not *sufficient* on its own — pair it with capability sandboxing, not in place of it.

## Defender Checklist

Four questions decide whether a pipeline is exposed:

1. Does any artifact cross a tool, module, session, or agent-instance boundary?
2. At each enforcement point, can the defender observe the lineage of every artifact the action depends on?
3. Is the lineage builder isolated from the model being defended?
4. Does the capability sandbox bound what the eventual trigger can do?

A "no" on (2) plus a "no" on (4) is the high-risk configuration — turn-local defenses, a broad tool surface, and no provenance trace to constrain it.

## Key Takeaways

- CFD is a structural attack family, not a model failure — refusal training and data-centric defenses do not close it ([Lin et al., 2026](https://arxiv.org/abs/2606.09084)).
- The vulnerability surface is any pipeline where artifacts cross tools, modules, sessions, or agent instances without lineage tracking.
- Provenance lineage tagging is the proposed mitigation direction, corroborated independently by [MemLineage](https://arxiv.org/abs/2605.14421) and [Agent-Sentry](https://arxiv.org/abs/2603.22868); it must be paired with capability sandboxing, not used instead of it.
- Skip provenance instrumentation when artifacts never cross enforcement boundaries or when capability sandboxing already binds the blast radius.

## Related

- [Provenance-Aware Decision Auditing for LLM Agents](provenance-aware-decision-auditing.md) — runtime influence-provenance graph that traces every tool-call argument to its source span; complementary mitigation surface for CFD.
- [Dual-Graph Alignment for Indirect Prompt Injection Defense (AuthGraph)](authgraph-dual-graph-injection-defense.md) — pairs a clean authorization graph built from user intent with the execution-trace provenance graph; structural divergence flags injection-driven calls.
- [Three-Vector Evasion Taxonomy for Agent Security Tests](temporal-spatial-semantic-evasion-taxonomy.md) — temporal, spatial, semantic evasion axes; CFD is one realisation of the temporal+spatial combination.
- [Compositional Vulnerability Induction in Coding Agents](compositional-vulnerability-induction.md) — sibling decomposition-style attack against coding agents, where benign tickets compose into a vulnerable diff.
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — the capability-sandboxing control that bounds CFD's blast radius even when detection fails.
