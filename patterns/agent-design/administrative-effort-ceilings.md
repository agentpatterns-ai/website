---
title: "Administrative Effort Ceilings for Reasoning Budget"
term: "Administrative Effort Ceiling"
description: "The maxEffortLevel cap bounds every operator effort control. Caps compose by minimum across settings scopes, and the clamp is silent in headless runs."
tags:
  - agent-design
  - cost-performance
  - claude
aliases:
  - administrative reasoning effort cap
  - maximum effort level setting
  - organization effort limit
applies_to: "claude-code@2.x"
last_reviewed: 2026-09-14
status: current
maturity: emerging
---

# Administrative Effort Ceilings for Reasoning Budget

> An administrative effort ceiling caps reasoning effort above every operator control, so a higher request runs at the cap instead of being refused.

Set an effort ceiling when the levels you remove are ones your workload does not need. Claude Code shipped the control in v2.1.267 on 9 September 2026 ([changelog](https://code.claude.com/docs/en/changelog#2-1-267)). `maxEffortLevel` caps the effort level a session can use, and any higher level "runs at the cap instead, including one from `/effort`, the `/model` picker, `--effort`, `CLAUDE_CODE_EFFORT_LEVEL`, a skill's or subagent's `effort` frontmatter, or the model's own default" ([settings reference](https://code.claude.com/docs/en/settings-reference#maxeffortlevel)). Where task difficulty varies widely, the ceiling takes depth the work needed, and an unattended run gets no warning.

## What makes it a ceiling rather than a default

Claude Code resolves a session's effort from an explicit choice (`CLAUDE_CODE_EFFORT_LEVEL`, `--effort`, or `/effort`), then a held model default, then your saved settings, then the model's own default ([model configuration](https://code.claude.com/docs/en/model-config#adjust-effort-level)). Every entry in that chain is a preference, and a higher-precedence source replaces a lower one.

`maxEffortLevel` does not join the chain. It composes by minimum: "When several scopes set a cap, the lowest applies, so a cap set in one scope can't be raised from another" ([settings reference](https://code.claude.com/docs/en/settings-reference#maxeffortlevel)). That sentence is the whole distinction, and it is the merge rule behind [most-restrictive-wins fusion](most-restrictive-wins-fusion.md) applied to a scalar. An organization that deploys the key in managed settings gets a bound no user file can lift. A developer who sets it in `~/.claude/settings.json` binds themselves on identical terms.

## Why it works

The clamp runs in the client. Claude Code "applies the cap itself before each request, so it holds on every provider, including Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry" ([settings reference](https://code.claude.com/docs/en/settings-reference#maxeffortlevel)). Enforcing before the request is what makes the cap portable, and it is the difference between the two routes an organization has. Per-role effort limits are a Claude Enterprise feature delivered from the server, while `maxEffortLevel` applies on any plan and any provider and caps effort on the client ([model configuration](https://code.claude.com/docs/en/model-config#organization-effort-limits)). Where both reach the same model, "the lower cap applies".

## When this backfires

- The workload needs the tier you cut. On GameEngineBench's C++ runtime tasks, "Increasing reasoning effort from medium to high to xhigh raises pass@1 from 9.1% to 19.1% to 29.1%" ([GameEngineBench](https://arxiv.org/abs/2607.03525v2)). A ceiling at medium buys that 20-point gap on work of that shape.
- Nobody reads the warning. Interactive sessions and plain-text `--print` runs get a warning naming the requested and applied levels, but "with `json` or `stream-json` output or in background agents, the clamp applies silently" ([model configuration](https://code.claude.com/docs/en/model-config#organization-effort-limits)). Unattended runs are the case least able to notice and the one told least.
- The cap removes more than depth. A cap below `xhigh` makes ultracode unavailable: "the session runs at the cap instead and ultracode stays off. Claude then doesn't plan workflows on its own" ([settings reference](https://code.claude.com/docs/en/settings-reference#ultracode)).
- Effort was not the binding constraint. Capping to curb overthinking assumes effort drives the behavior you dislike. On FixedBench, correct-abstention across four effort levels moved from 61.5% to 65.8%, a change "notably smaller than the confidence intervals of ∼±7.0%" ([Coding Agents Don't Know When to Act](https://arxiv.org/abs/2605.07769v1)).

The rival control bounds volume instead of depth. GitHub's premium request overage policy offers an enterprise or organization two options, one of which is to "Block usage when your included premium requests are exhausted" ([GitHub Changelog](https://github.blog/changelog/2025-08-22-premium-request-overage-policy-is-generally-available-for-copilot-business-and-enterprise/)). A quota fails loudly. Work stops and somebody asks why. A ceiling fails quietly, and on the four conditions above you learn about it at review.

## Example

```json
{
  "maxEffortLevel": "medium",
  "modelSettings": {
    "claude-sonnet-4-6": {
      "maxEffortLevel": "max"
    }
  }
}
```

This caps every model at `medium` and exempts Sonnet 4.6, because a `"max"` value sets no cap ([settings reference](https://code.claude.com/docs/en/settings-reference#maxeffortlevel)). Deployed in managed settings, no user file raises either value.

## Key Takeaways

- A cap composes by minimum across settings scopes while an `effortLevel` resolves by precedence, so setting the cap anywhere binds every source that sets it higher.
- The clamp runs client-side before each request, which is why it holds on Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry.
- Headless and background runs get no warning. If you cap and also run agents in CI, check the applied level yourself rather than assuming the requested one ran.
- Capping below `xhigh` also switches ultracode off, so the session stops orchestrating dynamic workflows.

## Related

- [Interactive Effort Sliders: Per-Turn Reasoning-Budget Controls](interactive-effort-sliders.md) — the per-turn operator control a ceiling bounds
- [Heuristic-Based Effort Scaling in Agent System Prompts](heuristic-effort-scaling.md) — effort sized from task cues rather than from policy
- [Reasoning Budget Allocation: The Reasoning Sandwich](reasoning-budget-allocation.md) — phase-varying effort, which a low ceiling flattens
- [Tenant Model Policy: Organization-Scoped Rules for AI Model Selection](tenant-model-policy.md) — the same admin tier applied to model choice
- [Codified Effort and Escalation Policy in the Instruction File](../../instructions/codified-effort-escalation-policy.md) — the written default that a ceiling is not
