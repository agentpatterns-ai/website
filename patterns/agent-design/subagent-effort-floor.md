---
title: "Subagent Effort Floors Instead of Session Inheritance"
term: "Subagent Effort Floor"
description: "A subagent effort floor sets the level delegated workers run at when nothing else names one. It beats inheritance for mechanical fan-out you did not author."
tags:
  - agent-design
  - cost-performance
  - claude
aliases:
  - subagent effort default
  - default effort level for subagents
  - subagent reasoning budget floor
applies_to: "claude-code@2.1.316"
last_reviewed: 2026-11-02
status: current
maturity: emerging
---

# Subagent Effort Floors Instead of Session Inheritance

> A subagent effort floor sets the level workers run at when nothing else names one, so fan-out stops inheriting the orchestrator's level.

A subagent effort floor is an operator-set default for the effort level delegated agents run at. Claude Code shipped one as `CLAUDE_CODE_SUBAGENT_EFFORT` in v2.1.316 on 31 October 2026. The variable sets "the effort level subagents run at when nothing else names one, instead of inheriting the session's" ([changelog 2.1.316](https://code.claude.com/docs/en/changelog#2-1-316)). Before it, the level an operator chose for an orchestrator descended to every worker it dispatched.

## Two conditions before you set one

Set a floor when both conditions hold. Where either fails, a per-agent `effort:` field or plain inheritance does the same job with less surprise.

- The fan-out is mechanical and uniform. Twenty workers running lookups have little for a higher level to verify. Three doing synthesis among seventeen doing lookups is the case one floor cannot serve, because it sets the wrong level for the three the orchestrator leans on most.
- You did not write the agent definitions. A definition's own `effort:` field wins over the floor, so the floor only reaches agents that name no level. Where you own the files, set `effort:` in each one instead, which is per-agent and visible to whoever reviews the file.

## The precedence chain

"When nothing else names one" is the precedence clause, and it is what makes this a floor rather than a cap. The sub-agents documentation places the three middle rungs explicitly ([Choose an effort level](https://code.claude.com/docs/en/sub-agents#choose-an-effort-level)).

| Rung | Source | Documented position |
|---|---|---|
| Ceiling | `maxEffortLevel` | Any higher level "runs at the cap instead", including one from "a skill's or subagent's `effort` frontmatter" ([settings reference](https://code.claude.com/docs/en/settings-reference#maxeffortlevel)) |
| Session variable | `CLAUDE_CODE_EFFORT_LEVEL` | "takes precedence over both" the invocation parameter and the frontmatter field |
| Per-invocation | `effort` parameter | "overrides the `effort` field"; needs v2.1.292 or later |
| Per-agent | `effort:` frontmatter | "Overrides the session effort level, but not the `CLAUDE_CODE_EFFORT_LEVEL` environment variable" |
| Floor | `CLAUDE_CODE_SUBAGENT_EFFORT` | Applies when "nothing else names one" ([changelog 2.1.316](https://code.claude.com/docs/en/changelog#2-1-316)); its order against `CLAUDE_CODE_EFFORT_LEVEL` is undocumented |

One rung is unplaced, and it is the one that matters for automation. As of 2 November 2026 the variable appears on neither the environment variables page nor the sub-agents page, so its position relative to `CLAUDE_CODE_EFFORT_LEVEL` is undocumented. A headless run that sets the session level that way has no documented answer on whether the floor applies. Test it rather than complete the chain by inference.

The model half of dispatch inheritance is already documented, and it reads as the template. `CLAUDE_CODE_SUBAGENT_MODEL` covers agents "that aren't assigned a model another way". The same entry says "Two sources take precedence over it: a model Claude passes when it spawns the agent, and a `model` field in the agent's definition" ([environment variables](https://code.claude.com/docs/en/env-vars)). That variable also has a force override, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, which inverts the order and pushes one model onto every subagent. No effort equivalent is documented, so plan on the floor yielding to any definition that names a level.

## Why it works

Fan-out multiplies the worker term and leaves the orchestrator term alone. Effort is a per-request allowance, so one orchestrator turn at a high level is paid once. Twenty worker turns at that level are paid twenty times. LangChain measured the size of the allowance on Terminal Bench 2.0 with `gpt-5.2-codex`. More reasoning "helps agents evaluate each step, but can burn over `2x` more tokens/time" ([LangChain: Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).

The return on that allowance varies with the kind of work. LangChain found reasoning paid in planning and in late verification. It built its baseline on the finding that "You can use the max reasoning budget on every task, but most work can benefit from optimizing reasoning compute spend" ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)). Inheritance ties the multiplied term to a level chosen for the term paid once. A floor separates the two. The evidence is one vendor's run on one model, and the same post reports no large differences across the budget splits it tried, so read the direction rather than the margin.

## When this backfires

- The workers reason like the parent. A critic reviewing a plan, or a worker hunting edge cases, sits in the phase that pays. LangChain kept more reasoning for that phase because "Later stage verification also benefits from more reasoning to catch mistakes and get a solution submitted" ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)). A floor below the session level starves that phase.
- The work is harder than the floor assumes. On GameEngineBench's Unreal Engine C++ tasks, "Increasing reasoning effort from medium to high to xhigh raises pass@1 from 9.1% to 19.1% to 29.1%" for GPT-5.5. The paper adds that the extra reasoning "does not close the gap to the strongest configuration and does not make the benchmark easy" ([GameEngineBench](https://arxiv.org/abs/2607.03525v2)). A low floor spends that 20-point span on every dispatch, not only the cheap ones.
- Nothing downstream reads the worker's output critically. A thin result looks finished, so the saving turns into a defect nobody attributes to the floor. [Dispatch-time reasoning level](dispatch-time-reasoning-level.md) names the same condition for one-shot delegation.
- The floor is inert and says nothing about it. Every agent whose definition sets `effort:` ignores it, so an operator who sees no change in spend has probably hit this rather than found a broken control.

Raising the floor is not the safe correction either. Running the same LangChain harness "only at `xhigh` scored poorly at `53.9%` due to agent timeouts compared to `63.6%` at `high`" ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)). The uniformly higher level came in 9.7 points lower, and the source puts the drop down to timeouts rather than to worse reasoning.

## Example

An orchestrator that reasons about a plan and dispatches cheap searches wants two levels. Set the session level with the flag and the worker default with the variable:

```bash
CLAUDE_CODE_SUBAGENT_EFFORT=low claude --effort xhigh
```

The flag is deliberate here. `--effort` sets the session level, and `CLAUDE_CODE_EFFORT_LEVEL` "Takes precedence over `--effort`, `/effort`, and the `modelSettings` and `effortLevel` settings" ([environment variables](https://code.claude.com/docs/en/env-vars)). Using the flag for the session keeps the pairing clear of the interaction the documentation does not yet describe.

The accepted values are the other thing to confirm. `CLAUDE_CODE_EFFORT_LEVEL` documents `low`, `medium`, `high`, `xhigh`, and `max`, with the available levels depending on the model ([environment variables](https://code.claude.com/docs/en/env-vars)). The subagent variable has no published value list yet, so treat `low` above as the level the changelog's wording implies rather than a documented one.

A worker that should ignore the floor names its own level, which wins:

```yaml
---
name: plan-critic
model: opus
effort: high
---
```

Check the result rather than trust it. `/tasks` lists each running subagent with its model and "adds the effort level set for that subagent, if any", from v2.1.242 ([sub-agents](https://code.claude.com/docs/en/sub-agents#choose-a-model)).

## Key Takeaways

- The floor only fills the gap. A definition's `effort:` and a per-invocation parameter name a level, so they outrank it, and `maxEffortLevel` clamps the result.
- It pays where the worker count is the multiplied term and worker-side work has nothing to verify. It costs where workers plan or verify.
- Where you own the agent files, `effort:` per definition is the better instrument. The variable's real use is agents you did not write.
- The floor's position relative to `CLAUDE_CODE_EFFORT_LEVEL` is undocumented as of 2 November 2026, so confirm the behavior in headless runs before relying on it.

## Related

- [Effort as a Verification Dial: What a Higher Level Buys](effort-as-verification-dial.md) — what a level buys once you have chosen where to set it
- [Administrative Effort Ceilings for Reasoning Budget](administrative-effort-ceilings.md) — the cap that clamps every rung of the chain above
- [Interactive Effort Sliders: Per-Turn Reasoning-Budget Controls](interactive-effort-sliders.md) — the operator's live per-turn control, where this page is a standing default
- [Dispatch-Time Reasoning Level for Delegated Agents](dispatch-time-reasoning-level.md) — the one-shot choice at hand-off to a cloud agent
- [Model-Directed Subagent Tiering: Lead Model Picks the Tier](model-directed-subagent-tiering.md) — the inverse surface, where the model chooses tier and effort per dispatch
