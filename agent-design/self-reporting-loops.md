---
title: "Self-Reporting Loops: Autonomous Routines That File Their Own Backlog"
term: "Self-Reporting Loops"
description: "Scheduled and autonomous agent runs treat out-of-scope observations as a first-class output, filing them as deduplicated backlog items so the signal survives the session boundary."
tags:
  - agent-design
  - workflows
  - observability
  - tool-agnostic
aliases:
  - autonomous routine backlog filing
  - self-filing agent observations
last_reviewed: 2026-06-12
---

# Self-Reporting Loops: Autonomous Routines That File Their Own Backlog

> Scheduled and autonomous agent runs file out-of-scope observations to the team's tracker so the signal survives the session boundary instead of dying in a transcript.

## When This Applies

A self-reporting loop is only worth wiring when three preconditions hold. Skipping any one turns the pattern into spam:

- **The tracker is a trusted, queryable substrate.** When engineers already route real work through Slack threads or empty status fields, agent-filed issues land where no one reads. Linear's CEO argued in March 2026 that human ticket ceremony is dying ([MindStudio summary](https://www.mindstudio.ai/blog/cursor-research-100-agents-parallel-flat-agent-teams-issue-tracker)); the rebuttal — that the *substrate* matters more — only holds when state inside it is current.
- **The routine fingerprints and dedupes before filing.** GitHub Agentic Workflows defaults to filing an issue for every no-op run and every fallback, then documents how to disable both with `noop: report-as-issue: false` and `fallback-as-issue: false` ([announcement](https://github.blog/changelog/2026-06-11-github-agentic-workflows-is-now-in-public-preview/)). That opt-out exists because filing-on-every-run is noisy by default. Search-before-create and update-existing-on-recurrence prevent a flaky CI step from spawning twenty-four duplicate issues a day.
- **Severity routing separates blockers from improvements.** Blockers surface on a notification path; improvements queue silently. A single uniform-priority channel collapses both signals into noise.

## The Discipline

Treat every routine run as a sensor whose observations must be externalized before the session ends. MACONA's production [Sense Before Act discipline](https://www.fabswill.com/blog/sense-before-act-four-artifacts-every-agent-iteration/) ships four required artifacts every iteration — Sensor Roll Call, Conflict Receipt, Gap Map, Cross-Source Dedup — emitted *before* any decision. The Gap Map names what the run did not check this iteration and how the policy stage compensates; the Conflict Receipt names disagreements between sources. Silent omission of any sensor is forbidden, because "we did not see anything" is exactly the failure mode the discipline exists to prevent.

The structured filing contract carries forward to the issue body. Each agent-filed backlog item should encode three fields a later reader needs to act without re-deriving context:

1. **What was observed** — the raw signal, with the timestamp and the sensor that produced it.
2. **Run context** — routine name, run ID, link to the transcript or trace.
3. **Suggested next action** — the agent's classification of the finding (in-scope fix, out-of-scope improvement, environmental gap) so a downstream agent or human can route it.

Anthropic's [Code Review system](https://alphasignalai.substack.com/p/anthropic-releases-code-review-that) layers a verification step on top of this: every finding is re-examined to prove or disprove it, with false positives filtered before the issue is filed. That discipline is what keeps the tracker from becoming a write-only sink.

## Why It Works

Routines file backlog because observations are time-limited evidence; the tracker is the only durable surface that survives the session boundary. Cursor's research on 100 parallel agents found that flat agent organizations rediscover the same coordination failures as flat human orgs — locks held too long, blockers invisible — and that an issue tracker with claiming, status, and dependencies fixes both ([MindStudio summary](https://www.mindstudio.ai/blog/cursor-research-100-agents-parallel-flat-agent-teams-issue-tracker)). OpenAI's Symphony spec wires Linear in as the *control plane* for autonomous Codex agents; some internal teams reported a 500% increase in landed pull requests under that model ([same MindStudio analysis](https://www.mindstudio.ai/blog/cursor-research-100-agents-parallel-flat-agent-teams-issue-tracker)). The improvement did not come from a better agent — it came from giving the system a shared, durable map of work. MACONA's Sense Before Act formalizes the same mechanism at iteration granularity: a gap that is not externalized is silently lost. The active ingredient is *state externalization*, not "more agents."

## When This Backfires

- **The tracker is already a graveyard.** If your team works around the tracker today, agent-filed issues compound the problem rather than solve it. Fix the substrate first.
- **No deduplication.** The 4M to 17M jump in agentic PR volume between September 2025 and March 2026 — with field reports that roughly one in ten is legitimate ([context in the issue-tracker dispatch page](../workflows/issue-tracker-agent-dispatch-surface.md)) — is the same risk surface that applies to filed issues. A routine without fingerprinting floods the backlog.
- **Small-team scale.** When one engineer reviews every routine run within the hour, the transcript IS the durable surface and structured filing is overhead. The payoff scales with the gap between routine cadence and human review cadence.
- **Sub-frontier classification.** The routine has to decide "is this in-scope (fix now) versus out-of-scope (file it)." A weak classifier mis-routes both ways and pollutes both queues.
- **Side-channel substitute.** Routing observations to a fenced low-priority queue (a JSONL file, a draft-issue label) is the steelman counter-position when the team distrusts agent-filed work in the main tracker. It preserves externalization but adds a human promotion step — useful as a transitional posture, not a permanent end state.

## Example

A `/loop` routine runs every six hours to refresh stale citations in documentation. On the third run, it encounters a flaky web fetch against a vendor's docs subdomain — the routine's own job is citation refresh, not vendor monitoring. Instead of retrying silently and moving on, the routine:

1. Records the failure in the run's Sensor Roll Call (timestamp, URL, response code).
2. Searches the tracker for an open issue with the fingerprint `flaky-fetch:vendor-docs`.
3. On a hit, posts a comment with the new run ID and bumps a recurrence counter. On a miss, files an issue with the structured body:

```markdown
**Observed**: vendor-docs.example.com returned 503 on 4 of 12 requests
**Run context**: routine=citation-refresh, run=2026-06-12T14:32, transcript=...
**Suggested action**: out-of-scope — vendor reliability issue, route to platform team
**Recurrence**: first occurrence
```

The citation refresh routine continues its bounded job. The vendor-reliability backlog item is now durable state a platform-team agent or human can act on independently.

## Key Takeaways

- Routines compound only when out-of-scope observations are externalized to a queryable substrate, not buried in transcripts
- The pattern requires three preconditions — trusted tracker, deduplication discipline, severity routing — before it produces signal instead of noise
- Structured filing contract (observation, run context, suggested action) is what lets a downstream agent or human act without re-deriving context
- Default-on issue creation (GitHub Agentic Workflows' noop and fallback behavior) is noisy by design — disable it unless you have dedup
- The mechanism is state externalization, not more agents; an agent without a durable substrate inherits all the failures of a flat human org

## Related

- [Issue-Tracker as Agent Dispatch Surface](../workflows/issue-tracker-agent-dispatch-surface.md) — the consumer side: how a coding agent picks up the items a self-reporting loop files
- [Agentic Flywheel: Self-Improving Agent Systems](agentic-flywheel.md) — closes the loop by feeding filed observations back into harness improvements
- [Observability-Driven Harness Evolution](observability-driven-harness-evolution.md) — predict-then-verify discipline for the harness edits that filed backlog items eventually motivate
- [Continuous Agent Improvement](../workflows/continuous-agent-improvement.md) — the observation-to-update workflow that consumes self-reported backlog items
- [QA Session to Issues Pipeline](../workflows/qa-session-to-issues-pipeline.md) — sibling pattern for the inbound-document side of the same substrate
