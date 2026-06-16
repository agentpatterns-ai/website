---
title: "Push-Event MCP Channels: Inverting the Pull-Tool Polarity"
term: "Push-Event MCP Channels"
description: "MCP channels invert the standard pull-tool polarity by pushing events into a running agent session — useful for warm-context reactions, gated by sender allowlist, capability declaration, and an always-open session."
tags:
  - tool-engineering
  - tool-agnostic
aliases:
  - push-event MCP server
  - MCP channel server
  - MCP server push notifications
last_reviewed: 2026-06-03
maturity: adopted
---

# Push-Event MCP Channels: Inverting the Pull-Tool Polarity

> MCP channels invert pull-tool polarity — the server pushes events into a running session through one capability declaration, gated by a sender allowlist.

A push-event MCP channel is an MCP server that declares `claude/channel` under `capabilities.experimental`, so the host registers a notification listener; the server then emits `notifications/claude/channel` events that arrive in context as `<channel source="...">` tags between turns ([Channels reference](https://code.claude.com/docs/en/channels-reference)). Standard MCP servers are pull-only — Claude queries them during a task ([Channels overview, How channels compare](https://code.claude.com/docs/en/channels#how-channels-compare)). Channels flip that polarity so the agent reacts to webhooks, chat messages, and monitoring alerts in the session it already has open, files still in context.

## The Polarity Flip

The host primitive is the capability declaration. Without it the server is a pull-only tool surface; with it the host wires a side-band notification stream multiplexed over the same stdio transport ([Channels reference §Server options](https://code.claude.com/docs/en/channels-reference#server-options)).

| Dimension | Standard MCP tool | Push-event channel |
|-----------|-------------------|--------------------|
| Direction | Agent pulls — `tools/call` request | Server pushes — `notifications/claude/channel` |
| Capability declaration | `capabilities.tools` | `capabilities.experimental['claude/channel']: {}` |
| Trigger | Agent reasoning loop decides | External event (HTTP POST, chat message, webhook) |
| Delivery surface | Tool result in the turn that called it | `<channel source="..." attr="...">body</channel>` injected before the next turn |
| Session requirement | Spawned on demand | Session must be open when the event fires |
| Acknowledgement | Request/response — agent sees errors | Fire-and-forget — `await mcp.notification()` resolves on transport write, not on Claude processing ([reference §Notification format](https://code.claude.com/docs/en/channels-reference#notification-format)) |

The same server can do both — declare `tools` for the agent to call (reply tool, status query) *and* `claude/channel` for inbound pushes — which is how two-way chat bridges work ([reference §Expose a reply tool](https://code.claude.com/docs/en/channels-reference#expose-a-reply-tool)).

## What This Solves

The proposal for generic MCP server push was filed against Claude Code as [#36665](https://github.com/anthropics/claude-code/issues/36665) and closed as not planned; channels are Anthropic's productised alternative for three failure modes:

- **Idle session blindness** — without push, an agent only learns about external state changes on its next tool call
- **Polling token tax** — workarounds that append a "check channel" call to every tool response waste context-window tokens on empty polls
- **Warm-context loss** — a fresh session per event ([Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web), [Claude in Slack](https://code.claude.com/docs/en/slack)) loses the in-progress file state the agent built

Channels move the event source-of-truth out of the tool-call loop into a side-band stream surfaced between turns.

## Why It Works

The mechanism is the capability gate plus stdio multiplexing. The MCP spec already defines server-to-client notifications as a transport primitive; the `claude/channel` capability tells Claude Code to register a listener for `notifications/claude/channel` and surface arriving events in context instead of dropping them ([reference §Overview](https://code.claude.com/docs/en/channels-reference#overview)). The same stdio pipe that carries tool requests carries the notifications — no second transport, no public webhook endpoint, no session-resume problem. That one-line opt-in makes the polarity inversion composable with existing MCP server code.

## The Security Model

Push polarity widens the inbound surface to anyone the channel accepts from. The docs prescribe three non-optional controls:

- **Sender allowlist inside the server** — gate on `message.from.id`, not the chat or room ID, before calling `mcp.notification()`. A group chat ID lets any member inject into the session ([reference §Gate inbound messages](https://code.claude.com/docs/en/channels-reference#gate-inbound-messages)).
- **Session opt-in via `--channels`** — declaration in `.mcp.json` is not enough; the server must also be named in `--channels` to register the listener ([Channels §Security](https://code.claude.com/docs/en/channels#security)).
- **Organizational policy** — on Team and Enterprise plans the `channelsEnabled` switch is off by default; `allowedChannelPlugins` replaces the Anthropic-curated allowlist when set ([Channels §Enterprise controls](https://code.claude.com/docs/en/channels#enterprise-controls)).

The opt-in [permission relay capability](https://code.claude.com/docs/en/channels-reference#relay-permission-prompts) sits on the same allowlist — anyone who can push messages can also approve or deny tool use. See [channels permission relay](../tools/claude/channels-permission-relay.md) for the relay UX.

## When This Backfires

The failure modes follow from "the session has to be open" and "the inbound surface is wider":

- **Sessions that aren't open 24/7** — events are dropped with "no error returned to your server" if the session is closed or org policy blocks ([reference §Notification format](https://code.claude.com/docs/en/channels-reference#notification-format)). Operators believing undelivered CI alerts arrived is the silent-stall failure mode.
- **Bedrock, Vertex AI, and Foundry deployments** — channels require Anthropic authentication (claude.ai account or Console API key); these backends silently lose the capability ([Channels overview](https://code.claude.com/docs/en/channels)).
- **High-frequency event bursts** — "if several notifications arrive while Claude is busy, they're delivered together on the next turn and Claude handles them as a group" ([reference §Notification format](https://code.claude.com/docs/en/channels-reference#notification-format)). Monitoring fan-in collapses to coarse batches; per-event fidelity is lost.
- **Loose sender allowlists** — the lethal-trifecta failure mode applies directly: a channel mixing untrusted inbound with private-data repo access and any egress tool is a one-step exfiltration path ([lethal trifecta](../security/lethal-trifecta-threat-model.md)). Gating on `chat.id` instead of `from.id` is the most common mistake ([reference §Gate inbound messages](https://code.claude.com/docs/en/channels-reference#gate-inbound-messages)).
- **Tasks that don't need warm context** — a fresh cloud session per event ([event-driven agent routing](../agent-design/event-driven-agent-routing.md) on GitHub Actions, the web, Slack mentions) is cheaper and more resilient with no in-progress state to preserve. The MCP "Tasks" primitive in the 2025-11-25 spec targets this case — `taskId` plus client-driven fetch, no pinned session ([Triggers and Events charter](https://modelcontextprotocol.io/community/triggers-events/charter)).
- **Multi-day operations** — MCP maintainers argue session-based push is the wrong shape past a few hours: "When a task spans several hours or even days, it's no longer just a 'task' — it's effectively a long-running job" ([MCP discussions #523](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/523)). Channels are a session-lifetime primitive, not a job-orchestration one.

## Example

A minimal one-way webhook channel ([adapted from the channels reference walkthrough](https://code.claude.com/docs/en/channels-reference#example-build-a-webhook-receiver)) — the `claude/channel` capability is the one line that distinguishes this from a standard MCP server:

```ts title="webhook.ts"
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'

const mcp = new Server(
  { name: 'webhook', version: '0.0.1' },
  {
    // presence of this key flips the polarity from pull to push
    capabilities: { experimental: { 'claude/channel': {} } },
    instructions: 'Events arrive as <channel source="webhook" ...>. Read and act, no reply.',
  },
)
await mcp.connect(new StdioServerTransport())

Bun.serve({
  port: 8788,
  hostname: '127.0.0.1',  // localhost-only — no public endpoint
  async fetch(req) {
    const body = await req.text()
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: {
        content: body,
        meta: { path: new URL(req.url).pathname, method: req.method },
      },
    })
    return new Response('ok')
  },
})
```

A CI failure POSTed to `localhost:8788` arrives in context as:

```text
<channel source="webhook" path="/" method="POST">build failed on main: https://ci.example.com/run/1234</channel>
```

The agent reads it in the next turn with the same files open it was using when the build started. To accept inbound from a public chat platform instead of localhost, add an allowlist check on `message.from.id` before the `mcp.notification()` call — the [gate inbound messages](https://code.claude.com/docs/en/channels-reference#gate-inbound-messages) section shows the canonical shape.

## Key Takeaways

- The polarity flip is a one-line capability declaration: `capabilities.experimental['claude/channel']: {}` registers the listener; absent it, the same server stays pull-only
- Notifications are fire-and-forget — `await mcp.notification()` resolves on transport write, not on Claude processing; sessions that aren't open silently drop events
- The session-must-be-open prerequisite bounds the pattern to "warm-context worth keeping" cases — fresh-session-per-event (Claude Code on the web, Slack, GitHub Actions routing) is cheaper for stateless reactions
- Sender allowlists are mandatory and gate on `from.id` (not chat or room ID); the lethal-trifecta failure mode is loose gating combined with repo access and egress
- Channels are a session-lifetime primitive, not a job-orchestration primitive — multi-day or always-online workloads belong on the MCP Tasks primitive or fresh-session routing instead

## Related

- [MCP Server Design](mcp-server-design.md) — server-author checklist; the pull-tool baseline this pattern inverts
- [MCP Client/Server Architecture](mcp-client-server-architecture.md) — transport selection and capability negotiation, the substrate the `claude/channel` capability rides on
- [MCP Elicitation](mcp-elicitation.md) — the inverse direction: server requests structured input from the user mid-task, still initiated by the agent's tool call
- [Channels Permission Relay](../tools/claude/channels-permission-relay.md) — the opt-in `claude/channel/permission` capability that uses the same allowlist to relay tool-use approvals
- [Event-Driven Agent Routing](../agent-design/event-driven-agent-routing.md) — the fresh-session-per-event alternative when warm context is not worth keeping
- [Agent Event Streaming](../agent-design/agent-event-streaming-model.md) — runtime-side typed event vocabulary; channels are an inbound source that feeds it
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md) — the security framing for any inbound channel that mixes untrusted senders with private data and egress
