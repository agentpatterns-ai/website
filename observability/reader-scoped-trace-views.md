---
title: "Reader-Scoped Trace Views: When to Build Your Own UI"
term: "Reader-Scoped Trace View"
description: "Build a second interface over agent trace data when the read repeats and the backend's own customization cannot express it — and expect to own it."
tags:
  - observability
  - agent-design
  - tool-agnostic
aliases:
  - custom trace interface
  - purpose-built trace view
  - custom app over trace data
last_reviewed: 2026-09-29
maturity: emerging
---

# Reader-Scoped Trace Views: When to Build Your Own UI

> Build a second interface over trace data when one reader's question repeats and the backend's own customization cannot express it. You then own it.

A reader-scoped trace view is an interface you build over a tracing backend's API, shaped for one reader and one recurring question. It runs beside the dashboard the vendor ships. One trace answers different questions for different people. LangSmith states the split directly: "An engineer may need the full trace, including tool calls, metadata, and intermediate steps. A subject matter expert (SME) may only need the user request, the model response, relevant context, and a clear rubric" ([LangChain, September 24 2026](https://www.langchain.com/blog/langsmith-custom-apps)).

## Three rungs over the same data

| Rung | What it gives you | What you own |
|---|---|---|
| The shipped view | LangSmith's defaults follow "the most common user requirements we've seen", including "prebuilt dashboards for latency, cost, and error rates, and a comparison view that highlights regressions across experiments" ([LangChain](https://www.langchain.com/blog/langsmith-custom-apps)) | Nothing |
| The configurable view | Langfuse widgets read traces, observations, or scores, group by user, model, time or trace name, and export as a "versioned JSON format" ([Langfuse](https://langfuse.com/docs/metrics/features/custom-dashboards)) | A definition file |
| The view you build | A UI calling the trace API. LangSmith Custom Apps hosts one inside the workspace so you "skip the hosting, auth, and permissions work" ([LangChain](https://www.langchain.com/blog/langsmith-custom-apps)) | An application |

Check the configurable rung before writing code. It covers any question that is a metric grouped by a dimension.

## Climb to the third rung when three things hold

The read repeats. LangSmith ties the pattern to repetition rather than dissatisfaction: "Custom Apps are especially useful when you need to repeat the same review process" ([LangChain](https://www.langchain.com/blog/langsmith-custom-apps)). A question asked once is answered by a filter, or by the CSV export on a Langfuse dashboard tile ([Langfuse](https://langfuse.com/docs/metrics/features/custom-dashboards)).

The question is not a grouped metric. Widget builders emit charts. A queue that paginates runs with a rubric beside them, or a diff of two trajectories at their decision points, is application logic. LangSmith draws the boundary the same way: use a custom app "for a workflow the built-in UI does not cover" ([LangSmith docs](https://docs.langchain.com/langsmith/custom-apps)).

Someone owns it by name. The view outlives the person who asked for it, and meets a data-model change without them.

## Why it works

A shipped dashboard fixes the projection at design time, for the modal reader. Everyone else still needs the answer, so they pay for the mismatch outside the tool, in export-and-reformat work that repeats every review cycle. Chime describes that before-state: "Our human-in-the-loop reviews used to live across spreadsheets and other separate tools. Reviewers switched between platforms, and our team spent manual effort prepping files and standardizing formats" ([LangChain, quoting Roxanne Wang of Chime](https://www.langchain.com/blog/langsmith-custom-apps)). That is one customer's account of its own workflow, not a measured result. Building a view converts a recurring per-read cost into a one-off build plus a standing maintenance cost. The trade turns on how often the read happens.

## When this backfires

A data-model change moves your numbers without breaking your view. Langfuse v4 adopted an OpenTelemetry-native data model with no separate trace object, where "A trace is the set of observations that share a `trace_id`". Trace counts moved from `SELECT count(*) FROM traces` to `uniq(trace_id)` over a wide observations table ([Langfuse v4 dashboard changes](https://langfuse.com/faq/all/dashboard-changes-in-v4)). Langfuse says the trace-count difference is "negligible for practical purposes", so this example is mild. The general risk holds: a view that keeps rendering a shifted number gives its reader no alert.

You built on endpoints the policy does not cover. LangSmith's policy covers documented public endpoints, with a minimum support window of "6 months from announcement to removal" for Cloud and "At least one major release" for self-hosted, where major releases ship on a roughly six-week cadence. Everything else "can change, including with breaking changes, at any time" ([LangSmith deprecation policy](https://docs.langchain.com/langsmith/endpoint-deprecation)).

The plan will not carry a view per reader. "Plus plans include one Custom App per organization" ([LangChain](https://www.langchain.com/blog/langsmith-custom-apps)), so the second reader who needs one does not get one.

The view needs data the host will not fetch. A LangSmith Custom App "runs in a sandbox with no network access of its own" ([LangSmith docs](https://docs.langchain.com/langsmith/custom-apps)), so joining traces to your ticket system means hosting the app yourself again.

A view per reader is also how tool sprawl starts. Google's Technical Infrastructure UX team surveyed 10,000 Google developers in 2021 and "uncovered that Google's internal infrastructure tools were fragmented and inefficient, hindering developers' productivity" ([arxiv 2506.16107v1](https://arxiv.org/abs/2506.16107v1)). The team then set out to consolidate 600 tools into one console. Retire a view when its reader stops reading it.

## Example

The LangSmith CLI scaffolds four starters: `annotation-queue`, `annotation-queue-grid`, `experiment-comparison`, and `coding-agent-dashboard`. The scaffold also writes an `AGENTS.md` that "gives a coding agent the conventions and API surface it needs to produce a working app on the first pass" ([LangSmith docs](https://docs.langchain.com/langsmith/custom-apps)):

```bash
langsmith apps init --name sme-review --template annotation-queue
cd sme-review && langsmith apps dev
langsmith apps push
```

Scaffolding is the cheap half; the standing cost is ownership. The first `langsmith apps push` records the app ID in `.langsmith/app.json`, which teammates commit so later pushes update the same app.

## Key Takeaways

- Treat the choice as three rungs, not build-or-buy: what ships, what the backend lets you configure, and what you write.
- Repetition is the trigger. A one-off question does not justify an application.
- The configurable rung answers metrics grouped by a dimension; go past it for review queues, trajectory diffs, and anything with workflow state.
- A hosted custom app removes hosting, auth and permissions, and leaves you the query code and the migrations.
- Ask what breaks at the next major version before you build, then name who fixes it.

## Related

- [Agent-Trace Data Layer: Storage for Hours-Long Traces](agent-trace-data-layer.md) — where the trace data this view reads is stored, and when a general backend stops holding it
- [Trajectory Projection: A Flattened View of Agent Traces](trajectory-projection.md) — the vendor-side projection a reader-scoped view often starts from
- [Prebuilt Agent Monitoring Dashboard](prebuilt-agent-monitoring-dashboard.md) — the first rung, shipped with the harness instead of built per reader
- [Traces Need Feedback to Power Learning](traces-need-feedback-to-power-learning.md) — what a review interface collects, and why the verdict has to land back on the trace
