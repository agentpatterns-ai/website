---
title: "Production Hosting Topology for Self-Hosted Agent SDK Runtimes"
description: "Four decisions — container-lifecycle pattern, autoscale signal, credential plane, per-tenant isolation — that turn a self-hosted Agent SDK into a production runtime."
tags:
  - agent-design
  - claude
  - long-form
aliases:
  - agent SDK hosting topology
  - self-hosted agent SDK deployment
  - claude agent SDK production hosting
last_reviewed: 2026-06-01
---

# Production Hosting Topology for Self-Hosted Agent SDK Runtimes

> Pod boundary, autoscale signal, credential plane, and tenant isolation — the four decisions that turn a self-hosted Agent SDK demo into a production runtime.

A self-hosted Agent SDK runtime is not a stateless API wrapper. Every running agent is a long-lived `claude` CLI subprocess that "owns the shell, the working directory, and the JSONL session transcripts on local disk" ([Anthropic: Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)). That fact forces four orthogonal topology decisions — container-lifecycle pattern, sizing and autoscale signal, credential mediation, and per-tenant isolation — that compound rather than cleanly stack. This is the deployment-shape sibling to [Cloud-Agent Three-Layer State Decoupling](cloud-agent-state-layer-decoupling.md) (state) and [Remote Agent Host Sessions](remote-agent-host-sessions.md) (transport).

## When to Defer

The pattern applies once at least one holds: real multi-tenancy, regulated egress (SOC2, FedRAMP, data residency) that rules out fully-managed cloud sandboxes, session lengths exceeding function-tier ceilings, or measured concurrency hitting rate limits. Without any, start on [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) or a single long-running container. "Anthropic token cost typically dominates container infrastructure cost by an order of magnitude or more" ([Anthropic: Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)) — pre-PMF teams gain more from cost caps than from topology.

Regulated egress no longer forces full self-hosting on its own. Anthropic's [self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes) (public beta, May 2026) keep orchestration — session, harness, and the agent loop — on Anthropic's side while moving tool execution onto your infrastructure, so "the filesystem the agent reads and writes, the processes it spawns, and the network it can reach are all under your control" and your existing network policy, audit logging, and DLP apply unchanged. That collapses the old binary: a team needing data residency or non-routable internal services can keep execution and egress inside its perimeter without owning the subprocess, session, and sandbox layers this page describes. Reach for the full self-hosted topology below only when you also need to control the orchestration layer itself — full on-premise operation of the agent loop is still not offered — or when multi-tenancy, function-tier overflow, or rate-limit pressure forces it.

## The Four Session-Lifecycle Patterns

Anthropic documents four patterns that map directly to container lifecycle ([Anthropic: Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)):

| Pattern | Container lifetime | Session storage | Best for |
|---------|-------------------|-----------------|----------|
| **Ephemeral** | One container per task | None | Bug-fix runs, document extraction, CI one-shots |
| **Long-running** | Persistent containers, many SDK subprocesses each | Local disk plus optional `SessionStore` mirror | Autonomous agents, Slack-bot-style continuous traffic |
| **Hybrid** | Ephemeral containers that hydrate from `SessionStore` on start | Mandatory — "Shutting a container down without a `SessionStore` configured loses the transcript" | Sessions with long gaps, pause-resume research, support agents |
| **Multi-agent container** | One container, multiple SDK subprocesses | Per-agent working directory and settings isolation | Multi-agent simulations sharing an environment |

The choice is reversible only at high cost — match the pattern to observed session-length and concurrency before locking in.

## Size on Measured RAM, Autoscale on Tokens

Anthropic's sizing formula is `agents per host = (host RAM − overhead) / (per-session RAM ceiling)`. The 1 GiB / 5 GiB disk / 1 CPU starting point is "a floor, not the ceiling" — measure peak RSS at target length under expected tool load ([Anthropic: Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)).

Requests-per-minute is the wrong autoscale signal. A single agent loop runs for minutes on one inbound request, and a stuck loop burns budget while staying under any RPM cap: "one autonomous agent stuck in a retry loop sent 50,000 requests over six hours because no individual rate limit was ever breached. The per-user limit was 60 requests per minute. The agent never exceeded it" ([Zuplo: Token-Based Rate Limiting for AI Agents](https://zuplo.com/learning-center/token-based-rate-limiting-ai-agents)).

- **Interactive long-running**: tokens-per-minute via the SDK's OpenTelemetry hooks (`CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_METRICS_EXPORTER=otlp`) ([Anthropic: Hosting §Observability](https://code.claude.com/docs/en/agent-sdk/hosting)).
- **Background worker pools**: queue depth — "autoscaling on queue depth rather than CPU, since the agent workload is API-bound" ([Digital Applied: Claude Agent SDK Production Patterns Guide](https://www.digitalapplied.com/blog/claude-agent-sdk-production-patterns-guide)).
- **Pooled long-running containers**: route by "consistent hashing on `sessionId`" so a session keeps hitting the same subprocess until eviction ([Anthropic: Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)).

## Credentials Through a Sidecar Proxy

Agents process untrusted content. Anthropic's threat model: "if an agent processes a malicious file that instructs it to send customer data to an external server, network controls can block that request entirely" ([Anthropic: Secure Deployment](https://code.claude.com/docs/en/agent-sdk/secure-deployment)). Credentials live outside the agent's security boundary and are injected on egress:

- For the Claude API, set `ANTHROPIC_BASE_URL` to your proxy; the proxy injects the key on egress.
- For other services, route via a TLS-terminating proxy with `HTTP_PROXY` / `HTTPS_PROXY`, or expose them as MCP tools that authenticate outside the agent's reach.
- The hardened container shape uses `--network none` plus a Unix-socket-mounted proxy, `--cap-drop ALL`, `--read-only`, `--security-opt no-new-privileges`, a seccomp profile, tmpfs writable paths, and a non-root user ([Anthropic: Secure Deployment §Containers](https://code.claude.com/docs/en/agent-sdk/secure-deployment)).

A successful prompt injection cannot read what the agent never sees.

## Multi-Tenant Isolation Needs Four Switches At Once

Default SDK behaviour reads `CLAUDE.md` memory and settings from the filesystem, leaking across tenants in a shared container. The isolation contract requires all four simultaneously ([Anthropic: Hosting §Multi-tenant isolation](https://code.claude.com/docs/en/agent-sdk/hosting)):

| Lever | What it blocks |
|-------|----------------|
| `settingSources: []` (TS) / `setting_sources=[]` (Python) | Filesystem-loaded settings |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` in `env` | Auto-memory that loads "into the system prompt regardless of `settingSources`" |
| Per-tenant `CLAUDE_CONFIG_DIR` | Sharing of the global `~/.claude.json` |
| Per-tenant `cwd` on every `query()` call | Filesystem cross-contamination |

Any missing switch leaks the corresponding input. Per-tenant egress rules at the proxy close the network leg.

## Why It Works

The four decisions compound because three failure modes have orthogonal mitigations. **Cold start trades off against blast radius**: pod-per-session minimises blast radius but pays a per-session cold start; pooled workers reuse warm subprocesses but accumulate tenant context that must be scrubbed. Practitioners report "starting a new pod adds about a second of overhead… when an agent is invoked after being idle, a one-second cold start breaks the continuity of the interaction" — the Kubernetes Sandbox CRD answers with a `SandboxWarmPool` that maintains pre-provisioned pods, "effectively eliminating cold starts" while preserving pod-per-session boundaries ([Kubernetes blog: Running Agents on Kubernetes with Agent Sandbox](https://kubernetes.io/blog/2026/03/20/running-agents-on-kubernetes-with-agent-sandbox/)). The other two failure modes mitigate independently — a token-bound autoscale signal sees the stuck loop that RPM cannot, and a sidecar-injected credential is one a successful injection cannot exfiltrate. Each lever is independently load-bearing.

Anthropic's Managed Agents architecture decomposes the runtime into Session, Harness, and Sandbox and reports the decoupling cut p50 time-to-first-token by roughly 60% and p95 by more than 90% ([Anthropic: Managed Agents](https://www.anthropic.com/engineering/managed-agents)) — evidence the "stateless harness, durable session" pattern composes downward to any pod shape.

## When This Backfires

- **Pre-PMF teams** building deep topology before learning the agent's actual session-length and concurrency waste platform engineering; a coupled prototype ships in weeks ([Cursor: Cloud-Agent Lessons](https://cursor.com/blog/cloud-agent-lessons)).
- **Single-tenant internal tools** never need per-tenant isolation, consistent-hash routing, or `SessionStore` durability. The four-switch isolation pattern is dead code.
- **Workloads that fit a function-duration tier** (Vercel, Lambda 15-min ceiling) are better served by a stateless function with checkpoint-and-resume between tool calls than by a pooled worker ([Digital Applied](https://www.digitalapplied.com/blog/claude-agent-sdk-production-patterns-guide)).
- **Managed Agents deployments** — the topology decisions do not apply; Anthropic operates the subprocess, sandbox, and session layer ([Anthropic: Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting) opens with this fork).
- **`SessionStore` as durability source-of-truth** — it is a best-effort mirror. On store outage "the SDK emits a `{ type: "system", subtype: "mirror_error" }` message and continues the query without retry" ([Anthropic: Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)). Local disk is authoritative.
- **Single-shot ephemeral agents** — pooled-worker and warm-pool patterns add only cost; a one-shot entrypoint exiting on completion is correct.

## Example

A team self-hosting a long-running multi-tenant agent on Kubernetes wants per-tenant isolation, warm starts, and an autoscale signal that catches stuck loops.

**Before** — pod-per-tenant with naive HPA:

```yaml
# HPA scales on request rate; one tenant's stuck loop never trips it.
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  metrics:
    - type: Pods
      pods:
        metric:
          name: http_requests_per_minute
        target:
          type: AverageValue
          averageValue: "60"
# Credentials in pod env — readable by any injected tool call.
env:
  - name: ANTHROPIC_API_KEY
    valueFrom: { secretKeyRef: { name: anthropic, key: api-key } }
```

**After** — pooled long-running containers, consistent-hash session routing, sidecar credential proxy, token-rate autoscale:

```yaml
# Front the pool with a consistent-hash router keyed on sessionId.
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  metrics:
    - type: Pods
      pods:
        metric:
          name: claude_tokens_per_minute  # exported via OTEL
        target:
          type: AverageValue
          averageValue: "200000"
# Credentials never enter the agent pod.
env:
  - name: ANTHROPIC_BASE_URL
    value: "http://credential-proxy.svc.cluster.local:8080"
  - name: CLAUDE_CODE_DISABLE_AUTO_MEMORY
    value: "1"
  - name: CLAUDE_CONFIG_DIR
    value: "/var/run/tenant-config"  # per-tenant volume mount
```

In TypeScript, each `query()` call still carries `cwd: tenantDir` and `settingSources: []` so the multi-tenant isolation contract holds inside the shared container ([Anthropic: Hosting the Agent SDK §Multi-tenant isolation](https://code.claude.com/docs/en/agent-sdk/hosting)).

## Key Takeaways

- The Agent SDK's subprocess model — one `claude` CLI process per session, owning shell, working directory, and on-disk transcripts — is what makes hosting topology a real design problem, not a stateless-API decision
- Four session-lifecycle patterns map to container lifetime: ephemeral, long-running, hybrid, multi-agent container; pick by observed session-length and concurrency, not by aspiration
- Size on measured peak RSS per session, not idle baseline; the 1 GiB / 5 GiB / 1 CPU starting point is a floor
- Autoscale on token rate (interactive) or queue depth (workers), never request rate — agent loops are long-tailed and a stuck loop stays under RPM caps
- For pooled long-running containers, consistent-hash routing on `sessionId` is mandatory so a session keeps hitting the warm subprocess that holds its state
- Credentials belong outside the agent's security boundary, injected by a sidecar proxy on egress; an injection cannot exfiltrate what the agent never sees
- Multi-tenant isolation requires four SDK switches at once — `settingSources: []`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, per-tenant `CLAUDE_CONFIG_DIR`, per-tenant `cwd` — any missing one leaks the corresponding input
- `SessionStore` (S3, Redis, Postgres) is a best-effort mirror, not a replacement for local-disk durability; alert on `mirror_error`
- The pattern is Qualified: defer the whole topology design until multi-tenancy, regulated egress, function-tier overflow, or measured rate-limit pressure forces it — token cost dominates infra cost by an order of magnitude or more

## Related

- [Cloud-Agent Three-Layer State Decoupling](cloud-agent-state-layer-decoupling.md) — the state-shape sibling: what is persistent vs ephemeral across loop, machine, and conversation layers
- [Remote Agent Host Sessions over SSH and Dev Tunnels](remote-agent-host-sessions.md) — the transport-shape sibling: how the client reaches a lifecycle-decoupled agent host
- [Subprocess-per-Session Hosting Model](subprocess-per-session-hosting-model.md) — the foundational frame: why one `claude` CLI process per session is what makes the four lifecycle patterns a real choice
- [Session Harness Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — the three-primitive theory that this deployment topology projects onto pod boundaries
- [Managed vs Self-Hosted Agent Harness](managed-vs-self-hosted-harness.md) — the decision frame for whether to self-host at all
- [Prebuilt Agent Environments](prebuilt-agent-environments.md) — bakes machine-state initial conditions into a container image, reducing per-session start cost
