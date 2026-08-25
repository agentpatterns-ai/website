---
title: "Parser-Versus-Shell Evasion in Command Permission Checks"
term: "Parser-Versus-Shell Evasion"
description: "A permission rule matches the text of a command while the shell computes a richer function of that same text; the gap between the two is a bypass class that regenerates after each fix."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - command-text permission bypass
  - permission check parser evasion
  - shell spelling evasion
last_reviewed: 2026-08-18
maturity: emerging
---

# Parser-Versus-Shell Evasion in Command Permission Checks

> A command permission check reads a string; the shell executes a different function of that string, and every gap between them is a bypass.

Treat a command-text permission check as a heuristic pre-flight and place the control you actually rely on somewhere the shell cannot respell its input. The check matches a proposed command against rules. The shell then parses, expands, redirects, and resolves that same command through its own pipeline, and any spelling the two disagree about is a permitted execution of a denied effect. One harness shipped eight separately-numbered fixes to that disagreement across four releases between 2026-08-04 and 2026-08-14, and the record includes a revert, which is what makes this a design conclusion rather than a patching schedule.

## The conditions this conclusion depends on

Moving enforcement below the parser pays only where three things hold. Check them before weakening a command-text check that is currently carrying load.

- A layer below the parser exists on your platform, with the capabilities you assume. What the floor offers varies by host: Claude Code's sandbox credential masking runs "on Linux and WSL", while "on macOS file masking falls back to `deny`" ([changelog](https://code.claude.com/docs/en/changelog#2-1-221)). Where the floor is thinner than you pictured, the pre-flight is carrying more than its share.
- That layer does not match strings either. Claude Code 2.1.224 fixed "sandbox filesystem deny entries written with a trailing slash (e.g. `denyRead: \"~/.aws/\"`) being silently bypassable on Linux and macOS" ([changelog](https://code.claude.com/docs/en/changelog#2-1-224)). Relocating a text match one floor down relocates the defect with it. The representation has to change: an inode, a resolved handle, a syscall, or a server-side check on the protected action.
- You can pay the false-positive cost of tightening. Version 2.1.232 extended permission checks to input redirections and Cygwin-style symlinks; 2.1.233 reverted both and fixed "Windows auto mode repeatedly stopping for manual approval on ordinary `cd <dir> && <command> > file` Bash commands (a 2.1.232 regression)" ([changelog](https://code.claude.com/docs/en/changelog#2-1-233)). A check that interrupts routine work gets switched off.

## The evasion classes on record

Every entry below was fixed. The point is the shape they share: in each one the checker read a string that the shell resolved into something else.

| Class | What the check saw | What the shell did | Fixed in |
|---|---|---|---|
| Conditional-context execution | a `[[ ]]` test | zsh executed the command hidden inside it | [2.1.221](https://code.claude.com/docs/en/changelog#2-1-221) |
| Quote handling in paths | one path | PowerShell resolved a different one | [2.1.221](https://code.claude.com/docs/en/changelog#2-1-221) |
| Self-concealing commands | part of the command | all of it | [2.1.223](https://code.claude.com/docs/en/changelog#2-1-223) |
| Invisible padding | the visible span in the approval dialog | the padded remainder as well | [2.1.223](https://code.claude.com/docs/en/changelog#2-1-223) |
| Default-value poisoning | one command's parameters | later commands' file access, redirected via `$PSDefaultParameterValues` | [2.1.232](https://code.claude.com/docs/en/changelog#2-1-232) |
| Symlink resolution | a regular file | a write through a Cygwin-style link under Git Bash | [2.1.232](https://code.claude.com/docs/en/changelog#2-1-232) |
| Unchecked argument spellings | no path operand | a read of the file named by `< file` | [2.1.232](https://code.claude.com/docs/en/changelog#2-1-232) |
| Path-namespace spellings | a path UNC validation accepted | reached a remote host through the NT `\??\` device prefix, leaking NTLM credentials | [2.1.233](https://code.claude.com/docs/en/changelog#2-1-233) |

Two of those rows target different readers. The self-concealing command hid from the permission check; the invisible padding hid from the approval dialog a human was reading. One crafted string can defeat the automated gate and the person reviewing its output, and those are distinct defects with distinct fixes.

The classes are not one vendor's. Cursor patched an allowlist bypass reached "with backtick(`` ` ``) character or `$(cmd)`" in 1.3 and described the fix as "a more robust parser" ([GHSA-534m-3w6r-8pqr](https://github.com/cursor/cursor/security/advisories/GHSA-534m-3w6r-8pqr)), then patched a second in 2.3, where "certain shell built-ins can still be executed without appearing in the allowlist" by poisoning the environment that trusted commands read ([CVE-2026-22708](https://github.com/cursor/cursor/security/advisories/GHSA-82wg-qcm4-fp2w)). VS Code states the limit in its own documentation: "The rule-based auto-approval system uses best-effort command parsing that has known limitations. For example, quote concatenation or shell aliases might bypass the rules" ([VS Code security](https://code.visualstudio.com/docs/copilot/security)). Anything computed from that parse inherits the same limits, including the [risk badge](pre-execution-command-risk-classification.md) shown to a human before the command runs.

## Why it works

Placing the control below the parser works because it collapses an unbounded matching problem into a bounded one. A permission rule is a predicate over a command string, and the effect that string produces is decided by the shell's own parse-expand-execute pipeline, a much richer function of the same input. Soundness would require reimplementing that pipeline exactly for every shell in play (bash, zsh, PowerShell, Git Bash over Cygwin) and every path namespace those shells reach, each an independently evolving grammar. The research side concedes the same boundary. CARE's authors write that "The goal of canonicalization is bounded normalization, not full semantic recovery", and position their gate as "a complementary *pre-execution* defense rather than a replacement for sandboxing, host hardening, or TOCTOU-safe enforcement" ([Liu et al., 2026](https://arxiv.org/abs/2607.21642v2)).

The effect a rule protects is the tractable half. A file write, an outbound connection, a merge into a protected branch: each is one well-defined event at one boundary, so a check placed there models a single thing rather than several grammars. Version 2.1.234 shows the price of the alternative, hardening "remote file reads, session restore, CLAUDE.md includes, workflow scripts and file uploads" against the same `\??\` spelling that 2.1.233 had already blocked at UNC path validation ([changelog](https://code.claude.com/docs/en/changelog#2-1-234)). One spelling, five more surfaces, because each ran its own string check. VS Code draws the conclusion directly: "Agent sandboxing is the strongest protection against malicious terminal commands."

## When this backfires

- The parser is your only control and you weaken it. The advice is to stop depending on a text match, never to delete one. A pre-flight that produces an explanatory denial at the moment of the mistake keeps its value even where it cannot be made sound.
- The lower layer is imperfect too, so this buys a better position rather than a guarantee. The clearest case is condition 2 repeating one layer down: a "SOCKS5 hostname null-byte injection that can be exploited to trick the sandbox allowlist filter into approving connections it should block" ([The Register, 2026-05-20](https://www.theregister.com/security/2026/05/20/even-claude-agrees-hole-in-its-sandbox-was-real-and-dangerous/5243662)) — an allowlist *filter* matching strings, which relocates the parser defect rather than escaping it. A defect that is genuinely different in kind looks like 2.1.232's "Hardened the Linux filesystem sandbox against a protected-path bypass" ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-232)): a bug in one implementation that stays fixed, where the parser gap is a property of finite rules meeting unbounded spellings.
- The protected effect has no chokepoint. Arbitrary developer shell work in a trusted repo exists only as "a command", with no server-side gate to move enforcement to. The answer there is a human decision rather than a better parser.
- Traffic is stereotyped rather than adversarial. On the CVE-derived Exploit-DB corpus, plain regex beat the full CARE pipeline on F1, 81.52% against 66.33% — the paper's own summary is that CARE "trails Regex on Exploit-DB (66.33 vs 81.52), where CVE proof-of-concepts embed stereotyped destructive idioms" that keyword matching captures without context ([Liu et al., 2026, §V-C2](https://arxiv.org/abs/2607.21642v2)). Sophistication in the matching layer is not monotonically better.

## Key Takeaways

- A command-text permission check and the shell compute different functions of the same string. Every spelling they disagree about is a bypass, so the class regenerates after each fix rather than being exhausted by it.
- Eight separately-shipped fixes across four releases in one ten-day window of a single changelog, plus two Cursor advisories a major version apart, put this in the structural column rather than the bug-count column.
- Anything unparseable must deny. Several entries on record are cases where the checker parsed something and matched nothing.
- Verify that the layer you move enforcement to is not another string match. A `denyRead` entry defeated by a trailing slash is the same defect one floor down.
- One spelling blocked at one surface stays open at the others. Enforce on the effect, which has one boundary, instead of on the command, which has as many spellings as your shells have grammars.
- Budget for the revert. Tightening a checker to cover a new spelling catches benign traffic too, and a control that interrupts routine work does not survive contact with a working team.

## Related

- [Static-First Shell Command Gating with Selective Escalation](static-first-shell-command-gating.md) — the cost model for classifying commands well; this page is why even a well-canonicalized verdict stays a pre-flight
- [Safe Command Allowlisting](safe-command-allowlisting.md) — the approval-fatigue case for allowlists, whose broad globs are what these evasions exploit
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — the same sorting question one level up: where a safeguard is evaluated decides whether it binds
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — the layer the conclusion points at, and the one a parser gap falls through to
- [Dual-Boundary Sandboxing: Filesystem and Network Isolation](dual-boundary-sandboxing.md) — what enforcement below the shell looks like when it is built deliberately
