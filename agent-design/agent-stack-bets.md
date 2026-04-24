---
title: "The Agent Stack Bet: Architectural Decisions for Production Agents"
description: "Four architectural bets that move agent identity, context, durability, and orchestration from application code to the platform layer — with the conditions under which each bet pays off."
aliases:
  - agent stack architectural bets
  - production agent architecture bets
tags:
  - agent-design
  - security
  - tool-agnostic
---

# The Agent Stack Bet: Architectural Decisions for Production Agents

> Production agents hit a stack ceiling that prompting cannot solve — identity, context, durability, and orchestration have to move from application code into the platform layer, but only after scale or compliance makes the trade-off pay.

## The Stack Ceiling

Once models and prompts stop being the bottleneck, residual failures are governance debt, context siloing, and session-lifetime durability — none can be prompted away ([Addy Osmani: The Agent Stack Bet](https://addyo.substack.com/p/the-agent-stack-bet)). The underlying class has a standard name: OWASP's LLM06:2025 Excessive Agency traces damaging actions to excessive functionality, permissions, and autonomy ([OWASP LLM06:2025](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)).

Four bets follow. Each moves a concern one layer down the stack.

## Bet 1: Identity, Not Shared Credentials

Most production agents borrow a service account or a user's OAuth token and "promise — in application code, in a prompt — to stay inside the lines" ([Osmani](https://addyo.substack.com/p/the-agent-stack-bet)). A prompt is not a policy: any injection that subverts the prompt subverts the policy — the LLM06 root cause.

The bet is that agent identity moves into the network/IAM layer — an unforgeable identity where an unauthorised database connection refuses before any middleware runs. Claude Code exposes partial primitives: `PreToolUse` hooks and managed settings like `allowManagedPermissionRulesOnly` enforce policy outside the prompt ([Claude Code settings](https://code.claude.com/docs/en/settings)). Per-agent network-level identity is still work an enterprise builds. See [Enterprise Agent Hardening](../security/enterprise-agent-hardening.md) and [Scoped Credentials via Proxy](../security/scoped-credentials-proxy.md).

## Bet 2: Universal Context, Not Scraped Windows

Context fragments across tabs, dragged-in files, and bespoke session stores. Osmani argues integration must happen at the platform level — CRM, ERP, warehouse, tickets — and without it "the ceiling of agentic AI is slightly better spreadsheet autocomplete" ([Osmani](https://addyo.substack.com/p/the-agent-stack-bet)).

This bet is the most aspirational. MCP is the current attempt; no platform delivers universal cross-system context as a commodity. Teams betting here bet on an emerging standard, not a shipped one.

## Bet 3: Missions That Outlive Sessions

A session that survives a dropped WebSocket is the current bar. The enterprise bar is a mission that survives a quarter — procurement, compliance audits, incident investigations. Anthropic confirms the failure mode: long-running agents without structured durability run out of context mid-implementation and leave the next session guessing ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

The bet is durable, cloud-native execution with four guarantees: checkpointing that survives restarts and model-version changes; long-horizon memory with handoff between instances; missions that persist across credential rotations; and first-class HITL pause-and-ask primitives ([Osmani](https://addyo.substack.com/p/the-agent-stack-bet)). See [Agent Harness](agent-harness.md) and [Durable Interactive Artifacts](durable-interactive-artifacts.md).

## Bet 4: Platform, Not Plumbing

Custom memory, bespoke evals, handwritten retries, and homegrown observability are undifferentiated work. LangChain's framing converges with Osmani's: "Harnesses are intimately tied to memory, which means that by choosing an open harness you are choosing to own your memory" ([Deep Agents Deploy](https://blog.langchain.com/deep-agents-deploy-an-open-alternative-to-claude-managed-agents/)). The bet is graduating from local open primitives to a managed platform without a rewrite — the shape cloud, containers, and CI/CD took. The [managed vs self-hosted harness](managed-vs-self-hosted-harness.md) decision is the concrete form today.

## When the Bets Pay — and When They Do Not

The four bets are direction for enterprise-scale, long-horizon work. They are premature in three conditions:

- **Small teams with bounded scope.** Two people running one internal agent against one API get a smaller, more portable system from a scoped service credential and a session timeout.
- **Short-horizon interactive agents.** When the full lifecycle fits in one HITL session, checkpoint/resume adds latency with no reliability gain.
- **Pre-product-market-fit.** Iteration speed beats governance before PMF; early platform adoption locks in patterns the product outgrows.

Bet 1 is also incomplete without containment. Industry surveys report 58–59% of organisations have continuous monitoring but only 37–40% have purpose binding or kill-switches ([CSA AI Agent Governance Framework Gap, April 2026](https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-agent-governance-framework-gap-20260403/)). Observability pays off only when paired with enforceable containment.

## Key Takeaways

- The stack ceiling is real: identity, context, durability, and orchestration cannot be prompted into existence — they require platform-layer investment.
- A prompt is not a policy. Move agent identity to the network/IAM layer or accept that OWASP LLM06 risk stays unmitigated.
- Durability guarantees — checkpointing, handoff, mission persistence, HITL pause — distinguish long-running agents from demos that happen to run for a while.
- The four bets pay at enterprise scale and long horizons; they are overkill for small teams, short-horizon agents, and pre-PMF products.
- Observability without containment documents incidents; pair it with kill-switches and purpose binding or the gate is one-sided.

## Related

- [Managed vs Self-Hosted Agent Harness](managed-vs-self-hosted-harness.md)
- [Enterprise Agent Hardening](../security/enterprise-agent-hardening.md)
- [Agent Harness: Initializer and Coding Agent](agent-harness.md)
- [Durable Interactive Artifacts](durable-interactive-artifacts.md)
- [Agentic AI Architecture: From Prompt-Response to Goal-Directed Systems](agentic-ai-architecture-evolution.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](../security/scoped-credentials-proxy.md)
- [Blast Radius Containment](../security/blast-radius-containment.md)
- [Human-in-the-Loop Confirmation Gates](../security/human-in-the-loop-confirmation-gates.md)
