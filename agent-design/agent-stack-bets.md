---
title: "The Agent Stack Bet: Architectural Decisions for Production Agents"
term: "Agent Stack Bet"
description: "Four architectural bets that move agent identity, context, durability, and orchestration from application code to the platform layer — with the conditions under which each bet pays off."
aliases:
  - agent stack architectural bets
  - production agent architecture bets
tags:
  - agent-design
  - security
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: established
---

# The Agent Stack Bet: Architectural Decisions for Production Agents

> Production agents hit a stack ceiling that prompting cannot solve: identity, context, durability, and orchestration must move into the platform layer.

## The stack ceiling

Once models and prompts stop being the bottleneck, the failures that remain are governance debt, context siloing, and session-lifetime durability. You cannot prompt any of them away ([Addy Osmani: The Agent Stack Bet](https://addyo.substack.com/p/the-agent-stack-bet)). This failure class has a standard name. OWASP's LLM06:2025 Excessive Agency traces damaging actions to too much functionality, too many permissions, and too much autonomy ([OWASP LLM06:2025](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)).

Four bets follow. Each moves a concern one layer down the stack.

## Bet 1: identity, not shared credentials

Most production agents borrow a service account or a user's OAuth token. They then "promise — in application code, in a prompt — to stay inside the lines" ([Osmani](https://addyo.substack.com/p/the-agent-stack-bet)). A prompt is not a policy. Any injection that subverts the prompt subverts the policy, which is the LLM06 root cause.

The bet is that agent identity moves into the network and IAM layer. An unforgeable identity refuses an unauthorized database connection before any middleware runs. Claude Code exposes partial primitives. `PreToolUse` hooks and managed settings like `allowManagedPermissionRulesOnly` enforce policy outside the prompt ([Claude Code settings](https://code.claude.com/docs/en/settings)). Per-agent network-level identity is still work an enterprise builds. See [Enterprise Agent Hardening](../security/enterprise-agent-hardening.md) and [Scoped Credentials via Proxy](../security/scoped-credentials-proxy.md).

## Bet 2: universal context, not scraped windows

Context fragments across tabs, dragged-in files, and one-off session stores. Osmani argues that integration must happen at the platform level: CRM, ERP, warehouse, and tickets. Without it, "the ceiling of agentic AI is slightly better spreadsheet autocomplete" ([Osmani](https://addyo.substack.com/p/the-agent-stack-bet)).

This bet is the most aspirational. MCP is the current attempt, but no platform delivers universal cross-system context as a commodity. The standard is also contested in practice. Perplexity said in March 2026 that it was stepping back from MCP internally in favor of REST APIs and CLIs ([Perplexity steps back from MCP](https://www.agent-engineering.dev/article/why-perplexity-is-stepping-back-from-the-model-context-protocol-mcp-internally)). Teams betting here bet on an emerging standard, not a shipped one.

## Bet 3: missions that outlive sessions

A session that survives a dropped WebSocket is the current bar. The enterprise bar is a mission that survives a quarter: procurement, compliance audits, and incident investigations. Anthropic confirms the failure mode. Long-running agents without structured durability run out of context mid-implementation and leave the next session guessing ([Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

The bet is durable, cloud-native execution with four guarantees: checkpointing across restarts and model-version changes; long-horizon memory with handoff between instances; missions that persist across credential rotations; and first-class human-in-the-loop pause-and-ask primitives ([Osmani](https://addyo.substack.com/p/the-agent-stack-bet)). See [Agent Harness](agent-harness.md) and [Durable Interactive Artifacts](durable-interactive-artifacts.md).

## Bet 4: platform, not plumbing

Custom memory, one-off evals, handwritten retries, and homegrown observability are undifferentiated work. LangChain's framing matches Osmani's: "Harnesses are intimately tied to memory, which means that by choosing an open harness you are choosing to own your memory" ([Deep Agents Deploy](https://blog.langchain.com/deep-agents-deploy-an-open-alternative-to-claude-managed-agents/)). The bet is moving from local open primitives to a managed platform without a rewrite, the same shape that cloud, containers, and CI/CD took. The [managed vs self-hosted harness](managed-vs-self-hosted-harness.md) decision is the concrete form today.

## When the bets pay off and when they do not

The four bets set the direction for enterprise-scale, long-horizon work. They are premature in three conditions:

- Small teams with bounded scope. A 2-person team running one internal agent against one API stays smaller and more portable with a scoped service credential and a session timeout.
- Short-horizon interactive agents. When the full lifecycle fits in one HITL session, checkpoint and resume add latency with no reliability gain.
- Pre-product-market-fit. Iteration speed beats governance before product-market fit, and early platform adoption locks in patterns the product outgrows.

Bet 1 is incomplete without containment. Industry surveys report that 58 to 59% of organizations have continuous monitoring, but only 37 to 40% have purpose binding or kill-switches ([CSA AI Agent Governance Framework Gap, April 2026](https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-agent-governance-framework-gap-20260403/)). Observability pays off only when you pair it with enforceable containment.

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
