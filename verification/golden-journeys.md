---
title: "Golden Journeys: Restartability as a First-Class Verification Primitive"
description: "Name a small set of end-to-end paths through the running system, each with an explicit failure signal per step, and gate completion on the system restarting cleanly afterward."
tags:
  - testing-verification
  - agent-design
  - workflows
  - tool-agnostic
  - harness-engineering
last_reviewed: 2026-06-03
---

# Golden Journeys: Restartability as a First-Class Verification Primitive

> Golden Journeys are named end-to-end paths through the running system, each with a per-step failure signal, gating completion on a clean restart.

## The Pattern

A Golden Journey is a named, repeatable path through the running system with an explicit failure signal at each step, treated as the canonical verification artefact. The governing rule from the Walking Labs reliability framework: **"No feature is complete if the system cannot restart cleanly afterward"** ([RELIABILITY.md](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/en/resources/openai-advanced/repo-template/docs/RELIABILITY.md)).

Each journey lists four fields:

- **Start command** — exact invocation that boots the surface from cold
- **User-visible steps** — what the operator or test driver does, in order
- **Observable end state** — what the system shows when the journey completes
- **Failure signal per step** — the specific log line, screen state, or process exit code that means "this step did not work"

The restart-clean rule turns the journey into a completion gate, not a smoke test afterthought. A feature passes its unit and integration tests but leaves a corrupt cache, a half-applied migration, or a stuck background worker — under this rule, it is not done.

## Not the Same as Happy Path Testing

Two name collisions matter. "Happy path" testing covers the nominal flow with no errors ([Wikipedia: Happy path](https://en.wikipedia.org/wiki/Happy_path)); "golden path" in platform engineering means a paved-road developer workflow ([Red Hat: Golden Paths](https://www.redhat.com/en/topics/platform-engineering/golden-paths)). Golden Journeys are neither. They add two constraints that happy-path tests do not enforce: a per-step failure signal that is specific enough to grep for, and a hard restart-clean completion criterion.

## Failure Signal Specificity

"Test fails" is not a failure signal. "Request to `/index` returns 500 with body containing `chunk size <= 0`" is. The rule mirrors observability practice — semantic exit codes and grep-friendly log lines are what make failure diagnosable from repo-local signals without spelunking through a trace UI ([Square: Command Line Observability with Semantic Exit Codes](https://developer.squareup.com/blog/command-line-observability-with-semantic-exit-codes/)).

Specific signals also defeat agent rubber-stamping. An agent that can read "exit code 137" and look it up will diagnose an OOM kill; an agent that sees "tests failed" will retry the same change.

## Representative, Not Exhaustive

Maintain 3 to 7 journeys per app surface. Representative coverage is the goal, not exhaustive coverage. The journey list is the smallest set that, if all pass and the system restarts clean, you would ship.

## Pairing with feature_list.json

Golden Journeys plug into the same completion-gate stack as [feature list files](../instructions/feature-list-files.md) and [pre-completion checklists](pre-completion-checklists.md). A feature's `verification` field can cite the Golden Journey it exercises; the pre-completion checklist runs the journey and checks the restart; the feature list flips to `passing` only when both pass.

## Example

A `feature_list.json` entry referencing its journey, and the journey itself in a project-local `RELIABILITY.md`:

```json
{
  "id": "feature-42",
  "description": "Index endpoint serves search results from warm cache",
  "status": "failing",
  "verification": "golden-journey:index-search",
  "acceptance_criteria": [
    "GET /index returns 200 within 200ms after warm cache",
    "System restarts clean after journey completes"
  ]
}
```

```markdown
## Golden Journey: index-search

**Start command**: `make run`

1. Operator visits `/index`
   - Failure signal: response status != 200, or body contains `chunk size <= 0`
2. Operator submits search query `"agent harness"`
   - Failure signal: log line `ERROR retrieval timeout` within 5s, or empty result page
3. Operator stops the service: `make stop`
   - Failure signal: exit code != 0, or stale lockfile in `./var/run/`
4. Operator restarts: `make run`
   - Failure signal: log line `ERROR startup` or HTTP probe to `/healthz` returns != 200 within 30s
```

## When This Backfires

- **Long-startup systems** — multi-minute model warm-up, large index loads, or migration-heavy databases pay the restart-clean cost on every PR cycle; either CI time balloons or the gate becomes nominal
- **Stateless or trivial systems** — a CLI tool with no persistent state has nothing meaningful to restart cleanly from; naming journeys produces ceremony without test signal
- **Pre-product-market-fit prototypes** — the surface changes faster than the documented journeys can be maintained; the journey list goes stale and stops catching drift
- **Mature observability already in place** — when distributed tracing and on-call dashboards already encode the critical paths, Golden Journeys re-encode information that exists elsewhere

## Key Takeaways

- Golden Journeys are a completion-gate artefact, not a flavour of end-to-end testing
- The load-bearing claim is the restart-clean rule — a feature is not done if the system cannot restart cleanly afterward
- Each step must have a specific failure signal (log line, exit code, screen state) — "fails" is not a signal
- Maintain a representative set of 3 to 7 journeys per surface; exhaustive coverage is the wrong goal
- Pair journeys with `feature_list.json` entries and pre-completion checklists so the gate runs in the same stack as other completion criteria

## Related

- [Feature List Files](../instructions/feature-list-files.md) — the structured contract a Golden Journey cites in its `verification` field
- [Pre-Completion Checklists](pre-completion-checklists.md) — the gate that runs the journey and the restart check before a task is declared done
- [Runnable Documentation as Agent Verification](runnable-documentation.md) — adjacent pattern for promoting implicit verification artefacts to CI-enforced ones
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — hard CI checks as the enforcement layer for journey signals
