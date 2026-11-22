---
title: "Plugin-Only Customization Sources for GitHub Copilot"
term: "Plugin-Only Customization Sources"
description: "Copilot's strictPluginOnlyCustomization makes selected customization categories come from plugins or managed settings; pair it with a marketplace allowlist."
tags:
  - security
  - instructions
  - copilot
aliases:
  - plugin-only customization policy
  - strictPluginOnlyCustomization setting
last_reviewed: 2026-11-21
maturity: emerging
---

# Plugin-Only Customization Sources for GitHub Copilot

> Copilot's plugin-only setting blocks standalone customizations in the categories an administrator selects, so those come only from plugins or managed settings.

Plugin-only customization is an enterprise-managed Copilot setting that controls where a customization may come from. GitHub added it on 16 November 2026: administrators "can now require selected GitHub Copilot customizations to come from plugins or managed settings, rather than standalone user or project configuration" ([GitHub Changelog](https://github.blog/changelog/2026-11-16-control-where-github-copilot-customizations-come-from)). Three conditions decide whether it limits customizations to sources the administrator controls:

- A marketplace allowlist sits beside it. "Plugin-only does not mean enterprise-managed plugins only, and it isn't a marketplace allowlist. Pair it with `strictKnownMarketplaces` to restrict eligible marketplace sources" ([Changelog](https://github.blog/changelog/2026-11-16-control-where-github-copilot-customizations-come-from)).
- The customization falls in a selected category. The five categories do not include instruction files ([reference](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/enterprise-administrators/enterprise-managed-settings#strictpluginonlycustomization)).
- The client enforces it. In VS Code, the setting applies to Copilot sessions that use Agent Host ([reference](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/enterprise-administrators/enterprise-managed-settings#strictpluginonlycustomization)).

## What the setting covers

`strictPluginOnlyCustomization` accepts `true` for all five categories, `false` or omitted for no restriction from this key, or an array of category names ([Enterprise managed settings reference](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/enterprise-administrators/enterprise-managed-settings#strictpluginonlycustomization)):

| Category | Customizations |
|---|---|
| `skills` | Agent skills |
| `agents` | Custom agents |
| `hooks` | Hooks |
| `mcp` | MCP servers |
| `extensions` | Executable Copilot extensions, including canvas providers; not VS Code Marketplace extensions |

The reference says the selected categories "must come from eligible plugins or managed settings instead of standalone user, workspace, or project configuration," and that the setting "controls their sources without disabling the capabilities entirely." The table has no category for custom instruction files, so this key does not name a repository's instruction file.

## Where an administrator sets it

The key goes in `managed-settings.json`. In a server-managed deployment, that file is `copilot/managed-settings.json` in the enterprise's `.github-private` repository. Other routes include MDM and local file delivery ([Getting started with enterprise-managed settings](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/get-started)). The changelog says administrators configure it on GitHub Enterprise Cloud for members "with Copilot Business or Copilot Enterprise licenses issued by the enterprise or one of its organizations" ([Changelog](https://github.blog/changelog/2026-11-16-control-where-github-copilot-customizations-come-from)).

Restrictions combine across layers. "User settings and repository settings cannot relax that value," and a category restricted by any server-managed, device-managed, or policy-helper source "stays restricted, even if another source sets the key to `false` or omits that category" ([reference](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/enterprise-administrators/enterprise-managed-settings#strictpluginonlycustomization)). In a server-managed deployment, an enterprise can wrap its default in `overridable` so that an applicable enterprise-team, organization, or organization-team setting may replace it. "None of these layers can relax an unwrapped enterprise restriction" ([reference](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/enterprise-administrators/enterprise-managed-settings#strictpluginonlycustomization)).

## What happens to a blocked customization

The setting blocks a standalone customization in a restricted category, while "Eligible plugins and managed settings remain allowed, subject to your other policies" ([Changelog](https://github.blog/changelog/2026-11-16-control-where-github-copilot-customizations-come-from)). GitHub tells administrators to confirm this in each client: "Confirm that an allowed plugin's customizations load and that equivalent standalone MCP servers and executable extensions do not" ([Managing plugin marketplaces and plugins](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/manage-plugin-marketplaces-and-plugins#restrict-standalone-customizations)). The reference's client-support table, read on 2026-11-21, has a row for `strictKnownMarketplaces` and none for `strictPluginOnlyCustomization`.

## Why it works

The setting removes standalone user, workspace, and project sources for the selected categories and leaves eligible plugins and managed settings. Combined with marketplace restrictions, the changelog says, this "lets you distribute approved MCP tools and canvases through a shared plugin library without disabling those capabilities entirely" ([Changelog](https://github.blog/changelog/2026-11-16-control-where-github-copilot-customizations-come-from)). "Allowing a customization's source does not grant it additional access," and MCP allowlists, permissions, and sandbox restrictions still apply ([reference](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/enterprise-administrators/enterprise-managed-settings#strictpluginonlycustomization)).

## When this backfires

- No marketplace allowlist. "Plugins can remain eligible even if the enterprise does not require them through `enabledPlugins`" ([reference](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/enterprise-administrators/enterprise-managed-settings#strictpluginonlycustomization)). The changelog's answer is to pair the key with `strictKnownMarketplaces`.
- VS Code sessions outside Agent Host. "Do not rely on this setting to enforce the same restrictions in other session types" ([reference](https://docs.github.com/en/enterprise-cloud@latest/copilot/reference/enterprise-administrators/enterprise-managed-settings#strictpluginonlycustomization)).
- Treating approval as vetting. "An approved marketplace is a distribution control, not a guarantee that its plugins are safe" ([how-to](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/manage-plugin-marketplaces-and-plugins#restrict-standalone-customizations)). In a public skills marketplace, Orca Security submitted a benign skill that "passed the platform's security scan," then added malicious instructions to its repository right after the scan ([Orca Security](https://orca.security/resources/blog/ai-agent-skill-supply-chain-security/)).
- Expecting a marketplace-only MCP rule. "Plugin-only restrictions also permit managed MCP sources and do not exclude built-in default servers" ([how-to](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/manage-plugin-marketplaces-and-plugins#move-mcp-distribution-from-a-registry-to-a-marketplace)).
- Teams that build MCP servers. Restricting `mcp` blocks their standalone configurations. A team override fixes that, but "The team value replaces the entire overridable default," so a category left out of the team value loses the enterprise default's restriction for that team. Another matching team or a device-managed setting that restricts the category still applies ([team overrides](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/override-settings-for-teams#allow-an-mcp-development-team-to-use-standalone-servers)).

## Example

GitHub's how-to restricts standalone MCP servers and executable extensions while it distributes an approved library. Trimmed to the two source keys:

```json
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "ORG/REPOSITORY" }
  ],
  "strictPluginOnlyCustomization": ["mcp", "extensions"]
}
```

The full example also adds the marketplace with `extraKnownMarketplaces` and requires or blocks plugins with `enabledPlugins`. Skills, custom agents, and hooks stay unrestricted by this key. To exempt an MCP-development team, the enterprise wraps the value as `{"overridable": ["mcp", "extensions"]}` and maps the team to a file that sets `["extensions"]` ([team overrides](https://docs.github.com/en/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/use-managed-settings/override-settings-for-teams#allow-an-mcp-development-team-to-use-standalone-servers)).

## Key Takeaways

- Set `strictKnownMarketplaces` in the same change. On its own, plugin-only accepts plugins from any eligible marketplace.
- The key names five categories. Instruction files are outside its table and need their own review path.
- Test each client after deployment. In VS Code it applies to Agent Host sessions, and the client-support table has no row for the key.
- Keep reviewing plugin code. A restricted source still serves whatever its plugins contain.

## Related

- [Enterprise-Managed Plugin Governance for Agent CLIs](enterprise-managed-plugin-governance.md) — the marketplace, enable, and pin levers this setting pairs with.
- [Team-Scoped Agent Policy Delegation](team-scoped-policy-delegation.md) — how the `overridable` wrapper hands a key to enterprise teams.
- [Centrally Provisioned MCP Servers: Remote Transports Only](centrally-provisioned-mcp-servers.md) — another way to control which MCP servers developers run.
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — the threat a restricted source does not remove.
- [Per-Surface Verification of Agent Plugin Packages](../tool-engineering/per-surface-plugin-verification.md) — why a plugin rule needs a check in each client.
