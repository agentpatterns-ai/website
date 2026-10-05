---
title: "Agent Approval Laundering: Effects Beyond the Named Command"
term: "Agent Approval Laundering"
description: "An approval record can name npm install correctly while its workflow runs lifecycle scripts or an MCP call exercises network authority the record never lists."
aliases:
  - record-coverage failure
  - transitive effects beyond approved invocation
tags:
  - security
  - tool-agnostic
  - arxiv
  - mcp
last_reviewed: 2026-09-26
maturity: emerging
---

# Agent Approval Laundering: Effects Beyond the Named Command

> An approval record can name a command correctly and still miss what that command's workflow does.

Agent approval laundering is a gap between the invocation an approval record names and the effects the workflow behind it reaches. A paper studying package installs and MCP tool calls names and measures the gap directly ([arXiv 2609.28586v1](https://arxiv.org/abs/2609.28586v1)). Closing it earns its cost only where nothing else already contains the effect: an unsandboxed shell command, an MCP tool call, or an auto-allow rule that skips a human check. Where an OS sandbox already covers the command, or `ignore-scripts` is already off, reading more of the record adds a prompt and changes no outcome.

## Where the record runs out

A permission rule authorizes the string it matches — `npm install`, `pnpm install`, a named MCP tool. Files the rule never reads decide what that string actually runs: `package.json` scripts, a Cargo `build.rs`, a Dockerfile, a Git hook, or the transport entry in `.mcp.json`.

The paper's own case is an approved `pnpm install` in Vite at a fixed commit. It ran `postinstall` and wrote a workspace file: "the execution transcript binds simple-git-hooks, and the workspace delta binds node_modules/.modules.yaml. The record therefore represents a process effect, while the executed workflow exercises both process and file effects" ([arXiv 2609.28586v1, §II-A](https://arxiv.org/abs/2609.28586v1)). npm's own scripts documentation confirms why: `npm install` runs "preinstall install postinstall prepublish preprepare prepare postprepare" as routine, not as an edge case ([npm docs: scripts](https://docs.npmjs.com/cli/v10/using-npm/scripts/)).

A second case in the paper swaps process effects for network effects. GitHub Copilot CLI and Qwen Code each approved a named documentation-tool call whose transport also carried network authority that neither the tool name nor the command text disclosed: "the network effect remains uncovered under both the explicit-field and command-aware views. The missing information is nevertheless available before execution: the 123-byte instance-specific .mcp.json identifies the configured transport" ([arXiv 2609.28586v1, §II-B](https://arxiv.org/abs/2609.28586v1)).

Across 111 approval and execution-trace pairs the paper assembled, reading more of the record shrank the count of effects it missed, from 40 under the fields a client shows explicitly, to 17 under ordinary command semantics, to 13 under raw metadata — and all 13 remaining gaps sit inside a synthetic test set, not a real run ([arXiv 2609.28586v1, §IV-C](https://arxiv.org/abs/2609.28586v1)). On 8 fixed-commit public repositories running 11 real executions, the same three readings left 10, 2, and 0 gaps; the two that metadata still closed were both successful MCP calls over a network ([arXiv 2609.28586v1, §V-A](https://arxiv.org/abs/2609.28586v1)). The paper reports the same pairing of a name-only record and a hidden effect under tested configurations of Claude Code, GitHub Copilot CLI, and Qwen Code ([arXiv 2609.28586v1, §V-B](https://arxiv.org/abs/2609.28586v1)).

## Why it works

An approval surface binds the text of the invocation, not the workflow it starts. Approving `npm install` approves whatever `preinstall`, `install`, `postinstall`, and `prepare` do, because npm's documentation lists all four as part of what `npm install` runs ([npm docs: scripts](https://docs.npmjs.com/cli/v10/using-npm/scripts/)). The paper states the resulting limit as a lemma: when two executions present the same fields to a rule but need different decisions, "the decision path must conservatively represent the union, re-mediate, reject, or contain the unresolved effects" ([arXiv 2609.28586v1, §III-C](https://arxiv.org/abs/2609.28586v1)).

Claude Code's permissions documentation states the same limit from the enforcement side. A deny rule reaches a named path, not "arbitrary subprocesses that read or write files indirectly, like a Python or Node script that opens files itself," and its sandbox — the layer that does enforce on child processes — "applies only to Bash, PowerShell, and Monitor commands and their child processes" ([Claude Code permissions](https://code.claude.com/docs/en/permissions)), which is why an MCP tool call sits outside it.

## When this backfires

- A working OS sandbox already covers the command. Bash lifecycle-script effects are already contained after the decision, so reading more of the record before the decision changes no outcome — it only adds a prompt.
- High-volume autonomous review. The paper's own effect-aware fix routed 17 of 18 evaluated cases to an extra confirmation, and "9/17 reached cases are no-added-effect ASK cases under the realized-trace proxy" — over half the extra prompts told the reviewer nothing the bare command had not already shown ([arXiv 2609.28586v1, Table III](https://arxiv.org/abs/2609.28586v1)). Anthropic reports that on Claude Code's existing manual prompts, "users accept 93% of them anyway" ([Anthropic: Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)), so a richer prompt may not change what gets approved.
- Teams that already run `ignore-scripts=true` or pnpm 10 defaults with a tight `onlyBuiltDependencies`. pnpm 10 already turns off dependency lifecycle scripts by default — "this is a breaking change aimed at increasing security" ([pnpm v10.0.0 release notes](https://github.com/pnpm/pnpm/releases/tag/v10.0.0)) — so most install-time expansion this pattern targets is already closed. A root project's own `postinstall` still runs regardless.
- Parser false assurance. A predicted-effect model that reaches 0.926 macro recall on holdout workflows still leaves 3 residual effect instances uncovered, down from 10 without it; a report that looks complete can lower scrutiny below what a bare command prompt gets.
- Closed or remote MCP servers whose transport is not inspectable before the call. There is no metadata to read, so no reading of the record closes the gap.

## What actually closes the gap

Two controls do the work for shell commands: turning lifecycle scripts off by default, and OS-level sandboxing of what a command's children can reach. Effect-aware review adds value only where those two are absent.

- Pair a broad install allowlist (`Bash(npm install *)`, `Bash(pnpm install *)`) with `ignore-scripts=true` or pnpm 10's tight `onlyBuiltDependencies`, since npm's own config still runs a script "explicitly intended" by a command like `npm run-script` even with `ignore-scripts` set ([npm docs: config](https://docs.npmjs.com/cli/v10/using-npm/config)).
- Review the transport in `.mcp.json` when you approve an MCP server, not the tool name on each call — a shell sandbox does not reach an MCP call.
- Reserve effect-disclosure prompts for what containment cannot reach today. The paper's own Claude Code PreToolUse proof of concept measured a median 87.8 ms per call and, on the one case it demonstrated end to end, denied rather than auto-allowed ([arXiv 2609.28586v1, §VI-E](https://arxiv.org/abs/2609.28586v1)).

## Key Takeaways

- An approval record can be accurate about the command it names and still silent about the workflow that command starts.
- The pattern pays off only for effects that containment does not already reach: unsandboxed shell commands, MCP calls, and auto-allow rules.
- pnpm 10 and `ignore-scripts=true` already close most of the install-time gap this pattern targets; a root project's own `postinstall` is the part that survives both.
- The paper's own fix adds a confirmation to 17 of 18 evaluated cases and over half of those add no new information — effect disclosure is not free of the approval-fatigue cost it is meant to fix.
- The result rests on one un-replicated 2026 preprint with no released artifact or execution ledger.

## Related

- [The Skill Closure Declaration Gap](skill-closure-declaration-gap.md) — the same record-names-less-than-it-grants shape for Agent Skills instead of shell commands and MCP calls
- [Parser-Versus-Shell Evasion in Command Permission Checks](parser-versus-shell-permission-evasion.md) — a rule that matches the wrong command text; this page covers a rule that matches the right command and still misses its effects
- [Gate Agent Writes to Executable Config Files as Privileged Actions](gate-agent-writes-to-executable-config.md) — the write-side control on the same expansion sources, `.npmrc` and `.devcontainer/` included
- [MCP Approval-View Fidelity Gap and Unicode Concealment](mcp-metadata-approval-view-gap.md) — a different MCP approval gap, where the reviewer cannot even see the metadata the model reads
- [Safe Command Allowlisting: Reducing Approval Fatigue](safe-command-allowlisting.md) — the approval-fatigue trade-off this pattern's own fix runs into when it adds a confirmation
- [Approval Records That Bind No Identity and No Session](../patterns/anti-patterns/unbound-approval-records.md) — the identity side of the same record, where the approved command is reused by another agent or in a later session
