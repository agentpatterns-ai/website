---
title: "Treating a Model-Judged Hook as a Deterministic Control"
term: "Model-Judged Hook Misread"
description: "Claude Code prompt and agent hooks decide by model judgement, not exit code, so counting them as deterministic enforcement moves a guard back into the layer you left."
aliases:
  - Prompt Hook as Hard Guard
  - Judged Hook Enforcement Gap
tags:
  - anti-pattern
  - claude
  - arxiv
last_reviewed: 2026-10-09
maturity: emerging
---

# Treating a Model-Judged Hook as a Deterministic Control

> A Claude Code `prompt` or `agent` hook returns a model's verdict, not an exit code, so a guard built on one is judged, not enforced.

This page applies to Claude Code. The anti-pattern is to write a `prompt` or `agent` hook, count it as part of the deterministic hook layer, and rely on it as the only control on a boundary that matters. The hook fires and runs, and the model's reading of its wording decides the outcome. Claude Code 2.1.294 shows the exposure: it fixed `prompt` and `agent` hooks "written as instructions (such as "Block commands that...") allowing what they should block" ([Claude Code changelog 2.1.294](https://code.claude.com/docs/en/changelog#2-1-294)).

## Two decision mechanisms

Claude Code has five hook handler types. Command, HTTP, and MCP tool hooks return results through exit codes or the JSON output format. Prompt hooks "send a prompt to a Claude model for single-turn evaluation. The model returns its decision as JSON." Agent hooks "spawn a subagent that can use tools like Read, Grep, and Glob to verify conditions before returning a decision" ([Hooks reference](https://code.claude.com/docs/en/hooks#hook-handler-fields)).

Anthropic's guide draws the same line. Hooks run "at specific points in its lifecycle, which gives you deterministic control", and for decisions that "require judgment rather than deterministic rules" you can use prompt-based or agent-based hooks that "use a Claude model to evaluate conditions" ([Hooks guide](https://code.claude.com/docs/en/hooks-guide)). The claim that a hook cannot be argued with or forgotten holds for the first group only. See [Enforcing Agent Behavior with Hooks](../../instructions/enforcing-agent-behavior-with-hooks.md) for the exit-code contract.

## What the verdict does

A prompt or agent hook answers with an `ok` field, and `ok: true` allows the action ([Hooks reference, response schema](https://code.claude.com/docs/en/hooks#response-schema)). The bullets below describe prompt hooks. Agent hooks have no `continueOnBlock` field and ignore `impossible`; on `ok: false` they act as if `continueOnBlock: true` were set, so on `PreToolUse` the turn continues. Agent hooks are skipped on `PermissionRequest` ([Hooks reference, response schema](https://code.claude.com/docs/en/hooks#response-schema)). What `ok: false` does depends on the event:

- `PreToolUse`: the tool call is denied. By default the turn ends, unless `continueOnBlock: true` returns the reason to Claude as the tool error.
- `PermissionRequest`: `ok: false` has no effect. Denying an approval needs a command hook.
- `PermissionDenied`: `ok: false` has no effect, because the denial already happened.
- `Stop` and `SubagentStop`: the reason becomes Claude's next instruction and the turn continues, unless the response sets `impossible: true`, which lets the turn end.

A prompt hook on `PermissionRequest` therefore looks like a guard and enforces nothing. On `Stop` the polarity inverts, so a wrong verdict decides whether work gets abandoned or the agent keeps looping.

## The 2.1.294 fixes

The same release made a second change: `prompt` hooks on Stop and SubagentStop "written as instructions (such as "Carry on if the build is broken") are judged" better, "so Claude is less likely to stop early" ([changelog](https://code.claude.com/docs/en/changelog#2-1-294)). The wording is "less likely", not fixed.

The reference docs now accept the imperative form: "In a prompt or agent hook, you can write the `prompt` as a rule about what to block or allow, such as "Block any Bash command that reads `.env` files", or as a condition that must hold, such as "All unit tests pass"" ([Hooks reference](https://code.claude.com/docs/en/hooks#prompt-hook-configuration)). On 2.1.294 and later, imperative phrasing is supported. The lesson is that Anthropic changed how the harness judged wording. A hook author cannot see that change coming and cannot pin it.

## Why it fails

The failure comes from the decision path. Claude Code sends the hook prompt and event JSON to a model and acts on the `ok` it returns ([Hooks reference](https://code.claude.com/docs/en/hooks#how-prompt-based-hooks-work)), and model output moves with wording. Format-only changes to a prompt moved accuracy by up to 76 points in one study of open-source models on few-shot tasks ([Sclar et al.](https://arxiv.org/abs/2310.11324v2)). That study did not test Claude or hook judging, so it shows the class of sensitivity, not a rate for hooks.

Anthropic does not say why imperative prompts failed before the fix. One reading is that `ok` asks whether a condition holds, and a command has no truth value to report. That is an inference, not Anthropic's account.

## Writing a judged guard

The guide's Stop example states a condition and spells out the response mapping: "Check if all tasks are complete. If not, respond with {\"ok\": false, \"reason\": \"what remains to be done\"}." ([Hooks guide](https://code.claude.com/docs/en/hooks-guide#prompt-based-hooks)). Follow that shape:

1. State a condition the judge can answer yes or no.
2. Spell out the JSON for each outcome.
3. Set the `model` field. By default the judge uses "the model Claude Code uses for background functionality" ([Hooks reference](https://code.claude.com/docs/en/hooks#prompt-hook-configuration)), and a hook that names a blocked model [runs on the session model](../agent-design/tenant-model-policy.md).
4. Test the hook on the event you attach it to, with inputs that should be blocked.

## When this backfires

Judgement is the right tool for some guards and the wrong one for others.

- Secret reads and destructive commands. In a prompt hook, `$ARGUMENTS` carries tool input the agent wrote, so the judged text is also an injection channel. Gradient-optimized adversarial suffixes (GCG) flipped LLM-judge verdicts in over 30% of attempts on two 3B open-source models in pairwise comparison ([Maloyan et al.](https://arxiv.org/abs/2505.13348v1)). That is the class of risk, not a measured Claude rate. Use a permission rule or command hook for a hard deny.
- Hot paths. A prompt hook on every Bash call adds a model round-trip, with defaults of 30 seconds for prompt hooks and 60 for agent hooks ([Hooks reference](https://code.claude.com/docs/en/hooks#common-fields)). A regex does that check.
- Production reliance on agent hooks. Anthropic says they are experimental and tells production workflows to "prefer command hooks" ([Hooks reference](https://code.claude.com/docs/en/hooks#agent-based-hooks)).
- Older versions. Before 2.1.294, instruction-phrased guards allowed what they named.

Command hooks are not perfectly deterministic either. The `if` filter is best-effort, and Anthropic says to use the permission system for a hard allow or deny ([Hooks reference](https://code.claude.com/docs/en/hooks#bash-if-matching)). Judgement does earn its place where no exit-code test exists, such as whether a Stop turn finished the user's tasks, or intent a pattern match misses. No measured rate of past failures exists, so this page makes no claim about frequency.

## Key Takeaways

- A `prompt` or `agent` hook is judged by a model; only command, HTTP, and MCP tool hooks decide by exit code or JSON output.
- `ok: false` has no effect on `PermissionRequest` or `PermissionDenied`, and Stop hooks invert the polarity.
- 2.1.294 fixed instruction-phrased judging, which shows judged hooks depend on harness version.
- Write the guard as a yes/no condition with an explicit JSON mapping and a pinned `model`.
- Keep hard denies in permission rules or command hooks.

## Related

- [Enforcing Agent Behavior with Hooks](../../instructions/enforcing-agent-behavior-with-hooks.md)
- [Hook Catalog](../../tool-engineering/hook-catalog.md)
- [Policy File Validation](../../instructions/policy-file-validation.md)
- [Tenant Model Policy](../agent-design/tenant-model-policy.md)
