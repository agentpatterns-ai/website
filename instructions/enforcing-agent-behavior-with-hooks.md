---
title: "Enforcing Agent Behavior with Hooks"
description: "Move critical behavioral rules out of prompts and into deterministic shell hooks that the model cannot override — blocking forbidden actions, rewriting inputs, and gating task completion."
tags:
  - instructions
  - agent-design
  - claude
  - source:docs
aliases:
  - Rigor Relocation
  - Deterministic Behavioral Enforcement
  - Hook-Based Agent Governance
---

# Enforcing Agent Behavior with Hooks

> Move critical behavioral rules out of prompts and into deterministic shell hooks that the model cannot override — blocking forbidden actions, rewriting inputs, and gating task completion.

!!! note "Also known as"
    Rigor Relocation, Deterministic Behavioral Enforcement, Hook-Based Agent Governance.

## The Enforcement Spectrum

Agent behavioral rules exist on a spectrum from advisory to deterministic. Most teams start at the left and never move right, leaving their highest-stakes rules at the mercy of model attention.

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

**Advisory** — Rules in CLAUDE.md or AGENTS.md. The model reads them at session start but may ignore them under task pressure, context compaction, or when strong training priors conflict ([Lavaee, 2025](https://alexlavaee.me/blog/openai-agent-first-codebase-learnings)).

**Probabilistic** — Rules injected via system prompts or event-driven reminders. Higher attention weight than file-based instructions, but still subject to drift in long sessions ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)).

**Deterministic** — Shell hooks that execute outside the model's context window. A hook returning exit code 2 blocks the tool call unconditionally — the model cannot override it, argue with it, or forget it ([Claude Code hooks](https://code.claude.com/docs/en/hooks)).

**Organizational** — Managed policies pushed via MDM or enterprise configuration. These hooks cannot be disabled at the project or user level, enforcing organization-wide standards.

The key insight: **rigor relocation**. Instead of writing more detailed instructions and hoping the model follows them, relocate the enforcement to a layer the model cannot influence. Every rule that moves from advisory to deterministic is a rule that stops failing silently.

## Three Hook Patterns

Claude Code hooks fire on lifecycle events (`PreToolUse`, `PostToolUse`, `Notification`, `Stop`) and receive JSON context via stdin. Three patterns cover most enforcement needs ([Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)):

### Block: Exit Code 2

The simplest pattern. The hook inspects the tool call, and if it violates a rule, exits with code 2. Claude Code blocks the call and shows the hook's stderr as the reason.

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

Exit code 2 means "blocked." Exit code 0 means "allowed." Any other exit code is treated as a hook error and does not block.

### Rewrite: Transform Inputs via `updatedInput`

A hook can modify the tool call rather than blocking it. Output a JSON object with an `updatedInput` field to stdout, and Claude Code replaces the original input before execution.

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

The model sees the rewritten command in its output, reinforcing the correct pattern for future calls without needing an instruction.

### Completion Gates: Stop Hooks

`Stop` hooks fire when the agent is about to end its turn. Use them to enforce completion criteria — running a linter, checking test coverage, or validating that a spec file was updated.

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

If the Stop hook exits with code 2, the agent does not stop — it continues working with the hook's stderr as feedback. This creates a completion gate: the agent cannot declare "done" until the gate passes.

## Hook Scoping Hierarchy

Hooks resolve from four scopes, each with different trust and override properties ([Claude Code hooks](https://code.claude.com/docs/en/hooks)):

| Scope | Location | Override by user? | Use case |
|---|---|---|---|
| **User** | `~/.claude/settings.json` | Yes | Personal workflow preferences |
| **Project** | `.claude/settings.json` (committed) | Yes | Team-wide enforcement |
| **Local** | `.claude/settings.local.json` | Yes | Per-machine overrides |
| **Managed** | Enterprise MDM policy | No | Organization-wide mandates |

Managed hooks cannot be disabled by project or user settings. This is how organizations enforce security policies without trusting individual developers to maintain their hook configurations.

## Why Hooks Beat Instructions

Models revert to training defaults under pressure. This is not a bug — it is how attention-based architectures work when the context window fills or when instructions conflict with strong priors ([Fowler, 2025](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)).

Common failure modes that instructions alone cannot prevent:

- **Training prior override**: The model uses `npm` despite CLAUDE.md saying "use pnpm" — `npm` is vastly more common in training data
- **Context compaction loss**: After compaction, behavioral rules are summarized or dropped, and the model reverts
- **Multi-step drift**: In long task chains, compliance with early instructions degrades as attention distributes across accumulated context

Hooks are immune to all three. They execute in the shell, not in the context window. The model's attention, priors, and compaction behavior are irrelevant.

## When to Use Each Layer

Not every rule needs a hook. The decision depends on the cost of violation and whether the rule requires judgment.

| Rule type | Layer | Example |
|---|---|---|
| Style preference | Advisory (CLAUDE.md) | "Prefer functional style" |
| Naming convention | Advisory + linter | "Use snake_case for variables" |
| Package manager | Deterministic (hook) | "Use uv, not pip" |
| Destructive command | Deterministic (hook) | "No force push" |
| Completion criteria | Deterministic (Stop hook) | "Tests must pass before done" |
| Security policy | Organizational (managed) | "No secrets in source" |

Rules that require context or judgment — "write concise commit messages," "prefer composition over inheritance" — belong in instructions. Rules that are binary and non-negotiable belong in hooks. See [hooks for enforcement vs prompts for guidance](../verification/hooks-vs-prompts.md) for the detailed decision framework.

## Key Takeaways

- Exit code 2 blocks a tool call unconditionally — no model can override a shell process
- Relocate rigor from instructions to hooks for every binary, non-negotiable rule
- Use Block hooks for prohibitions, Rewrite hooks for corrections, and Stop hooks for completion gates
- Managed hooks enforce organizational policy beyond individual developer control
- Instructions handle judgment; hooks handle compliance — use both, but know which does what

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Hooks for Enforcement vs Prompts for Guidance](../verification/hooks-vs-prompts.md)
- [Deterministic Guardrails](../verification/deterministic-guardrails.md)
- [Defense-in-Depth Agent Safety](../security/defense-in-depth-agent-safety.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Hooks Lifecycle Events](../tool-engineering/hooks-lifecycle-events.md)
