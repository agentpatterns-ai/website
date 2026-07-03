---
title: "Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party"
description: "Define sandbox rules only for tools your harness controls; document explicitly that external MCP and user-provided tools must enforce their own guardrails."
aliases:
  - sandbox scoping
  - tool-boundary sandboxing
tags:
  - agent-design
  - tool-agnostic
  - security
last_reviewed: 2026-06-12
maturity: adopted
---

# Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party

> Define sandbox rules only for tools your harness controls, and document explicitly that external tools enforce their own guardrails.

## The boundary problem

Agents now reach tools from many sources: built-in shell tools, MCP servers, and user-provided tools. It is tempting to write one blanket sandbox policy that covers them all. That policy creates a false security assumption. It implies the harness enforces restrictions on tools it does not actually control.

Codex draws a clear boundary. The sandbox developer message describes restrictions only for the Codex-provided shell execution tool. MCP servers and user-provided tools are excluded from harness-level sandboxing. [Source: [Unlocking the Codex Harness](https://openai.com/index/unlocking-the-codex-harness/)]

## Why the separation matters

A harness can only enforce restrictions on tools it controls at the API level. Take a harness-owned shell tool that wraps [`docker sbx`](docker-sbx-adoption.md). It sits inside the sandbox boundary the harness defines. An MCP server invoked from the same agent does not. When an MCP server receives a call, the harness has already handed off execution. The MCP server processes the request by its own logic and returns a result. The harness cannot intercept or change this behavior at the sandbox layer.

If you write harness sandbox rules as if they apply to MCP tools, two problems follow:

1. The model may believe the sandbox rules restrict the MCP tool, and change its behavior in ways the MCP tool does not expect.
2. Developers reviewing the harness may believe MCP tool behavior is sandboxed when it is not, a false sense of security.

## Implementation pattern

Scope sandbox rules explicitly in the developer message:

```
SANDBOX RULES (applies to shell tool only):
- No network access from shell commands
- No writes outside /workspace
- No access to /etc, /home, or system directories

Note: MCP servers and user-provided tools operate under their own
authorization policies and are not subject to these sandbox rules.
```

Any reviewer can audit the explicit note. They can see that MCP tools are excluded from harness-level sandboxing, and know to check each MCP server's own guardrails separately. [Source: [Unlocking the Codex Harness](https://openai.com/index/unlocking-the-codex-harness/)]

## Per-source trust boundaries

When you build harnesses that compose mixed tools, define trust boundaries per tool source. MCP server deployments span distinct trust contexts. Three factors shape each context: where the code originates (first-party, open source, or third-party), where it runs, and which resources it can reach. [Source: [MCP Security — CoSAI OASIS](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/model-context-protocol-security.md)]

| Tool source | Who enforces guardrails |
|-------------|------------------------|
| Harness-owned shell tool | Harness sandbox rules |
| First-party MCP server | MCP server's own policies |
| Third-party MCP server | Third-party's policies (audit separately) |
| User-provided tools | User's responsibility; document this explicitly |

This makes accountability visible at design time, not discovered during an incident.

## Auditing third-party MCP tools

Third-party MCP servers need separate security review. You cannot use the harness as a proxy for trusting them. Answer these questions before you deploy:

- What actions can this MCP server take?
- Does it have its own access controls and audit logging?
- What data does it access and what does it retain?
- What happens if the model is injected and calls this tool with crafted inputs across its [tool-invocation attack surface](tool-invocation-attack-surface.md)?

Document the answers. The harness sandbox policy is not a substitute for this review.

## When this backfires

Explicit scoping is not a cure-all. Here are specific failure conditions:

1. Exclusion confusion. Stating "sandbox rules apply to shell tool only" can leave the model uncertain whether MCP tools have any restrictions at all. The model may then invoke them in contexts where the absent policy would have said no. Pair the exclusion with a brief statement of what governs MCP calls, for example "MCP tools enforce their own authorization".
2. False audit comfort. A visibly scoped sandbox policy can create the impression that security has been addressed because the boundary is documented. Reviewers may skip auditing each MCP server's guardrails, assuming the explicit exclusion signals that MCP security was considered. Documentation of a gap is not closure of it.
3. Drift across tool upgrades. A harness-owned tool can be reimplemented as an MCP server, or the reverse, without updating the sandbox rules. The explicit scoping then misdescribes the current surface. Treat the list of which tools the sandbox covers as part of tool registration, not a one-time doc edit.

## Counterpoint: gateway-enforced uniform policy

The claim that a harness "cannot intercept" MCP calls holds for an in-process sandbox. Once execution hands off to an MCP client, there is no interposition point. It does not hold for every architecture. A dedicated MCP gateway or proxy is a separate interposition point that all agent-to-server traffic crosses. It evaluates each `tools/call` against a uniform policy and blocks violations before they reach the upstream server, with no changes to the servers themselves. [Source: [MCP and Zero Trust — Cerbos](https://www.cerbos.dev/blog/mcp-and-zero-trust-securing-ai-agents-with-identity-and-policy)]

This relocates a trust boundary rather than removing it. A gateway enforces coarse, uniform rules: which tools are callable, rate limits, and taint tracking. Each MCP server still owns the fine-grained authorization the gateway cannot see. The page's warning stands. Writing in-process shell-sandbox rules as if they cover MCP tools is still a mistake. The point is that "harness-level" need not mean "shell-sandbox-level". A proxy boundary is a legitimate place to enforce some cross-tool policy, as long as you document it as a distinct boundary and do not conflate it with the shell sandbox.

## Key Takeaways

- Harness sandbox rules only control tools the harness owns; MCP tools execute under their own policies
- Writing sandbox rules that imply coverage of MCP tools creates false security assumptions
- Explicitly document in the sandbox policy which tools are and are not covered
- Define trust boundaries per tool source and audit each source separately
- Third-party MCP servers require independent security review that harness policies cannot substitute for

## Related

- [Sandbox Runtime Comparison](sandbox-runtime-comparison.md)
- [Tool-Invocation Attack Surface in Coding Agents](tool-invocation-attack-surface.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Lethal Trifecta Threat Model for AI Agent Development](lethal-trifecta-threat-model.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Action-Selector Pattern: LLM as Intent Decoder with Deterministic Execution](action-selector-pattern.md)
- [Prompt Injection Threat Model](prompt-injection-threat-model.md)
