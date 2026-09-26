---
title: "Recurring Control Belongs in Harness Code, Not Context"
term: "Recurring Control in Harness Code"
description: "Move an agent's repeated control decisions out of per-task model context into harness code, once task volume, a regression gate, and a sandbox justify it."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - harness growth
  - code-first agent control
  - persistent control code
last_reviewed: 2026-09-23
maturity: emerging
---

# Recurring Control Belongs in Harness Code, Not Context

> Put an agent's repeated control into harness code and keep model calls for task-specific judgment, where the family repeats often enough to pay.

An agent serving one task family rebuilds the same control on every run: refine the query, filter the observation, check progress, recover from the error, stop. A harness that hands those decisions back to the model pays for each one twice, because "every decision incurs another inference call, grows context, and adds prompts, observations, and outputs to a growing execution history" ([Li et al., arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)). Written as code, the same decision is a function call. Across two benchmarks and three deployment models, a harness grown this way "reduces LLM calls by 76.0–91.8% and online cost by 74.4–98.6% across the six settings" against a tool-calling agent ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)).

## When this applies

That saving is a property of one setup, not of the idea. Check all three conditions before building anything.

- Volume inside one task family. The reported cost excludes the expensive half of the work: "Total Online Cost includes deployed-agent LLM calls only, excluding evaluator and offline-optimizer calls" ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)). GPT-5.6-terra and GPT-5.4 wrote the harnesses at high reasoning effort over 200 training tasks per benchmark, while the deployed agents ran gpt-oss-120b, gpt-oss-20b, and Qwen3.5-4B. The authors say what that leaves out: "Its value depends on reusing the learned harness enough to offset offline optimization" ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)).
- A regression gate that can reject a whole repair sequence. Local gains do not compound on their own. A continual-learning study of three harness optimizers found GEPA's optimized agent fell to 54.5% once new tasks arrived, below the 56.8% unoptimized baseline, while one of the three kept improving across rounds; compounding appeared "only when regression control was built into the optimization loop" ([Wang et al., arXiv:2607.14004v1](https://arxiv.org/abs/2607.14004v1)).
- A sandbox for the code you are about to run. The primary source closes on it: "Real deployment also requires sandboxing, explicit permission boundaries, and validation of generated code" ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)).

Miss one and the offline optimizer run buys you a program to maintain and nothing else.

## Drawing the line

Sort decisions by whether they change with the task. Behavior that repeats identically is a code candidate; behavior that turns on what this task says stays with the model. The reference method directs "code toward deterministic, reusable control" — "parsing, validation, state updates, conditional query refinement, error recovery, and stopping" — "while retaining LLM calls for semantic interpretation, synthesis, fuzzy comparison, and answer generation" ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)).

Two rules keep that code from degenerating into a lookup table. Scope every change to the functions a real failure touched, and refuse any control path that hard-codes an answer. The reference implementation enforces both: "the optimizer may modify only the entry function and functions invoked by a supplied failure trace", and generated code "may not encode task identifiers, expected answers, or fixed solutions" ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)). Write the harness by hand and both rules still hold.

## Why it works

A control decision made in code costs one function call and adds nothing to the context the next inference call must read, so the saving accumulates across a trajectory rather than arriving as a per-call discount ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)). The effect therefore grows as the deployment model shrinks. On WebArena-Verified "its mean success remains within a narrow 44.7–45.3% range across all three deployment models", while the tool-calling baseline falls from 30.0% with a 120B model to 6.7% with a 4B one ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)).

A separate mechanism decides whether the code is worth keeping. Scoping each edit to the functions a failure trace touched bounds the search as the program grows, and dropping that scope is the most damaging ablation reported: "Removing function-level guidance halves final success from 36% to 18%" ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)). A held-out gate then accepts a repair sequence only when aggregate success does not fall, because "a repair can solve current failures while damaging behavior acquired earlier". Without it, gate success "rises to 30% but then falls to 16%" ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)).

## When this backfires

- The task distribution moves. The WebArena-Verified harness "adds specialized handlers for diverse Shopping, Reddit, and Map tasks" ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)). Handlers that specific are pinned to the sites they grew against. Redesign a page and the branch keeps running and keeps returning something, with nothing naming the cause.
- The family is not really one family. The evidence covers two benchmarks with 200 training tasks each ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)). Below the volume that amortizes one optimizer run, the pipeline, the sandbox, and the gate are all cost with nothing offsetting them.
- The proposer invents failures. A success-first gate accepts an edit that changes no outcome, which is the shape of a fabricated fix. One controlled study planted a guardrail for a failure class that provably never occurred, and the proposer enabled it "in 15/60 runs, versus 0/60 on featureless input", calling the result "a fix for a failure that never happened, invisible to suppression-only acceptance" ([Wang et al., arXiv:2607.13083v1](https://arxiv.org/abs/2607.13083v1)). Inside an add-only loop these pile up as dead control nobody can attribute.
- Scaffolding was not the binding constraint. Where the model has headroom below its ceiling, raising reasoning effort can buy reliability more cheaply than adding structure around it ([Reasoning Effort Over Tool Scaffolding](reasoning-effort-over-tool-scaffolding.md)).
- Nobody owns the generated code. It runs in your process, no engineer wrote it, no review approved it, and it grows every round.

## Example

The single setting where the split matters most is WebArena-Verified on the 4B deployment model, because that is where the baseline has least capacity to reconstruct control per task ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)):

| WebArena-Verified, Qwen3.5-4B | Tool-Calling | Grown harness |
|---|---|---|
| Success rate | 6.7% | 45.3% |
| LLM calls per task | 37.8 | 5.4 |
| Input tokens per task | 1,355.6k | 13.7k |
| Cost per 50-task run | $7.26 | $0.10 |

The two middle rows are the mechanism and the top row is its consequence: "The largest gain therefore appears with the smallest deployment model." That is the best cell, so read it next to the whole set, where the method "improves mean success over Tool-Calling in five settings and remains within 0.7 pp. in the sixth" ([arXiv:2609.26760v1](https://arxiv.org/abs/2609.26760v1)). Every number is a mean over three evaluation runs of one method with one optimizer, so carry away the direction and measure your own.

## Key Takeaways

- Sort your agent's decisions by whether they change with the task. Everything that does not is a candidate for code.
- Price the optimizer, not just the saving. A published cost reduction that excludes the model which wrote the harness is half an answer.
- A regression gate is part of the pattern, not a hardening step. Of three optimizers benchmarked head to head, only the one carrying regression control kept improving across rounds.
- Watch for edits that fix nothing. A gate keyed on outcomes cannot see a guardrail for a failure that never happened.
- Generated control code is still code in your runtime. Sandbox it, review it, and keep it attributable.

## Related

- [Harness Hill-Climbing: Eval-Driven Iterative Improvement of Agent Harnesses](harness-hill-climbing.md) — the manual counterpart, where a person makes one change per eval round instead of an optimizer proposing them.
- [Observability-Driven Harness Evolution](observability-driven-harness-evolution.md) — attributes each harness edit to a prediction, which is the control this pattern's outcome gate cannot supply.
- [Compiled Specialist Agents: Muscle Memory for Recurring Intent](compiled-specialist-agents.md) — compiles a recurring user intent into a whole agent rather than recurring control into the harness.
- [Continual Learning for AI Agents: Three Layers of Knowledge Accumulation](continual-learning-layers.md) — the routing question one level up, deciding whether a fix belongs in the model, the harness, or the context.
- [Deterministic Fast Paths: Answer Without a Model Call](deterministic-fast-paths.md) — the same instinct applied per request, skipping the model on a signal retrieval already computed.
