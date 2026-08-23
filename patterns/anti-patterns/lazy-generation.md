---
title: "Shallow Agent Test Coverage from Premature Termination (Lazy Generation)"
term: "Lazy Generation"
description: "Coding agents generating tests quit early and systematically skip complex branches, leaving coverage shallow exactly where the hard-to-test logic lives; the fix is supervised coverage gates, not trusting the agent's self-report."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - lazy test generation
  - premature test termination
last_reviewed: 2026-07-13
maturity: emerging
---

# Shallow Agent Test Coverage from Premature Termination (Lazy Generation)

> Coding agents generating tests quit early and skip complex branches, so coverage stays shallow exactly where the hard-to-test logic lives.

Lazy generation is when a coding agent tasked with writing tests "prematurely terminate[s] tasks and systematically avoid[s] complex programmatic logic, resulting in inadequate code coverage" ([SCATE, arxiv 2607.08983](https://arxiv.org/abs/2607.08983v1)). The agent reports the job done; the branches it skipped are the ones that most needed a test.

## What it looks like

The agent announces tests are "generated and verified," but execution "prematurely terminates," leaving branch coverage "stalled at a mere 31%" in the SCATE authors' Gemini-cli run ([arxiv 2607.08983](https://arxiv.org/abs/2607.08983v1)). Agents "naturally gravitate toward simple methods and straight-line execution paths," so the untested remainder is not random — it concentrates on the deeply nested, dependency-heavy code where bugs hide. The tell is a self-report of completion that a coverage tool contradicts: the transcript says done, the branch-coverage number says half the decision points never ran.

## Why it happens

The agent must "understand source code, including complex control flows and extensive external dependencies, within a limited context window" ([arxiv 2607.08983](https://arxiv.org/abs/2607.08983v1)). High internal complexity raises "the reasoning burden on the LLM," and external coupling "complicates environment setup and dependency mocking." Under a bounded context window the path of least resistance is to cover the simple, dependency-free methods and stop. The shortfall therefore lands systematically on the complex branches, not evenly across the file.

## Distinguish from adjacent failures

Same neighborhood, different failure:

| Failure | What the agent does | Fix |
|---------|--------------------|-----|
| Lazy generation | Stops test generation early; skips complex branches | Supervise coverage of complex branches, not self-report |
| [Premature completion](premature-completion.md) | Declares the whole task done while any test fails | Externalize the stopping criterion to test-suite state |
| [Abstraction bloat](abstraction-bloat.md) | Produces too much code — unrequested abstractions | Explicit simplicity directives |
| [Assertion-free test theater](assertion-free-test-theater.md) | Emits tests that run but assert nothing | Gate on oracle strength, not test presence |

Lazy generation is the inverse of abstraction bloat — too little test coverage, not too much code — and narrower than premature completion, which terminates the whole task rather than skewing the shortfall onto hard branches.

## What to do instead

Treat coverage of complex branches as a supervised gate rather than the agent's word. SCATE watches three signals during generation — line coverage, branch coverage, and `missed_complexity` (uncovered method entries and decision points) — and re-prompts the agent on the specific gaps ([arxiv 2607.08983](https://arxiv.org/abs/2607.08983v1)). That supervision lifted Gemini-cli branch coverage by 30.9% over the unsupervised baseline, to 74.7%, at $0.693 per class ([arxiv 2607.08983](https://arxiv.org/abs/2607.08983v1)). Budget for the loop instead of assuming the agent finishes the hard cases on its own.

## Example

The SCATE authors' Gemini-cli run shows both sides of the failure on the Defects4J benchmark ([arxiv 2607.08983](https://arxiv.org/abs/2607.08983)).

Lazy generation, where the self-report is trusted:

```text
Agent report: "tests generated and verified"
Branch coverage: 31%   <- execution prematurely terminated; complex branches uncovered
```

Corrected, where the coverage signal is supervised:

```text
missed_complexity flags the uncovered method entries and decision points
-> agent re-prompted on exactly those branches
Branch coverage: 74.7%
```

The stop decision comes from the live coverage and `missed_complexity` signals, not from the agent's summary.

## When this backfires

- Simple code. SCATE's gains are shown only on structurally complex classes (WMC >=35 or RFC >=55) ([arxiv 2607.08983](https://arxiv.org/abs/2607.08983)). On straight-line code the agent already reaches coverage, so a supervision loop adds cost without value.
- A bare coverage number is gameable. Pushed to hit a line or branch target, an agent can emit shallow tests that execute a branch without checking behavior — 100% line coverage can sit next to a 30% mutation score ([Autonoma](https://getautonoma.com/blog/mutation-testing-vs-code-coverage)). Mutation score, not coverage, correlates with real fault detection ([Petrović et al., ICSE 2021](https://homes.cs.washington.edu/~rjust/publ/mutation_testing_practices_icse_2021.pdf)), so pair the coverage gate with mutation or assertion checks or you buy [test theater](assertion-free-test-theater.md).
- Single-language evidence. SCATE's results are Java and Defects4J only; the authors flag this as a "threat to external validity" ([arxiv 2607.08983](https://arxiv.org/abs/2607.08983)). The per-class cost and signal calibration are unverified on other stacks.

## Key Takeaways

- Lazy generation is premature termination inside test generation: the agent stops early and systematically skips the complex branches, so coverage is shallow where it matters most.
- The mechanism is a bounded context window — complex control flow and dependency mocking raise the reasoning burden, so the agent takes the easy paths and quits.
- The fix is automated supervision on live coverage and uncovered-complexity signals, not the agent's self-reported completion.
- Gate on mutation or assertion strength alongside coverage — a bare coverage target is gameable and evidence so far is Java-only.

## Related

- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — the broader stopping-criterion failure this narrows
- [Abstraction Bloat](abstraction-bloat.md) — the inverse: agents producing too much code, not too little coverage
- [Assertion-Free Test Theater in Agent-Authored Patches](assertion-free-test-theater.md) — the failure a naive coverage gate causes
- [Generating Tests From Agent-Written Code (Code-First Oracle Bias)](code-first-test-oracle-bias.md) — a related test-generation blind spot
- [The Test Homogenization Trap](test-homogenization-trap.md) — LLM test suites sharing the model's blind spots
