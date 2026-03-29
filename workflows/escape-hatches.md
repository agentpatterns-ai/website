---
title: "Escape Hatches: Unsticking Stuck Agents"
description: "Pre-planned recovery paths for agents that loop, stall, or produce degrading output — interrupt, compact, reset, or scope-reduce to unstick a running agent."
aliases:
  - "Mid-Run Correction"
  - "Steering Running Agents"
tags:
  - workflows
  - agent-design
---

# Escape Hatches: Unsticking Stuck Agents

> Pre-planned recovery paths for agents that loop, stall, or produce degrading output.

!!! note "Also known as"
    **Mid-Run Correction**, **Steering Running Agents**. This page covers *reactive* pre-built recovery mechanisms for stuck agents. For *proactive* human intervention techniques — redirecting agents mid-task before they go off course — see [Steering Running Agents](../agent-design/steering-running-agents.md).

## What "Stuck" Looks Like

An agent is stuck when it repeats the same failing approach, produces output that degrades across attempts, fills context without forward progress, or hits an error it can't resolve and keeps retrying. The failure mode matters: the right escape hatch depends on what's actually wrong.

| Symptom | Likely Cause |
|---|---|
| Same error on every attempt | Missing tool access or a structural blocker |
| Progressively worse output | Context pollution — earlier bad turns contaminate later ones |
| Circular behavior | Instruction conflict or goal ambiguity |
| Slow and incomplete results | Context overflow — earlier content dropped from window |

## Escape Hatches in Order of Cost

### 1. Interrupt and Redirect

Stop the agent mid-task and provide a more constrained goal. If the agent is trying to find something by searching broadly, redirect it to a more specific search or a different approach: "list the directory instead of searching."

This is the lowest-cost hatch — no context reset, no information loss. Use it first when the goal is still achievable but the current path isn't working.

### 2. Manual Override for a Specific Step

Take over the single step the agent can't handle, then hand control back. If an agent can't write a particular function correctly after two attempts, write it yourself and instruct the agent to continue from there.

This keeps the session productive without abandoning work already done. It works well when the stuck point is isolated — one step in a longer task.

### 3. Compact the Context

In Claude Code, `/compact` compresses the current session context while re-injecting CLAUDE.md and project instructions fresh from disk. [Claude Code documentation notes](https://code.claude.com/docs/en/memory#troubleshoot-memory-issues) that CLAUDE.md fully survives compaction — instructions given only in conversation do not.

Use `/compact` when:

- The session has been running long and output quality has dropped
- Context usage is high but the session goal is still achievable
- You want to reduce context without losing the session's progress

After compaction, the agent has a cleaner working context and fresh instructions. It does not have the conversation history that may have introduced bad assumptions.

### 4. Scope Reduction

Break the stuck task into smaller pieces. An agent that can't complete "refactor the auth module" may complete "extract token validation into a separate function" without issue.

Scope reduction is useful when the stuck agent has a real capability gap on the full task but can handle components of it. It also generates checkpoints — each smaller completion is a testable unit you can verify before proceeding.

### 5. Context Reset (New Session)

Start a fresh session when [context pollution](../anti-patterns/session-partitioning.md) is severe — many bad attempts have contaminated the conversation, or the accumulated context is large enough to affect reliability. Each Claude Code session starts with a fresh context window; [CLAUDE.md and project instructions reload automatically](https://code.claude.com/docs/en/memory).

Before resetting, note:

- What was tried and what failed (so you don't repeat it)
- What partial work exists that the next session can build on
- What constraint or instruction needs to change before retrying

A context reset without this information repeats the same failure in a new window.

### 6. Checkpoint Restore

If the agent made changes to files or state before getting stuck, roll back to the last known-good commit before retrying with a different approach. Use `git stash` or `git checkout` to restore the working state before the failed attempt.

This prevents the next session from inheriting broken state from the previous one — a common source of compounding failures.

## Build Escape Hatches into Agent Instructions

Ad-hoc intervention is reactive. Adding explicit escape hatch instructions to AGENTS.md or agent definitions makes them proactive:

```
If you cannot complete a step after 2 attempts, stop and report:
- What you tried
- What error or blocker you encountered
- What you believe is missing or wrong
Do not continue to the next step.
```

This instruction pattern converts a stuck loop into a structured escalation. The agent surfaces the failure with enough context for the human to choose a hatch, rather than spinning until the human notices.

The retry count (2 in the example) should match the task: some tasks warrant more attempts before escalation; others should escalate immediately. Set it based on how much context burn you can afford per task. [unverified: no formal evaluation of optimal retry thresholds by task type found in any source]

## Escalation: Surface, Don't Abandon

When an agent escalates a failure, the output should be actionable:

- What task was attempted
- What approach was used
- What specific error or blocker was encountered
- What the agent believes is missing (tool access, information, instruction)

Vague escalation ("I couldn't complete this") requires the human to re-investigate from scratch. Structured escalation lets the human pick the right hatch immediately.

## Programmatic Escape Hatches

Beyond human-triggered hatches, agent harnesses can enforce escape hatches automatically:

**Turn limits** — Claude Code sub-agents support a [`maxTurns`](https://code.claude.com/docs/en/sub-agents) field that caps agentic turns before forcing a stop. This is the simplest automated hatch: the agent returns whatever partial results it has when the limit hits.

**Loop detection middleware** — [LangChain's harness engineering approach](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) uses a `LoopDetectionMiddleware` that tracks per-file edit counts via tool call hooks. After N edits to the same file, it injects context telling the agent to reconsider its approach rather than letting it continue the same failing path.

**PreToolUse hooks** — Claude Code [hooks](https://code.claude.com/docs/en/hooks) can validate tool calls before execution, blocking dangerous or repetitive operations. A validation script that exits with code 2 blocks the action entirely — useful for preventing agents from retrying operations that will always fail.

**Replan gates** — [The nibzard agentic handbook](https://www.nibzard.com/agentic-handbook) recommends hard interruption points: stop on unexpected tool use, stop if diff exceeds N lines, stop on failing tests twice without narrowing scope. These deterministic checks prevent drift before it becomes a stuck loop.

**Auto-compaction** — Claude Code sub-agents [trigger automatic compaction](https://code.claude.com/docs/en/sub-agents) at approximately 95% context capacity (configurable via `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`). This prevents context overflow from silently degrading output.

## Error Preservation vs. Error Hiding

A common instinct when an agent fails is to clear the error and retry clean. [Manus found the opposite works better](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus): leaving wrong turns visible in context helps models avoid repeating the same mistakes. Error recovery works best when the agent can see what already failed.

This applies to context resets too — when starting a new session after a failure, carry forward a summary of what was tried and what went wrong. A blank slate that repeats the same approach produces the same result.

## Anti-Pattern: Infinite Retry

Letting an agent retry indefinitely is not a strategy — it's a resource burn. Every failed attempt adds to context, and context pollution compounds. The more the agent retries a doomed approach, the less context remains for a working one.

Set a retry ceiling in agent instructions and enforce it with [`maxTurns`](https://code.claude.com/docs/en/sub-agents) for sub-agents, [PreToolUse hooks](https://code.claude.com/docs/en/hooks) for tool-level validation, or CI timeouts for pipeline agents.

## Example

An agent tasked with migrating a database schema hits a permissions error on `ALTER TABLE`. It retries the same command three times, each failure adding error output to context.

**Hatch 1 — Interrupt and redirect**: Stop the agent. Tell it to run `SHOW GRANTS FOR CURRENT_USER` instead, so it discovers the missing privilege.

```
> You don't have ALTER permission on this database. Run SHOW GRANTS to check
> your current privileges, then report what's missing.
```

The agent runs the command and reports it lacks `ALTER` on the `production` schema.

**Hatch 2 — Manual override**: Grant the permission yourself (`GRANT ALTER ON production.* TO 'agent_user'`), then tell the agent to continue from where it stopped.

**Hatch 3 — Compact**: After three failed attempts, context is cluttered with error traces. Run `/compact` to compress the session. The agent restarts with clean context and the CLAUDE.md instructions re-injected, but retains awareness of the task goal.

**Hatch 4 — Scope reduction**: The full migration includes schema changes, data backfill, and index rebuilds. Break it into three separate tasks. The agent completes the schema change first, you verify, then proceed to backfill.

**Hatch 5 — Context reset**: After extended debugging, the session context is too polluted to recover. Start a new session with a note:

```
Previous session failed on ALTER TABLE — root cause was missing permission.
Permission is now granted. Resume migration from step 3: backfill staging_events.
```

**Hatch 6 — Checkpoint restore**: The agent's earlier attempt wrote a partial migration file that breaks the schema. Roll back before retrying:

```bash
git stash  # preserve the agent's partial work for reference
git checkout -- db/migrations/  # restore last known-good state
```

Then start a new attempt with the corrected approach.

## Key Takeaways

- Match the escape hatch to the failure mode — context pollution needs a reset; a blocked step needs a manual override
- `/compact` cleans context without losing session progress; CLAUDE.md re-injects automatically
- Build escalation instructions directly into agent definitions so agents surface failures structurally rather than spinning
- Before a context reset, document what failed and why — a fresh session repeating the same approach produces the same result
- Automate escape hatches where possible — `maxTurns`, loop detection middleware, and PreToolUse hooks catch stuck states without human intervention

## Unverified Claims

- Optimal retry thresholds vary by task type — no published benchmark compares retry counts across task categories [unverified: no formal evaluation of optimal retry thresholds by task type found in any source]

## Related

- [Steering Running Agents](../agent-design/steering-running-agents.md) — proactive mid-run redirection techniques
- [Human in the Loop](human-in-the-loop.md) — human intervention patterns and manual override workflows
- [Agent Debugging](../observability/agent-debugging.md)
- [Continuous Agent Improvement](continuous-agent-improvement.md)
