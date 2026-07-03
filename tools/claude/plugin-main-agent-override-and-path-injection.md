---
title: "Plugin-Activated Main-Agent Override and Bin/ PATH Injection"
description: "A plugin's settings.json swaps the main thread agent and its bin/ directory injects executables onto the Bash tool's PATH — one declarative bundle, atomically activated when the plugin is enabled."
tags:
  - claude
  - tool-engineering
  - security
aliases:
  - plugin settings.json agent field
  - plugin bin directory PATH injection
  - scope-bound agent activation
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-03
status: current
---

# Plugin-Activated Main-Agent Override and Bin/ PATH Injection

> A plugin's `settings.json` swaps the main thread agent and its `bin/` directory injects executables onto the Bash tool's PATH.

A plugin's root `settings.json` activates one of its bundled agents as the main thread; the same plugin's `bin/` directory adds executables to the Bash tool's `PATH` for the plugin's enabled lifetime. Enabling the plugin reshapes the agent without editing global settings; disabling reverses both legs. The contract requires Claude Code v2.1.157 or later — earlier versions silently ignored the `agent` field.

## The two contracts

### `settings.json.agent` swaps the main thread

A plugin places `settings.json` at its root. "Plugins can include a `settings.json` file at the plugin root to apply default configuration when the plugin is enabled. Currently, only the `agent` and `subagentStatusLine` keys are supported." ([Create plugins — Ship default settings](https://code.claude.com/docs/en/plugins#ship-default-settings-with-your-plugin))

```json
{
  "agent": "security-reviewer"
}
```

"Setting `agent` activates one of the plugin's custom agents as the main thread, applying its system prompt, tool restrictions, and model" ([Create plugins](https://code.claude.com/docs/en/plugins#ship-default-settings-with-your-plugin)). The named agent must exist as `agents/<name>.md` inside the plugin.

### `bin/` injects executables onto PATH

A `bin/` directory at the plugin root publishes executables to the Bash tool's environment: "`bin/` — Executables added to the Bash tool's `PATH`. Files here are invokable as bare commands in any Bash tool call while the plugin is enabled" ([Plugins reference — File locations](https://code.claude.com/docs/en/plugins-reference#file-locations-reference)). Executables are exposed under their filename — there is no `plugin-name:` namespace.

## Precedence and per-session override

- Plugin-internal: "Settings from `settings.json` take priority over `settings` declared in `plugin.json`. Unknown keys are silently ignored." ([Create plugins](https://code.claude.com/docs/en/plugins#ship-default-settings-with-your-plugin))
- Per-session: "the `agent` field in `settings.json` is now honored for dispatched sessions, with `--agent <name>` to override it" ([Claude Code changelog](https://code.claude.com/docs/en/changelog), v2.1.157).

## How it differs from related primitives

| Primitive | Activation | Lifetime | What it changes |
|---|---|---|---|
| `settings.json.agent` (plugin) | Plugin enabled | Plugin enabled | Main thread agent — prompt, tools, model |
| [Sub-agents](sub-agents.md) | Claude delegates | Per delegation | Isolated worker context — does not replace main |
| [Managed Settings Drop-In](managed-settings-drop-in.md) | Admin push | Until policy change | Org-wide configuration fragments |
| `bin/` PATH injection | Plugin enabled | Plugin enabled | Bash tool's `PATH` |
| [Plugin Background Monitors](plugin-background-monitors.md) | Plugin enabled (auto-arm) | Session | Stdout-to-notification stream |

Distinct from sub-agents because it replaces (not augments) the default personality, and from managed settings because scope is plugin enable/disable, not policy lifetime.

## Why it works

The pattern collapses two operations — swap the agent personality and make a set of binaries available — into one declarative file structure. It activates atomically when the plugin is enabled and reverses when it is disabled. Atomicity matters: the agent override and the binaries appear together, not in two install steps that could partially fail. The plugin-scoped `bin/` lives inside `${CLAUDE_PLUGIN_ROOT}` and is added to PATH only while the plugin is enabled ([Plugins reference](https://code.claude.com/docs/en/plugins-reference#file-locations-reference)), so `/plugin disable` removes both the agent and the PATH entry without per-developer cleanup.

## When this backfires

- Pre-v2.1.157, the `agent` field is silently dead. Dispatched sessions did not honor it until that release ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). On older clients the plugin loads, the binaries land on PATH, and the main thread stays the default. Half the contract ships with no error.
- A managed-enabled bundle is a silent permission expansion. An admin force-installs a plugin via `enabledPlugins` ([Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)). If the plugin ships `settings.json: { "agent": "permissive-helper" }`, it swaps every developer's main thread without per-developer consent. Review the plugin's `agents/<name>.md` tool allowlist and model before org-wide enablement — see [Enterprise-Managed Plugin Governance for Agent CLIs](../../security/enterprise-managed-plugin-governance.md).
- Bin names collide silently. `bin/` entries are bare command names with no namespace. Two enabled plugins shipping `bin/deploy` resolve to whichever appears first on PATH. The developer thinks they are running one tool, and they are running the other.
- Only two keys are recognized. Treating `settings.json` as a general per-plugin config file produces no error and no effect ([Create plugins](https://code.claude.com/docs/en/plugins#ship-default-settings-with-your-plugin)).
- Composability drops. A consumer who wants the activated agent but a different binary set has to fork the plugin — the bundle locks the two together.
- Marketplace injection threatens both legs at once. [PromptArmor](https://www.promptarmor.com/resources/hijacking-claude-code-via-injected-marketplace-plugins) and [SentinelOne](https://www.sentinelone.com/blog/marketplace-skills-and-dependency-hijack-in-claude-code/) marketplace-injection disclosures target plugin-supplied code. A tampered bundle swaps the agent personality and adds attacker-controlled binaries to PATH in one install.

## Example

A `security-reviewer` plugin that activates a hardened review agent and ships the binaries the review workflow shells out to.

`security-reviewer-plugin/settings.json`:

```json
{ "agent": "security-reviewer" }
```

`security-reviewer-plugin/agents/security-reviewer.md` (restricted tool allowlist, pinned model):

```markdown
---
name: security-reviewer
description: Security-focused review of diffs against an approved-action policy
model: sonnet
tools: [Read, Grep, Glob, Bash]
---

You are a security reviewer. Read the diff with Read+Grep+Glob.
Run only `semgrep-scan`, `gitleaks-scan`, and `trivy-scan` via Bash.
Refuse other shell commands. Report findings with severity.
```

Plugin layout — agent and binaries in one bundle:

```text
security-reviewer-plugin/
├── .claude-plugin/plugin.json
├── settings.json
├── agents/security-reviewer.md
└── bin/
    ├── semgrep-scan
    ├── gitleaks-scan
    └── trivy-scan
```

`/plugin enable security-reviewer` swaps the main thread to the security-reviewer agent and makes the three scanners callable as bare commands. `/plugin disable` reverts both. Mid-session, `claude --agent default` restores the default agent without disabling the plugin if the PATH bundle is still wanted.

## Key Takeaways

- `settings.json.agent` replaces the main thread with one of the plugin's bundled agents — prompt, tool restrictions, and model are all applied
- Requires Claude Code v2.1.157 or later; earlier versions ignore the field with no error
- `settings.json` keys override the same keys declared in `plugin.json`; unknown keys silently no-op
- `--agent <name>` on the CLI overrides the plugin-activated agent for the current session
- `bin/` publishes bare-name executables onto the Bash tool's PATH for the plugin's enabled lifetime
- `bin/` names are un-namespaced — colliding executables resolve by first-on-PATH, silently
- The bundled pairing plus `enabledPlugins` force-install is a permission-expansion vector that deserves pre-rollout review

## Related

- [Plugin Background Monitors](plugin-background-monitors.md) — sibling primitive: declarative supervision auto-armed at session start from a plugin manifest
- [Sub-Agents](sub-agents.md) — the agent definition format the `settings.json.agent` key activates
- [Managed Settings Drop-In Directory](managed-settings-drop-in.md) — orthogonal admin contract for distributing settings without merge conflicts
- [Extension Points](extension-points.md) — decision framework for choosing between CLAUDE.md, rules, skills, hooks, subagents, MCP, and plugins
- [Enterprise-Managed Plugin Governance for Agent CLIs](../../security/enterprise-managed-plugin-governance.md) — the `enabledPlugins` force-install surface that turns plugin-activated overrides into org-wide policy
- [Plugin and Extension Packaging](../../standards/plugin-packaging.md) — the broader distribution model that bundles `settings.json` and `bin/` alongside agents, skills, hooks, and MCP servers
- [Local Plugin Scaffolding via `claude plugin init`](local-plugin-scaffolding.md) — the authoring side of the same bundle: scaffolds the `settings.json` + `agents/` + `bin/` layout this page activates, gated on the same v2.1.157 release
