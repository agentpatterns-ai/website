---
title: "From Task Agents to Goal Agents: Harness Additions"
description: "A goal agent picks its own work and runs in the background. One practitioner lists six harness additions that follow, and this page maps each to existing pages."
tags:
  - workflows
  - agent-design
  - tool-agnostic
aliases:
  - task agent to goal agent shift
  - goal agent harness checklist
last_reviewed: 2026-11-23
maturity: emerging
---

# From Task Agents to Goal Agents: Harness Additions

> Harrison Chase argues that giving an agent a goal instead of a task adds six harness requirements: task visibility, tool limits, an inbox, feedback, triggers, and memory.

A goal agent receives an outcome such as "Maintain a blog" and chooses its own work. A task agent receives a bounded assignment such as "Draft this blog". Harrison Chase, writing on LangChain's blog, argues that this shift changes what the harness around the agent must provide, and Chase's post covers six additions ([LangChain, 16 Nov 2026](https://www.langchain.com/blog/from-tasks-to-goals)). The post is one practitioner's opinion and carries no measurements, so use the list as a review checklist for your own system. It has no outcome data behind it.

## What changes between a task and a goal

Chase describes two practical shifts: "From specifying an action to specifying an outcome" and "From a bounded assignment to an ongoing responsibility" ([LangChain](https://www.langchain.com/blog/from-tasks-to-goals)). Chase's post supports each cell below.

| | Task agent | Goal agent |
|---|---|---|
| Who picks the work | You specify the tasks | The agent breaks the goal into tasks, does some, and updates the task list |
| Tool calls | You largely know which tools it will call | You may not know which tools it needs |
| Questions | You are in the loop and the agent can ask in chat | It may run in the background and needs another route to a person |
| Run length | It runs until the task completes | It wakes at times to do some work |
| Context | You supply the relevant context each time | The agent carries decisions and feedback forward |

Chase's conclusion: "You're delegating decisions about what work to do and when to do it" ([LangChain](https://www.langchain.com/blog/from-tasks-to-goals)).

## Six harness additions

The post states each requirement and gives a few examples, but it does not prescribe an implementation. The pages linked under each heading are this site's mapping onto the requirement, which is my inference.

### 1. A visible task list

When the agent chooses the tasks, it has to brainstorm and select well. Chase says it must be somewhat creative and varied, because suggesting the same tasks over and over is "not great". Chase's practical advice is a way to see what the agent is doing, such as a to-do list, plus prompting that pushes it toward varied tasks ([LangChain](https://www.langchain.com/blog/from-tasks-to-goals)).

- [Background Todo Agent](../patterns/agent-design/background-todo-agent.md) routes to-do list maintenance to a small background model.
- [Goal Recitation](../context-engineering/goal-recitation.md) rewrites objectives and to-do lists at the tail of context to counter drift.

### 2. Tighter control over callable tools

Chase's example: asking for an email (a task) implies a Gmail tool and maybe a calendar tool. Asking to "reduce my coordination burden while keeping important commitments on track" (a goal) could need email, text, search, a browser, or other tools. Chase's advice is more control over which tools the agent can and cannot call ([LangChain](https://www.langchain.com/blog/from-tasks-to-goals)).

- [Deny-Fallback Permissions for Unattended Agent Runs](../patterns/agent-design/deny-fallback-unattended-permissions.md) denies any call that would have reached a permission prompt when no human is present.
- [Classifier-Gated Auto-Permission](../patterns/agent-design/classifier-gated-auto-permission.md) has a separate classifier inspect each tool call and re-prompt on escalations.

### 3. An inbox for clarifying questions

On a task, a missing detail becomes a follow-up question in chat. A background goal agent may have no chat open, so Chase says it needs a route to a person, "whether through Slack or a dedicated UI" ([LangChain](https://www.langchain.com/blog/from-tasks-to-goals)).

- [Deferred Permission Pattern](../patterns/agent-design/deferred-permission-pattern.md) pauses a headless Claude Code session at a tool call and resumes it after the caller collects human input through its own UI. Its example handles an `AskUserQuestion` call.
- [Define Async Task Update and Approval Contracts](../patterns/multi-agent/async-task-update-contracts.md) specifies how background task updates and approval requests interact.

### 4. A feedback signal

Chase says the agent needs to know how it is doing, either from a metric or from explicit human feedback. A metric is easy to track automatically, but it is "never wise to blindly optimize a metric". Chase's advice is to use both: define how the agent assesses progress, and "give people a way to correct its interpretation of success" ([LangChain](https://www.langchain.com/blog/from-tasks-to-goals)).

- [Goal Contract](../patterns/agent-design/goal-contract-completion-evaluator.md) covers the completion-check half, where a separate evaluator model decides when a stated condition holds.
- [Goal Monitoring and Progress Tracking](../patterns/agent-design/goal-monitoring-progress-tracking.md) covers progress tracking and drift detection.

### 5. Triggers with stopping rules

Chase lists four ways a goal agent wakes up: heartbeats every X minutes, recurring cron, one-off cron (a reminder), and listening to an event stream. It also needs a way to stop, pause or ignore them. A heartbeat every thirty minutes that repeats the same question is, in Chase's words, "a terrible UX". Chase adds that "Sometimes doing nothing is the right action" ([LangChain](https://www.langchain.com/blog/from-tasks-to-goals)).

- [Loop Trigger Selection](../loop-engineering/loop-trigger-selection.md) pairs each trigger type with its stopping rule, including a clean no-op as a terminal state for a scheduled firing.
- [Session Scheduling with Loop and Cron in Claude Code](../tools/claude/session-scheduling.md) shows one tool's scheduled shape.
- [Whose Permissions a Self-Scheduled Agent Run Carries](../security/self-scheduled-run-authority.md) covers the authority a detached trigger spends later.

### 6. Memory that carries decisions across runs

Chase says memory has not been needed much in a task-based world unless you repeat the same task, because you can supply the context each time. With an ongoing responsibility, more of that burden moves to the agent. Chase's example: rejecting a blog topic should shape later topic choices, "not just the current draft" ([LangChain](https://www.langchain.com/blog/from-tasks-to-goals)).

- [Agent Memory Patterns](../patterns/agent-design/agent-memory-patterns.md) covers persisting knowledge across conversations in scoped memory.
- [Memory-Induced Tool Drift](../patterns/anti-patterns/memory-induced-tool-drift.md) is the cost to weigh: biases held in long-term memory can steer tool-call parameters in unrelated contexts.

## Where the checklist stops

- One source. The post gives no data on which addition matters most, which to build first, or whether six is the complete set.
- Two meanings of goal. [Goal-Driven Autonomous Loop with Budget Cap](../loop-engineering/goal-driven-autonomous-loop.md) describes a goal as a stored objective with a completion audit, so the loop ends when the goal is met. Chase's examples ("Maintain a blog", "Make this product successful") read as responsibilities without a finish line, which fits the author's section on triggers and stopping rules. That reading is my inference. Check which meaning your harness implements before borrowing either page's controls.
- The harness mappings above rest on the linked pages' own sources, not on the LangChain post.

## Key Takeaways

- Review a task-agent harness against six gaps before you give the agent an open goal: task visibility, tool limits, a question route, feedback, triggers, and cross-run memory.
- Pair any metric with a human route to correct it, and treat doing nothing as a valid result of a trigger firing.
- Memory lets a goal agent carry feedback forward, and the linked tool-drift page documents the bias it can add.
- Check whether "goal" in your harness means a stored objective with an end, or an ongoing responsibility. The controls differ.
- The six-item list is one author's argument. Test it against your own failure logs before treating it as complete.

## Related

- [Loop Trigger Selection](../loop-engineering/loop-trigger-selection.md) — pairing a loop's start with its stop
- [Goal-Driven Autonomous Loop with Budget Cap](../loop-engineering/goal-driven-autonomous-loop.md) — the stored-objective meaning of goal
- [Recurring Agent Job Delegation](recurring-agent-job-delegation.md) — widening a recurring job's remit on per-run evidence
- [Background-to-Foreground Handoff](background-foreground-handoff.md) — handing background work to a person
- [Goal Monitoring and Progress Tracking](../patterns/agent-design/goal-monitoring-progress-tracking.md) — durable progress signals for long-running agents
