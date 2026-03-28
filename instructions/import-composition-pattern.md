---
title: "@import Composition Pattern for Agent Instruction Files"
description: "Use Claude Code's @path/to/file import syntax to compose CLAUDE.md from smaller, reusable files — and understand why other tools don't support it."
tags:
  - context-engineering
  - instructions
  - technique
  - tool-agnostic
---

# @import Composition Pattern for Instruction Files

> Claude Code supports `@path/to/file` imports in CLAUDE.md, enabling modular instruction authoring. Other major agent tools do not — they rely on hierarchical discovery instead.

## How Claude Code Imports Work

CLAUDE.md files can reference other files with `@path/to/file` syntax. At session start, Claude Code expands all imports and loads them into context ([docs](https://code.claude.com/docs/en/memory#import-additional-files)).

Rules:

- Both relative and absolute paths are supported
- Relative paths resolve from the importing file, not the working directory
- Imports nest up to five levels deep
- First encounter triggers an approval dialog; declined imports stay disabled

```text
# CLAUDE.md

See @README for project overview and @package.json for available npm scripts.

## Additional Instructions
- Git workflow: @docs/git-workflow.md
- Code style: @docs/code-style.md

# Individual Preferences
- @~/.claude/my-project-preferences.md
```

Each referenced file is pulled in verbatim — semantically equivalent to concatenation at session start.

## Known Limitation: Tilde Expansion

As of late 2025, `@~/.claude/file.md` references (tilde home-directory expansion) are silently not loaded in some configurations ([Issue #8765](https://github.com/anthropics/claude-code/issues/8765)). Use absolute paths as a workaround:

```text
# Works
@/home/username/.claude/my-preferences.md

# May silently fail
@~/.claude/my-preferences.md
```

## When to Use Imports vs `.claude/rules/`

Imports and `.claude/rules/` both modularise instructions. The distinction is load timing:

| Mechanism | When it loads | Best for |
|-----------|--------------|---------|
| `@path` imports | At session start, always | Core project context shared across all files |
| `.claude/rules/*.md` without `paths` | At session start (same as CLAUDE.md) | Topically organised rules that always apply |
| `.claude/rules/*.md` with `paths` frontmatter | On demand, when matching files are opened | Language- or directory-specific conventions |

Use imports when you want to pull external content (README, package.json, a canonical AGENTS.md) into CLAUDE.md without duplicating it. Use `.claude/rules/` when you want path-scoped rules that activate only when the agent works in a specific area.

## DRY Instruction Authoring

The main use case for imports is a single-source-of-truth for project conventions shared across tools or across team members:

```
project-root/
├── AGENTS.md                      # canonical project context (tool-agnostic)
├── CLAUDE.md                      # imports AGENTS.md, adds Claude-specific config
└── .github/
    └── copilot-instructions.md    # manual copy — Copilot has no import support
```

`CLAUDE.md` imports the canonical file:

```text
@AGENTS.md

## Claude Code
Use [worktrees](../workflows/worktree-isolation.md) for experimental work.
Check subdirectory CLAUDE.md files — auth code has additional constraints.
```

`.github/copilot-instructions.md` must duplicate the shared content because Copilot has no equivalent syntax. The drift surface is small and explicit.

User-specific preferences stay out of version control by importing from `~/.claude/`:

```text
# CLAUDE.md (checked in)
@~/.claude/my-project-preferences.md
```

The import reference is checked in; the file it points to stays local. Teammates who lack the file see the import silently skipped.

## Cross-Tool Comparison

| Tool | File inclusion syntax | Mechanism for modularity |
|------|----------------------|--------------------------|
| Claude Code | `@path/to/file` in CLAUDE.md ([docs](https://code.claude.com/docs/en/memory)) | Import expansion at load time |
| Claude Code (alternative) | `.claude/rules/*.md` with `paths` frontmatter | Path-scoped rules, demand-loaded |
| GitHub Copilot | None | Hierarchical discovery: nested AGENTS.md, `applyTo` globs in `.github/instructions/` |
| OpenAI Codex | None | Directory traversal + concatenation root-down |
| Cursor | `@file` within `.cursor/rules/*.mdc` | Context attachment, not import expansion [unverified] |

**Failure mode for unsupported tools**: `@AGENTS.md` in a Copilot instructions file passes through as literal Markdown text [unverified]. The model may attempt to interpret it as a file path or ignore it — there is no error.

## Example: Shared Base with Tool-Specific Extends

A team maintains a shared `shared/base-instructions.md` that both a project CLAUDE.md and a user CLAUDE.md import:

```
project-root/
├── CLAUDE.md
└── shared/
    └── base-instructions.md    # shared conventions (not a CLAUDE.md, just a .md file)
```

```text
# shared/base-instructions.md

## Commit format
Use Conventional Commits. Types: feat, fix, docs, chore, refactor.

## Testing
Run `pnpm test` before committing. All tests must pass.
```

```text
# CLAUDE.md
@shared/base-instructions.md

## Project-Specific
- API handlers live in `src/api/`; one file per resource
- Use `zod` for all input validation
```

```text
# ~/.claude/CLAUDE.md  (user scope, not version-controlled)
@shared/base-instructions.md

## Personal preferences
- Prefer concise responses without preamble
```

Both CLAUDE.md files stay short; shared content lives once.

## Key Takeaways

- Claude Code's `@path` import syntax is shipped and documented — imported files load at session start alongside CLAUDE.md
- Tilde expansion (`@~/...`) is unreliable; use absolute paths for home-directory imports
- Imports and `.claude/rules/` are complementary, not alternatives — imports for external content, rules for path-scoped conventions
- GitHub Copilot, OpenAI Codex, and AGENTS.md standard do not support file inclusion — modularity comes from hierarchical discovery, not imports
- Unsupported `@`-syntax in other tools passes through as literal text with no error

## Unverified Claims

- Declined import approvals cannot be re-enabled without manually editing a configuration file — the approval dialog does not re-appear.
- Cursor's `@file` reference in `.cursor/rules/*.mdc` files attaches context at rule-evaluation time rather than expanding the referenced file's content inline in the rule body.

## Related

- [CLAUDE.md Convention](claude-md-convention.md)
- [Hierarchical CLAUDE.md](hierarchical-claude-md.md)
- [Project Instruction File Ecosystem](instruction-file-ecosystem.md)
- [Layer Agent Instructions by Specificity](layered-instruction-scopes.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [AGENTS.md Design Patterns](agents-md-design-patterns.md)
- [Distributed Conventions via AGENTS.md](agents-md-distributed-conventions.md)
- [Prompt File Libraries](prompt-file-libraries.md)
