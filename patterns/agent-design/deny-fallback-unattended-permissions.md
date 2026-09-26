---
title: "Deny-Fallback Permissions for Unattended Agent Runs"
term: "Deny-Fallback Permissions"
description: "Deny whatever would have reached a permission prompt on a host with no human, while the permission mode and rules keep deciding every other call."
tags:
  - agent-design
  - automation
  - security
  - claude
aliases:
  - deny-fallback permission posture
  - permission prompts none
  - unattended permission fallback
applies_to: "claude-code@2.x"
last_reviewed: 2026-09-14
maturity: emerging
status: current
---

# Deny-Fallback Permissions for Unattended Agent Runs

> In an unattended run, Claude Code denies whatever would have reached a permission prompt, while the permission mode keeps deciding every other call.

Claude Code v2.1.259 added `--permission-prompts none`: "anything that would prompt is denied automatically while the active permission mode (including auto mode) keeps deciding" ([Claude Code changelog 2.1.259](https://code.claude.com/docs/en/changelog#2-1-259)). The flag sits beside the permission mode rather than replacing one. It takes two values, `host` and `none`, and applies to print mode only ([CLI reference](https://code.claude.com/docs/en/cli-reference)).

## When the fallback earns its place

Three conditions decide whether this buys you anything.

Your run has a permission host. Anthropic is explicit about where the flag bites: "The flag matters most when your run has a permission host: an Agent SDK app with a `canUseTool` callback, or an MCP tool you pass with `--permission-prompt-tool`. Without the flag, your run waits for that host to answer each permission request." ([Run Claude Code programmatically](https://code.claude.com/docs/en/headless)) A plain `-p` run with no host already denied those requests before the flag shipped, so there it adds only the no-retry instruction and the tool removal below.

You want to keep a mode you would otherwise trade away. `dontAsk` already denies the unanswerable and predates the flag: "If you set `dontAsk` mode, Claude Code auto-denies every tool call that would otherwise prompt you" ([Choose a permission mode](https://code.claude.com/docs/en/permission-modes)). But a mode is one value. If you want [auto mode's classifier](classifier-gated-auto-permission.md) deciding the middle of the range and still cannot afford a hang, only the flag gives you both.

The host runs v2.1.259 or later. Earlier versions "reject it with an unknown-option error" ([headless guide](https://code.claude.com/docs/en/headless)).

## What it changes, and what it leaves alone

Upstream decisions are untouched: "Permission rules, `PermissionRequest` hooks, and the permission mode you set still decide every call first; Claude Code denies only the requests that nothing else resolves" ([headless guide](https://code.claude.com/docs/en/headless)).

Two behaviors change beyond the denial. "With `--permission-prompts none`, Claude Code removes the tools that need an answer from a person, such as `AskUserQuestion`, so Claude can't call them. Any MCP elicitation request that no `Elicitation` hook answers is cancelled." ([headless guide](https://code.claude.com/docs/en/headless))

The third change is the one most often read backwards. The denial does not stop the job. Claude "is told that nobody can approve the request and not to retry it, and the run continues" ([headless guide](https://code.claude.com/docs/en/headless)). Anthropic reports the same outcome for auto mode's own repeated-block threshold in a non-interactive run: "the action doesn't run and Claude keeps working" ([Choose a permission mode](https://code.claude.com/docs/en/permission-modes)). The action fails closed. The run does not.

## Why it works

Permission decisions run as an ordered pipeline, and the flag substitutes only its last branch. Anthropic states the order: rules resolve first, then read-only actions and in-working-directory edits auto-approve, then "everything else goes to the classifier" ([Choose a permission mode](https://code.claude.com/docs/en/permission-modes)). The prompt is what is left when none of those settle the call. Swapping ask for deny at that terminal branch leaves every upstream decision intact. That is why the fallback composes with a mode instead of consuming one.

That same property makes the residue legible: whatever reaches the fallback is exactly what your policy could not settle.

## The denial list is a configuration input

Claude Code hands that residue back in a parseable form. "With `--output-format stream-json`, denials appear as `permission_denied` system messages, and the final result message lists them in `permission_denials`" ([headless guide](https://code.claude.com/docs/en/headless)). Anthropic wires denials into a configuration loop, listing "Review denials so you know what to add next" and directing a repeatedly blocked destination into `autoMode.environment` or an allow rule ([Configure auto mode](https://code.claude.com/docs/en/auto-mode-config)). Read the list before you widen anything, and you grant the permissions the workload reached for rather than the ones you guessed at.

## When this backfires

- The task has no alternative route. After a classifier block, Claude "receives the reason and tries an alternative" ([Choose a permission mode](https://code.claude.com/docs/en/permission-modes)), and after a fallback denial it is told not to retry. A deploy or a migration has none, so the run finishes having skipped what you scheduled it for.
- Nobody parses the denial record. Anthropic documents `permission_denials` for `--output-format stream-json` runs. A cron job emitting plain text into a log gets no structured list.
- The task is under-specified. With `AskUserQuestion` removed, an agent that should have asked a clarifying question guesses instead.
- The allowlist was enumerable all along. Where the action set is small and stable, `dontAsk` with explicit `--allowedTools` carries no version floor and one fewer moving part.
- You expected this to harden auto mode. It narrows the ask branch, not the approve branch, so whatever the classifier wrongly approves it still approves ([Classifier-Gated Auto-Permission](classifier-gated-auto-permission.md) carries the measured error rates).
- A mixed-version fleet. A scheduler that passes the flag uniformly fails to start on every host below v2.1.259.

## Example

Anthropic's own unattended invocation keeps the classifier and changes only the fallback:

```bash
claude -p "Update the dependency pins and run the tests" \
  --permission-mode auto --permission-prompts none
```

The classifier reviews each action as usual, and Claude Code denies anything that would have fallen back to a prompt ([headless guide](https://code.claude.com/docs/en/headless)).

The locked-down alternative spends the mode to get the same denial:

```bash
claude -p "run the test suite" \
  --permission-mode dontAsk --allowedTools "Bash(npm test)" "Read"
```

Here nothing outside the allowlist and the read-only set runs at all ([Choose a permission mode](https://code.claude.com/docs/en/permission-modes)). Take `dontAsk` when you can write the allowlist, and the fallback flag when you cannot.

## Key Takeaways

- Treat the fallback as an axis orthogonal to the permission mode. The choice is which branch resolves the unanswerable case, not which mode you run.
- Budget for silent partial completion rather than a halt. The denied action stops, the run finishes and reports, so the caller has to check `permission_denials` to learn what was skipped.
- Set `--output-format stream-json` on any unattended run using the flag. Plain text output carries no structured denial record.
- Reach for `dontAsk` first. The flag pays only when you need a mode's decisions and cannot tolerate a wait.
- Pin the host version. A fleet below v2.1.259 fails on the flag rather than degrading past it.

## Related

- [Deferred Permission Pattern](deferred-permission-pattern.md) — the opposite assumption: pause and serialize the session because a human will come back to answer
- [Classifier-Gated Auto-Permission](classifier-gated-auto-permission.md) — the mode that keeps deciding underneath the fallback, and its measured error rates
- [Most-Restrictive-Wins Fusion](most-restrictive-wins-fusion.md) — how competing control returns merge before any of this reaches a prompt
- [Ask-Everything Permission Policies Protect Less than Per-Action Approval](../anti-patterns/ask-everything-permission-policies.md) — why a policy that resolves to ask protects less than one that settles
- [bypassPermissions Silently Overrides allowedTools](../anti-patterns/bypass-permissions-overrides-allowlist.md) — the widening failure this posture exists to avoid
- [Headless Claude Code in CI](../../workflows/headless-claude-ci.md) — the surrounding non-interactive run this flag configures
