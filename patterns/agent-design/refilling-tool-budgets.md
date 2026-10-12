---
title: "Refilling Tool Budgets: Rationing by Rate, Not Session Cap"
term: "Refilling Tool Budget"
description: "Ration an expensive agent tool by a configurable refill rate instead of a hard per-session cap, and pay the visibility bill the refill creates by surfacing the balance to the agent."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - reliability
aliases:
  - refilling tool budget
  - tool call refill rate
  - token bucket tool rationing
  - rate-based tool budget
last_reviewed: 2026-10-11
maturity: emerging
---

# Refilling Tool Budgets: Rationing by Rate, Not Session Cap

> A refill rate bounds tool spend per hour instead of per session, so a long run is not starved by an early burst.

Four conditions decide whether a refilling budget beats a per-session cap. The tool's calls have to be independent, so a call that arrives late still carries its value. Sessions have to run long enough for cumulative refills to overtake the cap. The agent has to be able to read its current balance, because a consumer that cannot see capacity arrive behaves as though the budget were still spent. And the operator has to be able to turn the refill off.

## When the refill is the right shape

| Condition | Why it decides the case |
|---|---|
| Calls are independent | A delayed search or fetch still returns its answer, so the cost of waiting is latency. A fan-out that must complete all its calls to yield one result stalls instead of slowing. |
| Sessions outlast the crossover | A bucket that starts below the old cap is tighter than that cap until cumulative refills close the gap, so the short run subsidizes the long one. |
| The agent sees the balance | Without an explicit signal, agents "fail to utilize additional resources even when available" ([arXiv:2511.17006v2](https://arxiv.org/abs/2511.17006v2)). A refill nobody observes is a cap. |
| The operator can disable it | A team metering spend elsewhere has to be able to turn the refill off and fall back to a fixed cap, not reconcile two rations. |

The crossover is arithmetic on two published numbers. Claude Code's WebSearch budget refills at 100 calls per hour against a former 200-call session cap ([Claude Code changelog 2.1.290](https://code.claude.com/docs/en/changelog#2-1-290)); the tools reference describes a 200-call limit that "refills at about 100 calls per hour" and does not say whether refills accumulate above 200. The 2-hour break-even (200 calls at 100 per hour) holds only for a bucket that starts empty. Derive your own crossover from your own session-length distribution before adopting a rate.

## Why it works

The refill changes the quantity being bounded. A session cap bounds calls per session, and session length is a variable the budget owner neither picks nor predicts. So the cap rations the longest sessions hardest. A rate bounds calls per unit time, which is invariant to session length and is the denominator the spend owner is billed in.

The implementation is a token bucket, where "your capacity is continuously replenished up to your maximum limit, rather than being reset at fixed intervals" ([Claude API rate limits](https://platform.claude.com/docs/en/api/rate-limits)). That gives two parameters where a scalar cap has one: the rate bounds sustained spend, the capacity bounds the burst.

Observability is a precondition of the mechanism. Claude's API publishes the replenishment time in `anthropic-ratelimit-requests-reset`, documented as "The time when the request rate limit will be fully replenished, provided in RFC 3339 format" ([Claude API rate limits](https://platform.claude.com/docs/en/api/rate-limits)). That header is what lets a caller wait instead of fail. An agent given no equivalent signal keeps one strategy at any budget: Gemini-2.5-Pro running ReAct "uses nearly identical numbers of tool calls whether the budget is 30 or 100 (13.77 vs. 14.24 search calls)", and the paper puts the bottleneck in that rigidity rather than the call count ([arXiv:2511.17006v2](https://arxiv.org/abs/2511.17006v2)).

## When this backfires

- The agent cannot read the balance or the rate. Capacity arrives and goes unspent, because the agent terminates early, "unaware of unused resources, even though the context window is not filled up" ([arXiv:2511.17006v2](https://arxiv.org/abs/2511.17006v2)). The refill then costs engineering effort and delivers the cap's behavior.
- The consumer is a planner that conditions on a depleting budget. Budget-aware search uses the remaining-budget ratio as its exploration control, so that "as the budget depletes, it sharpens to concentrate probability mass on the highest-value branches". The authors prove convergence only "under an explicit finite budget bound" ([arXiv:2603.12634v1](https://arxiv.org/abs/2603.12634v1)). A refilling budget supplies neither a monotone depletion nor a finite bound, so the control loses the input it reads.
- The tool needs a burst to make any progress. A parallel verification sweep either gets its calls together or returns nothing useful, and the refill converts a clean failure into intermittent slowness. That class is expensive to diagnose. As the grey-failure literature puts it: "The symptoms of grey failure tend to be ambiguous". One study cited there "estimates a median time for the diagnosis of partial failures to be 6 days and 5 hours" ([arXiv:2210.17508v4](https://arxiv.org/abs/2210.17508v4)).
- Sessions are mostly short. The crossover cuts both ways, so a fleet of ten-minute interactive runs pays for a nightly routine's headroom. Weight the rate by the session lengths you actually serve, not by the longest one you can imagine.
- Spend is already metered upstream. Two independent rations interact in ways neither owner modeled, which is why an off switch belongs in the design.

## Example

Claude Code 2.1.290 made the swap on one tool: it "Changed the interactive session's WebSearch budget to refill over time (100 calls/hour; `CLAUDE_CODE_WEB_SEARCH_REFILLS_PER_HOUR` sets the rate, 0 turns it off) instead of ending after 200 calls" ([Claude Code changelog 2.1.290](https://code.claude.com/docs/en/changelog#2-1-290)). Three design choices sit in that one line. The scope is the interactive session, so one-shot runs are untouched. The rate is an environment variable rather than a constant. And `0` turns the refill off and leaves the session cap in place, which the tools reference says "can be raised but not turned off" ([Claude Code tools reference](https://code.claude.com/docs/en/tools-reference#session-search-limit)).

What the entry does not settle is whether the agent is told the rate or the balance.

## Key Takeaways

- Pick the budget shape from your session-length distribution, not from the tool's cost. The cap and the rate cross over at a session length you can compute before you ship either.
- Budget the engineering for the balance signal alongside the bucket. A refill the agent cannot read is a cap that took longer to build.
- Refills break budget-aware planners that need a finite, depleting bound to transition from exploration to exploitation. Expose a per-task finite budget beside the refilling one if a planner consumes it.
- Ship the off switch. An operator who already meters spend has to be able to turn the refill off and fall back to a fixed cap rather than nest it inside theirs.

## Related

- [Agent-Client Admission Control for Agentic Traffic](agent-client-admission-control.md) — the same token-bucket mechanism pointed the other way: a client throttling itself to protect an upstream, not a harness rationing its own agent
- [Per-Run Budget Reservation for Coding Agent Model Calls](per-run-budget-reservation.md) — prospective worst-case reservation inside one finite run-scoped balance, the shape a refill replaces
- [Dual-Budget Control for Search Agents](dual-budget-control-search-agents.md) — how an agent allocates under hard tool-call and token caps once the harness has set them
- [Per-Call Budget Hints on Tool Invocations](per-call-budget-hints-tool-calls.md) — lifting the ceiling on one call rather than reshaping the budget it draws from
- [Loop Budgeting: Allocating Iteration and Token Budget Across Turns](../../loop-engineering/loop-budgeting.md) — choosing the budget primitive for a loop, where this page chooses the ration's shape
