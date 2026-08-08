---
title: "Cross-Session Peer Messaging with a Posture-Keyed Inbox Gate"
term: "Peer Session Messaging"
description: "Two independently steered agent sessions exchange plain-text messages through per-session inboxes, with the receiving side gating delivery on permission posture rather than sender identity."
tags:
  - agent-design
  - claude
aliases:
  - cross-session messaging
  - peer session inbox
  - agent-to-agent session messaging
applies_to: "claude-code@2.x"
last_reviewed: 2026-08-08
maturity: emerging
status: current
---

# Cross-Session Peer Messaging with a Posture-Keyed Inbox Gate

> Two independently steered agent sessions exchange plain-text messages through per-session inboxes, and the receiving inbox gates delivery on permission posture rather than peer identity.

Reach for a peer inbox when two sessions you steer yourself need a fact mid-run and no shared file, queue, or sub-agent gets it there in time. Claude Code v2.1.224 ships the channel: `SendMessage` writes plain text into another session's inbox, and `ListAgents` discovers which sessions are reachable ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). The receiver decides what happens next, not the sender.

## What has to be true first

Each limit below rules out a plausible use.

- Claude Code v2.1.224 or later, on macOS or Linux. Native Windows lacks the feature, as do Amazon Bedrock, Claude Platform on AWS, Google Cloud's Agent Platform, and Microsoft Foundry ([cross-session messaging docs](https://code.claude.com/docs/en/cross-session-messaging#availability)).
- Both sessions read the same registration files on disk, so a session in a container and one on the host never find each other.
- The receiver can answer an approval dialog, or is set never to need one. A `claude -p` worker binds an inbox but cannot render that dialog.
- The fact fits in prose. A message carries text, never conversation history and never files.
- Across machines, v2.1.224 allowed only a reply. Version 2.1.225 added starting a conversation with a Remote Control session by name ([changelog](https://code.claude.com/docs/en/changelog)).

## The inbound gate

An arriving message is delivered, held undelivered, or refused and dropped. The `crossSessionInbound` setting picks which.

| Value | Behavior |
|---|---|
| `accept` | Claude Code delivers each message to Claude |
| `hold` | Claude Code shows a notice and withholds the message until an `accept` later applies |
| `refuse` | Claude Code drops each message without delivering it |

With no value set, the default decides per message from the permission class of both endpoints. Sessions that bypass permission prompts form one class and every other session forms the other, with `auto`, `acceptEdits`, and `dontAsk` counting as prompting ([docs](https://code.claude.com/docs/en/cross-session-messaging#control-inbound-messages)):

| Receiving session | Sender asserts bypassing | Sender does not |
|---|---|---|
| Prompts for permissions | Held for approval | Delivered |
| Bypasses prompts | Delivered | Held for approval |

Sender identity never enters that decision. The sender's permission class does, and it arrives as the sender's own assertion, so a message asserting no class is held rather than delivered in a bypassing receiver. The gate fails closed on the one input it cannot verify.

An unanswered hold dialog closes after `dialogExpiry`, five minutes by default, and the message is dropped. A parked message that never resolves is a stuck sender, so v2.1.225 added the missing notice and expiry for headless sessions and startup ([changelog](https://code.claude.com/docs/en/changelog)).

## Why it works

Permission posture bounds what an injected instruction can reach, and identity does not. Where a session still prompts, an instruction arriving by message meets a permission prompt at the dangerous action, so a check at the channel entrance adds friction without containment. Where permissions are bypassed there is no later gate, so the entrance is the only place left to interpose. Identity fails as a key because a trusted peer that has itself been injected emits the same bytes as a hostile one, and injected prompts self-replicate from agent to agent ([Lee and Tiwari, 2024](https://arxiv.org/abs/2410.07283v1)).

The rest of the receiving-side contract applies the authority-confusion invariant: an untrusted source may inform reasoning but must never authorize a side effect ([Qin et al., 2026](https://arxiv.org/abs/2605.28914v1)). A peer message never counts as your consent, cannot answer a pending permission prompt, and cannot license a change to permission settings or `CLAUDE.md`. Any slash command in the text arrives as inert prose ([docs](https://code.claude.com/docs/en/cross-session-messaging#how-a-session-treats-an-incoming-message)).

## When this backfires

- Unattended receivers swallow the coordination. The default holds messages in exactly the bypassed-permissions sessions that tend to run without a human, and a headless worker cannot show the dialog at all. Setting `crossSessionInbound` to `accept` there restores delivery and removes the gate with it.
- Approval fatigue arrives with the dialogs. Repeated hold prompts train approve-by-reflex, the documented failure mode of every [confirmation gate](../../security/human-in-the-loop-confirmation-gates.md), and expiry then drops unanswered content silently.
- Own-child verification is platform-dependent. Where Claude Code runs as process ID 1 it cannot confirm that a message came from its own child process, so a hook posting to its own socket is treated as an unverified peer and held.
- A compromised session becomes an authenticated sender. Receiving-side protection here is model instruction, which measures weaker than harness enforcement of the same rule: on DTAP-150 with GPT-5.4-mini, a prompt-only policy left 17% attack success against 4% for runtime dispatch-layer control ([Qin et al., 2026 §4.3](https://arxiv.org/abs/2605.28914v1)).
- Dependency-dense work needs more than prose. Peers acting on one-paragraph summaries make conflicting implicit decisions, the case against self-coordinating agents that Cognition argues in [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents). Split by worktree or use an orchestrator.
- Larger meshes degrade. Coordination quality in LLM peer networks falls away as the network grows ([AgentsNet](https://arxiv.org/abs/2507.08616)), so a peer inbox complements an orchestrator rather than replacing one.

## Example

A migration runs unattended in a headless worker while you work the API in a second terminal. The worker should take findings from you but never reach another machine on its own. Put the two settings in `worker-settings.json`, scoped to that session:

```json
{
  "crossSessionInbound": "accept",
  "isolatePeerMachines": true
}
```

```bash
claude -p --name migration-worker --settings ./worker-settings.json \
  "Run the tenant_id migration, then report what changed"
```

`isolatePeerMachines` requires your approval before any reply leaves the machine, and it holds even under `bypassPermissions`. A `true` from any settings scope applies, so a checked-in project file can turn the requirement on but cannot turn it off.

From the API terminal, `/list-agents` shows `migration-worker` with its working directory, which is what tells two same-named sessions apart. Ask for the message in your own words and Claude writes the text it sends:

```text
Ask the migration worker whether the tenant_id backfill finished
```

What arrives in the other session is one line of prose with a sender name and a reply address:

```text
Schema migration finished: the new column is tenant_id, and rebasing on main is safe now.
```

To close the channel instead, deny both tools and refuse arrivals in managed settings:

```json
{
  "permissions": { "deny": ["SendMessage", "ListAgents"] },
  "crossSessionInbound": "refuse"
}
```

Denying `SendMessage` also removes messaging to sub-agents and agent-team teammates, because one tool serves all three.

## FAQ

**Does a peer message let another session approve a permission prompt for me?**

No. Claude Code tells the receiving session that the message came from another session rather than from you, and a peer message never counts as your consent. It cannot answer a pending permission prompt, cannot change permission settings or `CLAUDE.md`, and any slash command in its text arrives as plain text that never executes ([cross-session messaging docs](https://code.claude.com/docs/en/cross-session-messaging#how-a-session-treats-an-incoming-message)).

**What stops two sessions from messaging each other in a loop?**

Claude Code rate-limits repeated messages per sender, drops identical repeats that arrive within a short window, and caps accepted-but-unread messages at 50 per session. Held messages cap separately at 100, with the oldest dropped past that. A loop between two sessions therefore stops on its own without anyone intervening ([docs](https://code.claude.com/docs/en/cross-session-messaging#limitations)).

**How do I tell whether a session has the feature at all?**

Run `/list-agents`, also available as `/peers`. An unrecognized command means the session lacks cross-session messaging, so check `claude --version` and then the platform and provider requirements. If the command works but a send never arrived, something narrower applies: a deny rule, the receiver's inbound controls, or a cross-machine reply-only path.

## Key Takeaways

- Treat a peer message as untrusted input with the same control-flow boundary you apply to fetched content, because a trusted peer that has been injected sends identical bytes to a hostile one
- The default gate keys on the permission class of both endpoints, and the sender's class is self-asserted, so design for a receiver that holds anything it cannot classify
- Decide a headless worker's `crossSessionInbound` value at launch, in its `--settings`, because the alternative is a session that neither delivers nor reports what it holds
- `dialogExpiry` drops rather than delivers after five minutes, so a peer inbox is not a durable queue and must not carry a fact the receiver has to have
- Confirm reachability with `/list-agents` before you rely on the channel, because an unreachable peer produces silence rather than an error

## Related

- [Claude Code Agent Teams](../../tools/claude/agent-teams.md) — supervised teammates inside one team, with structured protocol messages that stay in the team
- [Remote Session Control for Local CLI Agents](remote-session-control.md) — the human-to-session channel that cross-machine peer messages travel over
- [File-Based Agent Coordination](../multi-agent/file-based-agent-coordination.md) — the durable, ordered alternative when the coordination fact can wait for a commit
- [Agent Handoff Protocols](../multi-agent/agent-handoff-protocols.md) — what to transfer when the whole task moves rather than one fact
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](../../security/authority-confusion-untrusted-context.md) — the invariant the inbound contract implements
- [Agent View](../../tools/claude/agent-view.md) — watching many sessions from one place, which reports to you rather than between sessions
