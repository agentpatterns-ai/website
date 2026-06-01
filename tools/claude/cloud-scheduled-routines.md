---
title: "Cloud-Scheduled Routines vs Local Session Scheduling"
description: "Move scheduled agent work to Anthropic-managed cloud infrastructure when the laptop being asleep or the local env drifting breaks the schedule — trade local-file fidelity and human-in-the-loop for continuity."
tags:
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-05-30
status: current
---

# Cloud-Scheduled Routines vs Local Session Scheduling

> Cloud-scheduled Routines run on Anthropic infrastructure — trade working-tree fidelity and mid-run permission gates for uptime continuity.

A [Routine](https://code.claude.com/docs/en/routines) is a saved Claude Code configuration — prompt, repos, connectors, environment — that executes on Anthropic-managed cloud infrastructure on a schedule, API call, or GitHub event. It is the cloud counterpart to in-session `/loop` and `CronCreate` ([Session Scheduling](session-scheduling.md)) and to local [Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks). The deployment-location choice is a clean trade: cloud fixes host-uptime and env-drift failures but breaks working-tree fidelity, the human-in-the-loop permission gate, and sub-hour cadence.

## The Decision Axis

The Claude Code docs ship a comparison table that maps the trade directly. [Source: [Compare scheduling options](https://code.claude.com/docs/en/scheduled-tasks#compare-scheduling-options)]

| Dimension | Cloud Routine | Desktop Task | `/loop` |
|---|---|---|---|
| Runs on | Anthropic cloud | Your machine | Your machine |
| Requires machine on | No | Yes | Yes |
| Requires open session | No | No | Yes |
| Access to local files | No — fresh clone of default branch | Yes — working tree included | Yes |
| Permission prompts | None — runs autonomously | Configurable per task | Inherits from session |
| Minimum interval | 1 hour | 1 minute | 1 minute |

Move scheduled work out of the local box when the local box is the failure point — laptops that sleep, reboots that drop cron, dev-env drift between runs, secrets that rotated since the last invocation. Keep it local when the work needs the current branch, sub-hour cadence, mid-run approvals, or local-only MCP servers and `localhost` resources.

## When to Choose Cloud

A cloud routine fits when **all** of the following hold:

- **Cadence is hourly or slower.** Cron expressions firing more often than every hour are rejected. [Source: [Add a schedule trigger](https://code.claude.com/docs/en/routines#add-a-schedule-trigger)]
- **Work runs against the default branch.** Each run clones the repo fresh from the default branch — in-flight feature work elsewhere is invisible unless the prompt checks it out. [Source: [Repositories and branch permissions](https://code.claude.com/docs/en/routines#repositories-and-branch-permissions)]
- **No mid-run human approval is needed.** Routines run autonomously; reachability is fixed at creation by repos, environment policy, env vars, and connectors. [Source: [Create a routine](https://code.claude.com/docs/en/routines#create-a-routine)]
- **All required resources are reachable from the cloud environment.** The Default environment's Trusted allowlist covers common package registries, cloud APIs, and dev domains; arbitrary hosts return `403`. Local stdio MCP servers added via `claude mcp add` are not visible — re-add them as claude.ai connectors or declare them in a committed `.mcp.json`. [Source: [Environments and network access](https://code.claude.com/docs/en/routines#environments-and-network-access), [Connectors](https://code.claude.com/docs/en/routines#connectors)]

Backlog grooming against a hosted tracker, weekly docs-drift sweeps, GitHub-event-driven PR reviews, and webhook-triggered deploy verification all fit. [Source: [Example use cases](https://code.claude.com/docs/en/routines#example-use-cases)]

## When This Backfires

- **Working-tree drift.** A scheduled audit reading `STANDARDS.md` from `main` does not see the unmerged edit on your feature branch. The cloud snapshot is what was on the default branch at clone time.
- **Sub-hour cadence is impossible.** Queue-depth checks, build-status polling, and deploy-window verification need minute granularity. The 1-hour floor forces a hybrid local+cloud setup, doubling the failure surface.
- **Identity collapse.** Routines act as the creator on every connector and on GitHub — commits, PRs, Slack messages, and Linear tickets carry one person's name. Scheduling under one engineer's account creates single points of attribution, departure, and credential compromise. [Source: [Create a routine](https://code.claude.com/docs/en/routines#create-a-routine)]
- **Autonomous-run trifecta.** A routine combining a private-data connector, an untrusted-input source (web fetch, issue bodies), and an egress connector (push, Slack) closes the [Lethal Trifecta](../../security/lethal-trifecta-threat-model.md) — and runs with no prompts to interrupt the chain. An injected instruction in a fetched URL produces an immediate write under the creator's identity. The [confirmation-gate](../../security/human-in-the-loop-confirmation-gates.md) posture cannot apply: no human-in-the-loop surface exists during a run.
- **Quota competition.** Routines share subscription usage with interactive sessions and carry an additional daily run cap. One-off runs are exempt from the cap but still draw down subscription usage. [Source: [Usage and limits](https://code.claude.com/docs/en/routines#usage-and-limits)]
- **Local resources are unreachable.** `localhost` services, local databases, and VPN-only internal endpoints are invisible unless re-exposed.

## Why It Works

Cloud scheduling decouples the run from the local host. The two dominant failure modes of local scheduled work — host sleep/reboot and local-env drift between invocations — disappear because the execution environment is always on and its state is explicit: a cached setup script, declared env vars, and a per-routine connector list. [Source: [Select an environment](https://code.claude.com/docs/en/routines#create-a-routine)]

The cost is that "always on" plus "no permission prompts" plus "acts as the creator" closes new failure surfaces. The configured-at-creation snapshot can drift from the local working tree, and the autonomous posture means a prompt-injection vector in a fetched source produces immediate writes under the creator's identity. The trade is clean — uptime continuity and explicit-env reproducibility in exchange for working-tree fidelity and mid-run human gates.

## Risk-Reduction Posture

When the decision lands on cloud, three settings shrink the blast radius:

- **Keep the default `claude/`-prefixed branch restriction.** Only enable **Allow unrestricted branch pushes** per repo when the routine genuinely needs to write a long-lived branch. [Source: [Repositories and branch permissions](https://code.claude.com/docs/en/routines#repositories-and-branch-permissions)]
- **Trim the connector list per routine.** All currently-connected claude.ai connectors are included by default; every included connector is callable end-to-end with no per-tool prompt. Remove anything the routine does not need. [Source: [Create a routine](https://code.claude.com/docs/en/routines#create-a-routine)]
- **Keep the network policy at Trusted.** Widen to Custom or Full only when the prompt fails on a `403`; the change is per-environment and inherited by every routine using it. [Source: [Environments and network access](https://code.claude.com/docs/en/routines#environments-and-network-access)]

## Example

A weekly dependency-audit routine fits cloud cleanly. A hotfix loop watching CI on a feature branch does not.

**Cloud-suited** — weekly dependency audit:

```text
/schedule weekly on Monday at 9am, review the dependency manifests in
agentpatterns-ai/content for new CVEs against pinned versions and open a
claude/dep-audit-<date> PR with proposed bumps.
```

Runs against `main`, well under the 1-hour floor, no mid-run approvals, all sources (npm, PyPI advisory feeds) are on the Trusted allowlist, the autonomous PR posture is the point.

**Local-suited** — hotfix loop on the current feature branch:

```text
/loop 5m check whether CI passed on this branch — if it failed, pull the
failing job log and propose a minimal fix
```

Needs the current branch (cloud only sees `main`), needs 5-minute granularity (cloud floor is 1 hour), benefits from in-session permission prompts on the `git push` step.

## Key Takeaways

- The deployment-location axis is a clean trade: cloud fixes host-uptime and env-drift; local preserves working-tree fidelity, sub-hour cadence, and mid-run approval.
- Cloud routines are the right tool only when cadence is hourly or slower, work runs against the default branch, no mid-run human gate is needed, and all resources are reachable from the cloud environment.
- The autonomous-run posture closes the [Lethal Trifecta](../../security/lethal-trifecta-threat-model.md) instantly if a routine combines a private-data connector, an untrusted-input source, and an egress connector — trim the connector list and keep the branch-push restriction.
- Cloud routines act as the creator on every connector and on GitHub. Single-user attribution and credential concentration are intrinsic to the model — plan around them.

## Related

- [Session Scheduling](session-scheduling.md) — local `/loop` and `CronCreate`; the in-session counterpart this page contrasts with
- [Channels Permission Relay](channels-permission-relay.md) — local equivalent of the "always-on + remote approvals" half of routines, for cases where local cadence wins but unattended approvals are still needed
- [Lethal Trifecta Threat Model](../../security/lethal-trifecta-threat-model.md) — the security frame for any autonomous unattended agent run, cloud or local
- [Human-in-the-Loop Confirmation Gates](../../security/human-in-the-loop-confirmation-gates.md) — the gate pattern cloud routines explicitly disable; necessary context for what the trade gives up
- [Cloud/Local Agent Handoff](../../workflows/cloud-local-agent-handoff.md) — the broader handoff workflow when a task crosses the deployment-location boundary mid-execution
