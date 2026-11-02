---
title: "Passing Tests Are Not Evidence an Agent Patch Is Secure"
term: "Test-Pass Security Evidence"
description: "Adversarial issue text drove repair agents to test-passing patches carrying a reachable vulnerability in up to 0.91 of their correct patches."
aliases:
  - test-pass as a patch security verdict
  - adversarial issue statements for repair agents
  - correct but vulnerable agent patch
tags:
  - anti-pattern
  - security
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-01
maturity: emerging
---

# Passing Tests Are Not Evidence an Agent Patch Is Secure

> Where an outsider files the issue and little or no review stands between patch and main, a test-passing patch can hide a reachable vulnerability.

Reading a green regression run as the security verdict on a repair agent's patch is the mistake. Two conditions set the exposure. An outside party has to supply the text the agent repairs from. The patch has to reach the default branch through an automated merge or a thin review.

## What the measurements cover

Chen and colleagues generated adversarial issue statements against three repair agents. The benchmark was SWE-bench Lite, "which contains 300 self-contained functional bug-fix instances", The study covered twelve agent and backend-model combinations ([arXiv:2509.25894v2](https://arxiv.org/abs/2509.25894v2)). Among patches that correctly fixed the reported bug, the share also carrying a vulnerability reached 0.91 in the best cell. On that same measure the three attack baselines topped out at 0.20.

The number a maintainer normally watches did not move. In one setting "it achieves a Pass@1 of 0.48, matching the no-attack baseline" ([arXiv:2509.25894v2](https://arxiv.org/abs/2509.25894v2)).

A second study found the same on a different benchmark and different backends, though it shares two authors with the first. It built 750 adversarial issue descriptions from 150 SWE-bench Verified tasks. "On average, adversarial issue descriptions can induce malicious behaviors with successful repair in 51.7% of cases" ([arXiv:2609.15963v1](https://arxiv.org/abs/2609.15963v1)).

## Why it works

A test suite constrains behavior only on the inputs it runs, and the attack puts the payload outside that set. It sits alone in a branch "reachable only through attacker-controlled conditional inputs", and the paper states the consequence directly: "Because the branch is not exercised by CI/CD test inputs, the patch appears functionally correct while the vulnerability is exploitable under targeted conditions" ([arXiv:2509.25894v2](https://arxiv.org/abs/2509.25894v2)).

It stays quiet because it leaves the bug report largely intact and rewrites only the reproduction detail. The agent still fixes the reported bug. The weaker baselines failed for the opposite reason. Their injected functions "are not invoked by original code logic, making them unreachable dead code" ([arXiv:2509.25894v2](https://arxiv.org/abs/2509.25894v2)).

## What to review instead

Read the control flow the patch adds, not its size or its test result. The paper's own prescription says why: "Passing I/O tests only confirms behavior on observed inputs; untested branches introduced by the patch may still hide malicious logic" ([arXiv:2509.25894v2](https://arxiv.org/abs/2509.25894v2)). A new branch gated on caller-supplied input that no test exercises is the shape worth stopping on.

A scanner is one layer, not the answer. In the first study the static checker is the detector by construction. "A patch is considered vulnerable if it contains a vulnerable function that is invoked by other functions" ([arXiv:2509.25894v2](https://arxiv.org/abs/2509.25894v2)). Bandit does the measuring. That paper shows tests missing what a scanner saw, never that nothing can find it. The second measured the scanner layer directly and found it thin: "Semgrep flags 31.6%-39.6% of ASR patches, while Bandit flags only 10.4%-13.2%". Pairing an issue-level model screen with patch-level analysis took average detection accuracy to 65.9%, and its authors keep the residual attached: "even this combined setting remains incomplete, with an average error rate of 34.1%" ([arXiv:2609.15963v1](https://arxiv.org/abs/2609.15963v1)).

## When this backfires

- No outsider can file the issue your agent acts on. The first study assumes "a GitHub repository adopts a fully automated CI/CD pipeline or relies on a careless reviewer" ([arXiv:2509.25894v2](https://arxiv.org/abs/2509.25894v2)). Where maintainers triage first, closing that channel costs less than a new gate.
- You add a default scanner and read its silence as a pass. Bandit flagged 10.4-13.2% of test-passing vulnerable patches on the second benchmark ([arXiv:2609.15963v1](https://arxiv.org/abs/2609.15963v1)). One single-instance case study found that "lightweight obfuscation can conceal malicious intent from static analysis while preserving the payload's runtime effect" ([arXiv:2509.25894v2](https://arxiv.org/abs/2509.25894v2)).
- You route every agent patch to a reviewer already at capacity. A case-control study of Chromium OS reviews observes that "developers who participates in a large number of reviews may become less cautious (i.e., review fatigue) and miss security defects". Its authors add that they have no definite explanation for the association ([arXiv:2102.06909v1](https://arxiv.org/abs/2102.06909v1)).
- Your repository is not a benchmark instance. The first study measures 300 SWE-bench Lite instances. The second says of itself that it "uses 150 tasks selected from SWE-bench Verified and focuses primarily on Python repositories with five attack types" ([arXiv:2609.15963v1](https://arxiv.org/abs/2609.15963v1)). Transfer past that is unmeasured.
- You turn branch coverage into a hard merge rule. Correct patches add error paths no existing test reaches, so the rule rejects correct work.

## Example

**Before — the regression suite is the whole gate:**

```yaml
- run: pytest
- uses: ./.github/actions/automerge   # suite green, patch lands
```

**After — the patch's new lines get a named report and the merge waits for a person:**

```yaml
- run: pytest
- run: diff-cover coverage.xml        # report coverage of the patch's new lines
- run: semgrep --config=rules/
- if: ${{ always() }}
  run: gh pr edit "$PR" --add-label needs-human
```

Every step here reports and none of them merges. The coverage report names the new unexercised lines without blocking, which would reject a correct patch that adds an unreached error path. The label step runs even when an earlier step fails, so no result can skip the human. A quiet suite and a quiet scanner are the two signals you cannot condition on.

## Key Takeaways

- A green suite reports behavior on the inputs it ran. It cannot speak to a branch the patch added and no test reaches.
- Review the control flow the patch adds. A branch gated on caller-supplied input that no test exercises is the thing to look at.
- Treat every detection layer as partial. The strongest combination measured still erred on 34.1% of cases, so plan for a miss rather than for a clean dashboard.

## Related

- [Treating a Clean Static Scan as Security Evidence](static-clean-as-security-evidence.md) — the adjacent error, where the silent evidence is a scanner rather than a test run.
- [Passing Tests Are Not Evidence a Patch Is Fast](passing-tests-as-performance-evidence.md) — the same gate read as a verdict, on the performance axis instead of the security one.
- [Diff-Coverage Gating for Agent-Authored Pull Requests](../../verification/diff-coverage-gate-agent-prs.md) — the changed-line coverage measure that would surface a patch's unexercised new branch.
- [Circular CI Verification in Dual-Scope Agent PRs](../../verification/circular-ci-verification-agent-prs.md) — the other case where a passing check supplies no independent assurance.
- [Trusting Human Review to Catch Deliberate Agent Sabotage](deliberate-agent-code-sabotage.md) — the same hidden payload when the agent, not the issue author, is the adversary.
