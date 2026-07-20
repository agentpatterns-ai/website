---
title: "Permission-Gated Custom Commands for AI Agent Development"
term: "Permission-Gated Custom Commands"
description: "Declare an allowed-tools list in a Claude Code command's frontmatter to pre-approve specific tools, cutting prompts and signaling the expected surface."
aliases:
  - allowed-tools restriction
  - tool allowlisting for commands
tags:
  - instructions
  - agent-design
  - tool-agnostic
  - security
last_reviewed: 2026-06-12
maturity: established
---

# Permission-Gated Custom Commands

> Custom commands pre-approve specific tools through an `allowed-tools` frontmatter list, so listed tools run without prompting — signaling the expected surface, not blocking unlisted tools.

Related lesson: [Permissions and Safety Boundaries](https://learn.agentpatterns.ai/harness-engineering/permissions-and-safety-boundaries/) — this concept features in a hands-on lesson with quizzes.

## The default exposure problem

Custom commands in Claude Code inherit the session's full tool permissions. A `/review-pr` command that only reads files and runs `git diff` still has implicit access to `Write`, delete, and arbitrary shell. That is fine when you wrote it. It becomes a problem when you share it with a team or run it in an unfamiliar context.

The [Claude Code skills documentation](https://code.claude.com/docs/en/skills) describes the `allowed-tools` frontmatter field as the way to pre-approve specific tools, which cuts silent calls to unintended ones.

## Declaring allowed tools

Skills (including commands in `.claude/commands/`) accept YAML frontmatter between `---` markers. The `allowed-tools` field takes a list of tool names Claude may use when the skill is active:

```yaml
---
name: review-pr
description: Review the current pull request for issues
allowed-tools: Read, Grep, Glob, Bash(git diff *), Bash(git log *)
---

Review the current pull request...
```

When this command runs, Claude can read files, search with Grep and Glob, and run `git diff` and `git log` variants without prompting. Unlisted tools — `Write`, `Edit`, arbitrary `Bash` — are not blocked. They still need explicit user approval, the same as any tool in a session without an allowlist. The field narrows the set of tools that run silently, not the set that can run at all.

The `Bash(git diff *)` syntax scopes `Bash` access to commands that start with that prefix. The [Claude Code permissions model](https://code.claude.com/docs/en/permissions) supports both full tool names (`Read`) and prefix-scoped tool access through wildcards (`Bash(git diff *)`).

Claude Code applies the same subcommand-level granularity to its own auto-generated rules: approving a compound command with "Yes, don't ask again" saves a separate rule per subcommand — up to 5 rules for one compound command — rather than a single rule for the whole string ([Claude Code permissions docs](https://code.claude.com/docs/en/permissions)).

## What to include in the allowlist

Design the allowlist around the smallest set of tools the command needs. This cuts approval prompts for routine tool use and shows your intent to teammates reading the command file:

| Command type | Typical allowlist |
|---|---|
| Code review | `Read, Grep, Glob, Bash(git diff *), Bash(git log *)` |
| Documentation generation | `Read, Glob, Write` |
| Dependency audit | `Read, Bash(npm list *), Bash(pip list *)` |
| Safe exploration | `Read, Grep, Glob` |

The read-only pattern (`Read, Grep, Glob`) is a useful baseline for any command that only needs to inspect code. Add `Bash` access only for specific, named subcommands.

## Preventing automatic invocation of sensitive commands

By default, Claude can invoke any skill automatically when it judges the skill relevant. For commands with side effects — even when their allowed-tools list is small — you may want to require explicit invocation. Set `disable-model-invocation: true`:

```yaml
---
name: generate-release-notes
description: Generate release notes from git history
disable-model-invocation: true
allowed-tools: Read, Bash(git log *), Bash(git tag *)
---
```

This removes the command from Claude's automatic context. It runs only when you type `/generate-release-notes`. The [Claude Code documentation](https://code.claude.com/docs/en/skills) notes this also removes the skill description from Claude's active context, so pairing `disable-model-invocation` with `allowed-tools` produces the most constrained command mode.

## Sharing commands with a team

Commands checked into `.claude/commands/` (or `.claude/skills/<name>/SKILL.md`) ship to everyone who clones the repo. The `allowed-tools` declaration travels with the file, so the team gets safe defaults without per-invocation review. Author intent is machine-readable, not just a comment.

## Layering with session-level permissions

Command-level `allowed-tools` works on top of session-level permissions, not instead of them. Claude Code evaluates permission rules in [deny, then ask, then allow order](https://code.claude.com/docs/en/permissions). If a tool is denied at any level, no other level can allow it. The field narrows the set of tools that run without prompting during the command. It cannot grant access to tools blocked by session-level deny rules.

A PreToolUse hook enforces this even more strictly: a hook that exits with status code 2 blocks the tool call before permission rules are evaluated at all, so the block holds even when the command's `allowed-tools` list would otherwise let the call proceed without a prompt ([Claude Code permissions docs](https://code.claude.com/docs/en/permissions)).

## When this backfires

`allowed-tools` is a pre-approval mechanism, not a hard restriction. Account for three failure conditions:

- Unlisted tools still run with one approval. If a prompt injection or rogue model call attempts `Write`, the user sees a single approval prompt — the same guard that exists without any `allowed-tools` declaration. The allowlist does not add a deny layer; it only removes the prompt for listed tools.
- Allowlists go stale. A command that gains new abilities (for example, a `/deploy` skill that now needs `WebFetch` to post status) will prompt for unlisted tools until you update the allowlist. Teams that rely on "no prompt means expected behavior" will be surprised.
- A false sense of hard enforcement. Operators who assume `allowed-tools` blocks tools are wrong. To block a tool for real, use session-level deny rules in `settings.json` or a PreToolUse hook. Both work at a lower level than the skill allowlist and frontmatter cannot override them.

## Key Takeaways

- `allowed-tools` in command frontmatter pre-approves a named subset of tools — they run without prompting during that command's execution.
- Unlisted tools are not blocked; they require the same user approval as any tool in a session without an allowlist.
- The `Bash(prefix *)` syntax scopes bash access to specific subcommands rather than all shell execution.
- `disable-model-invocation: true` prevents Claude from triggering a command automatically — use this for any command with side effects, even conservative ones.
- Commands with declared `allowed-tools` are safe to commit to version control and share across a team; the pre-approval intent travels with the file.
- Session-level deny rules take precedence over `allowed-tools`; the field narrows the no-prompt set but cannot expand session permissions.

## Related

- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Transcript-Driven Permission Allowlist](transcript-driven-permission-allowlist.md)
- [Hooks vs Prompts](../instructions/hooks-vs-prompts.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Protecting Sensitive Files](protecting-sensitive-files.md)
- [Sandbox Rules for Harness-Owned Tools](sandbox-rules-harness-tools.md)
- [SKILL.md Frontmatter Reference](../tool-engineering/skill-frontmatter-reference.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
