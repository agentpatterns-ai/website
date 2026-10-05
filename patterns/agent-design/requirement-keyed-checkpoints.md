---
title: "Requirement-Keyed Checkpoints for Shifting Requirements"
term: "Requirement-Keyed Checkpoints"
description: "Tag each checkpoint with the requirement it satisfied, then resume from the last compatible one when a change withdraws an earlier requirement."
tags:
  - agent-design
  - tool-agnostic
  - pattern
  - arxiv
aliases:
  - requirement-keyed version graph
  - requirement-compatible checkpoint resume
last_reviewed: 2026-10-04
maturity: emerging
---

# Requirement-Keyed Checkpoints for Shifting Requirements

> Requirement-keyed checkpoints record which requirement each snapshot satisfied, so a withdrawn requirement sends the agent back to a compatible snapshot.

A requirement-keyed checkpoint is a restorable snapshot of an agent's work that carries the requirement state it satisfied. When a user withdraws or corrects an earlier requirement, you restore the newest checkpoint whose requirement still holds, instead of continuing from the latest state. The pattern applies only to that case. For an additive change, continue from the head. For a session whose context has drifted, consolidate the current requirements and restart.

## Choose the resume point by the kind of change

| Change | Resume from | Why |
|---|---|---|
| Adds to the work (a new constraint, a missing feature) | The head | Everything already done stays valid. |
| Withdraws or corrects an earlier requirement | The last checkpoint whose requirement still holds | Work built on the withdrawn requirement stays out of context. |
| Leaves the session cluttered by repeated corrections | A fresh session with one consolidated prompt | Claude Code advises `/clear` and a more specific prompt after more than two corrections on one issue ([Claude Code: Best practices](https://code.claude.com/docs/en/best-practices)). |

Most late-arriving requirements do not contradict the prior ledger. In a convenience sample of SWE-chat sessions, 89.3% are neutral to the prior requirement ledger and 14.5% are destructive ([Jiang et al., arxiv 2609.03028v1](https://arxiv.org/abs/2609.03028v1), as reported in [Late Requirement Arrival](../../workflows/late-requirement-arrival.md)). Changes that contradict earlier work are the minority, and they are the only case where this pattern pays.

## Manual form

You can run the pattern today with tools you already have.

1. Commit or checkpoint after each requirement the agent satisfies, and name that requirement in the commit message.
2. When a change arrives, decide whether it adds, withdraws, or corrects.
3. For a withdrawal, restore the last commit whose requirement still holds. In Claude Code, `/rewind` restores code, conversation, or both from a per-prompt checkpoint. To keep the original session intact, use `/branch` or `claude --continue --fork-session` ([Claude Code: Checkpointing](https://code.claude.com/docs/en/checkpointing)). In plain git, check out the commit.
4. State the new requirement in the restored session and continue.

[Selective Checkpoint Restore](selective-checkpoint-restore.md) covers the three restore actions. This page covers which checkpoint to restore to.

Claude Code checkpoints have limits: "Checkpointing does not track files modified by Bash commands." The docs also say checkpoints are for quick session-level recovery and point to version control for permanent history ([Claude Code: Checkpointing](https://code.claude.com/docs/en/checkpointing)). Commit to git when you want requirement tags that outlive the session.

## Automated form: GitHarness

GitHarness automates the manual form. It saves "a version after each successful turn—a snapshot pairing the requirement with a recoverable checkpoint of the work state." Only normally terminated results become versions, so a failed run leaves the graph unchanged ([GitHarness, arxiv 2609.36789v1](https://arxiv.org/abs/2609.36789v1)).

A Git Agent has three actions: Inspect, Commit, and Reuse. Choosing a base other than the head creates a branch. In the paper's words, "branching is thus a natural by-product of base selection, not a separate action." The anchor "need not be the most recent state" ([arxiv 2609.36789v1](https://arxiv.org/abs/2609.36789v1)).

After the base is chosen, one of three execution modes runs: ExactReuse (no execution), FreshSolve (an empty workspace), or ReuseAndPatch (fork the base checkpoint and edit it). A router reads a workspace manifest to choose between the last two. Historical checkpoints are immutable, so a failed execution cannot corrupt an earlier state ([arxiv 2609.36789v1](https://arxiv.org/abs/2609.36789v1)).

## Why it works

A flat history mixes superseded requirements with valid work. The authors argue that flattening a growing interaction history into one context "obscures which prior states are reusable and makes selective rollback impossible" ([arxiv 2609.36789v1](https://arxiv.org/abs/2609.36789v1)). Binding each checkpoint to its requirement turns the question of which work is still valid into the question of which requirement state is compatible with the new one. The system then gets locality from base selection rather than from predicting affected files. Resuming from a compatible prior state "naturally confines edits to what the new requirement demands" (same source).

The ablation backs the mechanism. On Code (a 100-task SWE-bench Verified subset) with StackPlanner and DeepSeek-V4-Flash, fixing the head as the base cuts the resolved rate from 74.0 to 44.0 and raises token use from 1.29M to 4.51M ([arxiv 2609.36789v1](https://arxiv.org/abs/2609.36789v1)). The paper does not separate the gain from excluding stale context from the gain from reusing artifacts.

## When this backfires

- Additive change streams. The right base is the head, so the version store adds cost and picks nothing better. Most late-arriving requirements do not contradict the prior ledger (see the SWE-chat figures above).
- Synthetic evidence. The benchmark builds multi-turn trajectories backward from single-turn tasks, and intermediate states "may depart from the source task through a transient edit" and later recover through a compensating edit. The authors say the interactions were generated "rather than collected from real users" ([arxiv 2609.36789v1](https://arxiv.org/abs/2609.36789v1)). Reverting edits raise how often an earlier base is correct, so the benchmark likely overstates the share of real changes that benefit.
- Savings that are not patch efficiency. The paper reports 73.6% fewer tokens than Native on Code, and also that "ExactReuse dominates Code" ([arxiv 2609.36789v1](https://arxiv.org/abs/2609.36789v1)). The paper links the lower cost to reusing compatible work and says ExactReuse dominates Code, so some of the saving is a return to an existing state, not cheaper patching.
- Versioning alone. The paper credits requirement-aware base selection. Do not read the result as a case for storing history in general; [Version-Controlled Agent Context](../../context-engineering/version-controlled-agent-context.md) covers the memory-only approach.
- Ambiguous or conflicting feedback. The authors state that GitHarness "depends on accurate requirement interpretation and historical-state selection, which can be challenging under ambiguous or conflicting feedback." A wrong base drops valid work or restores a withdrawn requirement, and restoring a state "does not guarantee that the underlying agent preserves all unaffected work" ([arxiv 2609.36789v1](https://arxiv.org/abs/2609.36789v1)).
- Side effects outside the checkpoint. Files changed by Bash commands, databases, and deployed services are not in a file checkpoint, so a restore gives a mixed state.
- No code release and a weaker trained variant. The reproduction repository is an anonymized placeholder, and the RL-trained variant scores below the training-free one. The authors say that gap "may partly reflect the smaller 8B policy capacity" ([arxiv 2609.36789v1](https://arxiv.org/abs/2609.36789v1)).
- Branches that need merging. GitHarness branches and never merges, so rejoining parallel branches is your problem.
- Restart is cheaper. Consolidating requirements into one instruction "is an effective strategy to improve the model's aptitude and reliability" ([Laban et al., arxiv 2505.06120v1](https://arxiv.org/abs/2505.06120v1)). Try it before building a version graph.

## Key Takeaways

- Resume from a requirement-compatible checkpoint only when a change withdraws or corrects an earlier requirement.
- For additive changes continue from the head; for a drifted session consolidate and restart.
- Commit per satisfied requirement and name that requirement in the message, then use `/rewind`, `/branch`, or `git checkout` on a shift.
- GitHarness automates base selection, but its evidence is synthetic and its code is unreleased.

## Related

- [Selective Checkpoint Restore](selective-checkpoint-restore.md)
- [Late Requirement Arrival in Agent Sessions](../../workflows/late-requirement-arrival.md)
- [Version-Controlled Agent Context](../../context-engineering/version-controlled-agent-context.md)
- [Rollback-First Design](rollback-first-design.md)
