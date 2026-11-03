---
title: "Write Boundaries Ship as a Setting, Read Boundaries as a Prompt"
term: "Declared Write Boundary"
description: "Claude Code 2.1.314 fences Write, Edit and NotebookEdit outside the working directories through a documented settings key with no prompt, while the read fence on the same boundary is negotiated four ways."
tags:
  - agent-design
  - claude
  - security
  - arxiv
aliases:
  - blockWritesOutsideWorkingDirectories
  - declared write boundary
  - write fence with no prompt
applies_to: "claude-code@2.1.314"
last_reviewed: 2026-11-03
maturity: emerging
status: current
---

# Write Boundaries Ship as a Setting, Read Boundaries as a Prompt

> Claude Code 2.1.314 fences three file tools, not the filesystem, with a settings key and no prompt; the read fence is negotiated four ways.

Three tools, every permission mode, no prompt. Claude Code 2.1.314, released October 30, 2026, "Added `permissions.blockWritesOutsideWorkingDirectories`: Write, Edit and NotebookEdit refuse paths outside the working directories in every permission mode" ([changelog](https://code.claude.com/docs/en/changelog#2-1-314)). The phrase "in every permission mode" is the half that matters: `acceptEdits`, auto mode, and `bypassPermissions` do not relax the refusal. The release ships no prompt, so there is also no answer that clears a single write.

## The write key documents what the read key does

Both keys have a full [settings reference](https://code.claude.com/docs/en/settings-reference#permissions-blockwritesoutsideworkingdirectories) entry, and the write entry answers the same four operator questions. The table is from the reference as checked on 2026-11-03; the changelog line states none of it.

| Question | Read key | Write key |
|---|---|---|
| Default | "unset, so reads outside the working directories follow your [permission mode]" | "unset, so writes outside the working directories follow your [permission mode]"; the block is also on while Claude Code can't read the `permissions` object in managed settings |
| Scope | "A `true` in any file applies, so a repository can turn the block on for itself but can't lift yours" | The same sentence, plus: in a cloud session Claude Code "might not apply the key, because the file tools run in a container that is itself the boundary" |
| Carve-outs | "Files Claude Code itself needs stay readable, such as your skills, plugins, rules, agents, commands" | "Some of Claude Code's own files stay writable, such as plan files, the scratchpad, a background session's `tmp` directory, and `.md` files in this project's auto memory" |
| Added directories | `--add-dir`, `/add-dir`, and `additionalDirectories` from user or managed settings count; repository settings do not | The same route lets a write through; a directory that only repository settings add stays refused |

Claude Code refuses writes to its own settings files whatever you add, "because a settings file can lift the block", and it refuses an `isolation: worktree` subagent's edits when that worktree sits outside the working directories ([settings reference](https://code.claude.com/docs/en/settings-reference#what-the-write-block-refuses-and-what-stays-writable)).

What the write side still lacks is a discovery route. Answer "No, and block reads outside the working directories from now on" on [auto mode's read prompt](one-shot-permission-answers.md) and Claude Code sets the read key "in your user settings, which makes the file tools refuse such reads in every later session and every permission mode" ([Permission modes](https://code.claude.com/docs/en/permission-modes#first-read-outside-the-working-directories)). That setting lands on machines whose operator never opened a settings file. The write block has no permission prompt that offers to enable it. User, repository, or managed settings can enable it.

## Where the fence stops

The release names Write, Edit and NotebookEdit. It does not name Bash, and Claude Code's file rules already reach only part of what a shell command does. Claude Code's redirection rules, which predate this key, already check a `> file` target: "the check covers your `Edit` allow and deny rules, [protected paths], and the [working directories]". Nothing checks a subprocess. The rules do not apply "to arbitrary subprocesses that read or write files indirectly, like a Python or Node script that opens files itself. For OS-level enforcement that blocks all processes from accessing a path, [enable the sandbox]" ([Configure permissions](https://code.claude.com/docs/en/permissions#file-permission-rules)).

A one-line Python script still writes wherever the process can reach. The documented filesystem fence is the sandbox, whose write default is "The working directory, a per-user temp directory, and [directories you've added]", with protected paths staying write-denied ([Sandboxing](https://code.claude.com/docs/en/sandboxing)). The file-tool key has its own exemptions (plan files, the scratchpad), but it exempts no general temp directory.

## Why it works

Reversibility sets the risk tier, and the tier decides whether a control is negotiated or declared in advance. Iyer and Suresh Babu rank tool risk from a rubric of "reversibility, external observability, and value transfer", reserving their top tier for tools "that are irreversible, externally observable, or value-transferring" ([Iyer and Suresh Babu, 2026](https://arxiv.org/abs/2606.13884v1)). They put that label in the tool contract rather than at the moment of the call: "The taxonomy is part of the tool contract and is the unit a reviewer audits." A write outside the tree sits in the top tier under that rubric, and a settings key is where a contract field lives.

Their evidence is synthetic and they say so: "The benchmark is synthetic and deterministically mocked; it isolates exposure behavior but does not capture real API failures, latency, or ambiguous observations." Take the rubric and none of the figures. They also say per-tool tiers miss risk that is "sequence-dependent".

## When this backfires

- Your own tooling writes outside the tree. The scratchpad is exempt, so scratch files do not trip the key. A cache, an artifact directory, or a subagent worktree outside the working directories is not exempt.
- A team reads the key as a filesystem boundary. A build script, a formatter, or any subprocess that opens a file itself sits outside the file-rule system, which is why the docs point at the sandbox for that case.
- A CI or headless run that must write past the checkout. "In every permission mode" means `bypassPermissions` will not rescue it, and no prompt means no per-call override. Add the directory in user or managed settings, or the run fails.
- A repository tries to arm the block for its own contributors. A `true` in any file applies, so this works for the repository. The reverse fails: a repository cannot add a directory that lifts the block for itself. In a cloud session the key may not apply at all.

## Example

A reviewer hardening an unattended runner wants writes confined to the checkout. Two settings do different halves of that job:

```json
{
  "permissions": {
    "blockWritesOutsideWorkingDirectories": true
  },
  "sandbox": {
    "enabled": true
  }
}
```

The first refuses Write, Edit and NotebookEdit past the boundary in every mode. The second is what stops a subprocess, and it is not on already: "The sandbox is off by default" ([Sandboxing](https://code.claude.com/docs/en/sandboxing)). Drop either and a channel stays open, and the channel the first one misses is the one a build script uses. Where legitimate writes genuinely cross the boundary, add that one directory instead of removing the key. The reference says to run `/add-dir <directory>`, pass `--add-dir`, or list it under `additionalDirectories` in user or managed settings, and that "No allow rule lets Claude's file tools through either block" ([settings reference](https://code.claude.com/docs/en/settings-reference#let-one-directory-through-the-read-or-write-block)).

## Key Takeaways

- Setting the key buys three tools in every permission mode. It buys nothing against a subprocess that opens a file itself, so pair it with the sandbox.
- The write block has no permission prompt that offers to enable it. User, repository, or managed settings can enable it.
- Scratchpad writes pass without any directory added. For other legitimate external writes, add the directory in user or managed settings; repository settings cannot lift the block.
- Quote the read key's documented behavior as the read key's and the write key's as the write key's. The two entries now match on default, scope, and added directories, but their carve-outs differ.

## Related

- [One-Shot Permission Answers for Out-of-Directory Reads](one-shot-permission-answers.md) — the read half of this boundary, where four prompt answers vary on whether the read runs and whether the answer persists
- [Out-of-Workspace Writes as the Agent Backup Trigger](out-of-workspace-backup-trigger.md) — the same predicate used to fire a backup rather than to refuse the call
- [Judging a Write by Its Spelled Path (Spelled-Path Scope)](../anti-patterns/spelled-path-permission-scope.md) — why a path-string check and the filesystem can disagree about where a write lands
- [Dual-Boundary Sandboxing: Filesystem and Network Isolation](../../security/dual-boundary-sandboxing.md) — the OS-level enforcement this key defers to for subprocess writes
- [Deny-Fallback Permissions for Unattended Agent Runs](deny-fallback-unattended-permissions.md) — what decides a call on a host where no prompt can be answered
