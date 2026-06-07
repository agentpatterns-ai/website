---
title: "ACID for Agent Repository State"
description: "Apply database transaction theory — Atomicity, Consistency, Isolation, Durability — as the operating model for how an agent commits, verifies, partitions, and persists its work in the repo."
tags:
  - agent-design
  - memory
  - tool-agnostic
aliases:
  - ACID agent commits
  - transactional agent state
last_reviewed: 2026-06-01
---

# ACID for Agent Repository State

> Apply database transaction theory — Atomicity, Consistency, Isolation, Durability — as the operating contract for how an agent commits, verifies, partitions, and persists repository work.

## Why ACID, Not Another Mnemonic

"Save your state," "commit progress," "leave the repo clean" — each phrase is vague. ACID — Codd and Gray's four-property contract for database transactions — supplies a precise mapping. Each letter names an observable discipline with a verification step; together they describe a repository that survives both context compaction and concurrent writers.

The [WalkingLabs harness-engineering lecture](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) applies ACID directly to agent state. The four properties are not metaphors — they are the operating contract.

## Atomicity

> Each logical operation maps to exactly one commit; a partial failure rolls the working tree back to a clean state.

The unit is the logical operation, not the file. "Add new endpoint and update tests" is one commit. The [WalkingLabs lecture](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) is explicit: "Each 'logical operation' (e.g., 'add new endpoint and update tests') gets one git commit." On partial failure the agent stashes or resets to the pre-operation state — half-applied changes do not persist.

Atomicity is what makes [Rollback-First Design](rollback-first-design.md) tractable. If a commit holds one logical unit, `git revert <sha>` undoes that unit cleanly. If a commit holds three half-finished units, revert is ambiguous.

## Consistency

> A verification predicate runs before every commit; broken invariants never persist.

Tests pass, lint passes, build passes — the predicate. The [WalkingLabs lecture](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) states it directly: "all tests pass, lint reports zero errors" before committing, with "the agent runs verification after each operation; inconsistent intermediate states don't get committed."

This converts agent self-report into an externalised contract. Per [Anthropic's harness post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), agents are optimistic about completion when not externally verified — they "make code changes, and even do testing with unit tests or `curl` commands against a development server, but would fail to recognize that the feature didn't work end-to-end." A predicate satisfied via tool calls — not via the agent's assertion that it ran — closes the optimism loop. Pair this with a [Feature List File](../instructions/feature-list-files.md) and the predicate becomes auditable.

## Isolation

> Concurrent agents work on disjoint branches or per-agent progress files; neither observes the other's in-flight state.

The [WalkingLabs lecture](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) prescribes: "each agent uses its own progress file, or use git branches for isolation." Branches isolate file writes; per-agent progress files isolate scratchpad state.

Git provides no transaction manager — isolation here is partitioning by convention, not serialization. If two agents target the same file on different branches, the conflict surfaces at merge time, not at write time. Treat branch-per-agent as write-disjoint coordination, not serialization — see [Worktree Isolation](../workflows/worktree-isolation.md) for the filesystem-level enforcement.

## Durability

> Cross-session knowledge lives in git-tracked files; nothing critical exists only in chat history, Slack, or human memory.

Per the [WalkingLabs lecture](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md), "critical project knowledge lives in git-tracked files" and "cross-session knowledge must be persisted to files." [Anthropic's harness post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) supplies the operational form: a `claude-progress.txt` log committed alongside code so subsequent sessions read the prior session's state from the repo, not from an absent context window.

Durability defeats compaction. The context window forgets; git does not. The corollary is [Discoverable vs Non-Discoverable Context](../context-engineering/discoverable-vs-nondiscoverable-context.md) — once knowledge is in the repo, the agent finds it via file reads instead of re-loading it every turn.

## When Strict ACID Backfires

The four properties are not equally valuable in every workflow:

- **Single-session greenfield tasks.** No cross-session continuity, no shared workspace — durability and isolation are overhead; atomicity and consistency carry the workflow.
- **Throwaway environments.** Per-task containers reset on each invocation. Durability via git is duplicative — the environment is already ephemeral.
- **High-frequency inner loops.** One commit per logical operation inflates history at sub-minute cadences. Squash-on-merge or commit-per-task scales better than strict per-operation atomicity.
- **Multi-agent with shared file ownership.** Branch isolation handles write-disjoint tasks but does not coordinate writes to the same file. Git has no transaction manager — the conflict surfaces at rebase, not at write.

Consistency and durability carry the most weight in typical single-agent workflows. Atomicity and isolation gain importance at scale and across sessions.

## Example

A long-running agent implements three features against a Python service. The system prompt installs the four properties as the operating contract:

```text
Your repository is your system of record. Follow ACID:

- Atomicity: one logical change per commit. On failure, `git stash` and revert
  the working tree before retrying.
- Consistency: before every commit run `uv run pytest && uv run ruff check`.
  Do not commit if either fails.
- Isolation: work on branch `agent/<feature-id>`. Maintain progress in
  `agent-progress/<feature-id>.md`. Do not read or write other agents' files.
- Durability: at session end, commit progress notes and push the branch.
  Cross-session knowledge lives in git-tracked files, not in your context window.
```

Session 1 starts feature `auth-reset`. The agent creates branch `agent/auth-reset`, writes the endpoint and tests, runs the predicate, commits, writes `agent-progress/auth-reset.md` noting the next step is integration tests, commits, pushes. Context compacts.

Session 2 starts on the same task. The agent reads `agent-progress/auth-reset.md` and `git log agent/auth-reset` to recover state — no chat history required. It resumes at integration tests, runs the predicate, commits, marks the feature passing in `features.json`. A concurrent agent on `agent/payment-retry` sees no in-flight state from `auth-reset` because both writes are partitioned by branch and progress file.

## Key Takeaways

- ACID is a documented operating model for agent repository state, not a metaphor — each letter has a citable agent discipline
- Atomicity binds the commit to a logical operation, not a file boundary; partial failures stash or reset
- Consistency runs the verification predicate via tool calls before commit, closing the agent-optimism gap
- Isolation partitions concurrent agents by branch and progress file — convention, not transaction-manager enforcement
- Durability puts cross-session knowledge in git-tracked files so context compaction does not destroy state
- Consistency and durability carry most workflows; atomicity and isolation matter most at scale and across sessions

## Related

- [Feature List Files](../instructions/feature-list-files.md)
- [Rollback-First Design](rollback-first-design.md)
- [Idempotent Agent Operations](idempotent-agent-operations.md)
- [Frozen Spec File](../instructions/frozen-spec-file.md)
- [AGENTS.md as Table of Contents](../instructions/agents-md-as-table-of-contents.md)
- [Discoverable vs Non-Discoverable Context](../context-engineering/discoverable-vs-nondiscoverable-context.md)
- [Worktree Isolation](../workflows/worktree-isolation.md)
- [Agent Harness](agent-harness.md)
