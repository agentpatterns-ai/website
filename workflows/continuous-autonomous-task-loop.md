---
title: "Continuous Autonomous Task Loop"
description: "Run a self-directed agent loop that reads a task backlog, executes each item via a ReAct inner loop, commits results, and repeats with fresh context per task."
tags:
  - workflows
  - agent-design
  - tool-agnostic
term: "Continuous Autonomous Task Loop"
aliases:
  - continuous task loop
  - autonomous task loop
last_reviewed: 2026-08-04
maturity: established
---

<!-- source: nibzard/awesome-agentic-patterns (Apache 2.0, https://github.com/nibzard/awesome-agentic-patterns) — retain attribution per license -->

# Continuous Autonomous Task Loop

> A self-directed agent loop reads a task backlog, executes each item via a ReAct inner loop, commits, and repeats with fresh context per iteration.

## How the loop works

The pattern has two nested cycles: an outer task loop that iterates over the backlog, and an inner ReAct turn (Thought → Action → Observation) that executes each task.

```mermaid
graph TD
    A[Read backlog] --> B[Select next task]
    B --> C[Execute via ReAct inner loop]
    C --> D[Commit changes]
    D --> E{More tasks?}
    E -->|Yes| F[Clear context]
    F --> A
    E -->|No| G[Done]
    C -->|Rate limit hit| H[Exponential backoff]
    H --> C
```

Outer loop — selects the next uncompleted task from a structured backlog file (for example, `TODO.md`), runs the agent to completion, commits results, then restarts with a clean context window. A safety limit (for example, `MAX_ITERATIONS=50`) prevents runaway execution. [Source: [nibzard/awesome-agentic-patterns](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/continuous-autonomous-task-loop-pattern.md)]

Inner loop — the ReAct cycle: the model reasons about the task (Thought), calls tools (Action), reads results (Observation), and repeats until the task is complete or the model emits a final message with no pending tool calls. Context grows within a single inner turn. The outer loop's context reset stops this accumulation from persisting across tasks. [Source: [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)]

Fresh context per task — each outer iteration starts a clean session. This removes [context rot](../context-engineering/context-window-dumb-zone.md): the reasoning-quality degradation that appears as context fills. Starting fresh stops a failed or noisy earlier task from coloring later ones. [Source: [Loop Strategy Spectrum](../loop-engineering/loop-strategy-spectrum.md)]

Rate-limit handling — when the agent hits an API rate limit, the loop waits using exponential backoff (configurable; a common default is 300 seconds) and resumes automatically. No human intervention required. [Source: [nibzard/awesome-agentic-patterns](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/continuous-autonomous-task-loop-pattern.md)]

Git automation — a post-task safety net commits changes after each task completes. Whether the agent committed or not, the safety net guarantees a clean commit history per task. This is the same [post-loop safety-net](../loop-engineering/agent-loop-middleware.md) pattern used in other harness designs. [Source: [Agent Loop Middleware](../loop-engineering/agent-loop-middleware.md)]

Anthropic's two-agent harness independently validates the same structure: an initializer agent populates a feature list; the coding agent runs one item per session, commits, updates the progress file, and stops — letting the outer loop restart with fresh context. [Source: [Anthropic: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)]

Linear's Loops feature applies the pattern inside a work tracker. It runs recurring agent workflows for bug triage, request routing, and documentation updates. Each run stays visible to the humans who own the work. [Source: [Linear: Introducing Loops](https://linear.app/now/introducing-loops)]

## Backlog design

Task backlog quality determines whether the loop succeeds. Tasks must be:

- Discrete — completable in a single agent session without external dependencies
- Atomic — one well-defined outcome, not a cluster of related changes
- Unambiguous — no interpretation required; the agent selects tasks autonomously

Ambiguous tasks make the agent guess. Those guesses compound silently across iterations — no human is watching each one. A task like "improve the auth module" is unsuitable; "add rate limiting to `/api/login` endpoint matching the existing middleware pattern in `src/middleware/rate-limit.ts`" is not.

The backlog file also carries state across sessions. Each iteration marks its task complete before the context is cleared, so the next iteration sees an accurate picture of remaining work.

## Trade-offs

| Factor | Continuous task loop | Alternative |
|--------|---------------------|-------------|
| Human oversight | Low — the loop runs unattended | High — [issue-to-PR pipeline](issue-to-pr-delegation-pipeline.md) has human triggers per task |
| Throughput | High — no inter-task idle time | Lower — each task requires a human handoff |
| Scope | Well-defined, discrete backlogs | Exploratory or high-judgment work |
| Error surface | Compounding across tasks if backlog is ambiguous | Isolated — one task fails, human resets |
| Horizontal scaling | Sequential only | [Parallel sessions](parallel-agent-sessions.md) add concurrency |

This pattern trades oversight for momentum. It is not appropriate for exploratory work, architectural decisions, or any task where mid-stream human judgment would change the direction. [Source: [nibzard/awesome-agentic-patterns](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/continuous-autonomous-task-loop-pattern.md)]

## Required guardrails

- Iteration cap — set `MAX_ITERATIONS` before starting. Without it, a backlog that never empties (because tasks keep failing and resetting) will run indefinitely.
- Token-budget cap — set an unattended spend ceiling per run. A 50-iteration loop on a medium codebase routinely consumes \$50–\$100+ in API credits, and stuck loops burn that budget on failed attempts; one 2026 incident saw an unattended scaling agent generate a \$60k/month cluster bill. [Source: [Autonomous Coding Agents: The Real 2026 Guide](https://www.agentik-os.com/blog/autonomous-coding-agents-complete-guide)]
- Version control per task — one commit per completed task provides rollback points. Without this, a bad task leaves the repository in an unknown state.
- Validate with a small batch first — run 3–5 tasks manually before enabling unattended mode. Catch backlog design failures before they replicate across 50 iterations.
- Execution monitoring — stream JSON output or log iteration counts so you can spot unexpected behavior without watching every step.

### Structural-coherence and sycophancy risks

Two failure modes do not surface in the per-task commit log and only appear after many iterations:

- Architectural drift from fresh context — each iteration starts blind to prior structural decisions. GitClear's 2025 analysis of 211 million lines of AI-assisted code found copy-pasted code rose from 8.3% to 12.3% of changes while refactoring dropped from 25% to under 10% — a pattern that compounds in fresh-context loops, where every iteration sees only the local task and not the architecture it implies. Mitigate with an explicit architecture-anchor file (for example, `ARCHITECTURE.md`) read on every iteration, and periodic human review for structural coherence. [Source: [The Ralph Wiggum Loop: Autonomous Code Generation with a Fresh Context (codecentric, 2026)](https://www.codecentric.de/en/knowledge-hub/blog/the-ralph-wiggum-loop-autonomous-code-generation-with-a-fresh-context)]
- Sycophancy or "overbaking" loops — autonomous loops can enter a please-the-user spiral in which the agent rewrites working code to chase a vague success signal, degrading the codebase rather than improving it. The backlog-design rules above (atomic, unambiguous tasks) are the primary defense; a verifying test suite or explicit acceptance criterion per task closes the loop. [Source: [Agentic Design Patterns Catalog 2026 — Augment Code](https://www.augmentcode.com/guides/agentic-design-patterns)]

## Permissions consideration

Unattended execution at this scale usually requires elevated agent permissions. In Claude Code, the `--dangerously-skip-permissions` flag bypasses interactive prompts to allow fully headless operation. Review your tool's permission model before enabling unattended mode — the blast radius of an ambiguous task grows in step with the permissions you grant. [Source: [nibzard/awesome-agentic-patterns](https://github.com/nibzard/awesome-agentic-patterns/blob/main/patterns/continuous-autonomous-task-loop-pattern.md)]

## Example

A bash wrapper implementing the outer loop over a `TODO.md` backlog:

```bash
#!/usr/bin/env bash
# continuous-loop.sh — runs until backlog is empty or MAX_ITERATIONS reached

TASK_FILE="TODO.md"
MAX_ITERATIONS=50
RATE_LIMIT_BACKOFF=300
ITERATION=0

while [[ $ITERATION -lt $MAX_ITERATIONS ]]; do
  remaining=$(grep -c "^- \[ \]" "$TASK_FILE" 2>/dev/null || echo 0)

  if [[ "$remaining" -eq 0 ]]; then
    echo "Backlog empty. Done."
    exit 0
  fi

  echo "=== Iteration $((ITERATION + 1)) / $MAX_ITERATIONS ==="

  # Run agent with fresh context; capture exit code
  claude --no-cache --print \
    "Read $TASK_FILE. Select the next unchecked task. Complete it. \
     Mark it done in $TASK_FILE. Commit all changes with a descriptive message. Stop."
  EXIT_CODE=$?

  if [[ $EXIT_CODE -ne 0 ]]; then
    echo "Agent exited with code $EXIT_CODE. Waiting ${RATE_LIMIT_BACKOFF}s before retry..."
    sleep "$RATE_LIMIT_BACKOFF"
    continue
  fi

  ITERATION=$((ITERATION + 1))
done

echo "Max iterations reached." && exit 1
```

The `--no-cache` flag gives a genuinely clean context each cycle. Non-zero exit codes (including rate-limit responses) trigger a configurable backoff before the next iteration. The task file serves as both backlog and state: checked items persist across restarts.

## Key Takeaways

- The pattern nests a ReAct inner loop inside an outer task loop; fresh context per outer iteration prevents context rot from accumulating across tasks
- Backlog quality is the primary lever — discrete, atomic, unambiguous tasks are a prerequisite for autonomous selection to work
- Rate-limit handling and git safety nets remove the two most common sources of manual interruption in long-running unattended loops
- This is sequential execution; combine with [parallel agent sessions](parallel-agent-sessions.md) to add horizontal throughput
- Guardrails (iteration cap, per-task commits, small-batch validation) are structural requirements, not optional enhancements

## Related

- [The Ralph Wiggum Loop](../loop-engineering/ralph-wiggum-loop.md) — the foundational fresh-context loop pattern this workflow extends
- [Loop Strategy Spectrum](../loop-engineering/loop-strategy-spectrum.md) — when to use fresh-context vs accumulated-context vs compression strategies
- [Agent Loop Middleware](../loop-engineering/agent-loop-middleware.md) — post-loop safety nets and pre-call injection patterns
- [Issue-to-PR Delegation Pipeline](issue-to-pr-delegation-pipeline.md) — human-triggered per-task delegation; the supervised alternative
- [Parallel Agent Sessions](parallel-agent-sessions.md) — horizontal scaling via simultaneous sessions; complements this pattern's sequential execution
- [Backlog Triage as a Named Agent Skill](backlog-triage-skill.md) — the upstream skill that produces the atomic, unambiguous tasks this loop requires
- [The Plan-First Loop](plan-first-loop.md) — the design-before-code variant for non-trivial tasks where this pattern's mechanical execution is unsafe
- [Continuous AI: A Navigation Map of Always-On Agent Workflows](continuous-ai.md) — the parent map of the continuous-* and triage families this loop belongs to
