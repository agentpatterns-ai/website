---
title: "On-Demand Skill Hooks: Session-Scoped Hook Guardrails"
description: "Register PreToolUse hooks through a skill invocation to arm strict guardrails for a single session without imposing friction on every workflow."
tags:
  - security
  - agent-design
  - claude
aliases:
  - on-demand hooks
  - session-scoped guardrails
  - opt-in hooks
---

# On-Demand Skill Hooks: Session-Scoped Guardrails via Skill Invocation

> Register `PreToolUse` hooks through a skill invocation to arm strict guardrails for the duration of a single session — without imposing that friction on every workflow.

## The Problem with Always-On Hooks

Always-on hooks in `.claude/settings.json` apply to every session, every developer, every task. For guardrails like blocking `rm -rf` or `DROP TABLE`, that universality is often appropriate. For stricter controls — blocking any write outside a specific directory, blocking all destructive git commands — always-on enforcement creates constant friction in the sessions that don't need it.

Skills registered through the `hooks` frontmatter field solve this. They activate when the skill is invoked and are automatically removed when the skill finishes or becomes inactive ([hooks reference](https://code.claude.com/docs/en/hooks)). The skill invocation is the signal: calling `/careful` communicates intent ("I'm touching prod") and arms the constraints simultaneously.

## How Skill-Scoped Hooks Work

Skills can declare a `hooks` field in their YAML frontmatter using the same configuration format as `settings.json` hooks ([skills docs](https://code.claude.com/docs/en/skills)). These hooks are registered in memory for the current session.

Per the [Claude Code documentation](https://code.claude.com/docs/en/hooks), skill hooks "use the same configuration format as settings-based hooks but are scoped to the component's lifetime and cleaned up when it finishes." The hooks are component-scoped — active while the skill is running — rather than persistent across the whole session. This makes skills an effective way to temporarily arm guardrails for the duration of a specific task.

Skill hooks support all hook event types — including `PreToolUse`, `PostToolUse`, `PermissionRequest`, and `Stop` — plus one additional field not available in `settings.json` or agents: `once`. When `once: true`, the hook fires once per session and is then removed — useful for initialization checks ([hooks reference](https://code.claude.com/docs/en/hooks)).

Hook source is shown in the `/hooks` menu with a `Session` label, distinguishing skill-registered hooks from project or user-level settings hooks ([changelog v2.1.75](https://code.claude.com/docs/en/changelog)).

## When to Use On-Demand vs. Always-On

| Scenario | On-demand (skill hook) | Always-on (`settings.json`) |
|----------|----------------------|------------------------------|
| Guardrail correct in one context, friction elsewhere | Yes | No |
| Rule applies to all developers on all tasks | No | Yes |
| Touching production systems | Yes | — |
| Working in a restricted directory | Yes | — |
| Debugging a fragile or high-stakes system | Yes | — |
| Team-wide package manager enforcement | No | Yes |

The cost of always-on hooks is friction in every session that doesn't need them. The cost of on-demand hooks is that the guardrail is absent unless explicitly invoked — the engineer must remember to call the skill.

## Contrast: Always-On vs. On-Demand

**Always-on** — applies to every session, whether touching prod or running a local demo:

```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": ".claude/hooks/block-destructive.sh"}]
    }]
  }
}
```

**On-demand via `/careful` skill** — arms the same hook only when the engineer invokes the skill:

```yaml
# .claude/skills/careful/SKILL.md
---
name: careful
description: Arms strict guardrails for this session. Invoke when touching
  production systems, running migrations, or operating in restricted
  directories. Blocks rm -rf, DROP TABLE, force-push, and kubectl delete.
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: .claude/hooks/block-destructive.sh
---

You are operating in careful mode. Every destructive command will be blocked.
Confirm with the user before proceeding with any irreversible operation.
```

## Example

A `/careful` skill registers a `PreToolUse` hook that blocks `rm -rf`, `DROP TABLE`, `git push --force`, and `kubectl delete`. The hook script reads the Bash command from stdin and denies any match:

```bash
#!/bin/bash
# .claude/hooks/block-destructive.sh
COMMAND=$(jq -r '.tool_input.command')
if echo "$COMMAND" | grep -qE 'rm -rf|DROP TABLE|git push --force|git push -f|kubectl delete'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive command blocked in careful mode — confirm intent before proceeding"
    }
  }'
else
  exit 0
fi
```

A `/freeze` variant uses the same mechanism but blocks any `Edit` or `Write` call outside a specific directory:

```bash
#!/bin/bash
# .claude/hooks/freeze-writes.sh
TOOL=$(jq -r '.tool_name')
FILE=$(jq -r '.tool_input.path // .tool_input.file_path // empty')
ALLOWED_PREFIX="/home/user/project/src"

if [[ "$TOOL" == "Edit" || "$TOOL" == "Write" ]]; then
  if [[ -n "$FILE" && "$FILE" != "$ALLOWED_PREFIX"* ]]; then
    jq -n '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Writes outside /src are blocked in freeze mode"
      }
    }'
    exit 0
  fi
fi
exit 0
```

The skill frontmatter wires it in:

```yaml
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: .claude/hooks/freeze-writes.sh
```

When the skill finishes, the hook is removed. No cleanup required.

## Key Takeaways

- Skill-defined hooks are component-scoped: they activate when the skill runs and are removed when it finishes ([hooks reference](https://code.claude.com/docs/en/hooks))
- Skill invocation is both the human signal ("I need prod-safe guardrails") and the system action (arming those guardrails)
- The `once` field, available only in skill hooks, fires a hook once per session then removes it — useful for initialization guardrails
- Session-sourced hooks appear with a `Session` label in the `/hooks` menu, distinct from project and user settings hooks
- The tradeoff: on-demand hooks require the engineer to invoke the skill; always-on hooks enforce without relying on that discipline
- Use on-demand hooks for context-specific restrictions; use always-on hooks for universal team standards

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](hook-catalog.md)
- [Hooks and Lifecycle Events: Intercepting Agent Behavior](hooks-lifecycle-events.md)
- [Conditional Hook Execution: Filter Hooks by Tool Pattern](conditional-hook-execution.md)
- [Skill Authoring Patterns](skill-authoring-patterns.md)
- [SKILL.md Frontmatter Reference: All Fields Explained](skill-frontmatter-reference.md)
- [Skill Tool as Enforcement: Loading Command Prompts at Runtime](skill-tool-runtime-enforcement.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md)
- [Protecting Sensitive Files from Agent Context](../security/protecting-sensitive-files.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](../workflows/posttooluse-auto-formatting.md)
