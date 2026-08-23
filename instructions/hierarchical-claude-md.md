---
title: "Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels"
term: "Hierarchical CLAUDE.md"
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
last_reviewed: 2026-06-13
maturity: emerging
---

# Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels

> Layer CLAUDE.md files at multiple scopes so each agent session receives only the context relevant to its working location.

!!! info "Also known as"
    Hierarchical CLAUDE.md · Layered Instruction Scopes · Directory-Level Instruction Hierarchy

    Claude Code–specific implementation. For the tool-agnostic pattern, see [Layer Agent Instructions by Specificity](layered-instruction-scopes.md).

## Four scopes

[Claude Code's memory system](https://code.claude.com/docs/en/memory) supports CLAUDE.md files at four scopes. Each scope has a different audience and lifetime:

| Scope | Location | Shared? | Covers |
|-------|----------|---------|--------|
| Managed policy | Enterprise-managed settings | Organization (admin-controlled) | Organization-wide policies and constraints |
| Project | `./CLAUDE.md` (repo root) | Team (version-controlled) | Project architecture, conventions, tooling |
| User | `~/.claude/CLAUDE.md` | Just you (all projects) | User preferences across all projects |
| Local | `./CLAUDE.local.md` | Just you (current project, gitignored) | Personal project-specific preferences |

Claude Code loads all four by increasing specificity. More specific instructions appear later in the assembled context and take priority.

## What belongs at each scope

Managed policy: organization-wide policies set by enterprise admins — approved tools, security requirements, and similar constraints.

Project root (`./CLAUDE.md`): the project's operating manual for agents — architecture overview, naming conventions, testing framework, required CI commands, and pointers to deeper docs. Version-controlled and team-shared.

User (`~/.claude/CLAUDE.md`): personal workflow preferences for any project — response format, editor conventions, tool access. Not version-controlled; does not affect teammates.

Local (`./CLAUDE.local.md`): personal project-specific preferences, not checked into version control. Add `CLAUDE.local.md` to `.gitignore` manually, or run `/init` and choose the personal option to have Claude Code add it for you ([memory setup docs](https://code.claude.com/docs/en/memory#set-up-a-project-claude-md)). Use it for sandbox URLs, personal test data, or per-machine settings.

Subdirectory CLAUDE.md files (`./api/CLAUDE.md`, `./frontend/CLAUDE.md`, and so on): part of the Project scope, not a separate scope. Claude Code walks the directory tree and loads them on demand when you work there, letting subprojects define their own conventions without duplicating the root file.

## What not to put in CLAUDE.md

CLAUDE.md files should be pointers to knowledge, not knowledge dumps. Per [Claude Code memory docs](https://code.claude.com/docs/en/memory):

- Keep each file short — target under 200 lines per CLAUDE.md file
- Link to documentation files rather than embedding content — `@path` imports still load their target in full at launch and can recurse up to four hops deep, so linking only cuts duplication, not token count ([Claude Code memory docs](https://code.claude.com/docs/en/memory#import-additional-files))
- Exclude task-specific instructions — those belong in the prompt
- Exclude knowledge the agent can discover from the codebase (types, structure, tests)

Claude Code loads CLAUDE.md files in full at the start of every session, consuming tokens alongside the conversation ([writing effective instructions](https://code.claude.com/docs/en/memory#write-effective-instructions)). Bloated files use context budget the agent needs for its task.

## Directory-level files for monorepos

A monorepo with distinct services usually has different lint rules, test commands, and conventions per service. Without directory-level files, the root must list every variant (growing the instruction count until compliance degrades) or omit service-specific rules (forcing the agent to guess). Directory-level files solve this: each service documents its conventions, and Claude Code [loads them on demand](https://code.claude.com/docs/en/memory#how-claude-md-files-load) for that directory.

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

## FAQ

**Do subdirectory CLAUDE.md files count as a fifth scope?**

No. Files such as `./api/CLAUDE.md` belong to the Project scope rather than sitting alongside managed policy, project, user, and local. Claude Code walks the directory tree and loads them on demand when you work in that directory, which lets a subproject document its own lint rules, test commands, and conventions without duplicating them into the repo root file.

**Does splitting rules across more files reduce the compliance risk of having many rules?**

No. Spreading instructions over several files does not lower the total instruction load the model must hold: even frontier models keep only 68% accuracy at the highest density tested, 500 simultaneous instructions, regardless of how many files that count is spread across ([IFScale, 2025](https://arxiv.org/abs/2507.11538v1)). Trim rules rather than add more files.

**Does linking to other docs instead of embedding them cut token cost?**

Only partly. Linking removes duplication, but an `@path` import still loads its target in full at launch and can recurse up to four hops deep, so the tokens still land in context ([Claude Code memory docs](https://code.claude.com/docs/en/memory#import-additional-files)). Because every loaded file is read in full at session start, keeping each file under 200 lines is what protects the budget.

## Key Takeaways

- Managed policy scope: organization-wide constraints, admin-controlled.
- Project scope: team-shared operating manual, version-controlled.
- User scope: personal preferences, not version-controlled.
- Local scope: personal project-specific preferences via `./CLAUDE.local.md`, gitignored (not version-controlled).
- More specific instructions load later and take priority.
- Keep files short; link to documentation rather than embedding it.

## Why it works

Hierarchical loading cuts context noise by separating instructions structurally. Fewer loaded instructions mean less risk of conflicting rules, lower token overhead before the first task token, and faster orientation. This applies the principle of least authority to context: each session receives only the knowledge its working location requires.

## When this backfires

Hierarchical scoping helps only when each file stays concise and consistent. A single root file is better in these conditions:

- Conflicting instructions across files: Claude Code concatenates all loaded CLAUDE.md files, and the [Claude Code memory docs](https://code.claude.com/docs/en/memory#write-effective-instructions) note that "if two rules contradict each other, Claude may pick one arbitrarily." A stale subdirectory file that contradicts updated root conventions silently wins for agent sessions in that directory.
- Compliance degradation at scale: splitting instructions across files does not lower the total instruction load — even frontier models hold only 68% accuracy at the highest instruction density tested, 500 simultaneous instructions, regardless of how many files that count is spread across ([IFScale, 2025](https://arxiv.org/abs/2507.11538v1); see also [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)). Trim rules rather than add more files.
- Maintenance fragmentation: when a shared convention changes, you must update every directory-level file that documents it. File renames leave CLAUDE.md behind while the root references the old path.
- Small, uniform projects: a single team working on one codebase gains nothing from extra files and pays the cost of keeping them in sync.

## Related

- [Layer Agent Instructions by Specificity](layered-instruction-scopes.md)
- [CLAUDE.md Convention](claude-md-convention.md)
- [Project Instruction File Ecosystem: CLAUDE.md, copilot-instructions, AGENTS.md](instruction-file-ecosystem.md)
- [@import Composition Pattern for Instruction Files](import-composition-pattern.md)
- [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Post-Compaction Re-Read Protocol](post-compaction-reread-protocol.md)
- [Getting Started: Setting Up Your Instruction File](getting-started-instruction-files.md)
