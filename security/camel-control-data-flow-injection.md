---
title: "CaMeL: Defeating Prompt Injections by Separating Control and Data Flow"
description: "Architectural defense against prompt injection that separates trusted control flow from untrusted data flow, making injection attacks structurally impossible rather than probabilistically reduced."
tags:
  - agent-design
  - security
  - tool-agnostic
aliases:
  - CaMeL prompt injection
  - control data flow separation
  - capability-based agent security
---

# CaMeL: Defeating Prompt Injections by Separating Control and Data Flow

> Most prompt injection defenses are probabilistic. CaMeL eliminates whole classes of injection by construction — untrusted data retrieved by tools can never alter which tools are called or how.

## The Architectural Insight

Probabilistic defenses (detection classifiers, [adversarial training](close-attack-to-fix-loop.md), instruction hierarchies) reduce injection success rates but cannot eliminate them. CaMeL, proposed by Debenedetti et al. at Google DeepMind, takes a different approach: enforce the instruction/data boundary at the harness level so the model's susceptibility to injection is irrelevant. [Source: [Debenedetti et al., 2025](https://arxiv.org/abs/2503.18813)]

The key observation: prompt injection succeeds because untrusted data (tool outputs, web pages, emails) and trusted control flow (the user's query) enter the same context. CaMeL separates them.

## How CaMeL Works

CaMeL uses four components: [Source: [Debenedetti et al., 2025](https://arxiv.org/abs/2503.18813)]

**Privileged LLM (P-LLM)** — sees only the trusted user query. Converts it into an execution plan expressed as restricted Python. Never receives raw tool outputs or untrusted content.

**Quarantined LLM (Q-LLM)** — processes untrusted external data (emails, web pages, documents). Has no ability to invoke tools directly. The P-LLM delegates specific extraction tasks to it ("extract the sender's email address from this text"), receives the result, but never exposes the raw untrusted content to the P-LLM.

**Custom Python interpreter** — executes the P-LLM's plan. Performs taint tracking: every value carries capability metadata encoding its provenance and permitted uses. Security policies are enforced at tool-call time.

**Security policies** — capability labels on each value specify what can be done with it. If untrusted data tries to flow into a tool it is not permitted to reach, the interpreter blocks it regardless of what the model intends.

```mermaid
graph TD
    U[User query] -->|trusted| P[P-LLM]
    P -->|Python plan| I[Interpreter]
    I -->|delegate extraction| Q[Q-LLM]
    T[Tool outputs<br/>web pages<br/>emails] -->|untrusted| Q
    Q -->|extracted value<br/>+ capability label| I
    I -->|policy check| TC{Capability<br/>check}
    TC -->|permitted| A[Tool call]
    TC -->|blocked| B[Policy violation]

    style T fill:#b60205,color:#fff
    style U fill:#0e8a16,color:#fff
    style B fill:#b60205,color:#fff
    style A fill:#0e8a16,color:#fff
```

The P-LLM is never exposed to raw untrusted tokens. The interpreter enforces that data cannot alter control flow — which tools are called, in what order, with what parameters — regardless of injected content.

## Security Guarantee

CaMeL's security is architectural rather than behavioral. Because:

- the execution plan is derived solely from the trusted user query (via the P-LLM), and
- capability labels block untrusted data from reaching prohibited tool parameters,

a successful injection in a tool output cannot redirect the agent to call unauthorized tools or exfiltrate data over unauthorized channels. The guarantee holds even if the underlying models are susceptible to injection. [Source: [Debenedetti et al., 2025](https://arxiv.org/abs/2503.18813)]

## Trade-offs

**Task completion**: CaMeL solves 77% of AgentDojo tasks with provable security, versus 84% for an undefended system — a 7 percentage point cost for architectural security guarantees. [Source: [Debenedetti et al., 2025](https://arxiv.org/abs/2503.18813)]

**Latency**: The dual-LLM design roughly doubles model invocations. When the Q-LLM processes complex artifacts, latency can exceed 10 seconds — unsuitable for interactive applications. [Source: [Tallam & Miller, 2025](https://arxiv.org/abs/2505.22852)]

**Residual risk**: CaMeL does not protect against text-to-text attacks. An injected email can instruct the Q-LLM to produce a misleading summary, which the P-LLM then acts on. The structural guarantee covers tool invocation; it does not cover the semantic content of Q-LLM outputs. [Source: [Debenedetti et al., 2025](https://arxiv.org/abs/2503.18813)]

**Policy maintenance**: Security policies must be authored and maintained. As tool sets evolve, policies require updates. [Source: [Tallam & Miller, 2025](https://arxiv.org/abs/2505.22852)]

## Relation to the Dual LLM Pattern

CaMeL is a formally implemented instance of the [Dual LLM pattern](prompt-injection-resistant-agent-design.md). The conceptual pattern separates a privileged LLM from a quarantined LLM; CaMeL adds:

- a Python interpreter as the enforcement engine,
- capability labels for taint tracking,
- formal security policies checked at tool-call time.

The distinction matters: the conceptual pattern relies on careful system design and prompt discipline; CaMeL's interpreter enforces the boundary mechanically.

## When to Use CaMeL

Use CaMeL-style control/data separation when:

- agents process high volumes of untrusted external content (email, web, documents)
- data exfiltration or unauthorized tool invocation would cause significant harm
- the task-completion cost (77% vs 84%) is acceptable given the security context
- latency requirements allow for dual-LLM overhead

For lower-risk contexts, the [defense-in-depth](defense-in-depth-agent-safety.md) layered approach (schema filtering, confirmation gates, sandbox isolation) achieves strong probabilistic reduction with lower operational overhead.

## Key Takeaways

- CaMeL separates control flow (trusted user query → P-LLM) from data flow (untrusted tool outputs → Q-LLM), making injection-driven tool misuse structurally impossible.
- A capability-labeled Python interpreter enforces security policies at tool-call time, independent of model behavior.
- Achieves 77% task completion with provable security vs 84% undefended — a measurable utility cost for architectural guarantees.
- Does not protect against text-to-text attacks: the Q-LLM can still be misled into producing inaccurate summaries.
- Complements, rather than replaces, defense-in-depth; blast-radius containment and confirmation gates address residual risks CaMeL cannot eliminate.

## Related

- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md)
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — instruction-data separation is the structural defense against the two-channel injection chain described there
- [Single-Layer Prompt Injection Defence](../anti-patterns/single-layer-injection-defence.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Code Injection Defence in Multi-Agent Pipelines](code-injection-multi-agent-defence.md)
- [Discovering Indirect Injection Vulnerabilities in Your Agent](indirect-injection-discovery.md)
- [Action-Selector Pattern: LLM as Intent Decoder with Deterministic Execution](action-selector-pattern.md)
- [Guarding Against URL-Based Data Exfiltration in Agentic Workflows](url-exfiltration-guard.md)
