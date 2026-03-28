---
title: "CLAUDE.md Convention for Structuring Agent Instructions"
description: "CLAUDE.md is Claude Code's project-level instruction file -- a Markdown file that Claude Code reads at session start to understand project conventions"
tags:
  - instructions
aliases:
  - Instruction File Convention
  - Project Instruction Files
---

# CLAUDE.md Convention

> CLAUDE.md is Claude Code's project-level instruction file -- a Markdown file that Claude Code reads at session start to understand project conventions, tooling, and behavioral rules.

??? note "Also known as: Instruction File Convention, Project Instruction Files"
    See also [Project Instruction File Ecosystem](instruction-file-ecosystem.md) and [copilot-instructions.md Convention](../tools/copilot/copilot-instructions-md-convention.md).

## What It Does

Claude Code loads CLAUDE.md files at session start and injects their contents into the context window ([docs](https://code.claude.com/docs/en/memory)). The instructions are context, not enforced configuration -- Claude follows them on a best-effort basis; more specific instructions produce more consistent compliance.

## File Locations and Scopes

Four scopes, each with a different persistence model ([docs](https://code.claude.com/docs/en/memory)):

| Scope | Location | Shared with | Purpose |
|-------|----------|-------------|---------|
| Managed policy | OS-specific system path | All users on machine | Organization-wide standards deployed via MDM/Group Policy |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team (version-controlled) | Project architecture, conventions, build commands |
| User | `~/.claude/CLAUDE.md` | Just you (all projects) | Personal preferences across projects |
| Local | `./CLAUDE.local.md` | Just you (current project) | Personal project-specific settings, not checked in |

## Load Order and Precedence

Claude Code walks up the directory tree loading every CLAUDE.md and CLAUDE.local.md it finds ([docs](https://code.claude.com/docs/en/memory)). Subdirectory files load on demand. More specific scopes take precedence: directory overrides project root, project overrides user, user overrides managed policy.

## Writing Effective Instructions

Key properties from the [official docs](https://code.claude.com/docs/en/memory):

| Property | Guidance |
|----------|----------|
| **Size** | Target under 200 lines -- longer files reduce adherence |
| **Structure** | Use headers and bullets for scanning |
| **Specificity** | Concrete enough to verify: "Use 2-space indentation" not "Format code properly" |
| **Consistency** | Contradictory rules cause unpredictable behavior; audit periodically |

## What to Include

A project CLAUDE.md should contain ([docs](https://code.claude.com/docs/en/memory)):

- **Build and test commands** -- exact commands to build, test, lint, deploy
- **Coding standards** -- naming conventions, formatting rules, patterns
- **Architecture** -- where code lives, how modules interact
- **Workflows** -- deployment steps, PR process, conventions
- **Navigation pointers** -- links to deeper docs rather than embedding

Run `/init` to generate a starting CLAUDE.md from discovered conventions.

## What Not to Include

- **Task-specific instructions** -- belong in the prompt
- **Discoverable knowledge** -- directory structure, types, and test output are available via tools (see [Discoverable vs Non-Discoverable Context](../context-engineering/discoverable-vs-nondiscoverable-context.md))
- **Full documentation** -- link to docs; CLAUDE.md tokens reduce task budget
- **Generic advice** -- "write clean code" adds noise without signal

## Importing Additional Files

CLAUDE.md supports `@path/to/file` import syntax ([docs](https://code.claude.com/docs/en/memory)). Both relative and absolute paths work; imports nest five levels deep. See [@import Composition Pattern](import-composition-pattern.md) for modular authoring patterns.

```text
See @README for project overview and @package.json for available npm commands.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

On first encounter, Claude Code shows an approval dialog; declined imports stay disabled.

## Path-Scoped Rules with `.claude/rules/`

Place topic-specific Markdown files in `.claude/rules/` ([docs](https://code.claude.com/docs/en/memory)). Files without `paths` frontmatter load unconditionally; files with `paths` load only when matching files are accessed.

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
```

Rules files support symlinks for cross-project sharing.

## CLAUDE.md vs. AGENTS.md

Both provide repository-level context but differ in audience and discovery model:

| Dimension | CLAUDE.md | AGENTS.md |
|-----------|-----------|-----------|
| Standard | Claude Code proprietary ([docs](https://code.claude.com/docs/en/memory)) | [Open standard](https://agents.md) |
| Read by | Claude Code only | Any AGENTS.md-compatible tool |
| Hierarchy | Directory traversal + imports + `.claude/rules/` | Directory traversal |
| Path scoping | `.claude/rules/` with `paths` frontmatter | Not in standard |
| Personal scope | `~/.claude/CLAUDE.md` and `CLAUDE.local.md` | Not in standard |

Teams using multiple AI tools should maintain both or consolidate into AGENTS.md.

## Auto Memory: The Companion System

Auto memory is the companion system Claude writes -- build commands, debugging insights, preferences from corrections ([docs](https://code.claude.com/docs/en/memory)). It lives in `~/.claude/projects/<project>/memory/`; the first 200 lines load at session start. Toggle via `/memory`.

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

## Related

- [Getting Started: Setting Up Your Instruction File](../workflows/getting-started-instruction-files.md)
- [Hierarchical CLAUDE.md](hierarchical-claude-md.md)
- [Project Instruction File Ecosystem](instruction-file-ecosystem.md)
- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [Layer Agent Instructions by Specificity](layered-instruction-scopes.md)
- [Instruction Polarity](instruction-polarity.md)
- [@import Composition Pattern](import-composition-pattern.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [When to Use Examples vs Rules in Agent Instructions](example-driven-vs-rule-driven-instructions.md)
- [Critical Instruction Repetition via Primacy and Recency](critical-instruction-repetition.md)
- [Domain-Specific System Prompts](domain-specific-system-prompts.md)
- [AGENTS.md Design Patterns](agents-md-design-patterns.md)
- [Content Exclusion Gap](content-exclusion-gap.md)
- [Frozen Spec File](frozen-spec-file.md)
