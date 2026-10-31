---
title: "Permission Policy Binds Only at an Enforcement Point"
term: "Enforcement-Point Prerequisite"
description: "VS Code 1.142 requires the Copilot harness in Agent Host once an organization sets a nonempty permissions object, and moves an existing Local chat there on open."
tags:
  - agent-design
  - security
  - pattern
  - copilot
aliases:
  - harness prerequisite for permission policy
  - policy-managed chat migration
  - enforcement point for agent permissions
last_reviewed: 2026-10-19
maturity: emerging
---

# Permission Policy Binds Only at an Enforcement Point

> A permission policy binds only where a component intercepts the call, so VS Code 1.142 relocates policy-managed chats to an enforcing harness.

Visual Studio Code 1.142 routes policy-managed chats to an enforcing harness. The trigger and opt-out below determine which sessions move ([release notes](https://code.visualstudio.com/updates/v1_142)).

## The conditions that arm the requirement

Two managed settings arm it. When an organization configures a nonempty `permissions` object or sets `sandbox.enabled` to `true`, VS Code "requires the Copilot harness in Agent Host for full chat sessions, to be able to enforce these policies" ([Visual Studio Code 1.142 release notes](https://code.visualstudio.com/updates/v1_142)).

"An empty `permissions` object or legacy policy alone does not trigger this migration," and the requirement covers full chat sessions rather than every surface, since editor inline chat "remains available for limited read and edit tasks." ([1.142 release notes](https://code.visualstudio.com/updates/v1_142)).

An administrator can "permit Assisted while blocking Allow All, giving developers assisted approvals without bypassing permission checks" ([1.142 release notes](https://code.visualstudio.com/updates/v1_142)).

## What the relocation does

Opening an existing, unarchived Local chat moves it to Copilot, "preserving the transcript and unsent draft, including attachments," and "Nothing is sent automatically." VS Code "archives the original chat only after the new chat opens successfully." ([1.142 release notes](https://code.visualstudio.com/updates/v1_142)).

While the policies apply, "Claude, Codex, and terminal chat are unavailable." ([1.142 release notes](https://code.visualstudio.com/updates/v1_142)). Windows sandboxing for terminal commands in Local agent sessions is deprecated, and sandboxed execution on Windows now needs an Agent Host session ([1.142 release notes](https://code.visualstudio.com/updates/v1_142)). The Local harness "sandboxes terminal commands on macOS and Linux only" ([agent sandboxing documentation](https://code.visualstudio.com/docs/agents/run/agent-sandboxing)).

## Example

The managed-settings block that grants Assisted without Allow All, from the [1.142 release notes](https://code.visualstudio.com/updates/v1_142):

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "disableAssistedPermissionsMode": false
  }
}
```

A nonempty `permissions` object is the trigger, so this block also arms the harness requirement. The documented way to defer it:

```json
{
  "vscode": {
    "temporaryDefaultToLocalHarness": true
  }
}
```

Set the second block and the first stops binding on every session that stays Local. The opt-out "also overrides routing required by managed sandbox and permission settings. Local does not enforce those runtime-only rules." The same note adds that "Enforcement in Copilot Agent Host sessions is unchanged." ([1.142 release notes](https://code.visualstudio.com/updates/v1_142)).

## Why it works

Seven of the twelve agentic-red-team systems one study evaluated shipped a guardrail, and all seven enforced it only at the orchestration layer, so "only the high-level decisions produced by the LLM are validated against the policy, while the actual behavior of the underlying execution infrastructure remains completely unchecked" ([arXiv:2606.24496v2](https://arxiv.org/abs/2606.24496v2)). The authors report unbounded weaponization across all tested agents and attribute it to the level at which the policies are enforced.

Boundary-Bench shows the working form. It realizes each restriction as "a native Linux access-control mechanism rather than requested of the agent," compiled "into the environment without the agent's knowledge," and reports that "Every restriction is inherited by each child process the agent spawns, so it cannot be evaded by launching a subprocess" ([arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)).

## Verify at the enforcement point

In a Copilot harness session, `/sandbox policy` reports whether sandboxing is active, and the documentation notes the command "isn't available in Local harness sessions." For Copilot harness sessions it directs readers to "use the effective sandbox policy report rather than inferring restrictions from another tool's behavior" ([agent sandboxing documentation](https://code.visualstudio.com/docs/agents/run/agent-sandboxing)).

Boundary-Bench does this mechanically. Its probe suite runs "once per sandbox before the agent starts" and "exercises every configured blockage," and a hardening step that cannot be established "fails closed rather than running unhardened" ([arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)).

## When this backfires

- The policy names a path the enforcer does not intercept. VS Code sandboxing "applies to terminal commands and their child processes," while built-in tools "that don't start operating system processes use their own permission checks." Server controls "don't cover servers you start independently" ([agent sandboxing documentation](https://code.visualstudio.com/docs/agents/run/agent-sandboxing)).
- `vscode.temporaryDefaultToLocalHarness` keeps Local available, and the release notes state it "also overrides routing required by managed sandbox and permission settings. Local does not enforce those runtime-only rules" ([1.142 release notes](https://code.visualstudio.com/updates/v1_142)). The note adds that "Enforcement in Copilot Agent Host sessions is unchanged."
- A default is mistaken for a restriction. `permissions.defaultMode` "supplies a starting default, not a restriction on the modes users can select," and the legacy `ChatToolsAutoApprove: false` policy "still blocks both Allow All and Assisted unless you configure explicit managed mode restrictions" ([1.142 release notes](https://code.visualstudio.com/updates/v1_142)).
- The relocation is treated as the whole answer. Managed sandbox enforcement "is in Preview," and the sandbox "is not a virtual machine or user-account boundary, and it does not replace endpoint security" ([agent sandboxing documentation](https://code.visualstudio.com/docs/agents/run/agent-sandboxing)). [arXiv:2606.24496v2](https://arxiv.org/abs/2606.24496v2) prescribes enforcement below the harness, at the OS level, preventing "the kernel from executing system calls that violate the policy at runtime".
- The cost is not budgeted. Hardening "is never free but far from uniform". Across 12 coding agents on Terminal-Bench 2.1 under Boundary-Bench's strictest policy, the largest success loss for any single model was 18.3 percentage points (Claude Sonnet 5) and the largest cost inflation 167.3% for a different model (Grok 4.5), per [arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1).

## Key Takeaways

- Before writing a fleet policy, name the component that will intercept each action it covers. If no component can, the policy is documentation.
- Treat a vendor's enforcement prerequisite as a scheduled change to your session topology. The 1.142 trigger relocates sessions and withdraws Claude, Codex, and terminal chat while it applies.
- An escape hatch that keeps the old harness available is an enforcement holiday for every session that takes it. Check what the opt-out does to the policy before planning around it.
- Grant each permission mode on its own. Independent controls mean a wrong default is a separate mistake from a wrong restriction.
- Make enforcement verifiable from inside the session. A policy report or a pre-flight probe turns "the policy is set" into "the policy is active."

## Related

- [Action-Class Permission Gates Leave Task Fit and Reversibility to the Human](action-class-permission-gates.md) — what a permission prompt names, and what the person answering it has to supply.
- [Continuation Authority in Agent Migration](continuation-authority-agent-migration.md) — the deployment boundary, not the checkpoint, holds the right to act after a move.
- [Deny-Fallback Permissions for Unattended Agent Runs](deny-fallback-unattended-permissions.md) — what the enforcement point should do when no human is there to answer.
- [Most-Restrictive-Wins Fusion for Parallel Agent Control Returns](most-restrictive-wins-fusion.md) — how parallel hook, classifier, and rule decisions merge into one answer.
- [Session Harness Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — why the session log, the harness loop, and the sandbox are replaceable separately.
