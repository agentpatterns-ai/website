---
title: "Typed Schemas at Agent Boundaries for Multi-Agent Systems"
description: "Formal schemas at agent boundaries enforce explicit contracts, preventing state mismanagement and silent failures across multi-agent system handoffs."
aliases:
  - "agent boundary contracts"
  - "typed agent interfaces"
tags:
  - agent-design
---

# Typed Schemas at Agent Boundaries for Multi-Agent Systems

> Formal schemas at every agent-to-agent interface establish explicit contracts that prevent state mismanagement, unpredictable outputs, and silent failures in multi-agent systems.

## The Problem: Missing Structure, Not Model Limitations

Most multi-agent failures stem from missing structure at handoff points, not from model capability gaps. When agents exchange unstructured text, each agent must guess the format, infer missing fields, and handle ambiguous outputs. [GitHub's engineering team identifies this as the primary failure mode](https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/) in multi-agent workflows and recommends applying distributed systems engineering rigor to agent coordination.

## Data Contracts with Typed Interfaces

Define explicit types for every piece of data that crosses an agent boundary. A TypeScript interface makes the contract visible and enforceable:

```typescript
type UserProfile = {
  id: number;
  email: string;
  plan: "free" | "pro" | "enterprise";
};
```

Treat [schema violations like contract failures](https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/): retry, repair, or escalate before bad state propagates to downstream agents. This is the same principle behind API versioning and protobuf contracts in microservice architectures — applied to agent-to-agent communication.

## Action Schemas with Discriminated Unions

Action schemas constrain agent outputs to enumerated outcomes using [discriminated unions](https://github.com/colinhacks/zod?tab=readme-ov-file#discriminated-unions) — a Zod primitive that enforces a tagged union where a single literal field (`type`) selects among mutually exclusive schemas:

```typescript
const ActionSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("request-more-info"), missing: z.array(z.string()) }),
  z.object({ type: z.literal("assign"), assignee: z.string() }),
  z.object({ type: z.literal("close-as-duplicate"), duplicateOf: z.number() }),
  z.object({ type: z.literal("no-action") }),
]);
```

The agent must return exactly one valid action. Anything else fails validation and triggers a retry or escalation. This eliminates the failure mode where an agent invents an action type that no downstream handler knows how to process.

## MCP as Runtime Enforcement

The [Model Context Protocol](../standards/mcp-protocol.md) adds a runtime enforcement layer by [defining input and output schemas on tool definitions](https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/):

```json
{
  "name": "create_issue",
  "input_schema": { "type": "object", "properties": { "title": { "type": "string" } }, "required": ["title"] },
  "output_schema": { "type": "object", "properties": { "id": { "type": "number" } } }
}
```

MCP validates before execution. Agents cannot invent fields, omit required inputs, or drift across interfaces. This moves validation from "hope the prompt works" to deterministic schema checking.

## Design Principles

The underlying principle is treating [agents like distributed systems, not chat flows](https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/):

- **Design for failure first** — every boundary assumes the upstream agent may produce invalid output
- **Validate every agent boundary** — no untyped data crosses between agents
- **Log intermediate state** — capture schema-validated payloads at each handoff for debugging
- **Expect retries and partial failures** — schema violations trigger structured recovery, not crashes

## When This Backfires

Typed schemas add overhead and rigidity — three conditions where the cost outweighs the benefit:

- **Rapid interface churn**: discriminated unions become a migration burden when action types change frequently. Every new action type requires updating schemas across all agents simultaneously; mismatched versions silently reject valid outputs during rolling deployments.
- **Exploratory or open-ended agents**: strict schemas block agents from returning legitimately unexpected outputs. A research agent that discovers a novel category it wasn't designed for will fail validation rather than surfacing the finding.
- **Schema complexity exceeds model reliability**: deeply nested or highly conditional schemas increase the rate of validation failures requiring retries. [When retry chains compound across multiple agent hops](https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/), latency and token costs can exceed the cost of tolerating occasional unstructured output.

Apply schemas at high-stakes boundaries — state transitions, inter-service calls, irreversible actions — and use looser validation for intermediate reasoning steps where flexibility matters more than precision.

## Key Takeaways

- Most multi-agent failures come from missing structure at boundaries, not model limitations
- Typed interfaces enforce data contracts; discriminated unions enforce action contracts
- MCP provides [runtime schema validation](https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/) that prevents field invention and drift
- Schema violations should trigger retry/repair/escalate flows, not silent propagation
- Agent-to-agent communication requires the same rigor as microservice API contracts

## Example

A triage agent receives a support ticket and must return a structured action. The orchestrator validates the response before routing it downstream:

```typescript
import { z } from "zod";

// Define the boundary contract
const TriageResult = z.object({
  ticketId: z.number(),
  action: z.discriminatedUnion("type", [
    z.object({ type: z.literal("escalate"), team: z.string(), reason: z.string() }),
    z.object({ type: z.literal("auto-resolve"), templateId: z.number() }),
    z.object({ type: z.literal("request-info"), questions: z.array(z.string()) }),
  ]),
  confidence: z.number().min(0).max(1),
});

// Orchestrator validates the agent's output
function handleTriageResponse(raw: unknown) {
  const result = TriageResult.safeParse(raw);
  if (!result.success) {
    // Schema violation: retry with the validation error as feedback
    return retryWithFeedback(result.error.format());
  }
  // Valid output: route to the appropriate downstream handler
  switch (result.data.action.type) {
    case "escalate":   return routeToTeam(result.data.action.team);
    case "auto-resolve": return applyTemplate(result.data.action.templateId);
    case "request-info": return sendFollowUp(result.data.action.questions);
  }
}
```

The orchestrator never inspects free-text output. If the triage agent returns an invalid shape — a missing field, an invented action type, or a confidence score outside `[0, 1]` — validation fails deterministically and triggers a retry before bad state reaches downstream agents.

## Related

- [Structured Output Constraints](../verification/structured-output-constraints.md)
- [Agent Composition Patterns](../agent-design/agent-composition-patterns.md)
- [Distributed Computing Parallels](../human/distributed-computing-parallels.md)
- [Tool Calling Schema Standards](../standards/tool-calling-schema-standards.md)
- [MCP Server Design](mcp-server-design.md)
- [MCP Client Design](mcp-client-design.md)
- [MCP Client-Server Architecture](mcp-client-server-architecture.md)
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md)
- [Agent Handoff Protocols](../multi-agent/agent-handoff-protocols.md)
- [Skill Tool Runtime Enforcement](skill-tool-runtime-enforcement.md)
