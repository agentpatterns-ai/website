---
title: "Judging a Write by Its Spelled Path (Spelled-Path Scope)"
term: "Spelled-Path Scope"
description: "A permission rule matches a path string while the filesystem resolves it. Resolving the path before deciding narrows that gap; hard links and a check-to-open race keep it open."
tags:
  - anti-pattern
  - claude
  - security
aliases:
  - spelled-path scope
  - unresolved path permission check
  - path spelling versus destination
last_reviewed: 2026-10-06
maturity: emerging
---

# Judging a Write by Its Spelled Path (Spelled-Path Scope)

> A path guard decides on the name the agent wrote; the kernel decides where that name resolves, and the two disagree without any respelling.

Resolve the path before you decide on it, and name the resolved destination in whatever a human approves. Two conditions decide whether that is worth doing. Links have to be possible on the host. The guard has to be the boundary, not a pre-flight above a sandbox. Where both hold, the fix is cheap and still incomplete.

Nothing here needs a respelling, a quoting trick, or a second shell. One unambiguous path, parsed identically by the guard and by the kernel, still reaches two different files.

## What the record shows

A keyword pass over the Claude Code [changelog](https://code.claude.com/docs/en/changelog), read through by hand afterwards, finds 24 entries across 20 releases where a symlink, hard link or junction decided a permission, an approval, or whether something stayed inside its boundary. The earliest is 2.1.69 and the most recent is 2.1.290. The version that prompted this page states the failure and the fix together: "Fixed writes through a symlinked path being judged by their in-tree spelling: the prompt names where the write lands, and `acceptEdits`, allow rules and auto mode no longer approve one landing outside" ([2.1.280](https://code.claude.com/docs/en/changelog#2-1-280)).

The remedy was already on record 151 releases earlier. Version 2.1.89 fixed "`Edit(//path/**)` and `Read(//path/**)` allow rules to check the resolved symlink target, not just the requested path" ([2.1.89](https://code.claude.com/docs/en/changelog#2-1-89)). The class recurred anyway, at each surface that takes a path, including worktree creation that followed "a repository-committed symlink at `.claude/worktrees`, which could create files outside the repository" ([2.1.212](https://code.claude.com/docs/en/changelog#2-1-212)). A repo-committed link is the ordinary case, with no adversary in it.

Resolving only the request leaves half the gap, because the rule is written in one of the two languages too. Version 2.1.268 covers both directions at once: "deny and ask permission rules on symlinked directories (`/etc`, `/tmp`, `/var` on macOS; `/bin` on Linux) not applying when a path was given by its real location, and Bash commands ignoring deny rules written on a symlinked path spelling" ([2.1.268](https://code.claude.com/docs/en/changelog#2-1-268)).

## Why it works

A path glob is a predicate over names. The kernel's path walk is a function from a name to a file, computed through a directory tree that two names can share and that changes under you. A guard matching names and a filesystem opening them therefore compute different functions of one string. Glob precision cannot close a gap that belongs to the two domains rather than to the pattern. Resolving the request first puts the matcher in the filesystem's domain, and that is the whole mechanism. It narrows rather than closes, because a resolved path is still a name.

MITRE has carried the class since long before agents. CWE-59 covers a product that "attempts to access a file based on the filename, but it does not properly prevent that filename from identifying a link or shortcut that resolves to an unintended resource" ([CWE-59](https://cwe.mitre.org/data/definitions/59.html)), with cited CVEs from 1999.

## When this backfires

- Containment already bounds the process. A jail that leaves only the checkout writable makes the destination absent from the namespace, so resolving inside the matcher changes no outcome. CWE-59's one listed mitigation is Separation of Privilege, not canonicalization: "Denying access to a file can prevent an attacker from replacing that file with a link to a sensitive file" ([CWE-59](https://cwe.mitre.org/data/definitions/59.html)).
- The target is a hard link or a device, where there is nothing to follow. Refusal is the move left, and 2.1.211 took it in file upload validation, where "files with multiple hard links are refused" ([2.1.211](https://code.claude.com/docs/en/changelog#2-1-211)). Version 2.1.285 had to fix "an approved Edit never going through when its target is a device, such as a file symlinked to /dev/null, and the approval came from the IDE diff view or changed the edit" ([2.1.285](https://code.claude.com/docs/en/changelog#2-1-285)).
- Resolution is not atomic with the open, so a resolved verdict is a snapshot. Version 2.1.251 fixed "file tools (Read, Write, Edit) following a symlink swapped inside the working directory after the permission check, which could read or write outside the approved location" ([2.1.251](https://code.claude.com/docs/en/changelog#2-1-251)).
- Your users legitimately reach one file under two names, and a resolution-aware check refuses them. One error string, `symlink resolution changed after permission was checked`, appears in two separate bug fixes: on macOS it refused "a dragged-in screenshot, or any file the system reports under a second path" ([2.1.273](https://code.claude.com/docs/en/changelog#2-1-273)), and on Windows it left Read, Write and Edit "refusing every file" inside an AppContainer or restricted-token sandbox ([2.1.265](https://code.claude.com/docs/en/changelog#2-1-265)).
- Budget for a revert. A tightening for Cygwin-style symlinks shipped in 2.1.232 and was withdrawn one release later ([2.1.233](https://code.claude.com/docs/en/changelog#2-1-233)).

## Example

This repository's hooks answer the question three different ways.

Resolving: `.claude/hooks/block-secret-reads.py` matches its credential globs against `Path(raw).expanduser()` and `literal.resolve()`. Its docstring gives the reason. A symlink whose name looks innocent but points at a guarded file is still blocked, because both the literal path and its realpath are matched.

Resolving, then answering a different question: `.claude/hooks/preload-rules-on-write.py` computes `target.resolve().relative_to(root)` and returns 0 when that raises, so a path resolving outside the repository root means no action. Correct for a convenience hook, and the defect in a deny gate.

Matching the spelling: a third hook in the same directory tests its globs against the raw path, `os.path.expanduser(raw)` and `os.path.abspath(os.path.expanduser(raw))`. That is the pair to look for in your own guards, because `os.path.abspath` normalizes text while `os.path.realpath` resolves links, and the two read almost identically in a diff.

Nothing has gone wrong here yet. `git ls-files -s` reports no tracked symlinks and no `worktree.symlinkDirectories` is set, so none of the three hooks has a link to disagree about. That is also the state this defect sits in right up to the commit that adds one.

## Key Takeaways

- Go through your guards and sort them by which function they call. A text normalizer such as `os.path.abspath` and a resolver such as `os.path.realpath` look alike in a diff and answer different questions.
- Resolve the rule as well as the request. A deny entry written on a link's spelling and a request written on the real location miss each other. Doing only one side is the common half-fix.
- Count the approval prompt as a consumer of the same decision. It is listed beside `acceptEdits` and the allow rules in the 2.1.280 entry. A prompt that names the spelling leaves a human approving a file that is not the one written.
- Expect to re-apply the fix at every new surface that takes a path, rather than once. The remedy was on record from 2.1.89 and the class still produced entries 161 releases later.
- Where a sandbox already makes the destination unreachable, spend the effort there instead. Resolution in the matcher is a narrowing, and it is the weaker of the two moves.

## Related

- [Parser-Versus-Shell Evasion in Command Permission Checks](../../security/parser-versus-shell-permission-evasion.md) — the sibling gap, where several shell grammars respell one command; this page is what remains when the grammars agree and the names still do not
- [Scoped-Looking Permission Grants](scoped-looking-permission-grants.md) — a rule that matches correctly and permits everything, where this one matches correctly and permits the wrong file
- [Parameter-Level Permission Rules (Tool(param:value) Syntax)](../../tools/claude/tool-param-value-permission-rules.md) — matching on an argument value, the layer that has to choose between a spelling and a destination
- [Blast Radius Containment: Least Privilege for AI Agents](../../security/blast-radius-containment.md) — the compartmentalization CWE-59 recommends over better path matching
- [MCP Allowlist by Label, Not by Identity (serverName Trap)](mcp-allowlist-label-vs-identity.md) — the same substitution one layer up, where the string the policy matches is a label the user picks
- [Treating a Worktree as a Safety Boundary](worktree-as-safety-boundary.md) — worktree scoping as placement rather than reach, which is the guard 2.1.212 found following a committed link
