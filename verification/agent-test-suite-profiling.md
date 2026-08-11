---
title: "Profile Your Agent Test Suite Against Measured Practice"
term: "Agent Test Suite Profiling"
description: "Label your agent tests by testing level, data pattern, fixture, and assertion target, then compare the distribution against two published baselines of what real agent suites actually contain."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - agent test suite profiling
  - test distribution baseline for agent suites
  - profiling agent test coverage by axis
last_reviewed: 2026-08-11
maturity: emerging
---

# Profile Your Agent Test Suite Against Measured Practice

> Label your agent tests by testing level, data pattern, fixture, and assertion target, then compare that distribution against two published baselines.

Two independent studies of real agent test suites report the same shape ([Pan et al., arXiv:2608.08413v1](https://arxiv.org/abs/2608.08413v1); [Hasan et al., arXiv:2509.19185v3](https://arxiv.org/abs/2509.19185v3)). Testing effort concentrates on the deterministic parts of the system and thins out sharply on the model-driven parts. Profiling your own suite on the axes those studies used answers one question: where does your reasoning and multi-step coverage live? An answer you cannot give is the finding.

## Run it when these hold

The profile is a diagnostic, and it only returns a usable signal under three conditions.

- Your agent plans over more than one tool. The multi-tool baseline below is not a gap when the agent has one tool and no multi-step plan.
- You can point at whatever carries trajectory and reasoning coverage, or say that nothing does. A study sampling `tests/` directories never sees a separate eval harness, so profile that too.
- The suite is large enough that proportions mean something. Below a few dozen agent-related tests, read the individual tests instead.

## The four axes

Tangent labeled 2,572 test methods across 240 modules in 12 repositories along the axes below ([Pan et al., arXiv:2608.08413v1](https://arxiv.org/abs/2608.08413v1)). Label your own tests the same way and put your percentages next to theirs.

| Axis | Label each test by | Measured baseline |
|---|---|---|
| Testing level | Isolated tool or agent, interaction, multi-tool scenario, exposed API endpoint | 61.8% isolated, 34.6% interaction, 3.5% multi-tool, 0.1% API |
| Test data | Dummy, realistic synthetic, mocked, real | 39.9% dummy, 54.0% realistic synthetic, 3.8% mocked, 1.5% real |
| Fixture | Mocks a component, mocks the entire agent, mocks the environment | 34.5% mock an agent or tool, of which 22.3% mock the entire agent |
| Assertion target | Output, state, reasoning, memory, environment | 55.9% output, 51.2% state, 8.8% reasoning, 2.6% memory |

Agent tests are also structurally trivial: a median of 14 non-comment lines, a cyclomatic complexity of 1, and 2 assertions each. Only 7.5% target non-functional requirements at all ([Pan et al., arXiv:2608.08413v1](https://arxiv.org/abs/2608.08413v1)).

A separate study of 39 agent frameworks and 439 agentic applications reaches the same distribution from a different corpus: deterministic tool and workflow artifacts absorb over 70% of testing effort while the foundation-model plan body receives under 5% ([Hasan et al., arXiv:2509.19185v3](https://arxiv.org/abs/2509.19185v3)). Two samples agreeing is what makes the baseline worth comparing against.

## Why it works

Test effort follows an oracle-availability gradient rather than a risk gradient. A test needs a controllable input and a stable, observable oracle. Deterministic tool code supplies both; model reasoning supplies neither, since its output varies run to run and no cheap ground truth exists. The least-effort response is to mock the model out of the test entirely, which is what 22.3% of the labeled tests do, leaving a suite whose pass rate is largely independent of the component under scrutiny. Tangent names that cause when it argues agentic frameworks need a testability theory built on observability and controllability. Its interviews with ten industry practitioners record the symptom directly, including one who reported having no adequacy metrics at all ([Pan et al., arXiv:2608.08413v1](https://arxiv.org/abs/2608.08413v1)). Closing a real gap therefore means supplying an oracle at that axis, not adding tests at it.

## When this backfires

- Treating convergence with the baseline as proof of a defect. Mocking a non-deterministic, rate-limited dependency out of a unit test is textbook isolation. Reasoning quality may also sit legitimately in a separate eval suite with its own datasets and cadence.
- Raising the multi-tool number with path assertions. Anthropic reports that checking a sequence of tool calls in the right order is "too rigid and results in overly brittle tests, as agents regularly find valid approaches that eval designers didn't anticipate" ([Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)). Assert on invariants the world must satisfy instead.
- Raising the reasoning number with an LLM judge. AgentRewardBench evaluated 12 judges over 1,302 web-agent trajectories and found that no single model excels across benchmarks ([Lù et al., arXiv:2504.08942v2](https://arxiv.org/abs/2504.08942v2)). Tangent adds that the tests already asserting on reasoning mostly check that the behavior is present rather than correct ([Pan et al., arXiv:2608.08413v1](https://arxiv.org/abs/2608.08413v1)).
- Profiling a library rather than an application. In a framework repo the test mix follows what the library exposes, and an application-derived baseline transfers poorly.

## Example

The fixture axis is the cheapest one to measure mechanically, because mocking leaves a syntactic trace. For a Python suite:

```bash
# Files containing tests
grep -rlE "def test_" tests/ | wc -l

# Files that patch or mock something
grep -rlE "unittest\.mock|mocker\.|@patch|MagicMock" tests/ | wc -l

# Files that mock the agent or model client itself, not a peripheral dependency
grep -rlE "(patch|Mock)[^)]*(Agent|LLM|Client|completion|invoke)" tests/ | wc -l
```

The third count over the first approximates your mock-the-agent rate, to read against the measured 22.3%. The other three axes need human labeling, and a sample of 50 tests is enough to place your suite on each one.

## Key Takeaways

- Profile before you prescribe. The output is a distribution across four axes, not a verdict.
- Read all four axes together. A suite can look healthy on assertion count while sitting at the corpus floor for multi-tool coverage.
- Treat "we do not know where reasoning coverage lives" as the result worth acting on, and go find the eval harness before writing a test.
- Budget for an oracle rather than for tests. The thin axes are thin because ground truth is expensive there, so the work item is a checkable invariant or a resettable environment.
- Rule out the two cheap remedies at the start. Path assertions and an unvalidated judge each turn a coverage gap into a new defect.

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — the default the multi-tool axis must not be closed against, since path grading fails valid alternative solutions
- [Stateful Agent Evals via State Snapshots and Transition Assertions](stateful-agent-state-and-transition-evals.md) — one sound way to add intermediate coverage once the profile shows the gap is real
- [Audit Your Test Suite With an Agent, Then Certify Each Flag](certified-agent-test-suite-auditing.md) — the adequacy question asked adversarially rather than by distribution
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — measurement gaps a stronger model cannot close, including the trajectory-opaque one this profile surfaces
- [Structural Coverage Criteria for Agent Workflows](structural-coverage-agent-workflows.md) — a coverage obligation derived from a coordination graph, for teams that want a target rather than a baseline
