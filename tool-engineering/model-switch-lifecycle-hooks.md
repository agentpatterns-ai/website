---
title: "Model-Switch Lifecycle Hooks: Gating a Mid-Session Model Change"
term: "Model-Switch Lifecycle Hooks"
description: "Claude Code v2.1.251 added PreModelSwitch, which can block a requested model switch and receives its re-cache cost estimate first, and PostModelSwitch, which reports the changes nobody requested."
tags:
  - tool-engineering
  - context-engineering
  - cost-performance
  - claude
aliases:
  - PreModelSwitch hook event
  - PostModelSwitch hook event
  - model switch interception
last_reviewed: 2026-09-14
maturity: emerging
---

# Model-Switch Lifecycle Hooks: Gating a Mid-Session Model Change

> `PreModelSwitch` blocks or annotates a requested model switch before it forfeits the prompt cache; `PostModelSwitch` reports the ones nobody requested.

Claude Code v2.1.251 added both events ([changelog](https://code.claude.com/docs/en/changelog#2-1-251)). `PreModelSwitch` "Runs before Claude Code applies a model switch that you or a client requested" and can cancel it; `PostModelSwitch` "Runs after the session's model changes" and cannot ([hooks reference](https://code.claude.com/docs/en/hooks#premodelswitch)). The pre-hook also receives a dollar estimate of what the switch costs, so a policy can be decided rather than guessed.

## When gating beats avoiding

Anthropic's own advice is to sidestep the boundary: "Pick your model and effort level at the top of a session… The fewer changes you make mid-task, the higher your cache hit rate" ([prompt caching](https://code.claude.com/docs/en/prompt-caching#how-the-cache-is-organized)). Where that is available to you, take it. Two cases it does not cover are what the hooks are for.

The first is a policy that must hold across operators who each control their own session. One person staying on Sonnet is a habit; a retired model nobody may select is a rule, and a rule needs an enforcement point. The second is a change you did not request, where the post-hook is the only report you get. One harness describes the gap left when nothing consumes the event: a mid-run switch "does not update the report, it falsifies it" ([miclip/conclave#202](https://github.com/miclip/conclave/issues/202)).

Confirmation, the third advertised verb, partly exists already: interactive `/model` "asks you to confirm the switch only while the cache is still warm" ([prompt caching](https://code.claude.com/docs/en/prompt-caching#switching-models)).

## What each hook sees

The pre-hook fires for five request surfaces: `/model <name>` and the `/model` picker, the `Option+P` or `Alt+P` picker, the Model setting in `/config`, fast mode when it changes the session's model, and an Agent SDK or Remote Control `set_model` or `apply_flag_settings` change ([hooks reference](https://code.claude.com/docs/en/hooks#premodelswitch)). Everything else reaches the post-hook alone, and one case reaches neither.

| Change | `PreModelSwitch` | `PostModelSwitch` |
|---|---|---|
| A switch you or a client requested | Fires | Fires |
| Automatic model fallback | No | Fires, `source: "auto"` |
| Model restored when you resume a session | No | Fires, `source: "resume"` |
| `opusplan` entering or leaving plan mode | No | Fires |
| A fallback-chain model serving one turn | No | No |

The last row is the real limit. "Claude Code doesn't run PostModelSwitch hooks when a model from a fallback model chain serves a turn, because that substitution lasts one turn and leaves the session's model unchanged" ([hooks reference](https://code.claude.com/docs/en/hooks#postmodelswitch)). That turn still forfeits the cache and still runs on a model you did not pick, and neither event reports it. Write the policy as "the harness will not switch on request", never as "this session will never run on model X".

## Why it works

A model switch is session state the harness mutates, so the harness can expose it the way it exposes tool dispatch. What makes a policy decidable here, rather than only observable, is that the price is known before it is paid. The prompt cache is keyed per model: "Each model has its own cache. Switching with `/model` means the next request reads the entire conversation history with no cache hits, even though the content is identical" ([prompt caching](https://code.claude.com/docs/en/prompt-caching#switching-models)). The cost is a function of two things Claude Code already holds at request time, how many tokens the next request re-sends and the target's cache-write rate.

So the pre-hook gets five cost fields rather than an after-the-fact bill: `context_tokens`, `prompt_cache_warm`, `cache_ttl`, `estimated_cache_write_usd`, and `pricing`. They cover "what re-sending the conversation to the new model costs, so a hook can show that figure before the switch happens", and the documented example of `/model opus` from a Sonnet 5 session reports 182,340 context tokens and an estimated `$1.1396` cache write ([hooks reference](https://code.claude.com/docs/en/hooks#premodelswitch-input)). A `PreToolUse` hook sees arguments it cannot price. This one sees a number.

## Deciding at the boundary

Exit 2 or `decision: "block"` cancels the switch; `hookSpecificOutput.permissionDecision` accepts `"allow"`, `"deny"`, and `"ask"`, resolved `deny` > `ask` > `allow` across several hooks. `systemMessage` is shown whatever the decision, so an annotate-only hook returns one and exits 0 ([hooks reference](https://code.claude.com/docs/en/hooks#premodelswitch-decision-control)).

Two defaults invert `PreToolUse`, which is what makes a ported `PreToolUse` script wrong here. Not answering in time blocks: "A PreModelSwitch hook that doesn't respond before its timeout blocks the switch. On PreToolUse, by contrast, a timed-out command hook lets the tool call continue." The budget is 30 seconds, not the usual 600. Crashing does the opposite: "A hook that exits with a code other than 0 or 2 and prints no JSON decision doesn't block: Claude Code shows its stderr and applies the switch" ([hooks reference](https://code.claude.com/docs/en/hooks#premodelswitch-decision-control)).

## Example

A `PreModelSwitch` hook that reports the re-cache cost and denies a switch above a threshold. It reads `to_model` rather than trusting the matcher, because an unresolvable canonical name makes Claude Code "run every PreModelSwitch hook regardless of matcher" ([hooks reference](https://code.claude.com/docs/en/hooks#premodelswitch)). It also declines to enforce the threshold when `pricing` is `"default"`, the value reported when `to_model` has no known price.

```json
{
  "hooks": {
    "PreModelSwitch": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/price-model-switch.sh"
          }
        ]
      }
    ]
  }
}
```

`.claude/hooks/price-model-switch.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

CEILING=2.00

jq --argjson ceiling "$CEILING" '
  if .pricing == "default" then
    # A guessed rate is no basis for a deny. Report it and step aside.
    {systemMessage: "Switch to \(.to_model) re-sends \(.context_tokens) tokens; no price on file."}
  elif .estimated_cache_write_usd > $ceiling then
    {hookSpecificOutput: {
       hookEventName: "PreModelSwitch",
       permissionDecision: "deny",
       permissionDecisionReason:
         "Switch to \(.to_model) re-caches \(.context_tokens) tokens for about $\(.estimated_cache_write_usd), over the $\($ceiling) ceiling."}}
  else
    {systemMessage: "Switch to \(.to_model): \(.context_tokens) tokens, about $\(.estimated_cache_write_usd) to re-cache."}
  end'
```

One `jq` invocation reads the payload, compares the estimate as a JSON number, and emits the decision, so the hook spawns a single process inside its 30-second budget. Its exit status is the script's, which keeps a malformed payload exiting non-zero rather than 2, and a non-zero, non-2 exit applies the switch instead of reading as a deliberate block.

## When this backfires

- An `"ask"` policy shipped to headless runs is a deny. "Only `/model` in an interactive session can show the `"ask"` prompt. On every other surface, including non-interactive mode with the `-p` flag, `/config`, and `set_model` requests, Claude Code treats `"ask"` as a refusal" ([hooks reference](https://code.claude.com/docs/en/hooks#premodelswitch-decision-control)). A confirm hook tested in a terminal blocks every CI runner.
- A dollar gate can rest on a placeholder. `estimated_cache_write_usd` is explicitly an estimate, "The server may not need to re-cache the whole context", and `pricing` returns `"default"` when the target has no known price. `context_tokens` is `0` before the first response, so a threshold passes trivially on turn one ([hooks reference](https://code.claude.com/docs/en/hooks#premodelswitch-input)).
- A hook that calls the network can block a switch by being slow. Exceeding the 30-second budget cancels the switch rather than allowing it.
- `PostModelSwitch` guidance is best-effort. Unfinished within five seconds of the next prompt, its output moves to the request after; several switches before that request collapse to the last target model only ([hooks reference](https://code.claude.com/docs/en/hooks#postmodelswitch-decision-control)).
- Gating the switch does not make the switch a good idea. On the Claude pair studied in [The Handoff Tax](../context-engineering/handoff-tax-model-switch-context.md), every mid-task escalation interface cost more than running the strong model throughout on easy and medium tasks. Below a handful of turns the forfeited prefix is small enough that the wiring is the larger cost.

## Key Takeaways

- `PreModelSwitch` covers requested switches only. Automatic fallback and resume-restore reach `PostModelSwitch`, and a fallback-chain turn reaches neither, so no hook can promise a session never runs on a given model.
- The pre-hook receives `context_tokens` and `estimated_cache_write_usd` before the switch, which is what lets a cost policy be enforced instead of reconstructed from a bill.
- Timeout blocks, crash allows. Both are the reverse of `PreToolUse`, and the budget here is 30 seconds.
- Check `to_model` in the script. The matcher runs every hook when the target's canonical name cannot be resolved, which is the case for a gateway-only model ID.
- Use `"ask"` only where an interactive `/model` is the sole entry point; everywhere else it is read as a refusal.

## Related

- [The Handoff Tax: What a Receiving Model Should Inherit](../context-engineering/handoff-tax-model-switch-context.md) — what should cross the boundary this page lets you stand on
- [Mid-Session Config Changes as Invisible Cache Invalidators](../patterns/anti-patterns/mid-session-config-cache-invalidators.md) — the cost these hooks let you quote, and the avoidance rule that is cheaper when it is available
- [PreCompact Hook: Vetoing Compaction at Lifecycle Boundaries](precompact-hook-compaction-veto.md) — the same veto shape on the compaction boundary, where an indefinite block exhausts the window
- [Effort-Aware Hooks: Reading the Reasoning Tier from PreToolUse and PostToolUse](effort-aware-hooks.md) — the other half of the session's cache key, exposed to hooks as a signal rather than a gate
- [Claude Code Hooks](../tools/claude/hooks-lifecycle.md) — the event catalog and matcher semantics these two events inherit
