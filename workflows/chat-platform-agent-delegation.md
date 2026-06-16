---
title: "Chat-Platform Agent Delegation: Invoking Cloud Coding Agents from Team Channels"
term: "Chat-Platform Agent Delegation"
description: "Mentioning an agent in a Slack or Microsoft Teams channel delegates a coding task from where coordination already happens — surfaced to the whole team, with a concentrated lethal-trifecta posture that the IDE entry point hides."
tags:
  - workflows
  - agent-design
  - security
  - tool-agnostic
aliases:
  - chat as agent control surface
  - chat-platform delegation
  - mentioning agents in chat channels
last_reviewed: 2026-06-12
maturity: established
---

# Chat-Platform Agent Delegation

> Mentioning a coding agent in a chat channel delegates work from where the team coordinates and concentrates the lethal trifecta on the chat principal.

## The Surface

A cloud coding agent registers as a chat-platform participant — a bot user in Microsoft Teams, Slack, or Discord — and accepts task delegation by `@mention` from inside a channel. The agent reads the thread for context, picks a repository, runs in its sandbox, and returns either a status message or a pull-request link to the same thread.

The pattern moves agent invocation out of the IDE and into the asynchronous medium where the team already coordinates work.

```mermaid
graph TD
    A[Team member] -->|@mention in channel| B[Chat platform]
    B -->|webhook/event| C[Agent runtime]
    C -->|read thread context| B
    C -->|select repo + model| D[Forge: GitHub/GitLab]
    C -->|run sandbox| E[Code changes]
    E --> D
    D -->|PR link| B
    B -->|status card| A
```

## Surface Availability

Chat-platform delegation ships on more than one agent as of June 2026, and the set of supported chat platforms differs per agent.

| Agent | Chat surface | Notes |
|-------|--------------|-------|
| Cursor | Slack, Microsoft Teams | `@Cursor` in any channel; auto-selects repo and model from the message and thread context; returns a PR to the thread. Teams added 2026-05 ([Cursor changelog](https://cursor.com/changelog/microsoft-teams), [Cursor docs](https://cursor.com/docs/integrations/microsoft-teams)) |
| GitHub Copilot coding agent | Slack, Microsoft Teams | Mention `@GitHub` in a Slack thread with a prompt; the coding agent runs in the background using the thread as context and opens a PR. Slack went generally available 2025-10-28; the GitHub app for Teams offers the same context-to-PR flow ([GitHub Changelog](https://github.blog/changelog/2025-10-28-work-with-copilot-coding-agent-in-slack/), [GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/integrate-cloud-agent-with-slack)) |
| Claude Code | None as built-in | `@claude` triggers are GitHub-comment based, not chat-platform ([Claude Code docs](https://code.claude.com/docs/en/github-actions)) |

Surface availability matters when comparing delegation strategies — the chat platforms a team already runs (Slack vs Teams) determine which agents can adopt the pattern without bridging to a different tool.

## The Mechanism — Locality of Coordination Context

Chat-as-control-surface works because **the channel already holds the decision context** that produced the request. The thread captures who proposed the change, what objections were raised, and which constraints were agreed. An agent that reads the thread before acting inherits that context without the user having to restate it.

Cursor's Teams integration makes the locality explicit: its Cloud Agents "read the relevant thread or chat context when invoked, understanding and acting on your team's discussion" ([Cursor docs](https://cursor.com/docs/integrations/microsoft-teams)). Copilot's Slack agent does the same — it "captures the entire thread as context" before opening the PR ([GitHub Changelog](https://github.blog/changelog/2025-10-28-work-with-copilot-coding-agent-in-slack/)). The IDE entry point cannot do this — an IDE-invoked agent sees only what the user pastes into the prompt.

The mechanism is locality, not visibility. Visibility is a side effect — every channel member sees the delegation and the result — and it cuts both ways (see [Failure Modes](#failure-modes)).

## Comparison to Adjacent Surfaces

Chat is one of three async delegation surfaces. Each suits different contexts.

| Surface | Audience | Repo binding | Trifecta posture |
|---------|----------|--------------|------------------|
| Chat channel (`@Cursor`, `@GitHub` in Slack/Teams) | Whole channel | Heuristic: message content → recent history → default | All three legs co-located on the chat principal |
| PR comment (`@copilot` in GitHub) | PR participants | Bound to the PR's repository | Same trifecta, scoped to forge audience |
| IDE side-panel (Copilot Chat, Cursor composer) | Single user | Bound to the open workspace | Private-data + egress; untrusted-content only if the user pastes it |

Chat broadens the audience and removes the IDE context switch. PR-comment delegation already accepts the same trifecta posture, but the audience is the smaller PR-participants set. IDE delegation is the narrowest — the untrusted-content leg only closes when the user voluntarily pastes external content.

## Repository Binding Is Heuristic, Not Channel-Bound

Cursor's selection hierarchy is explicit options → message content → recent agent activity → dashboard default ([Cursor docs](https://cursor.com/docs/integrations/microsoft-teams)). A user can write `@Cursor in cursor-app, fix the login bug` to pin the repo, but the default behaviour is inference. Teams that expect the channel itself to constrain blast radius get a softer guarantee than the framing implies — a single ambiguous message can silently route work to the wrong repo, surfacing only at PR review.

If channel-bound delegation is the security model the team wants, it must be enforced outside the agent — by restricting which repositories the bot account can write to, not by trusting the agent's inference.

## The Load-Bearing Risk — Trifecta Concentration

Chat delegation closes all three legs of the [lethal trifecta](../security/lethal-trifecta-threat-model.md) on the chat principal:

- **Private data** — the agent reads the repository it acts on
- **Untrusted content** — any channel member, and in shared or Connect channels any external participant, can post messages that become prompt context
- **Egress** — the agent writes pull requests to the forge, and posts status back to the channel

Per Willison's model, this combination is sufficient for exfiltration via a single injected message ([Willison, 2025](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)). Adding chat delegation to a project that already audits every new MCP server for the lethal trifecta must run the same audit on the chat principal. The cheapest leg to remove is usually untrusted content: restrict the bot to specific channels, treat channel content outside an explicit `@mention` as out-of-scope, or run the agent in a sandbox with no network egress beyond the forge API.

Cursor's Cloud Agents require temporary code storage while running, so legacy Privacy Mode is not supported for the integration; Cursor instead ships a snippet-exposure toggle for status messages ([Cursor docs](https://cursor.com/docs/integrations/microsoft-teams)) — a partial mitigation, not trifecta removal.

## Failure Modes

- **Shared and Connect channels**: external participants can post into the channel, so any mention becomes untrusted content from outside the security boundary. The trifecta closes instantly on the agent principal.
- **Heuristic repo binding silently mis-routes**: an ambiguous message routes work to the wrong repo. Compute and reviewer attention are spent before the mismatch surfaces at GitHub PR review.
- **Channel without engineering quorum**: delegation from a marketing or product channel where no engineer monitors produces orphan PRs. The visibility benefit only pays out if the audience can act on the result.
- **High-frequency channels**: agent-status messages compete with human messages; the team mutes the bot; visibility regresses to worse than IDE-private invocation because nobody reads the status updates.
- **Auth-model mismatch**: chat-platform identity (Slack or Microsoft Teams) binds to forge identity. Joint blast radius is whatever the forge account can do — if the chat identity is broader than the forge identity (contractors with Teams access but limited repo access), the link inverts the expected permission boundary.

## When to Adopt

Adopt chat delegation when all of the following hold:

- The agent platform ships a chat surface on a platform the team runs (today: Cursor and GitHub Copilot, on Slack and Microsoft Teams; verify before assuming)
- Coordination for the affected repository already happens in the chat platform
- The bot can be scoped to specific channels and to specific repositories
- A lethal-trifecta audit has been run on the chat principal and the chosen leg-removal mechanism is wired before the integration goes live

Skip it when the agent's IDE or PR-comment entry point already covers the workflow — the marginal locality gain does not justify a new trifecta surface in repositories with sensitive data or broad write scope.

## Key Takeaways

- Chat-platform delegation moves the invocation surface from the IDE to the team's coordination layer; the mechanism is locality of context, not visibility
- Surface availability is uneven across platforms — Cursor and GitHub Copilot both ship chat delegation on Slack and Microsoft Teams today; Claude Code does not ship chat-platform invocation as of June 2026
- Repository binding is heuristic, not channel-bound; enforce binding outside the agent if it must be a security boundary
- The pattern concentrates the lethal trifecta on the chat principal — extend the trifecta-audit posture used for MCP servers to the chat integration
- Shared channels, low-engineering-quorum channels, and high-frequency channels are predictable failure conditions

## Related

- [Issue-to-PR Delegation Pipeline](issue-to-pr-delegation-pipeline.md) — the issue-assignment surface that chat delegation parallels
- [Issue-Tracker as Agent Dispatch Surface](issue-tracker-agent-dispatch-surface.md) — parallel dispatch surface where the ticket, not the channel, is the principal
- [Programmatic Cloud-Agent Dispatch](programmatic-cloud-agent-dispatch.md) — the same cloud-agent surface invoked via REST/webhook instead of `@mention`
- [Public-Channel Agent Work](public-channel-agent-work.md) — the visibility policy layered on top of chat delegation to force conversations to channels everyone can read
- [In-Thread Side-Channel](in-thread-side-channel.md) — adjacent same-session bounded sub-conversation, orthogonal mechanism
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md) — the threat model this pattern concentrates
- [Agent Governance Policies](agent-governance-policies.md) — enterprise-level controls for chat-platform agent surfaces
- [GitHub Copilot Cloud Agent](../tools/copilot/coding-agent.md) — the GitHub-native cloud agent surface chat delegation often targets
