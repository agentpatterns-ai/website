---
title: "Audit Your Test Suite With an Agent, Then Certify Each Flag"
term: "Certified Agent Test-Suite Auditing"
description: "Point an agent at your suite to find inputs it wrongly accepts, and run every flag through a certification chain so the report is evidence rather than a guess."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - agent test-suite auditing
  - certification chain for agent-found bugs
  - adversarial suite adequacy audit
last_reviewed: 2026-08-04
maturity: emerging
---

# Audit Your Test Suite With an Agent, Then Certify Each Flag

> An agent flag is a hypothesis until an oracle independent of the code under test certifies it, so build the certification chain first.

Auditing a test suite with a coding agent means asking the agent to generate inputs the suite accepts but should not, then proving each flagged failure genuine without consulting the suite you are auditing. The proving half is the transferable part. Without it you get a queue of unverified hypotheses, each costing a developer roughly 10 to 20 minutes of inspection ([Du et al., 2026](https://arxiv.org/abs/2601.18844v1)).

## Check the preconditions before you start

The authors state the limit themselves: the chain assumes competitive-programming structure — a consensus oracle over accepted solutions, a statement-derived validator, exact-output judging — and has not been extended to specification-only tasks or tasks with no accepted solutions to seed the oracle ([Xie et al., 2026](https://arxiv.org/abs/2608.01715v1)). Three conditions decide whether your codebase qualifies.

1. You can name an oracle that does not depend on the code under test. A prior release, a slow reference implementation, a cross-language port, or a second team's rewrite all work. One implementation and nothing else does not.
2. Output is deterministic and comparable. Multiple valid answers, timing-dependent results, and unordered collections defeat comparison.
3. Preconditions can be written down as code before you see any failing input.

## The four gates

Each gate makes a failure attributable to the code under test rather than to a bad input or a wrong expectation ([Xie et al., 2026](https://arxiv.org/abs/2608.01715v1)).

| Gate | What it does | Your substitute |
|---|---|---|
| Consensus oracle | Takes expected output from agreement among independently written correct implementations, never from the artifact under audit | Prior release, reference implementation, cross-language port |
| Brute-force adjudication | Settles disagreements in the oracle set with a slow, obviously correct implementation | A naive quadratic version of the same function |
| Legality validator | Encodes declared preconditions as code and rejects out-of-spec inputs | A schema or contract check from the API docs |
| Reproducibility filter | Drops tolerance artifacts, keeps only repeatable failures | Re-run each candidate on a fixed harness |

Write the validator blind, before examining any failing input, as the authors did. Theirs recorded zero false accepts across 354 malformed mutations and 62 illegal-format inputs, and only a false accept can produce a false bug report ([Xie et al., 2026](https://arxiv.org/abs/2608.01715v1)).

## Why it works

The finding half works because of the agent loop rather than the model's prior knowledge. Holding the base model fixed, a single call reached 0.665 coverage of buggy solutions at a 50-input budget while the same model inside an agent loop reached 0.903 on the same 19 problems, which the authors attribute to the wrapper's tool and iteration affordances ([Xie et al., 2026](https://arxiv.org/abs/2608.01715v1)).

The trusting half works because the oracle sits upstream of the artifact under audit. A model shown buggy code asserts that code's defects: prompting with the buggy version instead of the fixed one cut effective bug-revealing tests from an average of 304.08 to 104.15, close to a threefold loss ([Zhao, Zhou and Cohen, 2026](https://arxiv.org/abs/2607.22883v1)). Any oracle derived downstream of the code you are auditing inherits its bugs.

Measured against real suites, one agent found 589 verified accepted-but-buggy submissions among 20,375 audited AtCoder submissions, and five agents together produced a union floor of 906. Those agents were not better than the official suites at what the suites already caught, staying within 1.7 percentage points of official coverage on logic bugs ([Xie et al., 2026](https://arxiv.org/abs/2608.01715v1)). The value sits entirely in the gap.

## When this backfires

- No independent oracle. With one implementation and no reference version, every flag reduces to the agent's opinion and the triage bill lands on a human.
- Loosely specified output. The published harness excluded 7 of 48 harvested problems as multi-solution or special-judge cases ([Xie et al., 2026](https://arxiv.org/abs/2608.01715v1)). Unguaranteed ordering is also the largest single cause of flakiness in LLM-generated tests, about 63% of flaky cases across four database systems ([Berndt et al., 2026](https://arxiv.org/abs/2601.08998v1)).
- Unwritable preconditions. If the contract lives in tribal knowledge, the audit reports bugs against inputs the code never promised to handle. Passing a validator still does not establish semantic ground truth ([Xie et al., 2026](https://arxiv.org/abs/2608.01715v1)).
- Repository-wide sweeps. Per-problem medians ran 21.7k to 30.5k output tokens and 5.8 to 22.8 minutes for a single competitive-programming problem ([Xie et al., 2026](https://arxiv.org/abs/2608.01715v1)). Aim this at a suite you have specific reason to distrust.
- An already-adequate suite. Since the agents matched official coverage to within 1.7 percentage points on bugs those suites caught, a strong suite leaves little gap for the audit to work in.

Reaching for coverage or mutation score instead is cheaper, but those proxies stop tracking real bug-detection effectiveness in exactly the case an audit targets, where the code under test may already be buggy ([Zhao, Zhou and Cohen's replicability study, 2026](https://arxiv.org/abs/2607.22880v1)).

## Key takeaways

- Build the certification chain before running the agent. The generation half is ordinary agent test writing; the chain is what makes its output usable.
- Name your oracle first. No independent oracle means no audit, only a triage queue.
- Write the legality validator from the specification, before you look at any failing input.
- Treat this as a targeted instrument for one suspect suite, not a continuous check across a repository.

## Related

- [Bug-Discriminating Validation Evidence for Repair Agents (BSG-VA)](bug-discriminating-validation-evidence.md) — the mirror problem: proving a passing test carries information about the bug it claims to fix
- [Deriving a Specification From Buggy Code Before Generating Tests](derived-specification-test-generation.md) — what to do when the only artifact available is the possibly-buggy implementation
- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — the cheaper adequacy proxy, and where it stops being informative
- [LLM-Driven Benchmark Auditing](llm-benchmark-auditing.md) — auditing the benchmark artifact itself rather than the suite under it
- [Specification-Grounded Test Writing](specification-grounded-test-generation.md) — supplying rules to the writer up front, the preventive counterpart to auditing after the fact
- [Profile Your Agent Test Suite Against Measured Practice](agent-test-suite-profiling.md) — the cheap distributional read to run before committing to an adversarial audit
