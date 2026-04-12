---
title: "Project Instruction File Ecosystem"
description: "CLAUDE.md, copilot-instructions.md, and AGENTS.md all carry project context for AI tools but differ in discovery and scope. Convergence strategy prevents drift."
aliases:
  - Instruction File Convention
  - Project Instruction Files
tags:
  - instructions
  - tool-agnostic
---

# Project Instruction File Ecosystem

> The instruction file ecosystem is a set of overlapping per-project context files — `CLAUDE.md`, `.github/copilot-instructions.md`, and `AGENTS.md` — that each AI coding tool reads for project conventions, constraints, and workflow rules.

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

GitHub Copilot also reads `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` as "agent-specific" instruction files ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)) — a concrete sign of convergence.

[AGENTS.md](https://agents.md), stewarded by the Linux Foundation, is supported by 20+ tools including OpenAI Codex, Google Jules, Copilot, Cursor, Devin, Aider, Zed, and Windsurf.

## Discovery Differences

**Claude Code** walks up the directory tree, loading every `CLAUDE.md` it finds. Subdirectory files load on demand. `.claude/rules/*.md` files with `paths` frontmatter add glob-scoped instructions that trigger only when matching files are read ([docs](https://code.claude.com/docs/en/memory)).

**GitHub Copilot** uses a multi-tier model. `.github/copilot-instructions.md` applies repository-wide; `*.instructions.md` files in `.github/instructions/` use `applyTo` globs to target specific paths ([docs](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)). All tiers are provided simultaneously. Code review reads only the first 4,000 characters; chat and coding agents have no limit ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)).

**AGENTS.md** uses proximity-based discovery: the closest file to the edited file wins. Monorepos nest files in subdirectories to scope instructions per package ([agents.md](https://agents.md)).

## Content Overlap and Drift

All three files contain the same categories — project context, conventions, constraints, workflow notes. Each tool reads only its own file, so updates to one file don't propagate. Without a convergence strategy, the files diverge independently: one file says "use pnpm", another says "use npm", and agents follow their own source.

## Convergence Strategies

**Single canonical file with symlinks.** Symlink all instruction files to one source of truth. Tradeoff: tool-specific syntax (e.g., Claude Code's [`@path/to/import`](https://code.claude.com/docs/en/memory)) may not work in other tools. Symlinks also require developer setup on Windows, where git does not create them by default.

**Shared base with tool-specific extends.** Claude Code supports this via `@AGENTS.md` import in `CLAUDE.md` ([docs](https://code.claude.com/docs/en/memory)). Copilot lacks cross-file imports, requiring duplication or generation.

**AGENTS.md as canonical standard.** With 20+ compatible tools and Linux Foundation governance, [AGENTS.md](https://agents.md) gives the widest reach.

## Hierarchy as a Feature

All three ecosystems support scoped instruction files — Claude Code via directory-level files and `.claude/rules/` globs, Copilot via `applyTo` patterns, AGENTS.md via proximity. High-sensitivity areas carry additional constraints while root files stay short.

## Size Limits and Practical Constraints

| Tool | Limit | Effect |
|------|-------|--------|
| Claude Code | ~200 lines per `CLAUDE.md` ([docs](https://code.claude.com/docs/en/memory)) | Longer files reduce adherence |
| GitHub Copilot | 4,000 chars for code review ([docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)) | Silently ignored beyond limit in PR review; chat has no limit |
| AGENTS.md | No formal limit | Keep concise for widest compatibility |

Claude Code mitigates this with `.claude/rules/` and `@path/to/import`, both loading content conditionally ([docs](https://code.claude.com/docs/en/memory)).

## What to Include

Include: project identity, conventions, constraints, and navigation pointers. Exclude: full documentation (link instead), architecture diagrams, and single-task content (use a skill).

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

- Without a convergence strategy, multiple instruction files diverge and become unreliable
- AGENTS.md has the widest tool support (20+) and is the strongest candidate for a canonical shared file
- Copilot reads AGENTS.md and CLAUDE.md natively, reducing duplication needs
- Claude Code's `@AGENTS.md` import syntax enables a shared-base-with-extends strategy
- Keep root files short; push specifics into path-scoped overrides

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
- [Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Hints over Code Samples](hints-over-code-samples.md)
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md)
- [Frozen Spec File](frozen-spec-file.md)
