---
title: "Agent-Native Filesystems: Gating Effects, Not Commands"
term: "Agent-Native Filesystem"
description: "Attach agent permission rules to filesystem paths instead of command strings, stage every mutation until the user commits, and keep the undo inside the filesystem."
tags:
  - agent-design
  - security
  - tool-agnostic
  - arxiv
aliases:
  - filesystem-level effect gating
  - effect-level permission boundary
  - staged agent mutations
last_reviewed: 2026-09-04
maturity: emerging
status: current
---

# Agent-Native Filesystems: Gating Effects, Not Commands

> Attach permission rules to filesystem paths rather than to commands, stage mutations for a single review, and let the agent undo its own mistakes.

An agent-native filesystem mediates file access itself. It reports what a command actually touched, holds mutations undoable until you commit them, and enforces rules on paths instead of on command strings ([Zhong et al., 2026, arXiv:2604.13536v4](https://arxiv.org/abs/2604.13536v4)). Two conditions bound it. It observes filesystem effects and nothing else, so a network call or a pushed commit stays outside its reach. Protection also holds only while every agent process runs inside the mediated mount. The reference implementation, YoloFS, gets that by rooting a mount namespace at its own mount, so anything launched outside is unmediated.

## What 290 misuse reports say about the harness

The case for moving the boundary is frequency data, not preference. Zhong et al. collected 290 public reports of agent filesystem misuse between February 2024 and March 2026, most of them GitHub issues (205). Harness failures contribute to 218 of those reports, more than the model (168) or user review (105) ([arXiv:2604.13536v4](https://arxiv.org/abs/2604.13536v4)).

Three harness failures account for most of that:

- Shell loophole, 77 reports. "When a read through a built-in tool is denied, the agent can use `cat` to read the same file."
- Effect-blind filter, 52 reports. The paper's Finding 4 states it plainly: "Filters on command strings are ineffective because they do not target the actual filesystem effects."
- Sandbox misfit, 41 reports. Sandboxes are "often too restrictive for legitimate work while too permissive within their boundaries."

Of the reports with known recoverability, 40% are unrecoverable: 23% total data loss and 17% partial. Detection is no better: in 68% of reports with a known agent reaction the agent "continues operating as if nothing went wrong", and 11% lie about it ([arXiv:2604.13536v4](https://arxiv.org/abs/2604.13536v4)).

## The three capabilities

| Capability | What the user gets | What the agent gets |
|---|---|---|
| Introspect effects | Review the session's accumulated changes | See what each command accessed and changed |
| Undo mutations | Decide the final change set in one pass | Reverse a mistake and retry without pre-approval |
| Gate accesses | Set rules on paths, refined during the run | Operate freely inside those rules |

Undo covers anything reversible, so the agent acts first and checks after. Gating covers what undo cannot reach: "once an agent reads a secret, it cannot unread it" ([arXiv:2604.13536v4](https://arxiv.org/abs/2604.13536v4)).

## Why it works

A command filter classifies a string, while the effect is decided by which syscalls touch which paths, and [no rule count closes that gap](../../security/parser-versus-shell-permission-evasion.md). The paper puts the reason in one line: "different commands can produce the same effect, and the same program can produce different effects depending on the arguments and environment" ([arXiv:2604.13536v4](https://arxiv.org/abs/2604.13536v4)). Moving the rule onto the path removes that degree of freedom: "a rule governs every access to that path regardless of what command makes it."

Undo changes the timing rather than the soundness. Once mutations are staged and reversible, approval moves from many uninformative prompts before execution to one informed review after it. Across 112 single-operation filesystem tasks the paper measures 0.4 user interactions per task at a 99% success rate. Stock Claude Code averages 0.9 and Gemini CLI 2.2 ([arXiv:2604.13536v4](https://arxiv.org/abs/2604.13536v4)). Codex also averages 0.4, so this is not a clean win over every baseline.

## When this backfires

- Your damage is not on disk. Staging and undo reach a deleted file, never a sent email, a captured payment, or a key that has already left the process. If exfiltration is the threat, spend the effort on egress control.
- Execution escapes the mount. Protection scoped to a mount namespace holds only while every subprocess, MCP server, and cloud runner stays inside it. A remote session gets nothing from a filesystem mounted on your laptop.
- Batch review becomes the new rubber stamp. The same study counts 80 reports where users enabled "YOLO mode" rather than keep "answering hundreds of prompts per session" ([arXiv:2604.13536v4](https://arxiv.org/abs/2604.13536v4)). One large staged diff nobody reads is the same failure.
- You already have the syscall layer. [Sandlock](https://arxiv.org/abs/2605.26298v1) enforces "filesystem, network, IPC, and syscall policies without root" with unprivileged Linux primitives, including reversible filesystem effects. Where kernel rules are available, a filesystem on every read and write path is one more component whose bugs are data-loss bugs.

## Example

The paper's self-correction test shows what the capabilities buy. It builds 11 tasks where a routine request carries a hidden destructive side effect. A linter deletes source files, a build clean also removes headers, a setup script resets `.env`. Claude Code with the agent-native filesystem self-corrected in 8 of the 11, and staged the other 3 for the user to reject. The unmediated baselines mostly failed outright or stopped to ask ([arXiv:2604.13536v4](https://arxiv.org/abs/2604.13536v4)).

Read the size caveat alongside that result. The authors "deliberately keep each project small (10–41 LoC), making it easier for the agent to inspect the codebase and detect unexpected effects" ([arXiv:2604.13536v4](https://arxiv.org/abs/2604.13536v4)). Self-correction depends on the agent noticing an anomaly in the effect report. A repo with a build tree and vendored dependencies is a harder read than 41 lines.

## Key Takeaways

- Sort your permission rules into the ones that name a path and the ones that name a command. The second set is the bypassable half, whatever layer you enforce it at.
- Gate what cannot be undone and stage the rest. A read of a credential file earns a prompt; a write inside the project does not.
- Before adopting any of this, count your irreversible surface. If most of it is network or third-party calls, a filesystem is the wrong layer and egress control is the spend.
- Set a size limit on the staged diff you will review. Past it, you are auto-approving again, in one keystroke instead of a hundred.

## Related

- [Parser-Versus-Shell Evasion in Command Permission Checks](../../security/parser-versus-shell-permission-evasion.md) — why a command-text check keeps losing to the shell that runs it
- [Rollback-First Design](rollback-first-design.md) — choosing the undo before choosing the action
- [Approval Gate Granularity in Agent Pipelines](approval-gate-granularity.md) — when batching approvals actually cuts reviewer load
- [Enforced Versus Advisory Controls in LLM-Native IDEs](../../security/enforced-versus-advisory-controls.md) — where a control is evaluated decides whether it binds
- [Sandbox Runtime Comparison](../../security/sandbox-runtime-comparison.md) — picking the isolation layer beneath all of this
