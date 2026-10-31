---
title: "Idempotent Agent Operations: Safe to Retry"
term: "Idempotent Agent Operations"
description: "Design agent operations so that running the same task twice produces the same end state — not duplicate artifacts, conflicting state, or compounded errors."
aliases: [idempotency, safe-retry-design]
tags:
  - agent-design
  - tool-agnostic
  - reliability
last_reviewed: 2026-06-12
maturity: established
---

# Idempotent Agent Operations: Safe to Retry

> Design agent operations so that running the same task twice produces the same end state — not duplicate artifacts, conflicting state, or compounded errors.

Related lesson: [Reversibility & Idempotency](https://learn.agentpatterns.ai/harness-engineering/reversibility-and-idempotency/) covers this concept in a hands-on lesson with quizzes.

## Why idempotency matters for agents

Agents fail mid-task. Context windows fill, API calls time out, and tool errors interrupt execution (the territory of [exception handling and recovery patterns](exception-handling-recovery-patterns.md)). When you re-run the agent, it starts fresh, with no memory of what it already did. If the first run created a branch, posted a comment, or applied a label before failing, the second run meets pre-existing state it does not know about.

Without idempotent design:

- Second run attempts to create a branch that already exists
- Second run posts a duplicate comment in the issue thread
- Second run applies a label that is already set
- Second run tries to create a PR that already exists

With idempotent design, the second run detects existing state and produces the same result as if the first run had succeeded.

## Core techniques

Check before act. Before creating, check whether it already exists. Before posting, check whether an equivalent already exists. The overhead is one read operation (the `git checkout` probe below). The alternative is duplicate state.

```
# Non-idempotent
git checkout -b feature/123

# Idempotent
git checkout feature/123 2>/dev/null || git checkout -b feature/123
```

Upsert over create. Update existing artifacts rather than failing on existence. A comment that updates rather than appends. A label transition that checks the current state before applying.

Unique identifiers. Use issue numbers, commit SHAs, or task IDs as keys. You can find and update a comment containing `[#123]` rather than duplicate it. A branch named `feature/issue-123` has a natural uniqueness constraint.

State labels as checkpoints. Issue labels encode pipeline state: `idea`, `researching`, `researched`, and `drafting`. An agent that checks the current label before transitioning avoids re-processing work that is already done.

## Checkpoints

[Claude Code checkpoints](https://code.claude.com/docs/en/checkpointing) capture file state automatically before each user prompt. When a task goes wrong, run `/rewind` (or press `Esc` twice at an empty prompt) to restore an earlier checkpoint, reverting code, conversation, or both, rather than re-running from the beginning. This shrinks the window of work that must be idempotent. Only the segment since the last checkpoint needs to be safe to retry.

The catch: checkpoints only capture edits made through Claude's file-editing tools. [Changes made by bash commands are not tracked](https://code.claude.com/docs/en/checkpointing). You cannot rewind an `rm`, `mv`, or migration script run as a shell call. Most agent side effects (branch creation, API calls, deployments) happen through tool and shell calls rather than file edits. So checkpoints shrink the retry window but do not replace per-artifact idempotency.

## Recheck authority before retrying

An idempotency key does not establish permission to send another write. Authorization can expire or change while an agent waits for an uncertain result. [Permission to Retry](https://arxiv.org/abs/2610.31916v1) separates four obligations in durable recovery:

- Checkpoint state records where execution can resume.
- A current dispatch grant authorizes the proposed write under the present policy and payload.
- Independent effect observations establish what the provider actually did.
- Reconciliation permission allows recovery to settle an earlier effect without granting another write.

The study's ledger-reconciliation policy preserves unknown outcomes and reservations when the provider cannot certify absence. A local revocation also cannot cancel an already admitted delivery that later commits. Revalidate dispatch authority and reconcile the earlier effect separately. [Recovery model and policies](https://arxiv.org/abs/2610.31916v1).

The evidence comprises 336 synthetic histories across LangGraph and Temporal, with 14 schedules, 3 provider contracts, and 4 application policies. Ledger reconciliation passes 42 histories per host: 21 checked completions, 15 denials, and 6 unknown outcomes with reservations retained. Passing therefore includes safe refusal and unresolved work. These are authored policy comparisons, not framework defaults; no actual provider, billing account, or model server participates. [Evaluation and limitations](https://arxiv.org/abs/2610.31916v1).

Use [exactly-once enforcement](exactly-once-enforcement-layer.md) to assess whether read-back can settle an uncertain effect. Check [authorization continuity](../../security/authorization-continuity-across-agent-mutation.md) separately when the agent or policy changes. In [recovery evaluations](../../verification/recovery-as-separate-eval-axis.md), report completion, denial, and unresolved outcomes separately so a safety pass does not imply task completion.

## What cannot be made idempotent

Some operations are inherently non-idempotent. Gate them, or track them for deduplication:

- External API calls that create resources (payment processing, email sending, webhook triggers)
- Deployments that have side effects beyond git state
- Notifications sent to external systems

For these, log the operation with a unique key before executing and check the log before re-executing. The log is the idempotency record.

## When this backfires

Check-before-act idempotency has known failure modes that make it the wrong tool in some contexts:

- Concurrency introduces TOCTOU gaps. Two runs that read "no branch exists" at the same moment will both create it. The [AWS Builders' Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) recommends server-side idempotency keys with atomic claim semantics. A client-side existence check is not enough when multiple actors can target the same resource.
- Partial state defeats existence checks. If the first run crashed after creating the branch but before posting the comment, the second run still needs to finish the comment. Guard each artifact, not the workflow — the per-action granularity that [rollback-first design](rollback-first-design.md) also depends on.
- Silent skip hides drift. Short-circuiting on pre-existing state also skips when that state came from a different actor or a stale run. "Fail loudly" surfaces conflicts that silent skips bury.
- Marker stores have TTLs. A 24-hour deduplication table silently stops protecting older replays. For Kafka-style replays or offline queues, the idempotency record must outlive the worst-case retry horizon.

Prefer atomic upserts, database-backed keys, or server-enforced unique constraints when duplicates are costly.

## Example

GitHub CLI supports updating the current user's last issue comment with `--edit-last` and reading replacement text with `--body-file`. Without `--create-if-none`, this command does not create a comment when none exists. [GitHub CLI issue comment manual](https://cli.github.com/manual/gh_issue_comment).

Set `ISSUE_URL` to the issue you are authorized to update and `COMMENT_FILE` to the file containing the intended comment. First inspect the comments with the documented [`gh issue view --comments`](https://cli.github.com/manual/gh_issue_view) command:

```bash
: "${ISSUE_URL:?Set the authorized issue URL}"
: "${COMMENT_FILE:?Set the comment body file}"
gh issue view "$ISSUE_URL" --comments
```

Confirm that your last comment is the intended target before updating it:

```bash
gh issue comment "$ISSUE_URL" --edit-last --body-file "$COMMENT_FILE"
```

Repeating the update with the same file restores the same comment body, provided the target remains your last comment. The check-before-act sequence is not atomic. Another writer using your identity can change which comment is last between inspection and update. Use a stored comment identifier when that targeting assumption cannot hold. A failed or uncertain read is not evidence that no earlier write occurred; keep the outcome unresolved until reconciliation supplies evidence.

## Key Takeaways

- Agents fail and get re-run — idempotent design makes retry produce the same result, not duplicate state
- Check-before-act is the foundational technique: one read to avoid a conflicting write
- Unique identifiers (issue numbers, SHAs) enable lookup instead of creation
- Verify the target identity before a retry; editing the last comment depends on no intervening comment from the same account
- Checkpoints reduce the retry window; only the segment since the last checkpoint needs idempotency

## Related

- [Tool Operability: Interfaces That Survive a Lost Response](tool-operability-lost-responses.md) — the interface-side half; what a tool must expose so the caller can tell a committed effect from an uncommitted one
- [Rollback-First Design: Every Agent Action Should Be Reversible](rollback-first-design.md)
- [Agent Circuit Breaker](agent-circuit-breaker.md)
- [Circuit Breakers for Agent Loops](../../observability/circuit-breakers.md)
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md)
- [Human-in-the-Loop Placement: Where to Gate Agent Pipelines](../../workflows/human-in-the-loop.md)
- [Model a Single Agent Turn as Many Inference and Tool-Call Iterations](agent-turn-model.md)
- [Agent Backpressure: Automated Feedback for Self-Correction](agent-backpressure.md)
- [The Ralph Wiggum Loop](../../loop-engineering/ralph-wiggum-loop.md)
- [Organizational Context Layer for Agents](../../context-engineering/organizational-context-layer.md)
