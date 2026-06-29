---
title: "MCP Allowlist by Label, Not by Identity (serverName Trap)"
term: "MCP Allowlist by Label, Not by Identity"
description: "A `serverName`-only MCP allowlist filters the user-chosen label, not the underlying server — any binary or URL the user calls `github` passes the check."
tags:
  - anti-pattern
  - security
  - tool-agnostic
aliases:
  - serverName allowlist trap
  - MCP label-based allowlist
  - identity-vs-label allowlist failure
last_reviewed: 2026-06-02
maturity: established
---

# MCP Allowlist by Label, Not by Identity (serverName Trap)

> A `serverName`-only MCP allowlist filters the user-chosen label, not the underlying server — any binary or URL the user calls `github` passes the check.

Claude Code's managed MCP allowlist accepts three matching keys: `serverUrl` (URL pattern with `*` wildcards), `serverCommand` (exact-match command and arguments), and `serverName` (the label assigned at `claude mcp add` time). The first two pin to artifacts the user does not own. The third is a string the user picks, and the vendor doc tags it with a Warning: "An allowlist that uses only `serverName` entries is not a security control … so a user can call any server `github`. To enforce which servers actually run, add `serverCommand` or `serverUrl` entries" ([Match servers by URL, command, or name](https://code.claude.com/docs/en/managed-mcp#match-servers-by-url-command-or-name)).

The trap lands because `serverName` is the most familiar matching shape — it matches how `~/.claude.json` and `.mcp.json` are keyed, and how `claude mcp get <name>` resolves servers locally. Admins reach for it first and ship a policy that filters labels their users control.

## Why it fails

A key the controlled principal chooses is not an access-control primitive. The MCP server name is a user-supplied positional argument: `claude mcp add --transport http <name> <url>` ([Installing MCP servers](https://code.claude.com/docs/en/mcp#installing-mcp-servers)). Nothing constrains `<name>` to the underlying artifact. `serverCommand` and `serverUrl` instead pin to the resolved invocation and hostname — impersonation requires a different attack class (filesystem write, DNS hijack).

Anthropic's evaluation order makes the demotion mechanical: when the allowlist contains any `serverUrl` entry, "A `serverName` match counts only when the allowlist contains no `serverUrl` entries", and the equivalent rule applies to stdio and `serverCommand` ([How a server is evaluated](https://code.claude.com/docs/en/managed-mcp#how-a-server-is-evaluated)). A mixed allowlist silently never matches `serverName` entries against the transport that has the stricter rule.

The same logic underwrites [Prompt-Only Tool Access Control](prompt-only-tool-access-control.md) and [permission-framework-over-model](../security/permission-framework-over-model.md): enforcement must depend on a signal the controlled party cannot author. Microsoft's Agent Governance Toolkit measures 26.67% policy violations under prompt-only controls versus 0.00% under deterministic enforcement ([agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit)) — same failure mode, one layer up.

## When this backfires

The `serverName` key is not always wrong. The failure modes are narrower than "never use it."

- Mixed allowlists silently demote `serverName`. The docs call it out: "A `serverName` entry in this allowlist would never match anything" once a `serverUrl` or `serverCommand` entry exists for the transport ([Example configuration](https://code.claude.com/docs/en/managed-mcp#example-configuration)).
- A soft allowlist leaks without `allowManagedMcpServersOnly`. Without that flag, "allowlists from every settings source merge, including a user's own `~/.claude/settings.json`" ([Policy-based control](https://code.claude.com/docs/en/managed-mcp#policy-based-control-with-allowlists-and-denylists)). User-authored entries then broaden the managed set.
- Command pinning drifts on dependency bumps. `serverCommand: ["npx", "-y", "@org/server@1.4.2"]` stops matching at `1.4.3`. The tempting patch is a `serverName` downgrade. The right fix is to automate the bump.
- `serverName` denylist entries remain useful. "Nothing overrides a denylist match" ([How a server is evaluated](https://code.claude.com/docs/en/managed-mcp#how-a-server-is-evaluated)). A label entry in `deniedMcpServers` is a belt to the URL or command suspenders.

## Example

Before — a `serverName`-only allowlist filters labels, not servers:

```json
{
  "allowedMcpServers": [
    { "serverName": "github" },
    { "serverName": "sentry" }
  ]
}
```

Any stdio binary or HTTP URL the user labels `github` at `claude mcp add` time passes the policy. The label is user-controlled. The check filters a string the user picks.

After — an identity-grounded allowlist:

```json
{
  "allowedMcpServers": [
    { "serverUrl": "https://api.githubcopilot.com/*" },
    { "serverUrl": "https://mcp.sentry.dev/*" }
  ],
  "deniedMcpServers": [
    { "serverName": "github-shadow" }
  ]
}
```

The allowlist matches by hostname, an artifact the user does not own. The denylist keeps the label key for its belt-and-suspenders use. This mirrors the structure of Anthropic's reference configuration ([Example configuration](https://code.claude.com/docs/en/managed-mcp#example-configuration)).

## Key Takeaways

- A key the controlled principal chooses is not an access-control primitive — `serverName` is a label a user picks, not the underlying server.
- The Anthropic doc carries an explicit Warning that `serverName`-only allowlists are not a security control; the evaluation-order table demotes `serverName` matches whenever any `serverUrl` or `serverCommand` entry exists.
- Mixed allowlists silently never match `serverName` entries for the transport that has a stricter key — admins assume coverage that the table withholds.
- The fix is to allowlist by `serverUrl` (hostname-grounded) or `serverCommand` (binary-grounded, exact arg sequence) and pair with `allowManagedMcpServersOnly: true` so user settings cannot merge in their own allowlist.
- `serverName` denylist entries remain useful — denylist matches always apply, so a labelled bad-server entry is a belt to the URL/command suspenders.

## Related

- [Prompt-Only Tool Access Control](prompt-only-tool-access-control.md)
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](../security/mcp-runtime-control-plane.md)
- [Enterprise-Managed Plugin Governance for Agent CLIs](../security/enterprise-managed-plugin-governance.md)
- [Permission Framework over Model Judgment](../security/permission-framework-over-model.md)
- [Single-Layer Prompt Injection Defence](single-layer-injection-defence.md)
