---
title: "GitHub Copilot Extensions for AI Agent Development"
description: "Deprecated. GitHub App-based Copilot Extensions were sunset on November 10, 2025. Build MCP servers instead. This page is retained as historical reference"
tags:
  - agent-design
  - copilot
---

# GitHub Copilot Extensions

> **Deprecated.** GitHub App-based Copilot Extensions were [sunset on November 10, 2025](https://github.blog/changelog/2025-09-24-deprecate-github-copilot-extensions-github-apps/). Build [MCP servers](mcp-integration.md) instead. This page is retained as historical reference.

> GitHub Copilot Extensions let you integrate external tools and services into Copilot Chat.

---

## Extension Types

Copilot Extensions come in two forms: [agents and skillsets](https://github.blog/changelog/2024-11-19-build-copilot-extensions-faster-with-skillsets/). An extension cannot be both simultaneously.

### Skillsets

Skillsets are lightweight integrations where you define [up to 5 API endpoints](https://github.blog/changelog/2024-11-19-build-copilot-extensions-faster-with-skillsets/) and let Copilot handle all AI interactions. Copilot analyzes the user query, selects the appropriate skill, structures the API request using your JSON schema, calls your endpoint, and formats the response.

Skillsets require no LLM logic on your side. You provide endpoints and schemas; Copilot handles routing, prompt crafting, function evaluation, and response generation. Use skillsets for straightforward integrations like data retrieval and basic actions.

### Agents

Agent extensions give you full control over user interactions and custom logic. The agent receives the user message, processes it (potentially calling its own LLM), and returns a response. Use agents for complex workflows requiring custom prompt crafting, specific LLM models, or multi-step reasoning.

## Authentication

Copilot Extensions use [OpenID Connect (OIDC)](https://github.blog/changelog/2025-02-19-announcing-the-general-availability-of-github-copilot-extensions/) for authentication, replacing the earlier X-GitHub-Token model. OIDC provides authentication tokens that reduce API round trips and eliminate per-request token verification.

You build extensions as GitHub Apps, inheriting the GitHub Apps permission model for repository and organization access.

## Distribution

Extensions can be [public or private](https://github.blog/changelog/2025-02-19-announcing-the-general-availability-of-github-copilot-extensions/):

- **Public**: Listed on GitHub Marketplace, available to any Copilot subscriber
- **Private**: Scoped to an organization, not publicly discoverable

Building extensions requires a Free, Team, or supported Enterprise Cloud organization [unverified].

## Constraints

| Constraint | Detail |
|-----------|--------|
| Max skills per skillset | 5 endpoints |
| Skillset scope | GitHub App-based extensions only |
| Mutual exclusivity | One extension cannot be both a skillset and an agent |
| Copilot subscription | Required for all users |
| Platform support | VS Code, Visual Studio, JetBrains IDEs, GitHub.com |

## When to Use What

| Approach | Best For |
|----------|----------|
| Skillset | Data retrieval, simple API calls, no custom LLM logic needed |
| Agent extension | Complex workflows, custom prompts, multi-turn conversations |
| MCP server | Cross-tool compatibility (works beyond Copilot), tool-level integrations |
| Local agent (`.agent.md`) | Team-specific workflows within a repository, no external hosting |

Skillsets and agent extensions run as hosted services. MCP servers and local agents run alongside the editor. Choose hosted extensions when you need marketplace distribution or centralized deployment; choose local approaches when portability and zero-infrastructure are priorities.

## Key Takeaways

- Skillsets require minimal setup: define endpoints and schemas, and Copilot handles all AI interaction logic.
- Agent extensions give full control over LLM interaction and response generation.
- OIDC authentication replaces the earlier token model with OIDC-based tokens.
- An extension is either a skillset or an agent — not both.
- Use MCP servers instead when you need cross-tool compatibility beyond the Copilot ecosystem.

## Unverified Claims

- Building extensions requires a Free, Team, or supported Enterprise Cloud organization [unverified]

## Related

- [Agent Mode](agent-mode.md)
- [Coding Agent](coding-agent.md)
- [Custom Agents, Skills & Plugins](custom-agents-skills.md)
- [MCP Integration](mcp-integration.md)
- [Copilot Extensions to MCP Migration](../../tool-engineering/copilot-extensions-to-mcp-migration.md)
