---
title: "Temporal Token Routing: Batch and Flex Tiers for Non-Urgent Work"
term: "Temporal Token Routing"
description: "Route non-urgent inference into asynchronous batch and flex tiers — Anthropic Message Batches and OpenAI Batch both ship a 50% discount with a 24-hour SLA, paid for in latency, expiry risk, and engineering overhead."
tags:
  - token-engineering
  - cost-performance
  - tool-agnostic
aliases:
  - batch API routing
  - off-peak inference routing
  - latency-tiered token routing
last_reviewed: 2026-06-29
maturity: adopted
---

# Temporal Token Routing: Batch and Flex Tiers for Non-Urgent Work

> Route non-urgent inference into batch and flex tiers — both providers cut token cost 50% in exchange for asynchronous turnaround and expiry risk.

Temporal token routing is the "right time" lever in [token engineering](index.md): for any call where the result is not needed in the next second, the synchronous API is the wrong price. Anthropic's Message Batches and OpenAI's Batch API both bill the same work at half the standard rate, completing asynchronously within a 24-hour SLA. OpenAI also exposes Flex processing — an interactive but pre-emptible tier at the same batch-priced rate. The technique is choosing which workload class belongs in which tier, and absorbing the failure modes that come with the discount.

## The two cost primitives

Both providers ship the same primary trade: defer the result, halve the bill.

| Tier | Discount | Turnaround | Best for |
|------|----------|-----------|----------|
| Anthropic Message Batches | 50% off synchronous Messages | "Most batches complete within 1 hour"; 24h expiry ([Anthropic — Message Batches](https://platform.claude.com/docs/en/build-with-claude/batch-processing)) | Bulk evals, embeddings, content moderation, dataset enrichment |
| OpenAI Batch | 50% off synchronous | 24h completion SLA ("often more quickly"); up to 50,000 requests per batch, 200 MB file, 2,000 batches/hr ([OpenAI — Batch](https://developers.openai.com/api/docs/guides/batch)) | Same workload shape; supports chat, embeddings, completions, moderations, image, video endpoints |
| OpenAI Flex processing | Tokens billed at Batch rates | Real-time API, but slower and pre-emptible; 429 "Resource Unavailable" returned without charge on shortage ([OpenAI — Flex](https://developers.openai.com/api/docs/guides/flex-processing)) | Interactive paths that can tolerate seconds-to-minutes of added latency and occasional retry |

Flex is the closest thing on the market today to an interactive latency-tiered discount, and it is the right lever for non-batch work that still does not need premium responsiveness — model evaluations driven inline, lower-priority agentic loops, data enrichment behind a queue. It is not dynamic spot-style per-token pricing; no major provider has shipped that as of mid-2026.

## When this works

Match the workload to the tier by asking one question: how long can this call wait without breaking something downstream?

- Sub-second — synchronous standard tier. Interactive coding, voice, anything blocking a human or a tool-calling agent loop.
- Seconds to a few minutes — Flex (where available). Background evals, data enrichment, low-priority agent steps. Caller must handle 429 "resource unavailable" by retrying or falling back to standard.
- Up to ~24 hours — Batch. Overnight evals, doc refreshes, bulk refactors that produce diffs for human review the next day, large-scale content moderation, embedding backfills, research passes over historical data.

The decision is not about volume — a single high-cost overnight eval belongs in batch the same way 50,000 embedding requests do. It is about whether anything wall-clock-sensitive consumes the output.

## Why it works

Inference compute is highly bursty. Provider GPU fleets see large diurnal and within-hour swings in synchronous load, and the marginal cost of serving a request during a trough is far below the average. Exposing a queue with a long SLA lets the provider defer work into capacity valleys and price it at marginal cost — the ~50% discount is the user-facing manifestation of that arbitrage. Anthropic's own docs make the trade explicit: "processing may be slowed down based on current demand and your request volume" with more expirations under load ([Anthropic — Rate Limits §Message Batches](https://platform.claude.com/docs/en/api/rate-limits)). Flex extends the same principle to interactive traffic — accepting pre-emption (429 "resource unavailable") is the user-side signal that the request is competing for the same trough capacity ([OpenAI — Flex](https://developers.openai.com/api/docs/guides/flex-processing)).

The 24-hour SLA, then, is not a generous deadline; it is the price ceiling. The provider promises to serve eventually, not promptly. That distinction governs every workload-fit decision below.

## When this backfires

The 50% discount is not free. Five conditions push the breakeven the other way.

- Interactive coding loops — any path where a human or another agent waits on the result. Even Flex's "few seconds extra" can break a multi-tool agent loop; Batch's 24h SLA makes it impossible.
- Chained batch dependencies — when one batched output feeds the next call's prompt, pipelining serializes the batch latency. Two chained one-hour batches take two hours minimum, with a long tail when either job slips toward the 24-hour expiry.
- Volume below the engineering crossover — building submit-poll-retry-resubmit logic, plus the operational overhead of monitoring expirations and stuck "finalizing" states, costs engineer time. Real-world reports document batches expiring at the 24h mark and getting stuck in "finalizing" indefinitely ([OpenAI community](https://community.openai.com/t/batch-api-stucks-at-in-progress-state-and-expire-after-24h/1358833)). For low-hundreds-of-dollars monthly spend, the discount saves less than a day of that work.
- Hard wall-clock deadlines under 24 hours — an overnight eval that must land before a 9am standup cannot tolerate the long tail of expirations under demand-driven slowdown. Either build for resubmission or stay on the synchronous tier and accept the full price.
- Caching-dominated workloads — when 80%+ of input tokens are cache hits on the synchronous path, the batch discount is a smaller marginal win than tightening cache hit-rate further. [Prompt caching architectural discipline](../context-engineering/prompt-caching-architectural-discipline.md) is the cheaper lever to reach for first.

A useful rule of thumb: route to batch only when the workload is both deferrable and high-volume enough that the 50% saving covers the cost of the queue-management pipeline. Otherwise, get sync cheaper through caching, smaller models, or lean context before reaching for temporal routing.

## Example

A nightly documentation-refresh job that re-summarizes 5,000 internal docs.

Before — synchronous tier:

```python
# 5,000 sync calls, full list price, each blocks until the next returns
for doc in docs:
    summary = client.messages.create(
        model="claude-sonnet-4",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"Summarize:\n{doc}"}],
    )
    store(doc.id, summary)
```

After — Message Batches:

```python
# One batch submission; poll until complete; 50% off; runs overnight in <1h typical
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": doc.id,
            "params": {
                "model": "claude-sonnet-4",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": f"Summarize:\n{doc}"}],
            },
        }
        for doc in docs
    ],
)
# Poll batch.id until status == "ended"; handle "expired" requests by re-batching
```

The refactor saves 50% on a recurring nightly job, and the queue-management code is amortized across every future bulk job. It would be the wrong move for a one-off 50-doc summarization kicked off ad-hoc — there, the synchronous tier and a tighter cache hit-rate win.

## Key Takeaways

- The "right time" question is one decision: does anything wall-clock-sensitive consume this output? If no, the synchronous tier is overpriced.
- Both Anthropic and OpenAI ship the same primary lever — Batch at 50% off with a 24-hour SLA. OpenAI Flex extends the same pricing to an interactive but pre-emptible tier.
- The 24-hour SLA is a price ceiling, not a deadline — expect long tails and expirations under demand-driven slowdown.
- The 50% discount is offset by submit-poll-retry-resubmit engineering and operational overhead; below a crossover volume, tighter caching beats temporal routing.
- "Dynamic latency-tiered token pricing" beyond Batch and Flex is not a shipped product as of mid-2026 — design for the current tiers, not the predicted ones.

## Related

- [Cost-Aware Agent Design: Route by Complexity, Not Habit](cost-aware-agent-design.md) — the right-model lever that pairs with this right-time lever
- [Idle-Time Speculative Planning for ReAct Agents](../agent-design/idle-time-speculative-planning.md) — what to do with capacity inside a latency-bound loop
- [Background Todo Agent](../agent-design/background-todo-agent.md) — out-of-band work the temporal-routing decision applies to first
- [Programmatic Cloud-Agent Dispatch via REST API and Webhooks](../workflows/programmatic-cloud-agent-dispatch.md) — the orchestration layer that consumes batch and flex tiers
- [Prompt Caching: Architectural Discipline for Agents](../context-engineering/prompt-caching-architectural-discipline.md) — the lever to reach for first on caching-dominated workloads
