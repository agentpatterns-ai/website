---
title: "Parameter-Level Permission Rules (Tool(param:value) Syntax)"
description: "Claude Code permission rules can match a tool's input-parameter values, not just the tool name — for example Agent(model:opus) to block Opus subagents — moving least-privilege control below the tool-name layer."
tags:
  - claude
  - security
  - agent-design
aliases:
  - Tool(param:value) syntax
  - parameter-level permission rules
  - Agent(model:opus) rule
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-28
status: current
---

# Parameter-Level Permission Rules

> Permission rules can match on a tool's input-parameter values, not just the tool name — `Agent(model:opus)` blocks Opus subagents while leaving the Agent tool available.

Claude Code v2.1.178 (2026-06-15) added `Tool(param:value)` syntax for permission rules that match a tool's input parameters, with `*` wildcard support: *"Added `Tool(param:value)` syntax for permission rules to match a tool's input parameters (with `*` wildcard), e.g. `Agent(model:opus)` to block Opus subagents"* ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). The rule fires when Claude calls the tool with that parameter set to that exact value, before the deny-then-ask-then-allow precedence resolves. Coarse tool-name allow/deny lists previously forced an all-or-nothing choice; parameter-level matching forbids a single expensive or dangerous argument value while keeping the tool available.

## Syntax and Matching Semantics

Each rule names one tool, one top-level parameter, and one value (or wildcard) ([Configure permissions](https://code.claude.com/docs/en/permissions)):

| Rule                           | Matches                                      |
|--------------------------------|----------------------------------------------|
| `Agent(model:opus)`            | Agent calls that request the Opus model tier |
| `Agent(isolation:worktree)`    | Agent calls that request a git worktree      |
| `Bash(run_in_background:true)` | Bash calls that run in the background        |

The matching rules are tight ([Configure permissions](https://code.claude.com/docs/en/permissions)):

- The parameter must be a direct field of the tool's input. Fields nested inside an object or array are not matchable.
- Each rule names one parameter. Gating on both `model` and `isolation` requires two separate rules.
- `*` matches any sequence of characters, so `Agent(isolation:*)` matches any explicit `isolation` value. Without `*` the match is exact.
- A parameter the model omits is never matched — `Agent(model:*)` does not match a call that leaves `model` unset.
- The value is compared against the literal input Claude sends, before normalization. `Agent(model:opus)` matches the alias `opus` but not the canonical ID like `claude-opus-4-7`. `--verbose` shows the exact parameter names and values per call.
- Whitespace around the colon is ignored.

## Deny and Ask Only

Parameter-level matching applies to deny and ask rules only. Allow rules continue to use each tool's own specifier syntax. The documented reason: *"An allow rule for one parameter value wouldn't establish that the call is safe overall"* ([Configure permissions](https://code.claude.com/docs/en/permissions)). One safe parameter does not certify the rest of the call; the existing per-tool specifier — which can encode the full safety story — remains required for allow.

The rules compose with the standard deny-first precedence: *"Rules are evaluated in order: deny, then ask, then allow. The first match in that order determines the outcome"* ([Configure permissions](https://code.claude.com/docs/en/permissions)). A `Tool(param:value)` deny match wins over any allow rule covering the same call. A `Tool(param:value)` ask match still prompts even when a more specific allow rule would otherwise auto-approve.

## Canonicalized-Field Exclusion

Fields that a tool already matches with its own canonicalizing rules are not matchable via `param:` — Claude Code ignores the rule and emits a startup warning ([Configure permissions](https://code.claude.com/docs/en/permissions)):

| Tool                  | Excluded parameter | Use this instead         |
|-----------------------|--------------------|--------------------------|
| Bash, PowerShell      | `command`          | `Bash(rm *)`             |
| Read, Edit, Write     | `file_path`        | `Read(./path)`           |
| Grep, Glob            | `path`             | `Grep(./src/**)`         |
| NotebookEdit          | `notebook_path`    | `NotebookEdit(./nb.ipynb)` |
| WebFetch              | `url`              | `WebFetch(domain:host)`  |

The exclusion exists because a literal-string rule against a compound argument is bypassable. A `Bash(command:rm *)` rule would let `rm -rf / && echo done` slip through as a compound command. The tool's own canonicalizing matcher (Bash's compound-command parser, WebFetch's hostname extractor, Read/Edit's gitignore-style path matcher) sees through those tricks; the parameter matcher would not.

## Why It Works

The comparison happens on the literal scalar input the model emits, before the tool executes — so the harness can enforce policy without running the call, and without inventing a new approval pathway ([Configure permissions](https://code.claude.com/docs/en/permissions)). Deny rules block; ask rules prompt; the existing deny-then-ask-then-allow precedence is preserved. Because matching one parameter does not establish overall call safety, the design restricts the syntax to deny/ask and keeps each tool's full specifier as the allow-side surface. This is what makes parameter-level rules a finer-grained least-privilege primitive that layers cleanly over the existing tool-name rules — they can only subtract from what a tool may do, never widen it.

For subagent cost control, the architectural fit is direct. By default, subagents inherit the parent session's model, so an Opus-tier session spawns Opus-tier subagents for tasks Haiku could handle, and the price delta between Opus 4.7 and Haiku 4.5 is not visible to the model ([Automation Labs, 2026-06](https://medium.com/@automation.labs/claude-code-can-now-block-opus-subagents-set-these-4-limits-3a7794d52587)). `Agent(model:opus)` in `deny` enforces the cost ceiling at the harness, not at every agent definition.

## When This Backfires

- Omitted-parameter blind spot. A model that simply omits the gated parameter sidesteps the rule. `Agent(model:*)` does not match an Agent call with no `model` set, which dispatches under the default. Pair parameter rules with a tool-level fallback when "no rule applies" must mean deny ([Configure permissions](https://code.claude.com/docs/en/permissions)).
- Alias vs canonical-ID coverage. `Agent(model:opus)` matches the alias `opus` but not the canonical ID `claude-opus-4-7`, and vice versa. A rule author who only writes one form lets the other through. Write both, or use a substring wildcard like `Agent(model:*opus*)` ([Configure permissions](https://code.claude.com/docs/en/permissions)).
- Nested-field opacity. Object- and array-nested parameters cannot be matched. A tool whose risky configuration lives inside a structured payload — a JSON config blob, an array of subcommands — is unreachable by `Tool(param:value)`. For those, either a PreToolUse hook that reads the full input or a tool-level deny is the right layer.
- Canonicalized-field rules silently no-op. A `Bash(command:rm *)`-shaped rule is ignored with a startup warning. Confirm rules apply by running `claude --verbose` and watching the merged permission set — do not assume a rule landed because the config parsed.
- Convenience confused with a guarantee. For compliance-grade enforcement, [`permissions.deny`](https://code.claude.com/docs/en/permissions) at the whole-tool level, or a [PreToolUse hook](https://code.claude.com/docs/en/hooks) reading the full input payload, is the durable layer. `Tool(param:value)` is a least-privilege primitive that layers over them — not a substitute.

## Example

A team running Claude Code with Opus 4.7 for the main thread wants to keep subagents on a cheaper tier without editing every subagent definition. They also want any Agent call that spawns into a worktree to prompt, since worktree-isolated agents can edit files — but in-place agents (read-only) should pass.

In project-level managed settings:

```json
{
  "permissions": {
    "deny": [
      "Agent(model:opus)"
    ],
    "ask": [
      "Agent(isolation:worktree)"
    ]
  }
}
```

The deny rule applies even when a developer's local `allow` list contains `Agent` — deny-first precedence wins. The ask rule prompts before any worktree-isolated subagent dispatches, regardless of which subagent is invoked. Because the rules name one parameter each, they compose: an Opus-tier worktree-isolated call hits the deny first and blocks; a Sonnet-tier worktree-isolated call hits the ask and prompts; a Sonnet-tier in-place call passes silently.

What this does not catch: an Agent call that omits `model` entirely, which would dispatch under whatever default the parent session inherits. To close that gap, pair the rule with subagent YAML pinning the model explicitly, or move to a PreToolUse hook that inspects every Agent call.

## Key Takeaways

- `Tool(param:value)` (Claude Code v2.1.178, 2026-06-15) matches deny and ask rules against a tool's top-level scalar input parameters, with `*` wildcard support
- Allow rules cannot use this syntax — one parameter does not certify the rest of the call
- Canonicalized fields (`command`, `file_path`, `path`, `notebook_path`, `url`) are excluded to prevent bypass via compound arguments; use the tool's own specifier instead
- Omitted parameters and alias-vs-canonical-ID values are the two common rule-coverage gaps — write rules for both forms or pair with a tool-level fallback
- Layer parameter-level rules over `permissions.deny` and PreToolUse hooks for compliance-grade enforcement — they are a least-privilege primitive, not a substitute

## Related

- [Hard-Deny Classifier Rule](hard-deny-classifier-rule.md) — Unconditional block layer inside auto mode's classifier, complementary to deterministic parameter-level rules
- [Skill disallowed-tools Frontmatter](skill-disallowed-tools.md) — Skill-layer tool denial: removes tools from the model's pool while a skill is active
- [Sub-Agents](sub-agents.md) — How Agent tool calls dispatch, inherit model and isolation, and which parameters parameter-level rules see
- [Managed Settings Drop-In Directory](managed-settings-drop-in.md) — Deploying organization-wide permission rules that user and project settings cannot override
- [Classifier-Gated Auto-Permission](../../patterns/agent-design/classifier-gated-auto-permission.md) — Permission-relay pattern at the classifier layer, distinct from the deterministic rule layer
