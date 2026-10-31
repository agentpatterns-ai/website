---
title: "Approver-Named Permission Answers"
term: "Approver-Named Permission Answer"
description: "A permission gate can answer with who may approve a call rather than what the verdict is, so only the permission dialog or a host callback can approve, and the call is refused where nobody can be asked."
tags:
  - agent-design
  - automation
  - hooks
  - claude
aliases:
  - naming the decider in a permission answer
  - person-only approval answer
  - decider person tool.check
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-22
maturity: emerging
status: current
---

# Approver-Named Permission Answers

> A permission gate names its approver, the dialog or a host callback, and refuses the call where nobody can be asked.

Reach for this when the gated call set is computed rather than enumerable. The same gate must work on a laptop and in an unattended run. Where you can write the pattern down, a managed `ask` rule is the stronger control: Claude Code "doesn't auto-approve the following in any mode, including `bypassPermissions`", and explicit ask rules head that list ([Choose a permission mode](https://code.claude.com/docs/en/permission-modes#actions-no-mode-auto-approves)).

Claude Code 2.1.304 added the answer on 19 October 2026: "Added `decider: \"person\"` to a mod's `tool.check` answer: only the permission dialog or a host's callback can approve the ask, and it is refused with the mod's reason where nobody can be asked" ([changelog 2.1.304](https://code.claude.com/docs/en/changelog#2-1-304)). A separate fix in that release concerns scheduled Cowork cloud sessions "waiting five minutes again for each subagent whose WebFetch needed a URL approval that nobody was there to give".

## What the verdict could not say

The documented `tool.check` answer is an outcome: `{ decision }` set to `allow`, `ask`, or `deny`, with an optional `reason` ([mods reference](https://code.claude.com/docs/en/plugins/mods/reference)). Returning `ask` buys less than it reads like, because `tool.check` fires "after the `PreToolUse` hooks run, and before the permission prompt, auto mode's classifier, or a `PermissionRequest` hook" ([mods events](https://code.claude.com/docs/en/plugins/mods/events#approve-or-refuse-a-tool-call-before-the-user-is-asked)). The `.d.ts` comment says `ask` goes to "the mode's decider (the dialog, the auto-mode classifier, a headless host)" ([claude-code.d.ts](https://github.com/anthropics/claude-code/blob/main/mods/types/claude-code.d.ts)). In auto mode it goes onward, because apart from critical-path removals "Everything else goes to the classifier" ([Choose a permission mode](https://code.claude.com/docs/en/permission-modes#how-the-classifier-evaluates-actions)). In modes that ask, "a `PermissionRequest` hook can answer the prompt" ([Choose a permission mode](https://code.claude.com/docs/en/permission-modes#critical-path-removals-in-each-permission-mode)). And under a permission host, absent `--permission-prompts none`, "your run waits for that host to answer each permission request" ([Run Claude Code programmatically](https://code.claude.com/docs/en/headless#turn-off-permission-prompts-in-unattended-runs)).

The fetched `ToolCheckResult` definition already includes `decider`, with `host` as its value and a comment about who receives an ask ([claude-code.d.ts](https://github.com/anthropics/claude-code/blob/main/mods/types/claude-code.d.ts)). The 2.1.304 changelog adds the mod-supplied `person` value.

## Why it works

The `.d.ts` comment says `ask` "puts it to the mode's decider" ([claude-code.d.ts](https://github.com/anthropics/claude-code/blob/main/mods/types/claude-code.d.ts)). Naming `person` narrows that decider to the dialog or a host's callback ([changelog 2.1.304](https://code.claude.com/docs/en/changelog#2-1-304)).

`AskUserQuestion` and MCP tools marked `requiresUserInteraction` already require interaction. A mod approval cannot skip their prompt ([permissions](https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods)). The new answer applies a dialog-or-host-only requirement per call.

## The read-only field, and its two traps

The same release added `e.isReadOnly`, "set when the tool call is read-only" ([changelog 2.1.304](https://code.claude.com/docs/en/changelog#2-1-304)), so a gate can reserve the person-only answer for calls that change something. Two traps sit in that filter. The field "is `true` when the tool reports the call as read-only. Otherwise the field is absent, not `false`". Thus, `isReadOnly: false` in a matcher means the hook never runs ([mods events](https://code.claude.com/docs/en/plugins/mods/events#check-whether-a-tool-call-is-read-only)). The value is self-reported: "WebFetch and Agent calls report as read-only, though WebFetch requests a URL and Agent starts a subagent that runs tools of its own".

## When this backfires

- A mod is not an enforcement point. Without managed settings or a Team or Enterprise login, "a mod can approve a call that an `ask` rule would prompt for, or that your `PreToolUse` hook blocked" ([Mods overview](https://code.claude.com/docs/en/plugins/mods/overview)). A surface that can widen permissions is a weak place to narrow them; [Claude Code mods](../../tools/claude/mods.md) carries the full trust posture.
- An earlier mod can skip the hook. "The first mod is outermost" ([mods events](https://code.claude.com/docs/en/plugins/mods/events#the-order-mods-run-in)), which is where the built-in guard and `prependPlugins` mods sit. 2.1.304 adds "a transcript line when a plugin that runs first skips one of your mod's hooks" ([changelog 2.1.304](https://code.claude.com/docs/en/changelog#2-1-304)), reporting the skip rather than preventing it.
- A refusal does not document the rest of the run. The changelog specifies refusal with the mod's reason, without a run-halting guarantee ([changelog](https://code.claude.com/docs/en/changelog#2-1-304)). Verify completion separately.
- A broad gate can raise prompt volume where a person can answer. This is an inference, not a measured figure.
- The v2.1.304 changelog adds the `person` value and `e.isReadOnly`. The fetched typings cap `ToolCheckDecider` at `host`. The reference documents `{ decision }` and `reason`. The permission-modes page says a `PermissionRequest` hook can answer the prompt in modes that ask, but no fetched source says whether that holds for an ask that names `person`. Check the `.d.ts` files a local load writes into the mod's directory ([mods reference](https://code.claude.com/docs/en/plugins/mods/reference)).

## Example

Anthropic's own `tool.check` example sends every `mcp__github__` call that is not read-only to an `ask` ([mods events](https://code.claude.com/docs/en/plugins/mods/events#check-whether-a-tool-call-is-read-only)).

**Before** — the answer names the outcome:

```javascript
on('tool.check', { tool: /^mcp__github__/ }, async ($, e, next) => {
  const decided = await next(e)
  // Read-only calls and denied calls pass through unchanged
  if (e.isReadOnly || decided.decision === 'deny') return decided
  return { decision: 'ask', reason: 'This tool can change the GitHub repository' }
})
```

That hook is right on a laptop and ambiguous in a scheduled run, where the configured permission route can settle the ask.

**After** — the answer names the approver. `decider` sits beside `decision` and `reason` on `ToolCheckResult` ([claude-code.d.ts](https://github.com/anthropics/claude-code/blob/main/mods/types/claude-code.d.ts)), and 2.1.304 adds `person` to its values:

```javascript
return {
  decision: 'ask',
  reason: 'This tool can change the GitHub repository',
  decider: 'person',
}
```

The dialog still appears for a developer. Where nobody can approve, the run refuses the write with the mod's reason. The hook needs no unattended-mode branch.

## Key Takeaways

- Decide between this and a managed `ask` rule on one question: can you write the gated calls down? If yes, the rule wins, because no mode auto-approves it and it needs nothing loaded.
- Audit an existing gate by grepping its hooks for environment tests: a check on `claude -p`, a TTY probe, or a CI variable is the branch this answer replaces.
- Narrow with `e.isReadOnly` in the hook body, never with `isReadOnly: false` in a matcher, and do not read WebFetch or Agent as harmless because they self-report read-only.
- Treat this as a fail-closed default, not a boundary. Put anything that has to hold in a managed deny or ask rule, and read the transcript for the shadowing line when a gate you expected never fired.
- Check the actual denial record before depending on it. With `--output-format stream-json`, the headless documentation describes `permission_denied` system messages and a `permission_denials` list for `--permission-prompts none`, not for mod refusals ([headless documentation](https://code.claude.com/docs/en/headless#turn-off-permission-prompts-in-unattended-runs)).

## Related

- [Six-Shape Approval Response Taxonomy](approval-response-taxonomy.md) — the six outcome-shaped answers a host's `canUseTool` callback can return; this answer names who may approve instead of the outcome, and that callback is one of its two allowed approvers, so it is not a seventh shape
- [Deny-Fallback Permissions for Unattended Agent Runs](deny-fallback-unattended-permissions.md) — the run-level counterpart an operator sets at launch; it never fires on a call the classifier approves, which is what an approver-named answer changes
- [Deferred Permission Pattern](deferred-permission-pattern.md) — the opposite assumption, where the session pauses and waits because a human will come back to answer
- [Classifier-Gated Auto-Permission](classifier-gated-auto-permission.md) — the branch that would otherwise settle the ask, and its measured error rates
- [Most-Restrictive-Wins Fusion](most-restrictive-wins-fusion.md) — how competing control returns merge into one verdict before any of this reaches a prompt
- [Claude Code Mods and When to Use One Instead of a Hook](../../tools/claude/mods.md) — the surface this answer lives in, including the `ceiling` and `agentId` fields added to the same event
