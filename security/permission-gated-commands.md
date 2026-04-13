---
title: "Permission-Gated Custom Commands for AI Agent Development"
description: "Pre-approve which tools a Claude Code slash command may use without prompting by declaring an allowed-tools list in its frontmatter — reducing interruptions while narrowing the expected surface"
aliases:
  - allowed-tools restriction
  - tool allowlisting for commands
tags:
  - instructions
  - agent-design
---

# Permission-Gated Custom Commands

> Pre-approve which tools a Claude Code slash command may use without prompting by declaring an `allowed-tools` list in its frontmatter — reducing interruptions while signaling the expected tool surface for shared commands.

## The Default Exposure Problem

Custom commands in Claude Code execute with the same tool permissions as the current session. A `/review-pr` command that only needs to read files and run `git diff` has implicit access to write files, delete, and run arbitrary shell commands. This is fine when you authored the command. It becomes a problem when sharing commands with a team or running one in an unfamiliar context.

[Claude Code skills documentation](https://code.claude.com/docs/en/skills) describes the `allowed-tools` frontmatter field as the mechanism for pre-approving specific tools and signaling the expected surface — reducing silent invocations of unintended tools.

## Declaring Allowed Tools

Skills (including commands in `.claude/commands/`) accept YAML frontmatter between `---` markers. The `allowed-tools` field takes a list of tool names Claude may use when the skill is active:

```yaml
---
name: review-pr
description: Review the current pull request for issues
allowed-tools: Read, Grep, Glob, Bash(git diff *), Bash(git log *)
---

Review the current pull request...
```

When this command runs, Claude can read files, search with Grep and Glob, and run `git diff` and `git log` variants without prompting. Unlisted tools — `Write`, `Edit`, arbitrary `Bash` — are not blocked: they still require explicit user approval, the same as any tool in a session without an allowlist. The field narrows the set of tools that run silently, not the set that can run at all.

The `Bash(git diff *)` syntax scopes `Bash` access to commands starting with that prefix. [Claude Code's permissions model](https://code.claude.com/docs/en/permissions) supports both full tool names (`Read`) and prefix-scoped tool access using wildcards (`Bash(git diff *)`).

## What to Include in the Allowlist

Design the allowlist around the minimum set of tools the command legitimately needs — this reduces approval prompts for routine tool use and communicates intent to teammates reading the command file:

| Command type | Typical allowlist |
|---|---|
| Code review | `Read, Grep, Glob, Bash(git diff *), Bash(git log *)` |
| Documentation generation | `Read, Glob, Write` |
| Dependency audit | `Read, Bash(npm list *), Bash(pip list *)` |
| Safe exploration | `Read, Grep, Glob` |

The read-only pattern (`Read, Grep, Glob`) is a useful baseline for any command that only needs to inspect code. Add `Bash` access only for specific, named subcommands.

## Preventing Automatic Invocation of Sensitive Commands

By default, Claude can invoke any skill automatically when it judges the skill relevant. For commands with side effects — even if their allowed-tools list is conservative — you may want Claude to require explicit invocation. Set `disable-model-invocation: true`:

```yaml
---
name: generate-release-notes
description: Generate release notes from git history
disable-model-invocation: true
allowed-tools: Read, Bash(git log *), Bash(git tag *)
---
```

This removes the command from Claude's automatic context. It only runs when you type `/generate-release-notes`. [Claude Code documentation](https://code.claude.com/docs/en/skills) notes this also removes the skill description from Claude's active context, so the combination of `disable-model-invocation` and `allowed-tools` produces the most constrained command mode.

## Sharing Commands with a Team

Commands checked into `.claude/commands/` (or `.claude/skills/<name>/SKILL.md`) are available to everyone who clones the repository. The `allowed-tools` declaration travels with the command file, so the team gets safe defaults without per-invocation review. The command author's intent is machine-readable, not just a comment in the Markdown.

## Layering with Session-Level Permissions

Command-level `allowed-tools` operates on top of session-level permissions, not instead of them. Claude Code evaluates permission rules in [deny, then ask, then allow order](https://code.claude.com/docs/en/permissions) — if a tool is denied at any level, no other level can allow it. The field narrows the set of tools that run without prompting during the command; it cannot grant access to tools blocked by session-level deny rules.

## When This Backfires

`allowed-tools` is a pre-approval mechanism, not a hard restriction. Three failure conditions to account for:

- **Unlisted tools still run with one approval.** If a prompt injection or rogue model call attempts `Write`, the user sees a single approval prompt — the same guard that exists without any `allowed-tools` declaration. The allowlist does not add a deny layer; it only removes the prompt for listed tools.
- **Allowlists go stale.** A command that gains new capabilities (e.g., a `/deploy` skill that now needs `WebFetch` to post status) will silently prompt for unlisted tools until the allowlist is updated. Teams relying on "no prompt = expected behavior" will be surprised.
- **False sense of hard enforcement.** Operators who assume `allowed-tools` blocks tools are wrong. For genuine tool blocking, use session-level deny rules in `settings.json` or a PreToolUse hook — both operate at a lower level than the skill allowlist and cannot be overridden by frontmatter.

## Key Takeaways

- `allowed-tools` in command frontmatter pre-approves a named subset of tools — they run without prompting during that command's execution.
- Unlisted tools are not blocked; they require the same user approval as any tool in a session without an allowlist.
- The `Bash(prefix *)` syntax scopes bash access to specific subcommands rather than all shell execution.
- `disable-model-invocation: true` prevents Claude from triggering a command automatically — use this for any command with side effects, even conservative ones.
- Commands with declared `allowed-tools` are safe to commit to version control and share across a team; the pre-approval intent travels with the file.
- Session-level deny rules take precedence over `allowed-tools`; the field narrows the no-prompt set but cannot expand session permissions.

## Related

- [Blast Radius Containment: Least Privilege for AI Agents](./blast-radius-containment.md)
- [Hooks vs Prompts](../verification/hooks-vs-prompts.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Protecting Sensitive Files](./protecting-sensitive-files.md)
- [System Prompt Altitude: Specific Without Being Brittle](../instructions/system-prompt-altitude.md)
- [SKILL.md Frontmatter Reference](../tool-engineering/skill-frontmatter-reference.md)
- [Defense-in-Depth Agent Safety](./defense-in-depth-agent-safety.md)
- [Task Scope as a Security Boundary](./task-scope-security-boundary.md)
- [Dual-Boundary Sandboxing](./dual-boundary-sandboxing.md)
- [Scoped Credentials via Proxy](./scoped-credentials-proxy.md)
- [Sandbox Rules for Harness-Owned Tools](./sandbox-rules-harness-tools.md)
- [Human-in-the-Loop Confirmation Gates](./human-in-the-loop-confirmation-gates.md)
- [Safe Outputs Pattern](./safe-outputs-pattern.md)
- [Tool Signing and Signature Verification](./tool-signing-verification.md)
- [Secrets Management for Agent Workflows](./secrets-management-for-agents.md)
- [Enterprise Agent Hardening](./enterprise-agent-hardening.md)
