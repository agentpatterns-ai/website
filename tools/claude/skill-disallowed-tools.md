---
title: "Skill disallowed-tools Frontmatter: Skill-Layer Tool Denial"
description: "A Claude Code skill lists disallowed-tools in frontmatter to remove tools from the model while active — the deny-side complement to allowed-tools."
tags:
  - claude
  - security
aliases:
  - skill tool denial
  - disallowed-tools frontmatter
applies_to: "claude-code@2.x"
last_reviewed: 2026-05-27
status: current
---

# Skill disallowed-tools Frontmatter

> A Claude Code skill lists `disallowed-tools` in frontmatter to remove tools from the model while active — the deny-side complement to `allowed-tools`.

The `disallowed-tools` frontmatter field removes the listed tools from Claude's available pool while a skill is active. It shipped in Claude Code v2.1.152 on 2026-05-27: "Skills and slash commands can now set `disallowed-tools` in frontmatter to remove tools from the model while the skill is active" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). A skill author who wants a read-only or analysis skill to never touch `Bash`, `Write`, or `Edit` lists those tools and they disappear for the skill's turn — least privilege applied at the skill layer, without editing global settings.

## allowed-tools vs disallowed-tools

The two fields are not symmetric. They operate on different parts of the permission model:

| Field | Effect | Tool still callable? |
|-------|--------|----------------------|
| `allowed-tools` | Pre-approves the listed tools so Claude uses them without prompting | Yes — every tool remains callable; this only suppresses the approval prompt |
| `disallowed-tools` | Removes the listed tools from the model's available pool | No — a removed tool cannot be seen or invoked |

`allowed-tools` "does not restrict which tools are available: every tool remains callable, and your permission settings still govern tools that are not listed" ([skills reference](https://code.claude.com/docs/en/skills)). It is permission pre-approval, not a boundary. `disallowed-tools` is the actual restriction the `allowed-tools` documentation points authors toward when removal — not pre-approval — is the goal.

## Why It Works

Removing a tool shrinks the action space the model can take: it cannot call a tool it cannot see. This is the deny-side instance of least privilege — the smallest blast radius is the one where dangerous tools are simply absent during the risky operation, rather than present-but-gated. The skills reference states the mechanism directly: tools are "removed from Claude's available pool while this skill is active" ([skills reference](https://code.claude.com/docs/en/skills)). Because a removed tool cannot be approved, `disallowed-tools` dominates `allowed-tools` for any tool named in both — and because removal can only take a tool away, it shrinks the available pool and never widens it. This subtract-only behavior is what makes it safe to layer over existing permission rules. See [Blast Radius Containment](../../security/blast-radius-containment.md) for the general least-privilege pattern and [Monotonic Capability Attenuation](../../security/monotonic-capability-attenuation.md) for why authority that can only shrink is composition-safe.

## When This Backfires

`disallowed-tools` is a turn-scoped convenience, not a durable security boundary. It backfires in three ways:

- **Over-restriction breaks a legitimate step.** A read-only audit skill that denies `Bash` cannot run a linter sub-command it actually needs. The skill silently degrades instead of failing loudly — scope the deny list to tools the skill genuinely never uses.
- **Turn-scope surprise.** "The restriction clears when you send your next message" ([skills reference](https://code.claude.com/docs/en/skills)). Authors who treat `disallowed-tools` as a persistent session lock get a false sense of security; a follow-up prompt re-exposes the tool. For durable denial, use permission deny rules in settings.
- **Fragmented posture at scale.** Many skills each declaring their own deny list makes the effective allow/deny set hard to audit centrally. For org-wide guarantees, managed-settings deny rules are the right layer — see [Managed Settings Drop-In Directory](managed-settings-drop-in.md).

For the durable, central alternative, deny the tool in [permission settings](https://code.claude.com/docs/en/permissions) instead.

## Example

A read-only audit skill that should analyze code but never modify it or shell out. Listing the write and execution tools in `disallowed-tools` removes them for the skill's turn:

```yaml
---
name: code-audit
description: Read-only audit of the working tree for security and structure issues.
disallowed-tools: Bash, Write, Edit, MultiEdit
allowed-tools: Read, Grep, Glob
---

Audit the current changes for:
- hardcoded secrets or credentials
- missing input validation
- structural complexity that warrants refactoring

Report findings only. Do not modify any files.
```

While this skill is active, `Bash`, `Write`, `Edit`, and `MultiEdit` are absent from the model's tool pool, so an injected instruction in a fetched file cannot coerce a write or a shell command — the tools are not there to call. `allowed-tools` pre-approves the read-only trio so the audit runs without per-use prompts. The deny list clears on the next user message.

## Key Takeaways

- `disallowed-tools` removes listed tools from the model's pool while a skill is active (Claude Code v2.1.152, 2026-05-27)
- It is the deny-side complement to `allowed-tools`: removal, not pre-approval — and it dominates `allowed-tools` for any overlapping tool
- Removal can only subtract: it shrinks the available tool pool and never widens it, so it layers safely over existing permission rules
- The restriction is turn-scoped — it clears on the next user message, so it is not a durable session lock
- For persistent or org-wide denial, use permission deny rules in settings, not skill frontmatter

## Related

- [SKILL.md Frontmatter Reference](../../tool-engineering/skill-frontmatter-reference.md)
- [Blast Radius Containment](../../security/blast-radius-containment.md)
- [Skill Shell Execution Gate](../../security/skill-shell-execution-gate.md)
- [Claude Code Sub-Agents](sub-agents.md)
- [Monotonic Capability Attenuation](../../security/monotonic-capability-attenuation.md)
