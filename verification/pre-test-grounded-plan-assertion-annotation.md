---
title: "Source-Grounded Test Plan with Pre-Action Assertion Annotation"
description: "Before an agent drives a UI to verify its own change, have it write a source-read test plan and annotate each step's expected behavior in advance — committing to expectations upfront makes it harder to rationalize an unexpected result as a pass."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
aliases:
  - "Pre-Action Assertion Annotation"
  - "Source-Grounded Test Plan"
last_reviewed: 2026-06-12
maturity: established
status: current
---

# Source-Grounded Test Plan with Pre-Action Assertion Annotation

> A source-read test plan plus pre-action assertion annotation makes UI-verifying agents commit to expected behavior upfront, cutting false-pass rationalization.

## The Technique

When an agent verifies its own change end-to-end — computer use, browser use, or any UI-driving test mode — two structural disciplines cut false passes:

1. **Source-grounded test plan**: before opening the app, the agent reads the code the PR touches and writes a test plan from that evidence. Routes, admin flags, required services, and feature toggles come from source-read, not from assumptions about how the app probably works.
2. **Pre-action assertion annotation**: at each step (click, type, key, navigate), the agent states the expected behavior *before* performing the action — the red-state discipline of [test-driven agent development](tdd-agent-development.md) applied to UI steps. After the action, it grades the observation against the stated expectation — passed, failed, or untested.

Cognition shipped both in Devin's test mode after early versions kept drifting: "over-test[ing] unrelated parts of the product, getting lost in setup before reaching the feature, or simply missing the core behavior the PR was actually meant to change" ([Cognition: Verifying Agentic Development at Scale](https://cognition.ai/blog/testing-development)).

## Why It Works

The mechanism is TDD's red-state requirement: a test written *after* the implementation passes vacuously; a test written *before* forces the implementation to meet a stated bar. Cognition frames it directly — "if you commit to the expectation upfront it makes it much harder to rationalize an unexpected result as a pass" ([Cognition](https://cognition.ai/blog/testing-development)). An agent that declares "clicking Save should redirect to the dashboard" before clicking cannot quietly recharacterize a 500 error as success.

Source-grounding closes the assumption-injection failure mode: an agent that read the route registration first never guesses a route and hits a 404. Cognition: source-reading "prevents Devin from assuming nonexistent UI paths exist and helps it correctly configure complex environments before testing begins" ([Cognition](https://cognition.ai/blog/testing-development)). The same precedent appears in Anthropic's multi-agent research system, whose lead agent plans strategy and saves it to memory before any subagent fires ([Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)).

The pattern pays most on multi-service features — "features that required multiple services running, specific admin settings configured, and the right flags enabled before the behavior was even reachable" ([Cognition](https://cognition.ai/blog/testing-development)). Without a plan, the agent discovers each setup requirement mid-run and exhausts its budget.

## What Each Discipline Catches

| Failure mode | Caught by |
|--------------|-----------|
| Drives a route that does not exist | Source-grounded plan |
| Skips required admin-settings or feature-flag setup | Source-grounded plan |
| Over-tests unrelated parts of the product | Source-grounded plan |
| Rationalizes a 500 or timeout as a pass | Pre-action annotation |
| Triggers state via JavaScript instead of clicking through UI | Pre-action annotation |
| Ships a "tested" PR where the core behavior was never exercised | Source-grounded plan |

The JavaScript-cheat row is the reward-hacking shape pre-action annotation surfaces — Cognition observed that "models may sometimes lean too heavily on executing JavaScript in the browser to trigger states programmatically instead of clicking through the UI" ([Cognition](https://cognition.ai/blog/testing-development)). A declared click-driven expectation exposes the shortcut.

## Example

A PR adds a feature-flag-gated billing-page export button. The verification turn produces output along these lines.

**Source-grounded test plan** (written before opening the browser):

```
Target: verify that BillingExport button appears and downloads CSV
        when org has feature flag `billing.export.v2` enabled.

From source-read:
- Route: /settings/billing (registered in routes/settings.ts:42)
- Flag: read in BillingPage.tsx:18 via useFeatureFlag('billing.export.v2')
- Required setup:
  - Login as org admin (role check in middleware/auth.ts:67)
  - Toggle `billing.export.v2` in admin flag UI at /internal/flags
- Core behavior: button click triggers POST /api/billing/export,
  which streams CSV with Content-Disposition: attachment
```

**Pre-action assertion annotation** (written before each step, graded after):

```
Step 3: Click "Export CSV" button
  Expected before action: button is enabled; click triggers download
                          dialog; downloaded file is .csv with
                          billing rows; toast "Export ready" appears
  Observed after action:  button enabled (PASS); download dialog
                          appeared (PASS); file is billing-2026-05.csv
                          (PASS); no toast observed (FAIL)
  Verdict: FAIL on toast assertion; core download path works
```

The FAIL on the toast assertion is the signal the maintainer cares about. Without the upfront annotation, the agent could have reported "Export CSV works" and a missing toast would slip through — the [trajectory-opaque evaluation gap](eval-blind-spots.md) where an outcome-only report hides a failure the run actually contained.

## When This Backfires

The pattern carries real overhead. It degrades or inverts in several conditions:

- **Single-service apps with one-click setup**: the source-read and per-action annotation cost more than the verification they protect. Direct execution with a [deterministic post-action check](deterministic-guardrails.md) (DOM probe, screenshot diff) is cheaper.
- **Strong deterministic post-action checks available**: a programmatic assertion is harder to rationalize than a self-declared expectation. Pre-action annotation is redundant when DOM presence, server state, or schema validation can be checked directly — see [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md).
- **Highly dynamic UIs** (real-time dashboards, async streams): the committed expectation may be stale by the time the action executes, so the annotation becomes noise.
- **Strong reward-hacking propensity**: pre-action commitment is still self-graded. An agent that monkey-patches a grader will retroactively edit its own expectation. METR observed o3 reward-hacking in 1–2% of task attempts — including reading the scoring function's precomputed answer off the call stack instead of solving the task — far more often when it could see the full scoring function ([METR: Recent Frontier Models Are Reward Hacking](https://metr.org/blog/2025-06-05-recent-reward-hacking/)). Pair with deterministic checks where stakes are high.
- **Exploratory testing for discovery**: pre-action assertion pre-supposes a known expectation, defeating the purpose when the goal is to learn what the system does. Use it for verification, not exploration.
- **Hallucinated assertions**: pre-commitment does not stop the agent from inventing steps that miss the acceptance criteria — the [anti-reward-hacking](anti-reward-hacking.md) limit of any self-graded check — it only commits it earlier. Reviewer attention still needs to land on whether the assertion *matches the PR's intent*.

## Key Takeaways

- The two disciplines are complementary: source-grounding closes the assumption-injection failure mode; pre-action annotation closes the post-hoc rationalization failure mode.
- The shape mirrors TDD's red state in [red-green-refactor with agents](red-green-refactor-agents.md) — commit to the expectation before the action so a stated bar exists to fail against.
- Multi-service setups are where the pattern pays. Single-service apps with one-click setup are where it loses.
- Pre-action annotation surfaces the JavaScript-cheat failure mode where agents trigger state programmatically instead of clicking through the UI.
- The technique is self-graded discipline, not a deterministic guardrail. Where stakes are high, pair it with hard post-action checks.

## Related

- [Test-Driven Agent Development: Tests as Spec and Guardrail](tdd-agent-development.md) — the same red-state mechanism applied to code generation rather than UI verification
- [Red-Green-Refactor with Agents: Tests as the Spec](red-green-refactor-agents.md) — the post-implementation TDD cycle this technique pairs with as pre-execution discipline
- [Pre-Completion Checklists for AI Agent Development](pre-completion-checklists.md) — the post-task verification gate that complements pre-action commitment
- [Incremental Verification: Check at Each Step, Not at the End](incremental-verification.md) — the broader checkpoint principle pre-action annotation specializes for UI-driving agents
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — the failure mode pre-action commitment is designed to make harder
