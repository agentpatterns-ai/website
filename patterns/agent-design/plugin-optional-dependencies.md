---
title: "Plugin optionalDependencies: Companions Users Can Disable"
term: "Plugin Optional Dependencies"
description: "Claude Code 2.1.331 plugins can list companions in optionalDependencies: they install with the plugin and users disable them alone. Use only if the core works without."
tags:
  - agent-design
  - claude
  - plugins
aliases:
  - optionalDependencies
  - optional plugin dependencies
  - companion plugins
last_reviewed: 2026-11-24
maturity: emerging
---

# Plugin optionalDependencies: Companions Users Can Disable

> Put a companion plugin in `optionalDependencies` only when your plugin still works with it turned off. Anything the core calls belongs in `dependencies`.

A plugin optional dependency is a companion plugin that installs with the plugin listing it and that a user can disable or uninstall on its own. Claude Code 2.1.331 added the `optionalDependencies` manifest field for this ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). It sits beside `dependencies`, which the manifest reference defines as "Plugins that must be enabled for this one to work" ([Manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference)).

## When to split a plugin

Split when one piece is useful to most users and another only to some. A deploy plugin with an optional runbook companion fits. The docs describe a hard dependency as a plugin "such as one whose MCP server or skill it calls" ([Plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies)). If your skill calls the companion's MCP tool, that skill breaks the moment a user disables the companion, so the companion stays a hard dependency.

Run one test per companion: disable it and use the core. If the core still does its job, the companion can be optional. If anything errors, the companion is a hard dependency.

## How it differs from a hard dependency

The two fields differ on the disable path. For a hard dependency, Claude Code refuses to disable a plugin "when another enabled plugin still needs the one you named", and prints a chained command that disables both ([Install plugins](https://code.claude.com/docs/en/plugins/install)). A user who wants to drop one extra from a bundle has to drop the bundle. An optional dependency installs the same way but can be disabled or uninstalled without touching the parent ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

| | `dependencies` | `optionalDependencies` |
|---|---|---|
| Installs with the parent | Yes, enabled at the same scope | Yes |
| User disables it alone | Refused while a dependent is enabled | Allowed |
| User uninstalls it alone | Not documented | Allowed |
| Version range syntax | Object with `name`, `marketplace`, `version` | Not documented |

## What the docs do not say yet

On 2026-11-24 the changelog line is the only documentation. The manifest reference field table lists `dependencies` and no `optionalDependencies`, and the dependencies page never mentions it ([Manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference), [Plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies)). The value syntax, version constraints, prune behavior, and the result of a failed optional install are all unstated. Do not borrow npm's meaning. In npm the field tells the installer to "proceed if it cannot be found or fails to install" ([npm package.json docs](https://docs.npmjs.com/cli/v11/configuring-npm/package-json)), which is a different promise.

## Why it works

A hard dependency couples install to requirement. That is correct for a plugin the core calls and wrong for an extra, because the disable refusal makes the user choose all or nothing. `optionalDependencies` keeps the install and drops the requirement. Debian draws the same line. Its policy says to use `Depends` when a package is "required for the depending package to provide a significant amount of functionality", and calls `Recommends` "a strong, but not absolute, dependency" ([Debian Policy, chapter 7](https://www.debian.org/doc/debian-policy/ch-relationships.html)).

## When this backfires

- The core calls the companion. npm's warning holds here too: "It is still your program's responsibility to handle the lack of the dependency" ([npm package.json docs](https://docs.npmjs.com/cli/v11/configuring-npm/package-json)).
- Most users never want the extra. It installs by default, and the install docs tell users to find plugins "that still add startup and context cost, then disable or uninstall them" ([Install plugins](https://code.claude.com/docs/en/plugins/install)). An opt-in plugin costs those users nothing.
- Your users run Claude Code older than 2.1.331. The current reference strips an unrecognized top-level key and loads the plugin, while v2.0.15 through v2.1.75 reject a manifest with an unrecognized `engines` key ([Manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference)). Test on the oldest version your users run.
- The companion must stay in a version range. Only `dependencies` documents range syntax, so keep it there.

## Example

The dependencies docs show a team bundle, `backend-standard`, whose manifest lists `secrets-vault`, `deploy-kit`, `db-migrate`, and `oncall-runbook` as `dependencies` ([Plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies)). Each one is a hard dependency, so an engineer who never works on-call cannot disable `oncall-runbook` while `backend-standard` is enabled. If no other plugin in the set calls `oncall-runbook`, it passes the disable test. Moving it to `optionalDependencies` then lets that engineer turn it off and keep the rest.

## Key Takeaways

- The deciding question is whether the core works with the companion disabled.
- A hard dependency blocks a lone disable; an optional one allows it.
- One changelog line is the whole spec today, so check the manifest reference before relying on syntax or edge behavior.
- npm's field of the same name means install-failure tolerance. Do not assume Claude Code tolerates a failed optional install.

## Related

- [Plugin Dependency Declaration and Disable-Chain Hints](../../standards/plugin-dependency-declaration.md)
- [Designing Agent Plugins to Survive Co-Installation](plugin-co-installation-safety.md)
- [Plugin and Extension Packaging](../../standards/plugin-packaging.md)
- [Per-Plugin Token-Cost Attribution](../../observability/plugin-token-cost-attribution.md)
