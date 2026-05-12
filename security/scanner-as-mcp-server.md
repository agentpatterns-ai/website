---
title: "Scanner-as-MCP-Server: Secret and Dependency Scans as Typed Agent Tools"
description: "Ship the security scanner itself as an MCP server so agents invoke typed scans pre-commit, with structured findings the model reasons over directly — distinct from CI-step and wrapped-CLI delivery shapes."
aliases:
  - scanner as MCP server
  - MCP-mediated security scanning
  - in-loop security scanning
tags:
  - security
  - tool-engineering
  - tool-agnostic
---

# Scanner-as-MCP-Server: Secret and Dependency Scans as Typed Agent Tools

> Ship the security scanner as an MCP server so the agent invokes typed scans pre-commit and reasons over structured findings — useful in the IDE loop, useless if the agent decides not to call it.

GitHub generalised this delivery shape on 2026-05-05: secret scanning via the GitHub MCP Server is generally available, and dependency scanning entered public preview the same day ([Secret scanning GA changelog](https://github.blog/changelog/2026-05-05-secret-scanning-with-github-mcp-server-is-now-generally-available/), [Dependency scanning preview changelog](https://github.blog/changelog/2026-05-05-dependency-scanning-with-github-mcp-server-is-in-public-preview/)). The scanners themselves existed in CI for years; what is new is the delivery shape — the scanner ships as an MCP server, and the agent calls `list_secret_scanning_alerts` or the dependency-scan equivalent as a typed tool, parsing the JSON response in-loop.

## Three Delivery Shapes

A scanner reaches developer code through one of three shapes; the choice changes who decides when to scan, when findings surface, and how findings are consumed.

| Shape | When the scan runs | Who decides | Output consumer | Bypass surface |
|---|---|---|---|---|
| **CI step** | `push`, `pull_request` event | Pipeline config | Reviewer, status check | Cannot be skipped at the gate |
| **Scheduled job** | Cron, cadence, advisory feed | Operator | Triage channel, issue tracker | Latency window for new code |
| **MCP server** | Agent decides, in-loop | Agent + user prompt | Agent reasoning step | Agent can choose not to call |

The first two are covered by [Always-On Agentic PR Security Review](always-on-pr-security-review.md). The three shapes compose.

## What "Scanner-as-MCP-Server" Means Concretely

The GitHub MCP Server exposes the security scanners as named toolsets, each containing typed tools the agent invokes by name ([github/github-mcp-server README](https://github.com/github/github-mcp-server/blob/main/README.md)):

- `secret_protection` — `get_secret_scanning_alert`, `list_secret_scanning_alerts`
- `dependabot` — `get_dependabot_alert`, `list_dependabot_alerts`
- `code_security` — `get_code_scanning_alert`, `list_code_scanning_alerts`
- `security_advisories` — `list_global_security_advisories`, `list_repository_security_advisories`

Toolsets are loaded per session, not eagerly. In Copilot CLI: `copilot --add-github-mcp-toolset dependabot`. In VS Code: header `"X-MCP-Toolsets": "dependabot"` or the selector in Copilot Chat ([Dependency scanning preview changelog](https://github.blog/changelog/2026-05-05-dependency-scanning-with-github-mcp-server-is-in-public-preview/)). This makes the scanner a JIT-loaded surface — see [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](../tool-engineering/mcp-eager-vs-jit-loading.md) for the cost rubric.

## Why Structured Output Is the Pivot

Agents that scrape stderr or parse CLI logs spend tokens on parsing; agents that receive typed JSON spend tokens on reasoning. The GitHub MCP Server returns "structured results with affected packages, severity, and recommended fixed versions" ([Dependency scanning preview changelog](https://github.blog/changelog/2026-05-05-dependency-scanning-with-github-mcp-server-is-in-public-preview/)) and "structured results with the locations of and details on any secrets found" ([Original preview changelog](https://github.blog/changelog/2026-03-17-secret-scanning-in-ai-coding-agents-via-the-github-mcp-server/)). The agent can group findings by severity, summarise to the user, or auto-fix a Dependabot advisory by editing `package.json` to the recommended version — none of which require log parsing.

This mechanism is the same one behind [Typed Schemas at Agent Boundaries](../tool-engineering/typed-schemas-at-agent-boundaries.md): machine-readable output keeps the model in the reasoning step and out of the parsing step.

## What MCP-Mediated Scanning Inherits

The GA announcement notes that "secret scanning tools in the MCP server now honor your existing push protection customization" ([Secret scanning GA changelog](https://github.blog/changelog/2026-05-05-secret-scanning-with-github-mcp-server-is-now-generally-available/)). The scanner's existing rule corpus, custom patterns, and bypass workflows apply unchanged; the MCP surface is a new front door, not a re-implementation of the engine.

## Failure Modes

Five conditions invert the pattern's value:

1. **Agent skips the scan.** Tools the agent decides to call do not enforce anything. Without a system-prompt directive or user prompt naming the scan, no scan runs. CI gates remove this agency by design.
2. **Repo lacks the upstream signal.** Secret scanning requires GitHub Secret Protection enabled; dependency scanning requires Dependabot alerts ([Secret scanning GA changelog](https://github.blog/changelog/2026-05-05-secret-scanning-with-github-mcp-server-is-now-generally-available/), [Dependency scanning preview changelog](https://github.blog/changelog/2026-05-05-dependency-scanning-with-github-mcp-server-is-in-public-preview/)). On repos without these, the toolset is callable but returns empty, and the agent reports a clean result.
3. **Scanner principal closes the lethal trifecta.** A scanner MCP server with repo read, a write-egress tool (ticket system, Slack, external triage), and exposure to untrusted content (PR descriptions, issue bodies, fetched log snippets) holds all three legs of the trifecta on the scanner principal itself. Run the [Lethal Trifecta Audit](../agent-readiness/audit-lethal-trifecta.md) before merge.
4. **Schema mutability.** MCP tool schemas can change between sessions, and most clients do not warn. An agent that parsed `severity` yesterday can receive `note` today and either fail silently or invent a severity ([DZone: Why Security Scanning Isn't Enough for MCP Servers](https://dzone.com/articles/why-security-scanning-isnt-enough-for-mcp-servers)).
5. **Latency on the developer path.** Each in-loop scan adds MCP round-trip seconds. Scheduled jobs cover the whole repo without per-call cost; agent-invoked scans cover only what the agent thought to scan.

## Compose, Don't Replace

The MCP-mediated scanner does not replace the CI step. Use the three shapes for what each does well:

- **CI step** — pre-merge gate, breadth, cannot be skipped by an agent that chose not to scan.
- **Scheduled job** — resident-risk coverage for files no PR touches.
- **MCP server** — IDE-time signal, pre-commit fix loop, structured output the agent acts on directly.

The MCP shape shortens the feedback loop *before* code reaches the CI gate; it does not remove the gate.

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
- The pattern is qualified by five failure modes: agent skips the scan, upstream signal disabled, scanner principal closes the trifecta, schema drift, and added developer-path latency.
- Compose with CI-step and scheduled-job delivery; the MCP shape shortens the feedback loop before the merge gate, it does not replace the gate.

## Related

- [Always-On Agentic PR Security Review](always-on-pr-security-review.md)
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md)
- [Lethal Trifecta Audit](../agent-readiness/audit-lethal-trifecta.md)
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](../tool-engineering/mcp-eager-vs-jit-loading.md)
- [Typed Schemas at Agent Boundaries](../tool-engineering/typed-schemas-at-agent-boundaries.md)
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md)
