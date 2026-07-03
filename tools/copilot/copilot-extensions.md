---
title: "GitHub Copilot Extensions for AI Agent Development"
description: "Deprecated. GitHub App-based Copilot Extensions were sunset on November 10, 2025. Build MCP servers instead. Retained as historical reference."
tags:
  - agent-design
  - copilot
  - mcp
applies_to: "copilot@1.x"
last_reviewed: 2026-06-13
status: archived
---

# GitHub Copilot Extensions

> Deprecated. GitHub App-based Copilot Extensions were [sunset on November 10, 2025](https://github.blog/changelog/2025-09-24-deprecate-github-copilot-extensions-github-apps/). Build [MCP servers](mcp-integration.md) instead. This page is retained as historical reference.

> GitHub Copilot Extensions let you integrate external tools and services into Copilot Chat.

---

## Extension types

Copilot Extensions come in two forms: [agents and skillsets](https://github.blog/changelog/2024-11-19-build-copilot-extensions-faster-with-skillsets/). An extension cannot be both.

### Skillsets

Skillsets are lightweight integrations. You define [up to 5 API endpoints](https://github.blog/changelog/2024-11-19-build-copilot-extensions-faster-with-skillsets/) and let Copilot handle all AI interactions. Copilot analyzes the user query, selects the right skill, builds the API request from your JSON schema, calls your endpoint, and formats the response.

Skillsets need no LLM logic on your side. You provide endpoints and schemas; Copilot handles routing, prompt crafting, function evaluation, and response generation. Copilot's function-calling mechanism maps user intent to your JSON schema at inference time, so your endpoint receives a structured, schema-validated payload without prompt engineering. Use skillsets for straightforward integrations like data retrieval and basic actions.

### Agents

Copilot agent extensions give you full control over user interactions and custom logic. The agent receives the user message, processes it (sometimes by calling its own LLM), and returns a response. Use agents for complex workflows that need custom prompt crafting, specific LLM models, or multi-step reasoning.

## Authentication

Copilot Extensions use [OpenID Connect (OIDC)](https://github.blog/changelog/2025-02-19-announcing-the-general-availability-of-github-copilot-extensions/) for authentication, replacing the earlier X-GitHub-Token model. OIDC issues short-lived signed JWTs that your extension verifies against GitHub's [published JWKS](https://docs.github.com/en/copilot/how-tos/use-copilot-extensions/set-up-oidc), which [reduces API round trips and lowers latency](https://github.blog/changelog/2025-02-19-announcing-the-general-availability-of-github-copilot-extensions/) compared to the earlier token exchange.

You build extensions as GitHub Apps, inheriting the GitHub Apps permission model for repository and organization access.

## Distribution

Extensions can be [public or private](https://github.blog/changelog/2025-02-19-announcing-the-general-availability-of-github-copilot-extensions/):

- Public: listed on GitHub Marketplace, available to any Copilot subscriber
- Private: scoped to an organization, not publicly discoverable

Building extensions requires a [Free, Team, or supported Enterprise Cloud organization](https://github.blog/changelog/2024-11-19-build-copilot-extensions-faster-with-skillsets/).

## Constraints

| Constraint | Detail |
|-----------|--------|
| Max skills per skillset | 5 endpoints |
| Skillset scope | GitHub App-based extensions only |
| Mutual exclusivity | One extension cannot be both a skillset and an agent |
| Copilot subscription | Required for all users |
| Platform support | VS Code, Visual Studio, JetBrains IDEs, GitHub.com |

## When to use what

| Approach | Best for |
|----------|----------|
| Skillset | Data retrieval, simple API calls, no custom LLM logic needed |
| Agent extension | Complex workflows, custom prompts, multi-turn conversations |
| MCP server | Cross-tool compatibility (works beyond Copilot), tool-level integrations |
| Local agent (`.agent.md`) | Team-specific workflows within a repository, no external hosting |

Skillsets and agent extensions run as hosted services. MCP servers and local agents run alongside the editor. Choose hosted extensions when you need marketplace distribution or centralized deployment. Choose local approaches when you need portability and no infrastructure.

## Key Takeaways

- Skillsets require minimal setup: define endpoints and schemas, and Copilot handles all AI interaction logic.
- Agent extensions give full control over LLM interaction and response generation.
- OIDC authentication replaces the earlier X-GitHub-Token model with short-lived signed JWTs verified against GitHub's JWKS.
- An extension is either a skillset or an agent — not both.
- Use MCP servers instead when you need cross-tool compatibility beyond the Copilot ecosystem.

## When this backfires

GitHub App-based Copilot Extensions sunset on November 10, 2025, so these patterns no longer apply to new development. For active development, use MCP servers.

For historical context on failure conditions:

- Skillset endpoint limits: the 5-endpoint cap per skillset forces you to split related functionality across multiple extensions, which complicates deployment and version management.
- OIDC dependency: your extension backend must validate tokens on every request. Misconfigured token validation fails silently under load, producing 401s that look like Copilot being unresponsive.
- Agent extension latency: agent extensions that call their own LLMs add one full LLM round-trip on top of Copilot's own inference, so multi-turn agent conversations run noticeably slower than native Copilot responses.
- GitHub App permission scope creep: extensions inherit the GitHub Apps permission model. Requesting broad repository permissions to support power users creates friction for standard users, who see an overly permissive install prompt.
- Marketplace lock-in: public extensions distributed through GitHub Marketplace are tied to GitHub's extension infrastructure, so cross-tool portability needs a full rewrite as MCP servers.

## Related

- [Agent Mode](agent-mode.md)
- [Coding Agent](coding-agent.md)
- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
- [MCP Integration](mcp-integration.md)
- [Copilot Extensions to MCP Migration](../../tool-engineering/copilot-extensions-to-mcp-migration.md)
