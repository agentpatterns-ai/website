---
title: "Defense-in-Depth Agent Safety for AI Agent Development"
description: "Layer multiple independent safety mechanisms so no single failure point can compromise an autonomous agent's behavior. Each layer catches what the others miss."
tags:
  - agent-design
  - security
  - source:opendev-paper
aliases:
  - defense in depth
  - layered security
  - multi-layer safety
last_reviewed: 2026-05-27
---

# Defense-in-Depth Agent Safety

> Layer multiple independent safety mechanisms so no single failure point can compromise an autonomous agent's behavior.

## Why Layers Matter

Any individual safety mechanism can fail. Prompt guardrails are bypassed by injection. Runtime checks miss edge cases. Approval gates cause fatigue-driven rubber-stamping. Defense-in-depth assumes every layer will eventually fail and ensures each catches what the others miss. Perplexity's response to NIST's AI-agent security RFI reaches the same conclusion: "No single layer is sufficient on its own; the non-deterministic nature of LLM reasoning ensures that any individual defense can be circumvented under sufficiently adaptive attack strategies" ([Li et al., 2026](https://arxiv.org/abs/2603.12230)).

The OPENDEV agent implements five independent safety layers, each operating at a different level of the stack ([Bui, 2026 §2.1](https://arxiv.org/abs/2603.05344)):

1. **Prompt guardrails** — safety instructions in the system prompt
2. **Schema restrictions** — subagents see only tools in their allowlist
3. **Runtime approvals** — user confirmation before dangerous operations
4. **Tool validation** — inputs validated before execution
5. **Lifecycle hooks** — pre-tool hooks can block execution with an explanation

Each layer is independent. Failure of one does not compromise the others ([Bui, 2026 §2.1](https://arxiv.org/abs/2603.05344)).

## Schema-Level Tool Filtering

The strongest form of tool restriction prevents the model from even knowing a tool exists. When a subagent's schema excludes write operations, the model cannot hallucinate calls to tools it has never seen ([Bui, 2026 §3.3](https://arxiv.org/abs/2603.05344)).

This is stronger than runtime rejection. A runtime check denies a forbidden call after the fact; schema filtering prevents the model from ever forming the intent. The attack surface shrinks before inference. See [Subagent Schema-Level Tool Filtering](../multi-agent/subagent-schema-level-tool-filtering.md) for implementation details.

## Three-Level Approval System

Runtime approvals use a three-level system ([Bui, 2026 §2.4.1](https://arxiv.org/abs/2603.05344)):

- **Manual** — every tool call requires explicit user approval
- **Semi-Auto** — only dangerous commands require approval; safe patterns execute freely
- **Auto** — all tool calls approved without user interaction

Approval persistence prevents fatigue: users grant blanket permission for safe patterns, and the agent remembers these grants across turns ([Bui, 2026 §3.3](https://arxiv.org/abs/2603.05344)). Pattern-based rules match command prefixes, danger patterns, and command types. Without persistence, repeated approval prompts train users to rubber-stamp everything — undermining the safety layer entirely.

## Designing for Approximate Outputs

Agents produce approximate outputs. Safety-conscious harness design accounts for this rather than treating it as a bug ([Bui, 2026 §3.4](https://arxiv.org/abs/2603.05344)):

- Auto-promote server commands to background tasks when the LLM misformats long-running commands
- Auto-install missing dependencies when the agent produces incomplete execution plans

These compensations reduce friction without compromising safety boundaries.

## Layer Interactions

The layers reinforce each other:

- Schema filtering reduces the surface area that runtime approvals must cover
- Lifecycle hooks catch what prompt guardrails miss
- Tool validation catches what schema filtering does not address (valid tool, invalid inputs)
- Approval gates provide human oversight for operations that pass all automated checks

No single layer is sufficient. The combination produces safety properties that no individual mechanism can achieve alone.

## Example

The following Claude Code agent definition shows three of the five safety layers applied at the agent configuration level: prompt guardrails, schema-level tool restrictions, and a lifecycle hook reference.

```markdown
---
name: deployment-agent
description: Deploys application builds to staging — never to production
tools:
  - Bash
  - Read
# Write and Edit are excluded from the schema: the agent cannot stage, commit,
# or modify files — it can only run deployment commands and read logs.
disallowed_tools:
  - Write
  - Edit
  - GitCommit
hooks:
  pre_tool: .claude/hooks/block-prod-commands.sh
---

You are a deployment agent for the staging environment only.
Never run commands that target production (prod, prd, live).
If a command targets production, refuse and explain why.
```

The corresponding `block-prod-commands.sh` hook adds a fourth layer — runtime validation — independent of the prompt guardrail:

```bash
#!/usr/bin/env bash
# Pre-tool hook: block any command containing production environment identifiers
COMMAND="$CLAUDE_TOOL_INPUT"
if echo "$COMMAND" | grep -qE '\b(prod|prd|live)\b'; then
  echo "BLOCKED: command targets a production environment" >&2
  exit 1
fi
```

Even if the prompt guardrail is bypassed by injection, the hook still blocks production-targeted commands. Schema filtering ensures the agent cannot commit changes even if both the prompt and hook are somehow circumvented. Each layer catches what the others miss.

## When This Backfires

Each layer adds configuration, testing, and maintenance cost — and misconfigured layers can block legitimate work or create false confidence while remaining ineffective.

- **Approval fatigue compounds across layers.** If every layer raises its own prompts, users approve everything to keep moving — converting the stack into security theater. The three-level system mitigates this only when safe patterns are classified correctly upfront.
- **Schema filtering limits legitimate capability.** Narrow subagent schemas cannot adapt outside their defined scope. In exploratory or general-purpose contexts, strict schema restrictions force constant operator intervention or fan-out into specialized agents where one broader agent would do.
- **Hooks and validation add latency.** In streaming, high-frequency, or real-time pipelines, per-call lifecycle hooks compound response time. A single well-tuned approval gate may beat five independent layers with inspection overhead at each level.

Apply the full five-layer stack to production agents with write access, external integrations, or multi-agent pipelines. For short-lived, read-only, or sandboxed internal tools, one or two targeted layers (schema restrictions plus lifecycle hooks) often deliver sufficient protection at lower cost.

## Key Takeaways

- Five independent safety layers: prompt guardrails, schema restrictions, runtime approvals, tool validation, lifecycle hooks
- Schema-level filtering is stronger than runtime rejection — the model cannot call tools it cannot see
- Approval persistence prevents fatigue-driven rubber-stamping
- Design for approximate outputs — compensate for LLM imprecision at the harness level
- Each layer assumes the others will fail; the architecture tolerates individual layer failures

## Related

- [Single-Layer Prompt Injection Defence](../anti-patterns/single-layer-injection-defence.md) — the anti-pattern this addresses
- [Subagent Schema-Level Tool Filtering](../multi-agent/subagent-schema-level-tool-filtering.md) — schema layer in depth
- [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md) — approval layer in depth
- [Hooks for Enforcement vs Prompts for Guidance](../verification/hooks-vs-prompts.md) — lifecycle-hook layer vs prompt layer
- [Deterministic Guardrails](../verification/deterministic-guardrails.md) — runtime validation layer
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — scopes what any single layer failure can damage
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — the threat model layers are defending against
- [Enterprise Agent Hardening](enterprise-agent-hardening.md) — applying these layers at organizational scale
