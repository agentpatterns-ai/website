---
title: "Gate Agent Writes to Executable Config Files as Privileged Actions"
description: "Writes to build-tool config files like .npmrc, .yarnrc, bunfig.toml, .bazelrc, .pre-commit-config.yaml, and .devcontainer/ are execution-escalations — gate them at the write site even under permissive edit modes."
term: "Gate Agent Writes to Executable Config"
tags:
  - security
  - tool-agnostic
aliases:
  - executable config write gate
  - acceptEdits build-tool config prompt
  - privileged write gate for code-execution config
last_reviewed: 2026-08-28
maturity: adopted
---

# Gate Agent Writes to Executable Config Files as Privileged Actions

> Treat agent edits to build-tool config files that grant code execution as privileged actions requiring confirmation, even under permissive edit modes.

A write to a code-execution config file is an execution-escalation, not an ordinary edit. The bytes the agent commits become standing authorization for execution in every future install, commit, build, or container-attach. Harnesses under permissive modes (`acceptEdits`, `auto`) should still cross a confirmation boundary at the write site. The user's prior trust on "this folder" did not contemplate this specific set of bytes ([Mindgard — Approve Once, Exploit Forever, 2026](https://mindgard.ai/blog/approve-once-exploit-forever-the-trust-persistence-problem-in-ai-coding-agents)).

## When this pattern applies

The gate helps only when three conditions hold. Mis-scoped, it collapses into the confirmation-fatigue failure mode already documented under [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md).

| Condition | Why it matters |
|---|---|
| The harness has a permissive edit mode the user routinely enables (`acceptEdits`, `auto`, "always accept", "yolo") | Without permissive modes, every edit already gates by default and the executable-config prompt is redundant. The gate exists to interrupt the permissive default for one specific file class. |
| The gate is scoped to executable-config paths only | Adding the prompt to every write devolves into confirmation fatigue — T10 in Rippling's 2025 Agentic AI Security guide. |
| The gate complements execution-side defaults rather than replacing them | Pinning `ignore-scripts=true` in `.npmrc`, `min-release-age=7`, sandboxed devcontainers, and pinned pre-commit hooks stay primary. The write gate catches the case where those defaults are about to be silently flipped. |

If any condition fails, fix that gap first.

## What counts as an executable config file

Claude Code's 2.1.160 changelog (2026-06-02) names the canonical set: "`acceptEdits` mode now prompts before writing build-tool config files that grant code execution (`.npmrc`, `.yarnrc*`, `bunfig.toml`, `.bazelrc`, `.pre-commit-config.yaml`, `.devcontainer/`, etc.)" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). The same release also gates shell-startup files (`.zshenv`, `.zlogin`, `.bash_login`) and `~/.config/git/`.

The structural property each file shares is that its bytes authorize subsequent code execution:

| File class | Execution surface it controls |
|---|---|
| `.npmrc`, `.yarnrc.yml`, `bunfig.toml` | Whether `npm`/`yarn`/`bun install` runs `preinstall`/`install`/`postinstall` lifecycle scripts; `ignore-scripts=true` is the [OWASP NPM cheat sheet's single most effective mitigation](https://www.nodejs-security.com/blog/npm-ignore-scripts-best-practices-as-security-mitigation-for-malicious-packages). `.yarnrc.yml` also points at plugin paths that execute on every Yarn run ([Snyk on Yarn 2 plugins](https://snyk.io/blog/yarn-2-plugins/)). |
| `.bazelrc` | Startup options applied to every `bazel` invocation ([Bazel bazelrc reference](https://bazel.build/run/bazelrc)). |
| `.pre-commit-config.yaml` | Arbitrary commands run on every `git commit`. |
| `.devcontainer/devcontainer.json` | `postCreateCommand`, `postStartCommand`, `postAttachCommand` execute inside the container with significant privileges; `docker-from-docker` mounts escalate to host access ([McCrindle — Exploiting VS Code Devcontainers](https://foldr.uk/exploiting-visual-studio-code-devcontainers/)). |
| Shell-startup files (`.zshenv`, `.zlogin`, `.bash_login`) | Run on every shell session start; an agent edit silently rewires every future terminal Claude or the user opens. |
| `~/.config/git/` | Git config can declare `core.editor`, `core.pager`, `core.fsmonitor`, and aliases that execute on routine git operations. |

The list is not closed. The mechanism — bytes that authorize future execution by other programs — is the same reason operating systems prompt before edits to `/etc/sudoers` or `~/.ssh/authorized_keys`.

## Why it works

Folder-level trust is durable. When the user accepted "trust this folder" at session start (or workspace-trusted in Cursor or Copilot), the consent was scoped to the contents the user reviewed at that moment. An agent edit changes those contents, and durable trust admits the change without a fresh prompt. The Mindgard "Persistent Trust Flaws in AI Coding Agents" research demonstrates the staleness problem directly: trust decisions tied to paths rather than to the thing being run persist past the moment of consent ([Mindgard, 2026](https://mindgard.ai/blog/approve-once-exploit-forever-the-trust-persistence-problem-in-ai-coding-agents)).

Gating the write restores the trust boundary at the point where the execution surface changes, before the next install, commit, or attach acts on the change. Google's 2026 security research frames the broader claim: "Opening a project, trusting a workspace, starting a debugger, rebuilding a container, or running a standard setup command may therefore execute attacker-controlled logic under the appearance of legitimate project automation" ([Google Cloud — Beyond source code](https://cloud.google.com/blog/products/identity-security/beyond-source-code-the-files-ai-coding-agents-trust-and-attackers-exploit)).

Two attack vectors converge on the same gate:

1. Direct injection — untrusted content (a fetched web page, an issue comment, a PR description) instructs the agent to flip `ignore-scripts=true` to `false` in `.npmrc`. Without the gate, the change lands silently under permissive edit mode and the next `npm install` runs lifecycle scripts. The [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) covers the upstream injection vector; the executable-config gate is a downstream control point.
2. Authority confusion — the agent rationalizes an "innocuous" config tweak as part of a legitimate task without recognizing that the bytes change the execution posture. This is the same class of error as [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md), but it targets the file-write boundary specifically.

## Differentiation from adjacent patterns

This gate addresses a surface that the existing pages on this site leave open:

- [Pre-Trust Execution Surface in Coding Agent Harnesses](pre-trust-execution-surface.md) covers the harness's own config (`.claude/settings.json`, `.mcp.json`) being read and executed before the trust prompt fires. This page covers build-tool config (`.npmrc`, `.bazelrc`, `.devcontainer/`) written by the agent after trust is granted. Different time domain, different file classes.
- [Agent-Emitted Dependency Version Ranges](agent-emitted-dependency-ranges.md) covers caret and tilde ranges in the manifest (`package.json`). This page covers the adjacent config (`.npmrc`) that controls whether install-time scripts run at all — orthogonal layers of the same supply-chain surface.
- [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md) enumerates Send, Purchase, Delete, Share, and Modify-auth as the consequential action classes. This page adds Write-executable-config as a structurally distinct sixth class. The action's consequence is not the write itself but the standing authorization it confers.
- [Pre-Execution Risk Classification for Terminal Commands](pre-execution-command-risk-classification.md) classifies terminal commands, not file writes. The write gate is the same shape applied to a different action class.

## When this backfires

- Greenfield scaffolding — when you expect the agent to author `.npmrc`, `.devcontainer/devcontainer.json`, or `.pre-commit-config.yaml` as part of project bootstrap, the gate fires on every legitimate step. Suppress the gate during explicit scaffolding flows, or scope it to changes of existing files rather than initial creation.
- Headless CI agent runs — background jobs have no human at a prompt, so the gate either fails the run or auto-bypasses, defeating itself. Use pre-merge config review or sandbox isolation instead ([Pre-Trust Execution Surface §Headless CI](pre-trust-execution-surface.md)). GitHub reports that push rules in rulesets now support path exceptions. That adds a server-side enforcement point for this same pattern ([Push rules in rulesets now support path exceptions](https://github.blog/changelog/2026-08-25-push-rules-in-rulesets-now-support-path-exceptions)).
- Confirmation-fatigue collapse — a multi-file refactor pass that touches ten config paths trains the reviewer to rubber-stamp. The same dynamic is flagged in [Confirmation Gates §When This Backfires](human-in-the-loop-confirmation-gates.md) and in [Approval Fatigue Is Breaking AI Agents (Edulakanti, 2026)](https://medium.com/@shreya_edulakanti/approval-fatigue-is-breaking-ai-agents-execution-boundaries-fix-it-6c46c6d512dd). Keep the gate's file scope narrow.
- Lies-in-the-Loop dialog manipulation — an injected payload manipulates how the confirmation renders, so the user approves a diff that looks like a benign preference change but actually adds a `postinstall` script. Researchers demonstrated this against Claude Code and Copilot Chat in 2025 ([Checkmarx — Bypassing AI Agent Defenses With Lies-In-The-Loop](https://checkmarx.com/zero-post/bypassing-ai-agent-defenses-with-lies-in-the-loop/)). Surface the exact diff and parse for `preinstall`, `postCreateCommand`, and plugin paths in the dialog text.
- Long-lived trust persistence — folder trust outlives any single approved edit. A teammate's PR review session weeks later picks up a config file the agent now treats as already trusted. Pair the write gate with periodic trust invalidation on config-file changes ([Mindgard, 2026](https://mindgard.ai/blog/approve-once-exploit-forever-the-trust-persistence-problem-in-ai-coding-agents)).
- Compositional vulnerability induction — an adversary breaks the malicious end-state into edits, each below the gate's salience threshold ([Compositional Vulnerability Induction](compositional-vulnerability-induction.md)). Mitigate by classifying on the resulting execution surface, not on diff size.

## Example

The Claude Code 2.1.160 release ([2026-06-02 changelog](https://code.claude.com/docs/en/changelog)) added the gate behavior described above. The shape generalizes to any harness with a permissive edit mode.

Before — `acceptEdits` honors every write to executable-config:

```text
User: read the README and set up the project
Agent: I'll add a .npmrc to make installs faster.

# Writes .npmrc with the following content, no prompt:
ignore-scripts=false

User: <unaware that the next `npm install` will now run lifecycle scripts>
```

After — `acceptEdits` interrupts for the executable-config class:

```text
User: read the README and set up the project
Agent: I'll add a .npmrc to make installs faster.

[harness] Claude wants to write .npmrc:
  +ignore-scripts=false
  This file controls npm install-time code execution. Approve? [y/N]

User: <sees the exact byte change, can reject>
```

The gate does not replace `ignore-scripts=true` as the project's resident default — it interrupts the agent's attempt to flip the default under a permissive edit mode.

## Key Takeaways

- A write to an executable-config file is an execution-escalation, not an ordinary edit — the bytes confer standing authorization for code execution in every future install / commit / build / attach against the repo.
- The canonical file classes are package-manager rc files (`.npmrc`, `.yarnrc.yml`, `bunfig.toml`), build-tool configs (`.bazelrc`), pre-commit hooks (`.pre-commit-config.yaml`), devcontainer files (`.devcontainer/`), shell-startup files, and git config.
- The gate is net-positive only when the harness runs a permissive edit mode, the gate is scoped tight to executable-config paths, and it complements execution-side defaults like `ignore-scripts=true` and `min-release-age`.
- The remediation generalizes across coding-agent tools — any harness with `acceptEdits`/`auto`/"always accept" modes has the same write-time surface and needs the same gate.
- The gate is distinct from the pre-trust read surface, the agent-emitted dependency-range surface, and the terminal-command pre-execution surface — it is a write-time control for the file class whose contents become execution authorization.

## Related

- [Pre-Trust Execution Surface in Coding Agent Harnesses](pre-trust-execution-surface.md)
- [Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface](agent-emitted-dependency-ranges.md)
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md)
- [Pre-Execution Risk Classification for Terminal Commands](pre-execution-command-risk-classification.md)
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
