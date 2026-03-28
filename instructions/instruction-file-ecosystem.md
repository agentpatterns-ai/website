---
title: "Project Instruction File Ecosystem: CLAUDE.md, copilot-instructions, AGENTS.md"
description: "Every major AI coding tool invented a project-level instruction file independently — understanding how these files relate helps teams working across tools avoid content drift and duplication."
aliases:
  - Instruction File Convention
  - Project Instruction Files
tags:
  - instructions
  - tool-agnostic
---

# Project Instruction File Ecosystem: CLAUDE.md, copilot-instructions, AGENTS.md

> Every major AI coding tool invented a project-level instruction file independently — understanding how these files relate helps teams working across tools avoid content drift and duplication.

??? note "Also known as: Instruction File Convention, Project Instruction Files"
    This page is the tool-agnostic overview. For tool-specific details, see:

    - [CLAUDE.md Convention](claude-md-convention.md) — Claude Code's project-level instruction file
    - [copilot-instructions.md Convention](../tools/copilot/copilot-instructions-md-convention.md) — GitHub Copilot's repository-level instruction file

## The Same Problem, Different Files

Each AI coding assistant needs project context. Multiple tools means multiple instruction files:

| Tool | File | Scope |
|------|------|-------|
| Claude Code | `CLAUDE.md` ([docs](https://code.claude.com/docs/en/memory)) | Workspace → project → directory hierarchy |
| GitHub Copilot | `.github/copilot-instructions.md` + `.github/instructions/*.instructions.md` ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)) | Repository-wide + path-specific |
| Any AGENTS.md-compatible tool | `AGENTS.md` ([standard](https://agents.md)) | Repository root |

These files solve the same problem — giving the agent project context — but differ in location, hierarchy support, and syntax.

## Discovery Differences

Claude Code uses a hierarchical discovery model: it reads `CLAUDE.md` at the workspace level, then at the project root, then in any subdirectory the agent navigates into ([docs](https://code.claude.com/docs/en/memory)). A `src/auth/CLAUDE.md` can add constraints specific to authentication code without affecting the rest of the project.

GitHub Copilot uses a two-tier model. `.github/copilot-instructions.md` applies repository-wide; path-specific `*.instructions.md` files in `.github/instructions/` use `applyTo` frontmatter globs to target specific files or directories ([docs](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)). Both tiers are provided simultaneously ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)).

AGENTS.md-compatible tools read `AGENTS.md` from the repository root on session start.

## Content Overlap and Drift

All three files typically contain the same categories: project context, coding conventions, architectural constraints, workflow notes. When maintained separately without a convergence strategy, content diverges [unverified] — one file says "use pnpm", another says "use npm", and each agent follows whatever its tool reads. Architectural decisions recorded in one file may not appear in others [unverified], making the files unreliable as context sources.

## Convergence Strategies

**Single canonical file with symlinks.** Maintain one source of truth (`AGENTS.md` or `CLAUDE.md`) and symlink the others to it. The tradeoff: tool-specific syntax (e.g., Claude Code's [`@path/to/import` syntax](https://code.claude.com/docs/en/memory)) may not be supported by other tools.

**Shared base with tool-specific extends.** Maintain a base file with project-wide content, and tool-specific files that import the base and add tool-specific configuration. Requires tooling support for imports or includes [unverified].

**AGENTS.md as the canonical standard.** The [AGENTS.md open standard](https://agents.md) is tool-agnostic by design. If you author for AGENTS.md, compatible tools read it natively; non-compatible tools still need their own file, but the canonical content lives in one place.

## Hierarchy as a Feature

Both Claude Code and GitHub Copilot support scoped instruction files. Claude Code uses directory-level `CLAUDE.md` files; Copilot uses `*.instructions.md` files with `applyTo` glob patterns. Both let high-sensitivity areas carry additional constraints while keeping the root file short.

## What to Include

The content categories that belong in any project instruction file:

- **Project identity** — what the project does, tech stack, primary language
- **Conventions** — naming, formatting, test strategy, commit format
- **Constraints** — banned tools, required tools, restricted files
- **Navigation** — pointers to architecture docs, workflow guides, area-specific files

What does not belong:

- Full documentation of conventions (link to where it lives)
- Architecture diagrams or lengthy explanations
- Anything only relevant to one task type (put that in a skill)

## Example

This example shows a convergence strategy where `AGENTS.md` is the canonical source of truth, `CLAUDE.md` includes it via Claude Code's import syntax, and a Copilot-specific file adds tool-specific configuration on top.

Repository layout:

```
AGENTS.md                                      # canonical — shared project context
CLAUDE.md                                      # Claude Code entry point
.github/
  copilot-instructions.md                      # Copilot entry point
  instructions/
    typescript.instructions.md                 # Copilot path-scoped override
src/
  auth/
    CLAUDE.md                                  # Claude Code directory-level override
```

`AGENTS.md` holds the shared content all tools need:

```markdown
# agent-patterns

TypeScript monorepo. Use pnpm. Run `pnpm test` before committing.
Commits must follow Conventional Commits. Do not modify `docs/generated/`.
```

`CLAUDE.md` imports `AGENTS.md` and adds Claude Code-specific configuration:

```markdown
@AGENTS.md

## Claude Code
Use worktrees for all experimental work (`isolation: worktree`).
Check CLAUDE.md files in subdirectories — auth code has additional constraints.
```

`.github/copilot-instructions.md` references the same content categories without import support:

```markdown
TypeScript monorepo. Use pnpm. Run `pnpm test` before committing.
Commits must follow Conventional Commits. Do not modify `docs/generated/`.
```

`.github/instructions/typescript.instructions.md` adds a path-scoped rule for Copilot:

```markdown
---
applyTo: "**/*.ts"
---
Prefer `unknown` over `any`. All exported functions must have JSDoc comments.
```

`src/auth/CLAUDE.md` adds directory-level constraints that apply only when Claude Code navigates into that subtree:

```markdown
Auth code: never log request payloads. Token handling must use the `crypto` module, not third-party alternatives.
```

With this layout, updating `AGENTS.md` propagates to Claude Code immediately (via import) while Copilot's file needs a manual sync — a deliberate tradeoff that makes the drift surface explicit and small.

## Key Takeaways

- Each major AI coding tool has a project-level instruction file; without a convergence strategy they diverge and become unreliable
- Symlinks to a canonical file or AGENTS.md as a shared base prevent content drift
- Both Claude Code and Copilot support scoped instructions; content categories are consistent: identity, conventions, constraints, navigation pointers

## Unverified Claims

- Content drift between instruction files compounds over time when maintained separately without a convergence strategy.
- Tool-specific "extends" strategies require tooling support for imports or includes.

## Related

- [Getting Started: Setting Up Your Instruction File](../workflows/getting-started-instruction-files.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
- [Prompt File Libraries](prompt-file-libraries.md)
- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [AGENTS.md as Table of Contents, Not Encyclopedia](agents-md-as-table-of-contents.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [Prompt Layering: How Instructions Stack and Override](../context-engineering/prompt-layering.md)
- [Import and Composition Pattern](import-composition-pattern.md)
- [Hierarchical CLAUDE.md](hierarchical-claude-md.md)
- [Convention Over Configuration](convention-over-configuration.md)
- [Content Exclusion Gap](content-exclusion-gap.md)
- [AGENTS.md Distributed Conventions](agents-md-distributed-conventions.md)
- [AGENTS.md Design Patterns](agents-md-design-patterns.md)
- [Evaluating AGENTS.md Context Files](evaluating-agents-md-context-files.md)
