---
title: "Treating a Worktree as a Safety Boundary"
term: "Worktree as a Safety Boundary"
description: "A git worktree bounds where an agent's edits land, not what its process can reach. The same user, credentials, and filesystem sit on both sides of it."
tags:
  - anti-pattern
  - security
  - multi-agent
  - tool-agnostic
aliases:
  - worktree isolation is not a sandbox
  - placement versus reach
last_reviewed: 2026-08-18
maturity: emerging
---

# Treating a Worktree as a Safety Boundary

> A worktree decides where an agent's edits land. It does not decide what the agent's process can reach.

A git worktree gives each agent its own directory and branch, so parallel agents stop overwriting each other's files. That is all it does. The agent still runs as the same operating system user, holds the same credentials, and sees the same filesystem, so a command it composes can name a path outside its tree. VS Code's harness documentation states this without hedging: "A worktree is a Git code-isolation boundary, not a security boundary. It does not restrict commands, network access, or access to files outside the worktree" ([VS Code — Agent harnesses](https://code.visualstudio.com/docs/agents/concepts/agent-harnesses)).

## When the distinction matters

If you isolate agents for merge hygiene, a worktree is the right control and the rest of this page is optional. The distinction matters once "isolated" does safety work: when it is why a fan-out runs unattended, why an approval prompt was switched off, or why a second control was never added. Cursor names the condition underneath: "There is no security boundary between agents and your user account. If your account can delete files, agents can delete files (with approval by default)" ([Cursor LLM safety and controls](https://cursor.com/docs/enterprise/llm-safety-and-controls)).

## Placement and reach

Two guarantees hide under one word. Placement means the edits this agent makes land inside its own tree, so siblings do not collide. Reach means this agent cannot touch anything outside its tree at all. A worktree gives placement by construction and reach never, and harness vendors have shipped the difference as a real defect. Claude Code fixed worktree-isolated subagents "redirecting git into the shared checkout via `git -C`, `--git-dir`, or `GIT_DIR`/`GIT_WORK_TREE`" in 2.1.216, then fixed worktree-isolated sessions and subagents "being able to run destructive git commands against the main checkout" in 2.1.222, with the same class of fix shipping in 2.1.196 ("running shell commands in the parent checkout instead of their own worktree") and 2.1.210 ("run git-mutating commands against the main repo checkout") before either ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

Spending the first guarantee as though it were the second is the anti-pattern, and it ships as a default. VS Code sets agent sessions in a worktree to the permission level that "auto-approves all tool calls without showing confirmation dialogs" ([VS Code approvals documentation](https://code.visualstudio.com/docs/agents/run/approvals)), giving a placement fact as the reason: "Worktree sessions use Bypass Approvals because their code changes are separate from your active workspace" ([VS Code Copilot CLI sessions](https://code.visualstudio.com/docs/copilot/agents/background-agents)). Approval prompts are a reach control. Separate code changes are a placement property.

## Why it works

Reach containment works when some layer outside the model evaluates it, the distinction [enforced versus advisory controls](../../security/enforced-versus-advisory-controls.md) draws. A worktree is not such a layer, because it shares the repository on purpose. Git commands run inside a worktree "write to the main repository's shared `.git` directory", project-scope plugins load from the main checkout, and a saved permission approval "applies in the main checkout and in every other worktree of the repository, and it survives the worktree's removal" ([Claude Code worktrees documentation](https://code.claude.com/docs/en/worktrees)). A path back to the main repository exists by design, and that same sharing is what makes worktree creation cheap.

Containment therefore comes from something that denies, and two layers do. Tool-layer checks inspect each command before it runs: Claude Code applies four inside an isolated session, failing closed by refusing "shell constructs it can't statically trace, such as brace expansion and heredocs with unquoted delimiters" ([Claude Code worktrees documentation](https://code.claude.com/docs/en/worktrees)). Coverage is then a property of the parser, which is why the same defect needed four releases and why the same page records that "for PowerShell commands, Claude Code applies only the working-directory check". Kernel-layer sandboxing inspects the syscall instead, so "sandboxed processes and all of their child processes cannot bypass these boundaries, even if a command is crafted to attempt it" ([VS Code trust and safety](https://code.visualstudio.com/docs/agents/concepts/trust-and-safety)), implemented as Seatbelt on macOS and Landlock plus seccomp on Linux ([Cursor run modes](https://cursor.com/docs/agent/security/run-modes)).

## When this backfires

Adding a reach control is a decision with costs, not a default:

- Local sessions with no untrusted input. The agent runs the operator's code under the operator's credentials either way, so a kernel sandbox buys containment against a threat that is not in the room.
- Sandboxes that break the work they contain. Cursor's sandbox blocks network by default, opened by the network mode and `sandbox.json` ([Cursor run modes](https://cursor.com/docs/agent/security/run-modes)), so dependency installs fail until an allowlist is curated. A control switched off after the first broken build leaves the team with neither.
- Reasoning in the opposite direction. A container per agent that mounts one shared working tree restores the silent-overwrite problem the worktree solved. The two guarantees are orthogonal.
- Write surfaces that are not files. A shared Postgres, a port, a Docker daemon, or a repository token is reached by neither a worktree nor a filesystem sandbox. [Worktree isolation](../../workflows/worktree-isolation.md) covers the runtime-state half of that gap.

## Example

The two guarantees are declared on two different surfaces. Placement goes in the subagent definition:

```yaml
# .claude/agents/refactorer.md frontmatter
isolation: worktree
```

Reach goes in the sandbox settings, and the sensitive keys are honored only from the sources an operator controls — "User settings, managed settings, and the `--settings` CLI flag can set it. Project settings in `.claude/settings.json` and `.claude/settings.local.json` can't, so a checked-out project can't switch filesystem isolation off" ([Claude Code sandboxing](https://code.claude.com/docs/en/sandboxing)):

```json
{ "sandbox": { "filesystem": { "denyRead": ["~/.ssh", "~/.aws"] } } }
```

The worktree still prevents the merge conflicts it was chosen for. Keeping only the first block, and reading it as a reason to switch approvals off, is the anti-pattern.

## Key Takeaways

- Name which guarantee you are buying before you buy it: placement stops sibling agents colliding, reach stops a process leaving its tree, and only the first is what a worktree sells.
- Vendors document the gap: VS Code calls a worktree "not a security boundary", and Cursor states there is no security boundary between agents and your user account.
- The gap is not theoretical. Claude Code shipped fixes for worktree-isolated agents reaching the main checkout in 2.1.196, 2.1.210, 2.1.216, and 2.1.222.
- Worktrees share the main repository's `.git`, plugins, and saved permission approvals, so a path back exists by design.
- Decide the second control against a threat model. If merge hygiene is the reason for isolating, a worktree alone is a complete answer.

## Related

- [Worktree Isolation: Parallel Agent Sessions in Safe Sandboxes](../../workflows/worktree-isolation.md) — what worktrees do provide, and the runtime state they leave shared
- [Blast Radius Containment: Least Privilege for AI Agents](../../security/blast-radius-containment.md) — scoping the permissions a contained agent still holds
- [Dual-Boundary Sandboxing: Filesystem and Network Isolation](../../security/dual-boundary-sandboxing.md) — the reach control a worktree does not supply
- [Enforced Versus Advisory Controls in LLM-Native IDEs](../../security/enforced-versus-advisory-controls.md) — sorting safeguards by where they are evaluated
- [Sub-Agents for Fan-Out Research and Context Isolation](../multi-agent/sub-agents-fan-out.md) — the fan-out that reaches for worktrees in the first place
