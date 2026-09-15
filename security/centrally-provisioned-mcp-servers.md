---
title: "Centrally Provisioned MCP Servers: Remote Transports Only"
term: "Centrally Provisioned MCP Servers"
description: "The managedMcpServers key pushes MCP servers to every user, and rejects any entry naming a command, args, env, or headersHelper, so a settings document cannot start a local process."
tags:
  - security
  - claude
  - mcp
aliases:
  - organization-provided MCP servers
  - managedMcpServers managed setting
  - central MCP server provisioning
applies_to: "claude-code@2.x"
last_reviewed: 2026-09-14
status: current
maturity: emerging
---

# Centrally Provisioned MCP Servers: Remote Transports Only

> An organization pushes MCP servers to every user through managed settings, and the channel refuses any entry that names a program to run.

`managedMcpServers` is a managed-settings key that gives every user in an organization a set of remote MCP servers alongside the ones they add themselves. Claude Code v2.1.259 shipped it on 2 September 2026, and "Earlier clients ignore the key" ([Control MCP server access for your organization](https://code.claude.com/docs/en/managed-mcp#provide-servers-through-managed-settings)). Two conditions bound it. The transport restriction covers this settings channel only, not central provisioning in general, and a rejected entry is recorded on the user's machine rather than at the console where the mistake was made.

## What an entry may contain

Claude Code "loads an entry only when it passes every check below. It drops an entry that fails one, records a notice you can read with `/status`, and still loads the other entries" ([managed-mcp](https://code.claude.com/docs/en/managed-mcp#what-an-entry-can-contain)). The checks:

- `type` is `http` or `sse`, with `streamable-http` accepted as an alias for `http`.
- `url` is an `https://` URL. Claude Code "refuses a plain `http://` URL, including one that points at `localhost`".
- The entry has no `command`, `args`, `env`, or `headersHelper` member.
- No value contains a `${VAR}` reference. Environment variables are not expanded here, so write literal values.
- The server name uses only letters, numbers, hyphens, and underscores, and no key or value carries control or invisible formatting characters.

The third check reaches further than the release note's "entries that name a command to run are skipped" ([changelog 2.1.259](https://code.claude.com/docs/en/changelog#2-1-259)). Claude Code "executes a `headersHelper` as an arbitrary shell command" ([MCP docs](https://code.claude.com/docs/en/mcp#use-dynamic-headers-for-custom-authentication)), so excluding `command` alone would have left the same reach open under a different key.

## Why it works

Capability is matched to the authority a delivery channel demands, not to the authority the organization nominally holds. The same administrator can distribute a local stdio server, but only through `managed-mcp.json`, whose documented example carries `"type": "stdio"` with a `command`. That file sits at a protected system path: "Any process that can write to a system path with administrator privileges can deploy the file", usually Jamf, Group Policy, or Intune. It "cannot be delivered through server-managed settings" ([managed-mcp](https://code.claude.com/docs/en/managed-mcp#deploy-managed-mcp-json)).

`managedMcpServers` travels the easier route: a settings document a server can hand to a client over the network. Anthropic states the consequence of the exclusion list directly, "so a managed settings document never names a program to run on a user's machine". The supporting checks close the same route by other means. Without `${VAR}` expansion an entry cannot read the user's environment, and with `https://` required it cannot be aimed at a process already listening on the user's own host.

## Who sees a dropped entry

The notice goes to the wrong person. `/status` on the user's machine is the only destination the documentation gives for it, so an administrator who deploys a bad entry has nothing to read at the console, and the user who lost the server has no reason to go looking. One mistake lands squarely in that gap: "Claude Desktop has a managed setting with the same name whose value is an array of a different entry shape, so don't copy one into the other" ([managed-mcp](https://code.claude.com/docs/en/managed-mcp#what-an-entry-can-contain)). Roll out to one machine you can log into before you push to the fleet.

## When this backfires

- The servers you need are local. A filesystem server, a `localhost` database proxy, or an internal service without TLS cannot be provided this way, which pushes you to `managed-mcp.json`. That file takes exclusive control as a side effect: with it deployed, "Users can't add, modify, or use any other MCP servers" ([managed-mcp](https://code.claude.com/docs/en/managed-mcp#exclusive-control-with-managed-mcp-json)).
- Provisioning is not enforcement. A provided server outranks a same-named entry in local, project, or user scope, and `claude mcp remove` refuses it. Users can still switch it off in `/mcp`, where provided servers appear under Managed MCPs, and their own `deniedMcpServers` blocks it outright ([managed-mcp](https://code.claude.com/docs/en/managed-mcp#what-users-can-see-and-change)).
- Delivered through server-managed settings, the key is withheld rather than served stale. "If the confirmation fails, the session continues without the provided servers and `/status` says they are withheld", and on a first launch "a `claude -p` run that has already started can finish without them". A CI job depending on a provided tool then fails as though the tool never existed.
- Header credentials are fleet-wide. "Anyone who can read the managed settings on a machine, including the user, can read a header value you set here." Issue the credential to that whole audience, or drop `headers` and let each user authenticate with OAuth.
- Nobody on the receiving end vetted the tools. Anthropic "doesn't security-audit or manage any MCP server", and a provided server's tool definitions reach the model on every turn. Central provisioning moves that review from many users at install time to one administrator at push time. See [Vetting Tool Definitions for Exfiltration Signatures](vetting-tool-definitions-before-install.md) for what it has to look for.

## Example

A two-server policy in a managed settings source. The search server uses OAuth, so each user authenticates as themselves. The records server sends a header issued for the whole organization ([managed-mcp](https://code.claude.com/docs/en/managed-mcp#provide-servers-through-managed-settings)).

```json
{
  "managedMcpServers": {
    "search": {
      "type": "http",
      "url": "https://search.example.com/mcp"
    },
    "records": {
      "type": "http",
      "url": "https://records.example.com/mcp",
      "headers": {
        "X-Records-Key": "key-issued-for-all-claude-code-users"
      }
    }
  }
}
```

Adding `"command": "/usr/local/bin/records-server"` to either entry produces no error at deploy time. The entry stops loading, the other one keeps working, and the notice waits in `/status` on each user's machine.

## Key Takeaways

- The exclusion list is `command`, `args`, `env`, and `headersHelper`, not `command` alone, because `headersHelper` runs as a shell command and would otherwise be an equivalent route.
- A dropped entry and one you never deployed look identical from the console, so diagnose a missing provided server from a user's `/status` rather than from the settings document you wrote.
- If your fleet needs a local stdio server, `managedMcpServers` is the wrong key. `managed-mcp.json` carries it, at the cost of exclusive control over every other MCP server.
- Users keep a per-machine veto through `/mcp` and their own `deniedMcpServers`, so treat provisioning as delivery rather than as a guarantee the server is running.

## Related

- [Enterprise-Managed Plugin Governance for Agent CLIs](enterprise-managed-plugin-governance.md) — the same admin channel applied to the plugin code-load path, where the code does get distributed
- [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md) — what to do about the fetch failure that withholds provided servers
- [Vetting Tool Definitions for Exfiltration Signatures](vetting-tool-definitions-before-install.md) — the install-time review that central provisioning relocates rather than removes
- [Scoped MCP Server Discovery: Most-Specific-Wins Resolution](../tool-engineering/scoped-mcp-server-discovery.md) — the local, project, and user precedence ladder a provided server sits above
- [Team-Scoped Agent Policy Delegation](team-scoped-policy-delegation.md) — the adjacent admin ceiling, where teams vary values inside a bound rather than receive them whole
