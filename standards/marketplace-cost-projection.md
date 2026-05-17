---
title: "Pre-Install Context-Cost Projection in Plugin Marketplaces"
description: "Marketplaces that show per-turn and per-invocation token cost at the browse pane move the cost signal from after install to the choice moment."
tags:
  - standards
  - cost-performance
  - claude
aliases:
  - Pre-Install Token Cost Projection
  - Plugin Marketplace Cost Projection
---

# Pre-Install Context-Cost Projection in Plugin Marketplaces

> Plugin marketplaces that publish each plugin's projected per-turn and per-invocation token cost beside the install button let an operator rank candidates by context budget at the choice moment, instead of discovering cost after installation.

Pre-install context-cost projection is a marketplace metadata pattern: the host computes each plugin's projected token contribution from its declared components and renders the number in the browse pane alongside name, description, and install action. Claude Code v2.1.143 (2026-05-15) implements it: *"Added projected context cost (per-turn and per-invocation token estimates) to the `/plugin` marketplace browse pane"* ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). The same telemetry was already available post-install via `claude plugin details <name>` (v2.1.141) — the marketplace projection moves the number one workflow step upstream, from the accountability moment to the comparison moment.

## When the Projection Pays Off

The pattern produces a real signal only under specific conditions. Lead with the conditions; without them, the number is advisory data:

- **Candidates have meaningfully different cost footprints.** When every plugin under consideration contributes 50–200 tokens always-on, the ranking is rounding noise — pick on functionality, not on 80 tokens.
- **A downstream budget exists.** Without a per-session token quota, a runtime warning, or a CI check on installed plugin cost, awareness alone is unlikely to change aggregate behaviour. The npm ecosystem ships parallel pre-install size signals — [Bundlephobia](https://bundlephobia.com/) and the [Shields.io npm-bundle-size badge](https://shields.io/badges/npm-bundle-size) — and the same critique applies: a number without an enforcement mechanism is a number.
- **Operators install via the browse pane**, not via direct CLI. `/plugin install <name>@<marketplace>` skips the marketplace UI entirely ([Discover and install plugins](https://code.claude.com/docs/en/discover-plugins)).

Outside these conditions the projection is theatre — a number that looks decisive without changing what gets installed.

## The Two Cost Figures

The Claude Code implementation splits cost into two regimes that should be ranked independently, mirroring the [post-install attribution split](../observability/plugin-token-cost-attribution.md):

- **Per-turn (always-on)** — tokens added every turn the plugin is active, contributed by skill descriptions, agent descriptions, and command names. A static cost that compounds with session length regardless of which components fire.
- **Per-invocation (on-invoke)** — tokens a component costs only when it fires. Shown per component, not summed across the plugin, because a session invokes only a subset of components ([Plugins reference — plugin details](https://code.claude.com/docs/en/plugins-reference)).

Sorting plugins by total cost collapses the two regimes. Sort always-on descending to find slow-growing static bloat. Sort on-invoke descending and cross-reference with workload data to find components whose firing frequency makes them expensive in aggregate.

## How the Host Computes the Projection

The host derives the number statically — the plugin does not need to run for the projection to exist. The always-on total is computed against the active model's tokenizer via the `count_tokens` API; per-component on-invoke numbers are proportionally scaled from declared component bodies. When the API is unreachable, the command falls back to a character-based estimate ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)).

The same reference is explicit about the accuracy ceiling: *"Token counts are estimates and may differ from actual usage."* The character-based fallback overcounts JSON-heavy descriptions and undercounts dense prose. Rankings stay directionally useful; absolute numbers drift.

## Why It Works

Pre-install projection works because it moves the cost signal from the **accountability moment** (after install, when the only remediation is uninstall) to the **choice moment** (during selection, when remediation is picking a lighter alternative for free). The same anchoring mechanism makes nutrition labels effective on packaged food and bundle-size badges effective in npm READMEs: the cost becomes a comparison axis at the moment the operator can act on it cheaply. The Plugins reference notes the same data exists post-install via `claude plugin details` ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)) — the projection's value is purely positional. The per-turn vs per-invocation split sharpens the mechanism further: per-turn collapses to a static budget the operator can cap deterministically, while per-invocation is variable cost that requires usage data to evaluate. Showing both at choice time lets the operator make different decisions for each column.

## When This Backfires

- **On-invoke variance dominates.** A plugin shows 50 tok per-turn and 8000 tok per-invocation. The number projects as cheap if the operator assumes rare firing; real cost can swing 100× based on workflow. Without `/usage` traffic data to pair against the projection, the on-invoke column misleads more than it informs.
- **CLI bypass.** Direct `claude plugin install` does not surface the projection. Operators who install from a README link or a peer's recommendation never see the number.
- **Tokenizer API unreachable.** The character-based fallback distorts cross-plugin rankings ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)). A plugin with verbose JSON tool schemas can rank as heavier than a plugin with dense prose that actually costs more.
- **MCP-server-heavy plugins.** MCP cost can dwarf skill and agent description cost, and the static projection cannot easily account for servers that return varying tool sets per session ([apideck.com — MCP context window cost](https://www.apideck.com/blog/mcp-server-eating-context-window-cli-alternative)).
- **No budget gate downstream.** Awareness without an enforcement mechanism is advisory data. VS Code's marketplace [does not show install size pre-install](https://github.com/microsoft/vscode/issues/158670) — a years-open feature request — and the inverse holds: surfacing a number without a budget to compare against does not change behaviour.

## Example

The Claude Code `/plugin` browse pane and `claude plugin details` share the same projection model. The latter shows what the marketplace pane displays per plugin ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)):

```text
security-guidance 1.2.0
  Real-time security analysis for Claude Code sessions
  Source: security-guidance@claude-code-marketplace

Projected token cost
  Always-on:   ~180 tok   added to every session

Per-component (rounded)
  component            always-on  on-invoke
  scan-dependencies        ~100      ~2400
  review-changes            ~80      ~1800
```

In the marketplace browse pane, the operator comparing `security-guidance` against an alternative sees the 180-token always-on number before clicking install. If the alternative shows 800 tokens always-on with similar functionality, the choice becomes a 620-token decision the operator could not have made post-install without first paying both costs and running `claude plugin details` against both.

The reverse case sharpens the limit: two security plugins showing 150 and 200 tokens always-on differ by rounding noise. The projection does not break the tie — functionality fit, MCP server count, or vendor trust decides.

## Key Takeaways

- Pre-install cost projection moves a token-cost signal from the post-install accountability moment to the pre-install comparison moment ([Claude Code changelog v2.1.143](https://code.claude.com/docs/en/changelog)).
- Per-turn and per-invocation are independent cost regimes — rank each column separately, never the sum.
- The host computes the projection statically via `count_tokens` against the active model's tokenizer, with character-based fallback when the API is unreachable ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)).
- The pattern produces signal only when candidates differ meaningfully, a downstream budget gate exists, and operators select via the browse pane rather than CLI.
- CLI installs (`claude plugin install <name>@<marketplace>`) bypass the projection entirely; the pattern's reach is bounded by the install surface.

## Related

- [Per-Plugin Token-Cost Attribution via `claude plugin details`](../observability/plugin-token-cost-attribution.md) — the post-install, per-plugin cut of the same telemetry
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md) — what a plugin is and why it sits at this attribution layer
- [Cross-IDE Plugin Discovery: One Install Surface, Many Consuming Agents](cross-ide-plugin-discovery.md) — the install-surface contract this pattern decorates with cost metadata
- [Audit Tool Output Token Cost](../agent-readiness/audit-tool-output-token-cost.md) — drill-down for the on-invoke column when one component dominates
- [The Infinite Context anti-pattern](../anti-patterns/infinite-context.md) — the failure mode the per-turn column makes visible
