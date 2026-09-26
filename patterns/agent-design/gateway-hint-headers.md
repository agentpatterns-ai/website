---
title: "Gateway Hint Headers for Routing and Budgeting Agent Calls"
term: "Gateway Hint Headers"
description: "Have the agent client declare request class, subagent type, tool durations, and compaction state in request headers, so a gateway can route, attribute, and budget without parsing the prompt."
tags:
  - agent-design
  - cost-performance
  - claude
aliases:
  - client-declared routing metadata
  - request-class header
  - x-claude-code hint headers
last_reviewed: 2026-09-24
maturity: emerging
---

# Gateway Hint Headers for Routing and Budgeting Agent Calls

> Let the client declare per-request facts in headers so the gateway routes and attributes without reading the prompt.

A gateway hint header is a request header the agent client sets to describe the call it is making: what class of request this is, which subagent issued it, how long the previous tools ran, whether a compaction just happened. The gateway reads those values and decides where to send the request and whose budget to charge, with no prompt content in scope. Two conditions bound it. The values are client-asserted, so they are a routing and accounting input and never an authorization input. And on the connection a gateway uses, they are off until someone turns them on.

## What the headers carry

Claude Code 2.1.273 (September 15, 2026) added five, off by default on a custom base URL and turned on with `CLAUDE_CODE_GATEWAY_HINT_HEADERS=1` ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). Each value comes from a closed vocabulary ([gateway compatibility guide](https://code.claude.com/docs/en/llm-gateway-protocol)):

| Header | Values | What a gateway does with it |
|---|---|---|
| `x-claude-code-request-class` | `main`, `subagent`, `workflow`, `compaction`, `auxiliary`. Sent on every request | Send a summarization call to a cheap model and a main turn to the expensive one |
| `x-claude-code-agent-type` | A built-in agent name such as `Explore` or `Plan`, or `custom`, `teammate`, `fork` | Attribute spend to the kind of subagent that generated it |
| `x-claude-code-prev-tool-durations` | `Bash=742;Read=9`, capped at 32 entries and 4 KB | Feed a latency-aware routing decision with what the last turn cost in wall time |
| `x-claude-code-compaction` | `auto`, `manual`, `reactive` | Tell a deliberate context reset from a conversation that outgrew its window |
| `x-claude-code-context-compacted` | Same values, present once on the first main-conversation request after a compaction | Drop a prompt cache entry keyed on a prefix that is now dead |

The set carries "only … fixed vocabularies, tool names, and durations, never prompt text or file contents", and a gateway "may consume [them] for routing, attribution, and tracing, and need not forward" them upstream ([gateway compatibility guide](https://code.claude.com/docs/en/llm-gateway-protocol)).

The mechanism is not vendor-specific. LiteLLM routes on an `x-litellm-tags` header carrying a tag list, with negation (`!provider:anthropic`) and required-AND (`&reasoning_type:high`) forms ([LiteLLM tag based routing](https://docs.litellm.ai/docs/proxy/tag_routing)).

## Check the default before you write the policy

The default is per-connection, and the gateway case is the one where the headers are off. A direct connection to the Anthropic API sends them by default. "Custom base URL: off by default, because a proxy that rejects unknown headers would fail the request", and any other backend sends them "only when `CLAUDE_CODE_GATEWAY_HINT_HEADERS=1` is set" ([gateway compatibility guide](https://code.claude.com/docs/en/llm-gateway-protocol)). Pointing Claude Code at a gateway is the configuration that suppresses them. The variable has to reach every machine, normally through managed settings, and until it does the policy is inert with no error to notice.

## Why it works

An HTTP intermediary sees headers before it sees the body, and these values come from a fixed vocabulary rather than free text, so the routing decision is a lookup instead of a classification. Anthropic states the consequence for `x-claude-code-session-id`, an identity header that predates these five: use it "to aggregate all requests from one session without parsing request bodies" ([gateway compatibility guide](https://code.claude.com/docs/en/llm-gateway-protocol)). Prompt content never enters the routing path, which narrows what an audit of the gateway has to cover, and the decision is cheap. The body-inspecting alternative is not. Before its authors optimized it, the vLLM Semantic Router's end-to-end latency was 4,918 ms, and "at 8K tokens, three concurrent classifiers need ~4.5 GB for attention masks alone" ([Liu et al., 2026](https://arxiv.org/abs/2603.12646v1)).

Cheapness is the weaker half. The client knows things the body does not encode. Which subagent in a fan-out issued a call, and how long the last Bash invocation took, are facts no classifier recovers from the prompt. That is the trade: fidelity on facts of origin, for values the gateway cannot verify.

## When this backfires

Treating a hint as an entitlement is the failure that costs money. LiteLLM says so for its own header routing: "Header-based routing is not a security boundary on its own … any client can spoof the User-Agent and be routed to a deployment it should not reach" ([LiteLLM tag based routing](https://docs.litellm.ai/docs/proxy/tag_routing)). Claude Code's docs supply the vector on the page that documents the hint headers: "If your developers set `ANTHROPIC_CUSTOM_HEADERS`, those headers appear on requests as well" ([gateway compatibility guide](https://code.claude.com/docs/en/llm-gateway-protocol)). An open security issue on the vLLM Semantic Router covers the same shape: the router "can consume configured identity headers such as `x-authz-user-id` and `x-authz-user-groups` from the request context", and the expected behavior is to "strip, ignore, or fail closed" unless the deployment "explicitly declares a verified external authorization/header-injection boundary" ([vllm-project/semantic-router #1445](https://github.com/vllm-project/semantic-router/issues/1445)).

The quieter failures come from reading too much into the data.

- Absence is not information. The duration header is missing on compaction calls, side requests, and the first request of a new prompt, and the docs warn against the obvious inference: "Don't read a missing header as a turn that ran no tools" ([gateway compatibility guide](https://code.claude.com/docs/en/llm-gateway-protocol)).
- Truncation biases the average. Durations stop "at most 32 entries and 4 KB, keeping the first entries" ([gateway compatibility guide](https://code.claude.com/docs/en/llm-gateway-protocol)), so a wide fan-out reports its opening tool calls and drops the rest. A latency-aware router then underestimates the turns that ran longest.
- Agent type is coarse. "A user-chosen agent name is never sent" ([gateway compatibility guide](https://code.claude.com/docs/en/llm-gateway-protocol)), so every user-defined agent collapses into `custom`. The separate `x-claude-code-agent-id` header, also outside the hint set, is "generated fresh each time Claude Code spawns a subagent", which attributes one run and cannot carry a standing budget.
- Version skew reads as a workload change. The headers require Claude Code v2.1.273 or later ([gateway compatibility guide](https://code.claude.com/docs/en/llm-gateway-protocol)), so a dashboard keyed on request class shows a distribution of client versions first.

One case argues for the opposite design. Where routing fidelity matters more than routing cost, a classifier over the prompt beats a self-declared class. A semantic router that encodes the prompt and classifies its reasoning need "achieves a 10.2 percentage point improvement in accuracy on the MMLU-Pro benchmark while reducing response latency by 47.1% and token consumption by 48.5% compared to direct inference with vLLM" ([Wang et al., 2025](https://arxiv.org/abs/2510.08731v1)). If the question is whether this prompt needs reasoning, read the prompt.

## Key Takeaways

- Client-declared headers turn per-dimension budgeting into a lookup and keep prompt content out of the gateway's routing path.
- Claude Code ships five of them from 2.1.273, off by default on the connection a gateway uses, so the managed-settings rollout is the real work.
- Route, attribute, and account on them. Enforce entitlements somewhere the client does not control.
- Absence and truncation are the two quiet failures: a missing duration header is not a toolless turn, and 32 entries is not the whole turn.

## Related

- [Centralized LLM Gateway for Per-Dimension Agent Budgets](../../observability/llm-gateway-per-dimension-budgets.md) — the budget dimensions these headers populate, and the chokepoint that enforces them
- [Gateway Model Routing](gateway-model-routing.md) — the same gateway as a model catalog, and the other headers Claude Code sends it
- [Per-Call Budget Hints on Tool Invocations](per-call-budget-hints-tool-calls.md) — the in-body sibling, where the hint goes to the model rather than to an intermediary
- [Cost Routing Without Quality Monitoring](../anti-patterns/cost-routing-without-quality-monitoring.md) — what happens when a cheap routing signal drives model choice with nothing watching the output
