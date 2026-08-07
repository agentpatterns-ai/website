---
title: "Dispatch-Time Reasoning Level for Delegated Agents"
term: "Dispatch-Time Reasoning Level"
description: "Choosing a delegated agent's reasoning level at hand-off is a one-shot commitment, so select on blast radius, reversibility, and detection cost rather than estimated difficulty."
aliases:
  - dispatch-time effort selection
  - per-task reasoning level for cloud agents
tags:
  - agent-design
  - cost-performance
  - copilot
  - reliability
  - arxiv
last_reviewed: 2026-08-04
maturity: emerging
---

# Dispatch-Time Reasoning Level for Delegated Agents

> Delegating work to a cloud agent gives you one chance to set the reasoning level, and a mismatch surfaces only at review.

Dispatch-time reasoning level is the effort setting you attach to a delegated task at hand-off, when it is the last input you can give before the run leaves your view. GitHub shipped the control for the Copilot cloud agent on 2026-08-03: you pick a reasoning level alongside the model when you start a task, on paid plans, for models that support it ([GitHub Changelog, 2026-08-03](https://github.blog/changelog/2026-08-03-customize-the-reasoning-level-for-copilot-cloud-agent)). Every entrypoint that offers the choice is a task-start entrypoint, such as assigning an issue to Copilot or leaving an `@copilot` pull request comment ([GitHub Docs: changing the AI model](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/changing-the-ai-model)). None of them adjusts a run already under way.

## When per-dispatch selection earns its cost

Two conditions have to hold together. Where either fails, a standing rule in the instruction file does the same work with no decision attached to each delegation, and GitHub's own advice is to use the regular level by default and raise it only for harder tasks ([GitHub Docs: optimize AI usage](https://docs.github.com/en/copilot/tutorials/optimize-ai-usage)).

- The delegation queue carries real variance. A stream of dependency bumps and lint fixes has no difficulty spread to exploit, so per-task choice is pure overhead. A queue that mixes one-line config edits with cross-service refactors does have the spread.
- Something downstream catches shallow output. A low setting produces a diff that looks finished, and only review reveals it is thin. Without a substantive human or CI gate on the resulting pull request, lowering the level converts a credit saving into an undetected defect.

## Select on structure, not estimated difficulty

Estimated difficulty is the wrong input. You cannot check the estimate before the run, and once the run ends you have the diff instead. Four properties of the task are observable at hand-off.

| Property | Question to ask | Effect on level |
|----------|-----------------|-----------------|
| Blast radius | How many files, services, or callers does the change reach? | Raise as reach grows |
| Reversibility | Can a wrong result be reverted with one command? | Keep low where revert is cheap |
| Detection cost | Would tests and CI catch a wrong answer, or only a careful reader? | Raise where only a reader would catch it |
| Specification quality | Does the issue state acceptance criteria? | Rewrite the issue instead of raising |

The last row matters most. Reasoning budget does not repair an underspecified ticket, and spending more of it on one degrades the result ([Inverse Scaling in Test-Time Compute, arXiv:2507.14417v2](https://arxiv.org/abs/2507.14417v2)).

## Why it works

The level buys serial compute before the response. GitHub describes it as controlling the depth of the model's reasoning process before it generates a response, and states that a higher level consumes more tokens and therefore more credits ([GitHub Docs: supported AI models](https://docs.github.com/en/copilot/reference/ai-models/supported-models)). That budget pays off when the difficulty sits in the reasoning, such as tracking constraints across files or weighing two approaches. It costs when the difficulty sits in the input, because a longer chain has more opportunity to latch onto irrelevant material ([Inverse Scaling in Test-Time Compute, arXiv:2507.14417v2](https://arxiv.org/abs/2507.14417v2)).

Delegation changes what the setting is. In an interactive session the operator watches the trajectory and corrects it, so the level acts as a starting guess with a feedback loop attached ([Interactive Effort Sliders](interactive-effort-sliders.md)). A cloud agent removes the loop, which turns the same setting into a commitment whose error is discovered at pull request review. Structural properties are the usable input because they survive that gap.

The selection is about accuracy and cost, not about permissions. Varying effort inside GPT-5.6 across 840 clerical trajectories under an explicit prohibition produced no policy-prohibited tool calls in any arm ([Xu and Wu 2026](https://arxiv.org/abs/2608.03169v1)). That is a bound rather than a guarantee, and [Equivalence Testing for Agent Configuration Changes](../../verification/equivalence-testing-agent-config-changes.md) covers what it does and does not license.

## When this backfires

- Raising the level as a hedge against uncertainty makes accuracy worse on average. Across 21,730 agent rollouts on 9 models and 9 benchmarks, higher reasoning effort reduced accuracy in the majority of runs ([HAL: Holistic Agent Leaderboard, arXiv:2510.11977v1](https://arxiv.org/abs/2510.11977v1)).
- Vague issues get worse rather than better. Extended reasoning leaves models increasingly distracted by irrelevant information and shifts them from reasonable priors toward spurious correlations ([Inverse Scaling in Test-Time Compute, arXiv:2507.14417v2](https://arxiv.org/abs/2507.14417v2)).
- Long-horizon runs lose to their own thinking. Reasoning spend competes with the run's remaining budget, and uniform maximum reasoning underperformed both a phase-varied allocation and a uniform high setting on Terminal Bench 2.0 because of agent timeouts ([LangChain: Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).
- Without per-task credit attribution the overspending half of the trade-off stays invisible, so the policy drifts upward and never corrects.

## Key Takeaways

- Put the four selection properties into the delegation checklist so the choice is mechanical: blast radius, reversibility, detection cost, specification quality.
- Default to the regular level and require a named reason to raise it, since higher effort lowered accuracy in the majority of measured runs.
- Treat a vague issue as a blocker on dispatch. Rewriting the ticket costs less than a run that reasons hard over the wrong requirements.
- Turn on per-task credit attribution before tuning anything, or only the accuracy half of the trade-off will ever be visible.
- Audit the queue first. A uniform queue or an ungated merge path means the per-task decision buys nothing, so codify one default instead.

## Related

- [Interactive Effort Sliders: Per-Turn Reasoning-Budget Controls](interactive-effort-sliders.md) — the same knob when the operator is present and can correct mid-session.
- [Codified Effort and Escalation Policy in the Instruction File](../../instructions/codified-effort-escalation-policy.md) — the standing-default alternative to choosing per task.
- [Reasoning Budget Allocation: The Reasoning Sandwich](reasoning-budget-allocation.md) — varying effort across phases of one run rather than across tasks.
- [Auto Model Selection: Harness-Driven Routing per Task](auto-model-selection.md) — the model half of the same dispatch decision.
- [Cost-Quality Pareto Measurement](../../token-engineering/cost-quality-pareto-measurement.md) — how to measure whether a level change paid for itself.
