---
title: "System Prompt Delivery Channels on Shared Runners"
term: "System Prompt Delivery Channel"
description: "Argv is readable by any user and the environment block is not, but both are open to a co-tenant job running as the same user, which is the reader GitHub's own leak example describes."
aliases:
  - prompt delivery channel
  - system prompt argv exposure
  - keeping the prompt out of the process table
tags:
  - security
  - instructions
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-09-24
maturity: adopted
status: current
---

# System Prompt Delivery Channels on Shared Runners

> Moving an agent's system prompt out of argv closes the process-table channel only when the reader runs under a different user.

Check for a user boundary before you change how the prompt reaches the process. The channel matters when the neighbor that could read it runs as a different UID or inside its own namespace. Where the neighbor shares your UID, argv, the environment block, and a mode-0600 file all read alike.

GitHub states the exposure in its own security reference: "Some jobs will use secrets as command-line arguments which can be seen by another job running on the same runner, such as `ps x -w`. This can lead to secret leaks" ([Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)). Look at the example command. "By default, ps selects all processes with the same effective user ID (euid=EUID) as the current user", and `x` only lifts the BSD-style "must have a tty" restriction ([ps(1)](https://man7.org/linux/man-pages/man1/ps.1.html)). The reader GitHub describes is a same-user neighbor.

## What each channel exposes

| Channel | A different user can read it | The same user can read it | Lifetime |
|---|---|---|---|
| Command line (`--system-prompt "…"`) | Yes, by default | Yes | Until the process exits |
| Environment variable | Only with `CAP_SYS_PTRACE` | Yes | Until the process exits |
| File passed by path (`--system-prompt-file`) | Only if the mode allows | Yes | Until something deletes it |

The environment row gets read wrong in both directions. It is not equivalent to argv, and it is not a boundary against a co-tenant job either. GitHub lists cross-job environment reads in the same breath as shared directories: "a job querying the environment variables used by a later job, writing files to a shared directory that a later job processes" ([Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)).

## Why it works

Linux publishes a process's arguments and its environment through two procfs entries, and only one of them is gated. Under the default `hidepid=0` mount, "Everybody may access all /proc/pid directories" ([proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)), which is where argv lives. The manual page for `/proc/pid/environ` adds a gate the [cmdline page](https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html) does not: "Permission to access this file is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check" ([proc_pid_environ(5)](https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html)).

That check compares credentials. It allows the read when "The real, effective, and saved-set user IDs of the target match the caller's user ID, and the real, effective, and saved-set group IDs of the target match the caller's group ID", or when "The caller has the CAP_SYS_PTRACE capability in the user namespace of the target" ([ptrace(2)](https://man7.org/linux/man-pages/man2/ptrace.2.html)). The gap between argv and every other channel is a credential gap, so changing channel changes who can read the prompt only across a UID boundary.

A runner operator can close argv at that same boundary without touching the harness. Mounting procfs with `hidepid=1` means "Sensitive files such as /proc/pid/cmdline and /proc/pid/status are now protected against other users" ([proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)).

## What Claude Code changed, and what it did not

Claude Code 2.1.281, released 23 September 2026, "Changed self-hosted runners to pass system prompts to Claude Code as private files instead of command-line text, so large prompts no longer fail the launch". It also names the migration: "a wrapper or `command` hook that appends `--system-prompt` or `--append-system-prompt` must switch to `--system-prompt-file` or `--append-system-prompt-file`" ([changelog 2.1.281](https://code.claude.com/docs/en/changelog#2-1-281)).

Read that reason literally. It is an argument-length limit, and the same rationale sits on the file flags themselves: `--append-subagent-system-prompt-file` is "An alternative to `--append-subagent-system-prompt` for text too long to pass on the command line" ([CLI reference](https://code.claude.com/docs/en/cli-reference)). The changelog calls the files private and names no mode, so the confidentiality benefit is yours to verify.

## How to check your own setup

Start the agent, then read the process table from the account a neighboring job would use:

```bash
tr '\0' '\n' < /proc/$(pgrep -n claude)/cmdline
```

If the prompt text appears there, argv is your delivery channel whatever the wrapper intended. Check the file's mode and directory next. A prompt written with the default umask into the checkout is a worse artifact than the argv entry it replaced.

## When this backfires

- Jobs share a UID. The `ps x -w` reader is the same user, passes the ptrace check on `/proc/pid/environ`, and opens a mode-0600 file owned by that UID. The channel change buys nothing, and `hidepid` does not help either.
- The file outlives the run. Argv disappears when the process exits. A prompt file sits in the workspace until something removes it, and a later job on the same runner reads it out of the shared directory.
- The runner is single-tenant and ephemeral. There is no neighbor, so you have taken on a temp-file lifecycle and one more way to leave the prompt on disk.
- The wrapper still echoes the text. A `command` hook that logs its own invocation, or a `set -x` in the calling script, writes the prompt into a log that outlives both channels.
- The prompt holds a credential. Then the delivery channel is the smaller defect, because a prompt is recoverable through the model as well as through the kernel. [The underlying rule](system-prompt-not-a-secret-store.md) applies first.

The durable fix is one job per machine, and GitHub recommends that rather than a channel. Destroying a runner after each job is only a partial mitigation, because "there is no way to guarantee that a self-hosted runner only runs one job". Just-in-time runners are the answer the same page gives: they "perform at most one job before being automatically removed from the repository, organization, or enterprise" ([Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)).

## Key Takeaways

- Establish the UID or namespace boundary first, then pick the channel. Without one, the channel is not the control you have.
- GitHub's own leak example is `ps x -w`, a same-user listing, so the documented CI case is the one a channel change does not fix.
- A prompt file trades a process-lifetime exposure for a filesystem one. Own its mode, its directory, and its deletion, or the problem just lasts longer.
- The changelog's stated reason for moving runners to prompt files was launch failure on large prompts. Confidentiality is a side effect you verify, not a guarantee it makes.
- Migrate wrappers before upgrading. A `command` hook appending `--system-prompt` or `--append-system-prompt` has to switch to the `-file` form.

## Related

- [System Prompt as Secret Store (OWASP LLM07)](system-prompt-not-a-secret-store.md) — the other channel the same prompt leaks through, recoverable from the model rather than from the kernel
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — the affirmative rule for credentials, and why the environment row above is not the end of the answer
- [Protecting Sensitive Files from Agent Context Access](protecting-sensitive-files.md) — the sibling problem once the prompt lives in a file the agent can also read
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md) — the namespace boundary that hides the process table when a UID boundary is unavailable
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) — filesystem and network isolation, the two boundaries a shared runner usually lacks
