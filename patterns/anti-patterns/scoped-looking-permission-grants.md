---
title: "Scoped-Looking Permission Grants"
term: "Scoped-Looking Grant"
description: "A permission rule naming one interpreter or one runner permits every command; 3.1% of scanned agent setups carry one and 3.8% ship one inside a published skill."
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
aliases:
  - scoped-looking grant
  - interpreter wildcard permission
  - Bash(python:*) grant
last_reviewed: 2026-09-09
maturity: emerging
---

# Scoped-Looking Permission Grants

> A permission rule that names one interpreter or one runner permits every command, and the syntax gives no hint.

`Bash(python:*)` grants what `Bash(*)` grants, and Kapner et al. put it exactly that way ([arxiv:2609.07360v1](https://arxiv.org/abs/2609.07360v1)). So do `Bash(awk:*)`, `Bash(sed:*)`, `Bash(npx:*)`, and any rule naming a program whose argument is itself a program. Scanning 3,171 public GitHub repositories, Kapner et al. found 3.1% of 2,660 assembled agent setups pre-approving arbitrary execution this way, and another 3.8% carrying a skill whose `allowed-tools` list ships that pre-approval to whoever installs it ([arxiv:2609.07360v1](https://arxiv.org/abs/2609.07360v1)).

## When the grant is the boundary

Two conditions decide whether this costs anything. The first is containment: if a sandbox already bounds the process, the allow list is a prompt-reduction setting and tightening it buys friction. The second is distribution. A grant in your own repo risks the machine you already trust, while a grant inside a published skill executes on every machine that installs it. That difference decides where the check runs. A skill's `allowed-tools` is readable at publication, so a marketplace can scan it; an allow list only exists once components are assembled, so a team has to check it on the pull request that adds one ([arxiv:2609.07360v1](https://arxiv.org/abs/2609.07360v1)).

## Why it works (the grant inherits the interpreter's input language)

A Bash rule matches command text. The program that text names then accepts a program as an argument, so the rule's real scope is the scope of that program's input language, which has no upper bound. Claude Code's documentation states the mechanism for runners: "Because these tools execute their arguments as a command, a rule like `Bash(devbox run *)` matches whatever comes after `run`, including `devbox run rm -rf .`" ([Configure permissions](https://code.claude.com/docs/en/permissions)). Kapner et al. enumerate the same reachability for utilities: "awk evaluates commands via `system()`, `python -c` runs anything, `find -exec` spawns processes, and GNU sed runs commands through its e flag" ([arxiv:2609.07360v1](https://arxiv.org/abs/2609.07360v1)). Anthropic acts on the same reading: entering auto mode drops "blanket shell access, wildcarded script interpreters (python, node, ruby, and similar), and package manager run commands" so the classifier still reviews them ([How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)).

No respelling is involved, so this is not [parser-versus-shell evasion](../../security/parser-versus-shell-permission-evasion.md). The check reads the string correctly, and the string permits everything.

## When this backfires

Rewriting an allow list to remove these grants is worth less than it looks in several common setups.

- A setup that already allows a build, test, or package-manager script reaches the same capability through repo-controlled code. Anthropic classes "package manager run commands" with the interpreters for this reason ([How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)). Removing the interpreter grant narrows the visible surface only.
- Enumerating one rule per inner command ages badly. Every new script needs an entry, and the list drifts back toward a broad grant.
- The finding may sit in a template, example, or fixture directory. On the 18 gating and provisional pairs carrying a headline figure, the study's independent reviewer agreed with its adjudicator on 10, and "every disagreement is an unpinned package inside a shipped template, an example directory, or a test fixture" ([arxiv:2609.07360v1](https://arxiv.org/abs/2609.07360v1)).
- Intent is not measurable from bytes, and the authors say so: "Whether they understood that `Bash(python:*)` is `Bash(*)` is a claim about expectations that no static audit can measure." The study also confirmed no credential-exfiltration path, so this is a hygiene finding rather than an incident report.

Consequences are dated too. A `Bash(find *)` rule in Claude Code no longer covers `find -exec` or `-delete`, and exec wrappers such as `watch` and `flock` cannot be auto-approved by a prefix rule at all ([Configure permissions](https://code.claude.com/docs/en/permissions)). `python`, `awk`, `npx`, and `docker exec` remain open.

## Example

The grant that reads as narrow:

```json
{
  "permissions": {
    "allow": ["Bash(python:*)", "Bash(npx:*)", "Bash(awk:*)"]
  }
}
```

Each entry approves every command the named program can be told to run. Claude Code's remedy is to name both halves: "write a specific rule that includes both the runner and the inner command, such as `Bash(devbox run npm test)`. Add one rule per inner command you want to allow." ([Configure permissions](https://code.claude.com/docs/en/permissions))

```json
{
  "permissions": {
    "allow": ["Bash(python scripts/build.py)", "Bash(npx tsc --noEmit)"]
  }
}
```

Anthropic says a list of this kind "will inevitably be incomplete" ([How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)). That is the argument for putting the durable boundary in a sandbox.

## Key Takeaways

- A permission rule naming an interpreter, a shell-escape utility, or a package runner grants arbitrary execution. The narrow-looking syntax is the whole problem.
- Read the measured rates as a floor. The authors call every headline figure "a lower bound on the defects the instrument can express", and their corpus over-represents repositories that advertise their tooling ([arxiv:2609.07360v1](https://arxiv.org/abs/2609.07360v1)).
- Audit your own allow list by asking one question of each entry: does the named program take a program as an argument? If yes, the entry is `Bash(*)`.
- Fix by naming the runner and the inner command together, and accept that the list needs maintenance.
- Do this work only where the allow list is the boundary. Under a sandbox it is prompt reduction, and the effort is better spent on the sandbox.

## Related

- [Parser-Versus-Shell Evasion in Command Permission Checks](../../security/parser-versus-shell-permission-evasion.md) — the adjacent failure where the check and the shell disagree about one command string
- [bypassPermissions Silently Overrides allowedTools](bypass-permissions-overrides-allowlist.md) — the other way a permission config reads as restrictive and is not
- [Safe Command Allowlisting: Reducing Approval Fatigue](../../security/safe-command-allowlisting.md) — the practice this anti-pattern is a failure mode of
- [Skill Shell Execution Gate](../../security/skill-shell-execution-gate.md) — the managed-settings control for shell side-effects arriving through skills
- [Agent Config as a Managed Supply Chain](../../instructions/agent-config-as-managed-supply-chain.md) — pinning and hashing for the same harness layer these grants live in
