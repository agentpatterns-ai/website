---
title: "Dual-Boundary Sandboxing for Secure Agent Execution"
description: "Enforce both filesystem and network isolation; neither boundary alone prevents security breaches or data exfiltration by an autonomous agent."
tags:
  - agent-design
  - security
---
# Dual-Boundary Sandboxing

> Enforce both filesystem and network isolation simultaneously; neither boundary alone is sufficient to prevent security breaches or data exfiltration by an autonomous agent.

## Why One Boundary Is Not Enough

A common assumption is that restricting an agent to its working directory is sufficient to contain it. It is not. An agent with filesystem access but unrestricted network access can exfiltrate any file it can read — SSH keys, environment variables, secrets — via outbound connections.

The inverse is equally incomplete: restricting network access while leaving filesystem paths unrestricted allows the agent to write to sensitive locations (startup scripts, crontabs, shell configuration files) that execute with elevated permissions on the next trigger.

Per [Anthropic's Claude Code sandboxing post](https://www.anthropic.com/engineering/claude-code-sandboxing), effective sandboxing requires both boundaries enforced simultaneously at the OS level.

## The Two Boundaries

**Filesystem boundary:**

- Restrict write access to the current working directory
- Block writes to parent directories, home directory files, and system paths
- Read access restrictions depend on the task's legitimate data needs

**Network boundary:**

- Allowlist approved outbound domains (package registries, APIs the agent is explicitly authorized to use)
- Route all other traffic through a validating proxy or block it
- Block inbound connections to the agent's environment

These boundaries are enforced at the OS level, not the prompt level. Prompt-level restrictions can be bypassed by a sufficiently determined or confused agent; OS-level restrictions cannot.

## OS Enforcement Mechanisms

- **Linux:** `bubblewrap` (used by Flatpak) applies filesystem namespaces and seccomp filters; network namespaces restrict outbound traffic
- **macOS:** `Seatbelt` (sandbox profiles via `sandbox-exec`) applies filesystem and network policies — note that `sandbox-exec` is deprecated since macOS 10.13 and may be removed in a future release; prefer container-based approaches (Docker/Podman) for new tooling
- **Container-based:** Docker/Podman with restricted mount points and network policies achieve similar effects with more tooling overhead

The agent runs inside the enforced environment. Permissions it needs (specific filesystem paths, specific domains) are granted explicitly; everything else is denied by default.

## The Approval Fatigue Problem

Granular permission prompts for every agent action create [approval fatigue](../human/safe-command-allowlisting.md): users click through without reading. This is worse than no prompts — it produces the illusion of oversight with none of the substance. Dual-boundary sandboxing resolves this by defining a safe operating zone where the agent can act freely, and hard limits where it cannot act at all. Prompts are reserved for boundary-crossing requests, which are rare and meaningful.

## Threat Model

The sandbox addresses two distinct threat vectors:

1. **Prompt injection** — malicious content in files or web pages the agent processes instructs it to exfiltrate data or modify system files. Network and filesystem restrictions limit the damage scope.
2. **Agent error** — the agent makes a mistake (deletes a file outside the working directory, makes an unintended API call). OS-level restrictions prevent the error from having consequences outside the defined boundary.

The sandbox does not address all threats. It does not prevent the agent from producing incorrect output, spending budget on unauthorized API calls within the allowlist, or leaking data through allowed channels.

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

Both examples enforce the filesystem boundary (write access restricted to `$PROJECT_DIR`) and the network boundary (`--unshare-net` / `(deny network*)`) at the OS level — not through prompts — so no agent instruction can override them.

## Key Takeaways

- Filesystem-only sandboxing allows network exfiltration; network-only allows filesystem-based privilege escalation
- Both boundaries must be enforced simultaneously at the OS level — not the prompt level
- Use OS primitives: Linux bubblewrap, container network/mount policies (Docker/Podman), or macOS Seatbelt (note: the `sandbox-exec` CLI is deprecated; prefer containers on macOS)
- Define a safe zone (CWD + allowlisted domains) where the agent acts freely; deny everything else
- Approval fatigue from granular prompts is a security risk; dual-boundary sandboxing replaces prompts with hard limits

## Related

- [Worktree Isolation](../workflows/worktree-isolation.md)
- [Protecting Sensitive Files](protecting-sensitive-files.md)
- [Deterministic Guardrails](../verification/deterministic-guardrails.md)
- [Secrets Management for Agents](secrets-management-for-agents.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Scope Sandbox Rules to Harness-Owned Tools, Not Third-Party MCP Tools](sandbox-rules-harness-tools.md)
- [Enterprise Agent Hardening: Governance, Observability, and Reproducibility](enterprise-agent-hardening.md)
- [Close the Attack-to-Fix Loop](close-attack-to-fix-loop.md)
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md)
- [Guarding Against URL-Based Data Exfiltration](url-exfiltration-guard.md)
- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md)
- [Code Injection Defence in Multi-Agent Pipelines](code-injection-multi-agent-defence.md)
- [Safe Outputs Pattern](safe-outputs-pattern.md)
- [Human-in-the-Loop Confirmation Gates](human-in-the-loop-confirmation-gates.md)
- [Use a Public-Web Index to Gate Automatic URL Fetching](url-fetch-public-index-gate.md)
- [Tool Signing and Signature Verification](tool-signing-verification.md)
- [Permission-Gated Custom Commands](permission-gated-commands.md)
- [PII Tokenization in Agent Context](pii-tokenization-in-agent-context.md)
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md)
