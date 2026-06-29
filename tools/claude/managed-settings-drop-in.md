---
title: "Managed Settings Drop-In Directory: Enterprise Policy Fragmentation"
description: "Deploy independent policy fragments per team using managed-settings.d/, eliminating merge conflicts and centralizing ownership without a single shared file."
tags:
  - claude
  - instructions
  - security
aliases:
  - managed-settings.d
  - managed settings drop-in
applies_to: "claude-code@2.x"
last_reviewed: 2026-05-27
status: current
---
# Managed Settings Drop-In Directory

> Deploy independent policy fragments per team using `managed-settings.d/`, eliminating merge conflicts and centralizing ownership without a single shared file.

## The problem it solves

Enterprise Claude Code deployments typically start with a single `managed-settings.json` owned by one team. As more teams need to add policies — security, platform, product — the file becomes a shared resource with contention. Whoever owns the file must coordinate, review, and deploy each change, which creates a bottleneck.

The `managed-settings.d/` drop-in directory follows the [systemd drop-in convention](https://manpages.ubuntu.com/manpages/bionic/man5/systemd.unit.5.html) — fragments in a `.d/` directory are [parsed alphabetically after the base file](https://code.claude.com/docs/en/settings#settings-files). Each team deploys its own fragment independently, and Claude Code composes them at runtime.

## How fragments merge

Fragments in `managed-settings.d/` are [sorted alphabetically and merged on top](https://code.claude.com/docs/en/settings#settings-files) of the base `managed-settings.json`. Merge behavior differs by value type:

| Value type | Merge behavior |
|------------|---------------|
| Scalar (`string`, `bool`, `number`) | Later file wins |
| Array | Concatenated and de-duplicated |
| Object | Deep-merged recursively |

`managed-settings.json` is always merged first as the base. All `*.json` files in `managed-settings.d/` are then applied in alphabetical order. Hidden files (starting with `.`) are ignored.

Ordering matters for scalar values: an alphabetically later file wins. A rule in `90-override.json` overwrites the same scalar from `10-base.json`. For arrays, both files contribute — order does not affect the final set, only de-duplication.

## Numeric prefix convention

Use numeric prefixes to make merge order explicit:

```
managed-settings.d/
  00-security.json      # security team: deny rules, allowManagedPermissionRulesOnly
  50-platform.json      # platform team: MCP allowlist, telemetry, auto-update channel
  80-product.json       # product team: tool-specific allow rules for known workflows
```

Lower numbers run first. For scalar settings, the last writer wins, so a higher-numbered fragment overrides a lower-numbered one. Design fragments so teams own non-overlapping settings, which avoids silent overrides.

## Interaction with the primary file

`managed-settings.json` is [merged first as the base](https://code.claude.com/docs/en/settings#settings-files), then all fragments in `managed-settings.d/` layer on top. Because later files win for scalar values, a fragment can override a scalar set in the primary file. Use the primary file for org-wide defaults, and design fragments to extend — not contradict — it.

```
Load order:
  managed-settings.json    ← merged first (base)
  managed-settings.d/00-security.json   ← merged second
  managed-settings.d/50-platform.json   ← merged third
  managed-settings.d/80-product.json    ← merged last
```

## System directory locations

The `managed-settings.d/` directory sits alongside `managed-settings.json` in the [system directory](https://code.claude.com/docs/en/settings#settings-files) for each platform:

| Platform | Path |
|----------|------|
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.d/` |
| Linux / WSL | `/etc/claude-code/managed-settings.d/` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.d\` |

Each team deploys its fragment independently — security CI can push `00-security.json` without touching the platform team's file.

## Trade-offs versus single-file managed settings

| Factor | Single file | Drop-in directory |
|--------|-------------|-------------------|
| Ownership | Centralized | Per-team |
| Merge conflict risk | High (concurrent edits) | Low (separate files) |
| Audit trail | One file in one repo | Fragments across team repos |
| Conflict detection | Explicit (file diff) | Implicit (scalar silently overrides) |
| Deployment complexity | One artifact | One artifact per team |

The main risk with fragments is silent scalar conflicts: if two teams set the same scalar key, the alphabetically later file wins without warning. Keep teams to non-overlapping settings domains, or enforce this through policy review.

## When server-managed settings apply instead

Claude Code 2.1.30+ (Enterprise) and 2.1.38+ (Teams) also support [server-managed settings](https://code.claude.com/docs/en/server-managed-settings) delivered from the Claude.ai admin console. Server-managed and endpoint-managed (file-based) settings occupy the same top tier of the [settings hierarchy](https://code.claude.com/docs/en/settings#settings-precedence), and they [do not merge with each other](https://code.claude.com/docs/en/server-managed-settings). If server-managed delivers any non-empty configuration, Claude Code ignores all endpoint-managed settings, including `managed-settings.d/` fragments. The drop-in directory pattern applies when your org deploys policy through MDM or managed files rather than through the admin console. Anthropic positions endpoint-managed as the stronger option on MDM-enrolled devices because the OS can protect the file from user modification.

## Example

Three teams each own a fragment, deployed through their own CI pipeline.

`00-security.json` — the security team locks down permission rules and blocks bypass mode:

```json
{
  "allowManagedPermissionRulesOnly": true,
  "permissions": {
    "deny": [
      "Bash(curl *)",
      "Bash(wget *)"
    ]
  },
  "disableBypassPermissionsMode": "disable"
}
```

`50-platform.json` — the platform team configures telemetry and the MCP allowlist:

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "https://otel.internal.example.com"
  },
  "allowedMcpServers": [
    { "serverName": "github" },
    { "serverName": "jira" }
  ],
  "allowManagedMcpServersOnly": true
}
```

`80-product.json` — the product team adds allow rules for known safe workflows:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run test *)",
      "Bash(npm run build)"
    ]
  }
}
```

At runtime, Claude Code merges these in order. The security team's `deny` rules and the product team's `allow` rules both appear in the final `permissions` array (arrays are concatenated and de-duplicated). The `allowManagedPermissionRulesOnly: true` from the security fragment means user and project settings cannot add their own permission rules — the merged managed policy is the only one that applies.

## Key Takeaways

- `managed-settings.d/` fragments merge alphabetically on top of `managed-settings.json`
- Scalar values: last file wins. Arrays: concatenated and de-duplicated. Objects: deep-merged
- Numeric prefixes make merge order explicit — design for non-overlapping ownership
- Each team deploys its own fragment independently; no coordination required per change
- Silent scalar conflicts are the main risk — restrict teams to non-overlapping settings domains

## Related

- [Feature Flags & Environment Variables](feature-flags.md)
- [Hooks & Lifecycle](hooks-lifecycle.md)
- [Extension Points: When to Use What](extension-points.md)
- [Auto Mode](auto-mode.md)
- [Channels Permission Relay](channels-permission-relay.md)
