---
title: "Cross-Tool Subagent Comparison"
description: "Three terminal agents now ship subagents as a first-class primitive — side-by-side on definition format, context isolation, tool scoping, and composition."
term: "Cross-Tool Subagent Comparison"
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
aliases:
  - terminal agent subagent comparison
  - gemini cli subagents vs claude code
last_reviewed: 2026-08-18
maturity: adopted
---

# Cross-Tool Subagent Comparison

> Claude Code, Gemini CLI, and Copilot CLI each ship a subagent primitive with shared Markdown-plus-YAML syntax, but recursion depth, isolation, and tool scoping diverge.

[Gemini CLI v0.38.1 shipped subagents](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md) in April 2026, joining [Claude Code](https://code.claude.com/docs/en/sub-agents) and [GitHub Copilot CLI](https://github.blog/changelog/2025-10-28-github-copilot-cli-use-custom-agents-and-delegate-to-copilot-coding-agent/). All three use Markdown plus YAML frontmatter and route delegation through `description`. Gemini CLI blocks a subagent from spawning another. Claude Code raised its default subagent nesting depth to 3 in July 2026, and setting `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` restores the single-level cap ([Claude Code changelog #2.1.219](https://code.claude.com/docs/en/changelog#2-1-219)). The differences in isolation, tool scoping, and composition determine portability.

## The shared model

| | Claude Code | Gemini CLI | Copilot CLI |
|---|---|---|---|
| Project path | `.claude/agents/*.md` | `.gemini/agents/*.md` | `.github/agents/*.agent.md` |
| User path | `~/.claude/agents/*.md` | `~/.gemini/agents/*.md` | `~/.copilot/agents/*.agent.md` |
| Required frontmatter | `name`, `description` | `name`, `description` | `description` (name = filename) |
| Delegation signal | `description` match | `description` match | `description` + tool-surfaced |
| Explicit invocation | by name in prompt | `@agent-name` | `/agent <name>` |
| Recursion depth | 3 (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` restores 1) | 1 (guard even with wildcard tools) | not documented |

Sources: [Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents), [Claude Code changelog #2.1.219](https://code.claude.com/docs/en/changelog#2-1-219), [Gemini CLI subagents](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md), [Copilot CLI changelog](https://github.blog/changelog/2025-10-28-github-copilot-cli-use-custom-agents-and-delegate-to-copilot-coding-agent/).

Gemini CLI still blocks a subagent from spawning another, even when `tools: ['*']` is granted. Claude Code's Plan subagent was built for that same single-layer restriction. Copilot CLI's docs describe delegation to a subagent but state no depth limit in either direction, so treat its recursion behavior as unspecified rather than capped ([invoking custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/invoke-custom-agents)). Claude Code raised its default subagent nesting depth to 3 in July 2026 ([Claude Code changelog #2.1.219](https://code.claude.com/docs/en/changelog#2-1-219)). Setting `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` restores the one-level cap. Claude Code also removed its 200-subagent-per-session spawn cap ([Claude Code changelog #2.1.232](https://code.claude.com/docs/en/changelog#2-1-232)), so session-wide fan-out width is no longer capped either.

## Context isolation

Every subagent runs in its own context window. The parent receives only a summary.

- Claude Code — subagent starts in the parent's working directory, and `cd` does not leak back ([docs](https://code.claude.com/docs/en/sub-agents)). `isolation: worktree` gives the subagent a disposable git worktree, auto-cleaned if no changes land.
- Gemini CLI — separate context loop, separate system prompt, persona, tools, and MCP servers. The subagent "reports back to the main agent with its findings" ([docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md)).
- Copilot CLI — temporary subagent per invocation, torn down after it returns ([docs](https://github.blog/changelog/2025-10-28-github-copilot-cli-use-custom-agents-and-delegate-to-copilot-coding-agent/)).

Only Claude Code offers file-level isolation beyond context isolation.

## Tool scoping

Scoping diverges most.

Claude Code uses `tools` (allowlist) plus `disallowedTools` (denylist). Denylist resolves first, then allowlist ([docs](https://code.claude.com/docs/en/sub-agents)). Omitting both inherits all parent tools.

```yaml
tools: Read, Grep, Glob, Bash     # allowlist
disallowedTools: Write, Edit      # denylist (inherits everything else)
```

Gemini CLI uses a single `tools` array with wildcard syntax ([docs](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md)):

```yaml
tools:
  - "*"                          # all built-in and discovered tools
  - "mcp_*"                      # all tools from all MCP servers
  - "mcp_my-server_*"            # all tools from one server
  - read_file                    # explicit named tool
```

Omitting `tools` inherits every tool from the parent session.

Copilot CLI uses a single `tools` array — `["*"]` for all, or explicit tool names and MCP tool paths ([docs](https://github.com/github/copilot-cli-for-beginners/blob/main/04-agents-custom-instructions/README.md)). MCP servers declare inline with command, args, env, and secret bindings.

```yaml
tools: ['read', 'edit', 'search', 'custom-mcp/tool-1']
mcp-servers:
  custom-mcp:
    type: local
    command: some-command
    env:
      API_KEY: ${{ secrets.COPILOT_MCP_ENV_VAR_VALUE }}
```

All three allow scoping MCP servers to a single subagent, keeping server tool descriptions out of the parent context. Claude Code alone supports `skills:` preloading ([docs](https://code.claude.com/docs/en/sub-agents)). The field injects full skill content into the subagent at startup, and subagents do not inherit skills from the parent.

## Composition and delegation

All three tools delegate through the `description`. The parent reads each subagent's `description` and routes matching tasks.

```mermaid
graph TD
    P[Parent Agent] -->|reads description| R{Route}
    R -->|matches| SA[Subagent]
    SA -->|summary| P
    SA -.->|cannot spawn| SB[another subagent]
```

Each tool adds a distinct primitive for deeper composition past the recursion cap: Claude Code [agent teams](https://code.claude.com/docs/en/agent-teams) (persistent coordinated agents across sessions), Copilot CLI `/fleet` (same task fanned across parallel subagents with convergence), Gemini CLI [remote subagents over A2A](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md) (delegation to processes outside the local CLI).

## Portability implications

The common surface — `name`, `description`, `tools`, body-as-system-prompt — is large enough that a straight file copy between tools mostly works for simple research subagents. It breaks on tool-specific fields:

- Claude: `isolation`, `permissionMode`, `hooks`, `memory`, `skills`, `disallowedTools`, `effort`
- Gemini: `kind: remote`, `temperature`, `max_turns`, `timeout_mins`, and wildcard tool syntax
- Copilot: inline `mcp-servers` with GitHub secrets binding

Standardizing on one tool makes this moot. The comparison matters when Copilot in the IDE, Claude Code or Gemini CLI in the terminal, and a coding agent in CI all reach the same repo. Portable: body, `description`, a shared-vocabulary tool list. Tool-specific: everything else.

Per-tool detail: [Claude Code Sub-Agents](../../tools/claude/sub-agents.md), [Copilot Custom Agents](../../tools/copilot/custom-agents-skills.md), [Gemini CLI Subagents](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md).

## When not to reach for a subagent

Skip the subagent when:

- Task is small and low-context — spawning adds more latency than it saves when exploration would not have polluted the parent
- Subtasks are interdependent — when B needs A's output, fan-out collapses into two sequential phases and boundary cost dominates
- Descriptions are vague — all three tools route on `description` matching, so unclear descriptions produce unused or misrouted subagents

A single-threaded main agent with disciplined [context engineering](../../context-engineering/context-engineering.md) is often the better default. [Cognition's "Don't Build Multi-Agents"](https://cognition.ai/blog/dont-build-multi-agents) argues every handoff is lossy and synthesis across subagents confidently reconciles inconsistent views. The converged primitive is useful when isolation is the binding constraint — not by default.

## Key Takeaways

- All three terminal agents ship Markdown + YAML frontmatter subagents with `name`/`description` delegation; Gemini CLI still blocks nested subagents, Copilot CLI documents no depth limit either way, and Claude Code's default rose to 3 in July 2026
- Isolation semantics are shared (separate context window, summary return); only Claude Code offers file-level isolation via `isolation: worktree`
- Tool scoping diverges: Claude uses allowlist+denylist, Gemini uses wildcards, Copilot uses explicit lists with inline MCP
- Composition beyond one level requires distinct primitives in each tool: Claude agent teams, Copilot `/fleet`, Gemini A2A remote subagents
- Body, description, and a shared tool list are portable across tools; `isolation`, `permissionMode`, `temperature`, `timeout_mins`, and MCP binding are not

## Related

- [Sub-Agents for Fan-Out Research and Context Isolation](sub-agents-fan-out.md)
- [Orchestrator-Worker Pattern](orchestrator-worker.md)
- [Subagent Schema-Level Tool Filtering](subagent-schema-level-tool-filtering.md)
- [Claude Code Sub-Agents](../../tools/claude/sub-agents.md)
- [Claude Code Agent Teams](../../tools/claude/agent-teams.md)
- [Copilot Custom Agents and Skills](../../tools/copilot/custom-agents-skills.md)
- [Cross-Tool Translation](../../human/cross-tool-translation.md)
