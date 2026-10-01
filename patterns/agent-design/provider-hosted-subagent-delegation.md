---
title: "Provider-Hosted Subagent Delegation: One Model Price for the Whole Tree"
term: "Provider-Hosted Subagent Delegation"
description: "Hosted delegation lets the model spawn subagents inside one API request, but every agent inherits the request's model and price, so size that model to the hardest subtask in the tree."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - hosted multi-agent
  - API-side subagent orchestration
last_reviewed: 2026-09-30
maturity: emerging
---

# Provider-Hosted Subagent Delegation: One Model Price for the Whole Tree

> Hosted delegation moves subagent orchestration into one API request and gives the tree a single model, so that model must fit the hardest subtask.

Provider-hosted subagent delegation lets the model spawn and coordinate subagents without your application implementing orchestration. OpenAI shipped it in beta alongside GPT-6.1 Sol on 2026-09-29: "Let the model delegate work to subagents in a Responses API request" ([OpenAI API changelog](https://developers.openai.com/api/docs/changelog)). Every agent in the tree inherits one model. "The subagents share the request's model and available tools, while agents coordinate through collaboration primitives such as spawning, messaging, and waiting" ([OpenAI: Multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent)). This page covers OpenAI's design only, so treat it as one vendor's shape rather than a settled one.

## Conditions that have to hold

- The work splits into bounded, independent subtasks. OpenAI names the shapes that do not: tasks that "depend on a single ordered chain of reasoning, require frequent writes to shared mutable state, or are already dominated by one slow external operation" ([OpenAI](https://developers.openai.com/api/docs/guides/responses-multi-agent)).
- Those subtasks sit close together in difficulty. One rate covers the tree, so a mix of trivial and hard work pays the hard rate throughout.
- You do not need the three controls hosted mode withdraws. `/responses/compact`, `reasoning.summary` and `max_tool_calls` are all unsupported once `multi_agent.enabled` is true, and server-side compaction switches on "even if the request does not configure `context_management`" ([OpenAI](https://developers.openai.com/api/docs/guides/responses-multi-agent)).

## How the tree works

The root agent is `/root`, and children take paths like `/root/reviewer/tester`. Six hosted actions drive coordination: `spawn_agent`, `send_message`, `followup_task`, `wait_agent`, `interrupt_agent` and `list_agents`. `max_concurrent_subagents` defaults to 3, capping active subagent turns tree-wide, and OpenAI "imposes no fixed limit on the total number of subagents or tree depth" ([OpenAI](https://developers.openai.com/api/docs/guides/responses-multi-agent)).

Uniformity is not an accident of the beta. OpenAI states it to the model, in instructions the caller cannot edit: "All agents in the team, including the agents that you can assign tasks to, are equally intelligent and capable, and have access to the same set of tools" ([OpenAI](https://developers.openai.com/api/docs/guides/responses-multi-agent)). A lead that picks a cheaper tier per dispatch, as in [model-directed subagent tiering](model-directed-subagent-tiering.md), has no equivalent here.

## Why it works

Delegation buys two separable things, and the hosted form buys one. The first is context isolation: "Each subagent receives a bounded task and maintains its own context, which reduces interference in context between unrelated lines of work and improves performance" ([OpenAI](https://developers.openai.com/api/docs/guides/responses-multi-agent)). A study outside the vendor states the same condition: multi-agent systems can be advantageous "when a single agent's effective context utilization is degraded (e.g., due to long or noisy contexts)" ([Tran and Kiela](https://arxiv.org/abs/2604.02460v2)).

The second is price arbitrage. Cost is rate times tokens, so moving routine tokens onto a cheaper model lowers the bill, which is what a tiering harness does at each dispatch. A tree that shares one model cannot express that, because one rate covers every agent. The rule follows from the price tables, not from any vendor claim. Pick the request's model for the hardest subtask, and pay that rate for the easy ones.

## When this backfires

- Subtask difficulty varies widely. GPT-6.1 Sol and GPT-6 Astra share a 1,050,000 context window and an Apr 30, 2026 knowledge cutoff. Astra costs $10.00 per million input tokens and $50.00 output. Sol costs $2.00 and $10.00 ([GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol); [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)). A tree pinned to Astra for one hard subagent pays five times over for the rest.
- Token growth outruns the parallel gain. OpenAI warns that "adding subagents can increase token usage" ([OpenAI](https://developers.openai.com/api/docs/guides/responses-multi-agent)), and the launch material puts no number on the gain.
- The prompt crosses 272K input tokens, at which point "2x input and cache rates and 1.5x output for the full request" apply ([GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)).
- Agents contend rather than cooperate. Cognition argues that "Actions carry implicit decisions, and conflicting decisions carry bad results", and that running agents in collaboration "only results in fragile systems" because "decision-making ends up being too dispersed" ([Cognition](https://cognition.com/blog/dont-build-multi-agents)). The post is dated June 12, 2025, before hosted coordination actions existed.
- The gain may be compute, not architecture. Tran and Kiela conclude that "for multi-hop reasoning tasks, many reported advantages of multi-agent systems are better explained by unaccounted computation and context effects rather than inherent architectural benefits" ([arXiv:2604.02460v2](https://arxiv.org/abs/2604.02460v2)). Their scope is multi-hop reasoning, not coding agents.

## Example

The same five-agent job, priced two ways, at OpenAI's published rates for one hard subtask and three mechanical ones:

```text
Harness-built tiering            Hosted tree
  lead      -> Astra  $10/$50     /root           -> Sol  $2/$10
  hard      -> Astra  $10/$50     /root/hard      -> Sol  $2/$10
  rename x3 -> Sol    $2/$10      /root/rename x3 -> Sol  $2/$10

Tiering sets the rate per dispatch.
Hosting sets it once, in the request.
```

Pinning the hosted request to Astra to serve the one hard subagent reprices all five agents at $10/$50. The cheaper reading is to run the tree on Sol and keep the hard subtask out of it.

## Key Takeaways

- Hosted delegation ships the orchestration and withholds the tier: subagents share the request's model and tools.
- Size the request's model to the hardest subtask in the tree, and count every easy subagent as billed at that rate.
- The mechanism on offer is context isolation and parallelism. Price arbitrage is not available, and OpenAI warns that adding subagents can increase token usage.
- Enabling it costs `/responses/compact`, `reasoning.summary` and `max_tool_calls`, and forces server-side compaction on.
- The feature is beta, from one vendor, and the vendor publishes no number for the gain.

## Related

- [Model-Directed Subagent Tiering](model-directed-subagent-tiering.md) covers the lead model choosing a tier and effort per dispatch, which the hosted form removes.
- [Auto Model Selection](auto-model-selection.md) covers the harness picking the model per request from a vendor-managed pool.
- [Recursive Sub-Agent Delegation](../multi-agent/recursive-sub-agent-delegation-depth.md) covers depth as a design lever in nested hierarchies.
- [Static Roster vs Runtime Subagent Definition](../multi-agent/static-roster-vs-runtime-subagent-definition.md) covers who defines a subagent's prompt and tool allowlist, and when.
- [Sub-Agents for Fan-Out](../multi-agent/sub-agents-fan-out.md) covers single-level dispatch, which this tree extends with nesting.
