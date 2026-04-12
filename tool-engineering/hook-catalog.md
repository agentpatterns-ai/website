---
title: "Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement"
description: "A reference catalog of high-value Claude Code hooks grouped by purpose — CLI enforcement, destructive operation guardrails, sandboxing, and workflow automation."
tags:
  - agent-design
  - instructions
  - workflows
  - claude
aliases:
  - Hook Examples & Recipes
  - Common Enforcement Patterns
  - Enforcing with Hooks
  - Hook Enforcement Patterns
---

# Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement

> Claude Code hooks are shell commands that intercept agent lifecycle events — blocking forbidden tool calls, enforcing CLI standards, and automating side effects — without relying on the model to follow instructions.

!!! note "Also known as"
    Hook Examples & Recipes, Common Enforcement Patterns, Hook Catalog, Enforcing with Hooks, Hook Enforcement Patterns.

## Why Hooks

Models carry strong training priors: they reach for `npm`, `git add -A`, or `curl` by default. Instructions can suggest alternatives, but models revert under pressure. Hooks move enforcement out of the context window and into the shell.

| Approach | Reliability | Override risk |
|----------|------------|---------------|
| AGENTS.md instruction | Low — model interprets freely | High — model may ignore under task pressure |
| System prompt rule | Medium — higher attention weight | Medium — multi-step tasks cause drift |
| `PreToolUse` hook | High — executes in shell | None — model cannot bypass |

## How Hooks Work

[Claude Code hooks](https://code.claude.com/docs/en/hooks) are shell commands that run in response to agent lifecycle events. Claude Code passes JSON context about the event to the hook on stdin. Use `jq` to extract fields.

| Event | Fires when |
|-------|-----------|
| `PreToolUse` | Before any tool call executes — can block it |
| `PostToolUse` | After a tool call succeeds |
| `UserPromptSubmit` | When the user sends a message |
| `Stop` | When the agent finishes a turn |

A hook that returns a `permissionDecision` of `"deny"` **blocks the tool call**. The `permissionDecisionReason` is fed back into the agent's context, so the agent must adapt — it cannot proceed without complying.

## CLI Tool Enforcement

Force the model to use project-mandated tools instead of training defaults.

**Block npm, require bun:**

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

**Block python, require uv:**

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

## Destructive Operation Guardrails

Block or flag commands that are difficult or impossible to reverse.

**Block `rm -rf`:**

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

**Block `git reset --hard` and `git push --force`:**

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

**Block direct push to main:**

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

## Workflow Automation

Run side effects automatically as the agent works.

**Auto-lint after file writes:**

```json
{
  "hooks": {
    "PostToolUse": [{"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "bun run lint --fix"}]}]
  }
}
```

**Log all prompts for audit:**

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

**Desktop notification on agent completion:**

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

Note: `UserPromptSubmit`, `Stop`, and other session-level events do not support matchers — they fire on every occurrence ([docs](https://code.claude.com/docs/en/hooks)).

## Sandboxing

Restrict what the agent can read or execute during sensitive operations.

**Restrict Bash to a command allowlist:**

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

**Block outbound network calls during agent sessions:**

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

## Instruction Auditing

Track which instruction files are loaded to verify configuration consistency across team members.

**Log loaded instructions:**

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

`InstructionsLoaded` fires when CLAUDE.md or `.claude/rules/*.md` files are loaded. The event payload includes `file_path`, `memory_type`, `load_reason`, and `trigger_file_path` — enough to audit which instruction files each agent session loads ([docs](https://code.claude.com/docs/en/hooks)).

## Hook Configuration and Combining

Multiple handlers can fire for the same event and matcher. Hooks scope at different levels ([docs](https://code.claude.com/docs/en/hooks); [settings reference](https://code.claude.com/docs/en/settings)):

| Location | Scope | Shareable |
|----------|-------|-----------|
| `~/.claude/settings.json` | All projects | No |
| `.claude/settings.json` | Single project | Yes — commit to repo |
| `.claude/settings.local.json` | Single project | No — gitignored |

Project-level hooks in `.claude/settings.json` travel with the repo and enforce team conventions for all contributors.

## When This Backfires

- **False positive blocking**: Over-broad regex matchers (e.g., matching `rm` instead of `rm -rf`) block legitimate commands. The model then exhausts retry attempts or hallucinates workarounds. Validate patterns against real command logs before deploying.
- **Silent failures hide problems**: A hook that exits non-zero without emitting a `permissionDecisionReason` gives the model no signal to adapt — the tool call silently fails. Always emit a reason string.
- **Maintenance burden from fragile patterns**: Hooks that match on exact command strings break when the model changes invocation style (e.g., `git push origin main` vs `git push --set-upstream origin main`). Pattern maintenance can outpace instruction updates.
- **No bypass path for emergency changes**: A hook enforcing team standards can block a legitimate time-sensitive operation. Without a documented override mechanism (e.g., `settings.local.json` entry), contributors are stuck.

## When to Use Hooks vs. Instructions

Use hooks when:

- The rule must be enforced without exception (security, compliance, team standards)
- The model has a strong opposing prior (package managers, test runners, git workflows)
- The behavior must persist across long multi-step sessions

Use instructions when:

- The guidance is contextual — "prefer X when Y" — and benefits from model judgment
- The rule is a suggestion, not a requirement

Instructions drift in long sessions; hooks do not.

## Key Takeaways

- `PreToolUse` + `Bash` matcher covers CLI enforcement and destructive guardrails
- `PostToolUse` + `Edit|Write` matcher runs side effects like linting after file changes
- Session-level events (`Stop`, `UserPromptSubmit`) fire unconditionally — no matcher support
- Return `permissionDecision: "deny"` to block; `permissionDecisionReason` feeds back into the model
- Project hooks in `.claude/settings.json` travel with the repo and apply to all contributors

## Related

- [Hooks for Enforcement vs Prompts for Guidance](../verification/hooks-vs-prompts.md)
- [Hooks and Lifecycle Events: Intercepting Agent Behavior](hooks-lifecycle-events.md)
- [Example-Driven vs Rule-Driven Instructions](../instructions/example-driven-vs-rule-driven-instructions.md)
- [Protecting Sensitive Files from Agent Context](../security/protecting-sensitive-files.md)
- [Secrets Management for Agent Workflows](../security/secrets-management-for-agents.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../workflows/posttooluse-auto-formatting.md)
- [On-Demand Skill Hooks: Session-Scoped Hook Guardrails](on-demand-skill-hooks.md)
- [PostToolUse Hook for BSD/GNU CLI Incompatibilities](posttooluse-bsd-gnu-detection.md)
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md)
- [Skill-Tool Runtime Enforcement](skill-tool-runtime-enforcement.md)
- [CLI Scripts as Agent Tools](cli-scripts-as-agent-tools.md)
