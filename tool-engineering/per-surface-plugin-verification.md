---
title: "Per-Surface Verification of Agent Plugin Packages"
description: "Agent Plugins 1.0 standardizes skills and MCP configuration. Verify client-specific components, install trust, and update behavior in each client."
tags:
  - tool-engineering
  - copilot
  - plugins
term: "Per-Surface Plugin Verification"
aliases:
  - per-surface plugin testing
  - cross-client plugin verification
last_reviewed: 2026-08-13
maturity: emerging
---

# Per-Surface Verification of Agent Plugin Packages

> Agent Plugins 1.0 standardizes skills and MCP configuration; verify client-specific components and installation behavior in each client separately.

Test a plugin in every client you claim to support, and read a vendor changelog as a claim rather than a result. GitHub shipped Agent Plugins 1.0 support in VS Code, Copilot CLI, and the Copilot app on 2026-08-12 ([GitHub Changelog](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app)). One vendor, one package format, and the documented behavior still differs on enablement, install-time trust, update timing, and which components load at all.

## Where the portable guarantee stops

Agent Plugins 1.0 covers skills and MCP servers. Other component types do not affect v1 conformance ([Agent Plugins v1.0.0, §7](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)). This does not guarantee that every client supports every packaged capability.

GitHub's changelog places Copilot-specific agents, commands, rules, and hooks under `com.github.copilot/` across the three Copilot clients. The current [VS Code authoring reference](https://code.visualstudio.com/docs/agents/reference/agent-plugin-reference) confirms that VS Code reads this namespace and ignores other clients' namespaces. The [CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference) also documents its namespaced component locations. Namespace support is a client feature, not part of the portable contract.

## What differs across the three clients

| Question | VS Code | Copilot CLI | Copilot app |
|---|---|---|---|
| Feature enablement | `chat.plugins.enabled` must be on | No enablement setting documented | No enablement setting documented |
| Install surface | Agent Customizations editor, or a Git URL | `copilot plugin install` | Customize in the sidebar, then Browse and Install |
| Install-time trust | Trust prompt for a new marketplace | No approval step documented | No approval step documented |
| Effect of declaring `$schema` | Switches the package to Agent Plugins semantics | Recognized schema opts into Agent Plugins semantics | Not documented |
| Namespaced components | Reads `com.github.copilot` | Reads `com.github.copilot` | Changelog states support for Copilot agents, commands, rules, and hooks |

Table sources: [VS Code authoring reference](https://code.visualstudio.com/docs/agents/reference/agent-plugin-reference), [GitHub Changelog](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app), [VS Code](https://code.visualstudio.com/docs/agent-customization/agent-plugins), [Finding and installing plugins for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing), [GitHub Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [Customizing the GitHub Copilot app](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app).

Update behavior also needs verification. Plugins from the built-in `awesome-copilot` marketplace update at session start in a trusted working directory. Disable this with `autoUpdate: false` or `COPILOT_AUTO_UPDATE=false`. The CLI reference now lists `copilot-plugins` as non-default; fresh installs must register it manually ([CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)). VS Code supports automatic plugin updates, but npm and PyPI plugins require manual updates and confirmation ([VS Code](https://code.visualstudio.com/docs/agent-customization/agent-plugins)).

## Why it works

The specification requires clients to ignore unsupported component types and unimplemented namespaces. It assigns no portable loading or failure behavior to client extension files ([Agent Plugins v1.0.0, §§7–8](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)). Thus, portable skills and MCP configuration can coexist with extensions that only some clients implement. Test those extensions against each client's documented paths and behavior.

## When this backfires

- Your plugin depends on hooks or custom agents. Check the target client's namespace support and file paths before migration; portable conformance alone does not cover these components.
- You verify on Copilot CLI and generalize. Both CLI and VS Code recognize Agent Plugins manifests, but this does not establish identical loading across all clients.
- You rely on install-time review as the control. The CLI updates `awesome-copilot` plugins at session start in trusted directories, so the installed version can change after review.
- You are an administrator assuming one policy file covers everyone. GitHub documents `enabledPlugins`, `extraKnownMarketplaces`, and `strictKnownMarketplaces` in a per-client support matrix ([enterprise managed settings reference](https://docs.github.com/en/copilot/reference/enterprise-managed-settings-reference)), and requires supported client versions for enforcement ([enterprise plugin standards](https://docs.github.com/en/copilot/concepts/agents/about-enterprise-plugin-standards)).
- Your team standardizes on one client. There is no fragmentation to collapse, and the native format is simpler than the portable one plus a namespace directory that client may ignore.

## Example

The [VS Code authoring reference](https://code.visualstudio.com/docs/agents/reference/agent-plugin-reference) includes a testing-plugin layout. Its relevant paths are:

```text
my-testing-plugin/
├── plugin.json              # $schema declares Agent Plugins 1.0
├── skills/
│   └── test-runner/
│       └── SKILL.md         # portable
├── mcp.json                 # portable
└── com.github.copilot/
    └── hooks/
        └── hooks.json       # Copilot-specific hooks
```

VS Code documents hooks at `com.github.copilot/hooks/hooks.json` in Agent Plugins packages. The CLI reference lists the same path ([VS Code authoring reference](https://code.visualstudio.com/docs/agents/reference/agent-plugin-reference), [CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)). Verify that the intended hook runs in each target client; a documented path is not a test result for your package.

## Key Takeaways

- Claim cross-surface support only for `skills/` and `mcp.json`; scope every other claim to a client you installed and exercised.
- A recognized `$schema` selects Agent Plugins semantics in both CLI and VS Code ([CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [VS Code authoring reference](https://code.visualstudio.com/docs/agents/reference/agent-plugin-reference)).
- Before moving components into a client namespace, confirm the target client documents reading that namespace. VS Code and CLI document support for `com.github.copilot`.
- Install-time review is not equivalent across surfaces. VS Code documents a marketplace trust prompt, and the CLI auto-updates `awesome-copilot` plugins in trusted directories.
- Enterprise plugin policy is keyed per client and per client version, so a supported-in-principle key can be inactive for part of your fleet.

## Related

- [Agent Plugins: Portable Packaging With Client-Defined Trust](../standards/agent-plugins-standard.md) — the specification this page tests against one vendor's three clients
- [Plugin and Extension Packaging: Distributing Agent Capabilities](../standards/plugin-packaging.md) — the bundle model underneath the portable layout
- [Cross-IDE Plugin Discovery: One Install Surface, Many Consuming Agents](../standards/cross-ide-plugin-discovery.md) — the shared install path, where this page covers divergent client behavior instead
- [Pre-Install Plugin Transparency: Capability Inventory and Cost Projection](../standards/pre-install-plugin-transparency.md) — the disclosure layer each client defines for itself
- [Proprietary-to-Open-Standard Tool Migration (Copilot Extensions to MCP)](copilot-extensions-to-mcp-migration.md) — the earlier GitHub migration with the same verify-per-surface cost
- [Policy File Validation: Catching Silent Non-Enforcement](../instructions/policy-file-validation.md) — the other route to an unenforced managed setting, where the file itself is malformed rather than the client unsupported
