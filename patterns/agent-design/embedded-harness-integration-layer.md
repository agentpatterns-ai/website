---
title: "Choosing an Integration Layer for an Embedded Agent Harness"
term: "Embedded Harness Integration Layer"
description: "Adopting an open agent harness means picking one of three integration layers (one-shot process, SDK, or app-server protocol), and that choice fixes what the host application owns."
tags:
  - agent-design
  - tool-agnostic
  - harness-engineering
aliases:
  - embedding an agent harness
  - agent harness integration layer
  - host application harness ownership split
last_reviewed: 2026-08-20
maturity: adopted
---

# Choosing an Integration Layer for an Embedded Agent Harness

> Adopting an agent harness fixes an integration layer (one-shot, SDK, or app server), and that choice decides what the host application still builds.

A harness is the execution system wrapped around the model call. It maintains context over time, calls tools, exposes progress, handles failures, and requests human approval. OpenAI's name for it is direct: "That surrounding execution system is the harness" ([OpenAI](https://developers.openai.com/blog/codex-as-a-platform)). Adopting an open one is a layer decision, and the layer you pick sets what your application still has to build.

## When to adopt at all

Two conditions make an adopted harness worth its cost. The work runs over many turns and needs context carried across them, and someone other than the author operates it, so approval prompts and progress reporting are product surfaces rather than debug output. Below both conditions, a direct API call and your own loop is the cheaper answer.

Anthropic ships a harness of its own and still tells developers to "start by using LLM APIs directly: many patterns can be implemented in a few lines of code". The stated reason is debuggability: frameworks "often create extra layers of abstraction that can obscure the underlying prompts and responses, making them harder to debug" ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)). The ladder below is the decision you make after clearing that bar.

## The three integration layers

| Layer | Fits | The harness holds | The application rebuilds |
|-------|------|-------------------|--------------------------|
| One-shot process | "a script, CI job, or one-off background task" ([OpenAI](https://developers.openai.com/blog/codex-as-a-platform)) | One bounded run, returning "structured output" | Everything between runs: state, resumption, progress |
| SDK | "application code that needs to start, resume, or stream" tasks ([OpenAI](https://developers.openai.com/blog/codex-as-a-platform)) | The agent loop, behind session handles your code drives | The user-facing conversation and its lifecycle |
| App-server protocol | "when the agent is part of the product itself" ([OpenAI](https://developers.openai.com/blog/codex-as-a-platform)) | Open conversations, streamed events, interruption, approval round-trips | No part of the loop; interface and domain logic only |

The same ladder appears in a second vendor's stack, which suggests it tracks the problem rather than one product's packaging. Anthropic's Agent SDK is "available as a CLI for scripts and CI/CD, or as Python and TypeScript packages for full programmatic control" ([Anthropic](https://code.claude.com/docs/en/headless)), and its persistent rung is the recommended one: streaming input "allows the agent to operate as a long lived process that takes in user input, handles interruptions, surfaces permission requests, and handles session management" ([Anthropic](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)). Single-message input offers no queueing, no real-time interruption, and no multi-turn conversation (same source).

## What the application owns

The split is one sentence: "Your application owns product context, business rules, and tools; Codex app-server provides the agent loop and sandboxed execution" ([OpenAI](https://developers.openai.com/blog/codex-as-a-platform)). Interface stays on the application side too, which is the point of embedding instead of adopting an assistant. OpenAI names the anti-goal directly: "Instead of asking every team to move its work into a general-purpose coding assistant, you can bring the agent into software designed around the actual job."

A vendor-neutral protocol draws the same line. The Agent Client Protocol "standardizes communication between code editors ... and coding agents" ([Agent Client Protocol](https://github.com/agentclientprotocol/agent-client-protocol)). Its specification puts the split in the same place: clients "provide the interface between users and agents" and "manage the environment, handle user interactions, and control access to resources", with `session/request_permission` reserved for requesting "user authorization for tool calls", while agents are the programs that "autonomously modify code" ([ACP, Architecture](https://agentclientprotocol.com/protocol/overview)). Transport follows deployment rather than being fixed: "local agents run as sub-processes of the code editor, communicating via JSON-RPC over stdio", while remote agents communicate "over HTTP or WebSocket" — for which the protocol notes "full support for remote agents is a work in progress" ([ACP, Overview](https://agentclientprotocol.com/)).

## Why it works

Harness behavior can move a score further than a model change does, which is what makes the layer worth adopting rather than approximating. On ARC-AGI-3, "retained reasoning and context compaction raised GPT-5.6 Sol's score from 13.3% to 38.3% while reducing output tokens sixfold" ([OpenAI](https://developers.openai.com/blog/codex-as-a-platform)). Same model, different harness behavior, near-triple the score at a sixth of the output.

The layer choice then works because each rung fixes where conversation state lives. A one-shot run returns structured output and exits, so the caller holds nothing between invocations. An app server keeps conversations open and lets the application "stream events, interrupt work, expose tools, and respond to approval requests" ([OpenAI](https://developers.openai.com/blog/codex-as-a-platform)). Whatever a rung does not hold, the application writes itself.

## When this backfires

- The job is one bounded call. A single extract-and-return task needs no conversation state, no interruption, and no approval channel. A harness there buys abstraction over the prompts you have to debug ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)).
- The rung sits above the need. An app-server integration for a nightly CI job leaves you operating a long-lived process and an event stream for a run nobody watches.
- The rung sits below the need. An in-product agent on the one-shot rung forces the application to rebuild session and turn management, because that mode carries no queueing, no interruption, and no multi-turn conversation ([Anthropic](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)).
- The split gets read as a security boundary. Sandbox and approval enforcement sitting with the harness does not make your tools safe: "The tools you expose define your attacker's affected scope. Any tool parameter the model can influence must be treated as attacker-controlled input" ([Microsoft Security](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/)). You also inherit the harness's own defects: Microsoft disclosed CVE-2026-26030 and CVE-2026-25592 in Semantic Kernel, where unsafe string interpolation reached `eval()` and an exposed file-write allowed a sandbox escape.
- Open source gets read as a free agent. "The open-source layer is the harness and integration surface; model access and managed services remain separate" ([OpenAI](https://developers.openai.com/blog/codex-as-a-platform)). Inference is still billed, so an adoption justified on cost alone fails.

## Example

OpenAI's sample application, Relay, shows the split at the app-server rung. Its logistics dashboard is a fictional sample rather than a deployed customer system. A user selects a shipment and clicks a domain action such as Compare recovery. The application supplies the relevant context and its own tools, the agent explains the available options, "and any consequential write requires approval" ([OpenAI](https://developers.openai.com/blog/codex-as-a-platform)) before the business view refreshes.

The record, the action, the tools, and the refreshed view stay in the application. The harness contributes only the loop between click and proposal.

## Key Takeaways

- Pick the integration layer from how long the agent's work stays open, not from how capable the harness is.
- Before choosing a rung, list what it does not hold — session lifetime, streaming, interruption, approval routing — and cost that list as build work, because it is.
- The ownership split assigns tools to the application, which makes tool surface your security problem whatever the harness sandboxes.
- Re-check the rung when the product's usage shifts. A workflow that grows from batch runs to an operated conversation has outgrown its integration layer, and no amount of prompt work substitutes for moving up.

## Related

- [Managed vs Self-Hosted Agent Harness](managed-vs-self-hosted-harness.md) — the deployment axis of the same adoption decision.
- [Production Hosting Topology for Self-Hosted Agent SDK Runtimes](agent-sdk-hosting-topology.md) — what running the adopted harness costs operationally.
- [The Harness as Product: What Listed-Rate Pricing Buys](harness-as-product.md) — what a paid harness layer includes when you do not self-host.
- [Agent Event Streaming: Consumer Contract Above the Tokens](agent-event-streaming-model.md) — designing the event contract the app-server rung hands you.
- [Six-Shape Approval Response Taxonomy](approval-response-taxonomy.md) — the approval round-trip the top rung exposes.
