---
title: "Claude Code Sub-Agents for Delegating Complex Tasks"
description: "Sub-agents are ephemeral, isolated agents that execute focused tasks and return results to a parent agent in Claude Code."
aliases:
  - child agents
  - delegated agents
tags:
  - agent-design
  - claude
---

# Claude Code Sub-Agents

> Ephemeral, isolated agents that execute focused tasks and return results to the parent.

## How They Work

[Sub-agents](https://code.claude.com/docs/en/sub-agents) are defined as Markdown files with YAML frontmatter in `.claude/agents/` (project scope) or `~/.claude/agents/` (user scope). Each sub-agent runs in its own fresh context window. Only the final result returns to the parent — the parent never sees the sub-agent's intermediate reasoning or tool calls.

## Definition Format

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

Key frontmatter fields: `name`, `description`, `tools` (restrict which tools are available), `model` (route to a specific Claude model — e.g. `opus`, `sonnet`, `haiku`). Set `disable-model-invocation: true` to prevent Claude from auto-invoking the sub-agent [unverified — not found in official sub-agents docs].

## Agent Tool `model` Parameter

The `Agent` tool accepts a `model` parameter for per-invocation model selection (e.g. `model: opus`, `model: sonnet`, `model: haiku`). This allows the parent to route individual sub-agent invocations to a specific model regardless of the default.

This parameter was temporarily removed and restored in v2.1.72 [unverified]. Prior to the fix, sub-agents on Bedrock, Vertex, and Foundry that specified a model were silently downgraded to older model versions — this is now resolved [unverified].

## Properties

- **Context isolation**: each sub-agent only sees what it needs
- **Parallelization**: multiple sub-agents run concurrently
- **Error isolation**: parallel `Read`, `WebFetch`, and `Glob` calls isolate failures — a failed call no longer cancels sibling calls running in parallel; only `Bash` errors still cascade (as of v2.1.72) [unverified]
- **Specialized instructions**: tailored system prompts per agent
- **Tool restrictions**: limit access to reduce unintended actions
- **Worktree isolation**: optional `isolation: "worktree"` for filesystem-level isolation

## SDK Sub-Agents

The [Agent SDK](https://platform.claude.com/docs/en/agent-sdk/subagents) supports programmatic sub-agents defined inline via the `agents` option — no filesystem dependency needed. Claude spawns them via the `Agent` tool.

## When to Use

Use sub-agents for quick, focused tasks that report back: code review, research, file search, test execution. For tasks requiring coordination between agents, consider [agent teams](agent-teams.md) instead.

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

The sub-agent runs in its own context window with access only to `Read`, `Grep`, and `Glob`. The parent receives only the final findings — never the sub-agent's intermediate tool calls or reasoning.

## Key Takeaways

- Sub-agents run in isolated context — the parent only sees the final result
- Restrict tools and model per sub-agent for focused, cost-efficient execution — the Agent tool `model` parameter supports per-invocation routing (restored in v2.1.72)
- Use worktree isolation for filesystem-level separation in parallel workflows
- SDK sub-agents can be defined inline for programmatic use

## Unverified Claims

- `disable-model-invocation: true` prevents Claude from auto-invoking the sub-agent [unverified — not found in official sub-agents docs]

## Related

- [Agent Teams](agent-teams.md)
- [Agent SDK](agent-sdk.md)
- [Batch and Worktrees](batch-worktrees.md)
- [Agent Composition Patterns](../../agent-design/agent-composition-patterns.md)
- [Orchestrator-Worker](../../multi-agent/orchestrator-worker.md)
