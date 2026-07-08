---
title: "Hook Catalog for Claude Code Enforcement"
term: "Hook Catalog"
description: "A reference catalog of high-value Claude Code hooks grouped by purpose — CLI enforcement, destructive operation guardrails, sandboxing, and workflow automation."
tags:
  - agent-design
  - instructions
  - workflows
  - claude
  - tool-engineering
aliases:
  - Hook Examples & Recipes
  - Common Enforcement Patterns
  - Enforcing with Hooks
  - Hook Enforcement Patterns
last_reviewed: 2026-05-27
maturity: adopted
---

# Hook Catalog for Claude Code Enforcement

> Claude Code hooks are shell commands that intercept agent lifecycle events — blocking forbidden tool calls, enforcing CLI standards, and automating side effects — without relying on the model to follow instructions.

!!! note "Also known as"
    Hook Examples & Recipes, Common Enforcement Patterns, Enforcing with Hooks, Hook Enforcement Patterns.

## Why hooks

Models carry strong priors (`npm`, `git add -A`, `curl`) and revert under pressure. Hooks move enforcement out of the context window and into the shell.

| Approach | Reliability | Override risk |
|----------|------------|---------------|
| AGENTS.md instruction | Low | High — model may ignore under pressure |
| System prompt rule | Medium | Medium — multi-step tasks cause drift |
| `PreToolUse` hook | High | Low — bypass via tool-switching (see When this backfires) |

## How hooks work

[Claude Code hooks](https://code.claude.com/docs/en/hooks) run on agent lifecycle events. Claude Code passes JSON on stdin. Use `jq` to extract fields.

| Event | Fires when |
|-------|-----------|
| `PreToolUse` | Before any tool call — can block it |
| `PostToolUse` | After a tool call succeeds |
| `UserPromptSubmit` | When the user sends a message |
| `Stop` | When the agent finishes a turn |

A `permissionDecision` of `"deny"` blocks the tool call. Claude Code feeds the `permissionDecisionReason` back into the agent's context.

## CLI tool enforcement

Force project-mandated tools over training defaults.

Block npm, require bun:

```bash
#!/bin/bash
# .claude/hooks/enforce-bun.sh
COMMAND=$(jq -r '.tool_input.command')
if echo "$COMMAND" | grep -qE '^npm '; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "Use bun instead of npm"}}'
else
  exit 0
fi
```

```json
{
  "hooks": {
    "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": ".claude/hooks/enforce-bun.sh"}]}]
  }
}
```

Block python, require uv:

```bash
#!/bin/bash
# .claude/hooks/enforce-uv.sh
COMMAND=$(jq -r '.tool_input.command')
if echo "$COMMAND" | grep -qE '^python '; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "Use uv run instead of python"}}'
else
  exit 0
fi
```

## Destructive operation guardrails

Block hard-to-reverse commands.

Block `rm -rf`:

```bash
#!/bin/bash
# .claude/hooks/block-rm.sh
COMMAND=$(jq -r '.tool_input.command')
if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "rm -rf is blocked — move files to /tmp or use git clean"}}'
else
  exit 0
fi
```

Block `git reset --hard` and `git push --force`:

```bash
#!/bin/bash
# .claude/hooks/block-destructive-git.sh
COMMAND=$(jq -r '.tool_input.command')
if echo "$COMMAND" | grep -qE 'git reset --hard|git push --force|git push -f'; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "Destructive git command blocked — use --force-with-lease or open a PR"}}'
else
  exit 0
fi
```

Block direct push to main:

```bash
#!/bin/bash
# .claude/hooks/block-push-main.sh
COMMAND=$(jq -r '.tool_input.command')
if echo "$COMMAND" | grep -qE 'git push.*(main|master)'; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "Direct push to main is blocked — open a PR"}}'
else
  exit 0
fi
```

## Workflow automation

Run side effects automatically.

Auto-lint after file writes:

```json
{
  "hooks": {
    "PostToolUse": [{"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "bun run lint --fix"}]}]
  }
}
```

Log all prompts for audit:

```bash
#!/bin/bash
# .claude/hooks/log-prompts.sh
PROMPT=$(jq -r '.prompt')
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $PROMPT" >> ~/.claude/prompt-audit.log
```

```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": ".claude/hooks/log-prompts.sh"}]}]
  }
}
```

Desktop notification on agent completion:

```bash
#!/bin/bash
# .claude/hooks/notify-done.sh
# macOS — adapt for Linux (notify-send) or Windows (toast)
osascript -e 'display notification "Claude Code finished" with title "Done"'
```

```json
{
  "hooks": {
    "Stop": [{"hooks": [{"type": "command", "command": ".claude/hooks/notify-done.sh"}]}]
  }
}
```

## Sandboxing

Restrict reads or execs during sensitive operations.

Restrict Bash to a command allowlist:

```bash
#!/bin/bash
# .claude/hooks/allowlist-bash.sh
COMMAND=$(jq -r '.tool_input.command')
ALLOWED="^(bun|git|tsc|eslint|cat|ls|echo)"
if ! echo "$COMMAND" | grep -qE "$ALLOWED"; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "Command not in allowlist"}}'
else
  exit 0
fi
```

Block outbound network calls during agent sessions:

```bash
#!/bin/bash
# .claude/hooks/block-network.sh
COMMAND=$(jq -r '.tool_input.command')
if echo "$COMMAND" | grep -qE 'curl|wget|fetch'; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "Outbound network calls are blocked during agent sessions"}}'
else
  exit 0
fi
```

## Instruction auditing

Track which instruction files load — useful for config drift across teammates.

Log loaded instructions:

```bash
#!/bin/bash
# .claude/hooks/log-instructions.sh
INSTRUCTIONS=$(jq -r '.instructions // empty')
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Instructions loaded: $INSTRUCTIONS" >> ~/.claude/instructions-audit.log
```

```json
{
  "hooks": {
    "InstructionsLoaded": [{"hooks": [{"type": "command", "command": ".claude/hooks/log-instructions.sh"}]}]
  }
}
```

`InstructionsLoaded` fires when CLAUDE.md or `.claude/rules/*.md` load. The payload — `file_path`, `memory_type`, `load_reason`, `trigger_file_path` — is enough to audit per-session instruction loads ([docs](https://code.claude.com/docs/en/hooks)).

## Hook configuration and combining

Multiple handlers can fire per event/matcher. Hooks scope at three levels ([docs](https://code.claude.com/docs/en/hooks); [settings](https://code.claude.com/docs/en/settings)):

| Location | Scope | Shareable |
|----------|-------|-----------|
| `~/.claude/settings.json` | All projects | No |
| `.claude/settings.json` | Single project | Yes — commit to repo |
| `.claude/settings.local.json` | Single project | No — gitignored |

## When this backfires

- False positive blocking: over-broad regex matchers (matching `rm` instead of `rm -rf`) block legitimate commands. The model then exhausts retries or hallucinates workarounds. Validate patterns against real command logs.
- Silent failures: a hook that exits non-zero without a `permissionDecisionReason` gives the model no signal to adapt. Always emit a reason string.
- Exit code 1 fails open: for most hook events Claude Code treats only exit code `2` as a block. Exit code `1` is logged as a non-blocking error and the call proceeds. Developers who reach for the conventional Unix failure code ship guards that silently fail open ([hooks reference](https://code.claude.com/docs/en/hooks)).
- Tool-switching circumvention: hooks fire per tool match. Block `Edit`/`Write` and the model reaches for `Bash` + `sed`/`python -c`/heredoc; block `rm` and it falls back to `perl -e 'unlink(...)'`. Anchor outcome-layer harms in file permissions, network policy, or a sandbox, and pair tool hooks with a `Bash` matcher for the obvious bypasses ([issue #43189](https://github.com/anthropics/claude-code/issues/43189)).
- Exit-code-2 stop-instead-of-retry: a `PreToolUse` block with exit `2` is meant to feed `stderr` back so the agent adapts. In practice Claude often stops mid-turn and waits for user input, turning a fixable guardrail into a hard halt ([issue #24327](https://github.com/anthropics/claude-code/issues/24327)).
- Long sub-command chains bypass deny rules: Claude Code has been shown to skip permission checks when a tool call carries a long chain of sub-commands, falling back to asking the user instead of enforcing the deny ([The Register, Apr 2026](https://www.theregister.com/software/2026/04/01/claude-code-bypasses-safety-rule-if-given-too-many-commands/)). Scope hook matchers to atomic commands.
- Fragile string matchers: exact-command matchers break when the model varies invocation style (`git push origin main` versus `git push --set-upstream origin main`).
- No emergency override: a hook can block a legitimate time-sensitive operation. Document an override (for example, a `settings.local.json` entry) so contributors are not stuck.

## When to use hooks instead of instructions

Hooks: rules that must hold without exception, strong opposing model priors (package managers, test runners), behavior that must survive multi-step sessions.

Instructions: contextual "prefer X when Y" guidance, or suggestions rather than requirements.

## Key Takeaways

- `PreToolUse` + `Bash` matcher covers CLI enforcement and destructive guardrails
- `PostToolUse` + `Edit|Write` matcher runs side effects like linting after file changes
- Session-level events (`Stop`, `UserPromptSubmit`) fire unconditionally — no matcher support
- Return `permissionDecision: "deny"` to block; `permissionDecisionReason` feeds back into the model
- Project hooks in `.claude/settings.json` travel with the repo and apply to all contributors

## Related

- [Hooks and Lifecycle Events: Intercepting Agent Behavior](hooks-lifecycle-events.md)
- [Hooks for Enforcement vs Prompts for Guidance](../instructions/hooks-vs-prompts.md)
- [Conditional Hook Execution: Filter Hooks by Tool Pattern](conditional-hook-execution.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../tools/claude/posttooluse-auto-formatting.md)
- [PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries](precompact-hook-compaction-veto.md)
- [On-Demand Skill Hooks: Session-Scoped Hook Guardrails](on-demand-skill-hooks.md)
- [StopFailure Hook: Observability for API Error Termination](stopfailure-hook.md)
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md)
- [Hook Exec Form vs Shell Form: Shell-Injection-Safe Hook Commands](hook-exec-form-vs-shell.md) — choosing the args-array exec form so substituted tool input cannot inject shell metacharacters into a hook command
