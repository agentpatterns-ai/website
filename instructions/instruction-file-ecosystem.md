---
title: "Project Instruction File Ecosystem"
description: "Every major AI coding tool invented a project-level instruction file independently — understanding how these files relate helps teams working across tools avoid content drift and duplication."
aliases:
  - Instruction File Convention
  - Project Instruction Files
tags:
  - instructions
  - tool-agnostic
---

# Project Instruction File Ecosystem

> Every major AI coding tool invented a project-level instruction file independently — understanding how these files relate helps teams working across tools avoid content drift and duplication.

??? note "Also known as: Instruction File Convention, Project Instruction Files"
    This page is the tool-agnostic overview. For tool-specific details, see:

    - [CLAUDE.md Convention](claude-md-convention.md) — Claude Code's project-level instruction file
    - [copilot-instructions.md Convention](../tools/copilot/copilot-instructions-md-convention.md) — GitHub Copilot's repository-level instruction file

## The Same Problem, Different Files

Each AI coding assistant needs project context. Multiple tools means multiple instruction files:

| Tool | File | Scope |
|------|------|-------|
| Claude Code | `CLAUDE.md` ([docs](https://code.claude.com/docs/en/memory)) | Managed policy → project → user; subdirectory files load on demand |
| GitHub Copilot | `.github/copilot-instructions.md` + `.github/instructions/*.instructions.md` ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)) | Organization → repository-wide → path-specific → personal |
| AGENTS.md-compatible tools | `AGENTS.md` ([standard](https://agents.md)) | Closest file to edited file wins; nested in subdirectories |

GitHub Copilot also reads `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` as "agent-specific" instruction files, though with limited feature support compared to its native `.github/copilot-instructions.md` ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)). This cross-reading is a concrete sign of convergence.

The [AGENTS.md open standard](https://agents.md), now stewarded by the Agentic AI Foundation under the Linux Foundation, is supported by 20+ tools including OpenAI Codex, Google Jules, GitHub Copilot, Cursor, Devin, Aider, Zed, and Windsurf ([agents.md](https://agents.md)).

## Discovery Differences

**Claude Code** walks up the directory tree from the working directory, loading every `CLAUDE.md` it finds. Subdirectory files load on demand when the agent navigates there. Claude Code also supports `.claude/rules/*.md` files with `paths` frontmatter for glob-scoped instructions that only trigger when matching files are read ([docs](https://code.claude.com/docs/en/memory)). A `src/auth/CLAUDE.md` can add constraints specific to authentication code without affecting the rest of the project.

**GitHub Copilot** uses a multi-tier model. `.github/copilot-instructions.md` applies repository-wide; path-specific `*.instructions.md` files in `.github/instructions/` use `applyTo` frontmatter globs to target specific files or directories ([docs](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)). All relevant tiers are provided simultaneously ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)). Copilot code review reads only the first 4,000 characters of instruction files; chat and coding agents have no character restriction ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)).

**AGENTS.md** uses proximity-based discovery: the closest `AGENTS.md` to the edited file wins, with explicit user prompts overriding everything. Monorepos can nest files in subdirectories — large projects like OpenAI's repository use dozens of AGENTS.md files to scope instructions per package ([agents.md](https://agents.md)).

## Content Overlap and Drift

All three files typically contain the same categories: project context, coding conventions, architectural constraints, workflow notes. When maintained separately without a convergence strategy, content diverges [unverified] — one file says "use pnpm", another says "use npm", and each agent follows whatever its tool reads. Architectural decisions recorded in one file may not appear in others [unverified], making the files unreliable as context sources.

## Convergence Strategies

**Single canonical file with symlinks.** Maintain one source of truth (`AGENTS.md` or `CLAUDE.md`) and symlink the others to it. The tradeoff: tool-specific syntax (e.g., Claude Code's [`@path/to/import` syntax](https://code.claude.com/docs/en/memory)) may not be supported by other tools.

**Shared base with tool-specific extends.** Maintain a base file with project-wide content, and tool-specific files that import the base and add tool-specific configuration. Claude Code supports this natively via `@AGENTS.md` import syntax in `CLAUDE.md` ([docs](https://code.claude.com/docs/en/memory)). Copilot does not support cross-file imports, so its instructions must be duplicated or generated.

**AGENTS.md as the canonical standard.** The [AGENTS.md open standard](https://agents.md) is tool-agnostic by design and now governed by the Linux Foundation. With 20+ compatible tools, authoring for AGENTS.md gives the widest native reach. Non-compatible tools still need their own file, but the canonical content lives in one place.

## Hierarchy as a Feature

All three ecosystems support scoped instruction files. Claude Code uses directory-level `CLAUDE.md` files and `.claude/rules/*.md` with `paths` frontmatter globs. Copilot uses `*.instructions.md` files with `applyTo` glob patterns. AGENTS.md uses proximity — the nearest file to the edited file takes precedence. All three let high-sensitivity areas carry additional constraints while keeping the root file short.

## Size Limits and Practical Constraints

| Tool | Limit | Effect |
|------|-------|--------|
| Claude Code | ~200 lines per `CLAUDE.md` recommended ([docs](https://code.claude.com/docs/en/memory)) | Longer files consume more context and reduce adherence |
| GitHub Copilot | 4,000 characters for code review ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)) | Content beyond this is silently ignored during PR review; chat has no limit |
| AGENTS.md | No formal limit | Practical limit is tool-dependent — keep files concise for widest compatibility |

Claude Code mitigates the size constraint with `.claude/rules/` path-scoped files and `@path/to/import` syntax, both of which load content conditionally rather than front-loading everything ([docs](https://code.claude.com/docs/en/memory)).

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
CLAUDE.md                                      # Claude Code entry point (imports AGENTS.md)
.claude/
  rules/
    auth-security.md                           # Claude Code path-scoped rule
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
- AGENTS.md, governed by the Linux Foundation, has the widest tool support (20+) and is the strongest candidate for a canonical shared file
- GitHub Copilot now reads AGENTS.md and CLAUDE.md natively as "agent-specific" instruction files, reducing the need for duplication
- Claude Code's `@AGENTS.md` import syntax enables a shared-base-with-extends strategy where `AGENTS.md` holds canonical content and `CLAUDE.md` adds tool-specific configuration
- All three ecosystems support scoped/hierarchical instructions; keep root files short and push specifics into path-scoped overrides
- Respect size limits: ~200 lines for CLAUDE.md, 4,000 characters for Copilot code review

## Unverified Claims

- Content drift between instruction files compounds over time when maintained separately without a convergence strategy.
- Whether Cursor's `.cursor/rules/` system reads AGENTS.md natively.
- Whether the symlink convergence strategy works reliably across all tools and operating systems, particularly Windows symlinks with git.
- The 60,000+ project adoption figure for AGENTS.md is self-reported by the standard's website.

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
