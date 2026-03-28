---
title: "GitHub Copilot SDK for AI Agent Development"
description: "A programmable layer that embeds Copilot agent capabilities — planning, tool invocation, file editing, and command execution — into any application."
tags:
  - agent-design
  - copilot
---

# GitHub Copilot SDK

> A programmable layer that embeds Copilot agent capabilities — planning, tool invocation, file editing, and command execution — into any application.

## What the SDK Provides

The [Copilot SDK](https://github.blog/news-insights/company-news/build-an-agent-into-any-app-with-the-github-copilot-sdk/) (technical preview) exposes the same execution loop that powers GitHub Copilot CLI as a library you can embed in your own applications. Instead of interacting with Copilot through an IDE or web interface, you programmatically create agent sessions, send prompts, and handle streaming responses.

Core capabilities:

- **Planning and execution** — the agent plans multi-step tasks, invokes tools, edits files, and runs commands
- **Multi-turn context management** — persistent memory across turns with intelligent session compaction
- **Model flexibility** — support for multiple AI models with user selection at different workflow steps
- **Tool integration** — custom tool definitions and MCP server support
- **Real-time streaming** — async task delegation with streaming responses

## Language Support

The SDK provides bindings for [Node.js, Python, Go, and .NET](https://github.blog/news-insights/company-news/build-an-agent-into-any-app-with-the-github-copilot-sdk/).

## Architecture

The SDK abstracts the infrastructure that the Copilot CLI uses in production:

- Planner and tool orchestration
- Multi-model routing
- MCP server management
- GitHub authentication flows
- Chat session persistence

This means applications built on the SDK inherit the same [production-tested execution loop](https://github.blog/news-insights/company-news/build-an-agent-into-any-app-with-the-github-copilot-sdk/) without reimplementing agent orchestration. Authentication flows through existing GitHub Copilot subscriptions or custom API keys.

## Agent-in-App Pattern

The SDK enables an "agent-in-app" architecture where AI coding capabilities are embedded directly in domain-specific tools rather than accessed through general-purpose interfaces. GitHub's announcement lists use cases including custom agent GUIs, speech-to-command workflows, content summarization tools, and purpose-built developer platforms [unverified].

This pattern lets you move agent capabilities from a fixed surface (IDE, CLI) to any application context where code generation, editing, or reasoning is valuable.

## Example

The following Node.js snippet illustrates the agent-in-app pattern: creating a session, sending a task prompt, and streaming the response to stdout. The SDK is in technical preview and the API surface may change; this example reflects the announced design rather than a stable release.

```typescript
import { createSession } from "@github/copilot-sdk";

const session = await createSession({
  auth: { type: "github-copilot" },
});

const stream = session.send({
  prompt: "Refactor src/utils.ts to use async/await throughout",
  tools: ["file_edit", "shell"],
});

for await (const chunk of stream) {
  process.stdout.write(chunk.text ?? "");
}

await session.close();
```

The `tools` array limits which capabilities the agent can invoke. Omitting it grants the full built-in tool set. Pass a custom MCP server URL in `mcpServers` to extend the agent with domain-specific tools at session creation time.

## Key Takeaways

- The Copilot SDK exposes Copilot CLI's production execution loop as an embeddable library you can integrate into your own applications
- Supports Node.js, Python, Go, and .NET with the same agent capabilities across all bindings [unverified]
- Enables the agent-in-app pattern: you embed planning, tool use, and file editing into custom applications
- MCP server support and custom tool definitions let you extend the agent's capabilities beyond built-in tools
- Currently in technical preview with authentication through Copilot subscriptions or custom API keys

## Unverified Claims

- Use cases including custom agent GUIs, speech-to-command workflows, content summarization tools, and purpose-built developer platforms [unverified]
- Same agent capabilities across all bindings (Node.js, Python, Go, .NET) [unverified]

## Related

- [Agent Mode](agent-mode.md)
- [Coding Agent](coding-agent.md)
- [MCP Integration](mcp-integration.md)
- [Agent HQ (Multi-Agent Platform)](agent-hq.md)
- [Copilot CLI Agentic Workflows](copilot-cli-agentic-workflows.md)
- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
