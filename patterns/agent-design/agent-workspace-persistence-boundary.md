---
title: "Agent Workspace Volumes: Picking the Persistence Boundary"
term: "Workspace Persistence Boundary"
description: "Mount an agent's working tree on a volume that outlives its sandbox when preserving work or reusing cached dependencies justifies the cost and the workload fits the volume's concurrency and file-count limits."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - workspace volume decoupling
  - persistent agent workspace
  - drive-mounted agent workspace
last_reviewed: 2026-10-28
maturity: emerging
---

# Agent Workspace Volumes: Picking the Persistence Boundary

> Persist an agent's workspace or cached dependencies when reuse justifies storage costs and the volume's concurrency and file-count limits fit the workload.

A workspace persistence boundary is the single filesystem path that separates what survives an agent's sandbox from what dies with it. In Vercel's example the rule is positional. With a drive mounted at `/workspace`, "everything under `/workspace` persists on the drive. Everything else belongs to the sandbox" ([Vercel, 2026-10-15](https://vercel.com/blog/introducing-vercel-drives-persistent-storage-for-agents)). Agents resume in a differently configured environment: "Agents can mount the same drive in a new environment configured for the next task and continue where they left off" ([Vercel, 2026-10-15](https://vercel.com/blog/introducing-vercel-drives-persistent-storage-for-agents)). On Vercel the price is one writer, one region, and a slower cold read.

## Choosing the boundary

Northflank recommends a default for independent tasks: "Use ephemeral AI sandboxes by default for independent, reproducible tasks" ([Northflank](https://northflank.com/blog/persistent-vs-ephemeral-ai-sandboxes)).

1. Weigh saved work and setup time against retained-state costs. Vercel documents drives for project files and cached dependencies ([Vercel docs](https://vercel.com/docs/sandbox/concepts/drives)). Northflank says reuse reduces setup, but adds dependency drift and cleanup obligations ([Northflank](https://northflank.com/blog/persistent-vs-ephemeral-ai-sandboxes)).
2. The workload fits the writer contract. Vercel permits one writer; Google's stateful reference gives each agent a private workspace, and Google also documents a shared mode. Vercel: "Only one sandbox at a time can mount a given drive as read-write" ([Vercel docs](https://vercel.com/docs/sandbox/concepts/drives)). Google's Agent Sandbox reference uses `ReadWriteOnce`, where "an agent starts up with a private isolated storage directory it has sole read and write access to" ([Google Cloud](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox-storage)). Modal allows concurrent writers but has no locking: "Last write wins in case of concurrent modification of the same file" ([Modal](https://modal.com/docs/guide/volumes)). It recommends no more than five writers on Volumes v1. Google's `ReadWriteMany` collaborative workspace is the shared option on GKE ([Google Cloud](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox-storage)).
3. The file count fits the volume version. Modal recommends Volumes v1 hold "less than 50,000 files and directories", because "The latency to attach or modify a Volume scales linearly with the number of files in the Volume" ([Modal](https://modal.com/docs/guide/volumes)). Count the files you plan to mount against that figure before you mount them. Modal now recommends v2 for new volumes, with support for more files and concurrent writes from hundreds of containers ([Modal](https://modal.com/docs/guide/volumes)).

## Isolate fan-out writes

Vercel shares a dataset through read-only, point-in-time mounts: "Snapshots allow multiple sandboxes to mount the same drive concurrently. Each snapshot mount reflects the drive as it was at the moment you mounted it, and does not include any writes made to the drive thereafter" ([Vercel docs](https://vercel.com/docs/sandbox/concepts/drives)). Google documents an exploration-branching mode that reaches the same shape through access modes, where you "mount the template folder as read-only and providing a separate writable scratchpad" ([Google Cloud](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox-storage)). Readers write results elsewhere: "They use the shared files as input and save their results separately" ([Vercel, 2026-10-15](https://vercel.com/blog/introducing-vercel-drives-persistent-storage-for-agents)).

Forking a workspace gives each branch its own writable copy, and the reconciliation is yours to build: "Forks don't merge back into the original drive" ([Vercel, 2026-10-15](https://vercel.com/blog/introducing-vercel-drives-persistent-storage-for-agents)). Forking the whole environment instead is [sandbox forking](sandbox-forking.md).

## Why it works

Vercel distinguishes a drive's mounted directory from a snapshot's full sandbox filesystem. Its combined example uses a snapshot with tools installed, then a drive for "project files and cached dependencies" ([Vercel docs](https://vercel.com/docs/sandbox/concepts/drives)). This supports both preserving work and avoiding repeated dependency setup. Google sorts the same decision by data lifecycle into stateful, point-in-time-restore, and ephemeral workspace patterns ([Google Cloud](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox-storage)). Northflank, which sells both lifecycles, lands on the same split: "combine both when an agent needs a durable workspace plus disposable execution" ([Northflank](https://northflank.com/blog/persistent-vs-ephemeral-ai-sandboxes)).

## When this backfires

- Retained dependencies need maintenance. Northflank lists the costs: "dependency drift, accumulated temporary files, compromised state surviving reconnection, and abandoned volumes consuming storage" ([Northflank](https://northflank.com/blog/persistent-vs-ephemeral-ai-sandboxes)).
- Failures stop being attributable. Reset the writable state and "a package installed by one task cannot quietly change the next" ([Northflank](https://northflank.com/blog/persistent-vs-ephemeral-ai-sandboxes)).
- Two agents share a tree. Modal's semantics are last-write-wins, so "any data the last writer didn't have when committing changes will be lost" ([Modal](https://modal.com/docs/guide/volumes)). Even on Volumes v2, "any particular file should only be written to by a single container at a time" ([Modal](https://modal.com/docs/guide/volumes)).
- Placement and start latency are tight. A drive pins to one region and "A sandbox's main region must match a drive's region" ([Vercel docs](https://vercel.com/docs/sandbox/concepts/drives)). On GKE the stateful reference is "applicable to agents that tolerate multi-second startup latency", and going sub-second through warm pools "requires custom scripting and a privileged DaemonSet" ([Google Cloud](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox-storage)).
- The workspace holds fetched content. A volume that outlives the sandbox keeps whatever the agent wrote into it, and every later mount sees it. Northflank lists the result as "compromised state surviving reconnection" ([Northflank](https://northflank.com/blog/persistent-vs-ephemeral-ai-sandboxes)).
- Reads are hot and uncached. Vercel rates a drive at "NVMe speed writes and cache hit reads, slower cache miss reads" against a snapshot's "NVMe speed reads and writes" ([Vercel docs](https://vercel.com/docs/sandbox/concepts/drives)).

## Example

An agent works one repository across several sessions. The mount itself is two commands ([Vercel, 2026-10-15](https://vercel.com/blog/introducing-vercel-drives-persistent-storage-for-agents)):

```bash
sandbox drives get-or-create agent-workspace
sandbox create --mount agent-workspace:/workspace
```

Vercel's documented combination keeps installed tools in the sandbox snapshot and project files plus cached dependencies on the drive ([Vercel docs](https://vercel.com/docs/sandbox/concepts/drives)). Reusing dependencies saves setup work but retains state that needs cleanup ([Northflank](https://northflank.com/blog/persistent-vs-ephemeral-ai-sandboxes)). On Modal Volumes v1, attach latency scales linearly with file count ([Modal](https://modal.com/docs/guide/volumes)). That latency claim is specific to Modal's volume implementation.

Vercel's limits bound the shape: drives "default to 1 TiB, or 1 GiB on Hobby, with up to 16 TiB available" ([Vercel, 2026-10-15](https://vercel.com/blog/introducing-vercel-drives-persistent-storage-for-agents)), and "A sandbox can mount up to 4 drives per run" ([Vercel docs](https://vercel.com/docs/sandbox/concepts/drives)).

## Key Takeaways

- In Vercel's example the boundary is positional: everything under the mount point persists on the drive and everything else belongs to the sandbox
- Compare dependency setup time with retained-state maintenance costs. Vercel supports cached dependencies on drives; Modal Volumes v1 also adds attach latency as file count grows
- Vercel permits one writable mount; Google documents a private workspace per agent. Modal allows concurrent writers with last-write-wins per file, and Google also documents a shared mode. Give fan-out workers separate result paths
- The costs are vendor-specific. Vercel drives are single-region and read slower on a cache miss. GKE's stateful reference suits agents that tolerate multi-second startup, and sub-second start needs warm pools
- A workspace that outlives its sandbox keeps whatever the agent wrote into it; Northflank lists "compromised state surviving reconnection" as a cost

## Related

- [Session Harness Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — the three-primitive split this boundary sits inside, which treats the sandbox filesystem as one layer
- [Cloud-Agent Three-Layer State Decoupling](cloud-agent-state-layer-decoupling.md) — the same decoupling argument at machine-state granularity, where the whole sandbox hibernates rather than its working tree detaching
- [Continuously Built Agent Environments](continuously-built-agent-environments.md) — the derivable half, rebuilt on a schedule so the environment you discard is cheap to replace
- [Full Sandbox Snapshots Beat Retry Only for Untracked State](snapshot-branching-boundary.md) — a measured case that untracked state is what justifies persisting a machine at all
- [Sandbox Forking: Branch Agent Runs From a Warm Snapshot](sandbox-forking.md) — forking the environment rather than the workspace, and the conditions that make a fork pay
