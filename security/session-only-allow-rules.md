---
title: "Session-Only Allow Rules for Secret-Shaped and Tracked-File Grants"
term: "Session-Only Allow Rule"
description: "Since Claude Code 2.1.323, a \"don't ask again\" allow rule that looks like it holds a secret, or would land in a git-tracked settings.local.json, lasts one session. It is a backstop, not a review."
aliases:
  - session-scoped allow rule
  - non-persisted don't ask again rule
  - secret-shaped permission rule
tags:
  - security
  - claude
  - human-factors
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-20
status: current
maturity: emerging
---

# Session-Only Allow Rules for Secret-Shaped and Tracked-File Grants

> A session-only allow rule keeps a "don't ask again" grant for one session, unsaved, when the rule looks secret-bearing or its file is git-tracked.

Claude Code 2.1.323, released November 12, 2026, keeps two kinds of "don't ask again" approval off disk. The changelog entry reads: "Changed “don’t ask again” so an allow rule that looks like it holds a secret, or would be saved to a `settings.local.json` that git tracks, lasts for the session only and isn’t saved" ([changelog 2.1.323](https://code.claude.com/docs/en/changelog#2-1-323)).

Two conditions trigger it, and they protect against different leaks. The secret test stops a credential reaching a plaintext file. The tracked-file test stops a personal grant reaching every clone. Neither condition reviews the rules a repository already holds.

## What a saved approval normally does

Claude Code saves a Bash or WebFetch approval "to `.claude/settings.local.json` at the root of the git repository". The docs add: "The rule applies to future sessions anywhere in that repository, including sessions started in subdirectories and in worktrees" ([permissions](https://code.claude.com/docs/en/permissions#permission-system)). Bash rules persist "per repository and command" and WebFetch rules "per repository and domain". A file-edit approval already lasted only until the session ended.

Claude Code keeps the local file out of git when it writes the file. On its first write in a repository that does not already ignore the file, Claude Code "adds `**/.claude/settings.local.json` to your global git excludes file". A file you created by hand gets no such entry: "add it to `.gitignore` yourself" ([settings](https://code.claude.com/docs/en/settings#keep-personal-settings-out-of-a-repository)). A hand-made file that nobody added to `.gitignore` is one way a personal grant ends up tracked.

## Why it works

A saved allow rule is a standing grant written as plaintext. If the rule text holds a token, the file holds the token. If git tracks the file, every clone receives the token and the grant together. A rule that lasts for the session only is never written, so neither copy exists.

The tracked case matches how Claude Code already reads such a file. "When the file is tracked in git, or `.claude` is a symlink, Claude Code treats it as repository-supplied instead and holds its rules until you trust the folder" ([permissions](https://code.claude.com/docs/en/permissions#project-allow-rules-and-workspace-trust)). A rule saved there is no longer personal, so writing it there was the wrong home from the start.

A leak also outlives its fix. GitGuardian reports that "70% of secrets leaked in 2022 remain active today", and that "35% of customers' private repositories contain plaintext secrets" ([GitGuardian 2025](https://blog.gitguardian.com/the-state-of-secrets-sprawl-2025/)). A private repository does not make a committed token safe.

## When this backfires

- The secret test is undocumented. The changelog says "looks like it holds a secret" and neither the [permissions](https://code.claude.com/docs/en/permissions) nor the [settings](https://code.claude.com/docs/en/settings) page names the patterns. A token in a format the check misses still saves. Keep reading saved rules yourself.
- Existing rules stay. The entry changes what "don't ask again" saves. It says nothing about rules saved before 2.1.323, so a tracked file keeps every grant it held.
- Prompts come back each session. Anthropic reports that users "accept 93% of" manual prompts and that prompt volume "leads to approval fatigue, where people stop paying close attention to what they're approving" ([auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)). A daily command with an inline token now prompts daily, and each repeat is another chance for that fatigue to set in on the command you most need to read.

Take the token out of the command. A command that reads the token from an environment variable has no token in its text, so whether its rule saves or not, the file has nothing to leak.

## Review the allow rules a repository holds

Run these once per repository, then after any change to `.claude/`:

1. Open `/permissions`. "The dialog lists all permission rules and the `settings.json` file each rule comes from" ([permissions](https://code.claude.com/docs/en/permissions#manage-permissions)). Read every allow rule for an embedded token, key, or password.
2. Run `git ls-files .claude/settings.local.json`. Any output means git tracks the file. Remove it from the index with `git rm --cached`, and add it to `.gitignore`.
3. Rotate any secret you find in a rule. The GitGuardian report's advice for private repositories applies: "Leaked secrets in private repositories must be treated as compromised" ([GitGuardian 2025](https://blog.gitguardian.com/the-state-of-secrets-sprawl-2025/)).
4. Rewrite the command to read the secret from the environment, then approve the rewritten form.

## Key Takeaways

- Since 2.1.323, a rule saved from a prompt can vanish at session end. A prompt that keeps coming back for one command is the signal to look for a token in it.
- `git ls-files .claude/settings.local.json` printing a path means your grants travel with the repository, and from 2.1.323 your new approvals stop saving there.
- The change covers new saves only. Audit old rules in `/permissions` and rotate any secret you find.
- Moving the secret into an environment variable keeps it out of every rule, saved or not.

## Related

- [One-Shot Permission Answers for Out-of-Directory Reads](../patterns/agent-design/one-shot-permission-answers.md) — another answer that saves no rule, chosen by the user instead of the harness
- [Scope Demotion for Repository-Committed Settings](repo-committed-settings-scope-demotion.md) — what a committed settings file may not grant
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md) — deny rules that keep credential files out of reach
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — getting tokens into a session without putting them in commands
- [Transcript-Driven Permission Allowlist](transcript-driven-permission-allowlist.md) — building the allowlist deliberately rather than prompt by prompt
