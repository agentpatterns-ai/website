---
title: "Cursor SDK: Programmable TypeScript Agent Runtime"
description: "Embed Cursor's agent harness in your own TypeScript applications — local, Cursor-hosted, or self-hosted runtime behind one interface."
tags:
  - agent-design
  - cursor
aliases:
  - cursor typescript sdk
  - "@cursor/sdk"
---

# Cursor SDK

> Embed Cursor's agent harness in TypeScript applications, with local, Cursor-hosted, or self-hosted runtimes behind one interface.

The [Cursor SDK](https://cursor.com/blog/typescript-sdk) entered public beta on April 29, 2026 as `@cursor/sdk`, exposing the agent runtime that powers Cursor's desktop, CLI, and web apps as a programmable TypeScript library ([Cursor changelog](https://cursor.com/changelog)). It joins the [GitHub Copilot SDK](../copilot/copilot-sdk.md) and [Claude Agent SDK](../claude/agent-sdk.md) as a vendor-runtime SDK: applications inherit a production-tested harness — context indexing, planner, tool orchestration, MCP routing — without reimplementing agent infrastructure.

## What the SDK Exposes

The full Cursor harness is available through the SDK ([Cursor docs](https://cursor.com/docs/sdk/typescript)):

- **Codebase indexing and semantic search** — the same context system the IDE uses.
- **MCP servers** — stdio and HTTP, defined inline or loaded from `.cursor/mcp.json`.
- **Skills** — auto-loaded from `.cursor/skills/`.
- **Hooks** — file-based observers loaded from `.cursor/hooks.json` (no programmatic callbacks).
- **Subagents** — named delegates with independent prompts and models.
- **Multi-model selection** — every model in Cursor, including Composer 2 (coding-specialised, frontier-level performance at lower cost).

`Agent.create()` returns a long-lived agent; `agent.send(prompt)` returns a `Run` whose events stream via async iteration or callbacks:

```typescript
import { Agent } from "@cursor/sdk";

const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2" },
  local: { cwd: process.cwd() },
});

const run = await agent.send("Summarize what this repository does");
for await (const event of run.stream()) {
  console.log(event);
}
```

`Agent.prompt()` is a one-shot convenience that creates, runs, and disposes in one call.

## Three Runtimes, One Interface

The same SDK shape targets three execution modes ([Cursor blog](https://cursor.com/blog/typescript-sdk); [Cursor docs](https://cursor.com/docs/sdk/typescript)):

| Runtime | Where the agent runs | Use case |
|---------|----------------------|----------|
| **Local** | In your Node process; files come from disk | Dev scripts, CI checks, fast iteration |
| **Cloud (Cursor-hosted)** | Dedicated VM with cloned repo, sandboxing, persistent sessions | Parallel runs, disconnection-resilient long jobs, auto PR creation |
| **Cloud (self-hosted)** | Cursor cloud handles inference; your worker handles tool execution | Data residency, internal resource access — see [Self-Hosted Cloud Agents](self-hosted-cloud-agents.md) |

Cloud agents accept a `repos` list and `autoCreatePR` flag, so the agent clones a repo, works on a branch, and opens a PR on finish:

```typescript
const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "gpt-5.5" },
  cloud: {
    repos: [{ url: "https://github.com/cursor/cookbook", startingRef: "main" }],
    autoCreatePR: true,
  },
});

const run = await agent.send("Fix the auth token expiry bug");
```

## Streaming Model

Two consumption patterns ([Cursor docs](https://cursor.com/docs/sdk/typescript)):

- **Async iteration** — `for await (const event of run.stream())` yields `system`, `user`, `assistant`, `thinking`, `tool_call`, `status`, `task`, `request` events.
- **Delta callbacks** — `onDelta` and `onStep` deliver token-level text deltas, thinking streams, and step boundaries.

`run.wait()` blocks for terminal status (`finished` | `error` | `cancelled`) and exposes `durationMs` and, on cloud, the `git` branches the run produced.

## Pricing and Auth

SDK runs follow [standard token-based consumption pricing](https://cursor.com/blog/typescript-sdk), share request pools and Privacy Mode rules with IDE and Cloud Agent runs, and appear in usage dashboards under an SDK tag ([Cursor docs](https://cursor.com/docs/sdk/typescript)). Auth is via `CURSOR_API_KEY` (user or service-account keys); Team Admin keys are not yet supported.

## Comparison with Other Vendor SDKs

The three programmable agent SDKs share the same primitive — embed the vendor's harness in your application — but trade off differently:

| | Cursor SDK | [Copilot SDK](../copilot/copilot-sdk.md) | [Claude Agent SDK](../claude/agent-sdk.md) |
|---|---|---|---|
| Languages | TypeScript (beta) | Node.js, Python, Go, .NET, Java | Python, TypeScript |
| Local runtime | Yes — in-process Node | Yes — CLI-backed | Yes |
| Hosted runtime | Cursor-hosted VMs + self-hosted workers | None — local execution only | None — local execution only |
| Auto PR creation | Yes (cloud) | No (manual) | No (manual) |
| MCP support | Yes | Yes | Yes |
| Pricing | Token consumption (Cursor pool) | Counts against Copilot premium request quotas | Anthropic API tokens |

Cursor is the only one of the three that ships a vendor-managed cloud runtime as part of the SDK, with explicit support for long-running, disconnection-resilient jobs that produce PRs.

## When This Backfires

Vendor-runtime SDKs concentrate operational risk in the vendor's roadmap:

- **Users without Cursor billing.** All SDK runs count against Cursor consumption pricing ([Cursor blog](https://cursor.com/blog/typescript-sdk)); applications serving end users without a Cursor relationship cannot use the SDK as the runtime.
- **Strict data residency.** Cursor-hosted cloud agents clone repos into Cursor's VMs. Teams banning vendor-hosted execution need the [self-hosted worker mode](self-hosted-cloud-agents.md).
- **Stable long-horizon contract.** The SDK docs note the tool-call schema is unstable and inline `mcpServers` don't survive `Agent.resume()` ([Cursor docs](https://cursor.com/docs/sdk/typescript)); applications needing deterministic harness contracts absorb upstream churn or pin a vendored copy.
- **Multi-vendor orchestration.** Spanning Cursor, Copilot, and Claude harnesses simultaneously is easier on a thinner foundation (direct LLM API + custom orchestration).

## Example

The Quickstart in [cursor/cookbook](https://github.com/cursor/cookbook) shows the minimal local-agent pattern. The Kanban Board example uses the cloud runtime to spawn agents from a project board, link runs to PRs, and preview artifacts. Both starters fork without modification once `CURSOR_API_KEY` is set.

```typescript
// One-shot pattern from the cookbook
const result = await Agent.prompt("What does this code do?", {
  apiKey: process.env.CURSOR_API_KEY!,
  model: { id: "composer-2" },
  local: { cwd: process.cwd() },
});
```

## Key Takeaways

- The Cursor SDK exposes Cursor's production agent harness as a TypeScript library, in public beta from April 29, 2026.
- Three runtimes share one interface: in-process local, Cursor-hosted cloud VMs, and self-hosted workers — switch by changing the `local`/`cloud` field on `Agent.create()`.
- Cloud agents support auto-PR creation, persistent sessions across disconnections, and long-running jobs — the differentiator versus the Copilot and Claude Agent SDKs.
- Pricing is token-based consumption pooled with IDE and Cloud Agent usage; auth is `CURSOR_API_KEY`.
- The SDK couples your application to Cursor's harness roadmap, pricing, and rate limits — known limitations include unstable tool-call schemas and inline-MCP not surviving resume.

## Related

- [Cursor 3 Agents Window](agents-window.md)
- [Cursor Self-Hosted Cloud Agents](self-hosted-cloud-agents.md)
- [Claude Agent SDK](../claude/agent-sdk.md)
- [GitHub Copilot SDK](../copilot/copilot-sdk.md)
- [Cost-Aware Agent Design](../../agent-design/cost-aware-agent-design.md)
