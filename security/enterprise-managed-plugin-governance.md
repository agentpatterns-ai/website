---
title: "Enterprise-Managed Plugin Governance for Agent CLIs"
term: "Enterprise-Managed Plugin Governance"
description: "Admin contracts to curate marketplaces, pin versions, force-enable plugins, and gate policy changes — closing the supply-chain leg of the lethal trifecta on the plugin code-load path."
tags:
  - security
  - workflows
  - copilot
  - claude
  - cursor
tool_scope_exempt: true
aliases:
  - enterprise-managed plugin standards
  - managed plugin contract
  - plugin marketplace allowlist
last_reviewed: 2026-06-03
maturity: established
---

# Enterprise-Managed Plugin Governance for Agent CLIs

> A managed plugin contract is an admin-only settings file that curates marketplaces, pins versions, and force-enables plugins — gating the code-load path before any download.

It is a small set of admin-only settings that decide which marketplaces a CLI may add, which plugins auto-install, which versions are pinned, and what happens to installed plugins when policy changes. GitHub Copilot CLI's variant entered public preview on 2026-05-06 ([GitHub Changelog](https://github.blog/changelog/2026-05-06-enterprise-managed-plugins-in-github-copilot-cli-are-now-in-public-preview/)); Claude Code's has been live longer; Cursor's enterprise surface added MCP and extension allowlists in May 2026. The shapes are converging, but the levers differ enough that "managed plugins" means three different things in production today.

## The four levers

A managed plugin contract has four parts. The matrix below is the enforcement scope:

| Lever | What it controls | Why it matters |
|---|---|---|
| Catalogue allow/block | Which plugin marketplaces a user may add | Pre-network gate — a blocked source never reaches the cache or postinstall hook |
| Plugin enable | Which plugins auto-install at sign-in | Removes the "did the dev install the approved plugin?" question |
| Version pin | Branch, tag, or commit SHA the plugin resolves to | Defence against force-push tag rug-pulls |
| Policy-change behaviour | What happens to an installed plugin when policy tightens | Determines whether revocation is immediate or eventual |

## How the contracts compare

### GitHub Copilot CLI

Admins commit `settings.json` to `.github-private/.github/copilot/settings.json` ([Configuring enterprise plugin standards for Copilot CLI](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-agents/configure-enterprise-plugin-standards)). The preview schema has two keys: `extraKnownMarketplaces` (additional marketplaces, each `{"source": "github", "repo": "OWNER/REPO"}`) and `enabledPlugins` (force-installed plugins, keyed by `PLUGIN-NAME@MARKETPLACE-NAME`). The CLI reads the file at sign-in via a GitHub API endpoint ([About enterprise-managed plugin standards](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-enterprise-plugin-standards)). No allowlist-with-lockdown key and no in-schema version pin yet — pinning lives upstream in the plugin manifest.

### Claude Code

The surface is wider and split across two files. `marketplace.json` pins plugin sources with `ref` (branch/tag) plus `sha` (40-character commit) for GitHub, URL, and git-subdir sources ([Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)). `managed-settings.json` carries admin-only policy keys: `strictKnownMarketplaces` (allowlist; `[]` is "full lockdown"; supports `hostPattern` regex), `blockedMarketplaces` (denylist, checked before any download), `enabledPlugins`, `strictPluginOnlyCustomization` (blocks skills, agents, hooks, MCP servers from non-plugin sources), and `allowManagedHooksOnly`.

The managed file lives at `/etc/claude-code/managed-settings.json` (Linux), `/Library/Application Support/ClaudeCode/managed-settings.json` (macOS), and `C:\Program Files\ClaudeCode\managed-settings.json` (Windows); user and project settings cannot override ([Claude Code settings](https://code.claude.com/docs/en/settings)). Restrictions are checked "on marketplace add and on plugin install, update, refresh, and auto-update" — pre-existing installs fail at the next refresh, not retroactively ([Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)).

### VS Code and Cursor

VS Code added `extensions.allowed` with `AllowedExtensions` Group Policy enforcement from VS Code 1.96 ([Manage extensions in enterprise environments](https://code.visualstudio.com/docs/enterprise/extensions)); malformed policy is silently dropped. Cursor's May 2026 enterprise release added model/provider allowlists, MCP server allowlists with a new-tool onboarding flow, and hook-based command/secret enforcement deployable via MDM or Group Policy ([Cursor's New Enterprise Admin Controls](https://pondero.ai/coding/guides/cursor-enterprise-admin-controls-may-2026/)). Cursor does not fully honor VS Code's `extensions.allowed` — the schema is portable, the enforcement is not.

## Why it works

The contract moves the trust decision off the developer machine. It lives in a version-controlled config in a repo with org-level access controls. The check runs "before any network or filesystem operation … on marketplace add and on plugin install, update, refresh, and auto-update" ([Plugin marketplaces docs](https://code.claude.com/docs/en/plugin-marketplaces)). That is the structural difference from runtime-only controls like `PreToolUse` hooks: a blocked marketplace never reaches the plugin cache, so postinstall scripts, bundled `mcpServers` declarations, and `${CLAUDE_PLUGIN_ROOT}`-rooted hook commands never run with the user's tokens. Pinning by content hash (`ref` plus `sha`) closes force-push tag-move attacks.

In threat-model terms, the contract removes the egress leg of the [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) on the plugin code-load path: untrusted content cannot reach the agent's principal, so the trifecta doesn't form. The May 2026 Nx Console breach — which exfiltrated roughly 3,800 internal GitHub repositories after an employee installed a malicious extension ([VentureBeat](https://venturebeat.com/security/github-confirms-3800-repos-stolen-poisoned-vs-code-extension-supply-chain-worm-microsoft-python-sdk)) — is the attack class this contract is sized for, alongside the GlassWorm sleeper-extension campaign ([Dark Reading](https://www.darkreading.com/application-security/fresh-glassworm-vs-code-extensions-supply-chain)).

## When this backfires

The contract is real but not symmetric. Several failure modes follow from schema and check semantics:

- Lockdown bricks the default catalog. On Claude Code, `strictKnownMarketplaces: []` blocks the official Anthropic marketplace alongside everything else ([issue #34873](https://github.com/anthropics/claude-code/issues/34873)) — small teams without an internal marketplace end up worse off.
- Pre-existing installs survive until the next refresh. Both Copilot's preview and Claude Code gate at marketplace-add and plugin install/update/refresh, not retroactively ([Plugin marketplaces docs](https://code.claude.com/docs/en/plugin-marketplaces)). A revoked plugin keeps running on cached code until refresh — the "freeze now" window is days, not minutes.
- Cross-tool parity is incomplete. Copilot's preview has no allowlist-with-lockdown analogue and no in-schema version pin, so an org cannot enforce the same posture symmetrically across Copilot CLI, Claude Code, and Cursor today.
- The contract has sometimes been silently no-op'd. Claude Code shipped versions where `extraKnownMarketplaces` was ignored ([issue #16870](https://github.com/anthropics/claude-code/issues/16870)). Treat it as enforce-and-verify, paired with [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md).
- `enabledPlugins` does not retract user-added MCP servers or hooks. Without `strictPluginOnlyCustomization` set, servers and hooks declared in `.claude/settings.json` keep loading outside the contract.

The pattern fits orgs running multi-vendor agent CLIs with broad tool surfaces. For small teams authoring all plugins internally, a `CODEOWNERS`-gated single internal marketplace plus PR review may cover the same threat with less brittleness.

## Example

A staged rollout for Claude Code that avoids bricking sessions and survives the "pre-existing install" gap:

Stage 1 — register the internal marketplace alongside existing user marketplaces, with no lockdown:

```json
// /etc/claude-code/managed-settings.json
{
  "extraKnownMarketplaces": {
    "acme-internal": {
      "source": { "source": "github", "repo": "acme-corp/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "acme-baseline@acme-internal": true
  }
}
```

Stage 2 — narrow the catalog with `hostPattern`, then pin every entry in the marketplace by `sha`:

```json
// /etc/claude-code/managed-settings.json
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/claude-plugins" },
    { "source": "hostPattern", "hostPattern": "^github\\.acme-corp\\.com$" }
  ],
  "blockedMarketplaces": [
    { "source": "github", "repo": "anthropics/claude-plugins-official" }
  ]
}
```

```json
// acme-corp/claude-plugins/.claude-plugin/marketplace.json
{
  "name": "acme-internal",
  "owner": { "name": "Platform Security" },
  "plugins": [
    {
      "name": "acme-baseline",
      "source": {
        "source": "github",
        "repo": "acme-corp/baseline-plugin",
        "ref": "v1.4.0",
        "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
      }
    }
  ]
}
```

Stage 3 — close the user-customization surface so the plugin contract is the only entry point:

```json
// /etc/claude-code/managed-settings.json
{
  "strictPluginOnlyCustomization": ["skills", "hooks", "mcpServers"],
  "allowManagedHooksOnly": true
}
```

The first stage adds a managed marketplace without breaking working sessions. The second tightens the allowlist, blocks the upstream marketplace explicitly (because empty-array lockdown also blocks it via [issue #34873](https://github.com/anthropics/claude-code/issues/34873)), and pins every plugin by content hash so a forced tag move points at the old commit. The third closes side channels — MCP servers and hooks declared outside the plugin contract — only after the catalog is stable, so engineers don't lose working configs the day policy ships.

## Key Takeaways

- The managed-plugin contract is four levers — catalogue allow/block, plugin enable, version pin, and policy-change behaviour — not one switch
- Restrictions check before network or filesystem access, so a blocked marketplace never executes a postinstall, hook, or `mcpServers` declaration — the structural advantage over runtime-only controls
- Copilot CLI, Claude Code, and Cursor expose convergent but unequal surfaces today; a single cross-tool policy posture is not yet symmetric
- Pre-existing installs survive policy until the next refresh on every tool — managed plugins are not a "freeze now" lever
- Stage the rollout: register internal marketplace, then tighten allowlist with explicit blocks and pinned `sha`, then close MCP and hook side channels last

## Related

- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md)
- [Tool Signing and Signature Verification](tool-signing-verification.md)
- [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md)
- [Enterprise Agent Hardening](enterprise-agent-hardening.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Org-Membership-Gated Agent Entitlement](org-membership-gated-agent-entitlement.md)
