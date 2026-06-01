---
title: "Subprocess-per-Session Hosting Model: Four Session-Lifecycle Topology Patterns"
description: "Pick a session-lifecycle topology for self-hosted Agent SDK deployments — ephemeral, long-running, hybrid, or multi-agent container — by matching workload class to subprocess, container, and transcript-persistence lifetimes."
tags:
  - agent-design
  - claude
applies_to: "claude-code@2.x"
aliases:
  - subprocess-per-session hosting
  - agent SDK session lifecycle patterns
  - ephemeral long-running hybrid multi-agent container
last_reviewed: 2026-05-30
status: current
---

# Subprocess-per-Session Hosting Model

> The Agent SDK's subprocess-per-session model picks one of four hosting topologies — ephemeral, long-running, hybrid, or multi-agent container — by matching workload to lifetimes.

The Agent SDK spawns one `claude` CLI subprocess per session — "that subprocess owns the shell, the working directory, and the JSONL session transcripts on local disk" ([Claude Agent SDK: Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). Three orthogonal lifetimes — subprocess, container, transcript-persistence — define a 3D design space; the four patterns name the four operationally distinct corners. Choose the wrong corner for the workload and you get vanished transcripts, OOM containers, cross-agent settings leakage, or wasted operational cost.

## The Three Lifetimes That Define the Choice

| Lifetime | Decision | Failure mode if wrong |
|----------|----------|------------------------|
| Subprocess | One task vs. many turns held open | OOM growth over long sessions ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)) |
| Container | Per-task vs. per-session vs. across-idle vs. shared | Pet-container ops cost or vanished sessions on restart |
| Transcript persistence | Local disk only vs. mirrored to `SessionStore` | "Shutting a container down without a `SessionStore` configured loses the transcript with it" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)) |

Three classes of state live on the container's filesystem and "none of them survive a container restart, a scale-down, or a move to a different node" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)): session transcripts under `~/.claude/projects/`, `CLAUDE.md` memory files at user and project tier, and working-directory artifacts. Only transcripts mirror to a `SessionStore`; memory and artifacts need their own strategy ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)).

## The Four Patterns

| Pattern | Container lives | SessionStore | Best for |
|---------|-----------------|--------------|----------|
| **Ephemeral** | Per task; destroyed on completion | Optional | Bug fix, extraction, transformation |
| **Long-running** | Across many sessions; pinned by hash | Optional (cross-container migration) | Chat bots, email agents, content-serving agents |
| **Hybrid** | Per active period; suspended on idle | **Required** | Personal project manager, deep research, support agent |
| **Multi-agent container** | One container, many subprocesses | Optional | Multi-agent simulation in a shared environment |

### Ephemeral sessions

Container-per-task. The container runs "a one-shot entrypoint that calls the SDK and exits" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). Workloads Anthropic names directly: "bug investigation and fix, invoice and receipt extraction, document translation, and media transformation."

No `SessionStore` needed when the task completes inside one container's lifetime. Cold-start latency dominates the SLO — provider choice matters: "Ephemeral patterns need sub-second starts" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)).

### Long-running sessions

Persistent container instances host multiple SDK subprocesses, with each active session pinned to one subprocess. Workloads: "an email agent that triages and responds to incoming mail, a site builder that hosts a per-user editable site through container ports, and a chat bot that handles continuous traffic from a platform like Slack" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)).

Horizontal scaling uses a load balancer plus **consistent hashing on `sessionId`**: "A pinned session keeps hitting the same container, and therefore the same running subprocess, until it is evicted or the container restarts" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). Size each host with `agents per host = (host RAM - overhead) / per-session RAM ceiling`; the 1 GiB starting point is a floor measured per workload.

### Hybrid sessions

Ephemeral containers that hydrate from a `SessionStore` on startup and persist back on shutdown. Best for sessions that "sit idle between" interactions: "a personal project manager with intermittent check-ins, deep research that pauses and resumes over hours, and a customer support agent that loads ticket history across interactions" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)).

The `SessionStore` is "required for this pattern, not optional" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). Reference adapters ship for S3, Redis, and Postgres; the conformance suite validates custom adapters ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)). Mirror writes are best-effort: failures emit a `{ type: "system", subtype: "mirror_error" }` message and the query continues without retry — alert on these if store durability matters.

### Multi-agent container

Multiple subprocesses in one container, "for example multi-agent simulations where the agents interact with each other in a shared environment" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). The collision risk is structural and isolation is the operator's job: "Give each agent its own working directory so they do not overwrite each other's files, and isolate settings loading so per-agent `CLAUDE.md` files do not leak across agents" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). Four levers must be applied together for safe multi-tenant or multi-agent isolation: `settingSources: []`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, per-tenant `CLAUDE_CONFIG_DIR`, and per-tenant `cwd` on every `query()` call ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)).

## Why It Works

The four-pattern split is exhaustive because the subprocess model exposes three orthogonal lifetimes the operator must independently choose, and each pattern's cold-start, persistence, and cost profile differs. The mechanism is documented as causal in the primary source: "Every hosting decision on this page follows from how the SDK runs the agent" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). Naming the four corners explicitly lets operators pick by workload class instead of drifting into "long-running by default." The same three-layer split (session log, stateless harness, replaceable sandbox) is reached independently by LangChain Deep Agents Deploy ([LangChain, 2026](https://blog.langchain.com/deep-agents-deploy-an-open-alternative-to-claude-managed-agents/)) and Anthropic's Managed Agents ([Anthropic Managed Agents](https://www.anthropic.com/engineering/managed-agents)) — convergent evidence the topology is structural, not vendor-specific.

## When This Backfires

- **Stateless API wrapper analogy.** Teams treating the SDK like a stateless HTTP wrapper (one Lambda per call, no `SessionStore`, no `cwd` discipline) see sessions disappear on every cold start. The subprocess model assumes the container holds load-bearing state — the hosting page opens with exactly this warning: "Hosting it is not like hosting a stateless API wrapper" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)).
- **Long-running container without subprocess recycling.** Memory grows with session length and tool activity; the page lists "Memory growth over long sessions" as a known limitation with the remediation "cap session length or recycle subprocesses periodically" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). A long-running pattern that never recycles becomes a pet container that OOMs.
- **Hybrid pattern without `SessionStore`.** The pattern is undefined without one: "Shutting a container down without a `SessionStore` configured loses the transcript with it" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). Shipping hybrid topology while still designing the persistence story leaks data on every idle timeout.
- **Multi-agent container with shared `cwd`.** Two subprocesses defaulting to the same working directory overwrite each other's files; two reading the same `CLAUDE.md` leak settings across agents. Without per-agent `cwd`, `settingSources: []`, per-agent `CLAUDE_CONFIG_DIR`, and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` applied together, the multi-agent pattern is unsafe ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)).
- **Ephemeral pattern for sessions needing cross-task memory.** A bug fix that needs to remember decisions across container boundaries is misclassified — ephemeral discards everything on completion. Hybrid is the correct pattern.
- **Self-hosting when no infrastructure requirement justifies it.** The page itself flags the alternative: "If you do not need infrastructure control, custom isolation, or your own data plane, consider Managed Agents instead" ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting)). The "pet container" anti-pattern in Anthropic's Managed Agents post — "if a container failed, the session was lost. If a container was unresponsive, we had to nurse it back to health" ([Anthropic Managed Agents](https://www.anthropic.com/engineering/managed-agents)) — is the failure mode the four-pattern taxonomy exists to help operators avoid.

## Example

A SaaS team ships a customer-support agent. Users return to threads days later; idle windows between interactions are long; total active session time per ticket is minutes.

**Wrong choice — long-running**:

```text
Pool of containers behind LB, consistent hashing on sessionId.
A ticket idle for 24h still holds RAM in its pinned container.
Eviction strategy is unbounded: holding N tickets per container.
Container restart at deploy => active sessions lose transcript
  unless SessionStore is bolted on after the fact.
```

**Right choice — hybrid**:

```typescript
import { query, type SessionStore } from "@anthropic-ai/claude-agent-sdk";

const sessionStore: SessionStore = /* S3, Redis, or Postgres adapter */;

for await (const message of query({
  prompt: userInput,
  options: {
    resume: sessionId,        // looked up from your DB by user
    sessionStore,             // mirrors transcripts to durable storage
    cwd: `/work/${sessionId}`, // per-session working directory
  },
})) {
  // ...
}
```

The container spins down during the idle gap; the next interaction provisions a new container that hydrates from the `SessionStore` and resumes. Container restarts are no longer state-loss events ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)). The structural change is moving authoritative state off the container's local disk and into a substrate the container does not own.

## Key Takeaways

- One subprocess = one session = one bundle of disk-local state; "none of them survive a container restart, a scale-down, or a move to a different node" without explicit persistence ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting))
- The four patterns are an exhaustive partition of the design space: ephemeral (per-task container), long-running (persistent pool with consistent-hashed sessions), hybrid (ephemeral with `SessionStore`), multi-agent (many subprocesses, one container)
- The `SessionStore` is optional for ephemeral and long-running, **required** for hybrid, and a mirror-only adapter — `CLAUDE.md` memory and working-directory artifacts need their own persistence strategy ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage))
- Multi-agent container isolation requires four levers together: per-agent `cwd`, `settingSources: []`, per-agent `CLAUDE_CONFIG_DIR`, and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` — any one missing leaks settings or files across agents
- The four-pattern taxonomy applies only when self-hosting is the right choice — when infrastructure control, custom isolation, or your own data plane is not required, Managed Agents is the lower-cost alternative ([Hosting](https://code.claude.com/docs/en/agent-sdk/hosting))

## Related

- [Cloud-Agent Three-Layer State Decoupling](cloud-agent-state-layer-decoupling.md) — the state-shape layer above this one: split agent loop, machine state, and conversation state into independently restorable substrates
- [Session Harness Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — the three-primitive theory the four lifecycle patterns sit on top of
- [Remote Agent Host Sessions over SSH and Dev Tunnels](remote-agent-host-sessions.md) — the transport layer beneath this one: where the container runs and how the client reaches it
- [Cloud-Agent Session Bootstrap](cloud-agent-session-bootstrap.md) — the install/start lifecycle for the machine-state layer that all four patterns provision
- [Managed vs Self-Hosted Agent Harness](managed-vs-self-hosted-harness.md) — the decision frame for whether to apply these four patterns at all or pick the managed alternative
