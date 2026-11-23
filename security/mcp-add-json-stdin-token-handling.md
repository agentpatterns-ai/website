---
title: "Keep MCP Server Tokens Off the Command Line With Stdin JSON"
term: "MCP Add-JSON Stdin Token Handling"
description: "Claude Code 2.1.327 reads an MCP server's JSON from stdin with `claude mcp add-json <name> -`, so a token need not sit in the command. Outside sessions only."
aliases:
  - claude mcp add-json stdin
  - piping MCP server JSON
tags:
  - security
  - claude
  - mcp
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-23
maturity: emerging
---

# Keep MCP Server Tokens Off the Command Line With Stdin JSON

> Claude Code reads an MCP server's JSON from stdin, so a token can stay off the command line.

`claude mcp add-json <name> -` reads the MCP server's JSON from standard input instead of from the command line. Claude Code 2.1.327 added it "so tokens can stay off the command line", and the command is "not available inside a Claude Code session" ([changelog 2.1.327](https://code.claude.com/docs/en/changelog#2-1-327)).

## What the argument form exposes

The documented `add-json` examples put the credential in the command itself. One sets `"headers":{"Authorization":"Bearer token"}`, and a stdio example sets `"args":["--api-key","abc123"]` ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp)). Those strings are arguments of the `claude` process.

On Linux, `/proc/pid/cmdline` "holds the complete command line for the process" ([proc_pid_cmdline(5)](https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html)). That page does not say who may read the file, and it does not cover shell history. Neither the 2.1.327 changelog entry nor the MCP docs page, as fetched on 2026-11-23, names history or the process list as a leak path. This page claims neither. Check how your own shell and host expose a command line before you rely on the stdin route.

## The stdin form

The MCP docs give the form: "To pipe the JSON in, pass `-` in its place: `cat server.json | claude mcp add-json <name> -`. Run the command outside a Claude Code session. Requires Claude Code v2.1.327 or later" ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp)).

With `-`, the `claude` process has no token in its arguments. That follows from the sources above and is my inference, not a statement in either.

The command feeding the pipe can be anything that prints the JSON. A secret-store command that emits the whole server entry fits (inference; the docs show only `cat server.json`):

```bash
secret-store-cli get mcp/weather-api | claude mcp add-json weather-api -
```

`secret-store-cli` is a placeholder. The documented `cat server.json` form leaves the token in `server.json`, a file you then manage.

## Limits

- Run it in a terminal outside Claude Code. The pages as fetched on 2026-11-23 do not say why.
- The docs say it requires v2.1.327 or later.
- The token still lands in a config file. The docs list where each scope stores its configuration, and `add-json` writes the entry to the scope you pick (inference from the scope table below), so the token moves from the command into that file.

## Choose the scope

The MCP docs define three scopes ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp)):

| Scope | Stored in | Shared with team |
|-------|-----------|------------------|
| Local (default) | `~/.claude.json` | No |
| Project | `.mcp.json` in the project root | Yes, via version control |
| User | `~/.claude.json` | No |

The docs recommend local scope for "servers with credentials you don't want in version control". A literal token with `--scope project` would land in a file the docs say you check in (inference from the two statements). For a shared `.mcp.json`, the docs support `${VAR}` references in `command`, `args`, `env`, `url`, and `headers`, so each person supplies the token from their own environment.

## Example

A developer keeps the token in a secret store and adds a local-scope server with no token in any argument:

```bash
secret-store-cli get mcp/weather-api | claude mcp add-json weather-api -
claude mcp get weather-api
```

The first line runs in a terminal, not in a Claude Code session. `claude mcp get <name>` is the verify step the docs give after `add-json`.

## Key Takeaways

- `claude mcp add-json <name> -` reads the server JSON from stdin. It needs Claude Code 2.1.327 or later and runs outside a session.
- The changelog entry states the goal as keeping tokens off the command line. It names no specific leak path.
- Stdin moves the token out of the command and into the scope's config file. It does not remove the token from disk.
- Use local scope for a personal token, and `${VAR}` references in a project `.mcp.json` that the team shares.

## Related

- [Per-Server MCP Environment Scoping for Credential Isolation](mcp-server-credential-isolation.md) — which environment variables each MCP server receives
- [Secrets Management for AI Agents](secrets-management-for-agents.md) — injecting credentials so the agent never reads them as text
- [Credential-Free Subprocesses](credential-free-agent-subprocesses.md) — what Claude Code strips from tool environments
- [Scoped MCP Server Discovery](../tool-engineering/scoped-mcp-server-discovery.md) — how the three scopes resolve
