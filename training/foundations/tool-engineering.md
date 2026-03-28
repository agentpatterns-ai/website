---
title: "Tool Engineering for Agents: Design, Schemas, and MCP"
description: "Tool engineering shapes what agents can do and how much context each action costs — output design, minimalism, descriptions, poka-yoke, schemas, and MCP."
tags:
  - training
  - cost-performance
  - tool-agnostic
---
# Tool Engineering

> The quality of an agent's tools bounds the quality of its output -- no prompt compensates for a tool interface the model cannot use reliably.

Tool engineering is the discipline of designing the interfaces agents use to act on the world. Every tool call injects tokens into the context window, selects from competing options, and either succeeds or fails based on schema and description quality. The discipline sits at the convergence of [context cost](context-engineering.md), [instruction clarity](prompt-engineering.md), and [mechanical enforcement](harness-engineering.md) -- the three foundations covered in earlier modules. Where those shape what the agent sees and how it reasons, tool engineering shapes what it can do and how reliably it does it.

---

## Tools Are Context Injections

Every tool call has two costs: the tokens the agent spends selecting and invoking it, and the tokens its output injects into the context window. A tool returning a 10,000-token API response when 200 tokens suffice consumes budget that displaces reasoning and future tool results. [Anthropic identifies tool design as a direct lever on context quality](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) -- the shape of tool output determines how much of the window is signal versus noise.

This framing redefines what "good tool design" means for agents. A well-designed human API can afford verbose responses because humans read selectively. An agent processes every token. The design target shifts from "complete and well-documented" to "minimal and decision-relevant."

Three principles follow from this:

1. **Return only the next decision's inputs.** A CI status tool should return `"3 checks passed, 1 failed: lint"` -- not the full GitHub Actions run object with 40+ fields. See [Token-Efficient Tool Design](../../tool-engineering/token-efficient-tool-design.md) for the full pattern.

2. **Replace opaque identifiers with semantic equivalents.** UUIDs, MIME types, and internal codes are noise the agent must carry but cannot reason about. Return `"Q3 Budget Review"` and `"Word document"` instead. See [Semantic Tool Output](../../tool-engineering/semantic-tool-output.md).

3. **Apply filtering and pagination at the tool layer.** Tools that return full datasets shift the filtering burden to the agent, which either hallucinates the filter logic or consumes the entire dataset in context. Accept filter parameters and return bounded pages with sensible defaults.

---

## Fewer Tools, Better Results

The instinct to add more tools for coverage is counterproductive. [OpenAI's data agent team](https://openai.com/index/inside-our-in-house-data-agent/) found that exposing the full tool set created overlapping functionality that confused agents. Consolidating and restricting tool calls -- even removing valid options -- reduced ambiguity and improved end-to-end reliability.

The mechanism: before each call, the agent evaluates available tools and selects one. More tools means more evaluation tokens spent per decision. Overlapping tools force the agent to reason about *which* tool to use before it can reason about *the task*. That selection overhead compounds across every invocation in a session.

The audit is straightforward. Identify tool pairs with overlapping functionality -- multiple search tools without clear selection criteria, shell execution plus dedicated command tools for the same operations, multiple file-read mechanisms. For each overlap, either merge into one tool or add explicit selection criteria that make use cases non-overlapping. If the criteria are hard to articulate, merge. See [Tool Minimalism](../../tool-engineering/tool-minimalism.md) and [Consolidate Agent Tools](../../tool-engineering/consolidate-agent-tools.md) for detailed guidance.

Each surviving tool should map to a single, distinct sub-task. The test: if you cannot state in one sentence what a tool does that no other tool does, the tool set has overlap.

---

## Descriptions Are the Most Underinvested Lever

Agents select tools by reasoning about descriptions, not by browsing documentation. A tool with a weak description is effectively invisible for use cases the description fails to communicate -- even if the implementation handles them correctly. [Improving tool ergonomics including descriptions reduced task completion time by 40%](https://www.anthropic.com/engineering/multi-agent-research-system) in Anthropic's multi-agent research system.

The most common failure mode is a description accurate enough to explain what the tool does but not specific enough to tell the agent when to prefer it over alternatives. The fix is adding positive selection signals: "Use this tool when X" and "Prefer this over Y when Z." These are instructions to the agent, not documentation of the interface.

Write descriptions assuming the agent has never seen the underlying system. Include query syntax, domain terminology, resource relationships, and return shape -- the implicit context an experienced user takes for granted but an agent cannot infer. [Anthropic's guidance on writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) confirms that minor description refinements routinely yield dramatic accuracy improvements.

For MCP servers exposing many tools, each description must be self-contained. Agents may not read adjacent tool descriptions before selecting. See [Tool Description Quality](../../tool-engineering/tool-description-quality.md) and [Tool Descriptions as Onboarding](../../tool-engineering/tool-descriptions-as-onboarding.md).

---

## Make Wrong Calls Structurally Impossible

Documentation tells the agent how to use a tool correctly. Poka-yoke (mistake-proofing) makes incorrect use fail fast or become impossible. [Anthropic reports spending more time optimizing tools than the overall prompt](https://www.anthropic.com/engineering/swe-bench-sonnet) and applies this principle directly: "Change the arguments so that it is harder to make mistakes" ([Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).

Production patterns from real agent systems:

- **Absolute paths over relative.** Relative paths failed after directory changes. Requiring absolute paths [eliminated the failure mode entirely](https://www.anthropic.com/engineering/swe-bench-sonnet).
- **Enums over free text.** `file_type: Literal["python", "typescript", "all"]` prevents the agent from inventing values.
- **Read-before-write gates.** Claude Code's Edit tool rejects calls if the file has not been read in the current session -- a structural prerequisite, not an instruction.
- **Uniqueness constraints.** String replacement that requires `old_str` to match exactly one location forces the agent to provide sufficient context.
- **Training-aligned formats.** Inputs close to naturally-occurring text (JSON, markdown, prose) leverage model priors. Formats requiring line counting or custom DSLs [increase error rates](https://www.anthropic.com/engineering/building-effective-agents).

The design question for any new tool: can any parameter accept values that are never valid? Does the tool depend on prior state without enforcing it? Can the output overwhelm the context window? See [Poka-Yoke for Agent Tools](../../tool-engineering/poka-yoke-agent-tools.md) for the full catalog.

---

## Typed Schemas at Agent Boundaries

When agents exchange data -- with other agents, with tool servers, with downstream systems -- unstructured text at the boundary is the primary failure mode. [GitHub's engineering team identifies missing structure at handoff points, not model capability gaps, as the primary source of multi-agent failures](https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/).

The fix is the same discipline applied to microservice APIs: typed interfaces for data contracts, discriminated unions for action contracts, and runtime validation that rejects invalid payloads before they propagate.

MCP adds a runtime enforcement layer by defining input and output schemas on tool definitions. Agents cannot invent fields, omit required inputs, or drift across interfaces when the schema is validated before execution. Treat schema violations like contract failures: retry, repair, or escalate. See [Typed Schemas at Agent Boundaries](../../tool-engineering/typed-schemas-at-agent-boundaries.md).

---

## MCP as Architecture

The [Model Context Protocol](../../standards/mcp-protocol.md) is the emerging standard for agent-tool integration. The architectural decisions that matter are not protocol mechanics but deployment topology and tool surface design.

**Transport selection** is a deployment decision. Use stdio (server runs as subprocess of the client) unless you need multiple clients connecting to the same server or the server must run on a different machine. Streamable HTTP introduces network exposure, authentication requirements, and [Origin header validation to prevent DNS rebinding attacks](https://modelcontextprotocol.io/docs/concepts/transports).

**Tool surface design** determines agent performance. [Claude Code automatically defers MCP tool definitions when they exceed 10% of the context window](https://www.anthropic.com/engineering/advanced-tool-use), achieving an 85% token reduction compared to pre-loading. Servers with large tool surfaces should support lazy loading and the `listChanged` capability for dynamic refresh.

**Error handling** has two distinct mechanisms that serve different purposes: JSON-RPC protocol errors (infrastructure failures -- unknown tool, malformed arguments) and tool execution errors with `isError: true` (application failures the agent can reason about). A server that returns a generic protocol error for a database timeout denies the agent the information it needs to retry or fall back. See [MCP Client/Server Architecture](../../tool-engineering/mcp-client-server-architecture.md).

---

## Skills: Packaging Knowledge as Reusable Tools

Skills extend the tool surface with domain knowledge. A well-authored skill includes the conventions, edge cases, and gotchas that the base model would otherwise get wrong -- written as a delta from baseline model behavior, not a comprehensive tutorial.

The description field determines whether the agent loads a skill. Structure it as: what it does, when to use it, key capabilities. Include trigger phrases users would actually say. Add negative triggers to prevent over-firing. Debug by asking the agent "When would you use this skill?" -- it quotes the description back, revealing gaps.

The highest-signal content in any skill is the Gotchas section: cases where the agent would do something plausible but wrong. Build it incrementally from real failures, not from anticipated ones. See [Skill Authoring Patterns](../../tool-engineering/skill-authoring-patterns.md) for the five implementation patterns and testing methodology.

---

## Key Takeaways

- Every tool response is a context injection. Size it for the agent's next decision, not for completeness.
- Fewer, non-overlapping tools outperform large tool sets. [Consolidating tools improved reliability even when it removed valid options](https://openai.com/index/inside-our-in-house-data-agent/).
- Tool descriptions are prompt engineering surfaces. Add selection signals ("use this when X, prefer Y when Z"), not just capability summaries.
- Poka-yoke eliminates error classes structurally. Require absolute paths, use enums, enforce read-before-write gates, validate early.
- Typed schemas at agent boundaries prevent the primary multi-agent failure mode: missing structure at handoff points.
- MCP tool surface design is a performance lever. Keep tools focused, defer large surfaces, implement both protocol and execution error channels.
- Skill effectiveness depends on description craft and gotcha documentation, not comprehensiveness.

## Related

**Source pages (detailed patterns)**

- [Tool Engineering](../../tool-engineering/tool-engineering.md) -- foundational principles
- [Token-Efficient Tool Design](../../tool-engineering/token-efficient-tool-design.md) -- output shaping for context cost
- [Tool Minimalism](../../tool-engineering/tool-minimalism.md) -- fewer tools, goal-oriented prompting
- [Tool Description Quality](../../tool-engineering/tool-description-quality.md) -- selection signals and iteration
- [Tool Descriptions as Onboarding](../../tool-engineering/tool-descriptions-as-onboarding.md) -- implicit context for agents
- [Poka-Yoke for Agent Tools](../../tool-engineering/poka-yoke-agent-tools.md) -- structural mistake-proofing
- [Consolidate Agent Tools](../../tool-engineering/consolidate-agent-tools.md) -- reducing surface area
- [Semantic Tool Output](../../tool-engineering/semantic-tool-output.md) -- agent-readable output design
- [Typed Schemas at Agent Boundaries](../../tool-engineering/typed-schemas-at-agent-boundaries.md) -- contracts for multi-agent handoffs
- [MCP Client/Server Architecture](../../tool-engineering/mcp-client-server-architecture.md) -- transport, errors, security
- [Skill Authoring Patterns](../../tool-engineering/skill-authoring-patterns.md) -- building reusable agent skills

**Sibling modules**

- [Prompt Engineering](prompt-engineering.md) -- [system prompt altitude](../../instructions/system-prompt-altitude.md), polarity, compliance ceiling
- [Context Engineering](context-engineering.md) -- context window mechanics, compression, caching
- [Harness Engineering](harness-engineering.md) -- repo legibility, mechanical enforcement, backpressure
- [How the Four Disciplines Compound](prompt-context-harness-capstone.md) -- the multiplication model and diagnostic framework

**Other training modules**

- [GitHub Copilot: Context Engineering & Agent Workflows](../copilot/context-and-workflows.md)
