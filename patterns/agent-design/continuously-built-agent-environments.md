---
title: "Continuously Built Agent Environments"
term: "Continuously Built Agent Environments"
description: "Rebuild a cloud agent's environment in the background on a schedule and activate only builds that succeed, so each delegated task starts from a prepared snapshot instead of paying cold start."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - prebuilt cloud agent environments
  - environment build promotion
  - agent cold start tax
last_reviewed: 2026-09-02
maturity: emerging
---

# Continuously Built Agent Environments

> Continuously rebuild the agent environment in the background, promote only successful builds, and start every run from the last good one.

A continuously built agent environment is a prepared workspace snapshot that a platform rebuilds on its own schedule and activates only when the build succeeds. Cursor ships this as Builds, defined as "a bootable snapshot of a prepared Cloud Agent environment" ([Cursor Docs](https://cursor.com/docs/cloud-agents/builds)). The snapshot holds "repos cloned, dependencies installed, and the install script fully executed" ([Cursor](https://cursor.com/blog/builds)). Builds reached cloud agents on 2026-08-13, which takes the clone and install off the session's own clock ([Cursor Changelog, 2026-08-13](https://cursor.com/changelog/08-13-26)).

## When it pays

Three conditions have to hold before the pipeline earns its maintenance cost:

- Tasks are short and dispatch volume is high. Cold start is charged per delegated task, so setup time that disappears into a long refactor dominates the wall clock of a one-line fix.
- Rebuild cadence keeps pace with dependency churn. Cursor "runs a new build every hour" by default ([Cursor](https://cursor.com/blog/builds)), and a repo whose lockfiles move faster than that needs a tighter trigger.
- A run may legitimately start on a superseded environment. If it may not, use the fresh-provisioning path in [Agent Environment Bootstrapping](../../workflows/agent-environment-bootstrapping.md) instead.

## Three separable mechanisms

| Mechanism | What it does | Documented behavior |
|---|---|---|
| Background build | Runs clone and install off the hot path on a schedule, on config change, manually, or on agent request | "Cursor only skips recurring Builds. Manual, agent-requested, and configuration-change Builds always run" ([Cursor Docs](https://cursor.com/docs/cloud-agents/builds)) |
| Promotion gate | Activates a build only if it succeeded, so a failed build is never used | "agents continue to use the last successful Build" ([Cursor Docs](https://cursor.com/docs/cloud-agents/builds)) |
| Staleness dial | Pulls fresh default-branch code once a build passes an age threshold, default 24 hours, `0` for always fresh | Cursor's "Update stale builds" setting ([Cursor Docs](https://cursor.com/docs/cloud-agents/builds)) |

Per-run work does not disappear. Cursor keeps it on the `start` command: "Use it for services that must be fresh when the session begins, like bringing up Docker containers or other long-running processes" ([Cursor](https://cursor.com/blog/builds)). That boundary is the [Cloud-Agent Session Bootstrap](cloud-agent-session-bootstrap.md) split, moved one layer out.

Each run stays attributable to the environment that produced it. "Every agent run records the Build it started from. Use this provenance to compare environment behavior with the exact configuration and repository commits in the Build" ([Cursor Docs](https://cursor.com/docs/cloud-agents/builds)).

## Why it works

Cold start is a fixed cost that recurs with every delegated run, so it grows with dispatch volume while the work it enables does not. Cursor describes the old shape as "setting up the environment from scratch each session" ([Cursor](https://cursor.com/blog/builds)). Moving the clone and install into a background build converts that serial per-run cost into a periodic one, and every run in a build generation then reuses a single install. Two vendors measured the effect independently. Cursor reports that "our internal environments now boot 10x faster and time to first token is 3x faster" ([Cursor](https://cursor.com/blog/builds)), a figure drawn from its own repos rather than a general benchmark. GitHub found that "Copilot cloud agent now starts up over 20% faster, thanks to optimized runner environments built with GitHub Actions custom images" ([GitHub Changelog](https://github.blog/changelog/2026-04-27-copilot-cloud-agent-starts-20-faster-with-actions-custom-images/)).

The promotion gate works for a different reason. Gating activation on a successful build means a broken install never reaches a run, which changes the failure mode from "every agent breaks now" to "every agent runs on yesterday's environment until someone fixes it."

## When this backfires

- Long-running tasks. When the work itself dwarfs setup, the saved time is inside the noise and the pipeline buys nothing measurable.
- Correctness-sensitive breakage. The gate is explicit that sessions "keep running safely while you debug the environment in the background" ([Cursor](https://cursor.com/blog/builds)), so agents keep opening pull requests against a superseded toolchain and detection waits on whoever reads the notification.
- Churn faster than the dial. GitHub says the cheaper Codespaces prebuild triggers save Actions minutes but "codespaces may be created that do not use the latest dev container configuration changes" ([GitHub Docs](https://docs.github.com/en/codespaces/prebuilding-your-codespaces/configuring-prebuilds)). A 24-hour default is a full day of divergence.
- Metered storage at low volume. On Codespaces, "There is a storage cost associated with each prebuild version that's retained" ([GitHub Docs](https://docs.github.com/en/codespaces/prebuilding-your-codespaces/configuring-prebuilds)), billed per region. Cursor absorbing that cost is a pricing decision by one vendor, not a property of the technique.
- Shared identity. Runs started from one prepared image inherit its credentials, because "unique identifiers, cached random numbers, cryptographic tokens, etc will still be replicated across multiple microVMs resumed from the same snapshot" ([Firecracker](https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md)).

## Key Takeaways

- The build itself is the easy part; the promotion gate and the staleness dial are what you have to tune
- Treat published startup figures as scoped to the vendor's own repositories rather than as a result you will reproduce
- Last-known-good fallback trades a loud per-run failure for a background notification, which is a throughput win and a correctness risk
- Match the rebuild trigger to lockfile churn rather than accepting a latency-tuned default
- Track which build each run used, so a wrong result can be traced to the environment that produced it

## Related

- [Cloud-Agent Session Bootstrap](cloud-agent-session-bootstrap.md) — the install and start lifecycle split this layer sits above
- [Sandbox Forking: Branch Agent Runs From a Warm Snapshot](sandbox-forking.md) — copying a prepared snapshot per run, and the identity it replicates
- [Agent Environment Bootstrapping](../../workflows/agent-environment-bootstrapping.md) — the fresh-provisioning path when no prepared build is available
- [Session Harness Sandbox Separation](session-harness-sandbox-separation.md) — the architectural split that lets a run begin before its sandbox is ready
- [Cursor Self-Hosted Cloud Agents](../../tools/cursor/self-hosted-cloud-agents.md) — when the runner is yours, the build pipeline and its storage bill are yours too
