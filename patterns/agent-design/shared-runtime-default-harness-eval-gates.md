---
title: "Gate a Default Harness Switch With Online and Offline Evals"
term: "Default Harness Switch Gating"
description: "VS Code compared its Copilot harness with the Local harness online and offline. Count token savings only beside completion, then run the migration checklist."
tags:
  - agent-design
  - copilot
  - evals
  - migration
  - harness-engineering
aliases:
  - shared agent runtime migration
  - default harness rollout evaluation
  - harness switch eval gates
last_reviewed: 2026-11-23
maturity: emerging
---

# Gate a Default Harness Switch With Online and Offline Evals

> Gate a default-harness switch on a matched offline comparison and an online rollout comparison, and count token savings only beside completion.

A default-harness switch replaces the runtime that every new agent session starts on. In November 2026 VS Code reported that the Copilot harness, built on the Copilot SDK, is now the default for new agent sessions, replacing its editor-specific Local harness. Copilot CLI, the GitHub Copilot app, and other Microsoft products share that runtime, so a fix to it benefits each client ([VS Code blog](https://code.visualstudio.com/blogs/2026/11/18/copilot-harness)). VS Code measured the switch online and offline. Its figures describe one vendor's migration, not a general rate for harness switches.

## What the two comparisons measured

Online: Copilot Business and Enterprise users on VS Code Stable in October. New chats defaulted to the Copilot harness in one group and the Local harness in the other. The Copilot-default group used 14.2% fewer tokens, 7.7% fewer model requests, and 9.6% lower estimated processing cost per active device. The post calls the cost reduction statistically significant ([VS Code blog](https://code.visualstudio.com/blogs/2026/11/18/copilot-harness)).

Offline: task, model, and reasoning effort matched in each comparison, and repeated runs over multiple days produced 12,845 comparisons across the suites. The post tabulates one evaluation, 112 long DeepSWE tasks run across seven models, as overall results across the models:

| Result | Local harness | Copilot harness |
|---|---|---|
| Runs ending in an error | 5.3% | 1.9% |
| Runs that hung or crashed | 3.1% | 0.2% |
| Task completion, counting errors as incomplete | 54.8% | 61.2% |

Source: the [VS Code blog](https://code.visualstudio.com/blogs/2026/11/18/copilot-harness).

## Why both comparisons

The online numbers "describe resource use across varied day-to-day work, not repeated runs of the same task or how much work was completed" ([VS Code blog](https://code.visualstudio.com/blogs/2026/11/18/copilot-harness)). They show what real use costs and say nothing about completion. The offline runs hold task, model, and reasoning effort fixed, so a gap in errors or completion compares the two harnesses on the same work.

A separate published evaluation of the shared runtime, Copilot CLI against model-provider harnesses on the same models and tasks, found fewer tokens in most tested configurations and broadly comparable task completion. The post adds that "lower token consumption is useful only when the agent still gets the work done" ([VS Code blog](https://code.visualstudio.com/blogs/2026/11/18/copilot-harness)). The method behind that comparison is in [Fleet Harness Attribution](fleet-harness-attribution.md).

## How the rollout ran

VS Code widened the default in steps: internally first, then across Copilot plans, VS Code Insiders and Stable, and editor and Agents-window workflows. At each step the team reviewed key metrics alongside user feedback. Tracked signals included successful turn completion, errors, cancellations, and latency, broken down by categories such as first request versus follow-up request. Sampled first requests "have shown room to improve latency", and the post lists that wait as continuing work after the switch ([VS Code blog](https://code.visualstudio.com/blogs/2026/11/18/copilot-harness)).

## What the comparisons do not cover

"Switching harnesses doesn't automatically migrate every customization" ([VS Code blog](https://code.visualstudio.com/blogs/2026/11/18/copilot-harness)). The [transition guide](https://code.visualstudio.com/docs/agents/run/move-to-copilot) lists what to check:

| Check | What the guide says to verify |
|---|---|
| Prompt files | Convert recurring prompts to skills. Recheck agent, model, and tool choices the conversion does not keep. |
| Hooks | Review supported events, script inputs and outputs, and failure behavior. Hooks have no automatic conversion. |
| MCP servers | Verify configuration, authorization, tools, and sandbox behavior. Input prompts and stored editor secrets do not transfer automatically. |
| Tool sets and chat participants | Replace Local-specific aliases and participant workflows with supported tools, agents, skills, or publisher integrations. |

The guide also gives a before-and-after drill. Before the switch, pick a small task that already works in the Local harness and record its expected result, tools, customizations, and approvals. After it, run that task and check the actual edits, command results, and tests "rather than only the agent's summary" ([transition guide](https://code.visualstudio.com/docs/agents/run/move-to-copilot)).

## Deadline and fallback

The Local harness is deprecated, stays available during a three-month transition, and is removed in February 2027, unless your organization restricts its use ([VS Code blog](https://code.visualstudio.com/blogs/2026/11/18/copilot-harness)). Administrators can set `vscode.temporaryDefaultToLocalHarness` to keep it available. The Local harness cannot enforce Copilot runtime-only permission and sandbox controls, so the guide says an administrator must review and accept that gap before permitting fallback ([transition guide](https://code.visualstudio.com/docs/agents/run/move-to-copilot)).

## When this backfires

- The numbers are one vendor's. The online result covers one rollout comparison between two groups of Business and Enterprise users on Stable in October. The offline table covers one benchmark. Neither predicts another team's switch.
- The cost figure is an estimate. The team computed it from token usage at the same model-specific rates for both groups, not from billing records, and it does not report AI credits charged ([VS Code blog](https://code.visualstudio.com/blogs/2026/11/18/copilot-harness)).
- The post publishes no thresholds. It does not say what result would have paused the rollout, so the "gate" here is the pairing of evidence, not a published pass line.
- The completion row counts errors as incomplete, so it is not independent of the error row. The post does not say how hung or crashed runs were scored.

## Key Takeaways

- Run an online group comparison and an offline matched comparison. The online run shows cost under real use, and the offline run shows errors and completion on fixed work.
- Count a token or cost drop only beside task completion. VS Code's online figures say nothing about completion.
- Match task, model, and reasoning effort in the offline comparison, as VS Code did, so a gap compares the harnesses on the same work.
- Budget for customizations. Prompt files, hooks, MCP secrets, and chat participants do not convert on their own.
- Set the deadline and the fallback policy before the old harness is removed. Fallback drops Copilot runtime-only controls.

## Related

- [Fleet Harness Attribution: Pinning the Model to Compare Whole Harnesses](fleet-harness-attribution.md) — the method behind the shared-runtime comparison against model-provider harnesses.
- [Permission Policy Binds Only at an Enforcement Point](permission-policy-enforcement-prerequisite.md) — why a managed policy moves sessions to the Copilot harness, and what the Local opt-out does to it.
- [Surface Switch or Harness Handoff: What Each Preserves](session-surface-switch-vs-handoff.md) — what a session keeps when it moves interface or harness.
- [Client Version Metric Dip as Adoption Loss](../anti-patterns/client-version-metric-dip-as-adoption-loss.md) — a client release moved Copilot agent sessions to the Copilot SDK and changed what the usage metrics reported.
- [Frozen Task Set Agent A/B Testing](../../workflows/frozen-task-set-agent-ab-testing.md) — freeze a small task set so the offline half of a harness comparison stays repeatable.
