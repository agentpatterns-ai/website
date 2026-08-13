---
title: "Per-Surface Verification of Agent Plugin Packages"
description: "An Agent Plugins package is portable at skills/ and mcp.json and nowhere else, so enablement, install trust, and namespaced components must be verified in each client separately."
tags:
  - tool-engineering
  - copilot
term: "Per-Surface Plugin Verification"
aliases:
  - per-surface plugin testing
  - cross-client plugin verification
last_reviewed: 2026-08-13
maturity: emerging
---

# Per-Surface Verification of Agent Plugin Packages

> An Agent Plugins package travels as far as its skills and its `mcp.json`. Verify every other component in each client separately.

Test a plugin in every client you claim to support, and read a vendor changelog as a claim rather than a result. GitHub shipped Agent Plugins 1.0 support in VS Code, Copilot CLI, and the Copilot app on 2026-08-12 ([GitHub Changelog](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app)). One vendor, one package format, and the documented behavior still differs on enablement, install-time trust, update timing, and which components load at all.

## Where the portable guarantee stops

The guarantee covers two component types. Section 7 of the specification states that "Agent Plugins v1 defines exactly two component types: skills and MCP servers. Other component types are outside the v1 format and do not affect conformance" ([Agent Plugins v1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)). Those two do travel: "Compatible clients can discover the skills and MCP server configuration they support from the same package" ([GitHub Changelog](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app)). Everything else is a per-client question.

That includes the client extension namespace the migration guidance recommends. The changelog tells maintainers to "Move Copilot-specific files into the `com.github.copilot/` directory, which other clients ignore," and then says: "Custom agents, commands, rules, and hooks load from there across VS Code, Copilot CLI, and the Copilot app." The VS Code documentation states the opposite: "VS Code currently ignores client extension data and directories in Agent Plugins 1.0 packages" ([VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins)).

## What differs across the three clients

| Question | VS Code | Copilot CLI | Copilot app |
|---|---|---|---|
| Feature enablement | `chat.plugins.enabled` must be on; troubleshooting opens with "Confirm that agent plugins are enabled" | No enablement setting documented | No enablement setting documented |
| Install surface | Extensions view, Agent Customizations editor, or a Git URL | `copilot plugin install` | App settings |
| Install-time trust | "The first time you install a plugin from a new marketplace, VS Code shows a trust prompt" | No approval step documented | No approval step documented |
| Effect of declaring `$schema` | Switches the package to Agent Plugins semantics | Opts in "additively on top of standard plugin loading" | Not documented |
| Namespaced components | Ignored | Not documented | Not documented |

Table sources: [VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins), [Finding and installing plugins for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing), [GitHub Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [Customizing the GitHub Copilot app](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app).

Update timing diverges too, so reviewed code does not stay reviewed on every surface. The CLI reference records that "First-party plugins—those installed from the built-in `copilot-plugins` and `awesome-copilot` marketplaces—automatically update at the start of each session in a trusted working directory," disabled with `autoUpdate` or `COPILOT_AUTO_UPDATE=false`. VS Code holds the opposite line for external sources: "Plugins sourced from npm or PyPI never update automatically."

## Why it works

Portability and divergence come from the same clause. The specification buys forward compatibility by making clients drop what they have not implemented: "Clients MUST ignore component types they do not support" (§7), and "A client MUST ignore manifest entries for namespaces it does not implement without validating the contents of their values" (§8.1). Section 8 adds that "Agent Plugins assigns no portable discovery, validation, loading, or failure semantics to client extension data or files." The specification gives the reason it stopped at two types: commands, hooks, agents, rules, and LSP servers "remain too client-specific for a stable portable contract and are outside the v1 format until their formats converge" ([Agent Plugins v1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)). That same ignore rule permits one vendor's editor to skip that vendor's own namespace and stay conformant. A vendor shipping three clients gets no exemption, because the standard assigns nothing portable to the layer where clients differ.

## When this backfires

- Your plugin's value sits in hooks, custom agents, or slash commands, and you follow the migration steps. Adding `$schema` puts VS Code into Agent Plugins semantics, and VS Code ignores namespace directories in such a package, so the migration removes those components in VS Code.
- You verify on Copilot CLI and generalize. The CLI loads spec components additively on top of its standard loading, so a package carrying both layouts works there while losing half its surface elsewhere.
- You rely on install-time review as the control. The CLI auto-updates first-party plugins at session start, so reviewed code can be replaced without a second prompt.
- You are an administrator assuming one policy file covers everyone. GitHub documents `enabledPlugins`, `extraKnownMarketplaces`, and `strictKnownMarketplaces` in a per-client support matrix ([enterprise managed settings reference](https://docs.github.com/en/copilot/reference/enterprise-managed-settings-reference)), and warns that "Users must upgrade to a supported client version for these standards to be applied" ([enterprise plugin standards](https://docs.github.com/en/copilot/concepts/agents/about-enterprise-plugin-standards)).
- Your team standardizes on one client. There is no fragmentation to collapse, and the native format is simpler than the portable one plus a namespace directory that client may ignore.

## Example

A testing plugin ships one skill, one MCP server, and a set of hooks. Following the changelog's migration list produces this layout:

```text
testing-plugin/
├── plugin.json              # $schema declares Agent Plugins 1.0
├── skills/
│   └── test-runner/
│       └── SKILL.md         # portable
├── mcp.json                 # portable
└── com.github.copilot/
    └── hooks.json           # moved here per the migration guidance
```

In VS Code the first three entries load and the fourth does not, because VS Code "currently ignores these namespaces and loads only the portable skills and MCP server configuration" ([VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins)). The same page's hook-discovery table lists file locations only for the Claude format (`hooks/hooks.json`) and the Copilot format (`hooks.json` at the plugin root), under the note that "Hooks are client-specific and are not a portable Agent Plugins 1.0 component type." No Agent Plugins 1.0 row exists. The `com.github.copilot/` directory is named in the changelog and in none of the client reference or how-to pages cited here.

## Key Takeaways

- Claim cross-surface support only for `skills/` and `mcp.json`; scope every other claim to a client you installed and exercised.
- Declaring `$schema` is not a neutral metadata edit. It is additive in Copilot CLI and a semantics switch in VS Code ([CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins)).
- Before moving components into a client namespace, confirm the target client documents reading that namespace. VS Code documents ignoring it.
- Install-time review is not equivalent across surfaces. Only VS Code documents a marketplace trust prompt, and the CLI auto-updates first-party plugins at session start.
- Enterprise plugin policy is keyed per client and per client version, so a supported-in-principle key can be inactive for part of your fleet.

## Related

- [Agent Plugins: Portable Packaging With Client-Defined Trust](../standards/agent-plugins-standard.md) — the specification this page tests against one vendor's three clients
- [Plugin and Extension Packaging: Distributing Agent Capabilities](../standards/plugin-packaging.md) — the bundle model underneath the portable layout
- [Cross-IDE Plugin Discovery: One Install Surface, Many Consuming Agents](../standards/cross-ide-plugin-discovery.md) — the shared install path, where this page covers divergent client behavior instead
- [Pre-Install Plugin Transparency: Capability Inventory and Cost Projection](../standards/pre-install-plugin-transparency.md) — the disclosure layer each client defines for itself
- [Proprietary-to-Open-Standard Tool Migration (Copilot Extensions to MCP)](copilot-extensions-to-mcp-migration.md) — the earlier GitHub migration with the same verify-per-surface cost
