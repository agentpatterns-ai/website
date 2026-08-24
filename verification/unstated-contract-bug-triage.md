---
title: "Unstated-Contract Bugs: Sort Tickets by Information Gap"
term: "Unstated-Contract Bug"
description: "Agents fixed two hard bugs 16/16 and failed an easy one 12/12, because the contract lived in user data, so triage tickets by information gap."
tags:
  - testing-verification
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - unstated contract bug
  - information-gap triage
  - undocumented API contract failure
last_reviewed: 2026-08-24
maturity: emerging
---

# Unstated-Contract Bugs: Sort Tickets by Information Gap

> Twelve runs on one unstated-contract bug passed 84 tests and corrupted user data, because the answer lived outside the repository.

An unstated-contract bug is one whose correct fix depends on information that appears in no repository artifact: how callers structure their data, what behavior they rely on. Nhu Hoang's 28-run debugging study is the concrete case. Agents fixed two hard bugs, in immer and decimal.js, 16 times out of 16, and failed an easy bug in the HTTP client ky 12 times out of 12 ([Towards Data Science](https://towardsdatascience.com/bug-detection-blind-spots-in-ai-coding-harnesses-gstack-and-beyond/)). Every failing run found the root cause, then shipped a patch that "passed all 84 visible retry tests" while silently rewriting any `retry` field in the caller's own `json` payload into a retry configuration object.

## Conditions this holds under

- The evidence is thin, and the author says so. One unstated-contract bug, one library, one to three seeds per configuration. Hoang assigns difficulty "by intuition", names JS/TS-only sourcing and possible training contamination as limits, and calls the result "one case study, not a general law" ([Towards Data Science](https://towardsdatascience.com/bug-detection-blind-spots-in-ai-coding-harnesses-gstack-and-beyond/)). Read it as evidence the class exists, never as a rate for your backlog.
- Structure is the better general predictor. Across 45,769 tasks, Al-Haque and Johnson predict agent success from static features at AUC 0.863, driven by patch fragmentation and repository scale. Adding every prompt feature on top buys ΔAUC ≤ 0.002 ([arXiv:2608.18280v1](https://arxiv.org/abs/2608.18280v1)). Hoang's headline, "Difficulty didn't predict failure", does not survive contact with that dataset.
- The two studies measure different things, and that is where the class survives. The outcome variable in the 45,769-task study is `pass_rate`, "the fraction of runs that passed all tests". Passing all tests is the oracle the ky bug defeats. Difficulty predicts whether the harness goes green. It says nothing about whether green is right.

## The triage question

Ask one question before you assign a ticket. Is everything needed to produce the correct fix visible in the code and the ticket, or does correctness depend on how the system is actually used?

If the answer sits in the repository, hand the ticket over. If it lives in user behavior, write the contract into the ticket first. That move is [issue requirements preprocessing](../patterns/agent-design/issue-requirements-preprocessing.md); what this page adds is which tickets need it. Hoang calls the ticket one of two places with real leverage, because "every contract you make explicit gives the agent information it cannot infer from the code."

When you cannot tell, treat it as the second case. The cost is asymmetric, because this failure arrives as a confident green build rather than a visible error.

Do not let a reviewer agent's approval stand in for the check. In Hoang's run, one reviewer "correctly identified that the proposed patch would corrupt user data" and "approved the change anyway", reasoning the issue was unlikely. His reading: "The failure wasn't in detection—it was in judgment." Human review did catch the same mistake on the real pull request.

## Why it works

The agent builds its context from repository artifacts, and an unstated contract is absent from every one of them by construction. In the ky case, "The correct answer lived in users' data—a space no artifact ever mentioned" ([Towards Data Science](https://towardsdatascience.com/bug-detection-blind-spots-in-ai-coding-harnesses-gstack-and-beyond/)). No step in the loop notices the absence. Ambig-SWE finds that models "struggle to distinguish between well-specified and underspecified instructions" ([arXiv:2502.13069v3](https://arxiv.org/abs/2502.13069v3)), so the agent commits to an assumption instead of asking. That is what [interactive clarification](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) exists to interrupt. The existing suite cannot falsify the assumption either, since it was written from the same artifacts that omitted the contract.

Supplying the missing information closes the gap: Ambig-SWE measures gains "up to 74% over the non-interactive settings" ([arXiv:2502.13069v3](https://arxiv.org/abs/2502.13069v3)).

## When this backfires

- Most tickets are not this. In CoderForge-Preview, 49.8% of tasks are solved by every trajectory ([arXiv:2608.18280v1](https://arxiv.org/abs/2608.18280v1)). Interrogating all of them spends the review budget on the common case.
- Hard tickets need decomposition, not enrichment. Prompt features reach the top-5 SHAP contributors for 70.3% of mid-band tasks but only 6.8% of hard ones ([arXiv:2608.18280v1](https://arxiv.org/abs/2608.18280v1)). At the hard end, structure dominates and better ticket text barely moves the result.
- Code with one in-repo caller has no unstated user contract. The class needs users whose behavior you cannot read, so an internal service with a single known consumer dissolves it.
- The blocking gate's cost is unmeasured. Hoang's second recommendation is absolute: a review identifying a potential side effect or data corruption "blocks the merge. No weighing likelihood, no discretion." Removing the discretion is the point, since "the process only needs one reviewer to stop a bad change". But the study never measures how often reviewers flag a side effect that is not real, so the throughput cost on your repository is unknown.
- Enrichment assumes you know the contract. On an unfamiliar subsystem you will write a confident wrong one, and a stated wrong contract is worse than a missing one.

## Example

The ky bug: a base client configured with `retry: 3` was extended with `retry: {methods: ['get']}`, and the numeric limit silently vanished.

The obvious fix normalizes numeric values into `{ limit: 3 }` before merging. It passes all 84 retry tests. The same merge function also processes the caller's `json` payload, so a `retry` field sitting in that payload gets rewritten too, which is how twelve runs produced data corruption. The maintainer's fix applies "the conversion only to the top-level retry option" ([Towards Data Science](https://towardsdatascience.com/bug-detection-blind-spots-in-ai-coding-harnesses-gstack-and-beyond/)).

One sentence separates those two patches: users put arbitrary JSON in request bodies, and some of that JSON has a key called `retry`. It is in no test, no type signature, and no comment. Put it in the ticket and the agent has what it needs.

The GStack workflow under test already required agents to "enumerate everything your intended change will touch" before implementing. Impact enumeration did not rescue this bug, because enumeration walks the artifacts, and the artifacts are where the contract is not.

## Key Takeaways

- Ask one question at triage: is the answer in the repository, or in how people use the thing? Route on that, not on how hard the bug looks.
- When you cannot tell, assume the answer is outside the repository. The failure arrives as a green build, so guessing wrong costs more in one direction than the other.
- Keep using difficulty for the general case. Static structural features predict agent success at AUC 0.863, and the information question is for the minority where pass rate is the wrong oracle.
- Put the contract in the ticket, and do not let a reviewer's approval substitute for it. Hoang's reviewer detected the corruption and signed off anyway.
- A green test count is not evidence of a correct fix. Eighty-four passing tests accompanied twelve patches that corrupted user data.

## Related

- [Probing Unstated Constraints in Generated Code (Intent Violation Rate)](unstated-constraint-probes.md) — the constraint your prompt omitted but you still know; this page covers the contract nobody in the repo knows.
- [Generating Tests From Agent-Written Code (Code-First Oracle Bias)](../patterns/anti-patterns/code-first-test-oracle-bias.md) — a suite blind because it inherited the code's faults, where here a pre-existing suite is blind because the contract was never written down.
- [Issue Requirements Preprocessing: Structured Input Before Code Generation](../patterns/agent-design/issue-requirements-preprocessing.md) — the enrichment move measured across a benchmark; this page is how to tell which tickets are worth the effort.
- [Interactive Clarification for Underspecified Tasks](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) — the other repair for the same gap, where the agent asks instead of you writing the contract up front.
- [Precise Debugging: Measure Edit Precision, Not Just Test Pass Rate](precise-debugging-benchmark.md) — another case of a pass rate hiding what the patch actually did.
