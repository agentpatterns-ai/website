---
title: "Copilot Spaces: Curated Context Collections for Grounding"
description: "Named context collections that aggregate repos, files, PRs, issues, notes, images, and uploads into a curated container that grounds Copilot responses."
tags:
  - context-engineering
  - copilot
---

# Copilot Spaces: Curated Context Collections for Grounding

> Named context collections that aggregate repositories, code files, PRs, issues, notes, images, and uploads into a curated container that grounds Copilot responses.

## What Spaces Are

Copilot Spaces are manually curated context bundles. You assemble the reference material Copilot needs for a specific domain — repositories, files, pull requests, issues, free-text notes, images, and uploads — and questions asked inside the space are grounded in that curated content ([GitHub Docs](https://docs.github.com/en/copilot/concepts/context/spaces), [GitHub changelog, GA](https://github.blog/changelog/2025-09-24-copilot-spaces-is-now-generally-available/)).

Spaces replaced the deprecated Knowledge Bases (sunset November 2025), extending support beyond the repo-only model of their predecessor ([GitHub changelog, Knowledge Bases sunset](https://github.blog/changelog/2025-08-20-sunset-notice-copilot-knowledge-bases/)). Accessed at `github.com/copilot/spaces` and through the remote GitHub MCP server in IDEs — though repo-only Spaces currently need at least one non-repo source (file, issue, or note) to be reachable from the IDE ([community discussion](https://github.com/orgs/community/discussions/182622)).

## Why It Works

Grounding a Space is a retrieval-augmented-generation (RAG) step: Copilot indexes the assembled sources, retrieves passages most relevant to the question, and injects only those passages into the model's context window alongside the prompt ([GitHub Blog, RAG](https://github.blog/ai-and-ml/generative-ai/what-is-retrieval-augmented-generation-and-what-does-it-do-for-generative-ai/)). Curation narrows the retrieval pool to an on-topic corpus, so the snippets that reach the prompt are more likely to be the right ones.

## Where Spaces Fit in the Context Stack

Spaces sit between always-on instruction files and ad-hoc chat context:

| Layer | Mechanism | Persistence | Curated by |
|-------|-----------|-------------|------------|
| Behavioral rules | `.github/copilot-instructions.md` | Every interaction | Team (version-controlled) |
| Learned preferences | Copilot Memory | Autonomous, 28-day auto-expiry ([GitHub changelog](https://github.blog/changelog/2026-01-15-agentic-memory-for-github-copilot-is-in-public-preview/)) | Agent |
| **Reference material** | **Copilot Spaces** | **Persistent, manually curated** | **Human** |
| Ad-hoc context | Paste into chat / `@file` | Single interaction | Human |

Instruction files define *how* the agent behaves, memory captures *what* the agent learns, Spaces provide *the reference material* the agent draws on.

## Auto-Sync

GitHub-based sources (repositories, files, PRs, issues) auto-sync as they change, so the Space stays current as the codebase evolves ([GitHub Docs](https://docs.github.com/en/copilot/concepts/context/spaces), [GitHub changelog, GA](https://github.blog/changelog/2025-09-24-copilot-spaces-is-now-generally-available/)). Uploaded files, free-text notes, and images are static and require manual updates.

## Sharing and Access Control

**Organization-owned spaces** use tiered roles — admin, editor, viewer, or deny ([GitHub Docs](https://docs.github.com/en/copilot/concepts/context/spaces)).

**Individual-owned spaces** support three visibility modes — *private* (owner only), *shared* (specific GitHub users), or *public* (view-only via direct link, not search-indexed). Public is not available for org-owned spaces ([GitHub changelog, Dec 2025](https://github.blog/changelog/2025-12-01-copilot-spaces-public-spaces-and-code-view-support/)).

RBAC is enforced across every sharing model: viewers only see sources they already have permission to access, so no private content leaks through a shared Space ([GitHub changelog, Dec 2025](https://github.blog/changelog/2025-12-01-copilot-spaces-public-spaces-and-code-view-support/)).

## Practical Configurations

**Feature development:** feature branch code + product spec + design notes + related issues in one Space. Ask implementation questions against the full feature context rather than individual files ([GitHub Docs, tutorials](https://docs.github.com/en/copilot/tutorials/speed-up-development-work)).

**Recurring tasks:** a telemetry-events Space with event schemas, tracking code, and naming conventions — reused across sessions instead of re-explaining the tracking system.

**Cross-team onboarding:** Spaces for auth, API references, or architecture give new developers curated context instead of scattered wiki links ([GitHub changelog, GA](https://github.blog/changelog/2025-09-24-copilot-spaces-is-now-generally-available/)). See [Team Onboarding for Agent Workflows](../../workflows/team-onboarding.md).

## Space vs. Instruction File vs. Memory

| Use case | Mechanism |
|----------|-----------|
| "Always use camelCase in this repo" | Instruction file |
| "The sessions table excludes first-party traffic" | Memory (learned from correction) |
| "Here are the API schemas, product spec, and auth docs for this feature" | Space |

Spaces follow the same billing model as Copilot Chat ([GitHub changelog, GA](https://github.blog/changelog/2025-09-24-copilot-spaces-is-now-generally-available/)).

## Example

A recurring telemetry-feature Space assembles schemas, tracking code, and naming conventions so developers avoid re-explaining the tracking system each session:

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

## When This Backfires

Spaces work well for stable reference material — they underperform in several conditions:

- **Static uploads drift silently.** Uploads and free-text notes do not auto-sync. Copilot will reason from outdated content until someone manually re-uploads.
- **Undocumented quotas misbehave.** Space capacity is enforced on indexed semantic content rather than file size, and GitHub has not published the exact limits; community reports describe progress bars passing 100% with fewer than 200 small files, suggesting overfilled Spaces silently drop low-priority content ([community discussion](https://github.com/orgs/community/discussions/182622)). Treat Spaces as curated semantic context, not a mirror of a repo.
- **GitHub-hosted only.** Spaces require a GitHub account and work through github.com or the remote GitHub MCP server. Airgapped, self-hosted, or non-GitHub teams cannot use Spaces.
- **Shared spaces do not eliminate access gaps.** RBAC means collaborators with different repo permissions see different effective context from the same Space, producing divergent responses for the same question.

## Key Takeaways

- Spaces are the manual curation layer in the context stack — reference material that sits between always-on instruction files and ephemeral chat context.
- GitHub-based sources auto-sync; uploaded content does not.
- RBAC is enforced even on public spaces — viewers only see sources they can already access.
- Use spaces for reference material (specs, schemas, docs), instruction files for behavioral rules, and memory for agent-discovered knowledge.

## Related

- [Copilot Memory](copilot-memory.md)
- [Copilot Instructions Convention](copilot-instructions-md-convention.md)
- [Layered Context Architecture](../../context-engineering/layered-context-architecture.md)
- [Context Budget Allocation](../../context-engineering/context-budget-allocation.md)
- [Discoverable vs. Non-Discoverable Context](../../context-engineering/discoverable-vs-nondiscoverable-context.md)
- [MCP Integration with Copilot](mcp-integration.md)
