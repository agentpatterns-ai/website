---
title: "In-Agent Task Prioritization: Ranking the Next Action"
term: "In-Agent Task Prioritization"
description: "Rank pending work by a composite score — urgency, value, dependency, blast radius, staleness — so the agent's scarce attention lands on the item that pays back most per turn."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - agent next-action ranking
  - in-agent priority queue
  - task ranking pattern
last_reviewed: 2026-06-16
maturity: established
---

# In-Agent Task Prioritization

> Prioritization is the agent's ranking of pending tasks by composite score — distinct from routing (who) and scheduling (when).

In-agent task prioritization is the decision an agent makes, every turn, about which pending item to advance next. It is distinct from [parsimonious agent routing](../multi-agent/parsimonious-agent-routing.md) (which worker handles a task) and from scheduling (when a task runs). Prioritization is the agent's own next-action ranking over work it has already accepted. Antonio Gulli treats it as a first-class pattern in 'Agentic Design Patterns' ([Chapter 20](https://link.springer.com/book/10.1007/978-3-032-01402-3)).

## When this pattern pays off

The pattern earns its complexity under four conditions. Outside them, FIFO is the correct answer.

| Condition | Why ranking pays back |
|-----------|----------------------|
| Scarce attention, not scarce CPU | The per-turn attention budget is the bottleneck; reordering changes marginal value per turn |
| Long backlog or long sessions | Head-of-line blocking compounds — low-value items consume slots before high-value ones |
| Heterogeneous item value | A 10× spread in expected payoff makes ranking strictly dominate arrival order |
| Estimable signals | Urgency, dependency, or blast radius can be derived from state without guessing |

When the constraint is resource contention rather than attention, the answer is strict FIFO plus [lane-based execution queueing](lane-based-execution-queueing.md). Block's [agent-task-queue](https://github.com/block/agent-task-queue) ships exactly that — "FIFO Queuing: Strict first-in-first-out ordering within each exact queue_name" — because it serializes expensive operations to keep one machine responsive, not to maximize per-turn payoff.

## Ranking signals

A composite score combines several dimensions so no one signal dominates:

- Urgency — deadline proximity or external state changes that age out the item.
- Economic value — expected payoff if completed (the per-task equivalent of [economic-value signaling](../multi-agent/economic-value-signaling.md), which carries the same signal across agents).
- Dependency or unblocking — items that unblock other waiting work; ranking by transitive unblock count is what an autonomous backlog agent does instead of issue-number order.
- Blast radius — irreversibility or scope; some teams invert this signal and rank irreversible work last to keep options open.
- Staleness — items whose ground truth is decaying.

## Define the word you rank by

A scoring function makes you write down what "value" means. A request to "sort these by impact" leaves that choice to the agent. This section rests on one source, a [Microsoft for Developers post by Waldek Mastykarz](https://developer.microsoft.com/blog/is-sort-by-impact-just-vibes/) (2026-11-24).

It tested three domains, each with one fixed list of eight items, with and without data per item. Claude Sonnet 5.5 and GPT-6.1 Sol ranked all three. Claude Haiku 5.5 and GPT-6 Luna ranked only a developer-tool backlog. Each prompt ran 15 times, in Vally (Microsoft's agent evaluation tool) with the GitHub Copilot SDK.

Across 1,500 runs, agents ranked the same list in nearly the same order every time. Two runs of one prompt agreed on the order of 86% to 100% of item pairs, depending on model and list. Different models largely agreed too. The prompt never defined impact, so the agents picked a definition, and it changed with the domain. With titles only:

| List | Closest of the tested definitions | What agents said they ranked by |
|------|-----------------------------------|---------------------------------|
| Developer-tool backlog | Users reached | Reach, or a mix that included it |
| Online shop | Revenue | Money (GPT-6.1 Sol) or a mix (Claude Sonnet 5.5) |
| Security improvements | Losses avoided | Severity, which no tested definition covered |

Data in the list steers the choice too. The data versions of the shop and security lists gave every item reach, money and days of effort. On both, Claude Sonnet 5.5 and GPT-6.1 Sol matched the money order exactly in every run.

The post suggests three responses:

- Name the metric, such as expected revenue or value per day of effort.
- If you are unsure which definition fits, ask for one ranking per definition and compare them. Items that move between rankings are where the decision is.
- In a skill, prompt or agent that ranks for people, such as issue triage, put the definition in its instructions.

Asking the agent to define impact first still leaves the choice with the agent. In the post's runs it did not make rankings more consistent, and for three of the four models made them less so. The post gives no figures for this and does not say which lists it covers.

Read the result narrowly:

- The source is one vendor blog, with small constructed lists of business decisions and no human baseline.
- Consistency is not correctness. Repeated runs can agree on an order built on a definition you would reject.
- Naming the metric changes who picks the definition. The post found unnamed rankings about as consistent as named ones, and reports no figure for how closely agents follow a named metric.
- With titles only, 64% to 100% of runs picked the same first item.
- Reversing the input order changed full rankings only slightly. The backlog was the only list where it changed the top pick.
- The runs tested only "impact". The post extends its advice to "priority" and "importance".

## Why it works

Per-turn attention is the scarce resource, and arrival order has no relationship to marginal value. Pure FIFO produces head-of-line blocking — a high-value program waits behind low-value calls. [Autellix](https://arxiv.org/abs/2502.13965v1) identifies this as the dominant inefficiency in LLM-agent workloads and reports 4–15× program-throughput gains at equivalent latency from program-aware priority scheduling. A composite score reorders the queue so each turn pays back more of the goal; the mechanism is attention-budget allocation under head-of-line blocking, not "agents need lists".

## When this backfires

Three failure modes recur:

- Starvation of low-priority tasks. Pure top-K priority leaves low-priority items waiting indefinitely; [HEXGEN-FLOW](https://arxiv.org/pdf/2505.05286) documents this for agentic text-to-SQL and applies aging — promote an item's priority after it has waited past a threshold, borrowed from Solaris TS and MLFQ. Without aging, the queue eats its own tail.
- Thrashing from constant re-ranking. Recomputing scores every turn flips order under noise and the agent never finishes anything. Re-rank on state change, not on every turn; debounce.
- Gaming a single signal. When one dimension (self-declared urgency) is the only input, the system optimizes that signal at the expense of throughput. Cap per-signal weight, or split high-stakes work into a separate lane rather than racing it through the main queue.

## Example

A backlog agent processing the issue tracker via [labels-as-locks](../../workflows/labels-as-locks-pipeline.md) defaults to issue-number order. Replace the default ordering with a composite score, computed once per scan, and re-evaluate on state change rather than per turn:

```python
def score(issue):
    return (
        2.0 * unblock_count(issue)        # transitive items waiting on this one
        + 1.5 * value_estimate(issue)     # tag-derived expected payoff
        + 1.0 * urgency(issue)            # deadline + staleness
        + 0.2 * waiting_turns(issue)      # aging — anti-starvation boost
    )

next_issue = max(ready_issues, key=score)
```

The `waiting_turns` term is the aging mitigation; without it, an issue with low value and zero dependents never runs. Capped per-signal weight (no signal exceeds ~2×) prevents the gaming failure mode. Re-rank when an item moves to `ready` or an upstream item completes — not every turn — to avoid thrashing.

## Key Takeaways

- Prioritization is a different decision from routing (who) and scheduling (when) — name it as its own concern so teams can encode urgency, value, and dependency signals into the loop.
- The pattern earns its complexity when attention is scarce, the backlog is long, value spread is wide, and ranking signals are estimable. Otherwise FIFO plus lane isolation is correct — Block's agent-task-queue is the worked example of that choice.
- Composite scores beat single signals; aging beats pure priority; re-rank on state change, not per turn.
- Name the metric when you ask for a ranking. In one vendor study of eight-item lists, agents told to sort by "impact" chose the definition themselves and ranked in nearly the same order each run.
- Head-of-line blocking on the attention budget is the mechanism the pattern attacks; [Autellix](https://arxiv.org/abs/2502.13965v1) reports 4–15× program-throughput gains from program-aware priority over FIFO.

## Related

- [Economic Value Signaling in Multi-Agent Networks](../multi-agent/economic-value-signaling.md)
- [Parsimonious Agent Routing for Multi-Agent Dispatch](../multi-agent/parsimonious-agent-routing.md)
- [Lane-Based Execution Queueing](lane-based-execution-queueing.md)
- [Labels as Locks: Pipelined Backlog Processing](../../workflows/labels-as-locks-pipeline.md)
- [Background Todo Agent](background-todo-agent.md)
- [Interactive Clarification for Underspecified Tasks](interactive-clarification-underspecified-tasks.md) — the agent asks about a gap instead of filling it
- [Grill Me: Developer-Initiated Plan Interrogation](grill-me-technique.md) — have the agent question you before the work starts
- [Assumption Propagation](../anti-patterns/assumption-propagation.md) — how an early unchecked assumption compounds through later work
