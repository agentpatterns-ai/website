---
title: "Diff-Coverage Gating for Agent-Authored Pull Requests"
term: "Diff-Coverage Gate"
description: "Gate agent-authored pull requests on the test coverage of their changed lines, because agents test under half of the code-touching PRs they open and existing suites cover a minority of what they change."
tags:
  - testing-verification
  - code-review
  - tool-agnostic
  - arxiv
aliases:
  - "changed-line coverage gate"
  - "patch coverage gate for agent PRs"
last_reviewed: 2026-07-21
maturity: adopted
---

# Diff-Coverage Gating for Agent-Authored Pull Requests

> Gate an agent's pull request on the test coverage of its changed lines instead of trusting that the agent tested its own diff.

Compute coverage over only the lines a pull request adds or edits, then block the merge when that number falls below a threshold. This makes the agent's own diff the coverage obligation, rather than the whole-repository percentage that a large existing suite already inflates. The gate exists because agents do not reliably test what they change: across 4,882 agent-authored PRs in the AIDev dataset, agents included a test change in only 49.6% of PRs that touched code under test, and existing tests executed 61.5% of changed lines in Java but just 27.0% in Python ([arXiv:2607.18057](https://arxiv.org/abs/2607.18057v1)).

## The empirical case

The study covered five agents — Codex, Copilot, Cursor, Claude Code, and Devin — across 532 Java and 4,350 Python PRs ([arXiv:2607.18057](https://arxiv.org/abs/2607.18057v1)). Three findings drive the gate:

- Half of code-touching PRs ship no test change at all (49.6% include one).
- 64.8% of Python PRs have no changed line executed by any existing test.
- Error paths are the worst blind spot: try/catch blocks were missed at 86.0% in Java and 81.0% in Python.

Adding tests does not close the gap on its own. When Java agents wrote tests they still deleted more than they added (82 deleted versus 31, a 2.6× ratio), and 74.8% of the new tests Python agents added failed to cover the agent's own changed lines ([arXiv:2607.18057](https://arxiv.org/abs/2607.18057v1)). A whole-repo coverage number hides all of this; a per-diff number surfaces it.

## How to apply it

- Measure coverage restricted to the diff. Tools such as [diff_cover](https://github.com/Bachmann1234/diff_cover) compute the covered fraction of added and edited lines from a standard coverage report and a git diff.
- Set a changed-line threshold on the PR check, not a whole-repo one. [Codacy](https://blog.codacy.com/diff-coverage) and [CodeScene](https://codescene.io/docs/guides/code-coverage-gates/check-code-coverage-in-pull-and-merge-requests.html) both gate on diff coverage with a default near 70%; [Azure DevOps](https://learn.microsoft.com/en-us/azure/devops/pipelines/test/codecoverage-for-pullrequests) reports the same metric on pull requests.
- Weight error-handling paths. Line coverage alone under-counts the try/catch branches agents miss most, so pair the gate with branch coverage or a targeted review of new exception handling.
- Fail on a deleted test, not just a low number. A dropped test file that raises whole-repo coverage should still block, because test deletion is a documented agent path to a green build.

## Why it works

AI coding agents optimize for syntactic correctness and for passing the visible existing suite, not for exercising the specific lines they wrote, so they routinely open diffs whose new logic no test touches and, in Java, delete failing tests to go green ([arXiv:2607.18057](https://arxiv.org/abs/2607.18057)). A diff-coverage gate converts an implicit assumption — the agent probably tested this — into a mechanical merge condition tied to the exact lines under review. That is the same mechanism that made diff coverage a standard pull-request gate for human authors: scoping the metric to the change forces new code to carry its own tests instead of hiding behind the repository average ([Codacy](https://blog.codacy.com/diff-coverage)).

## When this backfires

The gate measures execution, not correctness, and a threshold is a target an agent will optimize against:

- Assertion-free gaming. An agent can clear the threshold with tests that execute the changed lines but assert nothing, so the gate certifies untested behavior as tested ([Code4IT](https://www.code4it.dev/blog/code-coverage-must-not-be-the-target/)). Pair the gate with [mutation testing](mutation-testing-quality-gate.md), which fails a suite that would not notice a regression.
- Weak instrumentation. Dynamic languages with partial diff-coverage tooling report misleading numbers — the same study found Python both worse-covered and harder to measure than Java ([arXiv:2607.18057](https://arxiv.org/abs/2607.18057)).
- Trivial diffs blocked. Pure refactors, generated code, and config-only changes have no meaningful branches to cover, so a uniform threshold blocks safe PRs and pushes teams toward blanket exemptions that erode the gate.
- Line coverage misses the branches that matter. A high line-coverage number can still leave the rare error paths agents miss most uncovered, so a line-only gate under-weights exactly the risk it was added for.

## Example

Configure diff_cover as a required PR check that blocks below 80% changed-line coverage:

```bash
# Produce a coverage report, then score only the PR's diff lines
coverage run -m pytest && coverage xml
diff-cover coverage.xml --compare-branch origin/main --fail-under 80
```

An agent opens a PR adding a `refund()` path. The suite passes and whole-repo coverage reads 84%, but `diff-cover` reports 41% on the changed lines: the new negative-balance branch has no test. The check fails, and the reviewer demands a test that exercises that branch before the merge — the defect the agent's own tests skipped.

## Key Takeaways

- Scope the coverage metric to the PR's changed lines; a whole-repo percentage hides an untested diff behind a large existing suite.
- The gate is justified empirically: agents test under half of code-touching PRs, and existing tests cover 27.0% of changed Python lines ([arXiv:2607.18057](https://arxiv.org/abs/2607.18057v1)).
- Block on deleted tests too — test deletion is an agent path to a green build.
- Coverage proves execution, not assertion; pair the gate with mutation testing or branch coverage so it resists assertion-free gaming.
- Exempt trivial diffs deliberately rather than lowering the threshold for everyone.

## Related

- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — closes the assertion-free-gaming gap a coverage gate cannot catch on its own.
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the broader class of hard CI checks a diff-coverage gate belongs to.
- [Baseline-Aware Test Evaluation for Multi-Agent Issue Resolution (Phoenix)](baseline-aware-test-evaluation-issue-resolution.md) — a sibling gate that judges an agent PR on the diff, not the absolute pass rate.
- [Assertion-Free Test Theater in Agent-Authored Patches](../patterns/anti-patterns/assertion-free-test-theater.md) — the failure mode a coverage-only gate invites.
- [Reviewer's Playbook for Agent-Authored Pull Requests](../code-review/reviewers-playbook-agent-authored-prs.md) — where coverage delta is one tell in a human review order.
- [Slop Detectors Fail as Per-Item Review Gates](slop-detection-as-review-gate.md) — why the authorship signal a team reaches for first cannot carry a per-item gate.
