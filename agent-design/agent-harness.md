---
title: "Agent Harness: Initializer and Coding Agent Pattern"
description: "Structure long-running agent work as an initializer that prepares the environment and a coding agent that resumes reliably from any prior session."
tags:
  - agent-design
  - workflows
  - source:opendev-paper
  - evals
  - observability
aliases:
  - initializer-coding agent pattern
  - two-phase agent harness
---
# Agent Harness: Initializer and Coding Agent

> Structure long-running agent work as two distinct phases — an initializer that prepares the environment and artifacts, and a coding agent that picks up reliably from wherever any prior session left off.

## The Stateless Session Problem

Agents have no memory between sessions. Without explicit design, they lose track of progress, repeat completed work, or [declare premature completion](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) when context pressure rises. A deliberate harness — two coordinated agents with structured artifacts — gives every session a [reliable on-ramp](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## Initializer Agent

The initializer runs once at the start of the overall task (not per session):

- Run environment setup scripts (e.g., `init.sh`) and verify readiness
- Create a `claude-progress.txt` recording what is started, completed, and remaining
- Make a baseline git commit so the coding agent has a clean starting point

## Coding Agent

Each session starts with the coding agent reading orientation artifacts before touching any code:

1. `git log` — commits since the baseline
2. `claude-progress.txt` — current task status
3. Feature list file — which features are complete, failing, or next

The agent selects the highest-priority incomplete work, completes it, and leaves clean artifacts for the next session.

## Git Commits as Cross-Session Memory

Each commit message is a structured handoff note documenting:

- What was implemented
- What tests pass
- What the next incomplete task is

`git log` becomes a human- and agent-readable audit trail of session progress.

## Eager Construction

Build system prompt and tool schemas before the constructor returns, eliminating first-call latency ([Bui, 2026 §2.2.1](https://arxiv.org/abs/2603.05344)). Assembly runs in three phases: skills discovery, subagent registration, main agent initialization. Subagents compile from spec to runtime, sharing a tool registry while isolating through [schema filtering](../multi-agent/subagent-schema-level-tool-filtering.md).

## Inner Loop: Execution Cycle

Each iteration follows a six-phase cycle ([Bui, 2026 §2.2.2](https://arxiv.org/abs/2603.05344)):

1. **Pre-check/compaction** — assess context pressure, compact if needed
2. **Thinking** — optional extended reasoning
3. **Self-critique** — evaluate the approach before committing
4. **Action** — LLM call with tool schemas
5. **Tool execution** — run the selected tool
6. **Post-processing** — update state, check termination conditions

## Failure Modes and Fixes

**Agent tries to do too much in one session** — exhausts context mid-feature, leaving partial work.

Fix: enforce single-feature-per-session in the coding agent's instructions [unverified].

**Agent prematurely declares completion** — marks a feature done before tests pass.

Fix: require passing tests as the completion gate. This rule must be explicit in the system prompt; agents without it will [optimistically self-report](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## Session Handoff Checklist

Every coding session ends with:

- All changes committed with a descriptive message
- `claude-progress.txt` updated with accurate status
- Tests passing for the completed feature
- Next priority task identified

## Example

The following shows what a `claude-progress.txt` handoff artifact looks like after a coding session, and what the next session's orientation reads before touching any code.

```text
# claude-progress.txt — updated 2026-03-10T14:32Z

## Completed
- [x] feat: user authentication flow (commit a3f92c1)
- [x] feat: session management and token refresh (commit b87de04)

## In Progress
- [ ] feat: profile page — INCOMPLETE, do not mark done until tests pass

## Next Priority
- [ ] feat: notification preferences

## Notes
- Run `./init.sh` if environment is cold-started
- Use `pytest tests/` as the completion gate before updating this file
```

At the start of a new coding session, the agent reads orientation artifacts in this order before writing a single line of code:

```bash
git log --oneline -10          # What has been committed since baseline?
cat claude-progress.txt        # What is the current task status?
cat features.md                # Which features remain, and in what priority order?
```

Only after this orientation does the agent select the highest-priority incomplete item and begin work. The session ends with a commit whose message documents what was implemented, which tests pass, and what the next task is — making `git log` a readable cross-session audit trail.

## Key Takeaways

- The initializer runs once; the coding agent runs once per session, always reading artifacts before acting
- Eager construction eliminates first-call latency by front-loading prompt and schema assembly
- Git commits are structured session handoff notes, not just change records
- Require test passage as the completion gate; never allow agent self-report alone

## Unverified Claims

- Enforcing single-feature-per-session in the coding agent's instructions prevents context exhaustion `[unverified]`

## Related

- [Feature List Files](../instructions/feature-list-files.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Worktree Isolation](../workflows/worktree-isolation.md)
- [Agent Memory Patterns](agent-memory-patterns.md)
- [Trajectory Logging via Progress Files and Git History](../observability/trajectory-logging-progress-files.md)
- [Harness Engineering](harness-engineering.md)
- [Session Initialization Ritual](session-initialization-ritual.md)
- [Loop Strategy Spectrum](loop-strategy-spectrum.md)
- [Agent Turn Model](agent-turn-model.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
- [Classical SE Patterns and Agent Analogues](classical-se-patterns-agent-analogues.md)
- [Memory Synthesis from Execution Logs](memory-synthesis-execution-logs.md)
- [Persona as Code](persona-as-code.md)
- [Agent Self-Review Loop](agent-self-review-loop.md)
- [Agent Loop Middleware](agent-loop-middleware.md)
- [Subtask-Level Memory](subtask-level-memory.md)
- [Goal Monitoring and Progress Tracking](goal-monitoring-progress-tracking.md)
- [Episodic Memory Retrieval](episodic-memory-retrieval.md)
