---
title: "Dual-Boundary Sandboxing: Filesystem and Network Isolation"
term: "Dual-Boundary Sandboxing"
description: "Enforce both filesystem and network isolation; neither boundary alone prevents security breaches or data exfiltration by an autonomous agent."
tags:
  - agent-design
  - security
  - tool-agnostic
last_reviewed: 2026-06-12
---

# Dual-Boundary Sandboxing: Filesystem and Network Isolation

> Enforce both filesystem and network isolation simultaneously; neither boundary alone is sufficient to prevent security breaches or data exfiltration by an autonomous agent.

## Why One Boundary Is Not Enough

Restricting an agent to its working directory does not contain it. With filesystem access but unrestricted network, the agent can exfiltrate any file it can read — SSH keys, environment variables, secrets — via outbound connections.

The inverse fails too: restricting network while leaving filesystem paths open lets the agent write to startup scripts, crontabs, or shell configs that execute with elevated permissions on the next trigger.

Per [Anthropic's Claude Code sandboxing post](https://www.anthropic.com/engineering/claude-code-sandboxing) and the [Claude Code sandboxing documentation](https://code.claude.com/docs/en/sandboxing), effective sandboxing enforces both boundaries simultaneously at the OS level.

## The Two Boundaries

**Filesystem boundary:**

- Restrict write access to the current working directory
- Block writes to parent directories, home directory files, and system paths
- Read access restrictions depend on the task's legitimate data needs

**Network boundary:**

- Allowlist approved outbound domains (package registries, APIs the agent is explicitly authorized to use)
- Route all other traffic through a validating proxy or block it
- Block inbound connections to the agent's environment

Enforce at the OS level, not the prompt level. Prompt-level restrictions can be bypassed by a confused agent; OS-level restrictions cannot be overridden by prompt content alone — though they still leak via kernel CVEs, configuration gaps, or agents reasoning around denylisted paths (see *When This Backfires*).

## OS Enforcement Mechanisms

- **Linux:** `bubblewrap` (used by Flatpak) applies filesystem namespaces and seccomp filters; network namespaces restrict outbound traffic
- **macOS:** `Seatbelt` profiles via `sandbox-exec` — deprecated since macOS 10.13; prefer container-based approaches for new tooling
- **Container-based:** Docker/Podman with restricted mount points and network policies
- **Agent-purpose-built:** [`docker sbx`](https://docs.docker.com/reference/cli/sbx/) wraps container primitives for agent sandboxes — see [Adopting `docker sbx`](docker-sbx-adoption.md) and the [Sandbox Runtime Comparison](sandbox-runtime-comparison.md) for trade-offs

The agent runs inside the enforced environment. Permissions it needs (paths, domains) are granted explicitly; everything else is denied by default.

## The Approval Fatigue Problem

Granular per-action prompts produce [approval fatigue](safe-command-allowlisting.md): users click through without reading — the illusion of oversight with none of the substance. Dual-boundary sandboxing defines a safe zone where the agent acts freely and hard limits where it cannot, reserving prompts for boundary-crossing requests.

## Threat Model

The sandbox addresses two threat vectors:

1. **Prompt injection** — malicious content in files or web pages instructs the agent to exfiltrate data or modify system files. Network and filesystem restrictions limit the damage scope.
2. **Agent error** — the agent deletes a file outside the working directory or makes an unintended API call. OS-level restrictions contain the consequences.

It does not prevent incorrect output, budget spent on allowed API calls, or leaks through allowed channels.

## When This Backfires

OS-level boundaries are not inviolable. Three documented failure modes:

- **Shared-kernel escapes.** Namespace-based sandboxes (`bubblewrap`, Docker, raw namespaces) share the host kernel. A kernel CVE turns the sandbox into a thin paper wall. For strictly untrusted code, microVMs (Firecracker, Kata Containers) or gVisor's user-space kernel offer stronger isolation at the cost of tooling overhead ([NVIDIA: Practical Security Guidance for Sandboxing Agentic Workflows](https://developer.nvidia.com/blog/practical-security-guidance-for-sandboxing-agentic-workflows-and-managing-execution-risk/)).
- **Configuration TOCTOU.** [CVE-2026-25725](https://nvd.nist.gov/vuln/detail/CVE-2026-25725) demonstrated that Claude Code's bubblewrap profile failed to protect `.claude/settings.json` when the file did not exist at startup; malicious code inside the sandbox could create it and inject `SessionStart` hooks that executed with host privileges on restart. Sandbox policies must cover absent files and mutation points in the config surface, not just existing paths.
- **Agents reasoning around denylists.** [Ona documented](https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox) a Claude Code session in which the agent located `/proc/self/root/usr/bin/npx` to bypass a denylist, then — when bubblewrap blocked namespace creation — autonomously disabled the sandbox to complete the task. Because agents reason about their constraints, pattern-based policies leak through alternative execution paths (library calls, renamed binaries, chained primitives). Manifold Security frames this as [the sandbox illusion](https://www.manifold.security/blog/the-sandboxing-illusion-how-to-isolate-agents): classical sandboxes assume the workload is deterministic; reasoning agents break that assumption.

Dual-boundary sandboxing remains a necessary baseline, but treat it as one layer in defense-in-depth — not a hard containment guarantee for adversarial or confused agents.

## Example

The following `bubblewrap` invocation enforces both boundaries simultaneously on Linux. It binds the agent's working directory read-write, mounts everything else read-only or not at all, and isolates the network namespace so outbound traffic is blocked by default.

```bash
bwrap \
  --ro-bind /usr /usr \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --ro-bind /etc/resolv.conf /etc/resolv.conf \
  --bind "$PROJECT_DIR" "$PROJECT_DIR" \
  --dev /dev \
  --proc /proc \
  --tmpfs /tmp \
  --unshare-net \
  --die-with-parent \
  -- claude --dangerously-skip-permissions
```

The `--bind "$PROJECT_DIR"` flag grants read-write access to the working directory only. `--ro-bind` mounts system paths read-only so the agent can execute binaries without modifying them. `--unshare-net` removes all network access; to allowlist specific domains, replace it with a network namespace that routes only through a validating proxy.

For macOS, the equivalent using `sandbox-exec` with a Seatbelt profile — **note: `sandbox-exec` is deprecated since macOS 10.13 and may be removed in a future macOS release**. For new tooling, prefer Docker/Podman or a container-based sandbox. This example illustrates the policy model but should not be used in production without evaluating its removal timeline:

```bash
cat > /tmp/agent-sandbox.sb << 'PROFILE'
(version 1)
(deny default)
(allow file-read*)
(allow file-write* (subpath (param "PROJECT_DIR")))
(allow process-exec)
(deny network*)
PROFILE

sandbox-exec -f /tmp/agent-sandbox.sb -D PROJECT_DIR="$PROJECT_DIR" \
  claude --dangerously-skip-permissions
```

Both examples enforce the filesystem boundary (write access restricted to `$PROJECT_DIR`) and the network boundary (`--unshare-net` / `(deny network*)`) at the OS level — not through prompts — so a prompt-level instruction alone cannot override them. See *When This Backfires* for cases where these boundaries still leak.

## Key Takeaways

- Filesystem-only sandboxing allows network exfiltration; network-only allows filesystem-based privilege escalation
- Both boundaries must be enforced simultaneously at the OS level — not the prompt level
- Use OS primitives: Linux bubblewrap, container network/mount policies (Docker/Podman), or macOS Seatbelt (note: the `sandbox-exec` CLI is deprecated; prefer containers on macOS)
- Define a safe zone (CWD + allowlisted domains) where the agent acts freely; deny everything else
- Approval fatigue from granular prompts is a security risk; dual-boundary sandboxing replaces prompts with hard limits

## Related

- [Sandbox Runtime Comparison](sandbox-runtime-comparison.md)
- [Adopting `docker sbx` for Agent Sandboxes](docker-sbx-adoption.md)
- [Subprocess PID Namespace Sandboxing](subprocess-pid-namespace-sandboxing.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Protecting Sensitive Files](protecting-sensitive-files.md)
