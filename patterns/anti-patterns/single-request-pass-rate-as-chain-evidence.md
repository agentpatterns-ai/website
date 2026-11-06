---
title: "Single-Request Pass Rates as Evidence for Chained Delegation"
term: "Single-Request Pass Rate as Chain Evidence"
description: "On average, ten coding agents completed 95% of requests one at a time and 51% chained. The gap came from mistakes nobody checked between requests, not from worse code."
tags:
  - anti-pattern
  - tool-agnostic
  - arxiv
aliases:
  - built on broken assumptions
  - per-request score as chain reliability
  - unattended request chains
last_reviewed: 2026-11-05
maturity: emerging
---

# Single-Request Pass Rates as Evidence for Chained Delegation

> On average, ten coding agents completed 95% of requests one at a time and 51% chained, because later requests built on mistakes nobody checked.

The anti-pattern is reading a per-request pass rate as evidence that an agent can run a chain of dependent requests unattended. It applies when no external check sits between one request and the next. Cuadron and Gupta built 280 chains of 20 consecutive requests from 140 Python repositories and ran ten agents on them ([Cuadron and Gupta, 2026](https://arxiv.org/abs/2611.02207v1)). They report that "On average, they complete 95% of requests taken one at a time, but when requests are chained together, they complete 51%."

Inside the chains, the same agents complete 66–84% of individual requests at the step they are issued. Only 39% of chains finish with no request missed and no earlier test broken ([Cuadron and Gupta, 2026](https://arxiv.org/abs/2611.02207v1)).

## What the gap is made of

The authors separated who wrote the code from whether anyone checked it. "Once checked, agent code is nearly as good a base for later requests as human code." The loss comes from unverified mistakes: "The next request then builds on broken code and fails about twice as often" ([Cuadron and Gupta, 2026](https://arxiv.org/abs/2611.02207v1)). Mistakes are rarely repaired later. Only 14-33% of the tests that fail are ever repaired ([Cuadron and Gupta, 2026](https://arxiv.org/abs/2611.02207v1)).

Two checks that look like substitutes do not work in this setting:

- The agent's own tests. Agents ran a test runner before 97% of submissions, yet "submissions preceded by a passing run fail their request's hidden contract 8.3% of the time against 8.6% for all submissions."
- Another agent as reviewer. "Asked whether an implementation is correct, they are right 53% of the time, barely better than a coin flip."

Changing the harness did not close the gap either. Under Codex CLI, the OpenHands SDK, and pi, four models completed no more chains than under mini-swe-agent ([Cuadron and Gupta, 2026](https://arxiv.org/abs/2611.02207v1)).

## Why it works

The agent checks its work against its own reading of the request. The paper puts it as "The agents test what they wrote, not what was asked; a passing run of their own tests is what makes them believe a request complete" ([Cuadron and Gupta, 2026](https://arxiv.org/abs/2611.02207v1)). Each request starts in a fresh conversation on whatever state the last one left. A miss the agent cannot see becomes the base for the next request, so per-request errors compound across the chain.

An outside signal breaks the loop. "A single external "that's wrong" after a failed request and one repair round lift chain completion from 51% to 59%, and a repaired mistake no longer hurts the requests that follow."

## When this backfires

A check between every request has a price, and it pays less when:

- Requests are independent. If a request does not build on the last, there is no broken base to compound.
- The call budget is tight. The repair round "raises the regression rate by 3 to 9 points and adds 47 to 294 calls per chain" ([Cuadron and Gupta, 2026](https://arxiv.org/abs/2611.02207v1)).
- An external gate already exists. A team whose CI runs the accumulated suite after every change and blocks on red already supplies the outside signal the paper tested.

A noisy check shrinks the gain but does not erase it. In the paper, "rejecting one correct submission in ten costs at most 2 points of completion, and rejecting every other one gives back most of the gain, though never below the level without a supervisor" ([Cuadron and Gupta, 2026](https://arxiv.org/abs/2611.02207v1)).

The numbers also carry benchmark caveats. The paper notes that "Specifications are model-written and model-audited, not yet human-reviewed," and that "twenty requests do not imply a twenty-link dependency chain." A sandbox judge "confirmed 795 as test-side" among the 1,733 failure sites it re-ran, so part of the measured failure is hidden-test strictness rather than agent error.

## Example

The paper's advice for users who hand an agent a sequence: "If a request is the foundation of the next, run it or try the feature before issuing the next request rather than after" ([Cuadron and Gupta, 2026](https://arxiv.org/abs/2611.02207v1)).

The paper measured the repair form of this check. One external signal that a request failed, plus one repair round, lifted chain completion from 51% to 59%. It also compared two kinds of message: "Naming the failing tests once achieves what insisting achieves in about three rounds" ([Cuadron and Gupta, 2026](https://arxiv.org/abs/2611.02207v1)).

## Key Takeaways

- Do not size delegation from a single-request benchmark score. All ten agents tested did worse on chains of 20 requests, and the average fell from 95% to 51%.
- A green run of the agent's own tests and an approval from an agent reviewer are both weak signals here. A passing local run left the miss rate at 8.3% against 8.6% overall, and review accuracy was 53%.
- Put the external check before the next request starts, and tell the agent which test failed rather than only that something did.
- In multi-agent setups, the paper says "the verifier's line must reach the subagents directly, not stop at the agent that delegated."

## Related

- [Building on Inherited Test Failures in Agent Task Chains](building-on-inherited-test-failures.md) — the three-event study with the same direction of effect
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — the single-session form of declaring done too early
- [Trust Without Verify: Skipping Agent Output Checks](trust-without-verify.md) — accepting agent output with no independent check
- [Incremental Verification: Check at Each Step, Not at the End](../../verification/incremental-verification.md) — checking each step before building on it
- [When a Second Model Helps in LLM Review](../../verification/cross-model-review-independence.md) — when a second model's review adds signal
