---
title: "Safe Command Allowlisting: Reducing Approval Fatigue"
term: "Safe Command Allowlisting"
description: "Pre-authorizing low-risk operations reduces permission prompts so developers stay alert to the ones that matter, preventing approval fatigue."
aliases:
  - command whitelisting
  - permission pre-authorization
tags:
  - agent-design
  - claude
  - security
last_reviewed: 2026-05-27
maturity: established
---

# Safe Command Allowlisting: Reducing Approval Fatigue

> Automatically approving low-risk operations reduces permission prompts so developers stay alert to the ones that matter.

## The problem with constant approval requests

When an agent requests permission for every action — file reads, variable echoes, `git status` — developers face a losing tradeoff: review each prompt carefully and accept the slowdown, or approve reflexively and lose oversight.

[Anthropic](https://www.anthropic.com/engineering/claude-code-sandboxing) names the consequence: "Constantly clicking 'approve' slows down development cycles and can lead to 'approval fatigue', where users might not pay close attention to what they're approving, and in turn making development less safe."

Approval fatigue converts a safety control into a ritual; real-risk prompts get the same cursory treatment as innocuous ones.

## The fix: allowlist low-risk operations

Remove low-signal prompts by pre-authorizing operations that cannot cause harm. Anthropic reports an 84% reduction in permission prompts with this approach, while keeping human review focused on risky actions.

Operations safe to auto-approve share four properties:

- Read-only — observe state without changing it
- Non-networked — no exfiltration or external calls
- Reversible — any change is trivially undone
- Locally scoped — bounded to a known filesystem path

## Configuring allowlists in Claude Code

Claude Code's permission system uses `allow`, `ask`, and `deny` rules in `.claude/settings.json` ([Claude Code settings reference](https://code.claude.com/docs/en/settings)). Rules match on tool name and an optional command specifier. Deny is evaluated first, allow last:

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

## Risk tiers for classification

Categorize agent actions across three tiers before deciding where to place them:

| Tier | Characteristics | Default handling |
|------|-----------------|-----------------|
| Safe | Read-only, no network, no state mutation | Auto-approve via `allow` |
| Elevated | Reversible writes, local scope, no secrets access | Confirm via `ask` |
| Restricted | Destructive, networked, or accesses sensitive paths | Block via `deny` |

Commands that write files sit in Elevated by default. Commands that mutate git history, push to remotes, or access secrets sit in Restricted regardless of how the agent frames the request.

## Pairing allowlists with sandbox boundaries

Allowlisting reduces prompt volume. Sandbox boundaries determine what allowlisted commands can actually reach.

- Filesystem isolation constrains read and write paths regardless of prompts
- Network isolation blocks exfiltration regardless of approval

Anthropic's sandboxing covers "not just Claude Code's direct interactions, but also any scripts, programs, or subprocesses" — a benign command can spawn a child that makes an outbound call.

An allowlist without sandbox boundaries relies entirely on the accuracy of your classification. A sandbox without an allowlist retains the fatigue problem. Together they achieve high-signal oversight and a contained [blast radius](blast-radius-containment.md) if a classification is wrong.

The sandbox layer is itself fallible. A SOCKS5 hostname null-byte bypass in Claude Code's network sandbox (Claude Code v2.0.24 through v2.1.89, patched in v2.1.88 on 2026-03-31 and re-bumped in v2.1.90, publicly disclosed May 2026) let an allowlisted shell command escape the network policy via a crafted hostname ([The Register, 2026-05-20](https://www.theregister.com/security/2026/05/20/even-claude-agrees-hole-in-its-sandbox-was-real-and-dangerous/5243662), [SecurityWeek](https://www.securityweek.com/anthropic-silently-patches-claude-code-sandbox-bypass/)). Defense-in-depth assumes both layers are current and patched — pin to a known-good harness version and treat sandbox CVEs as the same severity tier as classification errors.

## When this backfires

Broad globs trade fatigue for new failure modes:

- Parser-bypass exposure. `Bash(echo *)` assumes the matcher separates the prefix from injected suffixes. [CVE-2025-54795](https://nvd.nist.gov/vuln/detail/CVE-2025-54795) (patched in v1.0.20) and the command-chaining bypass fixed in v1.0.93 show that parser bugs can let a trusted prefix smuggle an untrusted command. Keep Claude Code current and prefer narrow patterns over broad globs.
- Incomplete deny lists. `Bash(cat *)` can read secrets if `deny` misses sensitive paths (dotfiles, `~/.ssh`, vendored credentials). Enumerate them deliberately.
- "Read-only" with side effects. `git status` can trigger filesystem writes via hooks or `fsmonitor` daemons. Classification by command name alone is not enough in foreign repos.
- Scope creep. A glob appropriate in the project root may be dangerous inside a submodule or mounted volume. Review allowlists when the working set changes.

If any of these apply, narrow the patterns, extend `deny`, or keep the action in `ask`.

## What this is not

Allowlisting eliminates noise so that genuine risk prompts stand out; it is not a reduction in oversight. The measure of a well-configured allowlist is whether the prompts that remain reliably signal actions worth reviewing — not how many prompts were suppressed.

## Key Takeaways

- Approval fatigue turns permission prompts into rubber-stamps, creating an illusion of oversight with none of the substance
- Anthropic reports 84% reduction in permission prompts by auto-approving read-only, locally scoped operations ([source](https://www.anthropic.com/engineering/claude-code-sandboxing))
- Claude Code's `allow` / `ask` / `deny` permission rules in `.claude/settings.json` implement allowlisting at the command level
- Classify operations into safe, elevated, and restricted tiers; auto-approve only safe-tier actions
- Pair allowlists with filesystem and network sandbox boundaries so misclassified commands are still contained

## Related

- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Hooks for Enforcement vs Prompts for Guidance](../instructions/hooks-vs-prompts.md)
- [The AI Development Maturity Model](../workflows/ai-development-maturity-model.md)
- [Evidence-Based Allowlist Auto-Discovery for Agents](evidence-based-allowlist-auto-discovery.md)
- [Progressive Autonomy: Scaling Trust with Model Evolution](../human/progressive-autonomy-model-evolution.md)
- [Cognitive Load, AI Fatigue, and Sustainable Agent Use](../human/cognitive-load-ai-fatigue.md)
- [The Bottleneck Migration](../human/bottleneck-migration.md)
- [Suggestion Gating](../human/suggestion-gating.md)
