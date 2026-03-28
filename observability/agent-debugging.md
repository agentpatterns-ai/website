---
title: "Agent Debugging: Diagnosing and Fixing Bad Agent Output"
description: "A systematic process for tracing why an agent produced wrong, incomplete, or unexpected output. Code bugs have stack traces. Agent bugs have context windows"
tags:
  - workflows
  - agent-design
  - instructions
aliases:
  - agent troubleshooting
  - LLM debugging
---

# Agent Debugging: Diagnosing Bad Agent Output

> A systematic process for tracing why an agent produced wrong, incomplete, or unexpected output.

## Why Agent Debugging Is Different

Code bugs have stack traces. Agent bugs have context windows. When an agent fails, the problem is usually not the model — it’s what the model was given to work with. The four failure modes are:

1. **Missing context** — the agent didn’t have information it needed
2. **Conflicting instructions** — two directives contradicted each other
3. **Missing or blocked tools** — the agent couldn’t take the action required
4. **Capability ceiling** — the task exceeded the model tier’s capability

Debugging means determining which category applies before changing anything.

## Diagnostic Sequence

### Step 1: What Did the Agent Actually See?

**Check which instructions loaded.** In Claude Code, run [`/memory`](https://code.claude.com/docs/en/memory#view-and-edit-with-memory) to list every CLAUDE.md and rules file in the session.

**Check which skills were available.** Skills only load when invoked or deemed relevant. If the agent missed a domain-specific workflow, the relevant skill may not have loaded.

**Check context usage.** When the context window fills, earlier instructions are dropped. An agent that followed rules early may stop later — not because it ignored them but because they fell out of the active window. [unverified: context window sizes and falloff behavior vary by model and implementation]

### Step 2: What Was the Agent Told?

Check for instruction conflicts:

- **Layer conflicts** — project-level, user-level, and managed policy CLAUDE.md files. More specific takes precedence ([Claude Code resolution order](https://code.claude.com/docs/en/memory#how-claudemd-files-load)), but [same-level contradictions may resolve arbitrarily](https://code.claude.com/docs/en/memory#write-effective-instructions).
- **Vague instructions** — "format code properly" is interpreted differently across runs. Specific, verifiable instructions ("use 2-space indentation") are more stable.
- **Stale instructions** — conventions overwritten in practice but not in the file.

Use [`/memory`](https://code.claude.com/docs/en/memory#view-and-edit-with-memory) to open instruction files and scan for contradictions.

### Step 3: What Could the Agent Do?

Check:

- Which tools were enabled vs. blocked in the session
- Whether any tool calls failed silently — the agent may have pivoted to a workaround
- Whether the agent needed a tool it never had (e.g., web search, a specific CLI)

In Claude Code, [tool permissions are configured in `.claude/settings.json`](https://code.claude.com/docs/en/settings). The session transcript shows which tools were attempted and whether they succeeded [unverified — transcript access for debugging is not discussed in the settings documentation].

### Step 4: Was the Model Right for the Task?

Some failures are capability problems, not context problems. A smaller model produces confidently wrong output on complex reasoning tasks. If context, instructions, and tools look right but output is still wrong, test with a more capable model tier.

## Transcript Analysis

Claude Code stores session transcripts under `~/.claude/projects/<project>/sessions/` [unverified — path inferred from observed behavior; not documented]. Each file is a JSON log of every tool call, result, and message in order.

Use the transcript to trace: what the agent did first, when behavior diverged, whether tool failures caused a pivot, and whether the agent flagged a missing resource.

The [troubleshooting documentation](https://code.claude.com/docs/en/troubleshooting) recommends `/doctor` to surface environment issues (malformed config, MCP server errors, oversized instruction files) not visible during normal operation.

## Reproducing the Issue

1. Start a fresh session (no accumulated context)
2. Provide exactly the same inputs
3. Observe whether the same bad output recurs

If it recurs, the problem is structural — instructions, skills, or tool configuration. If not, it was session-specific — context drift, context overflow, or transient state.

## Common Failure Patterns

| Symptom | Most Likely Cause |
|---|---|
| Agent ignores a rule it followed earlier | Context overflow — rule dropped from window |
| Agent produces confident but incorrect output | Conflicting instructions, or capability ceiling |
| Agent takes a longer path than necessary | Missing tool access — agent worked around a gap |
| Agent behavior varies across sessions | Missing or inconsistently loaded instruction files |
| Agent follows instructions in testing, not in production | Different instruction file scope (user vs. project vs. managed) |

## Example

An agent consistently generates test files with the wrong naming convention (`*.spec.ts` instead of `*.test.ts`). Fix attempts don’t stick.

**Step 1 — Check what it saw:** Run `/memory`. The project CLAUDE.md lists `*.test.ts`, but a user-level CLAUDE.md (from `~/.claude/`) has a stale entry specifying `*.spec.ts`. Both are loaded.

**Step 2 — Check what it was told:** The two instructions conflict across scopes. Project-level takes precedence, but the user-level entry is creating noise. Remove the stale entry from `~/.claude/CLAUDE.md`.

**Step 3 — Reproduce:** Fresh session, same task. The agent now produces `*.test.ts` files consistently.

Root cause: stale user-level instruction conflicting with project convention. Fix: remove the outdated entry, not the model or prompt.

## Related

- [Trajectory Logging via Progress Files](trajectory-logging-progress-files.md)
- [Loop Detection](loop-detection.md)
- [Making Observability Legible to Agents](observability-legible-to-agents.md)
- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md)
- [OpenTelemetry for AI Agent Observability and Tracing](../standards/opentelemetry-agent-observability.md)
- [Repository Bootstrap Checklist](../workflows/repository-bootstrap-checklist.md)
- [Escape Hatches: Unsticking Stuck Agents](../workflows/escape-hatches.md)
- [Continuous Agent Improvement](../workflows/continuous-agent-improvement.md)
- [Circuit Breakers](circuit-breakers.md)
- [Event Sourcing for Agents](event-sourcing-for-agents.md)
- [Visible Thinking in AI Development](visible-thinking-ai-development.md)
- [Using the Agent to Analyze Its Own Evaluation Transcripts](../verification/agent-transcript-analysis.md)
