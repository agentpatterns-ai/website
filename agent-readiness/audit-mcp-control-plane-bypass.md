---
title: "Audit MCP Control-Plane Bypass"
description: "Locate every off-protocol egress path an agent can take — shell out to curl, raw socket, DB driver, headless browser, in-thread side-channel — and validate that the project's MCP control plane sees them or that they are blocked at a lower layer."
tags:
  - tool-agnostic
  - security
  - observability
aliases:
  - off-protocol egress audit
  - mcp gateway bypass audit
  - agent egress blind spot audit
---

Packaged as: `.claude/skills/agent-readiness-audit-mcp-control-plane-bypass/`

# Audit MCP Control-Plane Bypass

> Locate every off-protocol egress path the agent can take — shell, raw HTTP, DB driver, headless browser, in-thread side-channel — and confirm each one is observed or blocked.

!!! info "Harness assumption"
    The runbook applies whether or not a runtime control plane (AWS AgentCore, Microsoft Agent Governance Toolkit, Red Hat MCP Gateway) is deployed. If no plane exists, the audit reports the off-protocol surface as the egress attack surface and points at the [`bootstrap-egress-policy`](bootstrap-egress-policy.md) and [`bootstrap-url-fetch-gate`](bootstrap-url-fetch-gate.md) compensations. If a plane is deployed, the audit measures coverage against it. See [Assumptions](index.md#assumptions).

[MCP Runtime Control Plane](../security/mcp-runtime-control-plane.md) §When This Backfires names two failure modes a control plane cannot fix on its own: **off-protocol actions bypass the plane** (shell, direct HTTP, DB drivers, headless browsers are invisible to the gateway) and **clients can skip the plane** (any agent runtime not wired through the gateway reaches servers unchecked). [Why MCP Gateways Are a Bad Idea](https://securityboulevard.com/2026/03/why-mcp-gateways-are-a-bad-idea-and-what-to-do-instead/) and [Strata: Prevent MCP Bypass](https://www.strata.io/blog/agentic-identity/prevent-mcp-bypass/) document both. This audit inventories the bypass paths and emits per-path findings.

## Step 1 — Inventory the Declared MCP Surface

```bash
# Servers the agent is wired to talk to
test -f .mcp.json && jq -r '.mcpServers | to_entries[] | "\(.key) \(.value.command // .value.url)"' .mcp.json

# Per-server tool list (if cached)
find .claude -name "tool-list*.json" 2>/dev/null

# Control plane config (Cedar / OPA / native)
find . -maxdepth 3 -type f \( -name "*.cedar" -o -name "*.rego" -o -name "policies/*.yaml" \) 2>/dev/null
```

This is the **observed surface**. Everything else in the agent's reach that doesn't pass through MCP is a bypass candidate.

## Step 2 — Detect Shell Egress

Shell commands are the primary off-protocol path documented by [Security Boulevard](https://securityboulevard.com/2026/03/why-mcp-gateways-are-a-bad-idea-and-what-to-do-instead/) — shell, direct HTTP, DB drivers, and headless browsers are invisible to MCP gateways.

```bash
# Bash tool allow-list — everything in here is potential off-protocol egress
test -f .claude/settings.json && jq -r '.permissions.allow[]? | select(test("Bash"))' .claude/settings.json

# Skill bodies that pipe into curl / wget / nc / ssh
grep -rEn "curl |wget |nc -|nc\(|ssh |scp |rsync " .claude/skills/*/SKILL.md .claude/commands/*.md 2>/dev/null

# Subprocess calls inside agent-callable code
grep -rEn "subprocess\.(run|Popen|call)|os\.system\(|exec\(" \
  scripts/ tools/ src/ 2>/dev/null | grep -vE "test_|#"
```

Decision rules:

- **`Bash(curl:*)` or unrestricted `Bash` allowed** → high. Direct HTTP from shell bypasses the control plane.
- **Skill or command pipes into network CLI** → medium. Each one is a documented bypass candidate.
- **Subprocess shells out to a network binary** → medium-to-high depending on argument injection surface (cross-reference [Trail of Bits §Prompt injection to RCE](https://blog.trailofbits.com/2025/10/22/prompt-injection-to-rce-in-ai-agents/)).

## Step 3 — Detect Raw HTTP Outside MCP

```bash
# Direct HTTP libraries used by agent-callable code
grep -rEn "httpx|requests\.|fetch\(|axios|node-fetch|urllib" \
  scripts/ tools/ src/ 2>/dev/null | grep -vE "test_|examples/|#"

# WebFetch / web_search uses outside the gated wrapper
grep -rEn "WebFetch|web_fetch|web_search" .claude/skills/*/SKILL.md .claude/agents/*.md 2>/dev/null
```

Each direct HTTP call from an agent-callable code path is a bypass — the gateway never sees it. Cross-reference [`bootstrap-url-fetch-gate`](bootstrap-url-fetch-gate.md) Step 1: every fetch site enumerated there must either route through the gated wrapper or be classified as not agent-reachable.

## Step 4 — Detect Database and Queue Drivers

```bash
# DB drivers used directly by agent-callable code
grep -rEn "psycopg|sqlalchemy|pymongo|redis\.|boto3|kafka|rabbitmq" \
  scripts/ tools/ src/ 2>/dev/null | grep -vE "test_|#"

# DB credentials in agent-readable files (cross-check audit-secrets-in-context)
find . -maxdepth 4 -type f \( -name ".env*" -o -name "config.*" \) -exec grep -l "PASSWORD\|SECRET\|TOKEN\|DSN" {} \; 2>/dev/null
```

DB drivers exfiltrate by side-channel: a `pg_notify` or `INSERT INTO public_table` call is data egress that no gateway sees. If the agent has DB credentials and an LLM-decision step can construct queries, this is in scope.

## Step 5 — Detect Headless Browser and Automation

```bash
grep -rEn "playwright|puppeteer|selenium|chromium|chromedriver" \
  scripts/ tools/ src/ .claude/skills/*/SKILL.md .mcp.json 2>/dev/null
```

Headless browsers are explicitly named in [Security Boulevard's bypass list](https://securityboulevard.com/2026/03/why-mcp-gateways-are-a-bad-idea-and-what-to-do-instead/). A Playwright session can fetch any URL, post any form, and exfiltrate via DOM events — none of which touch the MCP transport.

## Step 6 — Detect In-Thread Side-Channels

[In-Thread Side-Channel](../workflows/in-thread-side-channel.md) describes egress that uses the agent's own conversation as the channel — the agent emits a URL or string into its output that the user, an integration, or a downstream agent then fetches. The control plane sees no call.

```bash
# Agents whose output is rendered into a downstream pipeline
grep -rEn "render|markdown|html_template|message\.text" \
  .claude/agents/*.md .claude/skills/*/SKILL.md 2>/dev/null | head -30

# Hooks that consume agent output as data
test -f .claude/settings.json && jq '.hooks.PostToolUse[]?, .hooks.Stop[]?' .claude/settings.json
```

A finding here means the agent's output is itself an egress channel — the mitigation is per-pipeline (output filter, link rewriter, sanitiser) rather than a control-plane policy.

## Step 7 — Detect Skipped-Plane Clients

The second [MCP Runtime Control Plane §When This Backfires](../security/mcp-runtime-control-plane.md) failure mode: clients can skip the plane. Check that every agent runtime is wired through the gateway, not the server directly.

```bash
# .mcp.json entries pointing at the raw server URL instead of the gateway
test -f .mcp.json && jq -r '.mcpServers | to_entries[] | select(.value.url and (.value.url | test("gateway") | not)) | .key' .mcp.json

# Project-defined alternative MCP clients
find . -maxdepth 4 -type f -name "*.mcp.*" -o -name "shadow-mcp*" 2>/dev/null

# CI workflows or scripts spawning agents that talk to MCP without the gateway
grep -rEn "ANTHROPIC_API_KEY|claude-code|cursor.*mcp" .github/workflows/ 2>/dev/null
```

Findings:

- **Direct server URL in `.mcp.json`** → high if a gateway is supposed to be deployed; medium otherwise.
- **Shadow MCP client** → high. A second runtime invalidates the gateway's coverage promise.
- **CI agents that bypass the gateway** → high. The plane's value collapses to zero on partial coverage per [Strata's analysis](https://www.strata.io/blog/agentic-identity/prevent-mcp-bypass/).

## Step 8 — Validate Argument-Level Inspection on the Plane

Per [MCP Runtime Control Plane §When This Backfires](../security/mcp-runtime-control-plane.md) item 3, tool-name-only policies miss argument injection. Cross-check the policy corpus:

```bash
# Cedar / OPA policies that match only on tool name
grep -rEn "principal|action ==|resource ==" $(find . -name "*.cedar" -o -name "*.rego" 2>/dev/null) \
  | grep -v "arguments\."
```

A consequential tool (`shell.exec`, `deploy_service`, `send_email`) policed only by tool name is a finding — argument-level inspection per the [Trail of Bits demonstration](https://blog.trailofbits.com/2025/10/22/prompt-injection-to-rce-in-ai-agents/) is needed to catch injection-into-args.

## Step 9 — Emit Findings

```markdown
# Audit Report — MCP Control-Plane Bypass

## Bypass surface inventory
| Channel | Sites found | Gated by plane | Gated below | Ungated |
|---------|------------:|---------------:|------------:|--------:|
| Shell egress (curl/wget/nc) | <n> | n/a | <n> | <n> |
| Raw HTTP libraries | <n> | n/a | <n> | <n> |
| DB / queue drivers | <n> | n/a | <n> | <n> |
| Headless browser | <n> | n/a | <n> | <n> |
| In-thread side-channel | <n> | n/a | <n> | <n> |
| Skipped-plane clients | <n> | <n> | <n> | <n> |

## Per-path findings
| Channel | File | Line | Severity | Source page |
|---------|------|-----:|----------|-------------|

## Top fixes
| Severity | Finding | Suggested compensation |
|----------|---------|------------------------|
```

## Step 10 — Hand Off

For shell and raw-HTTP bypasses: pair with [`bootstrap-egress-policy`](bootstrap-egress-policy.md) (network-layer block) and [`bootstrap-url-fetch-gate`](bootstrap-url-fetch-gate.md) (URL-layer gate). For skipped-plane clients: route every runtime through the gateway and remove direct server URLs from `.mcp.json`. For argument-level gaps: extend the policy corpus to inspect `resource.arguments.*`. Pair this audit with [`audit-lethal-trifecta`](audit-lethal-trifecta.md) — a confirmed bypass on a private-data leg flips the trifecta finding to high.

## Idempotency

Read-only. Re-runs after compensation show fewer ungated channels and a smaller bypass inventory.

## Output Schema

```markdown
# Audit MCP Control-Plane Bypass — <repo>

| Plane present | Channels | Ungated | Skipped clients | Arg-only policies |
|:-------------:|---------:|--------:|----------------:|------------------:|
| y/n | <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually shell egress or a direct server URL in .mcp.json>
```

## Related

- [MCP Runtime Control Plane](../security/mcp-runtime-control-plane.md)
- [Agent Network Egress Policy](../security/agent-network-egress-policy.md)
- [URL Exfiltration Guard](../security/url-exfiltration-guard.md)
- [In-Thread Side-Channel](../workflows/in-thread-side-channel.md)
- [Bootstrap Egress Policy](bootstrap-egress-policy.md)
- [Bootstrap URL Fetch Gate](bootstrap-url-fetch-gate.md)
- [Audit Lethal Trifecta](audit-lethal-trifecta.md)
- [Audit Permissions Blast Radius](audit-permissions-blast-radius.md)
