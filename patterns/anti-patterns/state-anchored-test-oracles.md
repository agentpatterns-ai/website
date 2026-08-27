---
title: "Test Oracles That Read Their Expectation From the Code"
term: "State-Anchored Oracle"
description: "An oracle whose expected value flows from the code under test cannot fail, because a fault moves measurement and expectation together and the comparison cancels."
tags:
  - testing-verification
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - oracle anchoring
  - state-anchored expectation
  - state-anchored oracle
last_reviewed: 2026-08-23
maturity: emerging
status: current
---

# Test Oracles That Read Their Expectation From the Code

> An oracle whose expected value comes from the code it judges cannot fail, because a fault moves both sides of the comparison.

A state-anchored oracle obtains its expected value, directly or transitively, from the code it is judging. A specification-anchored one composes that value from constants, published procedures, or other values fixed outside that code ([Canedo, 2026](https://arxiv.org/abs/2608.17214v1)). The first cannot fail. A fault that shifts the system state shifts the measurement and the expectation together, the comparison cancels exactly, and no generated input reveals it. The defect lives in the oracle, not in the input space.

## The anti-pattern

The assertion looks like a real check. It exercises the system, works out a value to compare against, and compares. What it never does is disagree. That makes it the harder sibling of [assertion-free test theater](assertion-free-test-theater.md), where nothing is asserted at all.

The expected value is only one route by which mutated code reaches a verdict. Three more carry it just as well: the width of a tolerance band, a conditioning variable read at evaluation time, and a scenario-placing generator that runs before any assertion exists ([Canedo, 2026](https://arxiv.org/abs/2608.17214v1)). An audit has to trace all four, because closing the obvious one leaves the rest open.

## Why it works

The oracle passes by cancellation rather than by correctness. When the expected value and the measured value both derive from the same system state, a fault that perturbs that state perturbs both, so the predicate comparing them holds under the fault for every input ([Canedo, 2026](https://arxiv.org/abs/2608.17214v1)). What is lost is oracle independence: a yardstick has to be fixed outside whatever is being changed, or it moves with it. Two controls back this up. Running the mechanism backwards on a healthy oracle degraded it as predicted, and a reference-model suite killed exactly what the specification-anchored properties killed, which puts the risk in the anchoring rather than in model-freedom.

## What the measurement shows

The subject is a deployed air traffic control simulator with 12 model-free property suites, and the study intervenes three times, predicting each outcome first ([Canedo, 2026](https://arxiv.org/abs/2608.17214v1)):

- Closing every anchoring channel on the holding-geometry module, adding no assertion and changing no production code, "moves detection from 26.09 to 45.65%" over a fixed population of 46 mutants, taking the kill count from 12 to 21. Re-anchoring the yardstick on published procedure carries 8 of those 9 on its own.
- State-anchoring a healthy debounce oracle, as a negative control, dropped detection "from 18 of 19 to 14 of 19, from 94.74 to 73.68%".
- Writing the oracle the analysis said was missing exposed two defects deployment had not surfaced.

Half the predicate is static. Canedo calls the flow half "decidable on the import-and-call graph, without executing anything and without a mutant population" — you read where each value in the comparison comes from. The other half, whether the anchored value sizes the comparison, is not decidable and took a reading of each oracle.

## When this backfires

Most state-anchored oracles cost nothing. Of 6 instances Canedo found and ablated, the two where the anchored value sizes the comparison carry 11 of the 12 mutants the ablations recover; the other four carry one between them ([Canedo, 2026](https://arxiv.org/abs/2608.17214v1)). An audit that reports every instance without that split overstates the problem, which is why the flow question ("where did this value come from?") has to be paired with the sizing question ("does it set the bar the comparison uses?").

Anchoring is also relative to what is being changed, so a report is incomplete until it says anchored with respect to what. One unchanged oracle recovered nothing under one declared mutate target and 3 mutants under another that differed only in whether it contained the code producing the value the oracle reads. Canedo's conclusion: "State anchoring is fatal only when the observed state and the mutated code are the same artifact" ([Canedo, 2026](https://arxiv.org/abs/2608.17214v1)). A reader not running mutation testing has no declared target at all; the module or package boundary is the proxy he recommends.

There may be nothing external to anchor on. More than half the corpus in an independent review of LLM-based oracles reaches its verdict without consulting any specification ([Mughal and Bilal, 2026](https://arxiv.org/abs/2607.05031)). Re-anchoring undocumented code means writing the specification first.

Banning computed expectations outright reverts good repairs. The test-smell rule Canedo builds on requires the expected value to be a constant or a reference to one, not computed during the test. His repair calls a specification function, so that rule flags the fix as the defect: "The published smell rule would revert our repair" ([Canedo, 2026](https://arxiv.org/abs/2608.17214v1)).

The instrument has limits too. Canedo grants that mutation score is "a proxy, and a contested one", and a replication study finds its usefulness "highly context-dependent": informative when the code can be assumed bug-free, but not where the code under test may already be buggy and the goal is to expose that bug ([Zhao, Zhou and Cohen, 2026](https://arxiv.org/abs/2607.22880v1)). His external validity section concedes a single system, four modules, and one author.

## Key Takeaways

- Read the import-and-call graph behind the expected side of each assertion before writing more properties. That half needs no test run and no mutants.
- Ask the sizing question too, by hand: an anchored value that does not set the bar the comparison uses is usually free.
- Audit four routes, not one: the expected value, the tolerance band, any conditioning variable read at evaluation time, and the scenario generator.
- Say what scope the verdict is against. With no mutation testing to declare one, use the module or package boundary.
- Re-anchor on values fixed outside that scope. A constants-only rule is the wrong repair and reverts good ones.
- Treat the magnitudes as one system by one author, measured with a contested proxy.

## Related

- [Generating Tests From Agent-Written Code (Code-First Oracle Bias)](code-first-test-oracle-bias.md) — the generation-time sibling, where the model saw the implementation before writing the test and the assertions encode its faults.
- [Assertion-Free Test Theater in Agent-Authored Patches](assertion-free-test-theater.md) — the coarser failure, where the test executes code and asserts nothing at all.
- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](../../verification/mutation-testing-quality-gate.md) — the instrument an anchoring audit is measured with.
- [Deriving a Specification From Buggy Code Before Generating Tests](../../verification/derived-specification-test-generation.md) — what to do when there is no external specification to anchor on.
- [Overtrusting Human Sign-Off on Generated Assertions](generated-assertion-signoff.md) — why reading the assertion and nodding is not the audit.
