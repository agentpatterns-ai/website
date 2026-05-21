---
title: "Enterprise-Managed Plugin Governance for Agent CLIs"
description: "Admin contracts to curate marketplaces, pin versions, force-enable plugins, and gate policy changes — closing the supply-chain leg of the lethal trifecta on the plugin code-load path."
tags:
  - security
  - workflows
  - copilot
  - claude
aliases:
  - enterprise-managed plugin standards
  - managed plugin contract
  - plugin marketplace allowlist
---

# Enterprise-Managed Plugin Governance for Agent CLIs

> Agent CLIs ship plugin contracts that let admins curate marketplaces, pin versions, and force-enable plugins from a managed settings file — closing the supply-chain leg of the lethal trifecta on the code-load path, provided the rollout is staged and the contract's known schema gaps are respected.

The enterprise-managed plugin contract is a small set of admin-only settings that decide which plugin marketplaces a CLI may add, which plugins auto-install per user, which versions are pinned, and what happens to already-installed plugins when policy changes. GitHub Copilot CLI's variant entered public preview on 2026-05-06 ([GitHub Changelog](https://github.blog/changelog/2026-05-06-enterprise-managed-plugins-in-github-copilot-cli-are-now-in-public-preview/)); Claude Code's variant has been live longer; Cursor's enterprise admin surface added MCP and extension allowlists in May 2026. The shape is converging — but the levers differ enough that "managed plugins" means three different things in production today.

## The Four Levers

A managed plugin contract has four parts. Treat the matrix as the scope of what you can actually enforce:

| Lever | What it controls | Why it matters |
|---|---|---|
| **Catalogue allow/block** | Which plugin marketplaces a user may add | Pre-network gate — a blocked source never reaches the cache, never runs a postinstall hook |
| **Plugin enable (auto-install)** | Which plugins land on every machine at sign-in | Removes the "did the developer install the approved plugin?" question; baseline for onboarding |
| **Version pin** | Branch, tag, or commit SHA the plugin resolves to | Forces a hijacked tag to point at old code; the only defence against force-push rug-pulls |
| **Policy-change behaviour** | What happens to an installed plugin when policy tightens | Determines whether revocation is immediate or eventual |

## How the Contracts Compare

### GitHub Copilot CLI

Admins commit `settings.json` to `.github-private/.github/copilot/settings.json` ([Configuring enterprise plugin standards for Copilot CLI](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-agents/configure-enterprise-plugin-standards)). The preview schema exposes two keys: `extraKnownMarketplaces` (additional marketplaces, each `{"source": "github", "repo": "OWNER/REPO"}`) and `enabledPlugins` (plugins auto-installed for every user, keyed by `PLUGIN-NAME@MARKETPLACE-NAME`). The CLI reads the file at sign-in via a GitHub API endpoint ([About enterprise-managed plugin standards](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-enterprise-plugin-standards)). There is no allowlist-with-lockdown key and no in-schema version pin in the preview — pinning lives upstream in the plugin manifest.

### Claude Code

The surface is wider and split across two files. `marketplace.json` pins plugin sources with `ref` (branch/tag) plus `sha` (40-character commit) for GitHub, URL, and git-subdir sources ([Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)). `managed-settings.json` carries admin-only policy keys: `strictKnownMarketplaces` (allowlist; `[]` is "full lockdown"; supports `hostPattern` regex for self-hosted git), `blockedMarketplaces` (denylist, checked before any download), `enabledPlugins` (force-installed list), `strictPluginOnlyCustomization` (blocks skills, agents, hooks, MCP servers from non-plugin sources), and `allowManagedHooksOnly`.

The managed file lives at `/etc/claude-code/managed-settings.json` on Linux, `/Library/Application Support/ClaudeCode/managed-settings.json` on macOS, and `C:\Program Files\ClaudeCode\managed-settings.json` on Windows; user and project settings cannot override ([Claude Code settings](https://code.claude.com/docs/en/settings)). Restrictions are checked "on marketplace add and on plugin install, update, refresh, and auto-update" — pre-existing installs are not retroactively uninstalled; they fail at the next refresh ([Plugin marketplaces — Managed marketplace restrictions](https://code.claude.com/docs/en/plugin-marketplaces)).

### VS Code and Cursor

VS Code added `extensions.allowed` with `AllowedExtensions` Group Policy enforcement from VS Code 1.96 ([Manage extensions in enterprise environments](https://code.visualstudio.com/docs/enterprise/extensions)); a malformed policy value is dropped silently. Cursor's May 2026 enterprise release added model/provider allowlists, MCP server allowlists with a new-tool onboarding flow, and hook-based command and secret enforcement deployable via MDM or Group Policy ([Cursor's New Enterprise Admin Controls](https://pondero.ai/coding/guides/cursor-enterprise-admin-controls-may-2026/)). Cursor does not fully honour VS Code's `extensions.allowed` today — the schema is portable, the enforcement is not.

## Why It Works

The contract works because it relocates the trust decision from the developer machine to a version-controlled config file in a repository with org-level access controls, and gates the policy check before any network or filesystem operation. Claude Code's docs are explicit: restrictions run "before any network or filesystem operation … on marketplace add and on plugin install, update, refresh, and auto-update" ([Plugin marketplaces docs](https://code.claude.com/docs/en/plugin-marketplaces)). That is the structural difference from runtime-only controls such as `PreToolUse` hooks — a blocked marketplace source never reaches the plugin cache, so postinstall scripts, `mcpServers` declarations bundled with the plugin, and `${CLAUDE_PLUGIN_ROOT}`-rooted hook commands never get a chance to run with the user's tokens. Pinning by content hash (`ref` plus `sha`) closes the variant where attackers force-push to a previously trusted tag.

In threat-model terms, the contract removes the egress leg of the [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) on the plugin code-load path: untrusted content (a marketplace under attacker control) cannot reach the agent's principal at all, so the trifecta doesn't form. The May 2026 Nx Console VS Code extension breach — which exfiltrated approximately 3,800 internal GitHub repositories after an employee installed a malicious extension ([VentureBeat, May 2026](https://venturebeat.com/security/github-confirms-3800-repos-stolen-poisoned-vs-code-extension-supply-chain-worm-microsoft-python-sdk)) — is the exact attack class this contract is sized for, alongside the ongoing GlassWorm sleeper-extension campaign ([Dark Reading](https://www.darkreading.com/application-security/fresh-glassworm-vs-code-extensions-supply-chain)).

## When This Backfires

The contract is real but not symmetric, and several failure modes follow from the schema and check semantics:

- **Lockdown bricks the default catalogue**. On Claude Code, `strictKnownMarketplaces: []` blocks the official Anthropic marketplace alongside everything else ([Claude Code issue #34873](https://github.com/anthropics/claude-code/issues/34873)). Small teams without an internal marketplace are worse off than before.
- **Pre-existing installs survive policy until next refresh**. Both Copilot's preview docs and Claude Code's restriction semantics gate at marketplace-add and plugin install/update/refresh, not retroactively ([Plugin marketplaces docs](https://code.claude.com/docs/en/plugin-marketplaces)). A revoked plugin keeps running on cached code until the user next triggers a refresh — the "freeze a malicious plugin now" use case has a window measured in days, not minutes.
- **Cross-tool schema parity is incomplete**. Copilot's preview has no allowlist-with-lockdown analogue to `strictKnownMarketplaces` and no in-schema version pin. A cross-tool org cannot enforce the same posture symmetrically across Copilot CLI, Claude Code, and Cursor today.
- **The managed contract has historically been silently no-op'd**. Claude Code shipped versions where `extraKnownMarketplaces` in `managed-settings.json` was ignored ([Claude Code issue #16870](https://github.com/anthropics/claude-code/issues/16870)). Treat the contract as enforce-and-verify, paired with [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md), not enforce-and-assume.
- **`enabledPlugins` does not retract user-added MCP servers or hooks**. Without `strictPluginOnlyCustomization` set, MCP servers and hooks declared in `.claude/settings.json` keep loading outside the plugin contract — the contract leaves the broader customisation surface unmanaged.

The pattern is justified when the org runs multi-vendor agent CLIs with broad tool surfaces and a heterogeneous engineer population. For small teams that author all their plugins internally and never load third-party marketplaces, a `CODEOWNERS`-gated single internal marketplace plus PR review may cover the same threat with less brittleness.

## Example

A staged rollout for Claude Code that avoids bricking sessions and survives the "pre-existing install" gap:

**Stage 1 — register the internal marketplace alongside existing user marketplaces (no lockdown):**

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

**Stage 2 — narrow the catalogue with `hostPattern`; pin every entry in the marketplace by `sha`:**

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

**Stage 3 — close the user-customisation surface so the plugin contract is the only entry point:**

```json
// /etc/claude-code/managed-settings.json
{
  "strictPluginOnlyCustomization": ["skills", "hooks", "mcpServers"],
  "allowManagedHooksOnly": true
}
```

The first stage adds a managed marketplace without breaking working sessions. The second tightens the allowlist, blocks the upstream marketplace explicitly (because empty-array lockdown also blocks it via [issue #34873](https://github.com/anthropics/claude-code/issues/34873)), and pins every plugin by content hash so a forced tag move points at the old commit. The third closes side channels — MCP servers and hooks declared outside the plugin contract — only after the catalogue is stable, so engineers don't lose working configs the day policy ships.

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
