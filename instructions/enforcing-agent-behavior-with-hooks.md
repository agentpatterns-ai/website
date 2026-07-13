---
title: "Enforcing Agent Behavior with Hooks"
description: "Move critical behavioral rules out of prompts and into deterministic shell hooks that the model cannot override — blocking forbidden actions, rewriting inputs, and gating task completion."
term: "Enforcing Agent Behavior with Hooks"
tags:
  - instructions
  - agent-design
  - claude
aliases:
  - Rigor Relocation
  - Deterministic Behavioral Enforcement
  - Hook-Based Agent Governance
last_reviewed: 2026-06-09
maturity: emerging
---

# Enforcing Agent Behavior with Hooks

> Move critical rules out of prompts into deterministic shell hooks the model cannot override — blocking forbidden actions, rewriting inputs, and gating task completion.

## The enforcement spectrum

Behavioral rules sit on a spectrum from advisory to deterministic. Most teams leave high-stakes rules at the mercy of model attention.

```mermaid
graph LR
    A["Advisory<br/><small>CLAUDE.md rules</small>"] --> B["Probabilistic<br/><small>System prompt<br/>injection</small>"]
    B --> C["Deterministic<br/><small>Shell hooks<br/>(exit code 2)</small>"]
    C --> D["Organizational<br/><small>Managed policies<br/>via MDM</small>"]

    style A fill:#ffeeba,stroke:#856404
    style B fill:#d4edda,stroke:#155724
    style C fill:#cce5ff,stroke:#004085
    style D fill:#d6d8db,stroke:#383d41
```

Advisory — rules in CLAUDE.md or [AGENTS.md](../standards/agents-md.md). The model may ignore them under task pressure, [context compaction](../context-engineering/context-compression-strategies.md), or conflicting training priors ([Lavaee, 2025](https://alexlavaee.me/blog/openai-agent-first-codebase-learnings)).

Probabilistic — system prompts or event-driven reminders. They carry higher attention weight, but still drift in long sessions ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)).

Deterministic — shell hooks that run outside the context window. Exit code 2 is documented to block the tool call and feed stderr back to the model ([Claude Code hooks](https://code.claude.com/docs/en/hooks)). The model cannot argue with or forget a shell process. Coverage varies by event and tool — see [when this backfires](#when-this-backfires) for current gaps.

Organizational — managed policies via MDM. They enforce organization-wide standards beyond project or user control.

This is [rigor relocation](../human/rigor-relocation.md): move enforcement to a layer the model cannot influence. Every rule you shift from advisory to deterministic stops failing silently.

## Three hook patterns

Claude Code hooks fire on lifecycle events (`PreToolUse`, `PostToolUse`, `Notification`, `Stop`) and receive JSON via stdin ([Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)):

### Block: exit code 2

The hook exits with code 2 to block the tool call. Its stderr becomes the block reason.

```jsonc
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "python .claude/hooks/block-force-push.py"
      }
    ]
  }
}
```

```python
# .claude/hooks/block-force-push.py
import json, sys

event = json.load(sys.stdin)
cmd = event.get("tool_input", {}).get("command", "")
if "push" in cmd and ("--force" in cmd or "-f" in cmd):
    print("Blocked: force push requires human confirmation", file=sys.stderr)
    sys.exit(2)
```

Exit 2 blocks the call. Exit 0 allows it. Any other code counts as a hook error and does not block.

### Rewrite: transform inputs via `updatedInput`

A hook can modify the tool call instead of blocking. Print JSON with `updatedInput` to stdout and Claude Code replaces the original input.

```python
# .claude/hooks/enforce-uv.py
import json, sys

event = json.load(sys.stdin)
cmd = event.get("tool_input", {}).get("command", "")
if cmd.startswith("pip install"):
    package = cmd.replace("pip install", "uv pip install")
    result = {"updatedInput": {"command": package}}
    json.dump(result, sys.stdout)
```

The model sees the rewritten command, reinforcing the correct pattern for future calls.

### Completion gates: Stop hooks

`Stop` hooks fire when the agent is about to end its turn. Use them to run a linter, check test coverage, or validate spec updates before "done."

```jsonc
{
  "hooks": {
    "Stop": [
      {
        "command": "python .claude/hooks/lint-before-done.py"
      }
    ]
  }
}
```

Exit 2 from a Stop hook prevents the agent from stopping. It continues with the hook's stderr as feedback. The agent cannot declare "done" until the gate passes. `Stop` and `SubagentStop` hooks can also return `hookSpecificOutput.additionalContext` to give Claude steering feedback and keep the turn going, without being flagged as a hook error ([Claude Code 2.1.163 changelog](https://code.claude.com/docs/en/changelog)). This turns a completion gate into a soft nudge rather than a halt.

## Hook scoping hierarchy

Hooks resolve from four scopes with different trust and override properties ([Claude Code hooks](https://code.claude.com/docs/en/hooks)):

| Scope | Location | Override by user? | Use case |
|---|---|---|---|
| User | `~/.claude/settings.json` | Yes | Personal workflow preferences |
| Project | `.claude/settings.json` (committed) | Yes | Team-wide enforcement |
| Local | `.claude/settings.local.json` | Yes | Per-machine overrides |
| Managed | Enterprise MDM policy | No | Organization-wide mandates |

Managed hooks cannot be disabled by project or user settings, so organizations can enforce security policies regardless of developer configuration.

## Why hooks beat instructions

Models revert to training defaults under pressure — attention-based architectures lose instruction compliance as the context window fills or priors conflict ([Fowler, 2025](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)). Hooks execute in the shell, outside the context window.

## When to use each layer

| Rule type | Layer | Example |
|---|---|---|
| Style preference | Advisory (CLAUDE.md) | "Prefer functional style" |
| Naming convention | Advisory + linter | "Use snake_case for variables" |
| Package manager | Deterministic (hook) | "Use uv, not pip" |
| Destructive command | Deterministic (hook) | "No force push" |
| Completion criteria | Deterministic (Stop hook) | "Tests must pass before done" |
| Security policy | Organizational (managed) | "No secrets in source" |

Judgment rules belong in instructions. Binary, non-negotiable rules belong in hooks. See [hooks for enforcement vs prompts for guidance](hooks-vs-prompts.md).

## When this backfires

- Exit code 2 has coverage gaps. `PreToolUse` exit code 2 has failed to block `Write` and `Edit` while still blocking `Bash` ([anthropics/claude-code #13744](https://github.com/anthropics/claude-code/issues/13744)), and has caused the agent to halt idle rather than act on stderr ([#24327](https://github.com/anthropics/claude-code/issues/24327)). Prefer JSON stdout with explicit `decision` fields when tool-level nuance matters.
- False positives cost more than the rule saves. Broad matchers block legitimate commands. Rewrite hooks break projects with intentional exceptions. Scope matchers narrowly.
- Hooks fail open silently. Any exit code other than 0 or 2 counts as a hook error and does not block. Teammates with missing dependencies get no enforcement and no warning ([5 Claude Code hook mistakes](https://dev.to/yurukusa/5-claude-code-hook-mistakes-that-silently-break-your-safety-net-58l3)).
- Judgment rules regress when forced binary. "Prefer descriptive names" or "add tests when changing behavior" lose nuance compressed into a regex. Keep ambiguous rules in CLAUDE.md.

## Key Takeaways

- Exit code 2 is the documented block signal — a shell process sits outside the context window, but coverage gaps exist across tools and events
- Relocate rigor from instructions to hooks for every binary, non-negotiable rule
- Use Block hooks for prohibitions, Rewrite hooks for corrections, and Stop hooks for completion gates
- Managed hooks enforce organizational policy beyond individual developer control
- Instructions handle judgment; hooks handle compliance — use both, but know which does what

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Hooks for Enforcement vs Prompts for Guidance](hooks-vs-prompts.md)
- [Deterministic Guardrails](../verification/deterministic-guardrails.md)
- [Defense-in-Depth Agent Safety](../security/defense-in-depth-agent-safety.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md) — where instruction text stops working, hooks start
- [Event-Driven System Reminders](event-driven-system-reminders.md)
- [Hooks Lifecycle Events](../tool-engineering/hooks-lifecycle-events.md)
