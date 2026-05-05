---
title: "Prebuilt Agent Environments: Amortising Cloud Agent Cold Start with Custom Container Images"
description: "Bake the cloud agent's runtime — toolchain, dependencies, MCP servers — into a custom container image so each session pays an image-pull cost instead of a fresh install cost."
tags:
  - agent-design
  - workflows
  - tool-agnostic
  - github-actions
aliases:
  - prebuilt cloud agent images
  - custom Actions images for agents
  - agent runtime prebuild
---

# Prebuilt Agent Environments

> Bake the cloud agent's runtime — toolchain, dependencies, MCP servers — into a custom container image so each session pays an image-pull cost instead of a fresh install cost.

## The Cold-Start Tax

A cloud agent session pays a fixed cost before its first useful tool call: pull the runner image, clone the repo, install the toolchain, restore caches, hydrate secrets, connect MCP servers. That work runs every time the runner is dispatched. Per-session it is seconds-to-minutes; multiplied by the dispatch volume of a team running many issue-assigned and `@copilot`-triggered sessions per day, it is the dominant fleet-wide latency.

Two cold-start levers compose:

1. **Compress provisioning** — prebuild the environment so the runner pulls a cached artifact instead of running `apt-get`/`npm ci`/`pip install` on the hot path.
2. **Remove provisioning from the hot path** — start inference against the session log while the sandbox is still spinning up ([Anthropic, 2026](https://www.anthropic.com/engineering/managed-agents)).

This page covers lever (1). For lever (2), see [Session Harness Sandbox Separation](session-harness-sandbox-separation.md).

## What the Image Bakes

GitHub reported that switching the Copilot cloud agent to GitHub Actions custom images cut startup time by over 20%, "thanks to optimized runner environments built with GitHub Actions custom images" — a layer on top of an earlier 50% improvement from March 2026 ([GitHub Changelog, 2026-04-27](https://github.blog/changelog/2026-04-27-copilot-cloud-agent-starts-20-faster-with-actions-custom-images/)). The mechanism: "by prebuilding that environment with a custom Actions image, startup overhead has been significantly reduced" (same source).

Bake what is stable across sessions; keep dynamic what is per-session.

| Bake into image | Keep dynamic |
|-----------------|--------------|
| Language runtimes and package managers | Working tree (cloned per session) |
| Pinned dependency versions and global tools | Repository secrets and ephemeral tokens |
| Pre-installed MCP server binaries | OAuth flows and session-scoped credentials |
| Linters, formatters, build caches | User-provided task input |

## The Freshness Trade-off

A baked image is only as fresh as its last rebuild. The tighter the rebuild cadence, the smaller the staleness window — and the higher the build-pipeline cost. GitHub's onboarding guidance recommends "being explicit about versions and installation methods rather than letting the agent resolve them ad hoc, precisely to avoid unexpected versions" ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/onboarding-your-ai-peer-programmer-setting-up-github-copilot-coding-agent-for-success/)). Treat the image as production code:

- Pin base image digest, not tag — `ubuntu@sha256:...`, not `ubuntu:latest`
- Schedule rebuilds on a cadence that matches your dependency churn (weekly for stable stacks, daily for fast-moving)
- Gate rebuilds on dependency-lock changes so a security patch triggers a rebuild automatically

Stale images defeat the point: an agent running with outdated tooling produces output that diverges from what humans on the same repo see.

## Supply-Chain Burden

A custom image is a long-lived signed registry artifact. A `copilot-setup-steps.yml` install runs per-session and leaves no persistent artifact; a baked image is shared across every session pulled from the registry. Three new review surfaces:

- **Base image provenance** — who publishes it, signed by what key, scanned for what CVEs
- **Layer audit** — every `RUN` step that touches a secret leaves it in the layer history; secret leakage is an image-distribution leak, not a per-session leak
- **Registry trust** — pull from a registry whose access is gated by the same controls as the production deploy registry

If your team has no signed-registry pipeline or layer-scanning gate, the runtime-only path ([Agent Environment Bootstrapping](../workflows/agent-environment-bootstrapping.md)) is safer.

## When Not to Prebuild

- **Low dispatch volume** — when sessions are infrequent, the saved seconds per dispatch do not amortise the rebuild pipeline and image-review overhead. The benefit scales with dispatch frequency: the same per-session saving is a rounding error at one session per day and a meaningful fleet-wide gain at hundreds.
- **Rapidly-evolving toolchain** — pre-1.0 libraries or daily monorepo upgrades mean the image is stale before its next rebuild, and the agent runs against outdated tooling while developers see current versions.
- **No supply-chain review capacity** — without provenance review and signed registries, a custom image trades cold-start latency for amplified supply-chain risk.

## Example

A team that dispatches the Copilot cloud agent across many issues per day wants to compress cold start.

**Before** — runtime install via `copilot-setup-steps.yml`:

```yaml
jobs:
  copilot-setup-steps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
      - run: npm ci
      - run: npm install -g @company/internal-cli
```

Every session pays the `npm ci` and global install cost on the hot path before the agent runs its first tool call.

**After** — prebuilt custom image, runtime-only steps for dynamic work:

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

The `npm ci` step is gone from the hot path; what remains is the working-tree clone and a symlink. The image is rebuilt by a separate weekly workflow that scans the new layers and signs the resulting digest.

## Key Takeaways

- Prebuilt images compress cold start by shifting toolchain install from the hot path to a cached artifact — GitHub measured >20% startup improvement for Copilot cloud agent
- Bake stable runtimes, dependencies, and MCP servers; keep working tree, secrets, and ephemeral tokens dynamic
- Freshness is a discipline: pin base digests, rebuild on a cadence matched to dependency churn, gate on lock-file changes
- A custom image is a supply-chain artifact — base provenance, layer audit, and signed-registry pulls are now part of the agent's threat surface
- Skip this lever when dispatch volume is low, the toolchain churns weekly, or no signed-registry pipeline exists

## Related

- [Agent Environment Bootstrapping](../workflows/agent-environment-bootstrapping.md) — the runtime-side sibling: deterministic per-session setup via `copilot-setup-steps.yml`
- [Session Harness Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — the complementary lever: remove provisioning from the hot path entirely
- [Cursor Self-Hosted Cloud Agents](../tools/cursor/self-hosted-cloud-agents.md) — when the runner runs on your infra, image governance is yours end-to-end
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md) — the permissions surface that bounds what a baked image can reach
- [Long-Running Agents: Durability, Checkpoints, and Resumability](long-running-agents.md) — the operational shape that makes cold-start amortisation matter
