---
title: "Stateful Iteration State-Carry: Typed Persistent State for Long Agent Loops"
term: "Stateful Iteration State-Carry"
description: "Carry typed persistent state across agent iterations through a state-read tool instead of rebuilding context from message history each turn — converts O(n²) total token cost to O(n) for long loops with growing observations."
aliases:
  - typed persistent agent state
  - remember don't re-read pattern
  - state-carry across iterations
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-16
maturity: emerging
---

# Stateful Iteration State-Carry: Typed Persistent State for Long Agent Loops

> Carry agent state across iterations through a state-read tool instead of replaying the full transcript each turn — converts O(n²) loop token cost to O(n).

**Learn it hands-on:** [Remember, Don't Re-Read](https://learn.agentpatterns.ai/context-engineering/remember-dont-re-read/) — guided lesson with quizzes.

## When This Pattern Applies

This refactor pays back only under specific conditions. Apply it when **all** of the following hold ([Jabbarvaziri, 2026](https://arxiv.org/abs/2606.14945)):

- The loop is **long-horizon**: tens of iterations per run, not single-digit conversational turns.
- Per-iteration observations are **large**: source code, benchmark output, full search results — not single scalars.
- The loop runs **unattended in production**: the engineering cost of typed state and a checkpointer is amortised across many runs.
- The agent's next decision usually needs only a **subset** of prior state, not the whole trajectory.

If any condition is missing — short loops, tiny observations, exploratory single-shot runs — the simpler stateless approach with [prompt caching at the provider tier](static-content-first-caching.md) hits the same cost line for less engineering work.

## The Cost Curve the Pattern Targets

A stateless ReAct loop appends each Thought-Action-Observation triple to the message history, then re-sends the whole transcript on the next call. Per-call input grows linearly with step `n`, and total cost across `N` steps is **O(N²)** — every prior observation is re-billed on every subsequent inference. The pattern is mechanical and reproducible across providers ([Augment Code, 2026](https://www.augmentcode.com/guides/ai-agent-loop-token-cost-context-constraints); [Towards Data Science, 2026](https://towardsdatascience.com/your-react-agent-is-wasting-90-of-its-retries-heres-how-to-stop-it/)).

Stateful state-carry lifts the experimental record out of the transcript into a typed object that lives outside the prompt. The agent **reads** specific fields via a tool only when the current decision needs them. The conversation window stays approximately fixed-size; total cost across `N` steps becomes **O(N)** ([Jabbarvaziri, 2026](https://arxiv.org/abs/2606.14945)).

The paper measured both regimes on two benchmarks:

| Task | Iterations | Stateless tokens | Stateful tokens | Reduction |
|------|------------|------------------|-----------------|-----------|
| Hyperparameter tuning (small observations) | 15 | 24,465 | 2,492 | **90%** |
| Code optimization (large observations) | 40 | 1,275K | 627K | **52%** |

Optimization quality was comparable on both tasks — token reduction did not degrade outcomes ([Jabbarvaziri, 2026](https://arxiv.org/abs/2606.14945)).

## How To Apply It Tool-Agnostically

The paper's reference implementation uses LangGraph, but the pattern — state lives outside the prompt, accessed by tool call — is framework-agnostic, and resembles a [code-native memory substrate](../agent-design/code-native-memory-substrates.md) specialised for iteration loops:

1. **Define a typed state object** for the loop's experimental record — current best metric, last hyperparameter set, recent failure traces, working files. Keep fields minimal; every additional field becomes another schema migration ([Mem0, 2026](https://mem0.ai/blog/langgraph-tutorial-build-advanced-ai-agents)).
2. **Expose state through tools** the agent can call: `read_state(field)`, `update_state(field, value)`, `list_recent_attempts(n)`. The agent invokes these when it needs context, instead of expecting full history in the transcript.
3. **Persist state via a checkpointer**, not in-memory. InMemorySaver loses everything on restart and undermines durability ([Towards AI, 2026](https://pub.towardsai.net/getting-started-with-langgraph-build-a-stateful-ai-agent-not-another-prompt-chain-ccedc9b6e9ad)); production loops use Redis, Postgres, or DynamoDB-backed stores ([AWS, 2026](https://aws.amazon.com/blogs/database/build-durable-ai-agents-with-langgraph-and-amazon-dynamodb/)).
4. **Trim the message window to recent turns only**. The state object — not the transcript — is the source of truth for prior iterations.

## Why It Works

The causal mechanism is purely about **where state lives**, not about model reasoning. A stateless loop encodes the experimental record in the message transcript, which the inference call must re-process every turn — the provider re-bills the full prefix on each call. A stateful loop encodes the same record in a typed object outside the prompt and exposes it through tools, so per-call input is bounded by the working set the current step touches, not by cumulative history. The asymptotic effect (`O(N²) → O(N)`) is a direct consequence of decoupling the experimental record from the transcript ([Jabbarvaziri, 2026](https://arxiv.org/abs/2606.14945)). The 90% and 52% reductions are not optimisations on top of the same architecture — they are the gap between a quadratic and a linear cost curve at finite iteration counts.

## When This Backfires

Conditions under which the pattern is worse than the alternative:

- **Short loops with stable prefixes**. Below ~10 iterations, [prompt caching at the provider tier](static-content-first-caching.md) already converts the dominant cost line to roughly O(1) for the static portion — Anthropic charges ~10% of input price on cache hit, OpenAI ~50% ([NeuralTrust, 2026](https://neuraltrust.ai/blog/prompt-caching)). The stateful refactor adds engineering cost the cached stateless loop avoids.
- **State schema churn**. When the experimental shape changes often — new fields, renamed metrics, restructured observations — every schema change risks breaking persisted checkpoints. Projects have failed because "every additional field increases complexity exponentially" and the state object became a monolith ([Mem0, 2026](https://mem0.ai/blog/langgraph-tutorial-build-advanced-ai-agents)).
- **Concurrent / multi-replica execution without isolation**. Shared state corrupts silently under concurrent writes; the failure surfaces several state transitions downstream from the cause, making root-cause hard ([Focused.io, 2026](https://focused.io/lab/persistent-agent-memory-in-langgraph)).
- **Tasks that need the full trajectory**. Causal debugging, exploratory branching, transcript replay — pruning to typed state discards the audit trail that made the loop debuggable.
- **In-memory persistence in restart-prone environments**. InMemorySaver loses everything on restart; durable state requires a Postgres/DynamoDB backend, shifting cost from tokens to operations ([AWS, 2026](https://aws.amazon.com/blogs/database/build-durable-ai-agents-with-langgraph-and-amazon-dynamodb/)).

## Contrast With Prompt Caching

The two approaches attack the same cost curve from different layers:

| | Prompt caching | Stateful state-carry |
|---|---|---|
| **Where the fix lives** | Provider infra | Application code |
| **Engineering cost** | Order static content first; lock tool schemas | Design typed state, write state-read tools, operate a checkpointer |
| **What gets cheaper** | Static prefix (system prompt, tool defs) | Growing observation history |
| **Best for** | Stable prefix, short to medium loops | Long loops, large observations |
| **Failure mode** | Cache misses on prefix mutation | State schema churn, concurrent corruption |

They are complementary at the boundary case: a long-horizon stateful loop still benefits from a cached static prefix on the residual transcript. They are competing for short loops with stable observations.

## Key Takeaways

- The token saving comes from where state lives, not from changing the model — typed state outside the prompt makes per-iteration input independent of step count.
- Empirical savings scale with loop length and observation size: 90% at 15 iterations with small observations, 52% at 40 iterations with large observations.
- The refactor only pays back for long unattended loops with large observations; short or exploratory loops should reach for prompt caching first.
- State schema discipline matters as much as the lift itself — every added field becomes a migration surface, and shared state under concurrency corrupts silently.

## Related

- [Static Content First for Cache Hits](static-content-first-caching.md) — the prompt-caching alternative that targets the same O(n²) curve at the provider tier
- [Elastic Context Orchestration](elastic-context-orchestration.md) — per-turn vocabulary (Skip, Compress, Snippet, Rollback, Delete) for selective context retention in ReAct loops
- [Context Compression Strategies](context-compression-strategies.md) — tiered offloading and summarisation for long-running agents
- [Code-Native Memory Substrates for Coding Agents](../agent-design/code-native-memory-substrates.md) — typed external memory for code-bearing agents, from a different angle
- [Autonomous Research Loops](../training/foundations/autonomous-research-loops.md) — the curriculum module that puts loop architectures and termination design together
