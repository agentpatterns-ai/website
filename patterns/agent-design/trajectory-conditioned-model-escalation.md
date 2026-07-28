---
title: "Trajectory-Conditioned Model Escalation (SWE-Router)"
term: "Trajectory-Conditioned Model Escalation"
description: "Run a cheap model for a few exploratory turns, then read its partial trajectory to decide whether to escalate to a stronger model — the routing signal for agentic tasks that lack binary test feedback."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
  - reliability
aliases:
  - trajectory-based model routing
  - partial-trajectory escalation
last_reviewed: 2026-07-02
maturity: emerging
---

# Trajectory-Conditioned Model Escalation (SWE-Router)

> Run a cheap model for a few turns, then read its partial trajectory to decide whether to escalate to a stronger model.

Pick the model from how a cheap model behaves on the task, not from the task description alone. A weak model runs for a small fixed number of turns, and a learned value head reads the resulting partial trajectory — the thoughts, actions, and observations so far — before deciding to keep going cheap or hand the task to an expensive model. SWE-Router names and formalizes this approach ([SWE-Router, arxiv 2607.00053](https://arxiv.org/abs/2607.00053)).

## The routing gap it closes

Most LLM routers decide from the task description alone. That works when the prompt separates easy from hard, but agentic software tasks routinely defeat it: a near-identical issue can hide a one-line typo fix or a multi-module refactor, and the description does not tell them apart ([SWE-Router](https://arxiv.org/abs/2607.00053)).

[Cascade routing](../../loop-engineering/within-task-model-cascade.md) answers this by starting cheap and escalating when a gate rejects the output — but that needs a binary pass/fail signal. Many agentic tasks have no such signal: no test to run, no type check, no linter verdict at the routing moment. Trajectory-conditioned escalation substitutes a learned read of the partial trajectory for the missing test result, so the escalation decision survives on tasks where cascade routing has nothing to key on.

## How it runs

1. A weak model `m₁` executes the task for `K` exploratory turns. The paper tests `K ∈ {1, 2, 3, 4}`; `K=3` and `K=4` route best ([SWE-Router](https://arxiv.org/abs/2607.00053)).
2. The system collects the partial trajectory after turn `K` — problem description, thoughts, actions, and observations such as retrieved files, failed tests, and stack traces.
3. A learned value head predicts a cost-adjusted success probability for continuing cheap (`y₁`) versus escalating (`y₂`).
4. Decision rule: continue with `m₁` if `y₁ ≥ y₂`; otherwise switch to the strong model `m₂` from turn `K` onward ([SWE-Router](https://arxiv.org/abs/2607.00053)).

## Why it works

Description-only routing is capped by an information-theoretic Bayes-error floor. Two tasks with near-identical prompts can demand wildly different effort, and no function of the prompt alone can separate them ([SWE-Router](https://arxiv.org/abs/2607.00053)). Letting the cheap model act for a few turns surfaces execution evidence — which files it opened, whether its edits passed tests, what the stack trace showed — that is structural signal about difficulty no prompt-only router can access. SWE-Router's Bayes-optimality theorem proves that conditioning on this partial trajectory never harms routing and is strictly better whenever the exploration is informative ([SWE-Router](https://arxiv.org/abs/2607.00053)). Independent work reaches the same conclusion from the POMDP framing: difficulty in multi-turn agentic tasks is trajectory-dependent, so the routing decision belongs mid-trajectory rather than at the prompt ([Agent-as-a-Router, arxiv 2606.22902](https://arxiv.org/abs/2606.22902)).

## When this backfires

- High-signal task descriptions. When the prompt already separates easy from hard — uniform issue templates, tight repro steps — the trajectory adds nothing and the `K` exploratory turns are wasted overhead. The paper is explicit that the gain "vanishes when the prompt already determines the optimal choice" ([SWE-Router](https://arxiv.org/abs/2607.00053)).
- Correlated failure modes. When the weak and strong models fail on the same tasks, no routing decision recovers the strong model's wins; combining models hits a co-failure ceiling ([When Combining Language Models Help, arxiv 2606.27288](https://arxiv.org/abs/2606.27288)).
- Rework that outruns the saving. A weak model's "almost right" output can trigger retries and debugging that cost more than one clean frontier call, so per-call price drops while total token yield collapses ([Model Routing for Coding Agents](https://getunblocked.com/blog/model-routing-coding-agents/)).
- Latency-sensitive loops. Paying `K` weak-model turns plus value-head inference before every escalation adds serial latency an interactive user feels.
- Distribution shift. A value head trained on one task distribution degrades on another — SWE-Router did not consistently beat baselines on its SWE-Smith split ([SWE-Router](https://arxiv.org/abs/2607.00053)).

## Example

SWE-Router pairs a weak model with a strong one and lets the weak model explore before routing. With `deepseek-v3.2` as the weak model exploring for a few turns and `gemini` as the escalation target, reading the partial trajectory lifts Route-AUC on SWE-Bench Verified to 0.780, versus 0.627 for a non-temporal router that decides from the description alone — a 15.3-point gain at matched resolution ([SWE-Router](https://arxiv.org/abs/2607.00053)). The signal driving that gain is concrete: after three turns, a task where the weak model has already retrieved the right file and passed a smoke test looks very different from one where it is thrashing on failing tests, and the value head routes accordingly.

## Key Takeaways

- Route on behavior, not description: a cheap model runs a few turns, and a learned value head reads its partial trajectory to decide whether to escalate.
- It closes the gap cascade routing leaves — escalation without a binary test signal — by treating execution observations as the difficulty signal.
- The mechanism is proven: conditioning on the partial trajectory is never worse than prompt-only routing and strictly better when exploration is informative.
- It backfires when prompts are already high-signal, when weak and strong models share failure modes, when latency matters, or under distribution shift — the exploratory turns are pure overhead in those cases.

## Related

- [Within-Task Model Cascade: Designing the Escalation Gate](../../loop-engineering/within-task-model-cascade.md) — cascade routing that escalates when a gate rejects the output; this technique fills the gap it leaves on feedback-less tasks.
- [GitHub Copilot: Model Selection & Routing](../../training/copilot/model-selection.md) — the same cascade taught as a Copilot curriculum lesson, with worked credit costs.
- [Gateway Model Routing](gateway-model-routing.md) — the infrastructure layer that exposes the weak and strong models a router escalates between.
- [Heuristic-Based Effort Scaling in Agent Prompts](heuristic-effort-scaling.md) — a prompt-time complement that allocates effort from task cues rather than trajectory evidence.
- [Specialized Small Language Models as Agent Sub-Tools](specialized-slm-as-agent-tool.md) — the weak-model side of the pairing, used as a bounded sub-tool.
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md) — the broader cost-routing frame this escalation policy sits inside.
