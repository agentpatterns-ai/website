---
title: "Directory-Aware Plugin Suggestions via `pluginSuggestionMarketplaces`"
description: "A three-lever managed-settings pattern — allowlist suggesting marketplaces, mark plugins `defaultEnabled: false`, declare per-plugin relevance — that keeps the Claude Code `/plugin` Discover tab signal-dense as an internal marketplace grows."
tags:
  - standards
  - security
  - claude
aliases:
  - pluginSuggestionMarketplaces
  - Plugin Suggestion Marketplaces
last_reviewed: 2026-06-03
maturity: emerging
---

# Directory-Aware Plugin Suggestions via `pluginSuggestionMarketplaces`

> Three managed-settings levers — `pluginSuggestionMarketplaces` allowlist, marketplace `relevance` declaration, `defaultEnabled: false` — pin only directory-relevant plugins in the `/plugin` Discover tab.

The pattern earns its place once an internal marketplace exceeds roughly ten plugins. Below that, the Discover tab is short enough to scan and a relevance pin adds an unobservable ranking step without reducing real noise. Above it, every session pays attention tax to a Discover list of plugins it will never use.

## The Three-Lever Gate

The pattern composes three Claude Code settings that each enforce a different leg of the gate:

1. **`pluginSuggestionMarketplaces`** (managed settings only, v2.1.152) — admin allowlists the marketplace names whose plugins may surface as contextual install suggestions. From [Claude Code settings docs](https://code.claude.com/docs/en/settings): *"Marketplace names whose plugins can appear as contextual install suggestions, in addition to the official marketplace."* A name only takes effect when the marketplace is registered on the machine **and** its registered source is also declared in managed settings — either through `extraKnownMarketplaces` or `strictKnownMarketplaces`. A marketplace registered from a different source under an allowlisted name is silently ignored, closing the obvious name-collision spoof.
2. **Per-plugin `relevance` in `marketplace.json`** (v2.1.154) — the marketplace entry declares directory-matching signals. From the [Claude Code changelog](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md): *"The `/plugin` Discover tab now pins plugins whose relevance signals match the current directory with a 'suggested for this directory' annotation."* The full `relevance` schema is not yet documented publicly; the `anthropics/claude-plugins-official` marketplace catalogue does not yet populate the field. Until the schema lands, treat any plugin-author `relevance` declaration as untrusted input — there is no lint surface to bound how broad an author's match can be.
3. **`defaultEnabled: false`** in `plugin.json` or the marketplace entry (v2.1.154) — the plugin installs disabled and the user opts in. From [plugins reference §Default enablement](https://code.claude.com/docs/en/plugins-reference): *"Set `defaultEnabled: false` in `plugin.json` to ship a plugin that installs disabled. The user turns it on with `claude plugin enable <plugin>` or the `/plugin` interface."* The same field can appear in the marketplace entry, where it takes precedence over `plugin.json`.

Without lever 3, lever 2 is destructive: suggested plugins are already loaded and paying context cost from session start, so "suggestion" silently becomes "always-on tax."

## Why It Works

The mechanism is **strict-deny baseline with explicit grants**: nothing appears unless the marketplace is trusted, the plugin claims directory relevance, and the user opts in. Each lever closes a separate failure mode — `pluginSuggestionMarketplaces` closes the supply-chain leg (no community marketplace nudges an enterprise session), `relevance` closes the noise leg (a 50-plugin internal marketplace surfaces only the ~3 a given directory needs), and `defaultEnabled: false` closes the cost leg (a suggestion is an install/enable prompt, not silent activation). The Discover-tab change inverts the previous default: instead of "everything available, you discover what's relevant" the surface becomes "nothing pins to the top unless three independent admin- and author-set conditions hold" ([Discover plugins docs](https://code.claude.com/docs/en/discover-plugins)).

## When This Backfires

- **Misconfigured `relevance` declarations spam every directory.** A plugin author who writes a signal matching `.git` or `package.json` effectively re-spams every Node project. Until a central lint or admin review of `relevance` exists, an internal marketplace degenerates back to "everything is suggested" the moment one author over-claims.
- **Polyglot monorepos.** A monorepo opened at the root has a Python service, a Go service, and a TypeScript app. Any signal keyed on one language fires (or all fire), defeating the relevance pin. The pattern assumes the working directory reflects the task scope; in a monorepo it does not.
- **Small marketplaces (<10 plugins).** Below this scale the Discover-tab list is already short enough to scan. The relevance pin primes operators to trust an unobservable ranking signal without producing measurable noise reduction.
- **Admin misconfigures `extraKnownMarketplaces` source.** The gating rule *silently* ignores allowlisted names whose registered source does not match the managed-settings declaration ([Claude Code settings docs](https://code.claude.com/docs/en/settings)). Result: admin enables the allowlist, no suggestions appear, admin assumes the feature is broken instead of the configuration. The diagnostic surface is thin.
- **The official marketplace is always implicit.** `pluginSuggestionMarketplaces` *extends* the suggestion pool — it does not replace it. To suppress official-marketplace suggestions, use `strictKnownMarketplaces` to lock down what marketplaces are even known on the machine ([Plugin marketplaces — managed restrictions](https://code.claude.com/docs/en/plugin-marketplaces#managed-marketplace-restrictions)).
- **No published precision/recall data.** At time of writing, no third-party measurement of suggestion quality exists on real repos. The mechanism is plausible; its accuracy in your stack is unverified until you ship and measure.

## Example

A 30-plugin internal marketplace at `acme-corp/plugins`, mostly language- and stack-specific (Terraform formatters, Python type-checkers, Vault clients, internal SDK helpers). The pre-pattern Discover tab shows all 30 every session.

Managed settings (`managed-settings.json`):

```json
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "acme-corp/plugins" }
  ],
  "extraKnownMarketplaces": {
    "acme-corp-plugins": {
      "source": { "source": "github", "repo": "acme-corp/plugins" }
    }
  },
  "pluginSuggestionMarketplaces": ["acme-corp-plugins"]
}
```

A representative marketplace entry (`marketplace.json`), with `defaultEnabled: false` so install does not silently activate:

```json
{
  "name": "terraform-policy-pack",
  "source": { "source": "github", "repo": "acme-corp/tf-policy-pack" },
  "description": "Sentinel-style policy checks for internal Terraform modules",
  "defaultEnabled": false,
  "relevance": { "files": ["*.tf", "terraform.tfstate"] }
}
```

When a user opens a project containing `*.tf` files, the Discover tab pins `terraform-policy-pack` at the top with the **suggested for this directory** label ([Discover plugins docs](https://code.claude.com/docs/en/discover-plugins)). The other 29 plugins are still installable, just not pinned. In a directory with no `*.tf` files, the plugin does not appear at the top, is not auto-enabled, and contributes zero per-turn tokens.

The `relevance` payload shape above is illustrative — the public schema is not yet documented, and a misconfigured signal still requires manual review until a lint surface ships.

## Key Takeaways

- Three Claude Code settings compose into one pattern: `pluginSuggestionMarketplaces` (admin allowlist), per-plugin `relevance` (directory signals), and `defaultEnabled: false` (opt-in activation). All three are required to deliver the value.
- `pluginSuggestionMarketplaces` is managed-settings-only and depends on the marketplace also being declared in `extraKnownMarketplaces` or `strictKnownMarketplaces` ([Claude Code settings docs](https://code.claude.com/docs/en/settings)).
- Without `defaultEnabled: false`, "directory-aware suggestion" silently becomes "always-on context tax" — the plugin is already loaded by the time it is suggested.
- The `relevance` schema is not yet publicly documented; treat author-declared relevance as untrusted input until a lint surface bounds how broadly an author can claim relevance.
- The pattern only earns its place at ~10+ plugins per marketplace; below that, the Discover tab is already short enough to scan and the relevance pin adds an unobservable ranking step with no real noise to reduce.

## Related

- [Enterprise-Managed Plugin Governance](../security/enterprise-managed-plugin-governance.md) — the broader admin-policy surface that `pluginSuggestionMarketplaces` slots into
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md) — defines the plugin and marketplace unit this pattern decorates with relevance metadata
- [Pre-Install Context-Cost Projection in Plugin Marketplaces](marketplace-cost-projection.md) — the *how much* axis at the choice moment; this pattern decides the *which* axis at the same moment
- [Pre-Install Plugin Transparency: Capability Inventory and Cost Projection](pre-install-plugin-transparency.md) — the umbrella transparency contract a directory-aware suggestion presupposes
- [Cross-IDE Plugin Discovery: One Install Surface, Many Consuming Agents](cross-ide-plugin-discovery.md) — the install-surface contract; relevance signalling is the per-consumer filter on top
