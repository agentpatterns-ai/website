---
title: "Agent Loop Go/No-Go: When Looping Earns Its Cost"
term: "Agent Loop Go/No-Go Gate"
description: "Four-condition decision gate for whether to convert a manual prompting task into an automated agent loop, before designing one."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - loop ROI gate
  - agent loop economic decision
last_reviewed: 2026-06-22
maturity: adopted
---

# Agent Loop Go/No-Go: When Looping Earns Its Cost

> An agent loop earns its cost only when task cadence, automated verification, absorbable token budget, and real tooling all hold simultaneously.

## The Decision Gate

This is the upstream question to every loop-mechanics page on this site — [Loop Strategy Spectrum](loop-strategy-spectrum.md), [Ralph Wiggum Loop](ralph-wiggum-loop.md), [Goal-Driven Autonomous Loop](goal-driven-autonomous-loop.md), [Evaluator-Optimizer](evaluator-optimizer.md). Those answer *how* to build a loop. This answers *whether* you should.

A loop carries fixed setup costs (a verifier sub-agent, persisted state, a skill capturing project conventions, a schedule or trigger) and per-iteration token waste (re-reads, retries, exploration that does not converge). A single prompt-driven session carries none of that overhead. The loop pays back only when the same task shape recurs enough to amortise the setup *and* the per-iteration waste stays below the cost of doing the task yourself in a prompt session.

Four conditions must all hold:

| Condition | What it means | If absent |
|----------|----------------|-----------|
| **Task cadence** | The same task shape recurs at least roughly weekly | Setup never amortises — one-shot prompt is cheaper |
| **Objective verification** | An external gate (test, build, typecheck, lint, CI status) can grade "done" without an LLM's opinion | The loop stops on vibes; maker grades own homework |
| **Absorbable token budget** | You can spend on retries, re-reads, and exploration without it changing behaviour | Per-iteration waste dominates the savings |
| **Real tooling** | The agent has logs, a reproduction environment, and can run the thing it writes | Loop iterates on a stale view; convergence is theatre |

Fail any one and the loop's marginal cost stays at or above the prompt-session cost forever — there is no number of iterations that fixes it.

## Why It Works

The mechanism is fixed-cost amortisation. A loop carries a fixed cost (verifier, skill, state schema, scheduler glue) plus per-task waste (blind exploration, retries); a prompt session carries only per-task cost. So a loop wins only when the fixed cost amortised across N runs plus per-iteration waste falls below an attentive prompt session at the same per-task cost. Anthropic's [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) makes this concrete: "Only adopt agents when simpler approaches demonstrably underperform."

The four conditions each close one way the inequality flips: cadence sets N, verification removes human grading cost, budget absorbs per-iteration waste, tooling keeps the verifier ground-truth instead of advisory. Addy Osmani's [Loop Engineering](https://addyo.substack.com/p/loop-engineering) names the same mechanism from the practitioner side: "without skills the loop re-derives your whole project from zero every cycle, with skills it kind of compounds."

## The Operating Metric: Cost Per Accepted Change

Tokens-spent is the wrong unit. Tasks-attempted is the wrong unit. **Cost per accepted, merged change** is the unit that captures both the loop's throughput and the reviewer time it actually consumes.

An empirical study of 567 Claude Code pull requests across 157 open-source projects ([Bui et al. (2025), arxiv 2509.14745](https://arxiv.org/abs/2509.14745)) measured the baseline: 83.8% of agent-assisted PRs are merged, but **only 54.9% are merged without further modification** — ~45% of "successful" agent output still consumed reviewer time. Below ~55% no-modification acceptance, the loop is doing the review work it was supposed to remove. The same metric captures the inverse failure: a smarter model with fewer turns at higher per-token cost can be cheaper per accepted change than a cheaper model burning 80 tool calls.

## Good Fits and No-Go Work

The four conditions sort tasks cleanly.

| Good fit | Why it passes |
|----------|----------------|
| **CI failure triage** | Recurs daily; verification is "did the test pass on retry"; bounded token budget per run; agent runs the tests itself |
| **Dependency bumps** | Recurs weekly; verification is build + test green; budget bounded; agent runs the build |
| **Lint-and-fix passes across a repo** | Recurs whenever the rule changes; verification is the linter; budget known; agent runs the linter |
| **Doc generation from code** | Recurs on every API change; verification is a doc-build pass; budget bounded; agent runs the build |

| No-go | Why it fails |
|-------|---------------|
| **Architecture rewrites** | No automated verifier for "is the design right"; judgment-call done condition |
| **Auth and payments** | Verification needs human security review; cost of a wrong merge is catastrophic |
| **Production deploys** | Verification is the real environment, not a test suite; bounded blast radius matters more than cadence |
| **Solo developer on a metered plan, sub-weekly cadence** | N is too small to amortise setup; single prompt session is strictly cheaper |
| **Review-bound teams** | Multiplying output past the review ceiling makes the queue longer, not faster |

The no-go list maps onto pages already on this site — [comprehension-debt.md](../anti-patterns/comprehension-debt.md) for what happens when shipped-faster outruns understood; [trust-without-verify.md](../anti-patterns/trust-without-verify.md) for the verification-vibes failure; [cost-aware-agent-design.md](cost-aware-agent-design.md) for the budget side.

## When This Backfires

The gate itself can pass on tasks that should still not be looped.

- **Review capacity is the team's actual bottleneck.** A loop multiplies output by N; if reviewers were already the constraint, the loop's effective throughput is the reviewer's throughput minus the loop's triage overhead. [Addy Osmani — Loop Engineering](https://addyo.substack.com/p/loop-engineering) is explicit on this: "the worktrees take away the mechanical collision but YOU are still the ceiling, your review bandwidth decides how many you can actually run, not the tool." A passing four-condition score does not override a saturated reviewer.
- **Economics flip on plan type.** The same loop is "obviously worth it" on an unmetered enterprise plan and "reckless" on a metered consumer plan. Single autonomous refactoring runs in the wild have produced $4,200 weekend bills for one developer ([Vantage — Hidden Cost Driver in Agentic Coding](https://www.vantage.sh/blog/agentic-coding-costs)). The cadence-and-verification check passes; the budget check is doing the real work, and it has to be answered honestly.
- **Comprehension debt accelerates.** A loop ships code faster than you can read it; the gap between what exists and what the team understands grows in proportion to loop throughput. The [comprehension-debt](../anti-patterns/comprehension-debt.md) anti-pattern documents this directly — an [Anthropic RCT with 52 junior engineers](https://www.anthropic.com/research/AI-assistance-coding-skills) measured a 17-percentage-point comprehension drop for code-generation-delegation users versus conceptual-inquiry users. A loop is delegation by default.
- **Verifier is a second LLM grading the first.** The maker-grades-own-homework failure does not disappear when you split it across two models with shared training distribution. Osmani's framing — "the model that wrote the code is way too nice grading its own homework" — only resolves when the verifier is *external and objective*: a test runner, a typechecker, a CI gate. An LLM-as-judge that lacks ground truth is theatre, and the loop's stop condition is meaningless.
- **The opposite is sometimes the right call.** A reasonable practitioner can defend "stay in prompt-driven sessions until you have measured the same task shape recurring at least weekly" as the default — most engineers see fewer than three weekly-recurring task shapes, and a gate that passes on borderline cases produces too many loops the team cannot maintain. The gate exists to be honest about the conditions; it is not an instruction to build.

## Example

A team considers building a loop for two candidate tasks. The gate sorts them in opposite directions.

**Task A — nightly dependency bump pass on a monorepo**

| Condition | Score |
|----------|--------|
| Cadence | Pass — runs every night; dozens of dependency updates per week |
| Verification | Pass — `make test && make build` is objective; bounded retry on failure |
| Budget | Pass — repo CI already provisions tokens; per-run cost is known and small |
| Tooling | Pass — agent runs the same `make` targets a developer would |

Verdict: build the loop. The operating metric to instrument is cost-per-accepted-PR — track it weekly and pull the loop if no-modification acceptance falls below the ~55% Bui baseline.

**Task B — refactor the payment-service authorization layer**

| Condition | Score |
|----------|--------|
| Cadence | Fail — this is a one-time architectural change |
| Verification | Fail — "is the new authorization model correct" is a judgment call, not a test |
| Budget | Pass — budget exists, but irrelevant given the other fails |
| Tooling | Pass — but irrelevant |

Verdict: do not loop. A single prompt-driven session with a domain expert reviewing each step is strictly cheaper and safer. The loop's setup cost would be paid against N = 1, and the verifier would be vibes.

## Key Takeaways

- A loop earns its cost only when **all four conditions hold**: weekly-or-better cadence, objective external verification, absorbable token budget, real tooling for the agent.
- **Cost per accepted change** is the operating metric; tokens-spent and tasks-attempted both miss the reviewer-time leg of the cost.
- The break-even threshold sits near the [Bui et al. (2025)](https://arxiv.org/abs/2509.14745) baseline of ~55% no-modification acceptance; below that, the loop is doing the review work it was meant to remove.
- Review capacity overrides a passing score — multiplying output past the reviewer ceiling lengthens the queue rather than shortening it.
- Plan economics flip the same loop from worthwhile to reckless; the budget condition has to be answered for *your* token rate, not the practitioner-blog author's.

## Related

- [Loop Strategy Spectrum: Accumulated vs Fresh Context](loop-strategy-spectrum.md) — once the gate passes, this page chooses *how* the loop carries context between iterations
- [The Ralph Wiggum Loop: Fresh-Context Iteration Pattern](ralph-wiggum-loop.md) — the canonical fresh-context loop mechanic, downstream of this gate
- [Goal-Driven Autonomous Loop](goal-driven-autonomous-loop.md) — the goal-condition variant of looping, also downstream of this gate
- [Evaluator-Optimizer Pattern](evaluator-optimizer.md) — the split-the-maker-from-the-checker structure that closes the verification condition
- [Cost-Aware Agent Design](cost-aware-agent-design.md) — broader cost-control patterns once a loop is approved
- [Comprehension Debt: When Developers Understand Less of Their Own Codebase](../anti-patterns/comprehension-debt.md) — the anti-pattern that emerges when the gate is skipped and the loop ships faster than the team reads
