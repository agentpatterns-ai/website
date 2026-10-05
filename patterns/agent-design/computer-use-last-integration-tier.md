---
title: "Computer Use as the Last Integration Tier"
term: "Last Integration Tier"
description: "Driving a GUI is the bottom rung of the integration ladder. Select it only when no API, MCP server, terminal command, filesystem tool, or browser tool reaches the task, and only for short reversible workflows."
tags:
  - agent-design
  - copilot
aliases:
  - computer use as last resort integration
  - integration tier selection for agents
last_reviewed: 2026-10-03
maturity: emerging
status: current
---

# Computer Use as the Last Integration Tier

> Computer use is the bottom rung of the integration ladder — reach for it only when no machine surface reaches the task.

GitHub put computer use into public preview in Copilot CLI and the Copilot app on October 1, 2026. The changelog named a condition rather than a capability. The feature covers "workflows in legacy and GUI-only software that do not provide an API, command-line interface, or MCP integration" ([GitHub Changelog, 2026-10-01](https://github.blog/changelog/2026-10-01-github-copilot-can-now-interact-with-desktop-apps)). That is a tier-selection rule. The GUI is the surface you fall back to. Falling back costs you a standing permission grant plus a reliability penalty that grows with the length of the workflow.

## The conditions that hold the bottom rung

Check every rung above the GUI first. The docs name five, two more than the changelog does: "If an API, MCP server, terminal command, filesystem tool, or dedicated browser tool can complete the task directly, that tool typically provides more structured information and predictable results" ([GitHub Docs: About computer use](https://docs.github.com/copilot/concepts/agents/computer-use)).

Once you are on the bottom rung, two task properties decide whether it holds.

### Horizon

Frontier agents are "saturated at 79–83% binary accuracy on OSWorld 1.0", whose binary scoring "works for short tasks". On the long-horizon OSWorld 2.0 benchmark the best configuration "completes only 20.6% of tasks under strict binary completion while reaching 54.8% partial score" at 500 steps ([OSWorld 2.0, arXiv:2606.29537v2](https://arxiv.org/abs/2606.29537v2)). Cross-application navigation sits on GitHub's own capability list, and it is the regime where completion collapses.

### Reversibility

GitHub warns that "Changes in timing or window state can produce different results, cause computer use to repeat an action, or prevent it from continuing" ([GitHub Docs](https://docs.github.com/copilot/concepts/agents/computer-use)). A repeated click in a form that submits is not something a retry undoes.

## Why it works

The higher rungs win because they return something the agent can check, and a screenshot does not. That is the structured-and-predictable property GitHub names above. The research literature supplies the same mechanism independently. GUI-only agents "rely exclusively on primitive GUI actions (click, type, scroll), creating brittle execution chains prone to cascading failures", and mixing high-level tool calls back in works by "reducing error propagation". The paper reports a "22% relative improvement" on OSWorld over "existing approaches" ([UltraCUA, arXiv:2510.17790v3](https://arxiv.org/abs/2510.17790v3)).

Error propagation is why the penalty tracks workflow length rather than task difficulty. OSWorld 2.0 found that agents "execute local actions well" but skip "the verification that completion depends on", spending under 7% of their budget on detecting and repairing their own errors ([arXiv:2606.29537v2](https://arxiv.org/abs/2606.29537v2)). Each unverified step carries its mistake forward.

## What the approval model costs

Copilot asks before controlling an application, and you can choose **Always allow** for one. That decision becomes a standing grant. It is stored locally and "applies to both GitHub Copilot CLI and GitHub Copilot app on the same computer". Withdrawing it is not retroactive, because removing an application "does not revoke access already granted in a running session". A deny rule still outranks it, since "Permission rules that deny a tool take precedence over automatic or saved approvals" ([GitHub Docs](https://docs.github.com/copilot/concepts/agents/computer-use)) — the same [most-restrictive-wins ordering](most-restrictive-wins-fusion.md) that governs other agent-control returns.

GitHub's guidance follows from that: "Avoid choosing Always allow for applications that contain sensitive information or support high-impact actions." The per-session approval is the control, and the always-allow list is where you spend it.

None of this is yours to decide alone in a managed org. Enterprise administrators can disable computer use through managed settings, and "Enabling computer use locally does not override an enterprise policy" ([GitHub Docs](https://docs.github.com/copilot/concepts/agents/computer-use)).

## When this backfires

- Long cross-application workflows — at 20.6% binary completion the expected result is a half-finished workflow, which on a stateful GUI is worse than no attempt ([arXiv:2606.29537v2](https://arxiv.org/abs/2606.29537v2)).
- A partial machine surface — the rule reads as all-or-nothing, and most legacy software has a thin API instead of no API at all. Routing such a case wholly to the GUI forfeits the hybrid action gain, a 22% relative improvement on OSWorld over existing approaches per the UltraCUA abstract ([arXiv:2510.17790v3](https://arxiv.org/abs/2510.17790v3)).
- Justifying the ordering by clicking accuracy — OSWorld 2.0 is explicit that "These failures are not about basic GUI control or coding" ([arXiv:2606.29537v2](https://arxiv.org/abs/2606.29537v2)). Reason from verification cost instead, or you will reject short GUI tasks that work and accept long ones that do not.
- Windows holding other people's data — "Application windows may display sensitive information, including information about other people" ([GitHub Docs](https://docs.github.com/copilot/concepts/agents/computer-use)). The screen is the context payload, and you consent on behalf of whoever appears in it.

## Example

Computer use is disabled by default ([GitHub Docs: About computer use](https://docs.github.com/en/copilot/concepts/agents/computer-use)). In Copilot CLI, `/computer on` saves your preference and enables the computer-use plugin. Only the approval prompt is per session ([GitHub Docs: Copilot CLI computer use](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/computer-use)):

```
/computer on      # enable computer-use tools
/computer show    # check status
/computer off     # disable
```

The same `/computer on` works in the Copilot app, which also exposes a settings toggle. The [Copilot app how-to](https://docs.github.com/en/copilot/how-tos/github-copilot-app/computer-use) gives the menu path: Settings, then Computer Use, then Enable Computer Use. On macOS the flow "guides you through the required Accessibility and Screen Recording permissions" ([GitHub Changelog, 2026-10-01](https://github.blog/changelog/2026-10-01-github-copilot-can-now-interact-with-desktop-apps)).

The prompt shape GitHub prescribes mirrors the tier's weakness. Computer use "works best when you describe the outcome you want, the applications involved, and any important constraints" ([GitHub Docs: Copilot CLI computer use](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/computer-use)). Naming the applications bounds which windows enter context. Naming the constraints matters because agents "drop stated constraints" over a long horizon ([arXiv:2606.29537v2](https://arxiv.org/abs/2606.29537v2)). To interrupt, press Esc twice in the CLI or select **Stop** in the app ([GitHub Docs](https://docs.github.com/copilot/concepts/agents/computer-use)).

## Key Takeaways

- Check all five rungs before the GUI. Where a thin API covers part of the task, split the task across rungs instead of dropping the whole thing to the bottom.
- Scope a computer-use task to a short horizon and reversible actions. Put the state it must not drop into the prompt, because the screen will not hold it for you.
- An always-allow grant spans both Copilot surfaces on that machine and does not end a session that already holds access.
- Enterprise managed settings can disable the feature, and enabling it locally does not override that policy.

## Related

- [Headless-First Services: APIs for Agent Consumers](../../tool-engineering/headless-first-services.md) — the supply-side answer: build the rungs above the GUI for software you own
- [Lock-State Safeguards for Desktop-Controlling Agents](../../security/locked-desktop-agent-safeguards.md) — containment for an agent already driving a desktop
- [App-Window Snapshot as Agent Context](../../context-engineering/app-window-snapshot-context.md) — reading a window as context without controlling it
- [Minimum-Sufficient Control Ladder](minimum-sufficient-control-ladder.md) — the same escalate-on-named-failure logic applied to oversight mechanisms
- [Agent-Operable Interface Design](agent-operable-interface-design.md) — designing an interface an agent can work rather than one it must interpret
