---
title: "Agent Sprawl: Unmanaged Sub-Agent and Skill Proliferation"
term: "Agent Sprawl"
description: "A catalog of sub-agents and skills grows faster than it is pruned, degrading routing accuracy and producing unowned, overlapping, undocumented capabilities."
tags:
  - agent-design
  - tool-agnostic
  - anti-pattern
aliases:
  - AI agent sprawl
  - sub-agent proliferation
  - agent catalog drift
last_reviewed: 2026-06-16
maturity: emerging
---

# Agent Sprawl: Unmanaged Sub-Agent and Skill Proliferation

> An agent and skill catalog grows faster than it is pruned, leaving unowned overlapping entries that degrade routing accuracy.

Agent sprawl is the structural failure mode that follows agent-native development without governance. Augment Code defines it as *"deploying agents without ownership, accountability, or governance"* ([Augment Code](https://www.augmentcode.com/guides/agentic-design-patterns)); IBM as *"the uncontrolled proliferation of AI agents across an organization"* ([IBM Think](https://www.ibm.com/think/topics/ai-agent-sprawl)). The shape is the same at every scale: the catalog accumulates entries faster than anyone prunes them.

Sprawl is *not* over-agentification. Over-agentification is a per-task design error — choosing an agent when a deterministic workflow suffices ([Augment Code](https://www.augmentcode.com/guides/agentic-design-patterns)). Sprawl is a fleet-management failure over time: each individual agent may have been the right choice at creation, but the catalog has no owner, no audit, no deprecation path.

## Symptoms

- **Ambiguous routing.** Two sub-agents have overlapping descriptions and the orchestrator picks unpredictably.
- **Orphaned agents.** The original author has moved on; nobody knows what the agent does or whether it can be deleted. Only 18% of organizations maintain a current and complete inventory of their AI agents (IBM IBV via [IBM Think](https://www.ibm.com/think/topics/ai-agent-sprawl)).
- **Silent duplication.** Two teams build near-identical agents without knowing the other exists; Salesforce's 2026 Connectivity Benchmark reports 50% of enterprise AI agents operate in silos ([IBM Think](https://www.ibm.com/think/topics/ai-agent-sprawl)).
- **No deprecation path.** Agents are created but never retired — what IBM calls *"a decommissioning failure"* ([IBM Think](https://www.ibm.com/think/topics/ai-agent-sprawl)).
- **Capability overlap by tool allowlist.** Two agents request the same tool surface for the same job, splitting the audit trail.

## Why It Works (As a Failure Mode)

Three compounding mechanisms degrade the catalog faster than authors can keep up. **Routing degradation** comes first: Anthropic's tool-authoring guidance warns that *"when tools overlap in function or have a vague purpose, agents can get confused about which ones to use,"* and *"too many tools or overlapping tools can distract agents from pursuing efficient strategies"* ([Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)). **Ownership drift** compounds it — Augment Code notes *"scaling multi-agent systems increases coordination drift as more roles, prompts, and handoffs accumulate"* ([Augment Code](https://www.augmentcode.com/guides/agentic-design-patterns)). **Coordination cost** is third: each new agent multiplies handoff surface. Gartner reports only 13% of organizations have the right AI agent governance, while projecting the average Fortune 500 will run over 150,000 agents by 2028 ([Gartner via IBM Think](https://www.ibm.com/think/topics/ai-agent-sprawl)).

## Mitigations

Applicable to a single repository, not just enterprise scale:

- **Named ownership.** Every agent and skill carries a current owner in frontmatter; orphans surface in audit.
- **Discoverability index.** A `/list-skills` / `/list-commands`-style command exposes the catalog to humans and the orchestrator, so duplicates are visible rather than buried.
- **Periodic catalog audit.** Quarterly review for agents never selected, duplicated tool allowlists, and overlapping descriptions.
- **Explicit deprecation.** Retired agents are archived or deleted — IBM names lifecycle management as a primary control ([IBM Think](https://www.ibm.com/think/topics/ai-agent-sprawl)).
- **Standardize creation.** When building a new agent is easier through the standard path than outside it, governance becomes self-reinforcing ([IBM Think](https://www.ibm.com/think/topics/ai-agent-sprawl)).

## When This Backfires

Calling proliferation "sprawl" too early suppresses the divergence a team needs to find its taxonomy:

- **Early-stage discovery (first ~6 months).** Teams need to discover which tasks benefit from a dedicated agent versus a workflow versus a shared skill. The Fortune 500-scale governance toolkit is wildly disproportionate to a five-person team running eight sub-agents.
- **Solo catalogs.** Anthropic's routing mechanism is real at any size, but ownership drift requires multiple authors and time. A one-person catalog runs without a registry until it scales.
- **Intentional fork divergence.** Two agents that look like duplicates may be deliberate forks for separate codebases or risk tiers — the [Copy-Paste Agent](copy-paste-agent.md) page treats the same trade-off.
- **Generate-then-prune sprints.** Specialization is not unconditionally beneficial — generalist agents can outperform specialists when concurrent execution improves throughput ([Predicting Multi-Agent Specialization](https://arxiv.org/abs/2503.15703)). Sprawl framing during the generation phase removes the variants needed for selection.

## Key Takeaways

- Sprawl is unmanaged proliferation, not proliferation itself — the failure is no owner, no audit, no deprecation path.
- Distinct from over-agentification: a per-task design error vs. a fleet-management failure over time.
- Three compounding mechanisms degrade the catalog: routing degradation, ownership drift, coordination cost growth.
- Mitigations applicable in a single repo: named owners, discoverability index, periodic audit, explicit deprecation.
- The framing fires only after the catalog stabilizes; during early discovery, governance overhead suppresses the divergence the team needs.

## Related

- [The Copy-Paste Agent](copy-paste-agent.md) — sibling failure mode: duplication causes independent drift; sprawl is the catalog-level equivalent.
- [Task-Specific Agents vs Role-Based Agents](../agent-design/task-specific-vs-role-based-agents.md) — task-specific design pays off only when paired with governance to prevent the sprawl it would otherwise produce.
- [Agents vs Commands](../agent-design/agents-vs-commands.md) — over-agentification, the per-task counterpart distinct from sprawl.
- [SDLC-Phase Skill Taxonomy](../workflows/sdlc-skill-taxonomy.md) — structural partitioning by lifecycle phase as a mitigation.
- [Agent-Discoverable Slash Commands](../agent-design/agent-discoverable-slash-commands.md) — discoverability index as a sprawl mitigation surface.
