---
title: "Unbounded Agent Feedback Paths (Infinite Agentic Loops)"
term: "Infinite Agentic Loop"
description: "An agent feedback path with no effective stopping bound repeatedly triggers costly or state-growing actions — a distinct failure class from an ordinary program loop."
tags:
  - anti-pattern
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - infinite agentic loop
  - unbounded agent feedback path
  - agent loop without effective bound
last_reviewed: 2026-07-05
maturity: emerging
---

# Unbounded Agent Feedback Paths (Infinite Agentic Loops)

> An agent feedback path with no effective stopping bound repeatedly fires costly or state-growing actions until cost, context, or a rate limit runs out.

An Infinite Agentic Loop (IAL) is an execution failure in which an agentic feedback path repeatedly triggers costly or state-growing actions without an effective stopping bound ([When Agents Do Not Stop, arXiv 2607.01641](https://arxiv.org/abs/2607.01641)). It is not an ordinary program loop. A `for` loop terminates on a deterministic predicate you can read in the source; an agentic loop continues on non-deterministic runtime outputs — model decisions, tool results, external state, exceptions — and its feedback path spans wrappers, configuration, and runtime dispatch rather than one syntactic block. So a visible exit condition can sit outside the actual feedback path and never gate it, while messages and workflow state grow every iteration.

The failure amplifies a single request into long-running model and tool execution. Across 6,549 real-world agent repositories, one detector confirmed 68 IALs in 47 distinct projects at 91.9% precision; 95.6% caused API cost exhaustion and model denial of service, and 27.9% exhausted the context window ([arXiv 2607.01641](https://arxiv.org/abs/2607.01641v1)).

## The six shapes

The same study cut confirmed IALs into six patterns by observed share ([arXiv 2607.01641](https://arxiv.org/abs/2607.01641)):

| Pattern | Share | What loops |
|---|---|---|
| Retry feedback without bounds | 25.0% | A repair or retry path re-fires with no attempt cap |
| Tool-call iteration without bounds | 23.5% | A tool loop re-invokes without a step limit |
| Multi-agent chat without turn bounds | 20.6% | Agents exchange messages with no turn cap |
| Workflow loops without effective bounds | 13.2% | A workflow cycle has a bound placed outside its feedback path |
| Message reentry without bounds | 10.3% | Messages re-enter the queue and re-trigger processing |
| Runner/delegation/evaluator cycles | 7.4% | A delegation or evaluator hands work back indefinitely |

Every confirmed failure shared one root cause — a missing strong bound. The common near-misses were tool-controlled retry logic (41.2%), model-dependent termination (38.2%), and bounds placed outside the actual feedback path (30.9%) ([arXiv 2607.01641](https://arxiv.org/abs/2607.01641v1)).

## Why it works

The failure works because the loop's continuation predicate is not in your code — it is in the model's next decision, the tool's next result, or the framework's dispatch. Relying on the model to eventually stop makes termination a probabilistic event, which is why the paper names model-dependent termination a root cause and concludes that agent iteration should carry explicit stopping rules rather than trust the model to halt ([arXiv 2607.01641](https://arxiv.org/abs/2607.01641)). The fix is the mirror: a bound enforced at the runtime scope where the feedback path is created guarantees termination regardless of what the model or tools decide, which is why the paper recommends bounds be enforced there rather than exposed only as optional local parameters ([arXiv 2607.01641](https://arxiv.org/abs/2607.01641)). A `max_iterations` argument on the wrong wrapper looks safe and never fires.

## When this backfires

Bounding every feedback path is the fix, but a bound applied without judgment creates its own failure:

- An iteration or turn cap set below the real work envelope, with no grader, fires mid-deliverable — the agent halts before finishing rather than running away. Anthropic's managed-agent outcomes cap iterations (`max_iterations` defaults to 3, maximum 20) and, on `max_iterations_reached`, let the agent run one final revision before the session goes idle — a built-in wind-down ([Anthropic — Define outcomes](https://platform.claude.com/docs/en/managed-agents/define-outcomes)). Pair a cap with that kind of wind-down, not a blindly higher number. See [loop budgeting](../../loop-engineering/loop-budgeting.md).
- A bound exposed only as an optional local parameter, placed outside the runtime scope where the feedback is created, reads as bounded in code but never gates the loop ([arXiv 2607.01641](https://arxiv.org/abs/2607.01641)). Verify the bound sits on the path that actually repeats.
- Legitimate long-running loops — mechanical bulk refactors, batch jobs — starve when an arbitrarily low cap is chosen in isolation. Size bounds against the workload; a hard cap is a runaway guard, not a progress target.

## Example

Before — a tool-call iteration without a bound. A LangGraph agent routes between a tool node and the model until the model stops requesting tools. A flaky search tool keeps returning an empty result, the model keeps retrying it expecting different output, and the graph cycles until the API budget is exhausted. The `recursion_limit` was left at its framework default and the retry happens inside the tool wrapper, off the graph's counted path.

After — the bound sits on the feedback path itself. Cap the retry at the runtime scope where it is created:

```python
# retry is bounded where the feedback actually happens, not on an outer wrapper
for attempt in range(MAX_RETRIES):          # hard cap on the tool-retry path
    result = search(query)
    if result:
        break
else:
    result = escalate("search returned empty after retries")  # terminal state
```

The counted path is now the one that loops, and an empty-result run ends in an explicit terminal state instead of a cost-exhausting cycle.

## Key Takeaways

- An Infinite Agentic Loop is a feedback path that fires costly or state-growing actions with no effective bound — distinct from a program loop because its continuation is controlled by model, tool, and framework outputs, not a code predicate.
- The failure is common and expensive: 68 confirmed IALs across 47 projects, with 95.6% causing API cost exhaustion and model denial of service ([arXiv 2607.01641](https://arxiv.org/abs/2607.01641v1)).
- Six shapes cover the field — retry, tool-call, multi-agent chat, workflow, message reentry, and delegation cycles — and every confirmed case shared one root cause: a missing strong bound.
- Place the bound on the actual feedback path at the runtime scope where it is created; a cap on the wrong wrapper looks safe and never fires.
- Bounds sized below the real work envelope backfire as premature termination — pair a cap with a wind-down step and size it against the workload.

## Sources

- Anonymous, [When Agents Do Not Stop: Uncovering Infinite Agentic Loops in LLM Agents](https://arxiv.org/abs/2607.01641v1) (2026) — defines IALs, the six-pattern taxonomy, and the IAL-Scan detector; 6,549-repo study with 68 confirmed failures across 47 projects at 91.9% precision.
- Anthropic, [Define Outcomes — Managed Agents](https://platform.claude.com/docs/en/managed-agents/define-outcomes) (2026) — the outcome iteration cap (`max_iterations` default 3, maximum 20) and the `max_iterations_reached` one-final-revision wind-down.

## Related

- [Loop Budgeting: Allocating Iteration and Token Budget Across Turns](../../loop-engineering/loop-budgeting.md) — the bound primitives (iteration, token, wall-clock) and how to size them so a cap does not fire mid-deliverable
- [Convergence Detection in Iterative Agent Refinement](../../loop-engineering/convergence-detection.md) — progress-based early stopping for loops with no test harness, complementing a hard bound
- [Stuck-Loop Recovery](../../loop-engineering/stuck-loop-recovery.md) — the recovery ladder once detection flags a non-converging loop; this page owns the failure taxonomy, that page owns recovery
- [Agent Loop Go/No-Go Gate](../../loop-engineering/agent-loop-go-no-go-gate.md) — the upstream decision of whether a feedback loop earns its cost at all
- [Circuit Breakers for Agent Loops](../../observability/circuit-breakers.md) — the harder runtime stop that trips when a bound is breached
