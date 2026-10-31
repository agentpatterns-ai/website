---
title: "Tool Availability by Conversation Visibility"
term: "Visibility-Scoped Tool Availability"
description: "Where a tool's authority or result depends on who asked, the conversation's other readers decide whether to offer it, because authorization cannot see the audience."
tags:
  - agent-design
  - security
  - tool-agnostic
aliases:
  - DM-only agent tools
  - surface-scoped tool availability
  - visibility-scoped tool availability
last_reviewed: 2026-10-27
maturity: emerging
---

# Tool Availability by Conversation Visibility

> A caller-scoped tool's availability can depend on conversation visibility as well as the asker's identity.

Visibility-scoped tool availability shrinks an agent's live tool set when the conversation has more than one reader, whatever the asker is authorized to do. Two conditions have to hold first. The tool's authority or its result must depend on who asked, and the surface must be readable by other people. Where either fails, this audience-based reason for withdrawing the tool does not apply.

LangChain supplies a chat-hosted example, with caller resolution already in place. LangChain's Slack integration "runs the agent as the resolved caller" in a channel exactly as in a direct message ([Connect Managed Deep Agents to Slack, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-channels-slack)). The readers are the missing piece, and LangChain treats that audience as a benefit: in channels "others can see how people use it" ([Chase and Broekhuizen, LangChain, 2026-10-24](https://www.langchain.com/blog/components-building-company-harness)).

## Two narrowings beyond the asker's permissions

LangChain's internal agents apply one each. Its GTM agent withdraws the tools that act as the invoking person once the room has other people in it: "These tools are ONLY available in DMs. In shared channels, they are not available" ([Chase and Broekhuizen, 2026-10-24](https://www.langchain.com/blog/components-building-company-harness)). Its Content Studio agent adds a named list on the actions taken under a company credential, so "not everyone can post to Twitter (they may only be able to read/draft)" (same post).

| Tool acts as | Narrowing | What it protects |
|---|---|---|
| the invoking person | offered only where that person is the audience | the asker's own access at the provider, which a channel would republish |
| a fixed company identity | an allowlist of people for the high-authority operations | the company account, which any channel member could otherwise direct |

## Why it works

The asker and the surface set two things that no single check reads. A caller-scoped credential resolves to the asker's own access, so "the agent reads that person's documents and acts under their name" ([Manage connections, LangChain docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-connections)). The surface then decides who reads the answer. An authorization check cannot catch the mismatch, because the provider authorized the asker correctly and was never told who would be in the room. LangChain states the principle from the other side in its channel docs: "Within one thread, anyone reaches the files anyone else uploaded, since transfers use the bot's Slack access rather than the caller's" ([Slack channel docs](https://docs.langchain.com/langsmith/python/managed-deep-agents-channels-slack)). Once the credential belongs to the application, the thread bounds what is reachable.

Microsoft's Teams guidance makes message visibility an input to response generation. An agent should "consider the visibility of messages they receive and use it to inform response generation, response visibility, and whether the original request should be tracked as part of the conversation's context" ([Send and receive targeted messages in group conversations, Microsoft Learn](https://learn.microsoft.com/en-us/microsoftteams/platform/agents-in-teams/targeted-messages)). Visibility is an input to the response, on that reading, and the tool set is the same decision one step earlier.

## When this backfires

- Neither the result nor the authority varies by asker. If a tool uses shared authority and returns public information, audience-based withdrawal can cost the channel a capability without protecting caller-specific data. Microsoft's guidance puts that class in public messages, which should be "purely informational and don't require user-specific context" ([Microsoft Learn](https://learn.microsoft.com/en-us/microsoftteams/platform/agents-in-teams/targeted-messages)).
- A private reply would keep the capability. Teams answers the same problem without taking anything away: a targeted message "Can be used only for one-to-one interactions between an agent and a user in channels, group chats, and meeting chats" and carries an "Only you can see this message" indicator ([Microsoft's targeted-message guidance](https://learn.microsoft.com/en-us/microsoftteams/platform/agents-in-teams/targeted-messages)). Withdraw the tool when the action is the exposure, such as mail sent as the asker from a room anyone can post in. Narrow the audience when only the answer is.
- Surface is a proxy for audience, and the proxy leaks. Microsoft warns that for a card inside a targeted message, "interactions with a card can still generate public activity that users might not expect" ([Microsoft Learn](https://learn.microsoft.com/en-us/microsoftteams/platform/agents-in-teams/targeted-messages)). A two-person private channel is refused while a direct message with the wrong person is allowed.
- Earlier uploads are already shared. In LangChain's Slack threads, file transfers run on the application credential, as quoted above, so withholding a tool now retracts nothing that arrived before.
- A runtime blind to the surface cannot apply the rule, so the deployment only looks protected.
- Work moves into private messages, a trade-off discussed in [public-channel agent work](../../workflows/public-channel-agent-work.md).

## Key Takeaways

- Gate the set whose credential names a person. A caller-scoped read returns that person's own documents.
- LangChain's Slack integration resolves the caller in a channel too, so this is not a workaround for an agent that cannot tell who is speaking.
- Withdrawing the tool and privately answering solve different problems. Pick withdrawal when the action is the exposure.
- LangChain also gates high-authority operations of a company-credential tool on a named list of people.
- Check the intended recipients as well as the surface. A direct message or channel does not settle authorization on its own.

## Related

- [Per-Caller Identity: Who an Agent's Tool Call Acts As](../../security/per-caller-identity-for-agent-tool-calls.md) — which identity the call carries, the decision this page narrows by where the conversation happens
- [Chat-Platform Agent Delegation](../../workflows/chat-platform-agent-delegation.md) — the surface itself, including what changes when several people direct one session
- [Product-Operation Tool Surfaces for In-Product Agents](product-operation-tool-surface.md) — the other reason to scope a live tool catalog per thread, where selection accuracy rather than audience drives it
- [Whose Permissions a Self-Scheduled Agent Run Carries](../../security/self-scheduled-run-authority.md) — the same question once nobody is in the conversation at all
- [Public-Channel Agent Work as Lehrwerkstatt for Team Learning](../../workflows/public-channel-agent-work.md) — the case for keeping agent work in the open, which this pattern charges against
