---
title: "Loop Budgeting: Allocating Iteration and Token Budget Across Turns"
term: "Loop Budgeting"
description: "Pick the right budget primitive — iteration cap, token budget, or wall-clock — and decide whether to front-load reasoning across the loop's phases or split it evenly across turns."
tags:
  - loop-engineering
  - cost-performance
  - tool-agnostic
aliases:
  - loop budget allocation
  - per-turn budget allocation
  - agent loop budgeting
last_reviewed: 2026-06-29
maturity: adopted
---

# Loop Budgeting: Allocating Iteration and Token Budget Across Turns

> Pick the budget primitive by whether an external grader exists, then choose front-loaded vs even-split allocation by whether the loop has clean phases.

## The two decisions

Loop budgeting is two decisions, not one.

The first is which budget primitive caps the loop: an iteration count, a total cost or token budget, a wall-clock timeout, or some pair of these. The second is how the budget is allocated across turns within the cap: evenly, or front-loaded into the phases where ambiguity is highest.

These are independent. A loop can cap on iteration count and still front-load reasoning compute into early turns. A loop can cap on dollar spend and still split tokens evenly across actions. The [agent loop go/no-go gate](agent-loop-go-no-go-gate.md) decides whether to loop at all; this page decides how to bound it.

## Budget primitive: pick by what fires first

Three primitives compete to fire first. The Claude Agent SDK ships exactly two of them as first-class options: `max_turns`/`maxTurns` caps tool-use round-trips, `max_budget_usd`/`maxBudgetUsd` caps dollar spend, and on either fire the SDK returns a `ResultMessage` with subtype `error_max_turns` or `error_max_budget_usd` ([Claude Agent SDK — How the agent loop works](https://code.claude.com/docs/en/agent-sdk/agent-loop)).

| Primitive | When it is the right cap | When it is wrong |
|---|---|---|
| Iteration count (`max_turns`, `max_iterations`) | An external grader certifies correctness — the loop only needs a runaway guard | No grader; a fixed turn count may fire mid-deliverable |
| Token or cost budget (`max_budget_usd`, custom token cap) | Cost predictability matters more than completion; protects against runaway spend | Single-session loops where context grows non-linearly across turns — a flat per-turn budget mis-prices late iterations |
| Wall-clock (`max_execution_time_s` or equivalent) | Latency SLOs bind harder than spend; user-facing interactive agents | Background or batch work where the wall-clock pressure forces premature stop |

Anthropic's Managed Agents `outcome` primitive ships iteration cap only — `max_iterations` defaults to 3 and caps at 20 ([Anthropic — Define outcomes](https://platform.claude.com/docs/en/managed-agents/define-outcomes)). The design choice is deliberate: the grader runs in a separate context window and returns one of `satisfied`, `needs_revision`, `max_iterations_reached`, `failed`, or `interrupted`, so the harness only needs a runaway guard. On `max_iterations_reached` the agent may run one final revision before the session goes idle — a built-in wind-down budget.

A flat per-turn token cap is the common mistake. Per-turn cost in a single-session loop is not uniform — each turn re-sends the full accumulated conversation history plus tool definitions, so the marginal cost of iteration N grows roughly with N, and automatic compaction defers but does not eliminate this growth ([Claude Agent SDK — How the agent loop works](https://code.claude.com/docs/en/agent-sdk/agent-loop)). Enforce token budgets across the loop, not within each turn. The controller's primitive is the pair `(remaining_turns, remaining_tokens)` exposed every step — that is what lets a [dual-budget controller](../agent-design/dual-budget-control-search-agents.md) score actions correctly when budget is low.

The wrong default is to set all three primitives high and trust whichever fires first. Budgets that bind force discipline; budgets that never bind are decorative. One binding primitive beats three slack ones.

## Per-turn allocation: front-loaded vs even split

Once the cap is chosen, allocation across turns is the second decision. The two options are even split — each turn gets the same compute budget — and front-loaded, where planning and verification get extra-high compute and execution runs at high. The [reasoning sandwich](../agent-design/reasoning-budget-allocation.md) is the canonical front-loaded shape and the only one with published benchmark numbers: extra-high planning, high execution, extra-high verification scored 66.5% on Terminal Bench 2.0, beating uniform high (63.6%) and continuous maximum (53.9%, penalized by timeouts) ([LangChain — Improving deep agents with harness engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).

Front-loaded allocation works when planning errors propagate through every later turn and verification failures would be falsely reported as success — concentrating compute where ambiguity is highest beats spreading it uniformly. It fails when the phases are not separable: exploratory debugging interleaves planning and execution, so the sandwich degrades to noisy uniform compute with routing overhead.

Even split is the right default for loops without clean phases — bulk refactors, mechanical migrations, multi-file lint-and-fix passes. The work is execution-dominated; there is no planning phase that warrants extra compute and no verification phase distinct from "run the tests."

## Budget telemetry inside the loop

Loops that hit the cap silently usually emit a final tool-less summary call, which downstream consumers may misread as completion. The [goal-driven autonomous loop](goal-driven-autonomous-loop.md) documents both production patterns that prevent this: per-turn telemetry that injects `Tokens used / Token budget / Tokens remaining` into the continuation prompt, and a wind-down template (`budget_limit.md`) that fires at the cap and forbids the goal-complete tool call. The Claude Agent SDK's `error_max_turns` / `error_max_budget_usd` result subtypes are the harness-side signal, but they fire after the cap, not before it — the hermes-agent project tracks tiered budget-pressure warnings as a missing primitive ([hermes-agent #414](https://github.com/NousResearch/hermes-agent/issues/414)).

## Why it works

Planning errors propagate while execution errors do not — a wrong plan in turn 1 contaminates every later turn, but a wrong tool call in turn 5 is local. Different phases make structurally different cognitive demands ([Bui, 2026 §2.2.5](https://arxiv.org/abs/2603.05344)). Concentrating compute where ambiguity is highest beats spreading it uniformly when the phases are separable; the LangChain benchmark gap (66.5% sandwich vs 63.6% uniform high) is the empirical floor under that mechanism. The gap is small, which is why front-loading is a default only when planning and verification are clean phases — otherwise routing overhead eats the gain.

## When this backfires

- Iteration cap on a loop with no grader. The cap fires regardless of progress, so the agent stops mid-deliverable with no recovery prompt. The fix is a wind-down template (the Codex `budget_limit.md` pattern), not a higher cap.
- Flat per-turn token budget on a single-session loop. Late turns are several times more expensive than early ones due to accumulated context. A 1,000-token-per-turn cap that works at turn 1 is broken by turn 8. Use a whole-loop budget with per-action scoring instead.
- Token budget on a loop running across model versions. Tokens-per-decision changes between Sonnet 4 and Opus 4.7, so a token budget that bound correctly on one model fires unpredictably on the next. Iteration caps are portable; token budgets need re-tuning on every model upgrade. Anthropic's `outcome` ships iteration-cap-only ([default 3, max 20](https://platform.claude.com/docs/en/managed-agents/define-outcomes)) for this reason.
- Front-loaded budget on tasks with no clean planning phase. The reasoning-sandwich gap (66.5% vs 63.6%) requires planning, execution, and verification to be separable. Exploratory debugging interleaves all three; front-loading wastes the planning budget on what becomes mid-trajectory work.
- Wall-clock cap on background or batch work. A wall-clock primitive forces premature stop when the loop is not user-facing. Use iteration count or cost budget instead.
- All three primitives set high "as a safety net." Budgets that never bind teach the team nothing and surface no signal when the loop is structurally broken.

## Example

A research agent loop running 8-turn multi-hop questions with `max_turns=8` and a $2.00 cost budget. The harness exposes `(remaining_turns, remaining_tokens)` to the loop every turn.

Even-split allocation gives each turn the same reasoning effort and the same retrieval budget. Total cost lands near the cap; some turns retrieve when commit was the right action and vice versa.

Front-loaded allocation by phase:

```text
Turn 1 (planning):      effort=xhigh, retrievals=0  — decompose the question
Turns 2-6 (execution):  effort=high,  retrievals=4  — fan out, retrieve, intermediate reasoning
Turn 7 (verification):  effort=xhigh, retrievals=1  — check evidence supports the answer
Turn 8 (commit):        effort=high,  retrievals=0  — final answer
```

The planning turn uses extra-high reasoning so the decomposition is sound — every later retrieval is wasted if the plan is wrong. The verification turn uses extra-high reasoning because a missed inconsistency produces false completion. Execution turns run at high — they follow the decomposition. This mirrors the [reasoning sandwich](../agent-design/reasoning-budget-allocation.md) applied to a loop rather than a single-shot agent.

If the harness exposes `(remaining_turns, remaining_tokens)`, a [dual-budget controller](../agent-design/dual-budget-control-search-agents.md) can override the static phase allocation: at turn 7 with `(remaining_turns=2, remaining_tokens=400)`, a `commit` action with VOI/cost = 2.75 fires before the planned verification retrieval (VOI/cost = 0.81), because the marginal cost of running out of budget exceeds the marginal value of one more retrieval. Static phase allocation and dynamic controller-state allocation compose.

## Key Takeaways

- Loop budgeting is two decisions: which primitive caps the loop, and how budget is allocated across turns within the cap.
- Iteration caps are portable across model versions; token budgets need re-tuning on every model upgrade; wall-clock caps are right only when latency SLOs bind harder than cost.
- Per-turn cost in a single-session loop is not uniform — context accumulates, so a flat per-turn token cap mis-prices late iterations. Budget across the whole loop and expose `(remaining_turns, remaining_tokens)` to the controller.
- Front-loaded allocation (the [reasoning sandwich](../agent-design/reasoning-budget-allocation.md)) beats uniform compute by 66.5% vs 63.6% on Terminal Bench 2.0 when planning, execution, and verification are clean phases — and ties or loses when they are not.
- One binding budget primitive beats three slack ones — a budget that never fires teaches the team nothing.

## Related

- [Agent Loop Go/No-Go: When Looping Earns Its Cost](agent-loop-go-no-go-gate.md) — the upstream gate; this page assumes the loop has already earned its place
- [Reasoning Budget Allocation: The Reasoning Sandwich](../agent-design/reasoning-budget-allocation.md) — the canonical front-loaded shape across planning, execution, and verification phases
- [Goal-Driven Autonomous Loop with Budget Cap](goal-driven-autonomous-loop.md) — production example of per-turn budget telemetry plus a wind-down template at the cap
- [Dual-Budget Control for Search Agents](../agent-design/dual-budget-control-search-agents.md) — when the harness exposes `(remaining_tool_calls, remaining_tokens)`, score actions by VOI per unit budget
- [Convergence Detection in Iterative Agent Refinement](convergence-detection.md) — early-stopping that complements a hard budget cap with a progress-based exit
- [Loop Strategy Spectrum: Accumulated vs Fresh Context](loop-strategy-spectrum.md) — accumulated-context loops are where the per-turn-cost-growth mechanic bites hardest
- [Unbounded Agent Feedback Paths (Infinite Agentic Loops)](../anti-patterns/unbounded-agent-feedback-paths.md) — the failure class that results when the bound this page sizes is missing or placed off the actual feedback path
