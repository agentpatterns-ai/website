---
title: "Treating Read Denial as Confidentiality for a Build Input"
term: "Read Denial on a Build Input"
description: "Fifteen read routes to a protected build input, classified against four mechanisms an ordinary user can configure: five are refused by neither the permission rules nor the sandbox, and none of the four can say which program is reading."
aliases:
  - purpose-based access control for coding agents
  - protecting build inputs from a coding agent
  - build-input read confidentiality
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-01
maturity: emerging
---

# Treating Read Denial as Confidentiality for a Build Input

> The compiler must open a build input, and no rule that matches a path or a command can tell its read from the agent's.

Four conditions have to hold together before this costs anything, and all four come from the deployment Shobhan Roy describes ([arXiv:2609.35557v1](https://arxiv.org/abs/2609.35557v1)). The protected file is an input the build cannot run without. You are an ordinary user of the harness, so you cannot load a kernel policy or replace the language runtime. The agent and the build share one account, and the compiler starts from the agent's own shell. And something follows from the bytes reaching a transcript, such as a license term that permits publishing results but not passing on the algorithms. Drop one of the four and the ordinary advice on [protecting sensitive files](../../security/protecting-sensitive-files.md) applies instead.

## Which routes each mechanism covers

Shobhan Roy classified fifteen ways the protected bytes could reach a coding agent's context in one deployment. The two mechanisms that enforce anything divide the work rather than sharing it: "Two routes are covered by both, seven by the sandbox alone, one by the permission rules alone, and five by neither" ([arXiv:2609.35557v1](https://arxiv.org/abs/2609.35557v1)). Documented scope explains the division. Claude Code's sandbox "applies only to Bash, PowerShell, and Monitor commands and their child processes". The built-in tools go the other way: "Read, Edit, and Write use the permission system directly rather than running through the sandbox" ([Claude Code — Sandboxing](https://code.claude.com/docs/en/sandboxing)). That page corroborates the sandbox half of two of the five, warning that a command could "add a hook or MCP server that Claude Code runs outside the sandbox".

## Why it works (the criterion is not in any of the four)

Four mechanisms sit between the agent and the file here: the container, the permission rules, the sandbox, and the instruction file. "Out of the box, none of the four can state the criterion the rule turns on, which is which program is reading" ([arXiv:2609.35557v1](https://arxiv.org/abs/2609.35557v1)). No attribute is left for them to decide on, because "The agent and the build run as one user account, and the compiler is a child of the agent's own shell, inside the agent's container". So the compiler is the route that tightening cannot reach: "A direct read is refused while gfortran -E f is not, though the compiler names the path as plainly as cat does." The permission the build requires is what the route uses. Roy uses the literature's own names rather than coining one. The rule the deployment wants is purpose-based access control; the uncovered routes are a failure of complete mediation.

## What tightening the list buys

Roy kept one deny list under revision for five weeks with the protected paths held still. Four revisions took it from 14 rules to 488, 540, 556 and 586, adding 118, 13, 4 and then zero new command names. The fourth is the informative one: 30 new rules and no new name, extending fifteen already-listed commands from the directory to the single file. "What the revision fixed was a missing invariant rather than a missing command" ([arXiv:2609.35557v1](https://arxiv.org/abs/2609.35557v1)).

## When this backfires

Read this as a limit on what you claim for the boundary rather than a reason to remove it. Roy still runs the arrangement, and it produced 64 denial events over seven weeks of ordinary research work. No denial in that corpus blocked ordinary work on the protected files, and he states that "none of these counts supports a rate" ([arXiv:2609.35557v1](https://arxiv.org/abs/2609.35557v1)).

- You administer the host kernel. SELinux type enforcement moves a process into a domain on exec, so the kernel can refuse the agent's domain while the compiler proceeds. The answer is a privileged policy loader, not a longer list.
- The protected files are stable and sit apart from the code the agent works on. Hold them under a second account behind a build recipe the agent cannot edit. That trusted broker "approximates the rule rather than enforcing it", and it charges the edit-build-fix loop.
- Process lineage does not settle it. In [ActPlane](https://arxiv.org/abs/2606.25189v2) the tags propagate through fork and exec, so the compiler inherits the agent's label and the build fails. Name the compiler as an exception and "The exception that exists for the build is available to the agent on the same terms."
- One deployment, one vendor's rule syntax, one rater. Two routes were seen refused in practice against a decoy tree, the other thirteen were never run against the protected files, and the table "is not a measure of how often an attack would be stopped".

## Key Takeaways

- Ask whether the build opens the file before writing a read-denial rule for it. If it does, the exception that rule needs for the compiler is itself a route to the contents.
- Tightening stops finding new commands long before it closes the gap. Roy's fourth revision added 30 rules and no new command name ([arXiv:2609.35557v1](https://arxiv.org/abs/2609.35557v1)).
- Of any read control, work out which of three things it names: the account, the path, or the program consuming the bytes. Only the third expresses this rule.
- Both outputs the build is allowed to return carry content derived from the protected file, the diagnostic in the line it quotes and the compiled artifact in the models' constants ([arXiv:2609.35557v1](https://arxiv.org/abs/2609.35557v1)). A filter on the build's reply is the control, not a rule on the file.

## Related

- [Protecting Sensitive Files from Agent Context Access](../../security/protecting-sensitive-files.md) — the path-rule and pre-read-hook approach, which holds for a file nothing else has to open
- [Content Exclusion Gap: AI Security Boundaries by Mode](../../instructions/content-exclusion-gap.md) — the same boundary failing across a vendor's interaction modes, with filesystem-level restriction offered as the fix
- [Parser-Versus-Shell Evasion in Command Permission Checks](../../security/parser-versus-shell-permission-evasion.md) — the other half of why a command-text rule misses a read: the shell respells its own input
- [Treating a Worktree as a Safety Boundary](worktree-as-safety-boundary.md) — the same account, credentials, and filesystem on both sides of a boundary that only places edits
- [Revocable Resource-and-Effect Capabilities for Coding Agents (PORTICO)](../../security/revocable-resource-effect-capabilities.md) — a mechanism that does bind a path to an access mode, and models one consumer rather than two
