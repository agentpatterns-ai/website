---
title: "Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators"
term: "Sandboxed Coding Environments"
description: "A selection rubric for the runtime layer of sandboxed coding agents — when containers, microVMs, or OS-level isolators are the right fit and what each costs in latency, blast radius, and ergonomics."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - sandbox runtime comparison
  - agent sandbox runtime selection
last_reviewed: 2026-06-09
maturity: established
---

# Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators

> Pick a coding-agent sandbox runtime by trading isolation strength against startup cost: containers fast but kernel-shared, microVMs hardware-isolated but slower, OS-level isolators fastest but weakest.

## The Three Runtime Families

[Dual-boundary sandboxing](dual-boundary-sandboxing.md) defines *what* a sandbox enforces; this page picks *which runtime* enforces it:

- **Containerized** — Linux namespaces and cgroups, optionally hardened with [gVisor](https://github.com/google/gvisor) or seccomp. Examples: `docker sbx`, Podman.
- **MicroVM** — KVM-backed lightweight VMs with a minimalist VMM. Examples: [Firecracker](https://github.com/firecracker-microvm/firecracker)-based providers (e2b, Daytona, Modal), Kata Containers.
- **OS-level isolators** — host-kernel primitives without a container daemon. Examples: [bubblewrap](https://github.com/containers/bubblewrap) on Linux, `sandbox-exec`/Seatbelt on macOS.

A fourth, orthogonal option is to consume one of these families as a **managed/hosted runtime** rather than self-hosting it: LangChain's LangSmith ships a managed agent sandbox that gives each agent its own dedicated isolated computer — a VM with its own environment, dependencies, and network access ([LangChain — Give your AI agent its own computer](https://blog.langchain.com/give-your-ai-agent-its-own-computer)), and GitHub now offers commodity cloud and local agent-execution sandboxes for Copilot in public preview ([GitHub changelog — Cloud and local sandboxes for GitHub Copilot](https://github.blog/changelog/2026-06-02-cloud-and-local-sandboxes-for-github-copilot)). These trade operational control for the same isolation boundaries below — the comparison still applies to whichever family the managed provider wraps.

## Comparison

| Dimension | Containers | MicroVMs | OS-Level Isolators |
|-----------|-----------|----------|--------------------|
| Isolation boundary | Shared host kernel + namespaces | Hardware virtualization (KVM) | Shared host kernel + namespaces or Seatbelt policy |
| Startup latency | ~100 ms-seconds (image pull dominates) | ≤125 ms VM boot to guest init ([Firecracker spec](https://github.com/firecracker-microvm/firecracker/blob/main/SPECIFICATION.md)) | tens of ms (no daemon) |
| Per-instance memory overhead | Process-level (image footprint) | ≤5 MiB VMM at 1 vCPU/128 MiB ([Firecracker spec](https://github.com/firecracker-microvm/firecracker/blob/main/SPECIFICATION.md)) | Negligible (no VM, no daemon) |
| Blast radius on escape | Host kernel CVEs | Hypervisor CVEs (smaller surface) | Host kernel + namespace/profile bugs |
| Network policy | iptables, CNI, sidecar proxies | Tap device + host bridge | Network namespace + proxy |
| Secret hydration | Env vars, mounts, registry secrets | API-injected at provision time | Inherits parent env (scrub explicitly) |
| Daemon dependency | Yes (Docker/Podman/containerd) | Yes (jailer + VMM) | No |
| Multi-tenant safety | Weak without gVisor or Kata | Strong | Weak |

## When Containers Win

- **High session churn with prebuilt images.** Cold start is dominated by image pull, not VM boot; with [prebuilt agent environments](../agent-design/cloud-agent-session-bootstrap.md) and a warm cache, the first tool call lands sub-second.
- **Dev-machine parity.** The container the agent runs matches CI's.
- **Low-cost CI fleets.** Container runtimes ship with every CI provider — no extra infra.

[gVisor](https://github.com/google/gvisor) sits between plain containers and microVMs — a userspace kernel intercepting guest syscalls via `runsc`, trading syscall compatibility for a smaller attack surface.

## When MicroVMs Win

- **Untrusted-code execution.** When the agent runs code from untrusted inputs (third-party PRs, prompt-injected scripts, customer snippets), a kernel CVE turns a shared-kernel runtime into a multi-tenant breach. A microVM puts a hypervisor between workload and kernel.
- **Multi-tenant fleets.** Firecracker was built at AWS for Lambda and Fargate ([firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker)) — thousands of mutually-untrusting, hardware-separated microVMs per host.
- **Acceptable cold start.** ≤125 ms to guest init ([Firecracker spec](https://github.com/firecracker-microvm/firecracker/blob/main/SPECIFICATION.md)), imperceptible after image-pull amortization.

The cost: GPU passthrough and host-device access need explicit plumbing. Hypervisor isolation is necessary but not sufficient — the VMM and jailer perimeter still ships CVEs. [CVE-2026-1386](https://github.com/firecracker-microvm/firecracker/security/advisories/GHSA-36j2-f825-qvgc) (jailer symlink host-file overwrite, ≤ v1.13.1 and v1.14.0) is the reminder: patch the runtime as hard as the guest kernel.

## When OS-Level Isolators Win

- **Single-host dev workflows.** No daemon to install, no registry to authenticate. `bubblewrap` ships in every major Linux distribution and backs Flatpak ([containers/bubblewrap](https://github.com/containers/bubblewrap)); Claude Code uses it by default on Linux and WSL2 ([Claude Code Sandboxing](https://code.claude.com/docs/en/sandboxing)).
- **No daemon dependency.** Air-gapped or hardened hosts where adding `dockerd` is itself the risk.
- **Tightest host-shell integration.** The agent shares the host's PATH and dotfiles read-only — no image build.

The cost: weaker escape resistance than microVMs. On macOS, `sandbox-exec` is **deprecated since macOS 10.13** — prefer containers or microVMs for new macOS tooling. On Linux, depth depends on seccomp quality.

## Composition With Existing Patterns

Runtime choice is one layer, not the whole sandbox. [Dual-boundary sandboxing](dual-boundary-sandboxing.md) is the threat model every runtime enforces; [subprocess PID namespace sandboxing](subprocess-pid-namespace-sandboxing.md) adds a Linux layer blocking daemon persistence; [Session harness sandbox separation](../agent-design/session-harness-sandbox-separation.md) hides runtime choice behind `execute(name, input)`, so the runtime can change without rewriting agent code.

## When This Backfires

- **Procurement-driven choice trumps the rubric.** If the team is already on Modal, e2b, or Kubernetes, the platform decides the runtime — the comparison applies only at platform-selection time.
- **Single-host, single-tenant, trusted code.** A laptop running its owner's prompts has no multi-tenant adversary; bubblewrap or Seatbelt is correct, and microVMs add cost for nothing.
- **Agents reasoning around the runtime.** No runtime stops a capable agent from finding alternative execution paths. [Ona documented](https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox) a Claude Code session that bypassed its own denylist and disabled bubblewrap — runtime hardness is necessary, not sufficient (see *[the sandbox illusion](https://www.manifold.security/blog/the-sandboxing-illusion-how-to-isolate-agents)*).

## Example

A platform team evaluates runtimes for a fleet running customer-submitted prompts producing arbitrary code.

**Decision input:** untrusted workload; multi-tenant; cold-start budget < 1 s; existing Kubernetes on bare metal.

**Selection trace:**

1. Untrusted + multi-tenant → shared-kernel containers insufficient. Drop plain Docker.
2. Cold-start < 1 s → rules out heavyweight VMs; compatible with Firecracker (≤125 ms boot per [spec](https://github.com/firecracker-microvm/firecracker/blob/main/SPECIFICATION.md)).
3. Existing Kubernetes → Kata Containers or a Firecracker-based provider (e2b, Modal) integrate without abandoning the orchestrator.
4. OS-level isolators ruled out for this fleet, but remain the right pick for the developer laptops that build the agent.

**Outcome:** Firecracker-based microVMs for production; bubblewrap (Linux) and Seatbelt (macOS) for local dev — with the macOS choice flagged for migration when Apple removes `sandbox-exec`.

## Key Takeaways

- Three families with distinct trade-offs: containers (kernel-shared, fast, weakest), microVMs (hypervisor-isolated, ~125 ms boot, strong), OS-level isolators (no daemon, fastest, weak against escape)
- Untrusted-code or multi-tenant workloads warrant a microVM; trusted single-host dev workflows do not
- macOS `sandbox-exec` is deprecated since 10.13 — plan a migration path for new tooling on macOS
- Runtime choice composes with dual-boundary enforcement, subprocess sandboxing, prebuilt environments, and harness/sandbox separation — the runtime is one layer, not the whole sandbox
- The harness API hides runtime choice from the agent, so the runtime can change per fleet without rewriting the agent loop

## Related

- [Dual-Boundary Sandboxing for Secure Agent Execution](dual-boundary-sandboxing.md)
- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md)
- [Prebuilt Agent Environments](../agent-design/cloud-agent-session-bootstrap.md)
- [Session Harness Sandbox Separation for Long-Running Agents](../agent-design/session-harness-sandbox-separation.md)
- [Docker sbx Adoption for Coding Agents](docker-sbx-adoption.md)
- [Windows Sandboxing for Coding Agents](windows-sandbox-primitives-coding-agents.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
