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

Custom commands in Claude Code inherit the session's full tool permissions. A `/review-pr` command that only reads files and runs `git diff` still has implicit access to `Write`, delete, and arbitrary shell — fine for code you wrote yourself, a problem once you share it with a team or run it somewhere unfamiliar.

The `allowed-tools` frontmatter field "grants permission for the listed tools during the turn that invokes the skill". The docs are explicit about the limit: "It does not restrict which tools are available: every tool remains callable" ([Claude Code skills documentation](https://code.claude.com/docs/en/skills)). The grant clears when you send your next message.

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

Claude can read files, search with Grep and Glob, and run `git diff` and `git log` variants without prompting. Unlisted tools — `Write`, `Edit`, arbitrary `Bash` — still need the same explicit user approval as any tool in a session without an allowlist.

The `Bash(git diff *)` syntax scopes `Bash` to commands starting with that prefix. The [Claude Code permissions model](https://code.claude.com/docs/en/permissions) supports full tool names and prefix-scoped wildcards.

Claude Code applies the same subcommand granularity to its own auto-generated rules: approving a compound command with "Yes, don't ask again" saves one rule per subcommand — up to 5 for one compound command, not a single rule for the whole string ([Claude Code permissions docs](https://code.claude.com/docs/en/permissions)).

## What to include in the allowlist

Design the allowlist around the smallest set of tools the command needs:

| Command type | Typical allowlist |
|---|---|
| Code review | `Read, Grep, Glob, Bash(git diff *), Bash(git log *)` |
| Documentation generation | `Read, Glob, Write` |
| Dependency audit | `Read, Bash(npm list *), Bash(pip list *)` |
| Safe exploration | `Read, Grep, Glob` |

`Read, Grep, Glob` is a safe baseline for any command that only inspects code. Add `Bash` only for specific, named subcommands.

## Preventing automatic invocation of sensitive commands

By default Claude can invoke any skill it judges relevant. For commands with side effects, require explicit invocation instead. Set `disable-model-invocation: true`:

```yaml
---
name: generate-release-notes
description: Generate release notes from git history
disable-model-invocation: true
allowed-tools: Read, Bash(git log *), Bash(git tag *)
---
```

It now runs only when you type `/generate-release-notes`, and the [Claude Code documentation](https://code.claude.com/docs/en/skills) notes this also drops the skill description from Claude's active context. Pairing it with `allowed-tools` gives the most constrained command mode.

## Sharing commands with a team

Commands checked into `.claude/commands/` (or `.claude/skills/<name>/SKILL.md`) ship to everyone who clones the repo, and the `allowed-tools` declaration travels with them. Read that as a grant you inherit, not a default you can trust:

> Workspace trust doesn't gate this field. Claude Code applies a project skill's `allowed-tools` whenever you or Claude invoke the skill, including in a `-p` run in a folder you've never trusted. A skill can grant itself broad tool access, so review the `allowed-tools` of skills checked into a repository before you run Claude Code there.

([Claude Code skills documentation](https://code.claude.com/docs/en/skills))

A shared command removes the per-invocation prompt and adds a per-repository review, done once, before the first run, on somebody else's file.

## Layering with session-level permissions

Command-level `allowed-tools` works on top of session-level permissions, not instead of them. Claude Code evaluates permission rules in [deny, then ask, then allow order](https://code.claude.com/docs/en/permissions). If a tool is denied at any level, no other level can allow it — the field only narrows what runs without prompting; it cannot grant anything a session-level deny rule blocks.

A PreToolUse hook enforces this even more strictly: exiting with status code 2 blocks the call before permission rules run at all, holding even when the command's `allowed-tools` list would otherwise let it through without a prompt ([Claude Code permissions docs](https://code.claude.com/docs/en/permissions)).

## When this backfires

`allowed-tools` is a pre-approval mechanism, not a hard restriction. Three failure conditions to account for:

- Unlisted tools still run with one approval. If a prompt injection or rogue model call attempts `Write`, the user sees a single approval prompt — the same guard that exists without any `allowed-tools` declaration. The allowlist does not add a deny layer; it only removes the prompt for listed tools.
- Allowlists go stale. A command that gains new abilities (for example, a `/deploy` skill that now needs `WebFetch` to post status) prompts for unlisted tools until you update the allowlist, surprising teams that read "no prompt" as "expected behavior."
- A false sense of hard enforcement. `allowed-tools` cannot block a tool by itself. Three things can: a `disallowed-tools` entry in the same frontmatter, which lists "tools removed from Claude's available pool while this skill is active" ([skills documentation](https://code.claude.com/docs/en/skills)); a session-level deny rule; or a PreToolUse hook.

## Key Takeaways

- `allowed-tools` in command frontmatter pre-approves a named subset of tools — they run without prompting during that command's execution.
- Unlisted tools are not blocked; they require the same user approval as any tool in a session without an allowlist.
- The `Bash(prefix *)` syntax scopes bash access to specific subcommands rather than all shell execution.
- `disable-model-invocation: true` prevents Claude from triggering a command automatically — use this for any command with side effects, even conservative ones.
- Read the `allowed-tools` of any skill you did not write before running Claude Code in its repository. Workspace trust does not gate the field, and a skill can grant itself broad access.
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
