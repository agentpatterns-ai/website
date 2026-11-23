---
title: "The Chaos Loop: Hardening a Launch With Injected Faults"
term: "Agent Chaos Loop"
description: "One Claude Code session broke a staging service on purpose for two weeks and shipped fixes from telemetry. The account comes from one team's launch."
tags:
  - testing-verification
  - workflows
  - claude
aliases:
  - chaos loop
  - agent-driven chaos engineering
  - launch hardening loop
last_reviewed: 2026-11-23
maturity: emerging
---

# The Chaos Loop: Hardening a Launch With Injected Faults

> An agent breaks a staging service on purpose, reads the telemetry, and ships fixes; one launch reported 60 server errors in 2 billion requests.

A chaos loop is a long-running agent session that repeats one cycle against a staging copy of a service: pick a failure scenario, run a load harness that causes it, read the telemetry, and ship a fix. This page draws on one product's launch, written up by the engineer who ran the loop ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)). Every figure below comes from that post unless marked as my own reading.

## What the Claude Docs run did

About two weeks before launch, the author had Claude drive a staging cluster that mirrored production at over a million synthetic docs a day, and break core components on purpose. The loop was a Claude Code session that acted as coordinator and handed most work to sub-agents: usually about 11 at a time in the busiest week, and 30 at the peak ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)).

The author picked scenarios they thought were paranoid:

- 10 million new docs created in a single day
- 22,000 live connections reconnecting at once
- One hot doc with hundreds of viewers, a server killed while loading a doc, and a stalled database

## One iteration

The harness picked a feature, such as document creation, and pushed it to saturation. Claude read telemetry through the Datadog MCP server, then returned a short menu of options with a recommendation ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)).

What happened next depended on whether the fix could be undone:

- For an easy-to-undo change, Claude wrote it, deployed it to staging, and reran the test.
- For a hard-to-undo change, such as a database schema, a key layout, or how a doc is stored, Claude stopped and asked. The author named these categories before the loop started.

The author also gave Claude two invariants to hold: docs open almost instantly, even with a long history, and once the server acknowledges an edit, tests must show the edit is still there ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)).

## Telemetry decides what the loop can fix

The service reported on every operation. Each database query carried its name and the rows it scanned against the rows it returned, so Claude could spot a bad query and rewrite it. Claude also added telemetry it found missing ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)).

The memory case shows the cycle. One large doc used about 3 GB on its pod. Claude first shrank a server cache, then dropped that change when the next run showed the memory sat in a cache inside a dependency. Finer profiling found that each keystroke copied the doc into several data structures, and Claude made them copy-on-write. After about three days the doc topped out near 180 MB, and the launch estimate fell from over 500 memory-optimized pods to about 50 ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)).

The team also chose Rust and few dependencies, and vendored the few it kept. The author expected a garbage collector to add noise, because memory and latency shift on its schedule. The team did not benchmark Rust against Go, so this is one team's experience rather than a measured comparison ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)).

## What the 60 errors show

Claude Docs launched on September 16, 2026. By September 22 people had created over 4.6 million docs. Across 2 billion requests the team saw 60 server errors and never rolled back. About 50 memory-optimized pods ran the service, and the team rolled production 629 times in September. Seven of the ten scenarios rehearsed on staging happened in production. Claude had shipped fixes behind runtime flags, so the team usually flipped a flag ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)).

By division (my arithmetic), 60 errors in 2 billion requests is 3 in 100 million. Read it as a launch outcome, not a measurement of the loop. The author credits two decisions, the loop and a legible stack, and the post reports no comparison launch without them. It does not say how it defines a server error.

## Trying it at smaller scale

The author's steps assume one engineer with Claude Code, a staging environment, and an observability provider ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)):

1. Give Claude your telemetry, using your provider's MCP server.
2. Have Claude write a load script that sends ten times your real traffic to staging and breaks things on purpose: kill an instance, stall the database, deploy in the middle of a spike.
3. Write down your most important technical invariants and give them to Claude.
4. For anything hard to undo, have Claude stop and give you a few options with a recommendation.

The author spent roughly $125,000 of inference at Claude Fable 5.2 list price from the end of August to launch day. They put a two-week push on a small stack at $3,000 to $10,000 and say they have not run it. If sub-agents burn too many tokens per hour, they say a single agent should also work well ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)).

## When this backfires

- Model dependence. The author used an internal research model roughly comparable to Claude Fable 5.2. They say older models forgot the goal ten or twenty iterations in, and that the newer one held their invariants across many compactions ([Nair, 2026](https://claude.dev/blog/chaos-loop-claude-docs-launch/)).
- No staging copy. The author's steps assume one. Without a production-like environment that tolerates destructive tests, there is nothing to run the loop against (my inference).
- Unwritten invariants. The loop checked the two properties the author wrote down. A property nobody stated is not checked (my inference).
- Cost. The $125,000 figure includes tokens spent while the author worked out the process, and they say they could have spent about half as much.

## Key Takeaways

- A chaos loop is one agent session cycling scenario, harness, telemetry, and fix against a staging copy.
- The Claude Docs report is 60 server errors in 2 billion requests with no rollback, from one team and one product.
- The post gives no launch without the loop for comparison, so the loop's share of the result is unmeasured.
- The author named the hard-to-undo change categories before the loop started, and Claude stopped and asked on those.
- The author gave Claude two invariants: fast doc opens, and an acknowledged edit stays.
- Per-query telemetry (name, rows scanned, rows returned) let Claude find and rewrite bad queries.

## Related

- [LLM API Fault Injection at the HTTP Layer (AgentChaos)](llm-api-fault-injection-http-layer.md) — injects faults into an agent's model calls to score the agent, where the chaos loop uses an agent to fault a conventional service
- [Handoff-Boundary Fault Injection (llmmas-otel)](handoff-boundary-fault-injection.md) — delays a message between agents and diffs the faulted trace against a baseline
- [Recovery as a Separate Eval Axis (UndoBench)](recovery-as-separate-eval-axis.md) — scores recovery from a fault against an identical-seed control
- [Planted-Bug Methodology: Deliberate Bugs as Observability Calibration](planted-bug-observability-calibration.md) — checks that captured signals lead an agent to the right layer
- [Instrument First, Then Let the Agent Hill-Climb](../workflows/instrument-first-agent-performance-sprint.md) — a second Anthropic account of an agent loop that depends on trusted measurements
