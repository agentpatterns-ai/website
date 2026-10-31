---
title: "Mention-Shaped Placeholders as Inert Text"
term: "Mention-Shaped Placeholder"
description: "Mention-shaped role placeholders can resolve to real recipients. Validate the destination field before an agent publishes them."
tags:
  - anti-pattern
  - agent-design
  - instructions
  - tool-agnostic
aliases:
  - mention-shaped placeholder
  - role names written as mentions
  - placeholder mentions in agent-authored text
last_reviewed: 2026-10-27
maturity: adopted
status: current
---

# Mention-Shaped Placeholders as Inert Text

> Mention-shaped placeholders can name real GitHub users; writing a role as a mention can notify someone the agent never intended to contact.

Whether a mention-shaped token is inert depends on the destination field, not on what the agent meant by it. GitHub resolves `@` plus a username in a comment, issue, or pull-request body and notifies the owner, subject to repository read access and, for organization-owned repositories, organization membership ([GitHub Docs](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)). Slack uses different automatic-parsing controls for top-level text and layout blocks; automatic user-mention parsing is deprecated ([Slack formatting](https://docs.slack.dev/messaging/formatting-message-text)). Jira Cloud ADF identifies a mention through an account ID or collection name ([Atlassian mention node](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/mention/)). The rule an agent needs is therefore per-destination, and a blanket ban on the character is the wrong shape.

## The pattern

An agent drafting a pull request needs a slot for a person it cannot name, so it writes `@reviewer`, `@human`, or an invented role such as `@release-owner`. Package scopes also resemble mentions. The `types` prefix in `@types/node` matches a GitHub organization; that match alone does not show that a person receives notifications. Claude Code shipped a fix for this shape in version 2.1.309 on October 22, 2026, recorded as "Fixed Claude notifying unrelated GitHub users by writing role names and placeholders as mentions in PRs, issues and comments" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-309)).

Those spellings are not free namespace. Checked on 2026-10-27, [reviewer](https://github.com/reviewer), [human](https://github.com/human), and [maintainer](https://github.com/maintainer) resolve to personal accounts. [agent](https://github.com/agent) resolves to an organization, so it does not establish the same person-notification risk. [types](https://github.com/types) is a real organization whose profile reads "Deprecated, use NPM @types in TypeScript 2+".

## Where a glyph becomes a notification

| Destination | What carries the identity | Plain `@name` written by an agent |
|---|---|---|
| GitHub issue, PR, or comment body | the glyph itself | Resolves, and notifies the owner subject to repository read access and, in organization-owned repositories, organization membership ([GitHub Docs](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)) |
| Slack top-level text or secondary attachment text | User mentions use IDs such as `<@U123ABC456>` | Omit `link_names` to disable automatic parsing; user-name parsing is deprecated ([Slack](https://docs.slack.dev/messaging/formatting-message-text)) |
| Slack layout-block text objects | Automatic parsing has a separate control | Set `verbatim: true` to disable automatic parsing; the default is `false`. Special mentions can notify recipients ([Slack](https://docs.slack.dev/messaging/formatting-message-text)) |
| Jira Cloud ADF description or comment | A mention node's `attrs.id`, an account ID or collection name | Display text in `attrs.text` does not supply the recipient identity ([Atlassian](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/mention/)) |

## Why it works

Autocomplete can help an interactive author choose a recipient. An agent that submits a body through an API does not use that control. A person typing `@rev` into GitHub's web form is filtered by an autocomplete whose "results are restricted to repository collaborators and any other participants on the thread" ([GitHub Docs](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)). An agent posting a Markdown body skips that filter, and the account the glyph then matches need not be a collaborator at all: the Claude Code fix is described as notifying "unrelated GitHub users" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-309)).

The effect compounds, because a GitHub mention is a subscription rather than a ping. "Had your username @mentioned" sits in the list of events that automatically subscribe you to a conversation, and a later opt-out does not hold: "If you unsubscribe from a conversation and someone mentions your username or a team you're on that you're receiving updates for, then you will start to receive notifications from this conversation again" ([GitHub Docs](https://docs.github.com/en/subscriptions-and-notifications/concepts/about-notifications)). A team spelling reaches further still: enter `@organization/team-name` and "all members of that team will get subscribed to the conversation" ([GitHub Docs](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)).

An archived report describes unwanted notifications after an edit. A commenter on a W3C CSS Working Group issue hit this in 2020, had already edited the comment, and still told the wrongly mentioned person: "I don't think there's any way for us to remove you from notifications (especially now that you're replied in this thread)" ([public-css-archive](https://lists.w3.org/Archives/Public/public-css-archive/2020Apr/0517.html)). Check recipient resolution before submitting the message.

## When this backfires

- A private repository owned by an organization bounds the whole thing. GitHub notifies a mentioned person only "if the person has read access to the repository and, if the repository is owned by an organization, the person is a member of the organization" ([GitHub Docs](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)). Those conditions exclude notifications to outsiders without the required access and membership. What survives is the internal collision, where a colleague's handle happens to be `ops` or `release`.
- Slack scopes app-published user mentions to channel members: "non-members cannot be notified". Special mentions need separate handling. With automatic parsing enabled, `@everyone` can notify the workspace ([Slack](https://docs.slack.dev/messaging/formatting-message-text)).
- Jira Cloud ADF stores the recipient in a structured mention node. Check that node separately from ordinary text ([Atlassian](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/mention/)).
- Code-span advice for bodies does not establish title behavior. "The Markdown formatting will not be ignored in the title of an issue or a pull request" ([GitHub Docs](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)), so a rule that says to wrap the token in backticks leaves a title full of visible backticks. Keep the token out of titles instead.
- Banning the character breaks the job. Scoped package names, genuine review requests and handoffs all need `@`. When a notification is the point, resolve a real handle through the API.

## Example

The Rust repository enables triagebot's mention check for commit messages. Its pinned configuration contains this entry ([rust-lang/rust configuration](https://github.com/rust-lang/rust/blob/1b01decc1ca851e014b6951bdd7f2ac2f897adc9/triagebot.toml#L1562-L1564)):

```toml
# Prevents mentions in commits to avoid users being spammed
# Documentation at: https://forge.rust-lang.org/triagebot/no-mentions.html
[no-mentions]
```

This is a concrete check for one destination field. Use the destination's parsing rules when designing a corresponding check for agent-written issue or PR bodies.

## Key Takeaways

- Classify the token before writing it: role word, placeholder, package scope, or a handle you resolved. Only the last should carry a bare `@`.
- Check each field separately: GitHub body mentions, Slack top-level and block parsing controls, and Jira Cloud ADF mention nodes.
- A GitHub mention can subscribe the recipient. Prevent unwanted mentions before posting.
- Gate it at the write boundary. rust-lang/rust runs triagebot's `[no-mentions]` check over commits.

## Related

- [Agent-Authored Messages as a Deferred Exfiltration Channel](../../security/agent-authored-message-rendered-image-exfiltration.md) — the same rendering boundary with an egress risk, where a renderer fetches what the agent wrote
- [Delegating Change Descriptions to the Agent](delegating-change-descriptions.md) — the other defect in agent-written PR prose, with a focus on dropped intent
- [Agent-Laundered Bug Reports](agent-laundered-bug-reports.md) — agent-authored collaboration artifacts that cost a maintainer time they did not agree to spend
- [Chat-Platform Agent Delegation](../../workflows/chat-platform-agent-delegation.md) — the inbound direction, where a person mentions the agent to start work
- [Coordination Channel Policy for Multi-Agent Coding](../multi-agent/coordination-channel-policy.md) — choosing the channel agents coordinate through, one layer above which tokens are safe to write
