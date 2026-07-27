---
title: "Event-Loop Contention in Async Agent Fan-Out"
term: "Event-Loop Contention"
description: "Diagnose the case where adding concurrent agents raises end-to-end latency because per-response CPU work serializes on a single event loop, and separate it from provider throttling and connection-pool exhaustion."
tags:
  - observability
  - multi-agent
  - agent-design
  - tool-agnostic
aliases:
  - event loop starvation under fan-out
  - async fan-out latency inversion
  - serialization bottleneck in agent fan-out
last_reviewed: 2026-07-26
maturity: adopted
---

# Event-Loop Contention in Async Agent Fan-Out

> Fan-out latency rises with agent count when per-response CPU work serializes on one event loop, even while every provider call stays fast.

A fan-out service that slows down as you add agents has at least three plausible causes, and they share one symptom: the provider reports fast completions while your users see rising latency and timeouts. Telling event-loop contention apart from the other two takes one measurement, not a rewrite.

## Three causes, one signature

The symptom alone does not identify the cause:

| Cause | What is happening | Distinguishing evidence |
|---|---|---|
| Event-loop contention | Per-response CPU work runs on the loop's own thread and delays every other coroutine | Event-loop lag climbs with concurrency; the loop is busy rather than waiting |
| Provider throttling | Token-per-minute or request-per-minute limits queue or reject requests | 429 responses, or a local queue that grows while in-flight requests stay flat |
| Connection-pool exhaustion | Requests wait for a free connection in the client pool | In-flight requests plateau exactly at the configured pool limit |

Throttling is the more common cause: agent fan-out generates bursty traffic that trips provider limits, and a client that self-throttles queues requests locally, so users see latency instead of errors ([Portkey on rate limiting for LLM applications](https://portkey.ai/blog/rate-limiting-for-llm-applications/), [TrueFoundry on rate limiting AI agents](https://www.truefoundry.com/blog/rate-limiting-ai-agents-preventing-llm-api-exhaustion)). Check provider error codes and queue depth first.

## The measurement that discriminates

Event-loop lag separates "the loop is busy" from "the loop is waiting". Planck's investigation read `event-loop lag: 230 ms (loop was busy, not waiting)`, which ruled out both throttling and I/O ([Towards Data Science](https://towardsdatascience.com/why-adding-more-ai-agents-made-our-system-slower/)).

CPython ships the check. With asyncio debug mode enabled, any callback that runs longer than `loop.slow_callback_duration` (default 100 ms) is logged ([Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html)). A steady stream of those warnings under load, with provider latency flat, is the confirmation.

## Why it works

An async runtime multiplexes many coroutines onto one thread. While a coroutine awaits I/O the loop runs others, but any code between `await` points holds the thread exclusively. Each completed model call therefore forces a synchronous CPU segment — deserialize the payload, count tokens, validate, apply business logic — before the loop can service the next ready coroutine. Total delay is the sum of those segments, so it grows with concurrency even though the I/O overlaps perfectly ([Towards Data Science](https://towardsdatascience.com/why-adding-more-ai-agents-made-our-system-slower/)).

Under CPython the usual escape hatch is narrow. Asyncio "stalls the entire event loop during the inevitable CPU bound phases of data serialization", and naive thread-pool scaling degrades rather than parallelizes, because the global interpreter lock serializes bytecode ([Mandal and Shende, arxiv 2601.10582](https://arxiv.org/abs/2601.10582)). The docs still route blocking work through `loop.run_in_executor()` ([Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html)), but the durable fix is a separate process — or, on free-threaded builds, a separate event loop per thread ([asyncio and free-threaded Python](https://docs.python.org/3/library/asyncio-threading.html)).

## The fix ladder

Work upward, and stop when loop lag falls:

1. Shrink the payload. Less data to deserialize means a shorter CPU segment per completion.
2. Swap the serializer. Planck moved to `orjson` and tuned the `aiohttp` connector limit up from its default of 100; both helped marginally, and latency still rose with agent count ([Towards Data Science](https://towardsdatascience.com/why-adding-more-ai-agents-made-our-system-slower/)).
3. Offload the CPU segment with `run_in_executor()`. Pure-Python work stays behind the interpreter lock, so this rung pays only for C-accelerated or genuinely blocking calls.
4. Distribute the loop. Planck's fix was a router fanning requests across worker processes, each with its own event loop and connection pool, which stopped latency growing with agent count ([Towards Data Science](https://towardsdatascience.com/why-adding-more-ai-agents-made-our-system-slower/)). On free-threaded Python the same shape works with one loop per thread ([asyncio and free-threaded Python](https://docs.python.org/3/library/asyncio-threading.html)).

## When this backfires

Four conditions where chasing event-loop contention costs more than it returns:

1. Small payloads or modest fan-out. Per-completion CPU is negligible, so the instrumentation and a process router cost more than they recover. Bound the concurrency instead with [bounded batch dispatch](../patterns/multi-agent/bounded-batch-dispatch.md).
2. Throttling is the real constraint. Sharding across worker processes raises the burst rate the provider sees, so it deepens the throttling you were trying to escape ([Portkey](https://portkey.ai/blog/rate-limiting-for-llm-applications/)).
3. Single-core or memory-constrained hosts. Each worker process adds around 20 MB of resident memory, capping a 2 GB Raspberry Pi 4 at 4 to 8 workers, and single-core saturation persists under free-threaded Python 3.13t at 21.8% against 14.2% degradation — context-switch cost, not only the interpreter lock ([Mandal and Shende, arxiv 2601.10582](https://arxiv.org/abs/2601.10582)).
4. Runtimes without a global interpreter lock. The diagnostic transfers to any single-threaded loop, but the prescription does not: offloading to a thread there actually parallelizes, so step 3 resolves it.

The steelman: rate limits and retry storms are more common, cheaper to check, and produce the identical signature. Measure loop lag before you redesign.

## Example

Planck reproduced the failure with a local FastAPI server and simulated payloads rather than live provider calls ([Towards Data Science](https://towardsdatascience.com/why-adding-more-ai-agents-made-our-system-slower/)):

```python
NUM_AGENTS = 50
CALLS_PER_AGENT = 30
IO_RANGE = (0.45, 0.55)      # simulated LLM latency
CPU_RANGE = (0.001, 0.002)   # simulated (de)serialization
```

Response time rose in proportion to agent count despite a pure async implementation. The control run matters as much as the result: bare asyncio handled hundreds of thousands of coroutines efficiently, which ruled out scheduler overhead and left the 1 to 2 ms CPU segment per call as the cause. That segment is small enough to look free in a single-request trace and large enough to dominate at 1,500 concurrent calls.

## Key Takeaways

- Three causes share the "provider fast, wall-clock slow" signature: event-loop contention, provider throttling, and connection-pool exhaustion. Check throttling first, because it is the most common.
- Event-loop lag is the discriminator. In CPython, asyncio debug mode logs any callback exceeding `loop.slow_callback_duration`, default 100 ms ([Developing with asyncio](https://docs.python.org/3/library/asyncio-dev.html)).
- The mechanism is summation, not scheduling: per-completion CPU work runs between `await` points and adds up with concurrency, while the I/O overlaps ([Towards Data Science](https://towardsdatascience.com/why-adding-more-ai-agents-made-our-system-slower/)).
- Micro-optimization buys little. Planck's `orjson` and connector-limit changes helped marginally; distributing across worker processes, each with its own loop and pool, is what stopped the growth.
- The fix has conditions. It backfires under provider throttling, on memory-constrained hosts, and on runtimes with no global interpreter lock ([Mandal and Shende, arxiv 2601.10582](https://arxiv.org/abs/2601.10582)).

## Related

- [Async Non-Blocking Subagent Dispatch](../patterns/multi-agent/async-non-blocking-subagent-dispatch.md) — argues for async dispatch and backpressure; this page covers the starvation failure mode that pattern can hit at scale.
- [Bounded Batch Dispatch](../patterns/multi-agent/bounded-batch-dispatch.md) — capping in-flight work is the cheaper alternative when per-response CPU is small.
- [Staggered Agent Launch](../patterns/multi-agent/staggered-agent-launch.md) — the launch-side counterpart, addressing contention on a shared queue rather than on the runtime.
- [The Model Economics of Agent Swarms: Cost and Width](../patterns/multi-agent/model-economics-agent-swarms.md) — the other ceiling on fan-out width, set by cost rather than by runtime contention.
- [Failure-Aware Observability for Multi-Agent LLM Systems](failure-aware-observability-multi-agent.md) — the trace-signal taxonomy this diagnostic slots into as an infrastructure-layer signal.
