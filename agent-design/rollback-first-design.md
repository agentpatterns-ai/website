---
title: "Rollback-First Design: Every Agent Action Should Be Reversible"
description: "Treat recovery cost as a first-class design constraint. For every agent action, choose how you will undo it before you choose how to do it."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - reversible agent design
  - undo-first design
---

# Rollback-First Design: Every Agent Action Should Be Reversible

> Before choosing how an agent will perform an action, choose how you will undo it — if recovery costs more than one command, reconsider the approach.

## The Premise

Agents produce bad output. The question is not whether an agent will make a mistake, but what the recovery cost is when it does.

Rollback-first design treats recovery cost as a first-class constraint. For every agent action, ask "how hard is this to undo?" If the answer is "very," choose an approach that produces a reversible result.

## The Undo Cost Spectrum

```mermaid
graph LR
    A[Instant<br/>delete branch] --> B[Easy<br/>close PR, revert commit]
    B --> C[Hard<br/>manual rollback, data restore]
    C --> D[Impossible<br/>sent email, charged card]
```

Design agent workflows to stay in the left half. When a step must land in the right half, add a human gate before it — see [Human-in-the-Loop Placement](../workflows/human-in-the-loop.md).

## Reversible Primitives

**Git branches.** Agent work on a branch is reversible: delete the branch, nothing on main is affected. Git's [branching model](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell) makes creation and deletion nearly free, which is what makes it viable as a per-task primitive.

**Draft PRs.** A draft PR is visible and reviewable but not merged. Closing it discards the changes. Use draft PRs instead of direct pushes to main.

**Labels over status.** Changing a label is reversible. Closing an issue muddies history; deleting is irreversible on most platforms.

**Comments over edits.** Appending a comment is reversible (delete it). Editing a body overwrites the original. Prefer comments for agent-generated observations; reserve body edits for structured fields.

**Checkpoints.** [Claude Code checkpoints](https://code.claude.com/docs/en/checkpointing) capture file state before each user prompt. Restoration is selective — code only, conversation only, or both.

**Staging environments.** Agent output affecting live systems should pass through staging. A bad draft in staging costs nothing to discard; a bad production deployment costs recovery time.

**Transactional boundaries.** IBM Research's STRATUS system uses a "transactional-no-regression" rule: mitigation agents may only take reversible actions within a transaction, and commands per transaction are capped to keep rollbacks tractable ([IBM Research, 2025](https://research.ibm.com/blog/undo-agent-for-cloud)). The same applies to coding agents — bound each turn to changes that can be undone in one step.

## What Cannot Be Made Reversible

Some actions have inherent irreversibility:

- Sending external notifications (email, Slack, webhooks)
- Charging or refunding payment instruments
- Deleting external resources without snapshots
- Pushing to a CDN or cache that propagates globally

For these, apply human gates before the action, not after. There is no rollback; the gate is the only defense.

## Designing for Reversibility

Checklist for each agent action:

1. Can this be done on a branch instead of main?
2. Can the artifact be a draft before it becomes final?
3. Is there a checkpoint before this action?
4. If this action fails or is wrong, what is the one-command undo?

If the one-command undo does not exist, redesign the step before shipping the workflow.

## Example

An agent refactors a module across 40 files. Halfway through, it makes a wrong assumption about the interface and produces broken code in 15 files.

**Without rollback-first design:**

- The agent pushed directly to main
- Recovery requires reverting individual commits or manually fixing 15 files
- CI is broken; other developers are blocked

**With rollback-first design:**

- All changes happened on a branch (`agent/refactor-module-xyz`)
- A draft PR was opened for human review before any merge
- Recovery is one command: `git branch -D agent/refactor-module-xyz`
- Main is untouched; CI is unaffected; no one is blocked

The design choice was made before execution: work on a branch, open a draft PR, require human approval before merge. Each step has a one-command undo at the point it was created.

## When This Backfires

Rollback-first design is not free. Conditions where it is worse than the alternative:

- **Reversibility hides root cause.** When rollback is trivial, teams lean on "undo and retry" instead of fixing the underlying bug. A reliable undo path can delay diagnosis until the failure surfaces somewhere harder to reverse.
- **Gate latency dominates.** In high-frequency loops (inner-loop edits, self-review cycles), forcing every action through a draft/approval gate adds human-scale delay to machine-scale work. The recovery saved is smaller than the throughput lost.
- **The action is already cheap to redo.** For idempotent operations where re-running is faster than engineering a rollback primitive, the reversibility machinery is overhead. Prefer [idempotent design](idempotent-agent-operations.md) when the natural answer is "just run it again."
- **Ephemeral environments.** If the environment is throwaway (container spun up per task, test database that resets on each run), branch-level isolation is redundant — the environment itself is the rollback primitive.

The pattern scales with stakes. Apply it fully for agents touching shared codebases, production systems, or customer-facing data. Relax it when the blast radius is small and recovery is already trivial.

## Key Takeaways

- Treat undo cost as a design constraint, not an afterthought
- Git branches, draft PRs, and checkpoints are the core reversible primitives
- Comments are reversible; body edits less so — prefer comments for agent-generated content
- External side effects (emails, webhooks, payments) cannot be made reversible — gate them instead
- If recovery requires more than one command, reconsider the approach

## Related

- [Human-in-the-Loop Placement: Where to Gate Agent Pipelines](../workflows/human-in-the-loop.md)
- [Idempotent Agent Operations: Safe to Retry](idempotent-agent-operations.md)
- [Worktree Isolation](../workflows/worktree-isolation.md)
- [Agent Loop Middleware](agent-loop-middleware.md)
- [Agent Pushback Protocol](agent-pushback-protocol.md)
- [Exception Handling and Recovery Patterns](exception-handling-recovery-patterns.md)
- [Wink: Agent Misbehavior Correction](wink-agent-misbehavior-correction.md)
- [Steering Running Agents](steering-running-agents.md)
