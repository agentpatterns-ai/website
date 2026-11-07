---
title: "Define Async Task Update and Approval Contracts"
description: "Specify how background task updates, cancellation, approval requests, and completion events interact before relying on an asynchronous agent workflow."
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
last_reviewed: 2026-11-06
maturity: emerging
---

# Define Async Task Update and Approval Contracts

> Give every background task an explicit update, cancellation, and approval contract before accepting its result.

LangChain's [async-agent design discussion](https://www.langchain.com/blog/agents-are-going-async) describes work that continues while the user is elsewhere. This changes the handoff problem: the application must deliver later results and requests for input. A task identifier alone does not tell a reviewer which instructions produced an artifact.

## Distinguish a task from its runs

Deep Agents exposes start, check, update, cancel, and list tools. Updating a task creates a new run on the same thread; its task ID stays unchanged. The default interrupts the previous run. With `update_strategy="enqueue"`, the follow-up waits behind it. This option requires `deepagents>=0.7.30` and is beta ([lifecycle documentation](https://docs.langchain.com/oss/python/deepagents/async-subagents#understand-the-lifecycle)).

Record both task and run identifiers in review evidence. As a proposed application contract, attach the requested scope, input revision, output location, and verification result to each run. Bind verification evidence to the current requested scope and input revision before accepting the result.

## Preserve approval ownership

A waiting Deep Agents task has pending input or approval requests. The supervisor cannot approve for the user; the application resumes the child's own thread with the answer. Updating a waiting task drops its pending request. Even an enqueued follow-up starts if the earlier run pauses for approval, dropping that request ([waiting behavior](https://docs.langchain.com/oss/python/deepagents/async-subagents#handle-subagents-waiting-for-input)).

Treat these as explicit transitions in the application's interface. Before sending a follow-up, show whether it replaces an unresolved request. Keep cancellation separate from approval: stopping a task supplies no permission for a replacement run. Require each consequential action to resolve against the applicable authorization record.

## Deliver and verify late results

Deep Agents stores task metadata outside compacted messages. Its notifications carry task and run IDs plus status in structured metadata, although the message class is `HumanMessage` ([state and notifications](https://docs.langchain.com/oss/python/deepagents/async-subagents)). Use that metadata to distinguish completion events from human replies.

Test the following application behavior before unattended use:

| Event | Proposed acceptance check |
|---|---|
| Updated run completes | Review opens the artifact and checks from that run |
| Worker errors or times out | Failure reaches the task owner with recoverable evidence |
| Worker waits for approval | Request reaches the user and remains visibly unresolved |
| User cancels | Interface shows cancellation without claiming rollback |
| Old run reports after an update | Its result cannot silently replace the current artifact |

These are recommended checks, not guarantees provided by the cited framework. Assign an owner for unhandled failures and expired requests; a background job should not disappear because nobody is watching its chat.

## Key Takeaways

- Review the run that produced the result, not merely its stable task ID.
- Check update semantics at approval boundaries, including queued updates.
- Deliver errors and pending requests with the same care as successful results.

## Related

- [Async Non-Blocking Subagent Dispatch](async-non-blocking-subagent-dispatch.md) — launch and continue useful work
- [Agent Handoff Protocols](agent-handoff-protocols.md) — structure delegated work and results
- [Background–Foreground Handoff](../../workflows/background-foreground-handoff.md) — return background work to interactive review
