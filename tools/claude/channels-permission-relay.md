---
title: "Channels Permission Relay"
description: "Use Claude Code's --channels flag to forward tool-use approval prompts to your phone via Telegram, Discord, or iMessage — so long-running agents can pause on ambiguous actions and wait for remote approval instead of blocking at the terminal."
tags:
  - claude
  - agent-design
  - workflows
applies_to: "claude-code@2.x"
last_reviewed: 2026-05-27
status: current
---
# Channels Permission Relay

> Forward tool-use approval prompts from a running Claude Code session to your phone via Telegram, Discord, or iMessage — so agents can run overnight without requiring you at the terminal for every permission decision.

Unattended agent runs face a binary choice: `--dangerously-skip-permissions` removes safety checks, or the agent blocks waiting for terminal input. The channels permission relay sits between those extremes — routine tool use proceeds automatically while ambiguous or high-stakes actions pause, forward a prompt to your phone, and resume the moment you reply.

## How it works

A [channel](https://code.claude.com/docs/en/channels) is a local MCP server, spawned over stdio, that bridges your Claude Code session to an external platform. Enable one per session with `--channels`:

```bash
claude --channels plugin:telegram@claude-plugins-official
```

When Claude requests a tool-use approval and the channel has declared the [`claude/channel/permission` capability](https://code.claude.com/docs/en/channels-reference#relay-permission-prompts), Claude Code fires a `notifications/claude/channel/permission_request` notification carrying four fields:

| Field | Content |
|---|---|
| `request_id` | Five lowercase letters from `a`–`z` excluding `l`, unique to this prompt |
| `tool_name` | Tool Claude wants to use, such as `Bash` or `Write` |
| `description` | Human-readable summary of the specific call |
| `input_preview` | Tool arguments as JSON, truncated to 200 characters |

The channel formats those fields into a message and sends it to your phone. You reply `yes <id>` or `no <id>`; the channel parses that into a `notifications/claude/channel/permission` verdict, which Claude Code applies to unblock the tool call.

The local terminal dialog stays open throughout. Whichever answer arrives first — remote or local — applies; the other is dropped.

## Supported channels

Three channel plugins ship in the [claude-plugins-official research preview](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins):

| Channel | Setup requirement |
|---|---|
| [Telegram](https://code.claude.com/docs/en/channels#supported-channels) | BotFather token; sender pairing |
| [Discord](https://code.claude.com/docs/en/channels#supported-channels) | Bot token; Message Content Intent; sender pairing |
| [iMessage](https://code.claude.com/docs/en/channels#supported-channels) | macOS; Full Disk Access grant for your terminal |

Each plugin maintains a sender allowlist. Telegram and Discord bootstrap it via pairing: DM the bot, receive a pairing code, confirm it in Claude Code. iMessage auto-trusts messages from your own Apple ID; other contacts are added by handle with `/imessage:access allow`.

Channels require [Claude Code v2.1.80 or later](https://code.claude.com/docs/en/channels) and Anthropic authentication via claude.ai or a Console API key; Amazon Bedrock, Google Vertex AI, and Microsoft Foundry are not supported. Permission relay specifically [requires v2.1.81 or later](https://code.claude.com/docs/en/channels-reference#relay-permission-prompts) — earlier versions ignore the `claude/channel/permission` capability.

## Security gating

The sender allowlist that controls inbound chat also gates permission relay. Anyone who can reply through the channel can approve or deny tool use in your session — only allowlist senders you trust with that authority.

Being in `.mcp.json` is not enough to push messages or relay permissions: a server must also be named in `--channels`.

Project trust and MCP server consent dialogs do not relay; those only appear in the local terminal.

## Enterprise controls

On Team and Enterprise plans, channels are off by default. Two [managed settings](https://code.claude.com/docs/en/channels#enterprise-controls) control availability:

| Setting | Effect |
|---|---|
| `channelsEnabled` | Master switch. Must be `true` for any channel to deliver messages or relay permissions. |
| `allowedChannelPlugins` | Replaces the Anthropic-curated plugin allowlist. When set, only listed plugins can register. |

Pro and Max users without an org skip these checks.

## Relation to auto-mode

[Auto-mode](auto-mode.md) approves routine tool use without prompting; relay handles what auto-mode cannot classify or intentionally escalates. Together they cut prompt volume and ensure escalations still find you.

## When this backfires

Relay widens the approval surface and narrows the information the approver sees:

- Weaker credential than the terminal. A stolen phone, SIM-swap, or shared iMessage device becomes a tool-approval path — defeating a locked workstation takes more effort.
- Narrow remote view. The relay forwards only `tool_name`, a short `description`, and the first 200 characters of arguments. You cannot judge a blast radius that depends on working directory or session state from a phone.
- Approval fatigue. Prompts glanced at on a phone get approved by reflex — the failure mode that [safe command allowlisting](../../security/safe-command-allowlisting.md) and [auto-mode](auto-mode.md) exist to avoid.
- Sandboxable risk. For throwaway worktrees or ephemeral containers with no credentials in scope, `--dangerously-skip-permissions` inside a sandbox removes prompts entirely. Relay adds latency without adding safety.

## Example

A session running an overnight refactor on a large codebase:

```bash
claude --channels plugin:telegram@claude-plugins-official \
  "Refactor all API clients in src/ to use the new retry library. Run tests after each file."
```

File reads, edits within the project, and test runs proceed without interruption. When Claude prepares to run a destructive shell command outside the stated scope, the `Bash` prompt triggers the relay. Your Telegram bot sends:

```
Claude wants to run Bash: rm -rf src/legacy/api-helpers/
Reply "yes abcde" or "no abcde"
```

You reply `no abcde`. Claude Code receives the denial, the tool call is rejected, and Claude continues without the deletion. You check the session in the morning with a complete transcript.

## Key Takeaways

- `--channels` enables MCP servers to push events into a running session and relay permission prompts remotely
- The `claude/channel/permission` capability on the channel server is the opt-in for permission relay; without it, channels are one-way or chat-only
- Local terminal dialog and remote relay run in parallel — first answer wins
- Sender allowlist controls both inbound chat and permission verdicts; treat allowlist membership as equivalent to terminal access
- `channelsEnabled` must be set by an admin on Team/Enterprise plans before channels work at all

## Related

- [Auto Mode](auto-mode.md) — Classifier-based permission gating; pairs with channels relay for low-noise unattended runs
- [Session Scheduling](session-scheduling.md) — Schedule recurring sessions; combine with channels for overnight autonomous workflows
- [Hooks & Lifecycle](hooks-lifecycle.md) — Deterministic automation at lifecycle events; complementary to permission relay for pre-approved actions
- [Deferred Permission Pattern](../../agent-design/deferred-permission-pattern.md) — Alternative approach: pause headless sessions via `PreToolUse` hook `defer` verdict and resume after out-of-band approval
- [Feature Flags & Environment Variables](feature-flags.md) — Configuration knobs including permission-related flags
