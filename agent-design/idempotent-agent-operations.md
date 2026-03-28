---
title: "Idempotent Agent Operations: Design for Safe Retry"
description: "Design agent operations so that running the same task twice produces the same end state — not duplicate artifacts, conflicting state, or compounded errors"
aliases: [idempotency, safe-retry-design]
tags:
  - agent-design
  - tool-agnostic
---

# Idempotent Agent Operations: Safe to Retry

> Design agent operations so that running the same task twice produces the same end state — not duplicate artifacts, conflicting state, or compounded errors.

## Why Idempotency Matters for Agents

Agents fail mid-task: context windows fill, API calls time out, tool errors interrupt execution. When you re-run the agent, it starts fresh — with no memory of what it already did. If the first run created a branch, posted a comment, or applied a label before failing, the second run encounters pre-existing state it doesn't know about.

Without idempotent design:

- Second run creates a duplicate branch → both exist, conflict
- Second run posts a duplicate comment → noise in the issue thread
- Second run applies a label that's already set → harmless but wasteful
- Second run tries to create a PR that already exists → error and confusion

With idempotent design, the second run detects existing state and produces the same result as if the first run had succeeded.

## Core Techniques

**Check before act.** Before creating, check if it already exists. Before posting, check if an equivalent already exists. The overhead is one read operation; the alternative is duplicate state.

```
# Non-idempotent
git checkout -b feature/123

# Idempotent
git checkout feature/123 2>/dev/null || git checkout -b feature/123
```

**Upsert over create.** Update existing artifacts rather than failing on existence. A comment that updates rather than appends, a label transition that checks current state before applying.

**Unique identifiers.** Use issue numbers, commit SHAs, or task IDs as keys. A comment containing `[#123]` can be found and updated rather than duplicated. A branch named `feature/issue-123` has a natural uniqueness constraint.

**State labels as checkpoints.** Issue labels encode pipeline state: `idea → researching → researched → drafting`. An agent that checks the current label before transitioning avoids re-processing work that is already done.

**Git as natural idempotency.** Committing identical content twice produces the same tree SHA — git deduplicates at the object level. Pushing an already-pushed branch is a no-op if no new commits exist. File writes are idempotent by nature; comment posts are not.

## Checkpoints

[Claude Code checkpoints](https://code.claude.com/docs/en/checkpointing) automatically capture file state before each user prompt. When a task goes wrong, you can manually restore to an earlier checkpoint — reverting code, conversation, or both — rather than re-running from the beginning. This reduces the window of work that must be idempotent — only the segment since the last checkpoint needs to be safe to retry.

## What Cannot Be Made Idempotent

Some operations are inherently non-idempotent and should be gated or deduplication-tracked:

- External API calls that create resources (payment processing, email sending, webhook triggers)
- Deployments that have side effects beyond git state
- Notifications sent to external systems

For these, log the operation with a unique key before executing and check the log before re-executing. The log is the idempotency record.

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

The unique identifier (`issue.number`) is the key throughout: it names the branch and marks the comment. This makes every artifact findable rather than requiring creation.

## Key Takeaways

- Agents fail and get re-run — idempotent design makes retry produce the same result, not duplicate state
- Check-before-act is the foundational technique: one read to avoid a conflicting write
- Unique identifiers (issue numbers, SHAs) enable lookup instead of creation
- Git operations are naturally idempotent; comment and label operations are not — treat them differently
- Checkpoints reduce the retry window; only the segment since the last checkpoint needs idempotency

## Related

- [Rollback-First Design: Every Agent Action Should Be Reversible](rollback-first-design.md)
- [Circuit Breakers for Agent Loops](../observability/circuit-breakers.md)
- [Human-in-the-Loop Placement: Where to Gate Agent Pipelines](../workflows/human-in-the-loop.md)
- [Agent-First Software Design](agent-first-software-design.md)
- [Agentic AI Architecture: From Prompt-Response to Goal-Directed Systems](agentic-ai-architecture-evolution.md)
- [Model a Single Agent Turn as Many Inference and Tool-Call Iterations](agent-turn-model.md)
- [Agent Loop Middleware](agent-loop-middleware.md)
- [Event-Driven Agent Routing](event-driven-agent-routing.md)
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md)
- [The Ralph Wiggum Loop](ralph-wiggum-loop.md)
