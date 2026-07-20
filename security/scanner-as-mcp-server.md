---
title: "Scanner-as-MCP-Server: Secret and Dependency Scans as Typed Agent Tools"
term: "Scanner-as-MCP-Server"
description: "Ship the security scanner itself as an MCP server so agents invoke typed scans pre-commit, with structured findings the model reasons over directly — distinct from CI-step and wrapped-CLI delivery shapes."
aliases:
  - scanner as MCP server
  - MCP-mediated security scanning
  - in-loop security scanning
tags:
  - security
  - tool-engineering
  - tool-agnostic
  - mcp
last_reviewed: 2026-06-12
maturity: adopted
---

# Scanner-as-MCP-Server: Secret and Dependency Scans as Typed Agent Tools

> Ship the security scanner as an MCP server so the agent invokes typed scans in-loop and reasons over structured findings — distinct from CI-step delivery.

On 2026-05-05 GitHub MCP Server secret scanning went GA and dependency scanning entered preview ([Secret scanning GA](https://github.blog/changelog/2026-05-05-secret-scanning-with-github-mcp-server-is-now-generally-available/), [Dependency preview](https://github.blog/changelog/2026-05-05-dependency-scanning-with-github-mcp-server-is-in-public-preview/)). The scanners are not new. The delivery shape is: the agent calls `list_secret_scanning_alerts` or the dependency equivalent as a typed tool and parses JSON in-loop.

## Three delivery shapes

A scanner reaches developer code through three shapes. The shape you pick changes who scans, when they scan, and who reads the findings.

| Shape | When the scan runs | Who decides | Output consumer | Bypass surface |
|---|---|---|---|---|
| CI step | `push`, `pull_request` event | Pipeline config | Reviewer, status check | Cannot be skipped at the gate |
| Scheduled job | Cron, cadence, advisory feed | Operator | Triage channel, issue tracker | Latency window for new code |
| MCP server | Agent decides, in-loop | Agent + user prompt | Agent reasoning step | Agent can choose not to call |

The first two are covered by [Always-On Agentic PR Security Review](always-on-pr-security-review.md). The three shapes compose.

## What scanner-as-MCP-server means concretely

The GitHub MCP Server exposes scanners as named toolsets, each containing typed tools the agent invokes by name ([github-mcp-server README](https://github.com/github/github-mcp-server/blob/main/README.md)):

- `secret_protection` — `get_secret_scanning_alert`, `list_secret_scanning_alerts`
- `dependabot` — `get_dependabot_alert`, `list_dependabot_alerts`
- `code_security` — `get_code_scanning_alert`, `list_code_scanning_alerts`
- `security_advisories` — `list_global_security_advisories`, `list_repository_security_advisories`

Toolsets load per session — in Copilot CLI via `copilot --add-github-mcp-toolset dependabot`, in VS Code via header `"X-MCP-Toolsets": "dependabot"` or the Copilot Chat selector ([Dependency preview](https://github.blog/changelog/2026-05-05-dependency-scanning-with-github-mcp-server-is-in-public-preview/)). That makes the scanner a JIT-loaded surface — see [MCP alwaysLoad cost rubric](../tool-engineering/mcp-eager-vs-jit-loading.md).

## Why structured output is the pivot

Agents that parse CLI logs spend tokens on parsing. Agents that receive typed JSON spend them on reasoning. The MCP Server returns "structured results with affected packages, severity, and recommended fixed versions" ([Dependency preview](https://github.blog/changelog/2026-05-05-dependency-scanning-with-github-mcp-server-is-in-public-preview/)) and "the locations of and details on any secrets found" ([Original preview](https://github.blog/changelog/2026-03-17-secret-scanning-in-ai-coding-agents-via-the-github-mcp-server/)). The agent can group by severity, summarize, or auto-fix a Dependabot advisory by editing `package.json` — no log parsing required. This uses the same mechanism as [Typed Schemas at Agent Boundaries](../patterns/multi-agent/typed-schemas-at-agent-boundaries.md).

## What MCP-mediated scanning inherits

The MCP server "honor[s] your existing push protection customization" ([GA changelog](https://github.blog/changelog/2026-05-05-secret-scanning-with-github-mcp-server-is-now-generally-available/)) — the rule corpus, custom patterns, and bypass workflows apply unchanged. The MCP surface is a new front door, not a new engine.

## Failure modes

Six conditions invert the pattern's value:

1. Agent skips the scan. Tools the agent decides to call do not enforce. Without a system-prompt directive or a user prompt that names the scan, no scan runs. [CI gates](always-on-pr-security-review.md) remove that agency by design.
2. Repo lacks the upstream signal. Secret scanning requires Secret Protection enabled. Dependency scanning requires Dependabot alerts. Without them the toolset returns empty and the agent reports a clean result.
3. Scanner principal closes the lethal trifecta. A scanner MCP server with repo read, a write-egress tool, and exposure to untrusted content (PR bodies, log snippets) holds all three legs on the scanner principal. Audit for trifecta closure before merge.
4. Schema mutability. MCP tool schemas can change between sessions, and most clients do not warn. An agent that parsed `severity` yesterday can receive `note` today, then fail silently or invent a value ([DZone](https://dzone.com/articles/why-security-scanning-isnt-enough-for-mcp-servers)).
5. Latency on the developer path. Each in-loop scan adds round-trip seconds. Scheduled jobs cover the whole repo without per-call cost, while agent-invoked scans cover only what the agent thought to scan.
6. Findings are ephemeral, not a system of record. MCP scan results live in the agent's chat for the session only — they do not persist as alerts and do not appear in the Security tab or the REST/GraphQL alert APIs ([GitHub Docs](https://docs.github.com/en/code-security/how-tos/use-ghas-with-ai-coding-agents/scan-for-secrets-with-github-mcp-server)). Treat the MCP shape as a pre-commit safety check, not the audit trail. SIEM ingestion, triage queues, and compliance evidence still rely on the alert-based scanners.

## Compose, do not replace

The MCP scanner does not replace the CI step. Use each shape for what it does well:

- CI step — pre-merge gate that an agent cannot skip by choosing not to scan.
- Scheduled job — resident-risk coverage for files no PR touches.
- MCP server — IDE-time signal and pre-commit fix loop on structured output.

The MCP shape shortens the feedback loop before code reaches the CI gate — it does not replace it.

## Example

Wiring the GitHub MCP Server's `dependabot` toolset in Copilot CLI for a single session:

```bash
# Enable the dependabot toolset for this session
copilot --add-github-mcp-toolset dependabot

# Agent prompt
"Scan the dependencies I added on this branch for known vulnerabilities and
 tell me which versions to upgrade to before I commit."
```

The agent calls `list_dependabot_alerts` against the current repository, receives JSON with `package`, `severity`, and `fixed_version` fields per affected dependency, groups by severity in its reply, and offers to edit `package.json` to the recommended versions. The CI `pull_request` scan still runs at merge; the MCP call caught the issue minutes before push ([Dependency scanning preview changelog](https://github.blog/changelog/2026-05-05-dependency-scanning-with-github-mcp-server-is-in-public-preview/)).

## Key Takeaways

- Scanner-as-MCP-server is a delivery shape, not a new scanner: the engine, rules, and bypass policy are unchanged; the agent gets a typed tool surface in-loop.
- The GitHub MCP Server names this concretely with the `secret_protection`, `dependabot`, `code_security`, and `security_advisories` toolsets, each loaded per session.
- The structured-output mechanism keeps the agent in the reasoning step and out of log-parsing — the page's primary value over CLI-wrapped scanners.
- The pattern is qualified by six failure modes: agent skips the scan, upstream signal disabled, scanner principal closes the trifecta, schema drift, developer-path latency, and ephemeral findings that do not persist as alerts.
- Compose with CI-step and scheduled-job delivery; the MCP shape shortens the feedback loop before the merge gate, it does not replace the gate.

## Related

- [Always-On Agentic PR Security Review](always-on-pr-security-review.md)
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md)
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](../tool-engineering/mcp-eager-vs-jit-loading.md)
- [Typed Schemas at Agent Boundaries](../patterns/multi-agent/typed-schemas-at-agent-boundaries.md)
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md)
