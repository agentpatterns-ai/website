---
title: "Cross-OS Library MicroVM Sandbox for Agent Code (smolvm)"
term: "smolvm"
description: "Reach for smolvm when your agent needs a hardware-isolated sandbox on macOS, Linux, and Windows without adding a container daemon or provisioning Firecracker."
tags:
  - security
  - agent-design
  - tool-agnostic
  - sandboxing
aliases:
  - smolmachines sandbox
  - smolvm microvm
  - library microvm agent sandbox
last_reviewed: 2026-08-20
maturity: emerging
---

# Cross-OS Library MicroVM Sandbox for Agent Code (smolvm)

> smolvm runs each workload in a hardware-isolated libkrun microVM on macOS, Linux, or Windows, without adding a container daemon to the host.

smolvm is a single-binary microVM runtime that launches each workload in a KVM, Hypervisor.framework, or Windows Hypervisor Platform guest with its own kernel, using [libkrun](https://github.com/containers/libkrun) as an in-process VMM instead of a background daemon ([smolmachines.com](https://smolmachines.com)). The isolation boundary is the same hardware virtualization Firecracker relies on, exposed through per-workload CLI flags for CPU, memory, timeout, storage, mounts, and network. It fits the microVM slot in the [sandbox runtime comparison](sandbox-runtime-comparison.md) when sandbox hosts are not all Linux or the deployment cannot add a container-runtime daemon.

## When to reach for it

Pick smolvm over the existing microVM defaults when at least one of these conditions holds:

- Cross-OS host support: developers on macOS Apple Silicon or Intel, Linux x86_64/aarch64, or Windows x86_64 with WHP need the same sandbox artifact ([smolmachines.com](https://smolmachines.com) platform table). Firecracker is Linux-only; Kata Containers depends on a container runtime.
- No daemon on the host: the VMM ships as a library linked into the smolvm binary, so `docker`, `containerd`, or a jailer service is not part of the deployment ([smolmachines.com](https://smolmachines.com) how-it-works).
- Portable per-workload artifact: `smolvm pack create --image <base> -o <name>` produces a self-contained `.smolmachine` executable with dependencies pre-baked, which runs on any supported host ([smolmachines.com](https://smolmachines.com) pack examples).
- A per-task cold-start budget of about a second is acceptable, or throughput justifies the persistent-machine or `machine fork` warm-pool pattern the source documents as the intended production shape.

Skip it for production multi-tenant untrusted-code fleets with hardened CVE-response expectations. Firecracker's AWS Lambda and Fargate track record is the reason the [sandbox runtime comparison](sandbox-runtime-comparison.md) names it as the microVM default, and smolvm 1.8.3 has one publicly reported practitioner battery rather than that history.

## What the flags actually enforce

Simon Willison's test battery against smolvm 1.8.3, run on a GitHub Actions `ubuntu-latest` KVM runner, exercised each guarantee independently ([Simon Willison — Research: smolmachines / smolvm as a sandbox for untrusted Python & JavaScript, 2026-08-19](https://simonwillison.net/2026/Aug/19/smolmachines-untrusted-sandbox/); [simonw/research — smolmachines-untrusted-sandbox](https://github.com/simonw/research/tree/main/smolmachines-untrusted-sandbox)):

| Requirement | smolvm mechanism | Test result |
|-------------|------------------|-------------|
| RAM cap | `--mem <MiB>` | 1 GiB allocation in a 256 MiB VM fails with MemoryError inside guest; host memory unaffected |
| CPU cap | `--cpus <N>` | Fork bomb under `--cpus 1` tears down in about one second, host load 0.69, clean teardown |
| Runaway kill | `--timeout <dur>` enforced by guest agent | `while True:` spin killed at 11 s under `--timeout 10s`, zero leftover VMM processes |
| Disk cap | `--storage <GiB>` (`--overlay` does not bound `/` writes) | Round 2 with `--storage 3` returns ENOSPC as expected; T8 finding recorded that `--overlay 1` let the guest write 4 GB |
| No network | Default; no `--net` means no device attached | `wget` and DNS both fail; smolvm README notes `plan_launch_network` returns backend `None` |
| Read-only inputs | `-v HOST:/in:ro` (virtiofs) | Only the requested `/in` (ro) and `/out` (rw) mounts cross the boundary; `/`, `/workspace`, `/tmp` are guest-local |

Two findings from that battery are worth carrying forward: `--overlay N` does not bound rootfs writes as documented, so use `--storage N`; the HTTP API field is `timeoutSecs` (camelCase), and a `timeout_secs` field is silently ignored.

## Why it works

The isolation guarantee comes from hardware virtualization: each `smolvm machine run` creates a VM with its own guest kernel via KVM on Linux, Hypervisor.framework on macOS, or Windows Hypervisor Platform on Windows ([smolmachines.com](https://smolmachines.com) how-it-works). A syscall exploit inside the guest cannot reach the host kernel, the mechanism the [sandbox runtime comparison](sandbox-runtime-comparison.md) attributes to Firecracker and Kata Containers. The architectural distinctness comes from packaging the VMM as a library. smolmachines.com states "libkrun VMM + custom kernel ... No daemon — the VMM is a library linked into the smolvm binary," which removes the container-runtime daemon the comparison table lists as a microVM cost. Cross-OS reach follows from libkrun compiling against Hypervisor.framework, KVM, and WHP.

## When this backfires

- No nested virtualization available: smolvm needs bare-metal Linux with `/dev/kvm`, macOS 11+, or Windows with WHP. Most container and VM hosts without nested virt cannot run it — Simon Willison's Claude Code container is itself a Firecracker guest and reported "kvm not available" ([simonw/research](https://github.com/simonw/research/tree/main/smolmachines-untrusted-sandbox)).
- Production multi-tenant untrusted-code fleets: the maturity gap against Firecracker is load-bearing. smolvm 1.8.3 has one AI-authored practitioner battery in public view; Firecracker has years of AWS Lambda and Fargate operations plus a documented CVE and patching cadence ([CVE-2026-1386](https://github.com/firecracker-microvm/firecracker/security/advisories/GHSA-36j2-f825-qvgc), cited on the [sandbox runtime comparison](sandbox-runtime-comparison.md)). Choose Firecracker until smolvm accrues equivalent evidence.
- Per-task boot dominates the budget at high throughput: smolmachines.com quotes about 200 ms boot for smolvm against Firecracker's under-125 ms, and Simon Willison's full create-boot-exec-teardown cycle measures 577–643 ms with a local Alpine image. Warm pools via persistent `machine exec` (48 ms warm in the same battery) or `machine fork` recover throughput, at the cost of state persisting between execs on the reused machine.
- The host already carries a container runtime: the library-not-daemon advantage disappears when Docker or Podman is on the box for other reasons.
- Fully offline image pull: rehydration happens inside the guest, so `--image python:3.12-alpine` with no `--net` cannot work. Feed a `docker save` tar (`--image ./python.tar`) or a packed `.smolmachine` artifact instead.

## Example

Simon Willison's recommended per-task shape for a data-transformation service closes every axis with one `machine run` invocation ([simonw/research — smolmachines-untrusted-sandbox README](https://github.com/simonw/research/tree/main/smolmachines-untrusted-sandbox)):

```bash
smolvm machine run \
  --image ./python.tar \
  --cpus 1 --mem 512 \
  --timeout 30s \
  --storage 3 \
  --unprivileged \
  -v "$PWD/in:/in:ro" \
  -v "$PWD/out:/out" \
  -- python3 /in/transform.py
```

The task sees only `/in` (read-only), `/out` (read-write), and a throwaway 3 GiB storage disk. Exit code, stdout, and stderr propagate; the guest agent enforces the timeout and the ephemeral VM is torn down on exit either way. The `--unprivileged` flag drops the guest capability set from `1ffffffffff` to `a80425fb` (the standard unprivileged set), a defense-in-depth layer for the guest itself.

## Key Takeaways

- smolvm places a new row on the microVM axis of the [sandbox runtime comparison](sandbox-runtime-comparison.md): the same hardware boundary as Firecracker, delivered as a library rather than a daemon, on macOS and Windows as well as Linux
- Per-workload flags for CPU, memory, timeout, storage, mounts, and network each map to a mechanism a single practitioner battery has verified against v1.8.3, with two documented gotchas (`--overlay` does not cap rootfs writes, HTTP `timeoutSecs` is case-sensitive)
- Reach for it when cross-OS host support, the absence of a container daemon, or portable `.smolmachine` artifacts is what unblocks the design; stay on Firecracker or Kata Containers for production multi-tenant untrusted-code fleets until smolvm's operational track record catches up
- Nested-virtualization dependency rules it out inside most managed container and CI environments; hosts that expose `/dev/kvm` (GitHub Actions `ubuntu-latest`, some bare-metal cloud tiers) are the current fit
- Per-task cold start is about a second including image rehydration; warm pools via persistent machines or `machine fork` bring per-call latency to about 50 ms, with the trade-off of shared state on the reused machine

## Related

- [Sandboxed Coding Environments: Containers vs MicroVMs vs OS-Level Isolators](sandbox-runtime-comparison.md) — the runtime-family selection this page adds a row to
- [Workload-Keyed Sandbox Selection for Agent-Generated Code](workload-keyed-sandbox-selection.md) — the workload-shape rubric that decides whether a microVM is the right family in the first place
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md) — the filesystem-plus-network threat model smolvm's mount and `--net` defaults satisfy in one runtime
- [Network-less Container + Unix-Socket Egress Proxy for Agent Sandboxes](network-less-container-unix-socket-egress.md) — the same "no interface, no route" topology at the container layer, useful when nested virt rules out smolvm
- [In-Process WebAssembly Sandboxes for Agent-Generated Code](wasm-sandbox-agent-code-execution.md) — the lighter in-process choice when a hardware boundary is more than the workload needs
