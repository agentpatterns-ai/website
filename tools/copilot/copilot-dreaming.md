---
title: "Background Curation of Agent Context (Copilot Dreaming)"
description: "Copilot Dreaming rewrites memories without per-change approval, proposes instruction and skill edits as pull requests, and updates code review guidance invisibly. Turning it off reverts none of it."
tags:
  - context-engineering
  - memory
  - copilot
aliases:
  - Copilot background context curation
applies_to: "copilot@1.x"
last_reviewed: 2026-10-30
status: current
---

# Background Curation of Agent Context (Copilot Dreaming)

> A background layer that rewrites Copilot's memories and proposes instruction-file changes, with only one of its three write paths behind a review gate.

Copilot Dreaming analyzes your past Copilot sessions and merged pull request review feedback, then updates the context Copilot reads on the next task ([GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming)). It shipped in public preview on 28 October 2026, alongside Copilot Memory's general availability, and "Dreaming is opt-in" ([GitHub Changelog](https://github.blog/changelog/2026-10-28-github-intelligence-puts-your-code-context-and-history-to-work)). Enabling it commits you to auditing a store that a second actor now writes to, because the off switch stops future runs and reverses nothing.

## Before you enable it

| Requirement | Detail |
|---|---|
| Plan | Paid plans only. The preview "requires access to GPT-6.1 Sol and is not available on Copilot Pro" |
| Memory | Repository-level or personal Memory already on, matching the capability you want |
| Policy | Dreaming enabled through organization policy or a personally owned repository's settings, with GPT-6.1 Sol allowed by policy |
| Personal Dreaming | For personal memory curation, applicable managed policies permit it and the user enables it |
| Session syncing | Required for repository customization and personal memory curation; not for code review customization |
| Code review preview | Copilot code review and its preview features enabled, for code review customization |
| Excluded | GitHub Enterprise Cloud with data residency; self-hosted runners for code review customization |
| Spending | Set spending controls first, because "Alerts alone do not stop usage" |

Source: [GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming).

The repository toggle is coarse: repository customization and code review customization share one setting, and "You cannot switch these capabilities on or off individually" ([GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming)). A setting turns on whichever capabilities have their prerequisites met. Completing a prerequisite later does not activate more, so turn the setting off and on again.

## What each write path changes

Only one of the three targets is reviewable per change.

| Capability | Inputs | Output | Review gate |
|---|---|---|---|
| Repository customization | Repository sessions, code, memories, guidance | Repository memories, plus proposed instruction or skill changes | Pull request for files; none for memories |
| Personal memory curation | Your sessions and personal memories | Personal memories only | None |
| Code review customization | Merged pull request feedback, current code | Internal code review guidance | None |

Copilot Dreaming "adds, updates, and deletes memories automatically, without approval for each change". For checked-in files it "proposes changes in a pull request", and the docs add: "Files remain unchanged until you merge the pull request." For code review it "updates internal code review guidance without a pull request" ([GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming)).

The files in scope include several a team may already write-protect: `.github/copilot-instructions.md`, `.github/instructions/**`, `.github/agents/**`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `REVIEW.md`, and `.github/skills/**` ([GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming)). See [the copilot-instructions.md convention](copilot-instructions-md-convention.md) for what that first file governs.

## Why it works

Curation works because the drift it fixes is already recorded in artifacts GitHub stores, so nobody has to notice the drift and file a ticket. GitHub's worked case is an instruction file naming a command the repository stopped using: Dreaming "can propose an update when your repository's instructions describe an obsolete test command" ([GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming)). A synced session records the command the agent ran. Merged review feedback records human corrections. Both can expose outdated guidance.

GitHub does not say why the paths differ. The split matches where a review gate already exists: a checked-in file has pull requests, so changes to it use one. The docs warn: "AI-generated guidance can be incorrect. Review proposed file changes before merging." ([GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming)) The one write path you can review is the path you were reviewing anyway.

## What turning it off does not undo

Disabling Copilot Dreaming stops future runs and nothing else. It "does not undo its changes, delete information it has created, close its pull requests, or restore deleted memories", and "A run already in progress may continue". Run output in the Copilot app is "not a complete activity history" and offers no undo, so it will not tell you what to revert ([GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming)).

Cleanup is manual and per-store: personal memories in personal settings, repository memories in repository settings, and the open pull requests by hand.

## When this backfires

- Large estates with dormant repositories. Billing is per run, not per change: "Every Copilot Dreaming run uses AI credits. This includes runs that make no changes or process inactive repositories." Per-user budgets may not cover repository-level app usage. Per-installation budgets do not exist, so the spend resists capping where it arises ([GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming)).
- Teams mid-convention-change. The inputs are past sessions and merged review feedback, both of which describe the convention you are retiring. Switching Dreaming off afterwards leaves the retired version in the store.
- Repositories that gate their own agent config. Dreaming can propose changes to `AGENTS.md` and `.github/skills/**` through pull requests. Review those proposals against your rules for agent configuration.
- Stores audited one entry at a time. Research on agent memory attacks found a bad record's effect "is only activated within a specific context, making them hard to detect when individual memory entries are audited in isolation" ([arXiv:2510.02373v1](https://arxiv.org/abs/2510.02373v1)). That work studies adversarial injection, not benign curation, so take it as a caution about the auditing method.
- Self-updates that outlive the session. A systematic security and privacy analysis of self-evolving LLM agent systems reports that autonomous updates to memory, tools, and architecture let an influence "become permanently encoded, self-amplify across generations, and propagate through populations" ([arXiv:2606.23075v1](https://arxiv.org/abs/2606.23075v1)). It evaluates open-source frameworks rather than Copilot, but the persistence property is the one GitHub's own irreversibility statement records.

Copilot Memory runs with Dreaming off: it "stores repository facts and personal preferences that Copilot can learn and reuse during normal interactions, even when Copilot Dreaming is off" ([GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming)). Leaving Dreaming disabled costs you the curation, not the memory. See [Copilot Memory and Cross-Agent Persistence](copilot-memory.md) for how entries are created, verified, and expired without it.

## Example

GitHub's documented case is an instruction file that has fallen behind the code: Dreaming "can propose an update when your repository's instructions describe an obsolete test command" ([GitHub Docs](https://docs.github.com/copilot/concepts/prompting-and-context/copilot-dreaming)). Follow that case through both write paths.

Repository customization reads the synced sessions, which record the command the agent ran, against the current `.github/copilot-instructions.md`. Dreaming proposes the correction through a pull request. The obsolete command remains until someone merges it.

The same run can also add, update, or delete a repository memory covering the same ground. That memory change needs no approval and appears in no pull request. Disabling Dreaming afterwards will not restore a memory it deleted.

## Key Takeaways

- Of three write paths, one carries a per-change review gate. Budget audit time for memory changes as well as proposed file changes.
- Configure spending controls before enabling, not after. Runs bill on inactive repositories and on runs that change nothing.
- Disabling Dreaming stops future runs and preserves previous changes. Plan cleanup as three separate manual tasks: personal memories, repository memories, open pull requests.
- The repository toggle turns on every capability whose prerequisites are met, and you cannot switch them individually. Wanting one can mean accepting both.
- Dreaming is opt-in and Memory is not gated behind it, so the two decisions are separable.

## Related

- [Copilot Memory and Cross-Agent Persistence](copilot-memory.md)
- [copilot-instructions.md Convention](copilot-instructions-md-convention.md)
- [An Explicit Update Boundary for Agent Self-State](../../security/self-state-update-boundary.md)
- [Memory Synthesis: Extracting Lessons from Execution Logs](../../patterns/agent-design/memory-synthesis-execution-logs.md)
- [Continual Learning for AI Agents](../../patterns/agent-design/continual-learning-layers.md)
