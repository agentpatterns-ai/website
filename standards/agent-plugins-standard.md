---
title: "Agent Plugins: Portable Packaging With Client-Defined Trust"
description: "The Agent Plugins 1.0.0 standard fixes where skills and MCP servers sit inside a plugin directory, and leaves installation, distribution, provenance, and permissions to each consuming client."
tags:
  - standards
  - tool-engineering
  - tool-agnostic
term: "Agent Plugins"
aliases:
  - Agent Plugins specification
  - Agent Plugins 1.0.0
last_reviewed: 2026-08-06
maturity: emerging
---

# Agent Plugins: Portable Packaging With Client-Defined Trust

> Agent Plugins fixes where skills and MCP servers sit in a plugin directory, and leaves installation, trust, and permissions to each client.

The standard pays off under two conditions. You publish a plugin that several different agent clients consume, and the parts you ship are skills or MCP servers. Outside those conditions the format costs a manifest and returns little, because the portable surface stops well short of a whole plugin.

## What the format fixes

An Agent Plugin is "a directory with a `plugin.json` manifest and fixed locations for its components" ([Vercel](https://vercel.com/blog/introducing-agent-plugins)). Skills live in `skills/`, MCP server configuration in `mcp.json`, and client-specific files in reverse-domain namespace directories such as `com.example.client/`. The manifest requires two fields, `$schema` and `name`; `version`, `description`, `author`, `license`, and the rest are optional ([Agent Plugins specification v1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)).

Governance is charter-based. Vercel proposed the format and refined it with AWS, Anysphere, GitHub, Microsoft, and OpenAI. Maintainers on the steering committee come from AWS, Cursor, Microsoft, OpenAI, and Vercel. The charter binds that composition: "No single vendor may control a majority of Core Maintainer seats," and "No seats are reserved for specific companies" ([governance charter](https://github.com/agentplugins/agent-plugins-spec/blob/main/GOVERNANCE.md)). Launch clients are ChatGPT and Codex, Cursor, GitHub Copilot, Kiro, and VS Code ([Vercel](https://vercel.com/blog/introducing-agent-plugins)).

## What the format leaves to the client

The spec "leaves installation, distribution, policy, user experience, and client-specific capabilities to each client" ([Vercel](https://vercel.com/blog/introducing-agent-plugins)). No registry, no signing, no publisher identity, no permission model.

Some safety rules do travel with the package. Paths must resolve inside the plugin root and symlinks pointing outside are rejected, plugins "MUST NOT embed credentials or other secrets" in `env` or `headers`, and non-loopback MCP endpoints must use HTTPS. The spec then draws the line explicitly: "These containment rules govern access to files supplied by the plugin package. They do not sandbox a plugin subprocess or restrict paths supplied at runtime" ([Agent Plugins specification v1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)).

So the trust decision stays with whoever installs. VS Code supplies its own warning at that moment: "Plugins can include hooks and MCP servers that run code on your machine. Review the plugin contents and publisher before installing, especially for plugins from community marketplaces" ([VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins)). Organizations gate the feature through `chat.plugins.enabled`, which an administrator can manage centrally. One portable package still needs that policy configured in every client that reads it.

## Why it works

The format attacks an N×M problem. Plugin authors previously rearranged or duplicated the same components for each client's layout, so fixing the filesystem layout collapses the client axis for the components it covers ([Vercel](https://vercel.com/blog/introducing-agent-plugins)). The namespaced extension directory is what lets a minimal version ship at all: "Each client defines its own namespace, and other clients ignore it. This prevents client-specific behavior from leaking into the common format or blocking adoption of the shared components" ([Vercel](https://vercel.com/blog/introducing-agent-plugins)). The standard never has to settle the argument about the non-portable parts before shipping the portable ones. That same escape hatch is why the guarantee covers less than the phrase "portable plugin" suggests.

## When this backfires

- Your plugin's value sits in hooks, slash commands, subagents, or rules. Those component types "remain too client-specific for a stable portable contract and are outside the v1 format until their formats converge" ([Agent Plugins specification v1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)). Conforming yields a manifest plus per-client namespace directories, which is client-specific distribution wearing a standard.
- Your team standardizes on one client. With no second consumer there is no fragmentation to collapse, and the client's native layout is simpler than the portable one plus its extension directory.
- A reviewer treats conformance as a safety signal. A valid Agent Plugin carries no publisher identity, signature, or permission grant, and the spec declines to sandbox subprocesses, so validity says nothing about whether installing is safe.
- You expect the standard to replace incumbent formats. VS Code reads `mcp.json` for Agent Plugins 1.0 and `.mcp.json` for the Copilot and Claude formats ([VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins)), so implementers carry the new format alongside the old ones.
- You count on universal vendor coverage. Anthropic appears nowhere in the announcement as a launch client, contributing company, or committee member ([Vercel](https://vercel.com/blog/introducing-agent-plugins)), despite Agent Skills being one of the two component types the format packages.

## Example

A team publishes a database-migration helper: one skill, one MCP server, and a set of hooks that block destructive statements. Laid out to the spec, with the namespace placeholder the spec itself uses:

```text
migration-helper/
├── plugin.json          # $schema + name; portable
├── skills/
│   └── review-migration/
│       └── SKILL.md     # portable
├── mcp.json             # portable
└── com.example.client/
    └── hooks.json       # client-owned; ignored by everything else
```

The skill and the MCP server travel. The hooks do not, because hooks are outside v1, so they sit in a namespace directory a client is required to skip unless it implements that namespace ([Agent Plugins specification v1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)). The trust decision does not travel either. Every consuming client reads the same first three entries, then applies its own install flow, approval prompt, and administrator policy before anything runs.

## Key Takeaways

- Agent Plugins 1.0.0 standardizes one thing: a directory with `plugin.json`, `skills/`, and `mcp.json` at fixed locations ([Agent Plugins specification v1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)).
- Installation, distribution, policy, and user experience stay with each client ([Vercel](https://vercel.com/blog/introducing-agent-plugins)), so conformance is a packaging claim rather than a trust claim.
- Path containment and the ban on embedded secrets travel with the package; subprocess sandboxing does not ([Agent Plugins specification v1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)).
- Version 1 covers skills and MCP servers only. Hooks, commands, subagents, and rules stay in client-owned namespace directories.
- Judge adoption by how much of your plugin lands in the portable half. A skills-and-MCP plugin gains most; a hooks-heavy one mostly gains a manifest.

## Related

- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md) — the git-based bundle model this format specifies a portable layout for
- [Agent Skills: A Cross-Tool Task Knowledge Standard](agent-skills-standard.md) — the `SKILL.md` format that fills the `skills/` directory
- [MCP: The Plumbing Behind Agent Tool Access](mcp-protocol.md) — the protocol behind the servers `mcp.json` configures
- [Cross-IDE Plugin Discovery: One Install Surface, Many Consuming Agents](cross-ide-plugin-discovery.md) — the shared install path on one machine, where this standard fixes the package instead
- [Pre-Install Plugin Transparency: Capability Inventory and Cost Projection](pre-install-plugin-transparency.md) — the pre-install disclosure layer the spec leaves to each client
