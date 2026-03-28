---
title: "Copilot Spaces: Curated Context Collections for Grounding"
description: "Named context collections that aggregate repositories, code files, PRs, issues, notes, images, and uploads into a curated container that grounds Copilot"
tags:
  - context-engineering
  - copilot
---

# Copilot Spaces (Context Curation)

> Named context collections that aggregate repositories, code files, PRs, issues, notes, images, and uploads into a curated container that grounds Copilot responses.

## What Spaces Are

Copilot Spaces are manually curated context bundles. You assemble the reference material Copilot needs for a specific domain — repositories, individual files, pull requests, issues, free-text notes, images, and file uploads — and questions asked within that space are grounded in that curated content ([GitHub Docs](https://docs.github.com/en/copilot/concepts/context/spaces)) [unverified].

Spaces replaced the deprecated Knowledge Bases (sunset November 2025), adding support for richer content types beyond the repo-only model of their predecessor ([GitHub changelog, Knowledge Bases sunset](https://github.blog/changelog/2025-08-20-sunset-notice-copilot-knowledge-bases/)).

Accessed at `github.com/copilot/spaces` and through the remote GitHub MCP server in IDEs ([GitHub changelog, GA](https://github.blog/changelog/2025-09-24-copilot-spaces-is-now-generally-available/)).

## Where Spaces Fit in the Context Stack

Spaces occupy a specific layer in the context hierarchy — the manually curated reference layer between always-on instruction files and ad-hoc chat context:

| Layer | Mechanism | Persistence | Who Curates |
|-------|-----------|-------------|-------------|
| Behavioral rules | `.github/copilot-instructions.md` | Every interaction | Team (version-controlled) |
| Learned preferences | Copilot Memory | Autonomous, 28-day TTL [unverified] | Agent |
| **Reference material** | **Copilot Spaces** | **Persistent, manually curated** | **Human** |
| Ad-hoc context | Paste into chat / `@file` | Single interaction | Human |

Instruction files define *how* the agent behaves. Memory captures *what* the agent learns. Spaces provide *the reference material* the agent draws on. Each serves a different purpose, and they apply simultaneously when a space is active [unverified].

## Auto-Sync

GitHub-based sources (repositories, files, PRs, issues) auto-sync as they change — no manual re-import required. This keeps Copilot's understanding current as the codebase evolves ([GitHub Docs](https://docs.github.com/en/copilot/concepts/context/spaces), [GitHub changelog, GA](https://github.blog/changelog/2025-09-24-copilot-spaces-is-now-generally-available/)).

Non-GitHub content (uploaded files, free-text notes, images) is static and requires manual updates.

## Sharing and Access Control

**Organization-owned spaces** use tiered roles: admin, editor, viewer, or deny. Admins assign granular permissions to organization members ([GitHub Docs](https://docs.github.com/en/copilot/concepts/context/spaces)).

**Individual-owned spaces** support three visibility modes ([GitHub changelog, Dec 2025](https://github.blog/changelog/2025-12-01-copilot-spaces-public-spaces-and-code-view-support/)):

- **Private** — owner only
- **Shared** — specific GitHub users
- **Public** — view-only via direct link (not search-indexed)

Public spaces are available only for individual-owned spaces, not organization-owned ([GitHub changelog, Dec 2025](https://github.blog/changelog/2025-12-01-copilot-spaces-public-spaces-and-code-view-support/)).

RBAC is enforced across all sharing models: viewers only see sources they already have permission to access. No private or sensitive content is exposed through space sharing ([GitHub changelog, Dec 2025](https://github.blog/changelog/2025-12-01-copilot-spaces-public-spaces-and-code-view-support/)).

## Practical Configurations

**Feature development:** Assemble the feature branch code, relevant product spec, design notes, and related issues into a single space. Ask Copilot implementation questions grounded in the full feature context rather than individual files ([GitHub Docs, tutorials](https://docs.github.com/en/copilot/tutorials/speed-up-development-work)).

**Recurring tasks:** A telemetry events space containing event schemas, tracking code, and naming conventions. Reuse across sessions instead of re-explaining the tracking system each time ([GitHub Docs, tutorials](https://docs.github.com/en/copilot/tutorials/speed-up-development-work)).

**Cross-team onboarding:** Create spaces for auth systems, API references, or architecture guides. New developers get curated project context instead of scattered wiki links ([GitHub changelog, GA](https://github.blog/changelog/2025-09-24-copilot-spaces-is-now-generally-available/)). See [Team Onboarding for Agent Workflows](../../workflows/team-onboarding.md) for a structured onboarding sequence.

## Space vs. Instruction File vs. Memory

| Use case | Mechanism |
|----------|-----------|
| "Always use camelCase in this repo" | Instruction file |
| "The sessions table excludes first-party traffic" | Memory (learned from correction) |
| "Here are the API schemas, product spec, and auth docs for this feature" | Space |

Use instruction files for behavioral rules that apply to every interaction. Use memory for knowledge the agent discovers through work. Use spaces for curated reference material that a specific task or team needs.

## Billing

Spaces follow the Copilot Chat billing model with request-based consumption and model-specific multipliers ([GitHub changelog, GA](https://github.blog/changelog/2025-09-24-copilot-spaces-is-now-generally-available/)).

## Example

The following space configuration supports a recurring telemetry feature workflow. It assembles the event schemas, implementation code, and naming conventions a developer needs without re-explaining the tracking system in each session.

A space might include:

```
Sources in "Telemetry Events" space:
  - repo: acme-org/analytics-sdk          (auto-syncs)
  - file: acme-org/product/docs/event-naming-conventions.md  (auto-syncs)
  - issue: acme-org/product#284 — "Standardise session_start payload"  (auto-syncs)
  - upload: event-schema-v3.json          (static — update manually when schema changes)
  - note: "Exclude first-party traffic (internal IPs) from all session events"
```

When asking Copilot a question in this space — for example, "Add a `page_view` event following our naming conventions" — the response is grounded in the assembled schemas, conventions file, and the relevant issue discussion rather than generic knowledge.

Contrast with the wrong tool for each job:

```
# Wrong: putting reference material in the instruction file
# .github/copilot-instructions.md
Always use camelCase for event property names.          ← rule: correct for instruction file
Event schemas are defined in analytics-sdk/schemas/...  ← reference material: use a Space instead

# Right: instruction file for rules, Space for reference material
# .github/copilot-instructions.md
Always use camelCase for event property names.

# Copilot Space "Telemetry Events":
#   - analytics-sdk repo (auto-syncs as schemas update)
#   - event-naming-conventions.md
```

The instruction file handles the behavioral rule (camelCase). The space provides the schemas and docs the agent reads when implementing. Auto-sync on the repo source means the space stays current as `analytics-sdk` evolves — no manual re-import required.

## Key Takeaways

- Spaces are the manual curation layer in the context stack — reference material that sits between always-on instruction files and ephemeral chat context.
- GitHub-based sources auto-sync; uploaded content does not.
- RBAC is enforced even on public spaces — viewers only see sources they can already access.
- Use spaces for reference material (specs, schemas, docs), instruction files for behavioral rules, and memory for agent-discovered knowledge.

## Unverified Claims

- Spaces aggregate repositories, code files, PRs, issues, notes, images, and uploads into a curated container that grounds Copilot responses [unverified]
- Copilot Memory has a 28-day TTL [unverified]
- Instruction files, memory, and spaces apply simultaneously when a space is active [unverified]

## Related

- [Copilot Memory](copilot-memory.md)
- [Copilot Instructions Convention](copilot-instructions-md-convention.md)
- [Layered Context Architecture](../../context-engineering/layered-context-architecture.md)
- [Context Budget Allocation](../../context-engineering/context-budget-allocation.md)
- [Discoverable vs. Non-Discoverable Context](../../context-engineering/discoverable-vs-nondiscoverable-context.md)
- [MCP Integration with Copilot](mcp-integration.md)
