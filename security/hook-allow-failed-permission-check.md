---
title: "Fall Back to the No-Hook Decision When a Permission Check Errors"
term: "No-Hook Fallback"
description: "Since Claude Code 2.1.323, a tool call whose permission check errors after a PreToolUse hook allowed it is decided as if no hook had answered."
tags:
  - security
  - hooks
  - claude
aliases:
  - hook allow after a failed permission check
  - permission check error after a hook allow
last_reviewed: 2026-11-19
maturity: emerging
---

# Fall Back to the No-Hook Decision When a Permission Check Errors

> Since 2.1.323, Claude Code decides a tool call as if no hook had answered when its permission check errors after a PreToolUse hook allowed it.

The change matters where a `PreToolUse` hook allows calls that your rules or permission mode would prompt for or refuse. When the tool's permission check fails with an error, Claude Code 2.1.323 (November 12, 2026) "now decides the call as if no hook had answered" ([changelog 2.1.323](https://code.claude.com/docs/en/changelog#2-1-323)).

## The two rules in 2.1.323

| Case | What Claude Code does now |
|---|---|
| A `PreToolUse` hook returned allow, then the tool's permission check fails with an error | Decides the call as if no hook had answered |
| A `PermissionRequest` hook rewrote the input, then the permission check fails on that input | Asks again, or refuses the call where nobody can answer |

Both lines sit under Changed, and neither describes the earlier behavior ([changelog 2.1.323](https://code.claude.com/docs/en/changelog#2-1-323)). The hooks, permissions, and errors reference pages do not cover the error path yet.

"Where nobody can answer" has a documented meaning. In sessions that cannot show a prompt, such as background subagents in non-interactive mode, Claude Code still runs `PermissionRequest` hooks, "and if no hook returns a decision, it denies the tool call" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#permissionrequest)).

Plan mode already works this way. There, apart from `ExitPlanMode`, a hook's allow has no effect on a call that is not read-only, though Claude Code still applies its `updatedInput`: "You get the same prompt, block, or approval the call would get with no hook" ([permissions](https://code.claude.com/docs/en/permissions#hook-approvals-in-plan-mode)).

## Why it works

A hook allow was never meant to stand alone. "PreToolUse hook decisions don't bypass permission rules," and deny and ask rules run "regardless of what a PreToolUse hook returns" ([permissions](https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods)). The allow skips the prompt, and the check still decides whether a rule applies. A rewritten `PermissionRequest` input gets the same treatment: "The modified input is re-evaluated against deny and ask rules" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control)).

So a call carries two approvals, the hook's and the check's. If the allow stands after the check errors, the call rests on the hook alone, and no deny rule the check never reached gets applied. Checks do fail that way. In 2.1.285, Claude Code fixed the PowerShell tool's permission check "skipping deny and ask rules, and caching that failure for later checks, when its command parser failed to start" ([changelog 2.1.285](https://code.claude.com/docs/en/changelog#2-1-285)).

Saltzer and Schroeder gave the reason for two keys in 1975: held separately, "no single accident, deception, or breach of trust is sufficient to compromise the protected information" ([Saltzer and Schroeder](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html)). An allow that wins after an error is the CWE-636 weakness, where the design falls back "to a state that is less secure than other options that are available" ([CWE-636](https://cwe.mitre.org/data/definitions/636.html)). The no-hook decision is the state your rules and mode already define, so an error grants nothing beyond them.

GitHub Copilot CLI puts errors above an allow too. For a `preToolUse` command hook, "exit 2, crashes, and other non-zero exits all fail-closed and deny the tool call", even when the hook's JSON reports an allow ([GitHub hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)).

## Find the calls this changes

The Claude Code docs name no way to make a permission check error on demand, so test the fallback instead of the error.

1. Run the session's usual calls with hooks off. `--settings '{"disableAllHooks": true}'` turns hooks off for one run ([Claude Code hooks](https://code.claude.com/docs/en/hooks)), so the run shows what the session decides with no hook answering.
2. List every call your hook allows that this run prompts for or refuses. Those are the calls whose outcome can change when the check errors.
3. For each one in a headless job, decide whether a refusal is acceptable. Since 2.1.326, the message in non-interactive runs "names the cause" when a check fails with an error ([changelog 2.1.326](https://code.claude.com/docs/en/changelog#2-1-326)), so the job's output says why the call stopped.

The baseline has three limits. Managed hooks stay on, because `disableAllHooks` set outside managed settings "can't disable those managed hooks" ([Claude Code hooks](https://code.claude.com/docs/en/hooks)). The run shows decisions from a working check. No page documents what an erroring check decides with no hook, so the list marks the calls most at risk, not a full forecast. And `disableAllHooks` also turns off `PermissionRequest` hooks, which run when Claude Code "is about to ask you for permission, or when it would otherwise auto-deny a call that can't prompt" ([Claude Code hooks](https://code.claude.com/docs/en/hooks#permissionrequest-input)), so in sessions that use them the list can over-count.

## When this backfires

- Headless jobs where the hook is the only approver. A check error can end as a refusal, so a harness fault fails the job. GitHub keeps hook timeouts fail-open for this reason: "a slow or unreachable hook must not silently block tool calls or work" ([GitHub hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference)).
- Interactive sessions with high-volume auto-approvals. Each check error can become a prompt. Anthropic warns that prompts lead to "approval fatigue, where people stop paying close attention to what they're approving" ([auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)).
- A hook that checks more than the built-in check does. A team allowlist that inspects the full input can be right where a generic parser crashed, and the change trades its correct allow for a prompt or a refusal.
- A check that answers wrongly without erroring. The rule fires on errors only. A check handed a cut-short input that returns a clean allow is untouched, which [a guard hook approves the truncated input it was handed](../patterns/anti-patterns/guard-approves-truncated-input.md) covers.

## Example

A `PreToolUse` hook that allows a call prints this on exit 0 ([Claude Code hooks](https://code.claude.com/docs/en/hooks#pretooluse-decision-control)):

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "My reason here"
  }
}
```

Claude Code still runs the tool's permission check against your deny and ask rules. If that check finishes, the allow skips the prompt as before. If it fails with an error, 2.1.323 sets the allow aside, and the call gets whatever your rules and mode give it with no hook answering. In a background subagent that cannot show a prompt, Claude Code denies a call that would have prompted, unless a `PermissionRequest` hook decides it ([Claude Code hooks](https://code.claude.com/docs/en/hooks#permissionrequest)).

## Key Takeaways

- Treat a hook allow as a way to skip a prompt, never as the decision itself. After 2.1.323 it counts only when the tool's permission check also finishes.
- Run your usual calls once with hooks off. Any call the hook allows that this run prompts for or refuses is a call a check error can stall or refuse.
- In headless jobs, look for the 2.1.326 permission-check error message before blaming the hook.
- The rule covers errors only. A check that returns a wrong answer cleanly still needs its own guard.

## Related

- [Declaring a Per-Hook Failure Mode for Agent Policy Gates](per-hook-failure-mode.md) — the opposite case, where the hook breaks and the check works.
- [Most-Restrictive-Wins Fusion for Parallel Agent Control Returns](../patterns/agent-design/most-restrictive-wins-fusion.md) — how hook decisions and rules merge when every input answers.
- [Deny-Fallback Permissions for Unattended Agent Runs](../patterns/agent-design/deny-fallback-unattended-permissions.md) — what a prompt turns into on a host with no human.
- [Permission Framework Over Model](permission-framework-over-model.md) — why the harness, not the model or a hook, owns the final decision.
- [A Guard Hook Approves the Truncated Input It Was Handed](../patterns/anti-patterns/guard-approves-truncated-input.md) — the wrong-answer failure this rule does not catch.
- [A PermissionRequest Rewrite Can Move a Command Outside the Sandbox](permissionrequest-rewrite-sandbox-exit.md) — what a rewritten command does when it matches an excluded-command entry.
