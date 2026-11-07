---
title: "Fail Closed When the Sandbox Cannot Start"
term: "Fail-Closed Sandbox Startup"
description: "Require Claude Code's sandbox to start before relying on containment. Distinguish startup failure, later command refusal, and commands excluded from isolation."
aliases:
  - sandbox failIfUnavailable
  - enabled but unavailable sandbox
  - unsandboxed fallback refusal
tags:
  - security
  - sandboxing
  - agent-design
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-06
maturity: emerging
status: current
---

# Fail Closed When the Sandbox Cannot Start

> Fail-closed sandbox startup exits Claude Code when its sandbox cannot start; later initialization failures refuse sandboxed commands.

An enabled sandbox can still fail to start. With `sandbox.enabled: true`, Claude Code defaults to unsandboxed commands if the platform or dependency check prevents startup. Set `sandbox.failIfUnavailable: true` when the deployment requires that boundary ([settings reference](https://code.claude.com/docs/en/settings-reference#sandbox-failifunavailable)).

The failure mode matches the concern in MITRE's CWE-455: failed security initialization can leave a product less secure than its administrator intends. The operational test is therefore whether the boundary actually starts, not whether configuration requests it ([CWE-455](https://cwe.mitre.org/data/definitions/455.html)).

## Refusal depends on failure timing

With `failIfUnavailable` enabled, a failed startup check exits Claude Code. A later initialization failure leaves the session alive but refuses sandboxed commands ([settings reference](https://code.claude.com/docs/en/settings-reference#sandbox-failifunavailable)).

After startup, the documented errors distinguish failed initialization from a dependency that disappears on Linux or WSL2. Both begin with `Sandbox is required`. The command cannot retry with `dangerouslyDisableSandbox` while that refusal applies ([sandbox troubleshooting](https://code.claude.com/docs/en/sandboxing#commands-refused-with-sandbox-is-required)).

## Commands that remain outside the boundary

Excluded commands keep running outside the sandbox. Writes to `filesystem.allowWrite` paths outside the working directory use regular permission checks. Typed `!` commands also remain outside, except background sessions refuse them. On Linux with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`, the refusal includes excluded and typed commands ([documented exceptions](https://code.claude.com/docs/en/sandboxing#commands-refused-with-sandbox-is-required)).

Version 2.1.309 changed excluded-command writes while the enabled sandbox cannot run. Its release note describes permission checks for write-list paths and refusal of the unsandboxed fallback. It does not establish an unconditional guarantee for every command or configuration ([changelog](https://code.claude.com/docs/en/changelog#2-1-309)).

## Availability cost

Failing closed turns an unavailable boundary into unavailable work. Unsupported platforms cannot start Claude Code with the required sandbox enabled ([settings reference](https://code.claude.com/docs/en/settings-reference#sandbox-failifunavailable)). Validate deployment images before requiring it across a fleet.

MITRE's CWE-636 describes the opposing pressure: teams preserve functionality to reduce support costs when security controls fail. The trade depends on whether continued work without that control is acceptable. ([CWE-636](https://cwe.mitre.org/data/definitions/636.html)).

## Example

Enable the required sandbox in settings ([configuration reference](https://code.claude.com/docs/en/settings-reference#sandbox-failifunavailable)):

```json
{"sandbox": {"enabled": true, "failIfUnavailable": true}}
```

Ask Claude to run the vendor's probe; typing it through `!` usually tests an unsandboxed path:

```bash
touch ~/sandbox-probe
```

The test expects a denied write when the home directory is outside the sandbox's writable paths. Decline an unsandboxed retry. If the write succeeds and your home directory is not a sandbox write path, delete `~/sandbox-probe`. Then run `/sandbox` to check that the sandbox is on and its dependencies are installed ([sandbox verification](https://code.claude.com/docs/en/sandboxing#confirm-commands-run-inside-the-sandbox)).

## Key Takeaways

- Check both startup failure and refusal after startup before depending on the boundary.
- Review excluded and typed commands separately from commands the required sandbox refuses.
- Check the probe path's permissions before interpreting its result.

## Related

- [Declaring a Per-Hook Failure Mode for Agent Policy Gates](per-hook-failure-mode.md) — the same third-outcome question asked of a hook, where the harness default is also to let the action through
- [Fail-Closed Remote Settings Enforcement for Enterprise Agents](fail-closed-remote-settings-enforcement.md) — the startup-window version for managed policy that is stale or missing
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — why a runtime-evaluated control is the one worth checking the failure mode of
- [Dual-Boundary Sandboxing: Filesystem and Network Isolation](dual-boundary-sandboxing.md) — what the boundary covers while it is running
- [Sandbox Capability Opt-In as a Compatibility Setting](../patterns/anti-patterns/sandbox-capability-opt-in-as-compatibility-setting.md) — the adjacent case where a compatibility key weakens a sandbox that does start
