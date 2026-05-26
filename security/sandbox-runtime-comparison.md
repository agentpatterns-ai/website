---
title: "Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators"
description: "A selection rubric for the runtime layer of sandboxed coding agents — when containers, microVMs, or OS-level isolators are the right fit and what each costs in latency, blast radius, and ergonomics."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - sandbox runtime comparison
  - agent sandbox runtime selection
last_reviewed: 2026-05-27
---

# Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators

> Pick the runtime layer for a coding-agent sandbox by trading blast-radius granularity against startup cost — containers are fast and kernel-shared, microVMs are hardware-isolated and slower, OS-level isolators are fastest but weakest against escape.

## The Three Runtime Families

[Dual-boundary sandboxing](dual-boundary-sandboxing.md) defines *what* a sandbox enforces. This page picks *which runtime* enforces it:

- **Containerized** — Linux namespaces and cgroups, optionally hardened with [gVisor](https://github.com/google/gvisor) or seccomp. Examples: `docker sbx`, Podman.
- **MicroVM** — KVM-backed lightweight VMs with a minimalist VMM. Examples: [Firecracker](https://github.com/firecracker-microvm/firecracker)-based providers (e2b, Daytona, Modal), Kata Containers.
- **OS-level isolators** — host-kernel primitives without a container daemon. Examples: [bubblewrap](https://github.com/containers/bubblewrap) on Linux, `sandbox-exec`/Seatbelt on macOS.

Differences are trade-offs across startup latency, escape surface, host overhead, and secret hydration — not better vs worse.

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

- **High session churn with prebuilt images.** Cold start is dominated by image pull, not VM boot. With [prebuilt agent environments](../agent-design/prebuilt-agent-environments.md) and a warm registry cache, the first useful tool call lands well under a second.
- **Dev-machine parity.** The container the agent runs matches the one CI runs.
- **Low-cost CI fleets.** Container runtimes ship with every modern CI provider; no extra infra.

For untrusted code, [gVisor](https://github.com/google/gvisor) sits between plain containers and microVMs — a userspace kernel that intercepts guest syscalls via the `runsc` OCI runtime, trading syscall-compatibility breakage for a smaller host-kernel attack surface.

## When MicroVMs Win

- **Untrusted-code execution.** When the agent runs code generated from untrusted inputs (third-party PRs, prompt-injected scripts, customer snippets), a kernel CVE turns a shared-kernel runtime into a multi-tenant breach. A microVM puts a hypervisor between workload and kernel.
- **Multi-tenant fleets.** Firecracker was built at AWS for Lambda and Fargate ([firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker)) — thousands of mutually-untrusting microVMs per host with hardware-enforced separation.
- **Acceptable cold start.** ≤125 ms from API call to guest init ([Firecracker spec](https://github.com/firecracker-microvm/firecracker/blob/main/SPECIFICATION.md)) — the agent loop doesn't feel it after image-pull amortization.

The cost: GPU passthrough, exotic syscalls, and host-device access need explicit plumbing. Hypervisor isolation is also necessary but not sufficient — the VMM and jailer perimeter still ships CVEs. [CVE-2026-1386](https://github.com/firecracker-microvm/firecracker/security/advisories/GHSA-36j2-f825-qvgc) (host file overwrite via symlink in the Firecracker jailer, ≤ v1.13.1 and v1.14.0) is the recent reminder: patch the runtime as aggressively as the guest kernel.

## When OS-Level Isolators Win

- **Single-host dev workflows.** No daemon to install, no registry to authenticate against. `bubblewrap` ships in every major Linux distribution and backs Flatpak ([containers/bubblewrap](https://github.com/containers/bubblewrap)). Claude Code uses it by default on Linux and WSL2 ([Claude Code Sandboxing](https://code.claude.com/docs/en/sandboxing)).
- **No daemon dependency.** Air-gapped or hardened hosts where adding `dockerd` is itself a risk.
- **Tightest host-shell integration.** The agent shares the host's PATH, package cache, and dotfiles read-only without an image-build step.

The cost: weaker escape resistance than microVMs. On macOS, `sandbox-exec` is **deprecated since macOS 10.13** and may be removed; prefer containers or microVMs for new macOS tooling. On Linux, depth depends on seccomp filter quality.

## Composition With Existing Patterns

Runtime choice is one layer, not the whole sandbox. [Dual-boundary sandboxing](dual-boundary-sandboxing.md) is the threat model every runtime must enforce. [Subprocess PID namespace sandboxing](subprocess-pid-namespace-sandboxing.md) adds a Linux-specific third layer to block daemon persistence. [Prebuilt agent environments](../agent-design/prebuilt-agent-environments.md) is the container cold-start lever. [Session harness sandbox separation](../agent-design/session-harness-sandbox-separation.md) hides runtime choice behind `execute(name, input)` — "the harness doesn't know whether the sandbox is a container, a phone, or a Pokémon emulator" ([Anthropic, 2026](https://www.anthropic.com/engineering/managed-agents)) — so the fleet's runtime can change without rewriting agent code.

## When This Backfires

- **Procurement-driven choice trumps the rubric.** If the team is already on Modal, e2b, or Kubernetes, the runtime is decided by platform. The comparison applies at platform-selection time.
- **Single-host, single-tenant, trusted code.** A laptop running its owner's prompts has no multi-tenant adversary; bubblewrap or Seatbelt is correct and microVMs add cost without benefit.
- **Agents reasoning around the runtime.** No runtime stops a capable agent from finding alternative execution paths. [Ona documented](https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox) a Claude Code session that bypassed its own denylist and disabled bubblewrap. Runtime hardness is necessary, not sufficient — see *[the sandbox illusion](https://www.manifold.security/blog/the-sandboxing-illusion-how-to-isolate-agents)*.

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
- [Prebuilt Agent Environments](../agent-design/prebuilt-agent-environments.md)
- [Session Harness Sandbox Separation for Long-Running Agents](../agent-design/session-harness-sandbox-separation.md)
- [Docker sbx Adoption for Coding Agents](docker-sbx-adoption.md)
- [Windows Sandboxing for Coding Agents](windows-sandbox-primitives-coding-agents.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
