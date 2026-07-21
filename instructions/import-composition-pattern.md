---
title: "@import Composition Pattern for Agent Instruction Files"
term: "@import Composition Pattern"
description: "Use Claude Code's @path/to/file import syntax to compose CLAUDE.md from smaller, reusable files — and understand why other tools don't support it."
tags:
  - context-engineering
  - instructions
  - technique
  - claude
last_reviewed: 2026-05-27
maturity: emerging
---

# @import Composition Pattern for Instruction Files

> Claude Code supports `@path/to/file` imports in CLAUDE.md, enabling modular instruction authoring. Other major agent tools do not — they rely on hierarchical discovery instead.

Related lesson: [The Layer Stack](https://learn.agentpatterns.ai/context-engineering/prompt-layering/) covers this concept in a hands-on lesson with quizzes.

## How Claude Code imports work

CLAUDE.md files can reference other files with `@path/to/file` syntax. At session start, Claude Code expands every import and loads it into context ([Claude Code memory docs](https://code.claude.com/docs/en/memory#import-additional-files)).

Rules:

- Imports accept both relative and absolute paths
- Relative paths resolve from the importing file, not the working directory
- Imports nest up to five levels deep
- The first import triggers an approval dialog. Decline it and the import stays disabled, with no repeat prompt ([Claude Code memory docs](https://code.claude.com/docs/en/memory#import-additional-files))

```text
# CLAUDE.md

See @README for project overview and @package.json for available npm scripts.

## Additional Instructions
- Git workflow: @docs/git-workflow.md
- Code style: @docs/code-style.md

# Individual Preferences
- @~/.claude/my-project-preferences.md
```

Claude Code pulls in each referenced file verbatim — the same as concatenating them at session start.

## Known limitation: tilde expansion

As of late 2025, Claude Code silently skips `@~/.claude/file.md` references (tilde home-directory expansion) in some configurations ([Issue #8765](https://github.com/anthropics/claude-code/issues/8765)). Use an absolute path instead:

```text
# Works
@/home/username/.claude/my-preferences.md

# May silently fail
@~/.claude/my-preferences.md
```

## When to use imports vs `.claude/rules/`

Imports and `.claude/rules/` both modularize instructions. They differ in when they load:

| Mechanism | When it loads | Best for |
|-----------|--------------|---------|
| `@path` imports | At session start, always | Core project context shared across all files |
| `.claude/rules/*.md` without `paths` | At session start (same as CLAUDE.md) | Topically organized rules that always apply |
| `.claude/rules/*.md` with `paths` frontmatter | On demand, when matching files are opened | Language- or directory-specific conventions |

Use imports to pull external content (README, package.json, a canonical AGENTS.md) into CLAUDE.md without duplicating it. Use `.claude/rules/` for path-scoped rules that activate only when the agent works in a specific area.

## DRY instruction authoring

Imports work best as a single source of truth for project conventions shared across tools or team members:

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

[`.github/copilot-instructions.md`](../tools/copilot/copilot-instructions-md-convention.md) must duplicate the shared content because Copilot has no equivalent syntax. The drift surface is small and explicit.

Importing from `~/.claude/` keeps user-specific preferences out of version control:

```text
# CLAUDE.md (checked in)
@~/.claude/my-project-preferences.md
```

You check in the import reference, but the file it points to stays local. Teammates who lack the file see the import skipped silently.

## Cross-tool comparison

| Tool | File inclusion syntax | Mechanism for modularity |
|------|----------------------|--------------------------|
| Claude Code | `@path/to/file` in CLAUDE.md ([memory docs](https://code.claude.com/docs/en/memory)) | Import expansion at load time |
| Claude Code (alternative) | `.claude/rules/*.md` with `paths` frontmatter | Path-scoped rules, demand-loaded |
| GitHub Copilot | None | Hierarchical discovery: nested AGENTS.md, `applyTo` globs in `.github/instructions/` |
| OpenAI Codex | None | Directory traversal + concatenation root-down |
| Cursor | `@file` within `.cursor/rules/*.mdc` | Context attachment (referenced file appended as context at rule evaluation, not expanded inline into the rule body) |

Failure mode for unsupported tools: `@AGENTS.md` in a Copilot instructions file is not a supported directive — it passes through as literal Markdown text. The model may try to interpret it as a file path or ignore it, with no error.

## Example: shared base with tool-specific extends

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

## When this backfires

- Silent broken imports: renaming or moving an imported file breaks the reference with no error. Claude loads fewer instructions than expected, and the failure stays invisible.
- Approval-dialog friction: the first-use approval dialog blocks imports in headless or CI runs, where no interactive session can click through.
- Nesting limit: import chains stop at five levels. Claude Code truncates a deeply composed set that exceeds the limit at load time, with no warning.
- Tilde expansion is unreliable: `@~/.claude/file.md` fails silently in some configurations (closed as NOT_PLANNED: [Issue #8765](https://github.com/anthropics/claude-code/issues/8765)). Absolute paths are the only reliable workaround.

## Key Takeaways

- Claude Code's `@path` import syntax is shipped and documented — imported files load at session start alongside CLAUDE.md
- Tilde expansion (`@~/...`) is unreliable; use absolute paths for home-directory imports
- Imports and `.claude/rules/` are complementary, not alternatives — imports for external content, rules for path-scoped conventions
- GitHub Copilot, OpenAI Codex, and AGENTS.md standard do not support file inclusion — modularity comes from [hierarchical discovery](../tools/copilot/monorepo-hierarchical-discovery.md), not imports
- Unsupported `@`-syntax in other tools is not processed — it either appears as literal text or is silently ignored, with no error

## Related

- [CLAUDE.md Convention](claude-md-convention.md)
- [Hierarchical CLAUDE.md](hierarchical-claude-md.md)
- [Project Instruction File Ecosystem](instruction-file-ecosystem.md)
- [Layer Agent Instructions by Specificity](layered-instruction-scopes.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [AGENTS.md Design Patterns](agents-md-design-patterns.md)
- [Distributed Conventions via AGENTS.md](agents-md-distributed-conventions.md)
- [Prompt File Libraries](prompt-file-libraries.md)
- [Prompt Transpilation: Instructions as Build Artifacts](prompt-transpilation.md)
