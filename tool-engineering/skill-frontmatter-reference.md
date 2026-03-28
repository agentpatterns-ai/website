---
title: "SKILL.md Frontmatter Reference: All Fields Explained"
description: "All SKILL.md frontmatter fields: invocation control, subagent delegation, tool restriction, hooks, and argument handling in Claude Code."
tags:
  - instructions
  - agent-design
aliases:
  - "skill configuration"
  - "SKILL.md headers"
---

# SKILL.md Frontmatter Reference

> SKILL.md frontmatter controls how a skill is discovered, invoked, and executed — each field governs one aspect of that lifecycle: invocation control, subagent delegation, tool restriction, lifecycle hooks, and argument handling.

!!! note "Also known as"
    Skill configuration, SKILL.md headers. See [Skill Authoring Patterns](skill-authoring-patterns.md) for authoring guidance; [Agent Skills Standard](../standards/agent-skills-standard.md) for the portable format.

Most fields are optional. The base Agent Skills standard defines only `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`; all other fields are Claude Code extensions.

## Field Reference

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | No | Directory name | Slash-command name; lowercase, numbers, hyphens; max 64 chars. |
| `description` | Recommended | First paragraph | What the skill does and when to use it. Drives automatic loading. |
| `argument-hint` | No | — | Hint in the `/` autocomplete menu, e.g. `[issue-number]`. |
| `disable-model-invocation` | No | `false` | `true` prevents Claude from triggering the skill; user-only. |
| `user-invocable` | No | `true` | `false` hides from `/` menu; Claude can still load automatically. |
| `allowed-tools` | No | — | Tools usable without per-use approval during skill execution. |
| `model` | No | `inherit` | Model override for skill execution. |
| `context` | No | — | `fork` runs skill in an isolated subagent. |
| `agent` | No | `general-purpose` | Subagent type when `context: fork`. |
| `hooks` | No | — | Lifecycle hooks scoped to this skill. |

## Invocation Control

| Configuration | User can invoke `/name` | Claude can invoke | In context |
|---|---|---|---|
| (default) | Yes | Yes | Yes |
| `disable-model-invocation: true` | Yes | No | No |
| `user-invocable: false` | No | Yes | Yes |

Use `disable-model-invocation: true` for side-effect workflows (deployments, commits) where you control timing. Use `user-invocable: false` for background knowledge (style guides, domain rules) Claude should load automatically.

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
---
```

```yaml
---
name: api-conventions
description: REST API design patterns for this codebase. Load automatically when writing API endpoints.
user-invocable: false
---
```

## allowed-tools

Tools that may run without per-use approval while this skill is active. Unlisted tools follow normal permission rules.

```yaml
---
name: safe-reader
description: Read and analyze files without making changes
allowed-tools: Read, Grep, Glob
---
```

Skills specifying `allowed-tools` or `hooks` require user approval before first use — the runtime treats them as elevated-permission requests ([Claude Code changelog, 2.1.19](https://code.claude.com/docs/en/changelog)).

The base Agent Skills standard marks `allowed-tools` as experimental; support varies across other implementations.

## model

Model to use when this skill is active. Accepts aliases (`sonnet`, `opus`, `haiku`), full model IDs, or `inherit` (default — matches the main conversation's model).

```yaml
---
name: quick-lookup
description: Fast keyword search across the codebase
model: haiku
---
```

## context and agent

`context: fork` runs the skill in an isolated subagent. The skill body becomes the task prompt; the agent type provides system prompt, tools, and permissions.

```yaml
---
name: deep-research
description: Research a topic thoroughly across the codebase
context: fork
agent: Explore
---

Research $ARGUMENTS:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

Built-in `agent` values:

| Agent | Model | Tools | Use for |
|-------|-------|-------|---------|
| `Explore` | Haiku | Read-only | Fast codebase search and analysis |
| `Plan` | Inherits | Read-only | Pre-planning research |
| `general-purpose` | Inherits | All tools | Complex multi-step tasks |

[Custom agents](../tools/copilot/custom-agents-skills.md) in `.claude/agents/` can also be referenced by name.

`context: fork` requires explicit task instructions in the skill body. Reference-only skills (style guides, API conventions) produce no output when forked.

## hooks

Lifecycle hooks scoped to this skill. Same format as `.claude/settings.json` hooks; all four types supported: `command`, `http`, `prompt`, `agent`.

Hooks are scoped to the skill's execution and cleaned up on exit. [unverified]

```yaml
---
name: secure-operations
description: Run operations with pre-flight security validation
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

With `context: fork`, `Stop` hooks convert to `SubagentStop` events at runtime ([Claude Code hooks docs](https://code.claude.com/docs/en/hooks)). Skills defining `hooks` require user approval before first use.

## argument-hint

Display-only hint shown in the `/` autocomplete menu. Does not affect parsing.

```yaml
---
name: fix-issue
description: Fix a GitHub issue
argument-hint: "[issue-number]"
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.
```

The value must be a string. YAML arrays or non-string types are coerced to strings ([Claude Code changelog, 2.1.51](https://code.claude.com/docs/en/changelog)).

## Arguments in Skill Body

Substitution variables available in the skill body:

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments as a single string |
| `$ARGUMENTS[N]` | Argument at 0-based index N |
| `$N` | Shorthand for `$ARGUMENTS[N]` |
| `${CLAUDE_SKILL_DIR}` | Directory containing the skill's `SKILL.md` |
| `${CLAUDE_SESSION_ID}` | Current session ID |

If `$ARGUMENTS` is not present in the skill body, arguments are appended as `ARGUMENTS: <value>`.

## Related

- [Skill Authoring Patterns](skill-authoring-patterns.md)
- [Skill Tool as Enforcement: Loading Command Prompts at Runtime](skill-tool-runtime-enforcement.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Hooks and Lifecycle Events: Intercepting Agent Behavior](hooks-lifecycle-events.md)
- [Progressive Disclosure for Agent Definitions](../agent-design/progressive-disclosure-agents.md)
- [On-Demand Skill Hooks](on-demand-skill-hooks.md)
- [Skill as Knowledge](skill-as-knowledge.md)
- [Skill Library Evolution](skill-library-evolution.md)
- [Permission-Gated Custom Commands](../security/permission-gated-commands.md)
