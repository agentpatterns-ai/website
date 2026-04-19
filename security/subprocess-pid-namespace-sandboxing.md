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

PID namespace isolation confines the subprocess's view of the process tree: it cannot see or signal processes outside its namespace, and all processes inside the namespace receive `SIGKILL` when its init process (PID 1) exits — a standard Linux kernel guarantee documented in [`pid_namespaces(7)`](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html). Background daemons spawned inside the namespace cannot persist after the session ends.

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

## Example

A CI pipeline running on a Linux host invokes Claude Code to perform automated code review. Without subprocess sandboxing, the agent's Bash tool can spawn long-running background processes — for example, a build daemon — that persist after the session ends, consuming resources and retaining access to environment-inherited secrets.

With subprocess sandboxing enabled:

```bash
export CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1
export CLAUDE_CODE_SCRIPT_CAPS=100   # sufficient for a typical review pipeline
claude --dangerously-skip-permissions --print "Review the diff and run the test suite"
```

The agent's Bash invocations run inside a PID namespace. Any background process started by the agent — intentionally or via prompt injection — is killed when the namespace's init exits at session end. `ANTHROPIC_API_KEY` and cloud provider credentials present in the CI environment are stripped from subprocesses before execution.

## When This Backfires

**Linux-only**: macOS and Windows deployments get no benefit from `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`. On those platforms the env scrubbing still applies, but PID namespace isolation is silently skipped — process persistence remains possible.

**Env scrubbing breaks tools that expect inherited credentials**: Some subprocess tools (e.g., AWS CLI, gcloud, GitHub CLI) rely on inheriting credentials from the environment. Scrubbing removes those variables, causing auth failures. Mitigation: pass credentials explicitly via config files, credential helpers, or application-default mechanisms rather than raw env vars.

**Misconfigured `CLAUDE_CODE_SCRIPT_CAPS` terminates valid workloads**: A cap set too low for the actual workload (e.g., `CLAUDE_CODE_SCRIPT_CAPS=10` for a build agent that runs 80 test shards) causes the session to abort mid-task. Calibrate the cap against the actual script invocation profile before deploying.

**Namespace isolation is not a substitute for network sandboxing**: A process inside a PID namespace can still make outbound network calls. Process-level isolation must be combined with bubblewrap network namespacing to prevent exfiltration.

## Key Takeaways

- PID namespace isolation prevents subprocess daemons from persisting beyond the session; it is Linux-only
- `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` activates both PID namespace isolation and env var scrubbing for Bash subprocesses
- `CLAUDE_CODE_SCRIPT_CAPS` sets a per-session script invocation limit to prevent resource exhaustion loops
- All three isolation layers (filesystem, network, subprocess) should be configured together for production Linux deployments

## Related

- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party](sandbox-rules-harness-tools.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party](sandbox-rules-harness-tools.md)
