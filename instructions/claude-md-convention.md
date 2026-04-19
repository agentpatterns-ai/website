---
title: "CLAUDE.md Convention for Structuring Agent Instructions"
description: "CLAUDE.md is Claude Code's project-level instruction file — read at session start to convey conventions, tooling, and behavioral rules."
tags:
  - instructions
aliases:
  - Instruction File Convention
  - Project Instruction Files
---

# CLAUDE.md Convention

> CLAUDE.md is Claude Code's project-level instruction file -- a Markdown file that Claude Code reads at session start to understand project conventions, tooling, and behavioral rules.

??? note "Also known as: Instruction File Convention, Project Instruction Files"
    See [Project Instruction File Ecosystem](instruction-file-ecosystem.md) and [copilot-instructions.md Convention](../tools/copilot/copilot-instructions-md-convention.md).

## What It Does

Claude Code loads CLAUDE.md at session start into the context window ([docs](https://code.claude.com/docs/en/memory)). Instructions are context, not enforced configuration -- specificity yields compliance.

## File Locations and Scopes

Four scopes with different persistence models ([docs](https://code.claude.com/docs/en/memory)):

| Scope | Location | Shared with | Purpose |
|-------|----------|-------------|---------|
| Managed policy | OS-specific system path | All users on machine | Organization-wide standards deployed via MDM/Group Policy |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team (version-controlled) | Project architecture, conventions, build commands |
| User | `~/.claude/CLAUDE.md` | Just you (all projects) | Personal preferences across projects |
| Local | `./CLAUDE.local.md` | Just you (current project) | Personal project-specific settings, not checked in |

## Load Order and Precedence

Claude Code walks up the directory tree loading every CLAUDE.md and CLAUDE.local.md it finds ([docs](https://code.claude.com/docs/en/memory)). Subdirectory files load on demand. More specific scopes win: directory overrides project root, project overrides user, user overrides policy.

## Writing Effective Instructions

Key properties ([docs](https://code.claude.com/docs/en/memory)):

| Property | Guidance |
|----------|----------|
| **Size** | Under 200 lines -- longer files reduce adherence |
| **Structure** | Headers and bullets for scanning |
| **Specificity** | Verifiable: "Use 2-space indentation" not "Format code properly" |
| **Consistency** | Contradictions cause unpredictable behavior; audit regularly |

## What to Include

A project CLAUDE.md should cover ([docs](https://code.claude.com/docs/en/memory)):

- **Build and test commands** -- build, test, lint, deploy commands
- **Coding standards** -- naming conventions, formatting rules
- **Architecture** -- where code lives, module interactions
- **Workflows** -- deployment steps, PR process
- **Navigation pointers** -- link to deeper docs rather than embedding

Run `/init` to generate a CLAUDE.md from discovered conventions.

## What Not to Include

- **Task-specific instructions** -- belong in the prompt
- **Discoverable knowledge** -- directory structure, types, test output available via tools (see [Discoverable vs Non-Discoverable Context](../context-engineering/discoverable-vs-nondiscoverable-context.md))
- **Full documentation** -- link instead; tokens reduce task budget
- **Generic advice** -- "write clean code" is noise

## Importing Additional Files

CLAUDE.md supports `@path/to/file` import syntax ([docs](https://code.claude.com/docs/en/memory)). Relative and absolute paths work; imports nest five levels deep. See [@import Composition Pattern](import-composition-pattern.md) for modular authoring patterns.

```text
See @README for project overview and @package.json for available npm commands.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

Claude Code shows an approval dialog on first encounter; declined imports remain disabled ([docs](https://code.claude.com/docs/en/memory)).

## Path-Scoped Rules with `.claude/rules/`

Place topic-specific Markdown files in `.claude/rules/` ([docs](https://code.claude.com/docs/en/memory)). Files without `paths` frontmatter load unconditionally; files with `paths` load when matching files are in scope.

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
```

Rules files support symlinks for cross-repo sharing ([docs](https://code.claude.com/docs/en/memory)).

## CLAUDE.md vs. AGENTS.md

Both offer repo-level context but differ in audience and discovery:

| Dimension | CLAUDE.md | AGENTS.md |
|-----------|-----------|-----------|
| Standard | Claude Code proprietary ([docs](https://code.claude.com/docs/en/memory)) | [Open standard](https://agents.md) |
| Read by | Claude Code only | Any AGENTS.md-compatible tool |
| Hierarchy | Directory traversal + imports + `.claude/rules/` | Directory traversal |
| Path scoping | `.claude/rules/` with `paths` frontmatter | Not in standard |
| Personal scope | `~/.claude/CLAUDE.md` and `CLAUDE.local.md` | Not in standard |

Teams using multiple AI tools should maintain both or consolidate into AGENTS.md.

## Auto Memory: The Companion System

Auto memory is what Claude writes back -- build commands, debugging insights, preferences ([docs](https://code.claude.com/docs/en/memory)). Stored in `~/.claude/projects/<project>/memory/`; first 200 lines load at session start. Toggle via `/memory`.

## Example

A minimal project CLAUDE.md for a TypeScript monorepo:

```text
# Project Instructions

## Build and Test

    npm run build        # compile all packages
    npm test             # run full test suite
    npm run lint         # ESLint + Prettier check

## Conventions

- Use 2-space indentation throughout
- All public functions must have JSDoc comments
- Place new utilities in packages/shared/src/

## Architecture

- packages/api/ -- Express REST API, connects to Postgres via Prisma
- packages/worker/ -- BullMQ job processors
- packages/shared/ -- types and utilities shared across packages

## Additional Rules

@.claude/rules/api-standards.md
```

With path-scoped rules in `.claude/rules/api-standards.md`:

```markdown
---
paths:
  - "packages/api/**/*.ts"
---

# API Standards

- Validate all inputs with Zod before processing
- Return errors using the `ApiError` class from `shared/errors`
```

## Key Takeaways

- CLAUDE.md is context loaded into the session, not enforced configuration — specificity yields compliance.
- Four scopes layer from managed policy down to local overrides; more specific scopes win on conflict.
- Keep it under 200 lines of scannable headers and bullets; longer files erode adherence.
- Link to deeper docs and use `@path` imports or `.claude/rules/` for path-scoped content instead of inlining everything.
- Omit discoverable knowledge and task-specific instructions — those belong in tools or prompts, not the instruction file.

## Related

- [Getting Started: Setting Up Your Instruction File](../workflows/getting-started-instruction-files.md)
- [Project Instruction File Ecosystem](instruction-file-ecosystem.md)
- [Hierarchical CLAUDE.md](hierarchical-claude-md.md)
- [@import Composition Pattern](import-composition-pattern.md)
- [Layer Agent Instructions by Specificity](layered-instruction-scopes.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [Content Exclusion Gap](content-exclusion-gap.md)
