---
title: "Sandbox Forking: Branch Agent Runs From a Warm Snapshot"
term: "Sandbox Forking"
description: "Prepare an agent environment once, snapshot it, then fork a copy per run — worth doing only when setup is expensive and the children need no unique identity or live connections."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - fork from snapshot
  - snapshot-forked agent environments
last_reviewed: 2026-08-02
maturity: adopted
---

# Sandbox Forking: Branch Agent Runs From a Warm Snapshot

> Prepare an agent environment once, snapshot it, then fork a private copy per run so each run skips provisioning instead of repeating it.

Sandbox forking branches each parallel agent run off a saved snapshot of an already-provisioned environment rather than building that environment again. The child inherits the parent's filesystem, installed dependencies, and configuration, so five variations of a task cost one setup plus five copies instead of five setups.

Four vendors ship the primitive. Vercel exposes `Sandbox.fork()` and a `sandbox fork` command ([Vercel changelog, July 2026](https://vercel.com/changelog/vercel-sandbox-supports-forking)). Modal offers filesystem, directory, and memory snapshots for "branching your Sandbox's state to test different code changes independently" ([Modal docs](https://modal.com/docs/guide/sandbox-snapshots)). E2B's `fork()` takes a `count` parameter, and "You can request up to 100 forks at once" ([E2B docs](https://e2b.dev/docs/sandbox/fork)). GKE Pod snapshots let you "capture a specific state and use it as a base to start multiple new sandboxes with the same initialized state" ([Google Cloud docs](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox-pod-snapshots)).

## Three conditions make it worth doing

Setup has to be expensive relative to creating a sandbox. Forking is not a cheaper call: "A fork takes about the same time as creating a sandbox, with the same limits" ([Vercel](https://vercel.com/changelog/vercel-sandbox-supports-forking)). Everything you save comes from work inside the sandbox that you no longer repeat, so a baseline that installs a large toolchain and starts a database pays back where one cached dependency install does not.

The baseline has to be rebuilt from a declarative source on a schedule. A snapshot is a captured machine, not a build artifact, and machines maintained by hand drift into "unique, undocumented systems ... known as snowflakes" ([Wiz](https://www.wiz.io/academy/container-security/what-is-a-golden-image)). Treat the snapshot as a cache in front of a `Dockerfile`, devcontainer, or Nix flake that stays in version control. Refresh it on the cadence Wiz prescribes for golden images: "a scheduled cadence (typically monthly, with emergency rebuilds for critical CVEs)" ([Wiz](https://www.wiz.io/academy/container-security/what-is-a-golden-image)).

The children have to tolerate inherited identity. A Vercel fork "inherits its config and environment variables" ([Vercel](https://vercel.com/changelog/vercel-sandbox-supports-forking)), and at the microVM layer "unique identifiers, cached random numbers, cryptographic tokens, etc will still be replicated across multiple microVMs resumed from the same snapshot" ([Firecracker](https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md)). Every sibling starts life holding the same secrets.

## What a fork inherits

Read your platform's fork contract before assuming anything, because the semantics diverge between vendors. Three of them change what you may assume about a child on Vercel ([Vercel](https://vercel.com/changelog/vercel-sandbox-supports-forking)):

- The fork starts "from the source's current snapshot and inherits its config and environment variables." Any parameter you pass explicitly overrides the inherited value.
- If the source is running, the fork takes "the latest saved state, not the live in-memory state." Work in flight at fork time is absent from the child.
- If the source has no snapshot, the fork "falls back to a fresh create, using the source's `runtime` and config." The call succeeds and returns a working sandbox that quietly paid full setup cost.

E2B inverts the middle point: its fork snapshots the sandbox in place, "paused, captured with its full filesystem and memory state, and resumed," so each child does start from live memory including running processes and loaded variables ([E2B docs](https://e2b.dev/docs/sandbox/fork)). Which behavior you get is a property of the platform, not of the pattern.

## How this differs from worktree isolation

[Worktree isolation](../../workflows/worktree-isolation.md) branches the source tree: each agent gets its own checked-out branch and working directory while sharing git objects with the main checkout. Sandbox forking branches the whole provisioned machine, including installed packages, built artifacts, and running services. The two solve different halves of one problem and compose — fork the environment, then create a worktree inside each child.

Keep this separate from running several agents inside one sandbox, where each agent gets its own Linux user and private home directory so "users can't read, write, or list each other's files" ([Vercel changelog](https://vercel.com/changelog/run-multiple-isolated-agents-in-a-single-sandbox)). That shares one environment between agents; forking gives each agent its own.

## Why it works

Provisioning is deterministic and idempotent, so running it N times produces N identical results and only the first execution carries information. Snapshotting that result once and branching each run off it converts N executions into one execution plus N copy-on-write copies. That is why Vercel documents that "Using a snapshot is much faster than creating from scratch because it avoids reinstalling dependencies and repeating setup steps" ([Vercel docs](https://vercel.com/docs/vercel-sandbox/concepts)). DeltaBox measures the same structure at a finer grain: duplicating only the delta between checkpoints drops restore to "≈1.86 ms" on its template-fork path and cuts state-management overhead "from 23–48% of total time on the E2B baseline to 1–2%" ([Dong et al., 2026, v2](https://arxiv.org/abs/2605.22781v2)). The saving scales with how expensive the baseline was, not with how many children you launch.

## When this backfires

- Setup is already cheap. A fork costs roughly what a create costs, so a warm dependency install measured in seconds buys nothing ([Vercel](https://vercel.com/changelog/vercel-sandbox-supports-forking)).
- The child must observe live in-flight state and the platform does not capture it. On Vercel a fork of a running source takes "the latest saved state, not the live in-memory state" ([Vercel](https://vercel.com/changelog/vercel-sandbox-supports-forking)), so anything mid-execution is absent from every child.
- Children need distinct cryptographic identity. Firecracker's maintainers state that "resuming execution from the same state more than once" is insecure, and VMGenID reseeds only the guest kernel pool: "unique identifiers, cached random numbers, cryptographic tokens, etc will still be replicated" ([Firecracker snapshot support](https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md)). Cloning a post-initialization snapshot raises "the challenge of restoring the uniqueness of the VMs, to allow them to do unique things like generate UUIDs, secrets, and nonces" ([Brooker et al., 2021](https://arxiv.org/abs/2102.12892v1)).
- The baseline holds live network state. "It is also not guaranteed that the state of the network connections survives the process" ([Firecracker snapshot support](https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md)), and every clone resumes "with the same IP address(es)", so a fan-out needs a separate network namespace per clone plus `iptables` NAT ([Firecracker network guide](https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/network-for-clones.md)).
- Children write to shared external systems. Forking isolates the sandbox, not the database or API behind it, and DeltaBox "does not currently support network I/O rollback, which may incur external side effects" ([Dong et al., 2026, v2](https://arxiv.org/abs/2605.22781v2)).
- Nobody refreshes the baseline. An image built on a base "that hasn't been updated in months" inherits "every CVE in that base", and traditional snapshots "often accidentally capture sensitive data (like logs, temp files, or credentials) that were active during the golden build" ([Wiz](https://www.wiz.io/academy/container-security/what-is-a-golden-image)).

The strongest argument against the pattern follows from the last two points: a declarative rebuild plus a warm layer cache recovers much of the saving while producing an artifact your pipeline can sign with "Sigstore/Cosign", pin by digest "to ensure your builds are reproducible", and ship with "an SBOM (software bill of materials) for every build" ([Wiz](https://www.wiz.io/academy/container-security/what-is-a-golden-image)). Fork when measured setup cost justifies giving that up.

## Example

The check worth writing into a fan-out is a snapshot assertion before the first fork. On Vercel, "if the source has no snapshot, it falls back to a fresh create, using the source's `runtime` and config" ([Vercel changelog](https://vercel.com/changelog/vercel-sandbox-supports-forking)) — a success return that quietly paid full setup cost. A loop that calls `Sandbox.fork()` (or `sandbox fork` from the CLI) without first confirming the source was snapshotted can therefore run for weeks paying per-child setup while every call reports success.

## Key Takeaways

- Fork the environment when setup is expensive; the fork call itself costs about what a create costs, so all the saving comes from provisioning you skip.
- Treat the snapshot as a cache in front of a declarative build and refresh it on a schedule — a snapshot is a captured machine, not a reproducible artifact.
- Fork semantics are per-vendor: check whether your platform's fork captures live memory or only the last saved state, and whether a source with no snapshot silently falls back to a full build.
- Do not fork when children need unique cryptographic identity, or when the baseline holds live network state: identifiers and tokens replicate across siblings, and connections are not guaranteed to survive the resume.
- Worktree isolation branches the source tree, sandbox forking branches the provisioned machine, and the two compose.

## Related

- [Worktree Isolation: Parallel Agent Sessions in Safe Sandboxes](../../workflows/worktree-isolation.md) — isolates the working tree rather than the whole provisioned environment
- [Session Harness Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — the architecture that makes the sandbox a replaceable primitive you can snapshot
- [Delta Channels: Bounded Checkpoint Storage for Append-Only Agent State](delta-channels-checkpoint-storage.md) — the same delta-over-snapshot economics applied to session state
- [Agent Environment Bootstrapping](../../workflows/agent-environment-bootstrapping.md) — provisioning the baseline deterministically before any fork exists
- [Experiential-Learning Setup Agents with Snapshot Rollback (SetupX)](../../workflows/experiential-setup-agents-snapshot-rollback.md) — the same snapshot primitive used to undo a failed setup step rather than to fan out
- [Continuously Built Agent Environments](continuously-built-agent-environments.md) — the build-promotion loop that keeps the snapshot you fork from fresh and known-good
