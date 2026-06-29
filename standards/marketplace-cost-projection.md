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
last_reviewed: 2026-06-03
maturity: emerging
---

# Pre-Install Context-Cost Projection in Plugin Marketplaces

> Plugin marketplaces that show each plugin's projected per-turn and per-invocation token cost beside the install button let operators rank candidates by context budget before installing.

Pre-install context-cost projection is a marketplace metadata pattern. The host computes each plugin's projected token contribution from its declared components and renders it in the browse pane beside the name and install action. Claude Code v2.1.143 (2026-05-15) implements it: "Added projected context cost (per-turn and per-invocation token estimates) to the `/plugin` marketplace browse pane" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). The same telemetry was available after install via `claude plugin details <name>` (v2.1.141). The marketplace projection moves it upstream, from the accountability moment to the comparison moment.

## When the projection pays off

The pattern produces signal only under specific conditions:

- Cost footprints differ meaningfully. When candidates all contribute 50 to 200 tokens always-on, the ranking is rounding noise, so pick on functionality.
- A downstream budget exists. Without a per-session quota, runtime warning, or CI check, awareness rarely changes behavior. npm ships parallel pre-install size signals — [Bundlephobia](https://bundlephobia.com/) and the [Shields.io npm-bundle-size badge](https://shields.io/badges/npm-bundle-size) — and the critique applies: a number without enforcement is a number.
- Operators install via the browse pane, not the CLI. `/plugin install <name>@<marketplace>` skips the marketplace UI ([Discover and install plugins](https://code.claude.com/docs/en/discover-plugins)).

Outside these conditions the projection is theatre.

## The two cost figures

Claude Code splits cost into two regimes, and you should rank them independently. This mirrors the [post-install attribution split](../observability/plugin-token-cost-attribution.md):

- Per-turn (always-on) — tokens added every turn the plugin is active, from skill descriptions, agent descriptions, and command names. This static cost compounds with session length.
- Per-invocation (on-invoke) — tokens a component costs only when it fires. The pane shows these per component, not summed, because a session invokes only a subset ([Plugins reference — plugin details](https://code.claude.com/docs/en/plugins-reference)).

Sorting by total collapses the two regimes. Sort always-on descending to find static bloat. Sort on-invoke descending and cross-reference with workload data to find components whose firing frequency makes them expensive in aggregate.

## How the host computes the projection

The host derives the number statically, so the plugin does not need to run. It computes always-on totals against the active model's tokenizer via the `count_tokens` API. Per-component on-invoke numbers scale proportionally from declared component bodies. When the API is unreachable, the command falls back to a character-based estimate ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)).

The same reference flags the accuracy ceiling: "Token counts are estimates and may differ from actual usage." The fallback overcounts JSON-heavy descriptions and undercounts dense prose, so rankings stay directionally useful while absolute numbers drift.

## Why it works

Pre-install projection moves the cost signal from the accountability moment to the choice moment. At the accountability moment, after install, the only remediation is uninstall. At the choice moment, during selection, the remediation is picking a lighter alternative for free. The same anchoring makes nutrition labels work on packaged food and bundle-size badges work in npm READMEs: cost becomes a comparison axis when the operator can act on it cheaply. The per-turn versus per-invocation split sharpens it. Per-turn is a static budget the operator can cap deterministically. Per-invocation is variable cost that needs usage data to evaluate.

## When this backfires

- On-invoke variance dominates. A plugin at 50 tok per-turn and 8000 tok per-invocation reads as cheap if the operator assumes rare firing, yet real cost can swing 100 times by workflow. Without `/usage` data, the on-invoke column misleads.
- CLI bypass. Direct `claude plugin install` does not surface the projection. Operators installing from a README link or peer recommendation never see the number.
- Tokenizer API unreachable. The fallback distorts cross-plugin rankings ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)), so verbose JSON schemas can rank heavier than dense prose that actually costs more.
- MCP-server-heavy plugins. MCP cost can dwarf skill and agent description cost, and static projection cannot account for servers returning varying tool sets per session ([apideck.com — MCP context window cost](https://www.apideck.com/blog/mcp-server-eating-context-window-cli-alternative)).
- No budget gate downstream. VS Code's marketplace [does not show install size pre-install](https://github.com/microsoft/vscode/issues/158670), a years-open feature request, and the inverse holds: a number without a budget to compare against does not change behavior.

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

In the marketplace browse pane, the operator comparing `security-guidance` against an alternative sees the 180-token always-on number before selecting install. If the alternative shows 800 tokens always-on with similar functionality, the choice becomes a 620-token decision. The operator could not have made that decision after install without first paying both costs and running `claude plugin details` against both.

The reverse case sharpens the limit: two security plugins showing 150 and 200 tokens always-on differ by rounding noise. The projection does not break the tie. Functionality fit, MCP server count, or vendor trust decides.

## Key Takeaways

- Pre-install cost projection moves a token-cost signal from the post-install accountability moment to the pre-install comparison moment ([Claude Code changelog v2.1.143](https://code.claude.com/docs/en/changelog)).
- Per-turn and per-invocation are independent cost regimes — rank each column separately, never the sum.
- The host computes the projection statically via `count_tokens` against the active model's tokenizer, with character-based fallback when the API is unreachable ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)).
- The pattern produces signal only when candidates differ meaningfully, a downstream budget gate exists, and operators select via the browse pane rather than CLI.
- CLI installs (`claude plugin install <name>@<marketplace>`) bypass the projection entirely; the pattern's reach is bounded by the install surface.

## Related

- [Pre-Install Plugin Transparency: Capability Inventory and Cost Projection](pre-install-plugin-transparency.md) — the umbrella contract; cost projection is the *how much* column beside the *what* column
- [Plugin Dependency Declaration and Disable-Chain Hints](plugin-dependency-declaration.md) — transitive always-on cost compounds across declared dependencies; rank with this projection before adding edges
- [Per-Plugin Token-Cost Attribution via `claude plugin details`](../observability/plugin-token-cost-attribution.md) — the post-install, per-plugin cut of the same telemetry
- [Plugin and Extension Packaging: Distributing Agent Capabilities](plugin-packaging.md) — what a plugin is and why it sits at this attribution layer
- [Cross-IDE Plugin Discovery: One Install Surface, Many Consuming Agents](cross-ide-plugin-discovery.md) — the install-surface contract this pattern decorates with cost metadata
- [The Infinite Context anti-pattern](../anti-patterns/infinite-context.md) — the failure mode the per-turn column makes visible
