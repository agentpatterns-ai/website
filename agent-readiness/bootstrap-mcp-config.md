---
title: "Bootstrap MCP Config"
description: "Detect declared MCP servers, generate or refactor .mcp.json with per-server scope and allowlist, wire into harness settings, and validate against egress and least-privilege rules."
tags:
  - tool-agnostic
  - security
aliases:
  - generate mcp.json
  - scaffold MCP server config
  - MCP per-server scope
---

# Bootstrap MCP Config

> Detect declared MCP servers, generate or refactor `.mcp.json` with per-server scope and allowlist, wire into harness settings, validate.

!!! info "Harness assumption"
    Templates target Claude Code's `.mcp.json` and `.claude/settings.json` per-server allowlist. Cursor, Copilot, and any other MCP-aware harness use parallel mechanisms — translate the per-server scope and allowlist to your tool's equivalents. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip this runbook if the agent talks only to the local filesystem and the user. MCP is for connections to external services — issue trackers, databases, hosted APIs, browser automation. A purely local agent has nothing to configure here.

MCP is the plumbing through which agents talk to external systems. A loose `.mcp.json` configuration grants every connected server the same broad surface; a tight one scopes each server to the minimum it needs and pairs cleanly with [`bootstrap-egress-policy`](bootstrap-egress-policy.md) and [`bootstrap-permissions-allowlist`](bootstrap-permissions-allowlist.md). Sources: [MCP protocol](../standards/mcp-protocol.md), [MCP server design](../tool-engineering/mcp-server-design.md).

## Step 1 — Detect Current State

```bash
# Existing MCP config
find . -maxdepth 8 \( -name "mcp.json" -o -name ".mcp.json" \) ! -path "*/node_modules/*" 2>/dev/null
test -f .claude/settings.json && jq '.mcpServers // empty' .claude/settings.json

# Servers reachable from this project (transcript signal)
find ~/.claude/projects -name "*.jsonl" 2>/dev/null \
  | xargs grep -hoE '"name":"mcp__[a-z_]+__[a-z_]+"' 2>/dev/null \
  | sort -u | head -20
```

Decision rules:

- **No `.mcp.json` and no servers in `settings.json`** → ask which servers the project should connect to; do not invent a list
- **Existing config** → audit; merge new servers, never silently remove configured ones
- **Servers in `settings.json` but no `.mcp.json`** → migrate to `.mcp.json` (committed, versioned) so the team shares the same surface

## Step 2 — Categorize Each Server

For each server the project uses or intends to use:

| Server | Purpose | Egress? | Read scope | Write scope |
|--------|---------|:-------:|------------|-------------|
| `filesystem` | local repo operations | no | repo only | repo only |
| `github` | issues, PRs, repo metadata | yes | this repo + listed | this repo only |
| `linear` | issue tracker | yes | configured team | configured team |
| `slack` | notifications | yes (egress only) | none | configured channels |
| `puppeteer` / browser | web fetch | yes (broad) | n/a | n/a |
| `<custom>` | <internal> | depends | depends | depends |

The categorization decides scope: a server with no egress (filesystem) needs no allowlist; a broad-egress server (browser) needs decomposition or denial.

## Step 3 — Generate `.mcp.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "linear": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-linear"],
      "env": {
        "LINEAR_API_KEY": "${LINEAR_API_KEY}"
      }
    }
  }
}
```

Generation rules:

1. **Secrets via env-var substitution** (`${VAR_NAME}`), never literal — the literal value would be committed
2. **Command is the published entry point** — do not embed local paths that won't resolve on a teammate's machine
3. **Args are minimal** — pass only what the server needs; extra flags become surface
4. **No server gets `"env": {"*": true}`** or equivalent — explicit env list only
5. **Each server is in its own block** — never combine into a single proxy server unless the project owns the proxy

## Step 4 — Configure Per-Server Tool Allowlist

In `.claude/settings.json`, restrict the tool surface per server:

```json
{
  "permissions": {
    "allow": [
      "mcp__filesystem__*",
      "mcp__github__issue_read",
      "mcp__github__pull_request_read",
      "mcp__github__add_issue_comment",
      "mcp__linear__list_issues",
      "mcp__linear__get_issue"
    ],
    "ask": [
      "mcp__github__create_*",
      "mcp__github__merge_*",
      "mcp__linear__create_*",
      "mcp__linear__update_*"
    ],
    "deny": [
      "mcp__github__delete_*",
      "mcp__github__push_files",
      "mcp__github__create_repository",
      "mcp__github__fork_repository"
    ]
  }
}
```

Rules:

1. **Read tools default to allow** — agents need to gather context
2. **Create / update tools default to ask** — visible to others, hard to reverse
3. **Delete tools default to deny** — destructive; require explicit re-allow per task
4. **Repo-level operations** (create_repository, fork) default to deny — far broader scope than per-issue work

## Step 5 — Restrict Server Egress

For servers that fetch from the network (browser, web-fetch, custom HTTP), pair this runbook with [`bootstrap-egress-policy`](bootstrap-egress-policy.md):

- The MCP server's own egress is governed by the server, not by `.claude/settings.json` Bash rules
- For local-launched servers, restrict egress at the OS level if needed (firewall rules; `iptables` for self-hosted CI runners)
- For broad-egress browser servers, consider whether decomposition (a separate principal that owns just the browser tool) is cheaper than network restriction

## Step 6 — Validate

```bash
# JSON parses
jq empty .mcp.json || { echo "FATAL: .mcp.json malformed"; exit 1; }

# No literal secrets
jq -r '.mcpServers[].env | to_entries[] | .value' .mcp.json | while read v; do
  if [[ ! "$v" =~ ^\$\{ ]] && [[ "$v" =~ ^(sk-|ghp_|xoxb-|AKIA|gho_) ]]; then
    echo "FAIL: literal secret in .mcp.json env"
  fi
done

# Required env vars are set in the agent's environment
jq -r '.mcpServers[].env | to_entries[] | .value' .mcp.json \
  | grep -oE '\$\{[A-Z_]+\}' | tr -d '${}' | sort -u | while read var; do
  [[ -n "${!var:-}" ]] || echo "WARN: $var unset in current env (agent may fail)"
done

# Per-server tool allowlist exists
for server in $(jq -r '.mcpServers | keys[]' .mcp.json); do
  jq -e --arg s "$server" '.permissions.allow[] | select(test("mcp__" + $s))' \
    .claude/settings.json >/dev/null \
    || echo "FAIL: no tool allowlist for server $server"
done
```

Then run [`audit-tool-descriptions`](audit-tool-descriptions.md) and [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) over the new surface.

## Step 7 — Document

In `AGENTS.md`:

```markdown
## MCP servers

Configured in `.mcp.json`. Per-server tool scopes in `.claude/settings.json`.
Required env vars: `GITHUB_TOKEN`, `LINEAR_API_KEY` — set via your shell, direnv, dotenvx, doppler, 1Password CLI, or your project's existing secret-management mechanism.
```

## Idempotency

Re-running adds new servers; never silently removes configured ones. Tool allowlist entries are added to the union, not the intersection.

## Output Schema

```markdown
# Bootstrap MCP Config — <repo>

| Action | File | Notes |
|--------|------|-------|
| Created/Modified | .mcp.json | <n> servers |
| Modified | .claude/settings.json | per-server allow: <n>, ask: <n>, deny: <n> |
| Modified | AGENTS.md | added MCP-servers pointer |

Servers configured: <names>
Required env: <vars>
Validation: <pass/fail>
```

## Related

- [MCP Protocol Standard](../standards/mcp-protocol.md)
- [MCP Server Design](../tool-engineering/mcp-server-design.md)
- [Bootstrap Permissions Allowlist](bootstrap-permissions-allowlist.md)
- [Bootstrap Egress Policy](bootstrap-egress-policy.md)
- [Audit Tool Descriptions](audit-tool-descriptions.md)
- [Audit Permissions and Blast Radius](audit-permissions-blast-radius.md)
