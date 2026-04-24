---
title: "Open Standards and Protocols for AI Agent Development"
description: "Open standards and conventions shaping the AI agent ecosystem. - Agent-to-Agent (A2A) Protocol — An open standard for inter-agent communication — agents"
tags:
  - standards
  - tool-agnostic
---
# Standards

> Open standards and conventions shaping the AI agent ecosystem.

## Pages

- [A2UI: Framework-Agnostic Generative UI Standard](a2ui.md) — An open standard for agents to emit declarative UI blueprints that a host application renders with its own native components
- [Agent-to-Agent (A2A) Protocol](a2a-protocol.md) — An open standard for inter-agent communication — agents discover capabilities, delegate tasks, and exchange results over HTTP
- [Agent Cards: Capability Discovery Standard](agent-cards.md) — Machine-readable JSON descriptors that advertise agent capabilities, skills, and authentication at a well-known URL
- [Agent Definition Formats: How Tools Define Agent Behavior](agent-definition-formats.md) — Agent definitions control system prompt, tool access, model selection, and permissions — the format varies by tool but the concerns are the same across all implementations
- [Agent Skills: Cross-Tool Task Knowledge Standard](agent-skills-standard.md) — The Agent Skills open standard packages task-specific knowledge into portable SKILL.md folders that AI coding tools can discover and load on demand
- [AGENTS.md: A README for AI Coding Agents](agents-md.md) — AGENTS.md is an open standard for a project-level instruction file that gives AI coding agents the context they need to work effectively in a codebase
- [llms.txt: Making Your Project Discoverable to AI Agents](llms-txt.md) — Publish a standardized /llms.txt so agents can navigate your site without crawling every page
- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md) — The Model Context Protocol is an open standard for connecting AI agents to external tools and data sources
- [OAuth Client ID Metadata Documents (CIMD) for MCP Servers](oauth-client-id-metadata-documents.md) — CIMD makes an OAuth client_id a URL that dereferences to a JSON metadata document — the registration mechanism MCP recommends for cloud-hosted servers
- [OpenAPI as Agent Tool Specification](openapi-agent-tool-spec.md) — Use existing OpenAPI specs as the source of truth for agent tool definitions instead of writing schemas by hand
- [OpenTelemetry for Agent Observability](opentelemetry-agent-observability.md) — Vendor-neutral tracing standard for LLM calls, tool invocations, and agent spans using GenAI semantic conventions
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md) — Package agents, skills, MCP servers, and hooks into installable bundles that solve the distribution problem for agent capabilities
- [Portable Agent Definitions: Full-Stack Identity as Code](portable-agent-definitions.md) — Package an entire agent as a version-controlled, framework-agnostic git artifact using the gitagent open standard
- [Tool Calling Schema Standards](tool-calling-schema-standards.md) — Tool definitions converge on JSON Schema across providers but differ in field names, strict modes, and wrapping structures
