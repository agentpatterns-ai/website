---
title: "Agent Host Review Comments: Server-Side Feedback Transport"
description: "Review comments in VS Code 1.126 live on the agent host server, not the local session — three tools let agents read, add, and resolve them after disconnect."
tags:
  - copilot
  - code-review
applies_to: "copilot@1.x"
last_reviewed: 2026-06-30
status: current
---

# Agent Host Review Comments: Server-Side Feedback Transport

> In VS Code 1.126, Copilot stores review comments on the agent host server, so feedback survives client disconnects and agents can act on it later.

Server-side review comments change who can act on feedback and when. A background agent running on the agent host can read the comments you left, address them, and mark them resolved — even after your editor client has closed. VS Code 1.126 (released June 24, 2026) ships this transport under the name "Agentic code feedback with agent host harnesses" ([VS Code 1.126 release notes](https://code.visualstudio.com/updates/v1_126)). The value is greatest for async and background-agent workflows; for synchronous local review where the client never disconnects, the transport adds overhead without adding resilience.

## How it works

Review comments you leave on generated code are stored on the agent host, not in your local editor session. The VS Code release notes describe the behavior directly: comments are "stored on the agent host, so the agent can interact with your feedback by using server-side tools such as `listComments` and `resolveComments`" ([VS Code 1.126](https://code.visualstudio.com/updates/v1_126)). The agent can also create comments for you: "the agent can also create the comments for you by using the `addComment` tool" ([VS Code 1.126](https://code.visualstudio.com/updates/v1_126)).

Three tools form the review-comment transport:

- `listComments` — reads comments the reviewer left on generated code
- `addComment` — creates a new inline comment without the reviewer typing it
- `resolveComments` — marks a comment resolved after the agent has addressed it

## The /code-review flow

The `/code-review` skill works within this transport. The review skill "reviews your code and adds comments inline, which you can then accept or delete before submitting them to an agent" ([VS Code 1.126](https://code.visualstudio.com/updates/v1_126)). The flow is: review runs and adds comments; you see those comments inline; you accept the ones you want the agent to act on and delete the rest; then you submit. The accept-or-delete step keeps you in control of which feedback reaches the agent.

## Async review workflow

Because comments live on the server rather than in the local session, you can leave comments and disconnect. The VS Code release notes confirm this directly: "This works even when you disconnect the client, since the comments live on the server rather than in your local session" ([VS Code 1.126](https://code.visualstudio.com/updates/v1_126)). A background agent — running on the agent host after the editor client has closed — can call `listComments`, work through each open item, and call `resolveComments` as it finishes. You reconnect later and find resolved comments instead of an open queue.

## PR comment permission checkpoint

When you ask the agent to address not-yet-accepted PR review comments, it does not proceed without permission. The VS Code release notes describe the checkpoint: "when you ask the agent to resolve PR comments that you haven't accepted yet, it first requests your permission to view them, and once you grant access, it addresses the PR review items" ([VS Code 1.126](https://code.visualstudio.com/updates/v1_126)). The agent cannot silently pull in and act on unreviewed feedback; it surfaces the request and waits.

## Why it works

The capability works by decoupling review-feedback state from the client session. Review comments are persisted as server-side state on the agent host rather than in the local editor session, so a background agent can read, act on, and close feedback after the human's client has disconnected ([VS Code 1.126](https://code.visualstudio.com/updates/v1_126)). This is the same state-lifecycle decoupling that makes [remote agent host sessions](../../patterns/agent-design/remote-agent-host-sessions.md) durable — the client is a view onto server-held state, so client disconnects are UI events rather than state events. Applied to the review-comment channel, it means the agent's work queue does not reset when you close the editor.

## When this backfires

- Synchronous, never-disconnecting local review. When the client stays attached throughout a review session, server-side persistence delivers no resilience. The permission-checkpoint round-trip for not-yet-accepted PR comments adds a step a synchronous reviewer would have skipped. For a solo developer doing a small, in-session review, the machinery costs more than it saves.
- Rubber-stamp resolution at scale. A frictionless "resolve all PR comments" path lets an agent mark feedback resolved without the reviewer re-checking the resolution. Beyond about 400 changed lines a reviewer is no longer reviewing effectively, and making resolution easier amplifies that problem rather than compensating for it ([Bryan Finster on AI code review](https://bryanfinster.substack.com/p/ai-broke-your-code-review-heres-how)). The [trust-without-verify anti-pattern](../../patterns/anti-patterns/trust-without-verify.md) applies: polished-looking resolved comments are not the same as correctly addressed ones.
- Same-model self-review confirmation bias. If the agent that wrote the code also reads and resolves the review feedback, durable state makes a closed self-review loop more convenient — same training data, same blind spots ([Sean Goedecke on AI agents and code review](https://www.seangoedecke.com/ai-agents-and-code-review/)). The [LLM review overcorrection anti-pattern](../../patterns/anti-patterns/llm-review-overcorrection.md) covers the misclassification failure mode that follows from this dynamic.
- VS Code 1.126 agent host only. The transport is specific to the VS Code 1.126 agent host harness. Teams on other editors or harnesses have no portable equivalent.

## Key Takeaways

- Review comments in the VS Code 1.126 agent host live on the server, not the local session — client disconnect does not lose them
- Three tools form the transport: `listComments` reads feedback, `addComment` creates it, `resolveComments` closes it
- The `/code-review` skill adds comments inline for the reviewer to accept or delete before they reach the agent
- The PR-comment permission checkpoint prevents the agent from acting on unreviewed feedback without your consent
- The transport's value is greatest for async and background-agent workflows; for synchronous local review it adds overhead without resilience
- The accept-or-delete step and the permission checkpoint guard against rubber-stamp resolution — bypass neither

## Related

- [Agent-Assisted Code Review: Agents as PR First Pass](../../code-review/agent-assisted-code-review.md) — the review pattern (who reviews what); this page covers where the comments live
- [Review Feedback to Rule Loop](../../code-review/review-feedback-to-rule-loop.md) — promoting recurring comments into harness rules over time
- [Batched Suggestion Application](../../code-review/batched-suggestion-application.md) — bulk-applying suggestions on PRs after feedback is collected
- [Remote Agent Host Sessions over SSH and Dev Tunnels](../../patterns/agent-design/remote-agent-host-sessions.md) — the general host-owns-state principle; this page applies it to review-comment state
- [Trust Without Verify](../../patterns/anti-patterns/trust-without-verify.md) — why polished resolved comments are not the same as correctly addressed ones
