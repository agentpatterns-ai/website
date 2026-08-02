---
title: "Cloud-Agent Session Bootstrap: Cached Install plus Per-Session Start"
term: "Cloud-Agent Session Bootstrap"
description: "Split a cloud agent's session bootstrap into a cached install phase and a per-session start phase so dependency churn amortizes while ephemeral setup stays explicit."
tags:
  - agent-design
  - workflows
  - tool-agnostic
  - long-form
aliases:
  - cloud agent install start lifecycle
  - session start hook bootstrap
  - environment.json install lifecycle
last_reviewed: 2026-06-05
maturity: established
---

# Cloud-Agent Session Bootstrap

> Split a cloud agent's session bootstrap into a cached install phase and a per-session start phase so dependency churn amortizes while ephemeral setup stays explicit.

Cursor reports that the single biggest factor in cloud-agent output quality is giving the agent a full development environment — the kind a local agent inherits from a developer's laptop for free ([What we've learned building cloud agents](https://cursor.com/blog/cloud-agent-lessons)). A cloud agent has no laptop to inherit, so it must bootstrap that environment explicitly. That makes how you structure the bootstrap a first-order quality lever, not just a latency optimization.

## When this pattern applies

Three conditions need to hold for the install/start split to pay off:

- The platform exposes a cached-install primitive (Cursor's `environment.json` `install`, Copilot's `copilot-setup-steps.yml`) and a per-session primitive (Cursor's `start`, Copilot's `sessionStart` hook)
- Cacheable work (`npm ci`, `bazel build`, MCP-server install) is meaningfully separable from per-session work (DB seeding, server startup, token rotation)
- You treat the bootstrap script as production code — pinned versions, lockfile-gated rebuilds, review discipline

Without all three, fall through to an adjacent lever: the [prebuilt-image lever](#the-prebuilt-image-lever) below when the toolchain is stable, or [runtime-install only](../../workflows/agent-environment-bootstrapping.md) when no lifecycle split is available.

## The lifecycle split

Dependency installation has a bimodal cost structure. Most work is cacheable — a locked dependency tree produces the same `node_modules` every time. The rest is per-session — ephemeral credentials, DB seeds, server processes that must be alive when the agent attaches. Splitting these onto separate phases keeps cacheable work off the hot path.

| Phase | What runs | Cached? | Cursor field | Copilot surface |
|-------|-----------|---------|--------------|-----------------|
| Install | `npm ci`, `bazel build`, MCP-server install, language toolchains | Yes — disk state snapshotted | `install` ([Cursor Docs](https://cursor.com/docs/cloud-agent/setup)) | `copilot-setup-steps.yml` job ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)) |
| Start | DB seeding, server startup, token rotation, working-tree clone | No — fresh every session | `start` + `terminals` ([Cursor Docs](https://cursor.com/docs/cloud-agent/setup)) | `sessionStart` hook ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/use-hooks)) |

Cursor is explicit about the cache boundary: "After `install` completes, if it took more than a few seconds to run, Cursor will take an internal checkpoint snapshot and will attempt to start future cloud agents from this checkpoint" ([Cursor Docs](https://cursor.com/docs/cloud-agent/setup)). Subsequent sessions boot from the snapshot.

Copilot is more loosely coupled. `copilot-setup-steps.yml` runs in a separate Actions context before the agent starts ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)); `sessionStart` hooks live under `.github/hooks/NAME.json` with `version: 1` and a `hooks.sessionStart` array of bash/powershell commands ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/use-hooks)). The platform composes them; the bootstrap author splits work across both files.

## Why it works

Cacheable installation is isomorphic to a build artifact; per-session startup is isomorphic to a runtime process. Treating them as one obscures the boundary. The cacheable layer pays the install cost once per snapshot generation and amortizes it across many sessions. The start layer keeps per-session actions explicit so failures attribute correctly. Cursor's snapshot is the agent-session-boundary equivalent of Docker layer caching — identical inputs produce identical disk state, and one checkpoint serves every subsequent session until inputs change ([Cursor Docs](https://cursor.com/docs/cloud-agent/setup)). The same separation lets Copilot's `sessionStart` hook run with a 10 to 30 second timeout while heavy work lives in the cached Actions layer ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/use-hooks)).

## When this backfires

- High dispatch volume on a stable toolchain — when the toolchain is stable enough to justify the supply-chain pipeline, a prebuilt image (see [the prebuilt-image lever](#the-prebuilt-image-lever)) pulls in less time than a cached install resumes from snapshot. GitHub measured more than 20% startup improvement from custom Actions images ([GitHub Changelog, 2026-04-27](https://github.blog/changelog/2026-04-27-copilot-cloud-agent-starts-20-faster-with-actions-custom-images/)).
- Bootstrap-time credential exposure — the install hook reads more credentials than agent code should ever see: registry tokens, private-package access, baseline OAuth. Without strict secret scoping the install phase becomes a credential exfiltration surface, and any process it starts inherits its environment.
- Partial-install proceed-anyway semantics — Copilot's documented behavior when `copilot-setup-steps.yml` fails is that "Copilot will start working anyway" ([GitHub Changelog, 2025-07-30](https://github.blog/changelog/2025-07-30-copilot-coding-agent-custom-setup-steps-are-more-reliable-and-easier-to-debug/)). The agent then runs with a half-installed environment and no signal. A bootstrap script must fail loud or the start phase inherits an environment that compiles but does not run.
- Unpinned versions — GitHub's onboarding guide is direct: be "explicit about versions and installation methods rather than letting the agent resolve them ad hoc, precisely to avoid unexpected versions" ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/onboarding-your-ai-peer-programmer-setting-up-github-copilot-coding-agent-for-success/)). Floating versions defeat the snapshot mechanism — the snapshot is only as deterministic as the install that produced it.
- Snapshot staleness drift — long-lived snapshots mask dependency churn the same way stale prebuilt images do. The agent then runs against tooling that diverges from what developers see locally.

## Example

A team running Cursor cloud agents on a Node monorepo wants to compress per-session bootstrap without committing to a baked image.

Before — monolithic bootstrap with everything in one script:

```json
{
  "install": "npm ci && npm run db:seed && npm run dev &",
  "start": ""
}
```

`npm ci` is snapshot-cached, but so are `db:seed` and the backgrounded dev server — neither should persist into the snapshot. The DB seed embeds session-specific state into the cached disk image; the snapshot captures whatever filesystem state happens to exist when install returns.

After — lifecycle-aware split:

```json
{
  "snapshot": "POPULATED_FROM_SETTINGS",
  "install": "npm ci && npm install -g @company/internal-cli@1.4.2",
  "start": "npm run db:seed",
  "terminals": [
    { "name": "Next.js dev", "command": "npm run dev" }
  ]
}
```

The install phase is now purely cacheable: a deterministic `npm ci` from `package-lock.json` plus a pinned global install. Cursor checkpoints the resulting disk state. The start phase runs every session: a fresh DB seed against an ephemeral instance, and a terminal-managed dev server that the agent can interact with ([Cursor Docs](https://cursor.com/docs/cloud-agent/setup)).

The Copilot equivalent puts the cacheable work in `.github/workflows/copilot-setup-steps.yml` ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)) and the per-session work in `.github/hooks/bootstrap.json`:

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [
      {
        "type": "command",
        "bash": "./scripts/seed-db.sh && ./scripts/rotate-token.sh",
        "powershell": "./scripts/seed-db.ps1; ./scripts/rotate-token.ps1",
        "timeoutSec": 30
      }
    ]
  }
}
```

The hook config is on the default branch (Copilot only reads default-branch hook files) and bash/powershell variants run on the matching runner OS ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/use-hooks)).

## The prebuilt-image lever

When dispatch volume is high and the toolchain is stable, a third structure beats the cached install: bake the runtime (toolchain, dependencies, MCP servers) into a custom container image, so each session pays an image-pull instead of an install. Two cold-start levers compose: compress provisioning (prebuild so the runner pulls a cached artifact instead of running `apt-get`/`npm ci`/`pip install` on the hot path) and remove provisioning from the hot path (start inference against the session log while the sandbox is still spinning up — see [Session Harness Sandbox Separation](session-harness-sandbox-separation.md)). GitHub reported that switching the Copilot cloud agent to GitHub Actions custom images cut startup time by more than 20%, a layer on top of an earlier 50% improvement from March 2026 ([GitHub Changelog, 2026-04-27](https://github.blog/changelog/2026-04-27-copilot-cloud-agent-starts-20-faster-with-actions-custom-images/)).

Bake what is stable across sessions; keep dynamic what is per-session:

| Bake into image | Keep dynamic |
|-----------------|--------------|
| Language runtimes and package managers | Working tree (cloned per session) |
| Pinned dependency versions and global tools | Repository secrets and ephemeral tokens |
| Pre-installed MCP server binaries | OAuth flows and session-scoped credentials |
| Linters, formatters, build caches | User-provided task input |

A baked image is only as fresh as its last rebuild, so treat it as production code: pin the base image digest, not the tag (`ubuntu@sha256:...`, not `ubuntu:latest`); schedule rebuilds on a cadence matching dependency churn (weekly for stable stacks, daily for fast-moving); and gate rebuilds on dependency-lock changes so a security patch triggers a rebuild automatically. A custom image is also a long-lived signed registry artifact, unlike a `copilot-setup-steps.yml` install that leaves no persistent artifact, so it adds three review surfaces: base image provenance (publisher, signing key, CVE scan), layer audit (every `RUN` step touching a secret leaves it in layer history, so secret leakage becomes an image-distribution leak), and registry trust (gate pulls by the same controls as the production deploy registry). Agent-purpose sandbox runtimes such as [`docker sbx`](../../security/docker-sbx-adoption.md) compose with prebuilt images by mounting the baked image as the sandbox base ([Sandbox Runtime Comparison](../../security/sandbox-runtime-comparison.md)).

```dockerfile
# image-build pipeline (weekly + on package-lock.json change)
FROM ubuntu:22.04@sha256:<pinned-digest>
RUN apt-get update && apt-get install -y nodejs npm
COPY package.json package-lock.json /opt/prebuild/
RUN cd /opt/prebuild && npm ci --prefix /opt/node_modules
RUN npm install -g @company/internal-cli@1.4.2
```

```yaml
# copilot-setup-steps.yml — only the per-session work remains
jobs:
  copilot-setup-steps:
    runs-on: ghcr.io/company/copilot-runner:2026-05-01
    steps:
      - uses: actions/checkout@v5
      - run: ln -s /opt/node_modules node_modules
```

Skip this lever when dispatch volume is low (the saved seconds do not amortize the rebuild pipeline and image-review overhead), when the toolchain churns weekly (the image is stale before its next rebuild), or when no signed-registry pipeline exists — without provenance review and signed registries, a custom image trades cold-start latency for amplified supply-chain risk, and the runtime-only path ([Agent Environment Bootstrapping](../../workflows/agent-environment-bootstrapping.md)) is safer.

## Key Takeaways

- The install/start lifecycle split keeps cacheable work off the hot path while keeping per-session work explicit — the third bootstrap lever alongside prebuilt images and runtime-only install
- Cursor's `environment.json` and GitHub Copilot's `copilot-setup-steps.yml` + `sessionStart` hooks expose this lifecycle directly; lockfile-keyed snapshots are the cache boundary
- Use this pattern when dependency churn outpaces image rebuild cadence but session volume justifies amortizing the install cost
- Partial-install semantics are silent on both platforms — the bootstrap script must fail loud or the agent runs in a degraded environment
- Treat the install script as production code: pinned versions, lockfile-gated rebuilds, secret scoping that doesn't leak credentials into the snapshot

## Related

- [Agent Environment Bootstrapping](../../workflows/agent-environment-bootstrapping.md) — the runtime-install lever; what to do when no cached lifecycle is available
- [Sandbox Runtime Comparison](../../security/sandbox-runtime-comparison.md) — selection rubric across bubblewrap, Seatbelt, raw Docker/Podman, and `docker sbx` for the baked-image base
- [Cursor Self-Hosted Cloud Agents](../../tools/cursor/self-hosted-cloud-agents.md) — when the runner runs on your infra, image governance is yours end-to-end
- [Session Harness Sandbox Separation](session-harness-sandbox-separation.md) — the architectural split that makes per-session start phases cheap to retry
- [Cloud-Agent Three-Layer State Decoupling](cloud-agent-state-layer-decoupling.md) — the state-layer view of the same bootstrap boundary: which session state belongs in the cached install layer versus the per-session start layer
- [Session Initialization Ritual](session-initialization-ritual.md) — the in-session orient-before-act ritual that runs after bootstrap completes
- [Long-Running Agents](long-running-agents.md) — the operational shape that makes bootstrap latency matter at fleet scale
- [LLM-Pinned Library Versions Carry Systemic CVE Exposure](../../security/llm-pinned-vulnerable-versions.md) — why "pinned versions" is the right discipline: agent-written pins routinely point at CVE-bearing releases
  - long-form
