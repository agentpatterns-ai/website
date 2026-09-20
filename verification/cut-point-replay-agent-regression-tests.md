---
title: "Cut-Point Replay: Test a Fix Against a Recorded Agent Run"
term: "Cut-Point Replay"
description: "Serve a recorded agent run's unchanged boundaries from the record and run the changed ones live, so one production incident becomes a deterministic regression test."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - partial replay for agent tests
  - cut-point testing
last_reviewed: 2026-09-19
maturity: emerging
---

# Cut-Point Replay: Test a Fix Against a Recorded Agent Run

> Serve a recorded agent run's unchanged boundaries from the record and run the changed ones live, so one incident becomes a deterministic regression test.

Set this up only when two conditions hold: every non-deterministic call site in the agent is marked, and you accept that the resulting test covers one input. Given both, a recorded production failure becomes a test that runs on every commit. It costs nothing at the provider whenever the live subset holds no model boundary ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)).

## What gets recorded

The unit is a boundary: a model call, a tool call, or a routing decision, "which is exactly where a rerun can diverge" ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)). Each execution of one is a crossing, stored as an immutable envelope holding its input, its output, and drift metadata such as model version and sampling parameters.

Crossings are addressed by name and occurrence, so a boundary crossed three times in a loop yields `agent[1]`, `agent[2]`, and `agent[3]`. The replayer serves the kth crossing its kth envelope. An extra loop or a dropped retry makes lookup fail and replay raise, rather than pass on a stale fixture ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)).

Recording is cheap enough to leave on in production: a median 23 µs per crossing, 0.008% of an assumed 300 ms model call, and at most 1.44 KB of store ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)).

## Why it works

A rerun diverges in three places at once. Model inference is not bitwise reproducible even at temperature zero, tools read external state that has since changed, and retries and routing change how many times a step runs ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)). Fixing a boundary to its envelope removes it as a variable. What is left is the code at the live subset, the only difference between the failing run and the candidate run.

Stub everything instead and the verdict stops depending on your fix. The mock returns the recorded unsafe result whether or not a gate exists. On a benchmark of six recorded incidents, cut-point tests pass the fix and benign edits 6 times out of 6. The full-stub baseline passes the fix 0 times out of 6. In a mutation study of the guarded tools, cut-point tests kill 51 of 192 first-order mutants; the baseline kills none, "since the tool never runs under it" ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)).

## Choosing the live subset

Two rules cover the choice. Put the code you changed in the live subset, or the test cannot see your change. Keep destructive tools out of it unless the run targets a sandbox, because an envelope captures a boundary's interface and not its internal side effects ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)). The usual shape stubs the model crossing that produced the bad arguments and runs the tool live. The gated tool then executes against arguments the agent produced, not arguments a developer guessed.

What you leave live sets the bill. The benchmark's cut-point plan runs 6 of the suite's 12 model crossings live. Stub both model crossings and run only the tool live, and the same gate is tested "without re-paying for model calls" ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)).

## When this backfires

- Partial annotation. Coverage of non-deterministic call sites is the user's responsibility, and an unmarked call runs live and escapes the count check ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)). A half-marked agent yields a test that looks deterministic and is not.
- Reading a green suite as proof the guard is correct. Of the 141 mutants that survived the study, 110 "cannot be killed by any test built from these recordings", because each recording exercises one input ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)).
- Reordering that preserves call counts. The per-name check misses it, and the order-sensitive digest that would close the gap is not in the evaluated release ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)).
- Shapes the release does not cover: streaming responses, parallel tool calls, and re-raising a recorded exception ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)).
- Recordings you cannot safely keep. A recording copies prompts, agent state, and tool arguments, and may contain secrets or personal data. Redaction runs at record time, before anything is written ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)).
- Boundaries left stubbed are still stubs, and mocked tests "may be potentially easier to generate automatically (but less effective at validating real interactions)" ([Hora and Robbes, 2026](https://arxiv.org/abs/2602.00409v1)). A cut-point plan narrows that exposure to the stubbed set without removing it.

A plain unit test is cheaper when the faulty component is a function of its arguments and you can read those arguments out of the trace once. The record earns its keep when nobody would have guessed the arguments, and when you want the fixture to fail loudly after the boundary contract changes.

## Example

One of the released incidents is a trade where the agent read a notional amount as a share count. The plan stubs the first model crossing and runs the tool live:

```python
@boundary("place_order", kind="tool")
def place_order(symbol, qty): ...

plan = (ReplayPlan()
        .stub("agent", 1)       # from record
        .live("place_order", 1) # cut-point
        .live("agent", 2))
assert session.captured_result("place_order", 1)["blocked"]
```

The unguarded tool sells 1,000 shares, roughly $190k, for a request of roughly $1k. The gated tool blocks it. The cut-point test fails on the unguarded code and passes on the gated version and on benign rewordings ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)). The implementation and benchmark are MIT-licensed at [theagentplane/chronicle](https://github.com/theagentplane/chronicle).

## Key Takeaways

- Pick the live subset first. It must contain the code under test, and it must not contain a destructive tool pointed at production.
- Full replay and hand-written mocks are the two ends of one dial. Anything you stub stops contributing to the verdict, so stub only what you are not testing.
- Determinism is a property of your annotation coverage, not of the tool. One unmarked call site is enough to make a green suite meaningless.
- The evidence is six self-constructed three-step incidents with simulated model boundaries, with no loops, retries, or multi-agent routing ([Chawla and Koul, 2026](https://arxiv.org/abs/2609.20625v1)). Treat reported determinism as a property of the replay mechanism, not a measurement against a live provider.

## Related

- [One-Shot Record and Deterministic Replay for Periodic Agent Tasks](../tool-engineering/one-shot-record-deterministic-replay.md) — the same recording with nothing live, used to remove model cost from cron-style runs.
- [Simulation and Replay Testing for Agent Verification](../workflows/simulation-replay-testing.md) — re-runs a whole past task from a git state and diffs the output, with no boundary served from a record.
- [Incident-to-Eval Synthesis: Production Failures as Evals](incident-to-eval-synthesis.md) — the upstream step, turning an incident into a case; cut-point replay is one way to make that case deterministic.
- [Bug-Discriminating Validation Evidence for Repair Agents (BSG-VA)](bug-discriminating-validation-evidence.md) — the matching failure on the assertion side, where a passing test also passes on the unfixed code.
- [Decomposing Agent Output Variability by Layer](sampling-state-agent-variability-layers.md) — which layer the variance you are removing came from.
