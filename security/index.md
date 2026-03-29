---
title: "Security for AI Agent Development"
description: "Patterns and techniques for building agents that resist manipulation, protect sensitive data, and fail safely. Threat models identify the structural conditions"
tags:
  - security
  - agent-design
---
# Security

> Patterns and techniques for building agents that resist manipulation, protect sensitive data, and fail safely.

## Threat Models

Threat models identify the structural conditions that make agent systems exploitable and prescribe architectural mitigations.

- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — Risk emerges when an agent has private data access, untrusted input, and egress simultaneously; remove at least one leg from every execution path

## Prompt Injection

Prompt injection is the primary attack vector for agents that consume untrusted content. External instructions embedded in web pages, emails, documents, or API responses can redirect an agent's behavior at the model level.

- [Close the Attack-to-Fix Loop](close-attack-to-fix-loop.md) — Use new attack traces to adversarially train hardened model checkpoints immediately after discovery
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — Mandatory checkpoints before irreversible actions let humans catch injection-driven misbehavior before it causes harm
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md) — External content consumed by agents is an attack surface; malicious instructions can override agent instructions at the model level
- [RL-Trained Automated Red Teamers for Prompt Injection Discovery](rl-automated-red-teamers.md) — Train an LLM-based attacker with reinforcement learning to discover novel injection vectors before adversaries do
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md) — Narrow task scope limits both the attack surface and the blast radius of a successful injection
- [Use Explicit, Narrow Task Instructions to Reduce Agent Susceptibility to Injection](task-scope-security-boundary.md) — Precise, constrained instructions force injected content to contradict explicit directives rather than plausibly extend vague ones

**Anti-pattern:** [Single-Layer Prompt Injection Defence](../anti-patterns/single-layer-injection-defence.md) — Relying on one safeguard leaves agents vulnerable to attack vectors that layer does not address

## Sandboxing

Isolation limits what a compromised or misbehaving agent can affect.

- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) — Enforce both filesystem and network isolation simultaneously; neither boundary alone prevents exfiltration
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md) — Define guardrail rules only for tools your harness controls; external tools must enforce their own
- [Use a Public-Web Index to Gate Automatic URL Fetching](url-fetch-public-index-gate.md) — Cross-reference URLs against an independent crawl index before allowing automatic fetching

## Data Protection

Preventing sensitive data from entering agent context is cheaper than scrubbing it after the fact.

- [PII Tokenization in Agent Context](pii-tokenization-in-agent-context.md) — Replace sensitive fields with deterministic tokens before data reaches the model
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md) — Use permission rules and hooks to prevent agents from reading credentials and secrets
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — Keep broad credentials outside the sandbox; use an external proxy that attaches scoped tokens only to validated requests
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — Inject credentials as environment variables so secrets never appear in context or generated code

## Permissions

Excess permissions expand the blast radius of any failure or attack.

- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — Limit agent access to only what the current task requires; excess permissions directly amplify injection impact

## Code Injection

Code injection in multi-agent pipelines exploits agent trust in code it reads as input, distinct from prompt injection against a single agent.

- [Code Injection Attacks on Multi-Agent Systems: Coder-Reviewer-Tester as Defence](code-injection-multi-agent-defence.md) — A coder-reviewer-tester architecture with a dedicated security analysis agent achieves the highest resilience while recovering efficiency losses

## Tool Invocation

Tool invocation exposes attack surfaces distinct from prompt injection. Malicious tools exploit argument generation and return processing to leak context and execute arbitrary commands.

- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — Malicious MCP tools exploit argument generation to leak system prompts and chain description-plus-return injection to achieve remote code execution

## Supply Chain

Agents dynamically load tools from MCP servers, plugins, and registries at runtime. A tampered tool inherits the agent's full permissions.

- [Tool Signing and Signature Verification](tool-signing-verification.md) — Require cryptographic signature verification (Sigstore/Cosign) before an agent loads or invokes a tool

## Defense in Depth

No single safety mechanism is sufficient. Layered defenses ensure that failure of one layer does not compromise the agent.

- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — Layer five independent safety mechanisms so no single failure point can compromise agent behavior
- [Security Constitution for AI Code Generation](security-constitution-ai-code-gen.md) — Formalize security constraints as a versioned, machine-readable constitution that feeds agent specs, linters, and CI gates
