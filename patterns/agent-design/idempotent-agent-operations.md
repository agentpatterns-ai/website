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

- Second run creates a duplicate branch → both exist, conflict
- Second run posts a duplicate comment → noise in the issue thread
- Second run applies a label that is already set → harmless but wasteful
- Second run tries to create a PR that already exists → error and confusion

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

State labels as checkpoints. Issue labels encode pipeline state: `idea → researching → researched → drafting`. An agent that checks the current label before transitioning avoids re-processing work that is already done.

Git as natural idempotency. Committing identical content twice produces the same tree SHA, because git deduplicates at the object level. Pushing an already-pushed branch with `git push` is a no-op when no new commits exist. File writes are idempotent by nature; comment posts are not.

## Checkpoints

[Claude Code checkpoints](https://code.claude.com/docs/en/checkpointing) capture file state automatically before each user prompt. When a task goes wrong, run `/rewind` (or press `Esc` twice at an empty prompt) to restore an earlier checkpoint, reverting code, conversation, or both, rather than re-running from the beginning. This shrinks the window of work that must be idempotent. Only the segment since the last checkpoint needs to be safe to retry.

The catch: checkpoints only capture edits made through Claude's file-editing tools. [Changes made by bash commands are not tracked](https://code.claude.com/docs/en/checkpointing). You cannot rewind an `rm`, `mv`, or migration script run as a shell call. Most agent side effects (branch creation, API calls, deployments) happen through tool and shell calls rather than file edits. So checkpoints shrink the retry window but do not replace per-artifact idempotency.

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

A multi-step agent workflow that creates a GitHub issue, branches off it, and posts a comment — each step made idempotent.

```python
def run_issue_workflow(repo, task_title, task_body):
    """
    Idempotent agent workflow: create issue → create branch → post comment.
    Each step checks for existing state before acting.
    """
    gh = GitHubClient(repo)

    # Step 1: check-before-act — find or create the issue
    existing = gh.find_issues(title=task_title, state="open")
    if existing:
        issue = existing[0]
    else:
        issue = gh.create_issue(title=task_title, body=task_body)

    # Step 2: upsert branch — create only if absent; use issue number as key
    branch_name = f"feature/issue-{issue.number}"
    branches = gh.list_branches()
    if branch_name not in branches:
        gh.create_branch(branch_name, from_ref="main")

    # Step 3: idempotent comment — post only if no prior comment contains the marker
    marker = f"[workflow-run issue-{issue.number}]"
    existing_comments = gh.list_comments(issue.number)
    already_posted = any(marker in c.body for c in existing_comments)
    if not already_posted:
        gh.post_comment(issue.number, f"{marker} Branch `{branch_name}` ready.")

    return issue.number, branch_name
```

Running `run_issue_workflow` twice with the same inputs produces the same end state: one issue, one branch, one comment. The second run skips every creation step because the check-before-act guards short-circuit on existing state.

The unique identifier (`issue.number`) is the key throughout: it names the branch and marks the comment. This makes every artifact findable rather than requiring a new one.

## Key Takeaways

- Agents fail and get re-run — idempotent design makes retry produce the same result, not duplicate state
- Check-before-act is the foundational technique: one read to avoid a conflicting write
- Unique identifiers (issue numbers, SHAs) enable lookup instead of creation
- Git operations are naturally idempotent; comment and label operations are not — treat them differently
- Checkpoints reduce the retry window; only the segment since the last checkpoint needs idempotency

## Related

- [Rollback-First Design: Every Agent Action Should Be Reversible](rollback-first-design.md)
- [Agent Circuit Breaker](agent-circuit-breaker.md)
- [Circuit Breakers for Agent Loops](../../observability/circuit-breakers.md)
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md)
- [Human-in-the-Loop Placement: Where to Gate Agent Pipelines](../../workflows/human-in-the-loop.md)
- [Model a Single Agent Turn as Many Inference and Tool-Call Iterations](agent-turn-model.md)
- [Agent Backpressure: Automated Feedback for Self-Correction](agent-backpressure.md)
- [The Ralph Wiggum Loop](../../loop-engineering/ralph-wiggum-loop.md)
- [Organizational Context Layer for Agents](../../context-engineering/organizational-context-layer.md)
