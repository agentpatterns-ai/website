---
title: "Out-of-Workspace Writes as the Agent Backup Trigger"
term: "Out-of-Workspace Backup Trigger"
description: "Fire a pre-action backup on whether a tool call writes outside the workspace. A destructive-command guard covered 8.1% of the moments users regretted."
tags:
  - agent-design
  - hooks
  - tool-agnostic
  - arxiv
aliases:
  - out-of-workspace backup trigger
  - pre-action backup predicate
  - backup awareness
last_reviewed: 2026-10-25
maturity: emerging
status: current
---

# Out-of-Workspace Writes as the Agent Backup Trigger

> Back up on whether a tool call writes outside the workspace; a destructive-command guard, wired to real backup machinery, covered 8.1% of regret moments.

An out-of-workspace backup trigger runs a preservation step before any tool call that changes state outside the agent's working directory, whatever the command happens to be. It runs in a pre-tool-call hook. The paper compares automatic backup against destructive-command filtering and instructions asking the agent to preserve state. The location predicate is this page's adaptation: the paper's BackUpper checks every tool call, and the paper never tests a location-only trigger.

## Where the gap is

Build this only against state your harness does not already cover. Li et al. checked the native backup mechanisms of Hermes, OpenClaw, OpenHands, Claude Code and Codex, and each snapshots the workspace, saves files before native edits, or runs scheduled local backups. "None of these covers external state, such as local files outside the workspace or remote services" ([Li et al., 2026, arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)).

The headline measurement is scoped to that same boundary. Across six frontier models on 205 executable tasks built from reported regret moments, "agents complete 86.1% of tasks on average yet back up before these moments in only 15.2%". The authors removed the harness as a variable first: "We standardize harness-level protection to workspace snapshots, so any backup beyond the workspace reflects the agent itself" ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)). An agent confined to a workspace that its harness already snapshots has no external-state gap to close.

Two other results corroborate the location predicate. Snapshot-and-branch recovery pays for itself [only on progress outside the repository](snapshot-branching-boundary.md), and a mediated filesystem that [gates effects rather than command strings](agent-native-filesystem-mediation.md) stops at the disk, so a sent message stays outside its reach.

## What a destructiveness trigger misses

The authors tested the destructiveness predicate directly: they took Destructive Command Guard, extended it to all evaluated tools, and routed its flagged actions through their own backup tiers. "It reaches only 8.1% RMBR and 7.3% OWBR, suggesting that regret extends beyond destructive actions" ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)). Checking every call instead covered all of them.

Instructing the model to back up does much better. The Skill-Based baseline hands the main agent detailed backup instructions: "It reaches 81.4% RMBR and 80.5% OWBR, while 75% of its failures are backups that are performed but insufficient for recovery" ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)). In the paper's example, an agent exports a mailbox before deleting 116 messages, but the export records attachments only by name and size, so the attachment contents are lost ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)).

A stronger model does not close this either. Across three GPT generations in Codex on a 60-task subset, their Artificial Analysis Intelligence Index "scores rise from 39 to 47, yet RMBR stays at 5.0-6.7%" ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)). Task competence is separate evidence from backup awareness, in the same way that [a completed task is not a safe one](../anti-patterns/judging-agent-safety-by-task-completion.md).

## Why it works

The destructive-command baseline suggests that regret extends beyond destructive actions ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)). It does not establish statistical independence between destructiveness and regret. The paper illustrates its backup tiers with operations such as pairing `pip install` with `pip freeze` and exporting a remote mail folder before a deletion ([Li et al., 2026](https://arxiv.org/abs/2610.28934v1)). Location identifies a documented gap in the surveyed harnesses: external state falls outside their native backup coverage ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)). This is [rollback-first design](rollback-first-design.md) moved from design time to the tool call.

## Tiering it without a model on every call

The paper's reference implementation is "a training-free harness plug-in that extends native backup coverage" from Table 1, acting "through a pre-tool-call hook". It "lets calls on a read-only allowlist proceed without backup, and otherwise checks four backup tiers in order, applying the first that matches" ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)). The command examples and snapshot trigger below come from the paper:

| Tier | Action | Example |
|---|---|---|
| Rewrite | Replace the command with a reversible equivalent | `rm x` becomes `mv x .trash/` |
| Pair | Run a capture command before the original | `pip install` paired with `pip freeze` |
| Snapshot | Reuse the harness snapshot mechanism or a shadow Git repository | No earlier rule matches, and the action modifies workspace state or uses a native tool |
| Check, then delegate | Classify the call as read-only; if not, back up the affected state | `bash run.sh`, whose effect depends on the script |

The cheap top of the ladder covers a minority. On Terminal tasks, with workspace snapshots excluded because the standardized harness already supplied them, rule-based tiers handled 30.8% of triggers with no model call, and "The remaining 69.2% invoke the backup subagent". Build the read-only classifier first: "The checker thus adds only 5.2-6.5% of cost while triggering 20.9-37.9% of regret moment backups" ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)).

## When this backfires

- Your harness already snapshots every affected workspace file before a write. Four surveyed harnesses protect the workspace, but OpenClaw does so on a schedule. Verify that protection before skipping pre-action backup.
- You need reversal rather than recovery information. Restored state reached 92.2% average character-level similarity against 33.8% for post-hoc reconstruction, and the residue has a named cause: "some state, such as third-party replies or server-generated fields, may not be restorable even from a complete backup" ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)).
- The loop is interactive and latency-sensitive. Backup latency measured 23.3 seconds per regret-moment action against 34.1 for the instruction-based baseline. That beats the alternative and is still 23 seconds in front of a write.
- Your backup subagent model is weak. The authors list it as a limitation: "BackUpper's subagent tier depends on the capability of the subagent model, which may limit its effectiveness with less capable models" ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)).
- BackUpper's default checks every state-modifying call "because regret is hard to predict", and a location-only trigger inherits that coarseness. The authors propose learning "to predict which actions are likely to be regretted" so the layer can "skip low-risk actions and further improve efficiency" ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)). Until that exists, every out-of-workspace write pays.

Two caveats bound the result itself. The regret moments are human-reported; the original action may have been a person's. Both judges are LLMs. The backup judge agrees with human annotation in 95.3% of cases ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)).

## Example

RegretBench Appendix C.5 (Figure 14) gives a remote-mailbox recovery case. Without BackUpper, the main agent saves the raw text of 115 emails in two folders, then deletes them. That backup restores the messages but loses read and flagged states because it did not request IMAP `FLAGS`. This is external state, so a workspace snapshot cannot preserve it. The backup must include the mailbox state the user needs, not just message bodies ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)).

## Key Takeaways

- Scope the claim before you cost it: 15.2% is the share of tasks whose designated regret-moment action was backed up (RMBR). Coverage of all out-of-workspace modifications was 17.4% (OWBR), after workspace snapshots were standardized.
- Check restoration, not just whether a backup command ran. The study separately measures backup coverage and restored-state similarity.
- Scope the trigger against your harness's existing protection. A scheduled workspace backup and a pre-action backup protect different moments.
- Keep a backup log that links each action to its preserved state, as BackUpper does ([arXiv:2610.28934v1](https://arxiv.org/abs/2610.28934v1)).

## Related

- [Rollback-First Design: Every Agent Action Should Be Reversible](rollback-first-design.md)
- [Agent-Native Filesystems: Gating Effects, Not Commands](agent-native-filesystem-mediation.md)
- [Full Sandbox Snapshots Beat Retry Only for Untracked State](snapshot-branching-boundary.md)
- [Selective Checkpoint Restore Across Code and Conversation State](selective-checkpoint-restore.md)
- [Judging Agent Safety by Task Completion (Action-Boundary Violations)](../anti-patterns/judging-agent-safety-by-task-completion.md)
