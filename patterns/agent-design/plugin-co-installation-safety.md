---
title: "Designing Agent Plugins to Survive Co-Installation"
term: "Plugin Co-Installation Safety"
description: "Packaging conformance is checkable on one plugin alone. The failure a user hits needs a second plugin claiming the same capability name."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - capability name collision
  - plugin composition safety
  - plugin co-installation
last_reviewed: 2026-09-22
maturity: emerging
---

# Designing Agent Plugins to Survive Co-Installation

> Conformance checks one plugin alone. Co-installation is the configuration users run, and nothing in the standard decides which plugin answers.

Plugin co-installation safety is the set of packaging choices that keep your bundle working when a stranger's plugin is installed beside it. Agent Plugins v1.0.0 fixes where a bundle's files sit. It defines no qualified identity for a capability, no precedence rule when two installed plugins claim the same name, and no dependency relation between plugins, so "the same two plugins behave differently on different agents" ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)). That census covered 68,072 bundles across 30,655 repositories. Of the 31,901 that export a named capability, 81% share at least one name with another plugin, and a different-owner filter lowers that only to 74% ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)).

## When this applies

Three conditions have to hold before this earns your time. Strangers install your plugin next to plugins you have never seen, more than one client consumes it, and it exports named capabilities rather than only an MCP server. An internal bundle, published by one owner to one client, hits none of the failures below.

## Four moves you control

Ship the manifest at the bundle root with a `$schema` declaration. Omitting it is fatal rather than cosmetic: the client "MUST reject the plugin and MUST NOT discover or execute any of its components" ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)). Granting every manifest a correct `$schema` and changing nothing else takes the load rate from 6.4% to 96.6%.

Put client-specific data in the manifest's `extensions` object rather than inventing a top-level field. The v1.0.0 schema is closed, so a field it does not name is one the client must ignore. Your plugin loads and the host drops what you wrote. 40.2% of bundles would load with at least one field discarded, and 1.9% of manifests use the reverse-domain `extensions` object the specification already sanctions ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)).

Prefix the capability names you export. Do not ship a skill called `code-review`. `code-reviewer` is claimed by 300 distinct repository owners and `systematic-debugging` by 221, and the head of that distribution is made of "generic, task-shaped names for common jobs" ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)). Those are the names a user installs a plugin to get.

Generate any duplicate manifests rather than hand-maintaining them. Of a 3,998-bundle sample of multi-manifest bundles, 95.6% held copies that were not semantically identical and 7.3% disagreed about their own name ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)).

## Why it works

The manifest carries identity and provenance only, and "says nothing about what the plugin does" ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)). A client never asks it what the bundle contains. It walks `skills/*/SKILL.md` and reads `mcp.json`. The literal directory name is therefore the only handle a host has on a capability, and the specification supplies neither a qualified form nor a tiebreak, so each host invents its own. Claude Code namespaces every plugin skill by plugin name "to prevent conflicts when multiple plugins have skills with the same name" ([Claude Code plugin docs](https://code.claude.com/docs/en/plugins)). VS Code drops the qualification and deduplicates by bare name, so one plugin's skill disappears from model context ([microsoft/vscode#334438](https://github.com/microsoft/vscode/issues/334438)). Prefixing works because it makes the name unique before any host-specific rule runs.

## When this backfires

- Your host already namespaces by force. Claude Code prefixes plugin skills as `/plugin-name:skill-name`, so an author-side prefix ships `/my-plugin:my-plugin-code-review` and buys nothing ([Claude Code plugin docs](https://code.claude.com/docs/en/plugins)).
- One owner publishes the whole set. A name repeated across bundles inside a single organization is duplication, not a conflict a user can hit, and the census counts it separately for that reason ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)).
- The collision rate may be inflated. One critique argues the figure reflects forks and copies of a handful of starter templates, which "trivially collide on every capability name they export" ([research-issues#1675](https://github.com/jjakimoto/research-issues/issues/1675)). Filtering by owner does not remove a widely forked template.
- The repair may belong upstream. VS Code's shadowing is filed as a bug, so a client-side fix would repair every installed plugin at once rather than only the prefixed ones.
- Your plugin's value is hooks, commands, or sub-agents. Version 1.0.0 covers skills and MCP servers only, and other component types "do not affect conformance" ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)), so the work returns a manifest and little else. See [Agent Plugins: Portable Packaging With Client-Defined Trust](../../standards/agent-plugins-standard.md).
- The contract is still moving. A 1.1.0 working draft, a registry index, and a dependency field are all in progress ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)), so the fatal-`$schema` rule and the closed field list describe v1.0.0 rather than a settled answer.

## Example

Two independently published plugins each ship the same skill directory:

```text
plugin-a/skills/troubleshooting/SKILL.md
plugin-b/skills/troubleshooting/SKILL.md
```

| Host behavior | Result |
|---|---|
| Namespaces by plugin | Both reachable, as `/plugin-a:troubleshooting` and `/plugin-b:troubleshooting` ([Claude Code plugin docs](https://code.claude.com/docs/en/plugins)) |
| Deduplicates by bare name | One skill is dropped from model context ([microsoft/vscode#334438](https://github.com/microsoft/vscode/issues/334438)) |

Renaming the directories to `plugin-a-troubleshooting` and `plugin-b-troubleshooting` removes the second row, at the cost of a longer name on the host that would have namespaced anyway.

## Key Takeaways

- A conformance check reads one plugin. Every collision failure needs a second one installed, so a green validator says nothing about the configuration users actually run.
- `$schema` at the bundle root is the one fatal omission, and the part of portability an author fully controls. Adding it alone lifts the load rate to 96.6% ([AgentPluginZoo census](https://arxiv.org/abs/2609.23809v1)).
- A top-level field the closed schema does not name still loads, with the host discarding what you wrote. 40.2% of bundles would load with a field discarded; 1.9% of manifests use the `extensions` object that would have held it.
- Prefix exported capability names when strangers will co-install your bundle across more than one client. Skip it for a single-owner fleet or a host that namespaces by force.
- Duplicate manifests drift. 95.6% of sampled multi-manifest bundles already disagree with themselves, so generate them from one source or ship one.

## Related

- [Agent Plugins: Portable Packaging With Client-Defined Trust](../../standards/agent-plugins-standard.md) — what v1.0.0 fixes and what it hands to each client; this page starts where that one stops.
- [Agent Extension Conflicts: When Installed Skills and MCP Servers Fight Each Other](../anti-patterns/agent-extension-conflicts.md) — the runtime half of co-installation, where extensions compete for context budget and routing rather than for a name.
- [Plugin Dependency Declaration and Disable-Chain Hints](../../standards/plugin-dependency-declaration.md) — one vendor's answer to the relation between plugins that v1.0.0 leaves undefined.
- [Pre-Install Plugin Transparency: Capability Inventory and Cost Projection](../../standards/pre-install-plugin-transparency.md) — showing a user what a bundle exports before it is installed, which a declared capability surface would make cheap.
- [Scoped MCP Server Discovery: Most-Specific-Wins Resolution](../../tool-engineering/scoped-mcp-server-discovery.md) — a worked precedence rule at the configuration layer, against the one the plugin specification declines to write.
