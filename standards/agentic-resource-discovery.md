---
title: "Agentic Resource Discovery: Federated Pre-Invocation Search"
description: "A v0.9 draft open spec defining ai-catalog.json manifests and federated registries so agents find MCP, A2A, and skills before invocation."
tags:
  - agent-design
  - tool-agnostic
  - standards
aliases:
  - ARD discovery specification
  - Agentic Resource Discovery spec
  - ai-catalog.json discovery
last_reviewed: 2026-06-17
maturity: emerging
---

# Agentic Resource Discovery: Federated Pre-Invocation Search

> A draft open spec — `ai-catalog.json` manifests plus federated registries — for finding MCP servers, A2A agents, and skills before invocation.

## When ARD is the right layer

Agentic Resource Discovery (ARD) is useful only when three conditions hold together. Reach for it when:

- The catalog of MCP servers, A2A agents, and Skills the agent might call is large enough (hundreds to thousands of capabilities) that loading every tool description into the context window becomes the bottleneck for selection ([ARD Specification §2, §3.2](https://agenticresourcediscovery.org/spec/)).
- Publishers can ship a signed Trust Manifest and consumers verify it, so domain ownership plus attestation gives a meaningful identity check rather than a publisher's self-claim ([ARD Specification §5](https://agenticresourcediscovery.org/spec/)).
- The principal that performs discovery is not the same principal that processes untrusted content with egress — otherwise the discovery surface becomes a prompt-injection amplifier ([AppOmni: Agent-to-Agent Discovery Prompt Injection, ServiceNow Now Assist](https://thehackernews.com/2025/11/servicenow-ai-agents-can-be-tricked.html)).

When any of those three conditions fails, a pinned, allowlisted resource set is the safer default. ARD is the discovery layer above [MCP](mcp-protocol.md), [A2A](a2a-protocol.md), and the [Agent Skills standard](agent-skills-standard.md). It does not replace them, and it does not on its own harden the resources it surfaces.

## What ARD defines

The [Agentic Resource Discovery Specification](https://agenticresourcediscovery.org/spec/) is a v0.9 draft (Status: Proposal, 28 May 2026), authored by Junjie Bu (Google), R.V. Guha (Microsoft), and Shaun Smith (Hugging Face), Apache-2.0 licensed at [ards-project/ard-spec](https://github.com/ards-project/ard-spec). It builds on the AI Catalog Working Group's underlying data model under the Linux Foundation ([Google Developers blog: Announcing the Agentic Resource Discovery specification](https://developers.googleblog.com/en/announcing-the-agentic-resource-discovery-specification/)).

The spec sits entirely before invocation. It standardizes how a client asks "what is available for this task?" and how a discovery service answers, then steps out of the way so the client connects via the resource's native protocol ([ARD Home](https://agenticresourcediscovery.org/)).

Two primitives carry the model:

- Catalogs: a publisher hosts `ai-catalog.json` at `/.well-known/ai-catalog.json` under its own domain. The manifest lists catalog entries — each one a uniformly-shaped envelope with a `type` field set to an IANA media type (`application/mcp-server+json`, `application/a2a-agent-card+json`, `application/ai-catalog+json` for nested bundles), an `identifier` URN, and exactly one of `url` (remote reference) or `data` (inline artifact) ([ARD Specification §3.3, §3.4, §4.1](https://agenticresourcediscovery.org/spec/)).
- Registries: services that crawl published catalogs, index their contents, and expose a REST search interface. A registry MUST expose `POST /search` for task-driven lookup ("what can help me do X?"); `POST /explore` and `GET /agents` are optional ([How ARD works §4](https://agenticresourcediscovery.org/how_ard_works/), [ARD Specification §7](https://agenticresourcediscovery.org/spec/)).

The envelope is deliberately artifact-agnostic. ARD does not redefine MCP server schemas, Agent Card schemas, or skill formats. It carries them with a media type the client can dispatch on ([ARD Specification §3.3](https://agenticresourcediscovery.org/spec/)).

## Why it works

LLM tool selection scales linearly with the size of the tool catalog because every tool description has to fit in the context window before the model can pick one. At thousands of MCP servers, A2A agents, and skills, the descriptions alone exceed the available token budget before the task work begins ([ARD Specification §2](https://agenticresourcediscovery.org/spec/)). ARD applies the same mechanism search engines apply to the open web: move selection out of the model into a dedicated retrieval service that indexes richer signals — representative queries, publisher identity, compliance metadata — without consuming context tokens ([ARD Specification §3.2](https://agenticresourcediscovery.org/spec/)).

This is the cross-domain generalization of [filesystem-based tool discovery](../tool-engineering/filesystem-tool-discovery.md): lazy-load the descriptors the agent actually needs instead of registering everything upfront. ARD lifts the same lazy-load mechanism above one organization, with domain ownership as the cryptographic root for who published what the search returns.

## When this backfires

Runtime discovery is the same surface as runtime injection. The cases below mark where reaching for ARD makes the system worse than a curated, pinned resource set.

- Discovery plus untrusted content plus egress on one principal — Now Assist's agent-to-agent discovery let a benign agent recruit a privileged one when fed a crafted ticket body, exfiltrating data and modifying records ([AppOmni / ServiceNow disclosure](https://thehackernews.com/2025/11/servicenow-ai-agents-can-be-tricked.html)). ARD turns that exact discoverability into a product across organizational boundaries. Treat it as a multiplier on the [lethal trifecta threat model](../security/lethal-trifecta-threat-model.md); a principal that holds private data and egress should not also be free to discover new capabilities mid-task.
- Small, stable inventories — for fewer than roughly twenty MCP servers and skills that change rarely, an allowlisted config file or a [scoped-credentials proxy](../security/scoped-credentials-proxy.md) gets the same answer with no registry round-trip, no JSON Schema validation, and no protocol surface to misconfigure. ARD's "scale beyond context windows" claim assumes thousands of resources are in play.
- Trust manifest absent or unverified — the spec lets publishers ship a catalog without an Attestation object, and §3.3 explicitly instructs intermediaries to omit strict media-type verification while IANA registration is pending: "Implementers should note that while well-known path directories (like `/.well-known/agent-card.json`) are officially registered permanent entries, full type registrations are pending working group joint submission and the format may change. In the meantime, omit strict verification of these types by intermediaries." ([ARD Specification §3.3 note](https://agenticresourcediscovery.org/spec/)). Until attestation is mandatory and verified, "verified publisher" reduces to "controls the domain", which composes poorly with [skill supply-chain poisoning](../security/skill-supply-chain-poisoning.md) attacks operating at the artifact layer.
- Federation across mixed trust roots — ARD defers ranking, trust, and access policy to each registry operator. A consumer that federates indexes across multiple operators inherits the weakest one's trust posture; there is no protocol-level floor ([ARD Specification §8](https://agenticresourcediscovery.org/spec/)).
- Closed enterprise inventories with existing governance — when a platform team already curates an MCP fleet, signs releases, and pins versions in [enterprise-managed plugin governance](../security/enterprise-managed-plugin-governance.md), ARD adds discovery the team did not need. The spec acknowledges this: "in practice most enterprises will want the restricted case: discovery scoped to a governed, approved set rather than the open web" ([How ARD works §3](https://agenticresourcediscovery.org/how_ard_works/)).

## Adoption status

The spec is v0.9 (Draft, Status: Proposal). The contributor logo wall lists Cisco, Databricks, GitHub, GoDaddy, Google, Hugging Face, Microsoft, Nvidia, Salesforce, ServiceNow, and Snowflake ([ARD Home](https://agenticresourcediscovery.org/)). Google's hosted implementation is Agent Registry inside Gemini Enterprise Agent Platform, with native ARD support promised "in the coming months" rather than shipping today ([Google Developers blog](https://developers.googleblog.com/en/announcing-the-agentic-resource-discovery-specification/)).

ARD is not part of the Linux Foundation's Agentic AI Foundation (AAIF), which currently hosts MCP, AGENTS.md, and Block's goose framework as neutral-governance projects ([Block: Agentic AI Foundation launch](https://block.xyz/inside/block-anthropic-and-openai-launch-the-agentic-ai-foundation)). Neither Anthropic nor OpenAI has announced a client-side implementation of ARD at the time of writing. The reference repo carries 16 stars and four open issues against a six-week-old default branch ([ards-project/ard-spec](https://github.com/ards-project/ard-spec)). Track adoption as a capability to watch, not a settled standard to design against.

## Example

A publisher advertises one A2A agent and one MCP server through a single manifest, anchored to its own domain. The manifest below is the structural shape from the spec ([ARD Specification §4.1](https://agenticresourcediscovery.org/spec/)):

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Enterprise AI",
    "identifier": "did:web:acme.com"
  },
  "entries": [
    {
      "identifier": "urn:ai:acme.com:agent:assistant",
      "displayName": "Corporate Assistant (A2A)",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme.com/agents/assistant.json",
      "description": "General-purpose corporate A2A assistant.",
      "representativeQueries": [
        "help me draft an email to the security working group",
        "summarize my unread messages from Todd"
      ]
    },
    {
      "identifier": "urn:ai:acme.com:server:weather",
      "displayName": "Weather Data Node",
      "type": "application/mcp-server+json",
      "url": "https://api.acme.com/mcp/weather.json",
      "capabilities": ["WeatherTool", "ForecastTool"],
      "description": "Enterprise weather MCP server for live telemetry.",
      "representativeQueries": [
        "what is the current wind speed in Chicago",
        "get the 5-day forecast for Seattle"
      ]
    }
  ]
}
```

A registry crawls `https://acme.com/.well-known/ai-catalog.json`, indexes the entries together with their `representativeQueries`, and answers a client `POST /search` with the matching `urn:ai:acme.com:server:weather` envelope. The client then fetches the MCP server descriptor from `url` and connects using MCP — ARD does not participate in the invocation. Domain ownership of `acme.com` is the trust root; without a signed Attestation object on the entry, that is the only identity check the consumer gets.

## Key Takeaways

- ARD is a v0.9 draft spec (28 May 2026) defining `ai-catalog.json` manifests at `/.well-known/ai-catalog.json` and federated registries with a REST `POST /search` interface — the discovery layer above MCP, A2A, and Agent Skills.
- The mechanism is information retrieval: move tool selection out of the LLM context window into a dedicated search service so the catalog can scale beyond what fits in the prompt.
- Catalog entries are artifact-agnostic envelopes keyed by IANA media type (`application/mcp-server+json`, `application/a2a-agent-card+json`); ARD does not redefine the underlying schemas.
- Trust today is weak: attestation is optional, the spec instructs intermediaries to omit strict media-type verification pending IANA registration, and "verified publisher" reduces to "controls the domain". Treat ARD as discovery, not as a hardened trust layer.
- ARD productizes agent-to-agent discoverability across organizational boundaries — the same surface that enabled the ServiceNow Now Assist second-order prompt injection. Do not run it on a principal that also holds untrusted-content access and egress.
- ARD is not part of the Linux Foundation Agentic AI Foundation track; neither Anthropic nor OpenAI has announced client-side support. Track adoption rather than building against the draft.

## Related

- [MCP: The Open Protocol Connecting Agents to External Tools](mcp-protocol.md)
- [Agent Cards: Capability Discovery Standard for AI Agents](agent-cards.md)
- [Agent Skills: A Cross-Tool Task Knowledge Standard](agent-skills-standard.md)
- [WebMCP: Browser-Hosted Tool Contracts for In-Page AI Agents](webmcp.md)
- [Filesystem-Based Tool Discovery for AI Agent Development](../tool-engineering/filesystem-tool-discovery.md)
- [Skill Supply-Chain Poisoning](../security/skill-supply-chain-poisoning.md)
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md)
