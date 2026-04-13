---
title: "Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party"
description: "Define sandbox rules only for tools your harness controls; document explicitly that external MCP and user-provided tools must enforce their own guardrails."
aliases:
  - sandbox scoping
  - tool-boundary sandboxing
tags:
  - agent-design
  - human-factors
---
# Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools

> When composing tools from multiple sources, define sandbox and guardrail rules only for the tools your harness controls — and document explicitly that external tools must enforce their own guardrails.

## The Boundary Problem

As agents gain access to more tools from multiple sources — built-in shell tools, MCP servers, user-provided tools — the temptation is to write a single blanket sandbox policy covering all of them. This creates a false security assumption: the blanket policy implies the harness enforces restrictions on tools it doesn't actually control.

Codex draws a clear boundary: the sandbox developer message describes restrictions only for the Codex-provided shell execution tool. MCP servers and user-provided tools are explicitly excluded from harness-level sandboxing. [Source: [Unlocking the Codex Harness](https://openai.com/index/unlocking-the-codex-harness/)]

## Why the Separation Matters

A harness can only enforce restrictions on tools it controls at the API level. When an MCP server receives a call, the harness has already handed off execution. The MCP server processes the request according to its own logic and returns a result — the harness cannot intercept or modify this behavior at the sandbox layer.

If harness sandbox rules are written as if they apply to MCP tools, two problems follow:

1. The model may believe the MCP tool is restricted by the sandbox rules, altering its behavior in ways the MCP tool doesn't expect
2. Developers reviewing the harness may believe MCP tool behavior is sandboxed when it is not — a false sense of security

## Implementation Pattern

Scope sandbox rules explicitly in the developer message:

```
SANDBOX RULES (applies to shell tool only):
- No network access from shell commands
- No writes outside /workspace
- No access to /etc, /home, or system directories

Note: MCP servers and user-provided tools operate under their own
authorization policies and are not subject to these sandbox rules.
```

The explicit note is auditable: any reviewer can see that MCP tools are excluded from harness-level sandboxing and know to check each MCP server's own guardrails separately. [Source: [Unlocking the Codex Harness](https://openai.com/index/unlocking-the-codex-harness/)]

## Per-Source Trust Boundaries

When building harnesses that compose heterogeneous tools, define trust boundaries per tool source. MCP server deployments span distinct trust contexts shaped by where the code originates (first-party, open source, third-party), where it executes, and which resources it can access. [Source: [MCP Security — CoSAI OASIS](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/model-context-protocol-security.md)]

| Tool Source | Who Enforces Guardrails |
|-------------|------------------------|
| Harness-owned shell tool | Harness sandbox rules |
| First-party MCP server | MCP server's own policies |
| Third-party MCP server | Third-party's policies (audit separately) |
| User-provided tools | User's responsibility; document this explicitly |

This makes accountability visible at design time rather than discovered during an incident.

## Auditing Third-Party MCP Tools

Third-party MCP servers require separate security review. The harness cannot be used as a proxy for trusting them. Questions to answer before deploying:

- What actions can this MCP server take?
- Does it have its own access controls and audit logging?
- What data does it access and what does it retain?
- What happens if the model is injected and calls this tool with crafted inputs?

Document the answers. The harness sandbox policy is not a substitute for this review.

## When This Backfires

Explicit scoping is not a cure-all. Specific failure conditions:

1. **Exclusion confusion**: Stating "sandbox rules apply to shell tool only" can leave the model uncertain whether MCP tools have any restrictions at all, leading it to invoke them in contexts where the absent policy would have said no. Pair the exclusion with a brief statement of what governs MCP calls (e.g., "MCP tools enforce their own authorization").
2. **False audit comfort**: A visibly scoped sandbox policy can create the impression that security has been addressed because the boundary is documented. Reviewers may skip auditing each MCP server's guardrails, assuming the explicit exclusion signals that MCP security was considered. Documentation of a gap is not closure of it.
3. **Drift across tool upgrades**: A harness-owned tool can be reimplemented as an MCP server (or vice versa) without updating the sandbox rules. The explicit scoping then misdescribes the current surface. Treat the "which tools the sandbox covers" list as part of tool registration, not a one-time doc edit.

## Key Takeaways

- Harness sandbox rules only control tools the harness owns; MCP tools execute under their own policies
- Writing sandbox rules that imply coverage of MCP tools creates false security assumptions
- Explicitly document in the sandbox policy which tools are and are not covered
- Define trust boundaries per tool source and audit each source separately
- Third-party MCP servers require independent security review that harness policies cannot substitute for

## Related

- [Tool-Invocation Attack Surface in Coding Agents](tool-invocation-attack-surface.md)
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md)
- [Security Constitution for AI Code Generation](security-constitution-ai-code-gen.md)
- [Credential Hygiene for Agent Skill Authorship](credential-hygiene-agent-skills.md)
- [Action-Selector Pattern: LLM as Intent Decoder with Deterministic Execution](action-selector-pattern.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Model a Single Agent Turn as Many Inference and Tool-Call Iterations](../agent-design/agent-turn-model.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Enterprise Agent Hardening](enterprise-agent-hardening.md)
- [Defense in Depth for Agent Safety](defense-in-depth-agent-safety.md)
- [Lethal Trifecta Threat Model for AI Agent Development](lethal-trifecta-threat-model.md)
- [Tool Signing and Signature Verification for Agents](tool-signing-verification.md)
- [Safe Outputs Pattern for Trustworthy Agent Responses](safe-outputs-pattern.md)
- [Permission-Gated Custom Commands](permission-gated-commands.md)
- [Task-Scope Security Boundary](task-scope-security-boundary.md)
- [Secrets Management for Agents](secrets-management-for-agents.md)
- [Prompt Injection Threat Model](prompt-injection-threat-model.md)
- [Sandbox-Enforced PII Tokenization in Agent Workflows](pii-tokenization-in-agent-context.md)
- [Code Injection Defence in Multi-Agent Pipelines](code-injection-multi-agent-defence.md)
