---
title: "Seeding Agent Context: Embedding Breadcrumbs in Code"
description: "Embed context in codebases using AGENTS.md files, decision comments, type annotations, and example files so agents discover conventions automatically."
tags:
  - context-engineering
  - instructions
aliases:
  - Providing Context to Agents
  - Context Priming
  - Breadcrumbs in Code
---

# Seeding Agent Context: Breadcrumbs in Code

> Strategically place files, comments, and markers that agents discover during exploration and use to shape their behaviour.

!!! note "Also known as"
    Providing Context to Agents, Context Priming, Breadcrumbs in Code. Seeding embeds contextual hints directly in the codebase for agents to discover during exploration. For the general technique of loading relevant context before a task, see [Context Priming](context-priming.md).

## Why Seeding Works

Agents explore codebases by reading files. What they find determines what they do. Unlike interactive prompts that exist only for one session, seeded context is persistent — it influences every agent session that touches that part of the codebase.

This shifts [context management](context-engineering.md) from a per-session concern to a codebase hygiene concern. The information is where the work happens.

## Techniques

### Directory-Scoped AGENTS.md Files

The [AGENTS.md open standard](https://agents.md) defines a dedicated file for agent context. Agents read the nearest AGENTS.md in the directory tree, so subdirectory files override or extend project-level instructions. This makes them effective for scoping conventions to specific packages, modules, or services in a monorepo.

A directory-level AGENTS.md might contain:

- Package-specific conventions that differ from the project default
- Known constraints and decisions the agent should respect
- Which tests cover this module

The format is standard Markdown. No required fields. Agents across [multiple platforms](https://agents.md) read AGENTS.md files, including GitHub Copilot, Cursor, and Codex [unverified — Claude Code is not listed as an AGENTS.md-compatible tool on agents.md; it uses CLAUDE.md].

### Inline Decision Comments

Comments explaining *why* a decision was made prevent agents from reverting it. A comment like:

```typescript
// We use optimistic updates here rather than waiting for the server response.
// Reverting to pessimistic updates caused noticeable UI lag in user testing.
```

gives an agent the rationale to preserve, not change, this approach when editing the file.

Without the comment, an agent refactoring the function has no signal that this is an intentional design choice rather than something that should be "improved."

### TODO and FIXME Markers

Agents treat `TODO` and `FIXME` comments as actionable items [unverified — behaviour varies by tool and instruction set]. Placing a TODO at the exact location of a known issue ensures the agent encounters it when editing nearby code.

### Type Annotations

Complete type signatures eliminate an entire class of agent guesswork. The agent does not need to infer return types, parameter shapes, or nullability — the types specify them. This applies to function signatures, interface definitions, and data structure annotations.

### Example Files

Agents pattern-match against existing code. A well-written example — a reference implementation, a canonical test, a model migration — communicates conventions that no amount of prose instruction can match in precision. Agents extend patterns they can see.

Example files are the most direct way to establish the structure agents should follow [unverified — practitioner experience, not sourced from any specific standard].

## What to Seed vs. What to Prompt

Not everything belongs in the codebase as a breadcrumb:

| Seed in the codebase | Prompt interactively |
|---------------------|---------------------|
| Stable conventions and constraints | Task-specific requirements |
| Architectural decisions and rationale | Current context about what you're building |
| Known issues and TODOs | Priorities and scope for this session |
| Type annotations and interfaces | One-off instructions |

Breadcrumbs work for durable information. Session-specific intent belongs in the prompt.

## Key Takeaways

- Seeded context is persistent across sessions; prompt context is not. Use the codebase to carry durable conventions.
- Directory-level AGENTS.md files scope context to where it is relevant — use them in monorepos to give subprojects their own conventions.
- Inline decision comments preserve rationale that prevents agents from undoing deliberate design choices.
- Type annotations and example files are higher-signal than prose descriptions of the same information.

## Unverified Claims

- Agents across multiple platforms read AGENTS.md files, including GitHub Copilot, Cursor, and Codex [unverified — Claude Code is not listed as an AGENTS.md-compatible tool on agents.md; it uses CLAUDE.md]
- Agents treat `TODO` and `FIXME` comments as actionable items [unverified — behaviour varies by tool and instruction set]
- Example files are the most direct way to establish the structure agents should follow [unverified — practitioner experience, not sourced from any specific standard]

## Example

A Python monorepo with a data-pipeline package uses all four techniques together:

**Project-level `AGENTS.md`** (repo root) lists the packages and where conventions live:

```markdown
# Project: data-platform

## Structure
- `pipelines/` — ETL jobs. See `pipelines/AGENTS.md` for conventions.
- `api/` — FastAPI service. See `api/AGENTS.md` for conventions.
- `shared/` — shared utilities imported by both packages.

## Global rules
- All new modules require type annotations.
- Do not modify `shared/schema.py` without updating `docs/schema-changelog.md`.
```

**Package-level `pipelines/AGENTS.md`** scopes the package conventions:

```markdown
# Pipelines package

## Conventions
- Use `BaseTransform` as the base class for all transform steps.
- Each pipeline has a corresponding test in `tests/pipelines/`.
- Airflow DAG definitions live in `dags/`; do not put business logic there.

## Known constraints
- `ingest_raw.py` uses synchronous S3 calls intentionally — async caused
  throttling issues with the bucket policy. Do not convert to async.
```

**Inline decision comment** in `pipelines/ingest_raw.py`:

```python
# Synchronous S3 client is intentional. Async caused throttling errors
# under the bucket policy in prod (see AGENTS.md — Known constraints).
# TODO: revisit if bucket policy is updated to allow concurrent requests.
s3 = boto3.client("s3")
```

**Typed function signature** leaves no ambiguity for the agent:

```python
def fetch_records(
    bucket: str,
    prefix: str,
    since: datetime,
) -> list[dict[str, Any]]:
    ...
```

An agent editing `ingest_raw.py` reads the package AGENTS.md, encounters the decision comment, sees the TODO, and understands the typed interface — all without any session-level prompting.

## Related

- [Context Priming](context-priming.md)
- [The Specification as Prompt](../instructions/specification-as-prompt.md)
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md)
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md)
- [Prompt Layering](prompt-layering.md)
- [Repository Map Pattern](repository-map-pattern.md)
