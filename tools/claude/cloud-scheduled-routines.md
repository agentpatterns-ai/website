---
title: "Cloud-Scheduled Routines vs Local Session Scheduling"
description: "Move scheduled agent work to Anthropic-managed cloud infrastructure when the laptop being asleep or the local env drifting breaks the schedule — trade local-file fidelity and human-in-the-loop for continuity."
tags:
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-06-03
status: current
---

# Cloud-Scheduled Routines vs Local Session Scheduling

> Cloud-scheduled Routines run on Anthropic infrastructure — trade working-tree fidelity and mid-run permission gates for uptime continuity.

A [Routine](https://code.claude.com/docs/en/routines) is a saved Claude Code configuration — prompt, repos, connectors, environment — that executes on Anthropic-managed cloud infrastructure on a schedule, API call, or GitHub event. It is the cloud counterpart to in-session `/loop` and `CronCreate` ([Session Scheduling](session-scheduling.md)) and to local [Desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks). The deployment choice is a clean trade: cloud fixes host-uptime and env-drift failures but breaks working-tree fidelity, the permission gate, and sub-hour cadence.

## The decision axis

The Claude Code docs ship a comparison table that maps the trade directly. [Source: [Compare scheduling options](https://code.claude.com/docs/en/scheduled-tasks#compare-scheduling-options)]

| Dimension | Cloud Routine | Desktop Task | `/loop` |
|---|---|---|---|
| Runs on | Anthropic cloud | Your machine | Your machine |
| Requires machine on | No | Yes | Yes |
| Requires open session | No | No | Yes |
| Access to local files | No — fresh clone of default branch | Yes — working tree included | Yes |
| Permission prompts | None — runs autonomously | Configurable per task | Inherits from session |
| Minimum interval | 1 hour | 1 minute | 1 minute |

Move scheduled work to the cloud when the local box is the failure point — laptops that sleep, reboots that drop cron, dev-env drift, secrets that rotated since the last run. Keep it local when the work needs the current branch, sub-hour cadence, mid-run approvals, or local-only MCP servers and `localhost` resources.

## When to choose cloud

A cloud routine fits when all of the following hold:

- Cadence is hourly or slower. Cron expressions that fire more often than every hour are rejected. [Source: [Add a schedule trigger](https://code.claude.com/docs/en/routines#add-a-schedule-trigger)]
- Work runs against the default branch. Each run clones the repo fresh from the default branch, so in-flight feature work is invisible unless the prompt checks it out. [Source: [Repositories and branch permissions](https://code.claude.com/docs/en/routines#repositories-and-branch-permissions)]
- No mid-run human approval is needed. Routines run on their own. Repos, environment policy, env vars, and connectors fix what a run can reach at creation time. [Source: [Create a routine](https://code.claude.com/docs/en/routines#create-a-routine)]
- All required resources are reachable from the cloud environment. The Default environment's Trusted allowlist covers common package registries, cloud APIs, and dev domains; other hosts return `403`. Local stdio MCP servers added with `claude mcp add` are not visible, so re-add them as claude.ai connectors or declare them in a committed `.mcp.json`. [Source: [Connectors](https://code.claude.com/docs/en/routines#connectors)]

Backlog grooming against a hosted tracker, weekly docs-drift sweeps, GitHub-event-driven PR reviews, and webhook-triggered deploy verification all fit. [Source: [Example use cases](https://code.claude.com/docs/en/routines#example-use-cases)]

## When this backfires

- Working-tree drift. A scheduled audit that reads `STANDARDS.md` from `main` does not see the unmerged edit on your feature branch. The cloud snapshot is the default branch at clone time.
- Sub-hour cadence is impossible. Queue-depth checks, build-status polling, and deploy-window verification need minute granularity. The 1-hour floor forces a hybrid local-and-cloud setup, which doubles the failure surface.
- Identity collapse. Routines act as the creator on every connector and on GitHub. Commits, PRs, Slack messages, and Linear tickets all carry one person's name, which creates single points of attribution, departure, and credential compromise. [Source: [Create a routine](https://code.claude.com/docs/en/routines#create-a-routine)]
- Autonomous-run trifecta. A routine that combines a private-data connector, an untrusted-input source (web fetch, issue bodies), and an egress connector (push, Slack) closes the [Lethal Trifecta](../../security/lethal-trifecta-threat-model.md) with no prompts to interrupt the chain. An injected instruction in a fetched URL produces an immediate write under the creator's identity. The [confirmation-gate](../../security/human-in-the-loop-confirmation-gates.md) posture cannot apply, because no human-in-the-loop surface exists during a run.
- Quota competition. Routines share subscription usage with interactive sessions and carry an extra daily run cap. One-off runs are exempt from the cap but still draw down subscription usage. [Source: [Usage and limits](https://code.claude.com/docs/en/routines#usage-and-limits)]
- Local resources are unreachable. `localhost` services, local databases, and VPN-only internal endpoints are invisible unless you re-expose them.

## Why it works

Cloud scheduling decouples the run from the local host. The two main failure modes of local scheduled work disappear: host sleep or reboot, and local-env drift between runs. The execution environment is always on, and its state is explicit, captured in a cached setup script, declared env vars, and a per-routine connector list. That same "always on, no prompts, acts as creator" posture is what opens the failure surfaces above. [Source: [Select an environment](https://code.claude.com/docs/en/routines#create-a-routine)]

## Risk-reduction posture

When the decision lands on cloud, three settings shrink the damage a bad run can do:

- Keep the `claude/`-prefixed branch restriction. Turn on **Allow unrestricted branch pushes** per repo only when the routine needs a long-lived branch. [Source: [Repositories and branch permissions](https://code.claude.com/docs/en/routines#repositories-and-branch-permissions)]
- Trim the connector list. Every connected claude.ai connector is included by default and callable with no per-tool prompt, so remove anything the routine does not need. [Source: [Create a routine](https://code.claude.com/docs/en/routines#create-a-routine)]
- Keep the network policy at Trusted. Widen to Custom or Full only when the prompt fails on a `403`. The change is per-environment and inherited by every routine that uses it. [Source: [Environments and network access](https://code.claude.com/docs/en/routines#environments-and-network-access)]

## Example

A weekly dependency-audit routine fits cloud cleanly. A hotfix loop watching CI on a feature branch does not.

Cloud-suited, a weekly dependency audit:

```text
/schedule weekly on Monday at 9am, review the dependency manifests in
agentpatterns-ai/content for new CVEs against pinned versions and open a
claude/dep-audit-<date> PR with proposed bumps.
```

Runs against `main`, well under the 1-hour floor, no mid-run approvals, all sources (npm, PyPI advisory feeds) are on the Trusted allowlist, the autonomous PR posture is the point.

Local-suited, a hotfix loop on the current feature branch:

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
