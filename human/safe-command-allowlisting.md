---
title: "Safe Command Allowlisting: Reducing Approval Fatigue"
description: "Pre-authorizing low-risk operations reduces permission prompts so developers stay alert to the ones that matter, preventing approval fatigue."
aliases:
  - command whitelisting
  - permission pre-authorization
tags:
  - human-factors
  - agent-design
  - claude
---

# Safe Command Allowlisting: Reducing Approval Fatigue

> Automatically approving low-risk operations reduces permission prompts so developers stay alert to the ones that matter.

## The Problem with Constant Approval Requests

When an agent requests permission for every action — reading a file, echoing a variable, running `git status` — developers face a losing tradeoff: review each prompt carefully and accept the slowdown, or approve reflexively and lose meaningful oversight.

[Anthropic's engineering team](https://www.anthropic.com/engineering/claude-code-sandboxing) identifies the consequence directly: "Constantly clicking 'approve' slows down development cycles and can lead to 'approval fatigue', where users might not pay close attention to what they're approving, and in turn making development less safe."

Approval fatigue converts a safety control into a ritual. Real risk prompts receive the same cursory treatment as innocuous ones.

## The Fix: Allowlist Low-Risk Operations

The resolution is to remove low-signal prompts entirely by pre-authorizing operations that cannot cause harm. Anthropic reports an **84% reduction in permission prompts** through this approach in their Claude Code sandboxing implementation, while keeping human review focused on genuinely risky actions.

Operations appropriate for auto-approval share a profile:

- **Read-only** — they observe state without changing it
- **Non-networked** — they do not exfiltrate data or contact external services
- **Reversible** — if they do change anything, the change is trivially undone
- **Locally scoped** — they operate within a known, bounded filesystem path

## Configuring Allowlists in Claude Code

Claude Code's permission system uses `allow`, `ask`, and `deny` rules in `.claude/settings.json` ([docs](https://code.claude.com/docs/en/settings)). Rules match on tool name and an optional command specifier; deny is evaluated first, allow last:

```json
{
  "permissions": {
    "allow": [
      "Bash(echo *)", "Bash(cat *)", "Bash(ls *)",
      "Bash(git status)", "Bash(git diff *)", "Bash(git log *)"
    ],
    "ask": ["Bash(git push *)", "Bash(git reset *)"],
    "deny": ["Bash(curl *)", "Bash(wget *)", "Read(./.env)"]
  }
}
```

This auto-approves read-only shell operations, requires confirmation before pushing or resetting, and blocks network access and sensitive file reads.

## Risk Tiers for Classification

Categorize agent actions across three tiers before deciding where to place them:

| Tier | Characteristics | Default handling |
|------|-----------------|-----------------|
| Safe | Read-only, no network, no state mutation | Auto-approve via `allow` |
| Elevated | Reversible writes, local scope, no secrets access | Confirm via `ask` |
| Restricted | Destructive, networked, or accesses sensitive paths | Block via `deny` |

Commands that write files sit in Elevated by default. Commands that mutate git history, push to remotes, or access secrets sit in Restricted regardless of how the agent frames the request.

## Pairing Allowlists with Sandbox Boundaries

Allowlisting reduces prompt volume; sandbox boundaries determine what allowlisted commands can actually reach.

- **Filesystem isolation** constrains which paths the agent can read or write, independent of permission prompts
- **Network isolation** blocks exfiltration regardless of whether a command was auto-approved

Anthropic's sandboxing covers "not just Claude Code's direct interactions, but also any scripts, programs, or subprocesses that are spawned by the command" — a locally benign command can spawn a child process that makes an outbound call.

An allowlist without sandbox boundaries relies entirely on the accuracy of your classification. A sandbox without an allowlist retains the fatigue problem. Together they achieve high-signal oversight and a contained [blast radius](../security/blast-radius-containment.md) if a classification is wrong.

## What This Is Not

Allowlisting eliminates noise so that genuine risk prompts stand out; it is not a reduction in oversight. The measure of a well-configured allowlist is whether the prompts that remain reliably signal actions worth reviewing — not how many prompts were suppressed.

## Key Takeaways

- Approval fatigue turns permission prompts into rubber-stamps, creating an illusion of oversight with none of the substance
- Anthropic reports 84% reduction in permission prompts by auto-approving read-only, locally scoped operations ([source](https://www.anthropic.com/engineering/claude-code-sandboxing))
- Claude Code's `allow` / `ask` / `deny` permission rules in `.claude/settings.json` implement allowlisting at the command level
- Classify operations into safe, elevated, and restricted tiers; auto-approve only safe-tier actions
- Pair allowlists with filesystem and network sandbox boundaries so misclassified commands are still contained

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Hooks for Enforcement vs Prompts for Guidance](../verification/hooks-vs-prompts.md)
- [The AI Development Maturity Model](../workflows/ai-development-maturity-model.md)
- [Evidence-Based Allowlist Auto-Discovery for Agents](evidence-based-allowlist-auto-discovery.md)
- [Progressive Autonomy: Scaling Trust with Model Evolution](progressive-autonomy-model-evolution.md)
- [Cognitive Load, AI Fatigue, and Sustainable Agent Use](cognitive-load-ai-fatigue.md)
- [The Bottleneck Migration](bottleneck-migration.md)
- [Suggestion Gating](suggestion-gating.md)
