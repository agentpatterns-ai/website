---
tags:
  - security
  - claude
description: "Add PID namespace isolation and env var scrubbing to Bash subprocesses in Claude Code, preventing daemon persistence and secret leakage beyond the session."
---

# Subprocess PID Namespace Sandboxing in Claude Code

> A third isolation layer — separate from filesystem and network sandboxing — that prevents Bash subprocesses from escaping the agent's execution context through process-level tricks.

## What This Adds

[Dual-boundary sandboxing](dual-boundary-sandboxing.md) restricts what the agent can read, write, and reach over the network. It does not constrain the *process tree* a Bash invocation can produce. A subprocess can still:

- Spawn background daemons that outlive the session
- Persist processes after the agent exits
- Inherit sensitive environment variables (API keys, tokens) from the parent environment

Claude Code 2.1.98 (April 9, 2026) addressed this with [subprocess sandboxing using PID namespace isolation on Linux](https://code.claude.com/docs/en/changelog), controlled by two environment variables.

## The Two Controls

### `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`

Setting this variable activates subprocess sandboxing. When set, Claude Code:

1. Launches Bash subprocesses inside a Linux PID namespace
2. Strips sensitive environment variables from the subprocess environment before execution

PID namespace isolation confines the subprocess's view of the process tree: it cannot see or signal processes outside its namespace, and its child processes are reaped when the namespace exits [unverified: Claude Code's exact implementation detail; the reaping behavior is a standard Linux PID namespace property]. Background daemons spawned inside the namespace cannot persist after the session ends.

Env var scrubbing prevents secrets in the parent environment from leaking into child process environments — a common vector when a subprocess calls out to a tool that logs its environment, dumps it on error, or passes it through to a further child.

### `CLAUDE_CODE_SCRIPT_CAPS`

Sets a per-session ceiling on the number of script invocations. Without a cap, a runaway agent or injected payload can drive resource exhaustion by invoking scripts in a tight loop. `CLAUDE_CODE_SCRIPT_CAPS` enforces a hard limit so that loop terminates before it degrades the host.

## Linux-Only Constraint

PID namespace isolation is a Linux kernel primitive. This feature does not apply on macOS or Windows. On those platforms, the filesystem and network boundaries from the standard sandbox remain the primary isolation mechanisms.

For production agent deployments on Linux, all three layers should be configured together:

| Layer | Mechanism | What it prevents |
|-------|-----------|-----------------|
| Filesystem | bubblewrap bind mounts | Writes outside working directory |
| Network | bubblewrap network namespace + proxy | Unauthorized outbound connections |
| Subprocess | PID namespace + env scrub | Daemon persistence, env var leakage |

## Configuration

Both variables are set in the process environment that launches Claude Code, not in `settings.json`:

```bash
export CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1
export CLAUDE_CODE_SCRIPT_CAPS=50   # adjust per workload
claude --dangerously-skip-permissions
```

`CLAUDE_CODE_SCRIPT_CAPS` takes an integer. The right value depends on the workload — a build agent that runs many test invocations needs a higher cap than a read-only analysis agent.

## Relationship to the Existing Sandbox

These controls augment the built-in `/sandbox` command; they do not replace it. The existing sandbox (enabled via `/sandbox` or `sandbox.enabled` in settings) enforces filesystem and network boundaries using bubblewrap. Subprocess PID sandboxing adds process-level isolation on top.

Enabling `/sandbox` without `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` still provides filesystem and network isolation. Adding `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` closes the process persistence and env leakage gaps that bubblewrap's filesystem/network controls leave open.

## Key Takeaways

- PID namespace isolation prevents subprocess daemons from persisting beyond the session; it is Linux-only
- `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` activates both PID namespace isolation and env var scrubbing for Bash subprocesses
- `CLAUDE_CODE_SCRIPT_CAPS` sets a per-session script invocation limit to prevent resource exhaustion loops
- All three isolation layers (filesystem, network, subprocess) should be configured together for production Linux deployments

## Related

- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
