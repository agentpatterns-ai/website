---
title: "Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels"
description: "Layer CLAUDE.md files at multiple scopes so each agent session receives only the context relevant to its working location."
tags:
  - context-engineering
  - instructions
  - claude
aliases:
  - "Hierarchical CLAUDE.md"
  - "Layered Instruction Scopes"
  - "Directory-Level Instruction Hierarchy"
  - "Hierarchical CLAUDE.md: Layered Context File Scoping"
---

# Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels

> Layer CLAUDE.md files at multiple scopes so each agent session receives only the context relevant to its working location.

!!! info "Also known as"
    **Hierarchical CLAUDE.md** · **Layered Instruction Scopes** · **Directory-Level Instruction Hierarchy**

    Claude Code–specific implementation. For the tool-agnostic pattern, see [Layer Agent Instructions by Specificity](layered-instruction-scopes.md).

## Four Scopes

[Claude Code's memory system](https://code.claude.com/docs/en/memory) supports CLAUDE.md files at four scopes, each with a different audience and lifetime:

| Scope | Location | Shared? | Covers |
|-------|----------|---------|--------|
| Managed policy | Enterprise-managed settings | Organization (admin-controlled) | Organization-wide policies and constraints |
| Project | `./CLAUDE.md` (repo root) | Team (version-controlled) | Project architecture, conventions, tooling |
| User | `~/.claude/CLAUDE.md` | Just you (all projects) | User preferences across all projects |
| Local | `./CLAUDE.local.md` | Just you (current project, gitignored) | Personal project-specific preferences |

Claude Code loads all four in order of increasing specificity. More specific instructions appear later in the assembled context, giving them higher effective priority.

## What Belongs at Each Scope

**Managed policy**: Organization-wide policies set by enterprise admins — approved tools, security requirements, and similar constraints.

**Project root (`./CLAUDE.md`)**: The project's "operating manual" for agents — architecture overview, naming conventions, testing framework, required CI commands, and pointers to deeper docs. Version-controlled and team-shared.

**User (`~/.claude/CLAUDE.md`)**: Personal workflow preferences that apply regardless of project — response format, editor conventions, tool access. Not version-controlled; does not affect teammates.

**Local (`./CLAUDE.local.md`)**: Personal project-specific preferences, not checked into version control. Add `CLAUDE.local.md` to `.gitignore` manually, or run `/init` and choose the personal option to have Claude Code add it for you ([docs](https://code.claude.com/docs/en/memory#set-up-a-project-claude-md)). Use it for sandbox URLs, personal test data, or per-machine settings.

**Subdirectory CLAUDE.md files (`./api/CLAUDE.md`, `./frontend/CLAUDE.md`, etc.)**: Part of the Project scope, not a separate scope. Claude Code walks the directory tree and loads them on demand when working in those directories, letting subprojects define their own conventions without duplicating the root file.

## What Not to Put in CLAUDE.md

CLAUDE.md files should be pointers to knowledge, not knowledge dumps. Per [Claude Code memory docs](https://code.claude.com/docs/en/memory):

- Keep each file short — target under 200 lines per CLAUDE.md file
- Link to documentation files rather than embedding content
- Exclude task-specific instructions — those belong in the prompt
- Exclude knowledge the agent can discover from the codebase (types, structure, tests)

CLAUDE.md files are loaded in full at the start of every session, consuming tokens alongside the conversation ([docs](https://code.claude.com/docs/en/memory#write-effective-instructions)). Bloated files consume context budget the agent needs for the actual task.

## Directory-Level Files for Monorepos

A monorepo with distinct services typically has different lint rules, test commands, and conventions per service. Without directory-level files, the root must either enumerate all variants (growing the instruction count until compliance degrades) or omit service-specific rules (forcing the agent to guess). Directory-level files solve this: each service documents its own conventions, and Claude Code [loads them on demand](https://code.claude.com/docs/en/memory#how-claude-md-files-load) when working in those directories.

## Maintenance

Treat CLAUDE.md files as living documentation:

- When a convention changes, update the CLAUDE.md that documents it
- When a directory-level file contradicts the project root, the specific file wins — make the contradiction explicit
- Remove instructions that duplicate what is already expressed in code, types, or tests

## Example

A monorepo with a backend API and a React frontend uses three CLAUDE.md files to scope instructions without duplication. The directory layout is:

```
my-repo/
├── CLAUDE.md               # Project root — shared with the whole team
├── backend/
│   └── CLAUDE.md           # Backend-specific conventions
└── frontend/
    └── CLAUDE.md           # Frontend-specific conventions
```

The root file covers what every agent session needs regardless of where it is working:

```markdown
# my-repo

## Architecture
Monorepo: `backend/` (Python FastAPI) and `frontend/` (React + TypeScript).
See `docs/architecture.md` for service boundaries.

## Testing
- Backend: `pytest` — run from `backend/` with `pytest tests/`
- Frontend: `vitest` — run from `frontend/` with `npm test`

## CI
All PRs require `pre-commit run --all-files` to pass before merge.
```

`backend/CLAUDE.md` adds only what is specific to Python/FastAPI work:

```markdown
## Backend conventions
- Use `sqlalchemy` ORM; never write raw SQL
- API routes live in `backend/app/routers/`; one file per resource
- Validate all inputs with Pydantic models defined in `backend/app/schemas/`
- Run `alembic upgrade head` after any migration change
```

`frontend/CLAUDE.md` covers React-specific rules:

```markdown
## Frontend conventions
- State management: Zustand only; no Redux
- Prefer `React.FC` components in `src/components/`; no class components
- API calls go through `src/api/client.ts`; do not call `fetch` directly
- Run `npm run lint` and `npm run typecheck` before committing
```

When Claude Code works inside `frontend/`, it loads the root file plus `frontend/CLAUDE.md` — backend conventions stay out of its context. The reverse applies when working in `backend/`.

## Key Takeaways

- Managed policy scope: organization-wide constraints, admin-controlled.
- Project scope: team-shared operating manual, version-controlled.
- User scope: personal preferences, not version-controlled.
- Local scope: personal project-specific preferences via `./CLAUDE.local.md`, gitignored (not version-controlled).
- More specific instructions load later and take priority.
- Keep files short; link to documentation rather than embedding it.

## Why It Works

Hierarchical loading reduces context noise through structural separation. Fewer loaded instructions mean less risk of conflicting rules, lower token overhead before the first task token, and faster orientation. This applies the principle of least authority to context: each session receives only the knowledge its working location requires.

## When This Backfires

Hierarchical scoping adds value only when each file stays concise and consistent. Conditions where a single root file is better:

- **Conflicting instructions across files**: All loaded CLAUDE.md files are concatenated; the [official docs](https://code.claude.com/docs/en/memory#write-effective-instructions) note that "if two rules contradict each other, Claude may pick one arbitrarily." A stale subdirectory file that contradicts updated root conventions silently wins for agent sessions in that directory.
- **Compliance degradation at scale**: Splitting instructions across files does not lower the aggregate instruction load — see [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md). Prefer trimming rules over adding more files.
- **Maintenance fragmentation**: When a shared convention changes, every directory-level file that documents it needs a manual update. File renames leave CLAUDE.md behind while the root references the old path.
- **Small, uniform projects**: A single team working on one codebase gains nothing from extra files and pays the cost of keeping them in sync.

## Related

- [Layer Agent Instructions by Specificity](layered-instruction-scopes.md)
- [CLAUDE.md Convention](claude-md-convention.md)
- [Project Instruction File Ecosystem: CLAUDE.md, copilot-instructions, AGENTS.md](instruction-file-ecosystem.md)
- [@import Composition Pattern for Instruction Files](import-composition-pattern.md)
- [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Post-Compaction Re-Read Protocol](post-compaction-reread-protocol.md)
- [Getting Started: Setting Up Your Instruction File](../workflows/getting-started-instruction-files.md)
