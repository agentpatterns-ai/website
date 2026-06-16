---
title: "claudeMdExcludes: Selective Ancestor Instruction-File Exclusion"
term: "claudeMdExcludes"
description: "Skip irrelevant ancestor CLAUDE.md files in a monorepo with a glob list, so the agent's context is not burned on conventions for packages you never touch."
tags:
  - instructions
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-05-30
maturity: emerging
---

# claudeMdExcludes: Selective Ancestor Instruction-File Exclusion

> Skip specific ancestor CLAUDE.md files by glob so an agent launched from a monorepo root does not load conventions for packages it never touches.

In a large monorepo, every ancestor CLAUDE.md loads at session start when Claude Code walks the directory tree from the working directory ([memory docs](https://code.claude.com/docs/en/memory#how-claude-md-files-load)). Subdirectory files load on demand when the agent reads a file in them. Launched from the repo root, that pulls every team's conventions into context before the first task token.

The `claudeMdExcludes` setting suppresses specific files by path or glob pattern, so they never load ([memory docs](https://code.claude.com/docs/en/memory#exclude-specific-claude-md-files)).

## The Setting

`claudeMdExcludes` is an array of glob patterns matched against **absolute file paths**. Place it in any settings layer — managed, project, user, or local ([memory docs](https://code.claude.com/docs/en/memory#exclude-specific-claude-md-files)):

```json title=".claude/settings.local.json"
{
  "claudeMdExcludes": [
    "**/packages/admin-dashboard/**",
    "**/packages/legacy-*/**"
  ]
}
```

This skips every CLAUDE.md and `.claude/rules/*.md` file under those packages. The root CLAUDE.md and any package you do work in still load normally ([large-codebases docs](https://code.claude.com/docs/en/large-codebases#exclude-irrelevant-claude-md-files)).

Common pattern shapes:

| Pattern | Effect |
|---------|--------|
| `**/packages/*/CLAUDE.md` | Excludes every package's CLAUDE.md while keeping the root |
| `**/packages/web/**` | Excludes everything under the web package, including rules |
| `/home/user/monorepo/legacy/CLAUDE.md` | Excludes one specific file by absolute path |

Patterns are matched against absolute paths, so start relative-style patterns with `**/` to match anywhere in the tree ([large-codebases docs](https://code.claude.com/docs/en/large-codebases#exclude-irrelevant-claude-md-files)).

## Scope Merging

Arrays merge across [settings scopes](https://code.claude.com/docs/en/settings#configuration-scopes) ([memory docs](https://code.claude.com/docs/en/memory#exclude-specific-claude-md-files)). A team can commit project-level exclusions in `.claude/settings.json` while individuals append personal exclusions in `.claude/settings.local.json` — the merge is additive, so local scopes cannot remove patterns set higher up.

The [official guidance](https://code.claude.com/docs/en/large-codebases#exclude-irrelevant-claude-md-files) is to put personal exclusions in `.claude/settings.local.json` (gitignored) rather than committing one developer's task scope to the team config.

## What Cannot Be Excluded

Managed-policy CLAUDE.md files cannot be excluded by `claudeMdExcludes` ([memory docs](https://code.claude.com/docs/en/memory#exclude-specific-claude-md-files)). Organisation-wide instructions deployed via MDM, Group Policy, or the `claudeMd` key in managed settings always load, regardless of individual configuration. If a managed file contains the rule you wanted to skip, no project- or user-level exclusion will suppress it — the fix lives with the policy owner, not in your settings.

## Where Selective Exclusion Fits

Three independent levers control what reaches an agent's context in a monorepo:

| Lever | What it controls | Mechanism |
|-------|------------------|-----------|
| [Hierarchical CLAUDE.md](hierarchical-claude-md.md) | What is *written* per directory | Per-directory files load only on demand |
| [Sparse-checkout worktrees](../tools/claude/sparse-paths-monorepo-isolation.md) | What is *on disk* in the worktree | `worktree.sparsePaths` cone-mode checkout |
| `claudeMdExcludes` | What *loads at launch* from existing files | Glob suppression during ancestor walk |

The first two reduce upstream — fewer files exist or fewer files are checked out. `claudeMdExcludes` is the suppression layer over what is already there: useful when you cannot or do not want to restructure the tree.

## Example

A monorepo has three packages and a root CLAUDE.md. You work in `packages/api/` daily but launch Claude from the repo root because most sessions need access to root-level scripts.

```text
monorepo/
  CLAUDE.md
  packages/
    api/CLAUDE.md
    admin-dashboard/CLAUDE.md
    legacy-billing/CLAUDE.md
```

Without exclusions, every launch loads the root file plus all three package files on demand. The admin-dashboard and legacy-billing conventions burn context on rules the agent will never apply.

Commit a team baseline that excludes the legacy package (no one works there) in `.claude/settings.json`:

```json title=".claude/settings.json"
{
  "claudeMdExcludes": [
    "**/packages/legacy-*/**"
  ]
}
```

Append your personal exclusion for admin-dashboard in `.claude/settings.local.json` so teammates who do work on it keep loading it:

```json title=".claude/settings.local.json"
{
  "claudeMdExcludes": [
    "**/packages/admin-dashboard/**"
  ]
}
```

The merged exclusion list at launch contains both patterns. Your session loads the root CLAUDE.md plus `packages/api/CLAUDE.md` on demand. Sibling packages stay out of context until you actually need them.

## Why It Works

Claude Code loads CLAUDE.md content as a user message after the system prompt, and every byte counts against the same context window the conversation will use ([memory docs](https://code.claude.com/docs/en/memory#troubleshoot-memory-issues)). [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) shows that aggregate instruction load — not file count — drives degradation: doubling the number of rules in scope makes the agent less likely to follow any one of them. `claudeMdExcludes` works because it intercepts the discovery step itself. Matched files are never read, never tokenised, never concatenated into the launch context. The scope-merging semantic preserves a team-shared baseline while letting individuals add personal suppressions without an overwrite war.

## When This Backfires

`claudeMdExcludes` is a sharp instrument. Conditions where the trade-off goes the other way:

- **Cross-package tasks**: a refactor that touches `packages/api/` and `packages/admin-dashboard/` will silently lose the admin-dashboard conventions if that package is excluded. The agent does not know it is missing context — it just guesses. For task-by-task scoping, the [official guidance](https://code.claude.com/docs/en/large-codebases#exclude-irrelevant-claude-md-files) is to launch from the relevant subdirectory instead, which Claude treats as the new tree root.
- **Masking instruction-file bloat**: if the root CLAUDE.md is itself >1000 lines, excluding sibling files reduces token cost but the real fix is trimming the root toward the [200-line target](https://code.claude.com/docs/en/memory#write-effective-instructions). Exclusion that hides bloat removes the pressure to prune.
- **Managed-policy carve-out misunderstood**: a teammate may try to exclude an organisation-deployed CLAUDE.md and see it keep loading. Managed files [cannot be excluded](https://code.claude.com/docs/en/memory#exclude-specific-claude-md-files) — the suppression silently no-ops on that one entry.
- **Absolute paths ported across machines**: `/home/alice/monorepo/legacy/CLAUDE.md` works for Alice and silently fails for Bob whose checkout sits elsewhere. Use `**/`-prefixed patterns for portability across teammates and CI runners.
- **Per-developer scope committed as team policy**: pushing a narrow `claudeMdExcludes` into `.claude/settings.json` forces every teammate to inherit one developer's view. Personal exclusions belong in `.claude/settings.local.json`.

## Key Takeaways

- `claudeMdExcludes` skips ancestor CLAUDE.md and `.claude/rules/*.md` files by glob during launch-time discovery.
- Patterns match absolute paths; start them with `**/` for portability.
- Arrays merge across managed, project, user, and local settings scopes — team baseline plus personal additions.
- Managed-policy CLAUDE.md files cannot be excluded; organisation rules always load.
- The list is static. For task-by-task scoping, launch Claude from the relevant subdirectory.

## Related

- [Hierarchical CLAUDE.md](hierarchical-claude-md.md)
- [Sparse-Checkout Worktrees for Monorepo Agent Isolation](../tools/claude/sparse-paths-monorepo-isolation.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [CLAUDE.md Convention for Structuring Agent Instructions](claude-md-convention.md)
- [Project Instruction File Ecosystem](instruction-file-ecosystem.md)
