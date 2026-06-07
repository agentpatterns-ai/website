---
title: "Task Feasibility Awareness: Stop Before You Start"
description: "Tool-using agents burn compute on tasks made impossible by a missing tool. An up-front feasibility check against the tool manifest halts the impossible before the loop spends a token."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - infeasible task detection
  - feasibility-aware agents
last_reviewed: 2026-06-02
---

# Task Feasibility Awareness: Stop Before You Start

> Task feasibility awareness checks up front whether current tools can satisfy a task at all, halting the impossible before the agent spends a long chain.

Task feasibility awareness is the agent capability of judging, before committing compute, whether the tools currently available can in principle complete the requested task — and stopping early when they cannot. It is an environment-grounded predicate: compare what the task requires against what the tool manifest provides. When a critical capability is absent, no amount of reasoning or retrying recovers it, so continuing only wastes tokens.

This is the *inverse* of [premature completion](../anti-patterns/premature-completion.md): there, an agent stops too early on a *feasible* task and declares false success. Here, an agent fails to stop on an *infeasible* task and burns a long chain pursuing an impossible goal. Same calibration family — the continue/halt token — opposite error direction.

## The Gap It Closes

Agents are weak at recognizing infeasibility. The FeasiGen study constructed infeasible tasks by masking the tools consistently required for success, then measured how often agents kept going: false-continue rates reached up to 73.9% across nine evaluated models, described as "substantially weak infeasibility detection ability" ([Cheng et al., arXiv:2605.28532](https://arxiv.org/abs/2605.28532)). The blind spot is independently corroborated from a different angle — Ambig-SWE found "models struggle to distinguish between well-specified and underspecified instructions" without explicit prompting ([Vijayvargiya et al., arXiv:2502.13069](https://arxiv.org/abs/2502.13069)).

## Why It Works

Agents are trained predominantly on *successful* trajectories where the needed tools exist, so their continue/halt policy is conditioned to keep planning and calling tools toward a goal — with no learned signal that a *required capability is absent from the environment*. When a critical tool is removed, the continue-token keeps firing: the agent reasons about how to reach the goal without ever checking whether the goal is reachable with the present toolset ([Cheng et al., arXiv:2605.28532](https://arxiv.org/abs/2605.28532)).

A feasibility gate works because feasibility is a cheap, up-front, observable predicate — task requirements versus the tool manifest — that can short-circuit an expensive open-ended loop before it starts. The same study reports that multi-agent architectures "significantly reduce erroneous execution under infeasible conditions," indicating the judgment improves when a separate reviewer evaluates feasibility rather than the doing agent itself ([Cheng et al., arXiv:2605.28532](https://arxiv.org/abs/2605.28532)).

## How To Apply It

- **Enumerate the required capabilities first.** Before the loop, list the tool capabilities the task implies and check each against the available tool manifest. A missing critical capability is a halt signal, not a planning problem.
- **Externalize the judgment.** Have a separate evaluator assess feasibility, not the agent that will do the work — the doer's policy is biased toward continuing. This mirrors the multi-agent reduction in erroneous execution ([Cheng et al., arXiv:2605.28532](https://arxiv.org/abs/2605.28532)) and the doer/checker split in the [goal contract](goal-contract-completion-evaluator.md) pattern.
- **Make the halt cheap and legible.** An infeasible verdict should return *which* capability is missing, so the caller can add the tool or reject the task — not a silent abort.

## When This Backfires

- **Mis-calibrated judgment aborts solvable tasks.** A false-negative feasibility call is strictly worse than a budget cap — it abandons work a few more steps would have finished. Abstention is only correct when calibrated; treat it as an asymmetric-loss control decision, where a wrong "can't do this" can be more expensive than a bounded overspend ([Iscan, arXiv:2604.27283](https://arxiv.org/abs/2604.27283)).
- **Required capability isn't enumerable up front.** The gate only works when "critical tool present/absent" is observable before execution. For open-ended tasks where the solution path — and thus the required tools — is discovered mid-run, no honest up-front feasibility call exists.
- **Cheap tokens and a tight iteration cap.** When per-task chains are short and a max-iteration cap already bounds waste, a feasibility gate adds reasoning overhead and a false-negative risk for little savings. Brute-force-with-a-cap is simpler when the infeasible-task rate is low.
- **Gameable abstention.** If "I can't do this" is rewarded as the safe answer, agents over-abstain — the inverse of the 73.9% false-continue, and just as costly.

## Key Takeaways

- Feasibility awareness halts a task the current tools cannot satisfy *before* the agent spends a long chain on it — an up-front, environment-grounded gate, not a mid-run reaction.
- Agents are bad at this natively: false-continue rates up to 73.9% on tasks made infeasible by masking critical tools ([arXiv:2605.28532](https://arxiv.org/abs/2605.28532)).
- It is the inverse of premature completion: failing to stop on the impossible, rather than stopping too early on the possible.
- Externalize the feasibility judgment to a separate evaluator; the doing agent's policy is biased toward continuing.
- The dominant failure is over-abstention — a false-negative gate abandons solvable work, so calibrate before trusting the halt.

## Related

- [Premature Completion](../anti-patterns/premature-completion.md) — the inverse failure: stopping too early on a feasible task and declaring false success.
- [Agent Circuit Breaker](agent-circuit-breaker.md) — reactive cousin: blocks a tool that *degrades mid-session*, where feasibility awareness is a predictive up-front check for a tool that was never present.
- [Interactive Clarification for Underspecified Tasks](interactive-clarification-underspecified-tasks.md) — handles missing *information* (ask the user), where feasibility awareness handles missing *capability* (asking won't help).
- [Goal Contract: Separating the Doer from the Done-Checker](goal-contract-completion-evaluator.md) — the same externalized-judgment split, applied to completion rather than feasibility.
- [Cost-Aware Agent Design](cost-aware-agent-design.md) — the cost lever after this gate: route tier by complexity once a task is known to be feasible.
