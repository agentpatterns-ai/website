---
title: "Managed vs Self-Hosted Agent Harness: Deployment Trade-offs"
term: "Managed vs Self-Hosted Agent Harness"
description: "Decision framework for choosing between managed agent services and self-hosted open-source harnesses — covering memory lock-in, compliance, model routing, and ops burden."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - managed agent harness
  - self-hosted agent harness
  - agent harness deployment
last_reviewed: 2026-06-12
maturity: established
---

# Managed vs Self-Hosted Agent Harness

> Choose between a managed agent service and a self-hosted harness across five signals: compliance, memory ownership, observability ownership, model routing, and ops capacity.

## The Decision

Managed agent services — [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) — provide a pre-built harness, [sandboxed execution](../security/sandbox-runtime-comparison.md), and hosted infrastructure in exchange for vendor coupling. Self-hosted open-source harnesses — [LangChain Deep Agents Deploy](https://blog.langchain.com/deep-agents-deploy-an-open-alternative-to-claude-managed-agents/), Cursor's self-hosted cloud agents — trade ops burden for control over data, model selection, and accumulated [agent memory](agent-memory-patterns.md).

The choice mirrors the classic SaaS vs on-prem decision but with a compounding factor: agents accumulate memory over time. Locking memory behind a proprietary API raises migration cost with every session.

## The Five Signals

### 1. Compliance and Data Residency

Hard regulatory constraints that mandate data never leave your network force self-hosted *execution* regardless of other factors — though, as the hybrid pattern below shows, that need not mean a fully self-hosted harness. Cursor's self-hosted cloud agents (March 2026) address this directly: "your codebase, build outputs, and secrets all stay on internal machines running in your infrastructure" with "tool calls handled locally" — capability-equivalent to hosted, but with no data crossing Cursor's boundary ([Cursor changelog](https://cursor.com/changelog)).

Managed services run workloads on vendor infrastructure by default. If your threat model includes vendor access to execution artifacts, the fully-hosted variant is out — though the managed/self-hosted line is blurrier than it first appears (see [The Hybrid Pattern](#the-hybrid-pattern)).

### 2. Memory Ownership

Harnesses are coupled to memory management. An agent harness "is intimately tied to memory — a key role of the harness is to manage context" ([LangChain, April 2026](https://blog.langchain.com/deep-agents-deploy-an-open-alternative-to-claude-managed-agents/)). When an agent learns from interactions — adapting to user preferences, accumulating domain knowledge, building an internal model of your codebase — that memory accumulates inside the harness.

With a managed service, that memory sits behind the provider's API; migration means resetting learned state — a cost that grows with every session. With a self-hosted harness, memory lives in your own databases and persists through vendor changes. This is the strongest argument for self-hosting when agents are long-lived or customer-facing, not just for batch tasks.

### 3. Observability Ownership

Managed services emit verdict-labelled traces only through their dashboards. Self-hosted lets you wire OpenTelemetry into the pipeline that already covers the rest of your services. If agent traces must flow into your existing stack — same backend, retention policy, and correlation IDs — that constraint is observability-shaped, not compliance-shaped. You cannot debug what you do not own; see [Agent Observability with OpenTelemetry](../observability/agent-observability-otel.md) for the OTel instrumentation contract that decides whether a managed surface can plug in at all.

### 4. Model Routing Flexibility

Managed services vary: Claude Managed Agents uses Anthropic models exclusively; Amazon Bedrock AgentCore supports multiple providers including OpenAI and Gemini ([AWS, 2026](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-is-now-generally-available/)). The pattern holds at the platform layer — each managed service binds you to its approved roster, even one spanning providers. Self-hosted harnesses drop the roster and route across any provider: Deep Agents Deploy supports OpenAI, Google, Anthropic, Azure, Bedrock, Fireworks, Baseten, Open Router, and Ollama, switchable per deployment or task ([LangChain, April 2026](https://blog.langchain.com/deep-agents-deploy-an-open-alternative-to-claude-managed-agents/)).

If you need multi-model routing, cost-based routing across providers, or model migration without re-platforming, self-hosted gives you that. If one provider's flagship model covers your workload, managed removes the routing overhead.

### 5. Ops Capacity

Self-hosted means deploying and operating the harness, orchestration layer, sandboxes, and memory stores. Deep Agents Deploy cuts this to a single `deepagents deploy` command that provisions a multi-tenant, horizontally scalable server with 30+ endpoints — but you still own the infrastructure ([LangChain, April 2026](https://blog.langchain.com/deep-agents-deploy-an-open-alternative-to-claude-managed-agents/)). Managed services — Claude Managed Agents in particular — handle all of it: "no need to build your own agent loop, sandbox, or tool execution layer" ([Anthropic, 2026](https://platform.claude.com/docs/en/managed-agents/overview)). The trade-off is losing the ability to customize those layers.

## Decision Flow

```mermaid
graph TD
    A[Start] --> B{Hard compliance or<br>data residency requirement?}
    B -->|Yes| C[Self-hosted]
    B -->|No| D{Long-lived agents<br>with accumulating memory?}
    D -->|Yes| E{Memory migration<br>cost acceptable?}
    E -->|No| C
    E -->|Yes| OBS{Agent traces must flow<br>into your OTel stack?}
    D -->|No| OBS
    OBS -->|Yes| C
    OBS -->|No| F{Multi-provider model<br>routing required?}
    F -->|Yes| C
    F -->|No| G{Ops team to run<br>harness infrastructure?}
    G -->|No| H[Managed]
    G -->|Yes| I[Either — evaluate<br>lock-in tolerance]
```

## The Hybrid Pattern

Cursor's self-hosted cloud agents (March 2026) demonstrate a hybrid: managed orchestration and agent definitions hosted by Cursor; execution and tool calls running on customer infrastructure. You get the managed control plane without placing code, secrets, or build artifacts on vendor machines.

This is the pattern to consider when compliance concerns are about execution artifacts specifically, not orchestration metadata.

The hybrid is not Cursor-specific. Managed providers increasingly offer self-hosted execution as a first-class mode: Claude Managed Agents supports self-hosted sandboxes where "the agent's code, filesystem, and network egress never leave your environment," positioned for "your organization's own compliance and audit controls" ([Anthropic](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes)). So the data-residency signal alone rarely forces a fully self-hosted harness. What stays genuinely managed-only is narrower: in that case, [accumulated memory](agent-memory-patterns.md) is unsupported with self-hosted sandboxes, and managed sessions remain ineligible for Zero Data Retention and HIPAA BAA ([Anthropic](https://platform.claude.com/docs/en/managed-agents/overview)). Weigh those residual constraints, not the deployment label.

## Key Takeaways

- Compliance and data residency are hard constraints — evaluate them first; other factors only matter if you have a choice
- Memory accumulation behind a proprietary API compounds lock-in over time — this is the structural difference from classic SaaS vs on-prem
- Multi-model routing flexibility requires self-hosted; managed services bind you to their provider's model set
- The hybrid model (managed control plane, self-hosted execution) reduces ops burden while keeping execution artifacts on your infrastructure

## Related

- [Harness Engineering](harness-engineering.md) — the discipline of designing agent environments for reliable output
- [Agent Harness: Initializer and Coding Agent](agent-harness.md) — the two-phase harness pattern for long-running work
- [Cursor Self-Hosted Cloud Agents](../tools/cursor/self-hosted-cloud-agents.md) — hybrid deployment: managed orchestration, self-hosted execution
- [Cost-Aware Agent Design](cost-aware-agent-design.md) — routing by complexity, relevant when multi-provider routing is in scope
- [Cross-Vendor Competitive Routing](cross-vendor-competitive-routing.md) — assigning competing agents to the same task, a self-hosted-only pattern
- [Session Harness Sandbox Separation](session-harness-sandbox-separation.md) — the three-primitive architecture inside either deployment mode
- [Agent Observability with OpenTelemetry](../observability/agent-observability-otel.md) — the OTel instrumentation contract that determines whether a managed surface can plug into your existing observability stack
- [Sandbox Runtime Comparison](../security/sandbox-runtime-comparison.md) — sandbox primitive comparison, the same in either deployment mode but with different ownership of the boundary
