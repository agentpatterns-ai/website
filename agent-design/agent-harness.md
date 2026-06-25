---
title: "Agent Harness: Initializer and Coding Agent Pattern"
term: "Agent Harness"
description: "Structure long-running agent work as an initializer that prepares the environment and a coding agent that resumes reliably from any prior session."
tags:
  - agent-design
  - workflows
  - source:opendev-paper
  - evals
  - observability
  - tool-agnostic
  - harness-engineering
aliases:
  - initializer-coding agent pattern
  - two-phase agent harness
last_reviewed: 2026-06-12
maturity: established
---

# Agent Harness: Initializer and Coding Agent

> A two-phase agent harness pairs an initializer that prepares the environment with a coding agent that resumes from any prior session via git-based handoff artifacts.

**Related lesson:** [Long-Running Agents](https://learn.agentpatterns.ai/harness-engineering/long-running-agents/) — this concept features in a hands-on lesson with quizzes.

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

## Lazy Tool Discovery

Keep the active tool set small instead of loading every schema up front. The OPENDEV agent uses lazy tool discovery to hold down context bloat and reasoning degradation, surfacing tools to the model on demand rather than registering them all at construction time ([Bui, 2026](https://arxiv.org/abs/2603.05344)). Subagents still compile from spec to runtime and share a tool registry, but each isolates the schemas it actually exposes through [schema filtering](../multi-agent/subagent-schema-level-tool-filtering.md) — so a session pays the schema cost only for the tools it reaches for.

## Inner Loop: Execution Cycle

Each iteration follows a six-phase cycle ([Bui, 2026 §2.2.2](https://arxiv.org/abs/2603.05344)):

1. **Pre-check/compaction** — assess context pressure, compact if needed
2. **Thinking** — optional extended reasoning
3. **Self-critique** — evaluate the approach before committing
4. **Action** — LLM call with tool schemas
5. **Tool execution** — run the selected tool
6. **Post-processing** — update state, check termination conditions

LangChain's build-your-own walkthrough traces the same primitives — the loop, the tool set, and the state passed between iterations — when assembling a custom agent harness from scratch ([LangChain, how to build a custom agent harness](https://www.langchain.com/blog/how-to-build-a-custom-agent-harness)).

## Failure Modes and Fixes

**Agent tries to do too much in one session** — exhausts context mid-feature, leaving partial work.

Fix: enforce single-feature-per-session in the coding agent's instructions. Anthropic's engineering practice confirms this constraint [prevents context mid-feature exhaustion](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

**Agent prematurely declares completion** — marks a feature done before tests pass.

Fix: require passing tests as the completion gate. This rule must be explicit in the system prompt; agents without it will [optimistically self-report](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## When This Backfires

The two-phase harness adds structure and overhead — it is not always the right choice.

- **Short-lived or predictable tasks** — a task that fits in a single context window needs no initializer, progress file, or multi-session handoff machinery. The overhead of maintaining `claude-progress.txt` and baseline commits outweighs the benefit.
- **Human-in-the-loop workflows** — if a human reviews and redirects after every subtask, rigid single-feature sessions introduce unnecessary checkpointing friction. An interactive back-and-forth agent is simpler and faster.
- **Environments without reliable git access** — the pattern depends on `git log` commit history as cross-session memory. Without git, the handoff mechanism degrades to manual file management with no audit trail.

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
- Lazy tool discovery surfaces schemas on demand, holding down context bloat across a long-running session
- Git commits are structured session handoff notes, not just change records
- Require test passage as the completion gate; never allow agent self-report alone

## Related

- [Harness Engineering](harness-engineering.md) — broader engineering discipline that frames this pattern
- [Session Initialization Ritual](session-initialization-ritual.md) — the initializer's per-task setup procedure
- [Trajectory Logging via Progress Files and Git History](../observability/trajectory-logging-progress-files.md) — how `claude-progress.txt` and commits become an audit trail
- [Agent Handoff Protocols](../multi-agent/agent-handoff-protocols.md) — formalises the cross-session handoff mechanism
- [Feature List Files](../instructions/feature-list-files.md) — the priority-ordered task list the coding agent reads
- [Worktree Isolation](../workflows/worktree-isolation.md) — companion workflow for parallel session safety
- [Cross-Cycle Consensus Relay](cross-cycle-consensus-relay.md) — consensus structure that extends the initializer/worker pattern across autonomous cycles
- [Session Harness Sandbox Separation](session-harness-sandbox-separation.md) — full three-primitive virtualization that generalizes the initializer/worker split
