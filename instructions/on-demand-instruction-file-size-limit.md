---
title: "Size Limits on Instruction Files That Load on Demand"
term: "On-Demand Instruction File Size Limit"
description: "Claude Code caps each instruction file that loads on demand at a character count. Past it, the agent gets only the file's start and a pointer to read the rest."
tags:
  - context-engineering
  - instructions
  - claude
aliases:
  - Per-File Instruction Size Cap
  - Partial Instruction File Loading
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-25
status: current
maturity: emerging
---

# Size Limits on Instruction Files That Load on Demand

> An instruction file that loads on demand is capped by character count, and Claude Code injects only its start once the file is over.

Claude Code applies a per-file character limit to instruction files that load on demand: "When a subdirectory `CLAUDE.md` or a rules file that loads on demand is over a per-file size limit, Claude receives only the start of it" ([memory docs](https://code.claude.com/docs/en/memory#claude-ignores-the-end-of-my-subdirectory-claude-md)). The limit arrived in version 2.1.309, released 22 October 2026, whose changelog records both halves of the change in one line: "Fixed sessions compacting repeatedly after reading files under a very large nested CLAUDE.md; a nested CLAUDE.md over the size limit now loads only its start" ([changelog](https://code.claude.com/docs/en/changelog#2-1-309)). "Before v2.1.309, Claude Code didn't apply this limit to files that load on demand" ([memory docs](https://code.claude.com/docs/en/memory#claude-ignores-the-end-of-my-subdirectory-claude-md)).

## Which files are affected, and by what number

The limit covers three kinds of file, each of which loads when the agent touches a matching path rather than at launch ([memory docs](https://code.claude.com/docs/en/memory#claude-ignores-the-end-of-my-subdirectory-claude-md)):

- `CLAUDE.md` and `CLAUDE.local.md` in a subdirectory of your launch directory, plus the files they import with `@path`
- Rules files in a subdirectory's `.claude/rules/`
- Path-scoped rules in the project's `.claude/rules/` or in `~/.claude/rules/`

The threshold is a character count that depends on the session's context window: 40,000 characters at 200K, and at 1M "200,000 characters on Claude Opus 4.6 and Claude Sonnet 4.6, and 150,000 characters on later models" ([memory docs](https://code.claude.com/docs/en/memory#claude-ignores-the-end-of-my-subdirectory-claude-md)). "Sonnet 5 and later, Haiku 5.5, and Opus 4.7 and later run with the 1M window by default", among others ([model config](https://code.claude.com/docs/en/model-config#extended-context)). A session actually running at 1M on those later models gets 150,000; a 200K session gets 40,000. Check the active window: `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` can reduce even a default-1M model to 200K ([model config](https://code.claude.com/docs/en/model-config#turn-off-1m-context)). The docs name `wc -m` as the way to measure a file against it.

## Three size rules, three failure shapes

| File | Rule | What happens past it |
|---|---|---|
| On-demand `CLAUDE.md` or rules file | Character limit by context window | Only the start is injected, with a note to read the rest |
| `CLAUDE.md` that loads at launch | 4 MiB | The file is skipped and none of it loads |
| `MEMORY.md` auto-memory index | First 200 lines or 25KB | Content past the threshold is not loaded at session start |

The launch-time rule is the generous one: "Claude gets the whole of each CLAUDE.md file that loads at launch, as long as the file is 4 MiB or smaller" ([memory docs](https://code.claude.com/docs/en/memory#how-it-works)). The 200-line/25KB loading limit belongs to `MEMORY.md` alone: "This limit applies only to `MEMORY.md`" ([memory docs](https://code.claude.com/docs/en/memory#how-it-works)).

Claude Code also warns about file length, and the docs do not tie that warning to the character cap. "If one of your instruction files is over the recommended length, you see a warning at startup and when you run `/status`" ([memory docs](https://code.claude.com/docs/en/memory#my-claude-md-is-too-large)). The docs give no unit for "the recommended length". Their documented size recommendation is a "target under 200 lines per CLAUDE.md file" ([memory docs](https://code.claude.com/docs/en/memory#write-effective-instructions)), and "Files over 200 lines consume more context and may reduce adherence" ([memory docs](https://code.claude.com/docs/en/memory#my-claude-md-is-too-large)). A second warning fires when files "that are each within that length add up past a combined limit at session start" ([memory docs](https://code.claude.com/docs/en/memory#my-claude-md-is-too-large)). The docs do not say either warning measures the on-demand cap, so a quiet startup is no evidence that a file is under it.

## Why it works

Keeping the rules you cannot afford to lose in the launch-directory file works because of where each loader puts its ceiling. The on-demand loader stops at a fixed character offset and ends what it injected with "a note telling Claude to read the rest with the Read tool, and until Claude chooses to, the later instructions aren't in its context" ([memory docs](https://code.claude.com/docs/en/memory#claude-ignores-the-end-of-my-subdirectory-claude-md)). The launch-time loader has no such offset below 4 MiB, and a project-root `CLAUDE.md` is re-read from disk and re-injected after `/compact` ([memory docs](https://code.claude.com/docs/en/memory)).

Position can affect how a model uses text that reaches its context. In a separate retrieval study, Liu et al. report that "performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts" ([arXiv:2307.03172v3](https://arxiv.org/abs/2307.03172v3)). That study did not test instruction-file truncation. A loader cap removes text before the model can use any positional advantage.

## When this backfires

- Treating the cap as a reason to restructure a short file. Check the actual character count before treating truncation as the cause. Trim it for adherence, which is what the 200-line target is about, and do not call that a truncation fix.
- Splitting the tail into rules files. The documented remedy is to "move part of it into one or more rules files, which each count against the limit on their own" ([memory docs](https://code.claude.com/docs/en/memory#claude-ignores-the-end-of-my-subdirectory-claude-md)). Moving content into path-scoped rules makes those rules load "only when Claude works with matching files" ([memory docs](https://code.claude.com/docs/en/memory#my-claude-md-is-too-large)), so those rules are absent until the matching path triggers them. Unscoped project rules load at launch; splitting alone does not make a rule path-scoped.
- Pinning a repo convention to one number. The threshold moves with the window and the model, so a 40,000-character budget is conservative for a 1M session, while a 150,000-character budget exceeds the 200K session limit.
- Applying the rule to the launch-directory file. That file is governed by the 4 MiB rule, so cutting it to satisfy the on-demand cap addresses the wrong loading mechanism.
- Reading behavior from an older release. The limit reached on-demand files only in 2.1.309 ([memory docs](https://code.claude.com/docs/en/memory#claude-ignores-the-end-of-my-subdirectory-claude-md)), so an observation from an earlier version does not describe the current loader.

## Example

The memory documentation gives this Bash or Zsh check ([memory docs](https://code.claude.com/docs/en/memory#claude-ignores-the-end-of-my-subdirectory-claude-md)):

```bash
wc -m path/to/CLAUDE.md
```

Use the path of the on-demand file being diagnosed. Compare its returned character count with the threshold for the current model and window. The documentation directs you to trim an oversized file or divide it into rules files, each with its own limit. For a file below the threshold, investigate another cause. This procedure does not apply the on-demand cap to a launch-loaded file.

## Key Takeaways

- The limit applies to subdirectory `CLAUDE.md` or `CLAUDE.local.md`, their imports, rules in subdirectory `.claude/rules/`, and path-scoped project or user rules.
- The number is 40,000 characters on a 200K session, 200,000 on Opus 4.6 and Sonnet 4.6 at 1M, and 150,000 on later models at 1M.
- The injected part of an over-limit file ends in a note telling Claude to read the rest, so the tail waits on a Read instead of disappearing.
- Check a file with `wc -m`. The docs state no unit for the startup and `/status` warning, and they never link it to this cap. Their size recommendation is a target under 200 lines.
- A rule that must always be present belongs in the launch-directory file, which loads whole below 4 MiB and is re-injected after compaction.

## Related

- [Hierarchical CLAUDE.md](hierarchical-claude-md.md) — the four scopes these files sit in, and which of them load on demand.
- [Layer Agent Instructions by Specificity Across Scopes](layered-instruction-scopes.md) — the tool-agnostic version, including the Codex cap on assembled instruction content.
- [Critical Instruction Repetition via Primacy and Recency](critical-instruction-repetition.md) — why a rule gets placed at the end of a file in the first place.
- [@import Composition Pattern for Instruction Files](import-composition-pattern.md) — the separate five-level ceiling on `@path` import depth.
- [claudeMdExcludes: Selective Ancestor Instruction-File Exclusion](claude-md-excludes.md) — keeping another team's instruction files out of the load entirely.
