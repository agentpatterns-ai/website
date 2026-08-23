---
title: "Spec-Driven Test Generation: Contract Coverage Is the Lever"
term: "Spec-Driven Test Generation"
description: "Making an agent document pre-conditions, post-conditions and undefined behaviors before writing tests pays only when the extracted contract names the condition the bug violates."
tags:
  - testing-verification
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - contract-first test generation
  - spec-driven test synthesis
  - oracle-driven test generation
last_reviewed: 2026-08-23
maturity: emerging
---

# Spec-Driven Test Generation: Contract Coverage Is the Lever

> A contract written before the tests earns its token premium only when it names the condition the bug violates.

Spec-driven test generation adds one mandatory phase before test synthesis: the agent reads the code under test and documents its contract, then writes the suite against that artifact. Google measured the technique over 90 historical bug-fixes from its internal issue tracker, spanning C++, Java, Python and Go, and found bug detection rose from 53.4% to 63.2% across five sampling runs, a gain of 9.8 percentage points at p=0.0352 ([Tufano et al., 2026](https://arxiv.org/abs/2608.17177v1)).

## The conditions it needs

Three conditions have to hold before the extra phase is worth adding.

You run the generator more than once per unit. The significant result is a five-run number. At a single run the gain was 4.2 percentage points with p=0.3075, which does not clear significance, and the token premium is paid on every run either way ([Tufano et al., 2026](https://arxiv.org/abs/2608.17177v1)).

The defects you are chasing are boundary and contract violations rather than absent tests. Line coverage barely moved, 74.4% against 74.8%, and pass@5 was identical at 98.9%. Branch coverage rose 2.5 points at p=0.0034, so the suite reaches deeper into control flow without touching more code ([Tufano et al., 2026](https://arxiv.org/abs/2608.17177v1)).

The contract is legible from the code you point the agent at. Everything depends on the agent writing down the right constraint, and even in the study's favorable setting it captured the relevant one just 61.1% of the time on a single run ([Tufano et al., 2026](https://arxiv.org/abs/2608.17177v1)).

## What the spec artifact contains

The agent produces four fields for each code unit ([Tufano et al., 2026](https://arxiv.org/abs/2608.17177v1)):

| Field | Content |
|---|---|
| Description | What the unit is intended to do, in natural language |
| Pre-conditions | State required before execution |
| Post-conditions | Guaranteed state afterward, covering input validation, success values and side effects |
| Test suggestions | Conditions that are not yet covered |

Every condition is marked tested or untested, which turns the artifact into a checklist the synthesis phase works through.

## Why it works

The spec phase converts implicit behavioral constraints into an explicit enumerated list, and that list is what the synthesis phase writes assertions against. A bug is caught when the contract it violates was written down, and missed when it was not.

The study isolates that link rather than asserting it. Conditioning each run on whether the generated contract documented the pre-condition or post-condition the historical bug actually violated, detection was 54.9% (151 of 275 runs) with coverage and 19.4% (34 of 175) without, a Fisher's exact p of 3.62×10⁻¹⁴ with a phi coefficient of 0.35 ([Tufano et al., 2026](https://arxiv.org/abs/2608.17177v1)). The agent captured the relevant contract 61.1% of the time on a single run and 78.9% across five.

That reframes what to inspect: coverage of the contract predicts detection, not the presence of a planning step. The review question is whether the spec names the behavior you expect to break.

## When this backfires

A spec that documents the happy path. Per-run detection falls to 19.4% when the contract misses the violated condition. Code whose invariants live in the caller, in configuration, or in nobody's head produces exactly that spec.

Code that may itself be wrong. The evaluation synchronized the agent's workspace to the state immediately after the human fix, so every contract was extracted from correct code ([Tufano et al., 2026](https://arxiv.org/abs/2608.17177v1)). Point the same phase at suspect legacy code and it can record the defect as intended behavior. Prompting 11 models with buggy code instead of fixed code raised misguided tests from 16.46 to 137.69 on average and cut effective bug-revealing tests from 304.08 to 104.15 ([Zhao, Zhou and Cohen, 2026](https://arxiv.org/abs/2607.22883v1)).

Specs the model gets wrong. On [the VERINA benchmark](https://arxiv.org/abs/2505.23135v3) the strongest general-purpose model scored 52.3% on combined specification soundness and completeness, and the authors report post-conditions are harder to get right than pre-conditions. The phase can yield a confident, wrong contract.

Multi-file and integration defects. The authors kept only bugs whose fixes modify a single source file, so nothing in the evidence speaks to cross-unit failures ([Tufano et al., 2026](https://arxiv.org/abs/2608.17177v1)).

High-volume CI. Total tokens rose 38.0% and output tokens 59.1%. Cost per unique bug detected still rose 16.2% after counting the extra bugs found ([Tufano et al., 2026](https://arxiv.org/abs/2608.17177v1)).

One missing control is worth knowing about. The study never reports what the baseline achieves on the same 38% larger budget spent on extra sampling runs, the obvious alternative use of the money.

## Example

Run the spec phase as a separate step whose output is a file the synthesis step reads, so you can inspect the contract before any test exists. A `.spec.md` for a payment-capture function:

```markdown
# capture(order_id, amount_cents)

## Purpose
Capture a previously authorized payment, in whole or in part.

## Pre-conditions
- [tested]   order_id refers to an existing authorization
- [untested] amount_cents <= authorized amount
- [untested] amount_cents > 0
- [untested] the authorization has not expired

## Post-conditions
- [tested]   returns a capture record on success
- [untested] raises InvalidAmount when amount_cents exceeds the authorization
- [untested] leaves the authorization untouched on any failure
- [untested] a second capture on the same authorization is rejected

## Undefined
- Behavior when the gateway times out mid-capture
```

The untested lines are the working list, and reviewing them is cheaper than reviewing the suite. If none of them names the failure you are worried about, write the missing condition before running the generator again.

## Key Takeaways

- Bug detection rose from 53.4% to 63.2% across five sampling runs (p=0.0352); at one run the 4.2-point gain did not clear significance (p=0.3075).
- Contract coverage predicts detection: 54.9% of runs caught the bug when the spec named the violated condition against 19.4% of runs when it did not, Fisher's exact p=3.62×10⁻¹⁴.
- Branch coverage rose 2.5 points while line coverage stayed flat, so the gain is control-flow depth, not more code touched.
- The price is 38% more tokens and 16.2% more tokens per unique bug found. Apply it to units where a boundary defect is expensive rather than across a whole repository.
- Review the generated contract before the tests. A missing condition is visible in the artifact and cheap to add there.
- The evidence covers single-file fixes in one organization's monorepo, extracted from already-fixed code. Legacy code of unknown correctness sits outside it.

## Related

- [Specification-Grounded Test Writing](specification-grounded-test-generation.md) — the variant where a human supplies the specification as enumerated rules instead of the agent extracting it
- [Deriving a Specification From Buggy Code Before Generating Tests](derived-specification-test-generation.md) — what to do when the code under test may itself be wrong, the case this technique's evaluation excludes
- [Use pass@k and pass^k to Separate Agent Capability from Consistency](pass-at-k-metrics.md) — why a five-run result and a single-run result answer different questions
- [Test-Driven Agent Development: Tests as Spec and Guardrail](tdd-agent-development.md) — the inverse ordering, where tests are the contract and the implementation follows
- [Specification-Path Testing: Same Contract, Different History](specification-path-testing.md) — how the route a contract took to its final form changes which tasks an agent gets right
