---
title: "MCP LLM Sampling: Servers Requesting AI Inference Mid-Tool"
term: "MCP LLM Sampling"
description: "How MCP servers use sampling/createMessage to request host LLM inference mid-execution, creating hybrid tools that combine deterministic logic with embedded AI reasoning."
tags:
  - tool-engineering
  - copilot
  - mcp
last_reviewed: 2026-06-13
maturity: adopted
---

# MCP LLM Sampling: Servers Requesting AI Inference Mid-Tool

> MCP sampling lets a server request the host's LLM mid-execution, turning a deterministic tool into a hybrid that embeds AI reasoning inline.

## Inverted request direction

Standard MCP flows in one direction: the client calls a tool on the server. Sampling inverts this. The server sends a `sampling/createMessage` request to the client, the client runs inference against its hosted model, and the result flows back to the server — all within a single tool execution.

GitHub [Copilot CLI](../tools/copilot/copilot-cli-agentic-workflows.md) v1.0.13 (March 30, 2026) introduced this capability: [MCP servers can request LLM inference (sampling) with user approval via a new review prompt](https://github.com/github/copilot-cli/releases/tag/v1.0.13).

## The sampling/createMessage request

The server sends a `sampling/createMessage` request with the fields defined in the [MCP sampling specification](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-03-26/client/sampling.mdx):

| Field | Required | Description |
|-------|----------|-------------|
| `messages` | Yes | Conversation to sample from (`SamplingMessage[]`) |
| `maxTokens` | Yes | Token ceiling — clients may use fewer |
| `systemPrompt` | No | Requested system prompt; client may modify or ignore |
| `modelPreferences` | No | Non-binding hints for speed, intelligence, and cost priority |
| `includeContext` | No | Whether to attach MCP server context (`allServers`, `thisServer`, `none`) |
| `temperature` | No | Sampling temperature |
| `stopSequences` | No | Strings at which to stop generation |

The response (`CreateMessageResult`) returns the generated content, the name of the model that actually ran, and the stop reason.

Two constraints apply regardless of server preferences:

1. The client decides which model runs. `modelPreferences` expresses hints — `intelligencePriority`, `speedPriority`, `costPriority`, and ordered model name hints — but the client keeps full discretion. A server cannot force a specific model: [hints are advisory, and clients make the final model selection](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-03-26/client/sampling.mdx).
2. The user approves each sampling request. The host shows a review prompt before inference runs, and you can allow or deny it. This is a [spec-level SHOULD](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-03-26/client/sampling.mdx) that requires a human in the loop who can deny sampling requests, not an implementation detail.

## When to use sampling

Sampling suits tools that need judgment, not just deterministic logic, to interpret their own output:

- Unstructured output interpretation — a fetch tool classifies a web page before returning it
- Decision points in multi-step execution — a build tool decides which compiler errors are actionable
- Summary generation — a research tool synthesizes raw results before returning them
- Conditional branching — a monitoring tool decides which alert category a log line falls into

These are judgment calls, not rules-based branches, so sampling routes them through the host model rather than requiring the server to embed its own LLM client (see the `sampling/createMessage` example below).

## Trade-offs

Coupling. The server's behavior depends on the host model's capability and behavior. The same tool may produce different results against different models. `CreateMessageResult` returns the actual model name so servers can detect this, but they cannot compensate for it at the protocol level.

Latency. Each `sampling/createMessage` call adds at least one inference round-trip within the tool call. Tools that sample repeatedly compound this. Design sampling calls to batch what they need in a single request.

Trust boundary. The user-approval gate is the main defense against a malicious or compromised server that uses sampling to exfiltrate context or manipulate the host model. Do not deploy MCP servers with sampling capability from untrusted sources without reviewing what they send in `messages` and `systemPrompt`.

Contrast with elicitation. MCP elicitation requests structured input from the user mid-task. Sampling requests inference from the model. Both interrupt deterministic tool execution, but for different inputs: human judgment for one, AI reasoning for the other. A tool can use both in sequence — [elicit](mcp-elicitation.md) a decision from the user, then sample to process the result.

## Example

A code review MCP server fetches a pull diff, then requests a summary of security-relevant changes before returning:

```json
{
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "Identify security-relevant changes in this diff:\n\n<diff content>"
        }
      }
    ],
    "maxTokens": 512,
    "systemPrompt": "You are a security reviewer. Return only findings relevant to auth, input validation, and data exposure.",
    "modelPreferences": {
      "intelligencePriority": 0.8,
      "speedPriority": 0.2,
      "costPriority": 0.0
    }
  }
}
```

The client presents this to the user for approval, runs inference, and returns the result to the server. The server incorporates the summary into its tool response.

## Key Takeaways

- `sampling/createMessage` is a server-to-client request — the opposite direction of normal MCP tool calls.
- The client chooses the model; `modelPreferences` are non-binding hints.
- User approval is required before each inference call — the host controls the gate.
- Use sampling for mid-execution decisions that require language model reasoning, not for tasks achievable with deterministic code.
- Each sampling call adds an inference round-trip; batch what you need in one request.

## Related

- [MCP Elicitation](mcp-elicitation.md)
- [MCP Client Design](mcp-client-design.md)
- [MCP Server Design](mcp-server-design.md)
- [MCP Client/Server Architecture](mcp-client-server-architecture.md)
