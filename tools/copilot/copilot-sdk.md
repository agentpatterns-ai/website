---
title: "GitHub Copilot SDK for AI Agent Development"
description: "A programmable layer that embeds Copilot agent capabilities — planning, tool invocation, file editing, and command execution — into any application."
tags:
  - agent-design
  - copilot
applies_to: "copilot@1.x"
last_reviewed: 2026-07-28
status: current
---

# GitHub Copilot SDK

> A programmable layer that embeds Copilot agent capabilities — planning, tool invocation, file editing, and command execution — into any application.

## What the SDK provides

The [Copilot SDK](https://github.blog/news-insights/company-news/build-an-agent-into-any-app-with-the-github-copilot-sdk/) gives you the same execution loop that runs GitHub Copilot CLI, packaged as a library you embed in your own applications. Instead of reaching Copilot through an IDE or web interface, you create agent sessions, send prompts, and handle streaming responses in code. GitHub announced the SDK as [generally available on 2026-06-02](https://github.blog/changelog/2026-06-02-copilot-sdk-is-now-generally-available), graduating it from public preview.

Core capabilities:

- Planning and execution: the agent plans multi-step tasks, invokes tools, edits files, and runs commands
- Multi-turn context: persistent memory across turns, with session compaction
- Model choice: support for several AI models, with user selection at different workflow steps
- Tool integration: custom tool definitions and MCP server support
- Real-time streaming: async task delegation with streaming responses

## Language support

The SDK provides bindings for [Node.js, Python, Go, .NET, and Java](https://github.blog/changelog/2026-04-02-copilot-sdk-in-public-preview/).

Bindings do not all sit at the same maturity. The Java artifact is still published as a preview version, `com.github:copilot-sdk-java:1.0.10-preview.0`, and its annotation-based tool API is gated behind a compiler opt-in ([java binding README](https://github.com/github/copilot-sdk/tree/main/java)). A binding also inherits its host language's concurrency contract: the Java client takes an `Executor`, which a Jakarta EE application must supply from the container so tool callbacks keep their transaction and injection context ([Using the GitHub Copilot SDK for Java](https://github.blog/engineering/using-the-github-copilot-sdk-for-java/)). See [Embedding the Copilot SDK in a Managed Java Runtime](copilot-sdk-managed-runtime.md) for what that integration costs.

## Architecture

The SDK abstracts the infrastructure that the Copilot CLI uses in production:

- Planner and tool orchestration
- Multi-model routing
- MCP server management
- GitHub authentication flows
- Chat session persistence

Applications built on the SDK inherit the same [production-tested execution loop](https://github.blog/news-insights/company-news/build-an-agent-into-any-app-with-the-github-copilot-sdk/) without reimplementing agent orchestration. Authentication runs through existing GitHub Copilot subscriptions or custom API keys (BYOK for enterprises).

## Why it works

Embedding a shared execution loop, rather than building agent orchestration from scratch, removes a class of maintenance work. Context compaction, tool invocation order, and model routing are problems every agent must solve. The SDK keeps those solutions in one place, so your application code handles only domain-specific logic. The same runtime also gets the fixes and model updates applied to Copilot CLI, with no changes needed in the embedding application.

## Agent-in-app pattern

The SDK supports an "agent-in-app" architecture, where you embed AI coding capabilities directly in domain-specific tools rather than reach them through general-purpose interfaces. [GitHub's announcement](https://github.blog/news-insights/company-news/build-an-agent-into-any-app-with-the-github-copilot-sdk/) lists use cases such as custom agent GUIs, speech-to-command workflows, content summarization tools, and purpose-built developer platforms.

This pattern lets you move agent capabilities from a fixed surface (IDE, CLI) to any application context where code generation, editing, or reasoning helps.

## When this backfires

Embedding the Copilot SDK ties your application to GitHub's subscription model, billing regime, and runtime decisions. Conditions where this is worse than the alternative:

- Subscription dependency: users need an active Copilot subscription, or you supply BYOK keys. Applications that must serve users without Copilot access cannot use the SDK as-is.
- Billing exposure: SDK sessions consume [GitHub AI credits](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) metered by the input, output, and cached tokens they burn, so high-volume workflows drain a plan's included allowance faster than interactive use does. On Business and Enterprise plans that allowance is a single pool shared across the billing entity, and it resets — without rollover — on the first of each month ([usage-based billing for organizations](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises)).
- Runtime lock-in: the execution loop, tool surface, and session management are GitHub's. If the runtime changes behavior (model swap, tool API change), embedding applications absorb the regression without direct control over the upgrade path.

The billing risk is not theoretical: in April 2026 GitHub [paused new Copilot sign-ups](https://thenewstack.io/github-copilot-signups-paused/) after agentic usage broke flat-rate economics, [fixed a token-counting bug](https://www.theregister.com/2026/04/15/github_copilot_rate_limiting_bug/) that had been under-counting newer models, and [announced a shift to token-based billing with tighter rate limits for individual plans](https://github.blog/changelog/2026-04-20-changes-to-github-copilot-plans-for-individuals/). That shift landed on 2026-06-01, when premium requests gave way to [usage-based AI credits](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/). Applications embedding the SDK inherit whatever credit allowance and budget policy GitHub sets for their users' plans — including whether an exhausted pool keeps billing at published rates or blocks until the next cycle.

Runtime lock-in is similarly concrete. In May 2026 a cross-binding bug ([github/copilot-sdk#251](https://github.com/github/copilot-sdk/issues/251)) stopped custom agents initialized through the SDK from reaching the assistant in either Node or .NET — a defect in the shared `copilot-agent-runtime` that no embedding application could patch. A practitioner ship report covering six SDK upgrades documents runtime changes breaking the embedding harness mid-iteration ([SDK upgrade-path regression](https://dev.to/moonrunnerkc/i-shipped-6-upgrades-to-my-copilot-cli-orchestrator-the-sdk-had-other-plans-2jpa)). The SDK gives you GitHub's execution loop — and GitHub's bugs.

## Example

The following Node.js snippet illustrates the agent-in-app pattern: starting the client, creating a session, subscribing to streaming events, and sending a task prompt ([nodejs README](https://github.com/github/copilot-sdk/tree/main/nodejs)).

```typescript
import { CopilotClient, approveAll } from "@github/copilot-sdk";

const client = new CopilotClient();
await client.start();

const session = await client.createSession({
  model: "gpt-5",
  streaming: true,
  onPermissionRequest: approveAll,
});

const done = new Promise<void>((resolve) => {
  session.on("assistant.message_delta", (event) => {
    process.stdout.write(event.data.deltaContent);
  });
  session.on("session.idle", () => resolve());
});

await session.send({
  prompt: "Refactor src/utils.ts to use async/await throughout",
});
await done;

await session.disconnect();
await client.stop();
```

Streaming is event-based rather than async-iterable: `assistant.message_delta` fires for each incremental chunk, and `session.idle` signals completion. `onPermissionRequest` controls how tool invocations are authorized; `approveAll` suits trusted environments only. Register more MCP servers through the client configuration to extend the agent with domain-specific tools.

## Key Takeaways

- The Copilot SDK exposes Copilot CLI's production execution loop as an embeddable library you can integrate into your own applications
- Supports Node.js, Python, Go, .NET, and Java, though maturity varies by binding — the Java artifact is still preview-versioned
- Enables the agent-in-app pattern: you embed planning, tool use, and file editing into custom applications
- MCP server support and custom tool definitions let you extend the agent's capabilities beyond built-in tools
- Generally available (GA as of 2026-06-02) with authentication through Copilot subscriptions or custom API keys; sessions consume token-metered AI credits from the plan's allowance

## Related

- [Embedding the Copilot SDK in a Managed Java Runtime](copilot-sdk-managed-runtime.md)
- [Agent Mode](agent-mode.md)
- [Coding Agent](coding-agent.md)
- [MCP Integration](mcp-integration.md)
- [Agent HQ (Multi-Agent Platform)](agent-hq.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
- [Cost-Aware Agent Design: Route by Complexity, Not Habit](../../token-engineering/cost-aware-agent-design.md)
