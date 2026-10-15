---
title: "Whose Permissions a Self-Scheduled Agent Run Carries"
term: "Self-Scheduled Run Authority"
description: "A self-created schedule pins its principal at creation and spends that authority later, unattended. Inherit the requester, or declare it at the schedule."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - scheduled run principal
  - deferred agent run identity
  - permissions of an agent-created schedule
last_reviewed: 2026-10-12
maturity: adopted
---

# Whose Permissions a Self-Scheduled Agent Run Carries

> A detached schedule the agent creates pins a principal at creation and spends that authority later, with nobody in the room.

A self-scheduled run acts as whichever principal the schedule named. The agent picks that principal mid-conversation, and the run spends it later. LangChain's Schedules SDK makes that principal a required `owner` parameter with two values: `{ type: "user" }` "selects the authenticated person of the current run, and the schedule runs as that person", while `{ type: "agent" }` schedules "run as the agent's service identity" ([Schedules, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-schedules)). Inherit the requester where the answer depends on who asked, and declare the authority at the schedule everywhere else.

## Three answers, forced by how detached the run is

| Surface | Principal | Ceiling |
|---|---|---|
| Fires in the live session | The session's own | What the session already had |
| Detached, owner pinned to a person | The requester, resolved at fire time | That person's standing access |
| Detached, authority declared at the schedule | A service identity | What the schedule was given |

Claude Code covers the first two rows. For `/loop`, which stays in the open session, the surface comparison records "Permission prompts: Inherits from session" against the cloud column's "No (runs autonomously)" ([Scheduled tasks, Claude Code docs](https://code.claude.com/docs/en/scheduled-tasks)). Detached, the principal is a person: "Anything a routine does through your connected GitHub identity or connectors appears as you" ([Routines, Claude Code docs](https://code.claude.com/docs/en/routines)).

GitHub Actions takes the third row and splits attribution off from authority. "Notifications for scheduled workflows are sent to the user who last modified the cron syntax in the workflow file" ([Events that trigger workflows, GitHub Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)), while the run authenticates as software: `GITHUB_TOKEN` is an installation access token whose "permissions are limited to the repository that contains your workflow" ([Automatic token authentication, GitHub Docs](https://docs.github.com/en/actions/concepts/security/github_token)). The person gets the notification, never the rights.

## Why it works

The receiving system authorizes from the one identity a call presents, so the principal pinned at creation is the ceiling on everything the later run can reach. Pinning the requester sets that ceiling at the asker's own access and no higher. LangChain also binds the owner to the live caller: an optional `id` "must match that person" ([Schedules, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-schedules)), so the agent cannot schedule as somebody else.

The failure runs on the same mechanism in reverse. Maloyan and Namiot describe always-on agents that "run as a single persistent process under the owner's identity, folding messaging, memory, self-authored skills, scheduling, and shell into one authority boundary" ([2026, v1](https://arxiv.org/abs/2605.13471v1)). A schedule is the artifact in that boundary that fires with nobody watching. The authority is present and the judgment that granted it is not.

## When this backfires

- A privileged requester. A one-line reminder from an administrator becomes a recurring unattended run with administrator reach: the ceiling is that person's standing access, not the task's needs. The documented cap sits on the connection rather than on the schedule: `--allowed-scope` is the "Ceiling any later authorization may request" ([Connections, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)).
- Unvetted content shaped the schedule. Maloyan and Namiot walk "a confused-deputy cron attack end-to-end through OpenClaw at a pinned commit", where attacker text persists as a memory note and resurfaces in a later owner request. Probe logs report "19/20 emitted a runtime-valid cron.add with delivery.to pointing to the attacker URL", and 7 of 10 on a two-stage variant, on an anonymized model at temperature 1.0. The authors' "Empirical evaluation is preregistered as follow-on" ([2026, v1](https://arxiv.org/abs/2605.13471v1)).
- The grant lapses while the schedule sleeps. A one-time LangChain schedule may sit "at most 365 days in the future" ([Schedules, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-schedules)), and a user-owned connection with no grant raises a `credential_authorization_required` interrupt that Slack and LangSmith Studio "handle... for the caller" ([Connections, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)). A fired schedule has no caller present to answer it.
- Removing the person from the org changes nothing for the schedule. Deprovisioning the account stops it, on Enterprise Managed Users. GitHub documents that "removing a user from an organization will not prevent scheduled workflows which had that user as their `actor` from running" ([Events that trigger workflows, GitHub Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)).
- Nobody's identity is load-bearing. Where the output does not vary by who asked, requester inheritance spends a person's standing access and allowance for no gain; Claude Code routines "belong to your individual claude.ai account" and "their runs count against your account's" limits ([Routines, Claude Code docs](https://code.claude.com/docs/en/routines)). An application credential, by contrast, "is revocable on its own, and does not depend on any person's account" ([Connections, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)).

Two controls make the inheritance defensible. Bound the lapse: when the GitHub connection is missing or expired, Claude Code routines skip runs "until you reconnect, for up to 72 hours", then "the routine turns off" ([Routines, Claude Code docs](https://code.claude.com/docs/en/routines)). Then treat the stored prompt as a task rather than a permission, as Anthropic's own routine docs do: "the fired prompt is not live user input and can't act as approval or consent for actions during the run" ([Routines, Claude Code docs](https://code.claude.com/docs/en/routines)).

## Example

The owner is one argument, and it is the whole decision:

```python
item = await schedules.create(
    owner={"type": "user"},
    cron="0 9 * * 1-5",
    timezone="America/Los_Angeles",
    prompt="Write the daily digest.",
)
```

Swap `"user"` for `"agent"` and the weekday run stops acting as the person who asked and starts acting as the deployment ([Schedules, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-schedules)). The reach of the second form is whatever the deployment's own credentials cover, which makes it the safer default for work no individual needs to own.

Which calls the agent can make at all is a separate lever, set in code rather than in the prompt: "The agent reaches this API only through tools that you write. Expose the calls the agent needs, and leave out the ones it should not reach" ([Schedules, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-schedules)). An agent given `create` and `list` but not `update` can set a reminder and read it back without rewriting one it made last week.

## Key Takeaways

- The principal is chosen while the conversation is live and spent once it is over. That makes the owner argument a security decision rather than a default to leave alone.
- Requester inheritance caps the run at one person's access and removes the person who would have refused.
- How detached the run is decides how much the choice carries. An in-session loop inherits what the session already had; a detached schedule has to name a principal, and the deployment's own is the safer default.
- A borrowed grant needs an expiry story. LangChain accepts a fire time up to 365 days out; Claude Code routines tolerate a missing or expired GitHub connection for 72 hours, then switch themselves off.
- A stored prompt is an assigned task, not consent. A schedule that reads its own payload as approval is a confused-deputy channel.

## Related

- [Per-Caller Identity: Who an Agent's Tool Call Acts As](per-caller-identity-for-agent-tool-calls.md) — the owner and credential-type matrix for a call inside a live run, which this page extends across the gap between writing a schedule and firing it
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — why inheriting a privileged requester is the cost of the table's second row
- [Authorization Continuity Across Agent Mutation](authorization-continuity-across-agent-mutation.md) — what happens to a grant when the subject it names changes, the same question without the time delay
- [Heartbeat-Bound Hierarchical Credentials for Agent Swarms](heartbeat-bound-hierarchical-credentials.md) — making borrowed authority expire by construction instead of by a reconnect window
- [Deny-Fallback Permissions for Unattended Agent Runs](../patterns/agent-design/deny-fallback-unattended-permissions.md) — what a harness does at a permission prompt nobody is there to answer
- [Session Scheduling with Loop and Cron in Claude Code](../tools/claude/session-scheduling.md) — the mechanics of the in-session surface, where no separate principal exists
