---
title: "Agent Debugging: Diagnosing Bad Agent Output"
term: "Agent Debugging"
description: "A systematic process for tracing why an AI coding agent produced wrong, incomplete, or unexpected output by inspecting context, instructions, tools, and model tier."
tags:
  - workflows
  - agent-design
  - instructions
  - tool-agnostic
  - observability
aliases:
  - agent troubleshooting
  - LLM debugging
last_reviewed: 2026-07-21
maturity: established
---

# Agent Debugging: Diagnosing Bad Agent Output

> A systematic process for tracing why an agent produced wrong, incomplete, or unexpected output.

## Why agent debugging is different

Code bugs have stack traces. Agent bugs have context windows. When an agent fails, the problem is usually not the model — it’s what the model was given. The four modes:

1. Missing context — the agent did not have information it needed
2. Conflicting instructions — two directives contradicted each other
3. Missing or blocked tools — the agent could not act
4. Capability ceiling — the task exceeded the model tier’s capability

Debugging means working out which category applies before changing anything.

LangChain's [introduction to coding-agent observability](https://blog.langchain.com/blog/your-coding-agents-are-a-black-box-heres-how-to-crack-them-open) frames an opaque agent as a black box to crack open through tracing and instrumentation.

## Diagnostic sequence

### Step 1: What the agent saw

Check which instructions loaded. In Claude Code, run [`/memory`](https://code.claude.com/docs/en/memory#view-and-edit-with-memory) to list every CLAUDE.md and rules file in the session.

Check which skills were available. Skills only load when invoked or judged relevant. If the agent missed a domain-specific workflow, the relevant skill may not have loaded.

Check context usage. When Claude Code compacts a long session, it drops path-scoped rules and nested CLAUDE.md files, reloading them only when a matching file is read again ([context window — what survives compaction](https://code.claude.com/docs/en/context-window#what-survives-compaction)). An agent that followed rules early may stop later because they fell out after compaction — not because the model ignored them.

### Step 2: What the agent was told

Check for instruction conflicts:

- Layer conflicts — project-level, user-level, and managed policy CLAUDE.md files. More specific takes precedence ([Claude Code resolution order](https://code.claude.com/docs/en/memory#how-claudemd-files-load)), but [same-level contradictions may resolve arbitrarily](https://code.claude.com/docs/en/memory#write-effective-instructions).
- Vague instructions — each run reads "format code properly" differently. Specific, verifiable instructions ("use 2-space indentation") hold up better.
- Stale instructions — conventions overwritten in practice but not in the file.

Use [`/memory`](https://code.claude.com/docs/en/memory#view-and-edit-with-memory) to open instruction files and scan for contradictions.

### Step 3: What the agent could do

Check:

- Which tools were enabled or blocked in the session
- Whether any tool calls failed silently — the agent may have pivoted to a workaround
- Whether the agent needed a tool it never had (for example, web search or a specific CLI)

In Claude Code, you [configure tool permissions in `.claude/settings.json`](https://code.claude.com/docs/en/settings). Review the session to see which tools the agent attempted and whether they succeeded.

### Step 4: Whether the model fit the task

Some failures are [capability problems, not context problems](../workflows/escape-hatches.md). A smaller model produces confidently wrong output on complex reasoning. If context, instructions, and tools look right but output is still wrong, retest with a more capable model tier.

## Transcript analysis

Claude Code stores session transcripts locally under `~/.claude/projects/` ([data retention — local caching](https://code.claude.com/docs/en/data-usage#data-retention)). Use the transcript to trace what the agent did first, when behavior diverged, whether tool failures caused a pivot, and whether it flagged a missing resource.

The [troubleshooting documentation](https://code.claude.com/docs/en/troubleshooting) recommends `/doctor` to surface environment issues (malformed config, MCP errors, oversized instruction files) not visible during normal operation.

## Reproducing the issue

1. Start a fresh session with no accumulated context.
2. Provide exactly the same inputs.
3. Watch whether the same bad output recurs.

If it recurs, the problem is structural — instructions, skills, or tool configuration. If not, it was session-specific — context drift, context overflow, or transient state.

## Common failure patterns

| Symptom | Most likely cause |
|---|---|
| Agent ignores a rule it followed earlier | Context overflow — rule dropped from window |
| Agent produces confident but incorrect output | Conflicting instructions, or capability ceiling |
| Agent takes a longer path than necessary | Missing tool access — agent worked around a gap |
| Agent behavior varies across sessions | Missing or inconsistently loaded instruction files |
| Agent follows instructions in testing, not in production | Different instruction file scope (user vs. project vs. managed) |

## Example

An agent consistently generates test files with the wrong naming convention (`*.spec.ts` instead of `*.test.ts`). Fix attempts do not stick.

Step 1 — Check what it saw: Run `/memory`. The project CLAUDE.md lists `*.test.ts`, but a user-level CLAUDE.md (from `~/.claude/`) has a stale entry specifying `*.spec.ts`. Both are loaded.

Step 2 — Check what it was told: The two instructions conflict across scopes. Project-level takes precedence, but the user-level entry is creating noise. Remove the stale entry from `~/.claude/CLAUDE.md`.

Step 3 — Reproduce: Fresh session, same task. The agent now produces `*.test.ts` files consistently.

Root cause: stale user-level instruction conflicting with project convention. Fix: remove the outdated entry, not the model or prompt.

## When this backfires

The diagnostic sequence assumes the failure is structural. Three conditions where it adds overhead rather than insight:

1. Transient errors — rate limits, network timeouts, and API hiccups produce one-off bad output. Running the full diagnostic sequence wastes time — a retry in a fresh session is faster.
2. Novel capability gaps — if the task genuinely exceeds any available model tier's capability, no amount of context or instruction tuning will fix it. Reaching Step 4 too late delays this conclusion.
3. Over-instrumented environments — dense instruction files with many CLAUDE.md layers make conflict scanning slow. In these setups, reducing instruction surface area helps more than per-failure diagnosis.

## Key Takeaways

- The four agent-failure modes are missing context, conflicting instructions, missing or blocked tools, and capability ceiling — classify before you change anything.
- Use `/memory` to inspect every CLAUDE.md and rules file that actually loaded; layered scopes (user vs. project vs. managed) cause silent contradictions.
- Claude Code's compaction drops path-scoped rules; rules that held early in a session may quietly fall out, so check session length before blaming the model.
- Reproduce in a fresh session with identical inputs to separate structural bugs (instructions, skills, tools) from session-specific drift.
- Skip the full diagnostic for transient errors, true capability gaps, or over-instrumented setups — retry, escalate the tier, or reduce instruction surface area instead.

## Related

- [Trajectory Logging via Progress Files](trajectory-logging-progress-files.md)
- [Loop Detection](loop-detection.md)
- [Making Observability Legible to Agents](observability-legible-to-agents.md)
- [Agent Observability: OTel, Cost Tracking, and Trajectory Logging](agent-observability-otel.md)
- [Agent-Reactive Bugs at the Model-Harness Boundary](agent-reactive-bugs.md)
- [Escape Hatches: Unsticking Stuck Agents](../workflows/escape-hatches.md)
- [Continuous Agent Improvement](../workflows/continuous-agent-improvement.md)
- [Visible Thinking in AI Development](../human/visible-thinking-ai-development.md)
- [Using the Agent to Analyze Its Own Evaluation Transcripts](../verification/agent-transcript-analysis.md)
