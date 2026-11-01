---
title: "Overwriting a File After a Partial Read"
term: "Partial-Read Overwrite"
description: "A reader that truncates to protect the context window plus a writer that accepts whole-file content deletes every byte the agent never saw, and reports success."
tags:
  - anti-pattern
  - context-engineering
  - claude
aliases:
  - partial read then overwrite
  - truncated read whole-file write
  - unobserved region delete
last_reviewed: 2026-10-30
maturity: adopted
status: current
---

# Overwriting a File After a Partial Read

> A truncating read plus a whole-file write deletes everything the agent never saw, and the write call is where a harness can stop it.

Neither tool is wrong alone. The reader truncates because the file does not fit the budget it was given. The writer replaces the file because a whole-file write has no way to say "keep the rest". Compose them and the region past the cut is deleted, with a success report and no error.

## How two safety behaviors composed

Claude Code's changelog records the chain one entry at a time ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

- 2.1.145, May 19 2026, softened the read: "a truncated first page with a 'PARTIAL view' notice instead of a hard error when a whole-file read exceeds the token limit".
- 2.1.228, August 11 2026, softened the write: "newer models can overwrite an existing file they haven't read this session".
- 2.1.312, October 27 2026, landed the guard: "Fixed Claude overwriting a very large CLAUDE.md, rules file or @-included file in a subdirectory after seeing only its start; Write now asks Claude to read it all or edit in place".

Every file class that entry names is an instruction file. That is the worst case, because an agent rewriting the rules it runs under destroys the constraints it was operating under.

The shape is not one vendor's, and it is not confined to a context limit. GitLab's `add_commit` MCP tool hit the same composition at a 10 MB blob cap, described in the Example below ([GitLab merge request 251919](https://gitlab.com/gitlab-org/gitlab/-/merge_requests/251919)). The general pair is any truncating reader feeding any replacing writer, a paged API read driving a `PUT` included.

## Why it works

Truncation is unobservable from the truncated content. The dropped bytes leave no trace in what the reader returned, so detection needs a size reported out of band. That is what GitLab's guard keys off: `size` "reflects the full blob size reported by Gitaly, not the (possibly truncated) loaded byte count" ([GitLab merge request 251919](https://gitlab.com/gitlab-org/gitlab/-/merge_requests/251919)).

The check belongs on the write because the write has nothing to validate against. An anchored edit carries an `old_string` the harness can match against the file on disk. A whole-file write asserts only the end state. The review on AMD's GAIA pull request states why: "Keeping `file_write` strict, since it names no `old_string`, is the right asymmetry" ([amd/gaia pull request 3395](https://github.com/amd/gaia/pull/3395)).

A prompt rule cannot carry it. Prompt-level guardrails are "natural language instructions that operate at the same abstraction level as the threats they attempt to mitigate" ([Fokou, 2026, arXiv:2604.12986v1](https://arxiv.org/abs/2604.12986v1)).

## When this backfires

- Appending to a very large generated file. A complete read makes a one-line append to a multi-megabyte log unaffordable. The two vendors route around that cost in opposite directions, Claude Code toward the anchored edit and GitLab toward full content. Neither remedy is the general one.
- A file that changed on disk after the read. Completeness says nothing about freshness, so a full read satisfies the precondition and still clobbers a sibling agent's newer version. GAIA carries a separate stale-read rejection for that case ([amd/gaia pull request 3395](https://github.com/amd/gaia/pull/3395)).
- The edit-in-place branch fails quietly too. A non-unique anchor produced "a real edit, of the right shape, in the wrong place" with a success report, which the same pull request calls "the failure mode least likely to be caught in review" ([amd/gaia pull request 3395](https://github.com/amd/gaia/pull/3395)).
- Read-tracking state scoped per process. GAIA's tracker is a module singleton, so in its Agent UI server one session's write re-anchors the ledger for every other session. A second agent then edits content it never saw ([amd/gaia pull request 3395](https://github.com/amd/gaia/pull/3395)).
- Rollback complements prevention. Parallax refuses first and snapshots as well: "Before any destructive or irreversible action, the system captures state sufficient for rollback" ([Fokou, 2026, arXiv:2604.12986v1](https://arxiv.org/abs/2604.12986v1)). The paper adds it for the residual risk that remains when every pre-execution mechanism is bypassed. The guarantee stops at the local environment.

## Example

**Before — partial edit submitted as the whole file**: GitLab's `add_commit` MCP tool loaded a target file through a 10 MB cap, where the loader "returns silently truncated content — no error, no nil". The service matched `old_str` in the truncated content, substituted, and submitted that blob as the file's full content, which "silently deletes everything past the first 10 MB of the file while reporting a successful commit" ([GitLab merge request 251919](https://gitlab.com/gitlab-org/gitlab/-/merge_requests/251919)).

**After — the precondition rejects the call**: the same service now rejects any partial-edit target whose reported blob size exceeds the cap, "raising a `PartialEditError` instructing the caller to submit full file content instead" ([GitLab merge request 251919](https://gitlab.com/gitlab-org/gitlab/-/merge_requests/251919)). Claude Code's guard has the same shape and a different escape route: Write "asks Claude to read it all or edit in place" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

## Key Takeaways

- Check your harness version. The Claude Code fix is in 2.1.312, and the loosening it corrects shipped 11 weeks earlier in 2.1.228.
- A completeness check must read a size the tool reports, never the bytes it returned.
- Prefer an anchored edit over a whole-file write on any file past the read limit. The anchor gives the harness something to verify.
- The precondition covers completeness only. Staleness and non-unique anchors need their own rejections.
- Keep instruction files in version control. The precondition is the whole defense where there is no commit to recover from.

## Related

- [Graceful Tool-Output Truncation: The PARTIAL Signal](../../tool-engineering/graceful-tool-output-truncation.md)
- [A Guard Hook Approves the Truncated Input It Was Handed](guard-approves-truncated-input.md)
- [Edit Format Selection: Diff vs. Search-Replace vs. Full Rewrite](../../tool-engineering/llm-edit-format-selection.md)
- [Rollback-First Design](../agent-design/rollback-first-design.md)
- [Catastrophic Remembering: Instruction Files That Only Grow](catastrophic-remembering-instruction-files.md)
