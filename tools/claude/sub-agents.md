---
title: "Claude Code Sub-Agents for Delegating Complex Tasks"
description: "Sub-agents are ephemeral, isolated agents that execute focused tasks and return results to a parent agent in Claude Code."
aliases:
  - child agents
  - delegated agents
tags:
  - agent-design
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-05-27
status: current
---

# Claude Code Sub-Agents

> Ephemeral, isolated agents that execute focused tasks and return results to the parent.

Learn it hands-on with the [Sub-Agents & Orchestration](https://learn.agentpatterns.ai/harness-engineering/sub-agents-and-orchestration/) guided lesson, which includes quizzes.

## How they work

You define a [sub-agent](https://code.claude.com/docs/en/sub-agents) as a Markdown file with YAML frontmatter. Put it in `.claude/agents/` for project scope or `~/.claude/agents/` for user scope. Each sub-agent runs in its own fresh context window. Only the final result returns to the parent. The parent never sees the sub-agent's intermediate reasoning or tool calls.

## Definition format

```yaml
---
name: reviewer
description: Reviews code changes for quality issues
tools:
  - Read
  - Grep
  - Glob
model: sonnet
---

Review the provided code changes for...
```

The frontmatter fields are `name`, `description`, `tools` (restrict which tools are available), and `model` (route to a specific Claude model, for example `opus`, `sonnet`, or `haiku`). Only `name` and `description` are required. The rest are optional.

## Agent tool `model` parameter

The `Agent` tool accepts a `model` parameter to select a model per invocation, for example `model: opus`, `model: sonnet`, or `model: haiku`. The parent can route an individual sub-agent invocation to a specific model regardless of the default.

The `model` field in the sub-agent definition sets the default. The per-invocation parameter overrides it. The tool accepts both `model` aliases (`sonnet`, `opus`, `haiku`) and full model IDs, for example `claude-opus-4-6`.

## Properties

Sub-agents give you:

- context isolation: each sub-agent only sees what it needs
- parallelization: multiple sub-agents run concurrently
- error isolation: each sub-agent's failure stays within its own context, so a failed sub-agent does not cancel sibling sub-agents running in parallel
- specialized instructions: a system prompt tailored to each agent
- tool restrictions: limit access to reduce unintended actions
- worktree isolation: an optional `isolation: "worktree"` setting for filesystem-level isolation, described in [Worktree Isolation](../../workflows/worktree-isolation.md)

## SDK sub-agents

The [Agent SDK](https://platform.claude.com/docs/en/agent-sdk/subagents) supports programmatic sub-agents defined inline through the `agents` option, with no filesystem dependency. Claude spawns them through the `Agent` tool.

## When to use

Use sub-agents for quick, focused tasks that report back: code review, research, file search, and test execution. When a task needs agents to coordinate, use [agent teams](agent-teams.md) instead.

## Example

A parent agent delegates a focused code-review task to a sub-agent defined in `.claude/agents/reviewer.md`:

```markdown
---
name: reviewer
description: Reviews a single file for correctness and style issues
tools:
  - Read
  - Grep
  - Glob
model: sonnet
---

Read the file at the path provided by the caller. Check for:
1. Correctness — logic errors, off-by-one mistakes, unhandled edge cases
2. Style — naming conventions, dead code, overly complex expressions

Return a structured list of findings with line numbers.
```

The parent invokes this sub-agent via the `Agent` tool:

```
Agent(agent: "reviewer", prompt: "Review src/parser.ts for correctness and style issues.")
```

The sub-agent runs in its own context window with access only to `Read`, `Grep`, and `Glob`. The parent receives only the final findings, never the sub-agent's intermediate tool calls or reasoning.

## Why it works

Sub-agents stay isolated because each one runs in its own fresh context window. It sees only the content in its prompt: no inherited conversation history, no parent reasoning, no sibling tool outputs. The parent passes a scoped task description, and the sub-agent produces a focused result. This boundary is structural. The Claude Code runtime stops sub-agents from reading the parent context, and the parent receives only the final text response, not intermediate tool calls or reasoning traces. Parallelization follows from the same structure. Because sub-agents share nothing, several can run at once without coordination overhead.

## When this backfires

Sub-agents add overhead that outweighs the benefit for small tasks. When the work takes fewer tokens to finish than it takes to describe and delegate, a sub-agent is slower and more expensive than doing the work inline. Anthropic's research-system retrospective reports that [multi-agent systems use roughly 15× more tokens than a single-thread chat](https://www.anthropic.com/engineering/built-multi-agent-research-system), so the value of the delegated task has to justify that cost.

Debugging is harder because the parent only sees the final result. If a sub-agent quietly misunderstands the task or returns a wrong output, the parent cannot see the steps that led there. The isolation that prevents context pollution also prevents inspection.

Sub-agents cannot talk to each other. When a task needs agents to exchange partial results, coordinate decisions, or share state, [agent teams](agent-teams.md) are the right model. Sub-agents are for fire-and-forget delegation only.

## Key Takeaways

- Sub-agents run in isolated context — the parent only sees the final result
- Restrict tools and model per sub-agent for focused, cost-efficient execution — the `Agent` tool `model` parameter supports per-invocation routing that overrides the sub-agent definition's `model` field
- Use worktree isolation for filesystem-level separation in parallel workflows
- SDK sub-agents can be defined inline for programmatic use

## Related

- [Agent Teams](agent-teams.md)
- [Agent SDK](agent-sdk.md)
- [Batch and Worktrees](batch-worktrees.md)
- [Extension Points](extension-points.md) — where sub-agents sit among Claude Code's extension surfaces
- [Code Review](code-review.md) — common sub-agent use case for scoped review tasks
- [Hooks Lifecycle](hooks-lifecycle.md) — how sub-agent invocations interact with PreToolUse / PostToolUse / SessionStart events
- [Agent Composition Patterns](../../agent-design/agent-composition-patterns.md)
- [Orchestrator-Worker](../../multi-agent/orchestrator-worker.md)
