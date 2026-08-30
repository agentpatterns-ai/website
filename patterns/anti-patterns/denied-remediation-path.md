---
title: "Permission Gates That Deny the Agent's Own Cleanup (Denied Remediation Path)"
term: "Denied Remediation Path"
description: "A permission classifier scores commands by destructive surface, so it can allow a compromise and then block the agent's attempt to undo it."
tags:
  - anti-pattern
  - security
  - agent-design
  - claude
aliases:
  - denied remediation path
  - classifier blocks agent cleanup
  - safety gate denies incident recovery
last_reviewed: 2026-08-29
maturity: emerging
---

# Permission Gates That Deny the Agent's Own Cleanup (Denied Remediation Path)

> A permission classifier scores each command by its destructive surface, so it can allow a compromise and then deny the agent's cleanup.

Plan incident recovery to run outside the agent, because the gate that permitted the damage can refuse the command that undoes it. Johann Rehberger demonstrated this against Claude Code's auto mode: "In a few runs Claude tried to terminate the malware process once it noticed the compromise, but Auto Mode denied the cleanup command" ([Breaking Claude Code Opus 5 Auto Mode](https://embracethered.com/blog/posts/2026/breaking-claude-code-opus-5-and-automode/)). His summary of the shape: "The classifier allowed the creation of the malware process, but then it blocked the command intended to stop it."

## When this costs you something

Only on a runtime you cannot discard. In a container or VM you delete the container and the question never arises. The denial bites on a developer workstation with the agent's home directory, SSH keys, and cloud credentials in reach. Anthropic closed Rehberger's report as Informative and working as designed. He summarizes their position as auto mode being "a convenience feature backed by a best-effort classifier, not a security guarantee". The real boundary they name is OS isolation and network egress control.

## Why it works

The classifier judges the action, and the evidence that would justify it is withheld by design. Auto mode routes tool calls "through a classifier that blocks anything irreversible, destructive, or aimed outside your environment" ([Configure auto mode](https://code.claude.com/docs/en/auto-mode-config)), so a `kill` scores on that axis alone. Detection lives in tool results, and the classifier "never receives tool results themselves" ([Hooks reference](https://code.claude.com/docs/en/hooks)). That is the same reasoning-blinding that stops a hostile web page arguing the gate down. The agent cannot supply the missing authority either: only the user's own message clears a soft block, and "General requests don't count as explicit intent" ([Configure auto mode](https://code.claude.com/docs/en/auto-mode-config)).

Scoring is a single number per action. A mitmproxy capture of a live verdict shows `<severity>78</severity>` against a threshold where "Ratings over 50 are blocked" ([Prompt Injection Experiments with Opus-5 in Claude Code](https://itmeetsot.eu/posts/2026-08-12-opus5_automode/)). Nothing in that number tracks whether the command restores a safe state. Retrying makes it worse: one user recorded the classifier scoring a good-faith correction as `[Auto-Mode Bypass] ... a bad-faith tunneling attempt around a just-issued block with no new user authorization` ([anthropics/claude-code #75325](https://github.com/anthropics/claude-code/issues/75325)).

## When this backfires

The obvious fix is the dangerous one. An agent that has just executed attacker-supplied code is an untrusted principal, and an agent reporting that it found malware is exactly what an injected agent would report. Widening the gate to admit remediation hands that agent process control and file deletion at the moment of maximum suspicion. `autoMode.allow` entries are also "additive, not a hard policy boundary" ([Configure auto mode](https://code.claude.com/docs/en/auto-mode-config)). Read that way the denial was a true positive, and the defect is the earlier false negative that let the malware run.

Hardening in the other direction misfires too. A `permissions.deny` rule on process termination is stricter than the classifier without being safer, because deny "blocks the action before the classifier is consulted and can't be overridden."

Do not overstate what the blocked command was worth. Rehberger's payload had already established a C2 callback, "The detached process can outlive the Claude conversation", and one variant wrote files outside the workspace. He observed the denial in a few runs of 5-trial variants, so treat it as a documented failure mode rather than a measured frequency.

## What to do instead

Decide the recovery path before the incident and keep it off the agent's tool surface. Terminate the process from a second terminal or from the host. Where you want the agent's evidence to reach the gate, a `PostToolUse` hook can return `classifierContext`, the supported channel for telling the classifier what a call returned. It needs Claude Code v2.1.236 or later and caps the notes for one tool call at 2,000 characters. The classifier reads it as unverified application context, and the note "never establishes user intent" ([Hooks reference](https://code.claude.com/docs/en/hooks)). Wire a `PermissionDenied` hook so a denial during an incident reaches a human instead of a scrollback buffer.

## Key Takeaways

- A classifier that scores each command by destructive surface reads a `kill` and an attack the same way; direction is not one of its inputs.
- Do not file this as a classifier bug. Reasoning-blinding is the property you are paying for, so the fix belongs in the recovery path rather than in the gate.
- Making the gate remediation-aware would be the worse bug, because an agent claiming to have detected an attack is trivially injectable.
- Audit which of your agent runtimes are disposable. On the ones that are not, the classifier's incident behavior is part of your threat model.
- Pre-declare the recovery path: out-of-band process control, `classifierContext` from a `PostToolUse` hook, and a `PermissionDenied` alert. Nothing can be negotiated with the classifier mid-incident.

## Related

- [Classifier-Gated Auto-Permission for Cloud-IDE Coding Agents](../agent-design/classifier-gated-auto-permission.md) — the pattern this page is the failure edge of; it treats classifier error as a false-negative rate rather than a false positive on the recovery path
- [Permission Modes as a Defense Against a Tampered Response Path (Response-Path Control Gap)](response-path-control-gap.md) — the other way in-agent permission logic stops being the control you assumed it was
- [Single-Layer Prompt Injection Defense Anti-Pattern](single-layer-injection-defence.md) — why one classifier is a layer and never the boundary
- [Defense in Depth for Agent Safety](../../security/defense-in-depth-agent-safety.md) — the OS isolation and egress layers that carry the boundary a best-effort classifier does not
- [Enforced Versus Advisory Controls](../../security/enforced-versus-advisory-controls.md) — the difference between a gate that holds and one that is best-effort by design
