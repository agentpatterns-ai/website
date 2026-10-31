---
title: "Agentic Resource Discovery: Federated Pre-Invocation Search"
description: "The v0.91 proposal describes searchable JSON-LD entries for MCP servers, A2A agents, and skills, with trust verification separate from relevance."
tags:
  - agent-design
  - tool-agnostic
  - standards
aliases:
  - ARD discovery specification
  - Agentic Resource Discovery spec
  - ai-catalog.json discovery
last_reviewed: 2026-10-28
maturity: emerging
---

# Agentic Resource Discovery: Federated Pre-Invocation Search

> Agentic Resource Discovery describes resources as searchable entries so clients can find capabilities through registries before invoking their underlying protocols.

The Agentic Resource Discovery specification (ARD) is a proposal for discovering MCP servers, A2A agents, and skills across registries. Version 0.91, dated August 26, 2026, describes entries as JSON-LD nodes. It preserves existing entries while adding namespace extensions through `@context` ([ARD specification, overview](https://agenticresourcediscovery.org/spec/)).

## What discovery supplies

ARD moves resource selection into a search service instead of putting every description in the model's context. A registry must expose an HTTP REST search interface. Authentication for invoking a resource remains the responsibility of its artifact protocol ([ARD specification, sections 3.2–3.6](https://agenticresourcediscovery.org/spec/)).

Each entry requires `identifier`, `displayName`, `type`, and exactly one of `url` or `data`. The identifier uses the domain-anchored form `urn:air:<publisher>:[<namespace>:]<agent-name>`. A URL references the artifact; `data` carries it inline ([ARD specification, sections 4.2–4.3](https://agenticresourcediscovery.org/spec/)).

The specification recommends two to five `representativeQueries` as search examples. Missing examples produce conformance warnings rather than schema rejection. Optional `capabilities` tokens support filtering without fetching the artifact. Consumers expand entries using ARD's base JSON-LD context; publishers can add namespaces through an entry's own `@context` ([ARD specification, sections 4.1–4.2](https://agenticresourcediscovery.org/spec/)).

`POST /search` is required. Browsing through `POST /explore` and listing through `GET /agents` are optional. Discovery can run during integration or while an agent works, over an approved collection or a broader index ([How ARD works](https://agenticresourcediscovery.org/how_ard_works/)).

## Trust remains a separate decision

The optional `trustManifest` can carry identity, attestations, provenance, and signatures. Its identity must align with the publisher domain in the discovery identifier. ARD delegates signing and verification procedures to the manifest's declared trust framework. Federated registries should verify the manifest and can use the result for admission, ranking, or filtering ([ARD specification, section 4.5](https://agenticresourcediscovery.org/spec/)).

A search score measures relevance only. The specification explicitly forbids treating it as a trust, compliance, or safety judgment. An organizational compliance attestation also says nothing by itself about a particular artifact's safety. Artifact attestations should identify the evaluated artifact by digest ([ARD specification, sections 4.5.2 and 5.3.2](https://agenticresourcediscovery.org/spec/)).

## When this backfires

- You treat discovery as authorization. Keep permission checks on the invocation path; ARD delegates authentication to the artifact protocol.
- You accept an unverified trust manifest. The declared framework and publisher binding still need checking.
- You search the open web when the task needs an approved collection. ARD also supports restricted collections, which its guide identifies as the likely enterprise case ([How ARD works](https://agenticresourcediscovery.org/how_ard_works/)).
- You require registered media types before accepting entries. Section 3.3 says registration is pending and directs intermediaries to omit strict verification of those types ([ARD specification](https://agenticresourcediscovery.org/spec/)).

## Governance context

The AAIF launch announcement names MCP, AGENTS.md, and Block's goose as contributions ([Block announcement](https://block.xyz/inside/block-anthropic-and-openai-launch-the-agentic-ai-foundation)). Anthropic announced the Agent Skills donation on October 22, 2026. It describes this as "donating the standard to the Agentic AI Foundation (AAIF) under the Linux Foundation" ([Anthropic announcement](https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation)). These examples are not an exhaustive project roster, and neither announcement establishes ARD membership.

## Example

This weather-server entry comes from section 4.4. It names the artifact type and supplies the queries a registry can index ([ARD specification](https://agenticresourcediscovery.org/spec/)):

```json
{
  "identifier": "urn:air:acme.com:server:weather",
  "displayName": "Weather Data Node",
  "type": "application/mcp-server-card+json",
  "url": "https://api.acme.com/mcp/weather.json",
  "capabilities": ["WeatherTool", "ForecastTool"],
  "description": "Enterprise weather MCP server for live telemetry.",
  "representativeQueries": [
    "what is the current wind speed in Chicago",
    "get the 5-day forecast for Seattle"
  ]
}
```

The entry describes the server. Its search relevance does not authorize a connection or verify the server's safety.

## Key Takeaways

- Validate discovery entries separately from the artifacts they describe.
- Supply representative queries even though their absence is only a conformance warning.
- Check publisher binding and the declared trust framework before relying on attestations.
- Keep search relevance separate from permission and safety decisions.

## Related

- [MCP: The Open Protocol Connecting Agents to External Tools](mcp-protocol.md)
- [Agent Cards: Capability Discovery Standard for AI Agents](agent-cards.md)
- [Agent Skills: A Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [WebMCP: Browser-Hosted Tool Contracts for In-Page AI Agents](webmcp.md)
- [Filesystem-Based Tool Discovery for AI Agent Development](../tool-engineering/filesystem-tool-discovery.md)
- [Skill Supply-Chain Poisoning](../security/skill-supply-chain-poisoning.md)
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md)
