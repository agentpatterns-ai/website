---
title: "Gating Agent Pull Requests on Documentation Co-Change"
term: "Documentation Co-Change Gate"
description: "A documentation-presence check clears on a CHANGELOG line and fails a refactor that needs no docs. The study behind the 63.2% drift figure recommends triggering review on change size instead."
aliases:
  - documentation co-change gate
  - documentation presence merge gate
  - requiring a docs change in every agent pull request
tags:
  - anti-pattern
  - testing-verification
  - code-review
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-23
maturity: emerging
---

# Gating Agent Pull Requests on Documentation Co-Change

> A documentation file in the diff proves only that a documentation file was touched; the check clears on a CHANGELOG edit.

The study behind the 63.2% drift figure rejects documentation presence as the trigger for human review. It does not evaluate merge gates. Its advice to organizations is to trigger human review on change size, "not on the presence of documentation, and treat drift itself as a risk signal" ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)). Its stated reason is that "undocumented changes are more often followed by fixes and drift persists" ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)).

## What the measure counts

The AIDev analysis covers 29,669 agent-authored pull requests across 2,585 repositories. A pull request counts as drifted when it changes at least one code file and zero documentation files, and 63.2% did ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)). The label is coarse by design: "Our label captures whether any documentation file is updated alongside code, not whether an update was needed or related to the changed code" ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)). The authors name both error directions in one sentence: "an unrelated CHANGELOG edit counts as co-change, while an internal refactoring that needs no documentation counts as drift" ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)).

One repository shape defeats the check outright: documentation kept outside the repository counts as drift, because "inline comments, docstrings, and out-of-repo docs (wikis, hosted sites, API portals) are invisible to a commit-level method and count as drift, inflating our 63.2% rate" ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)).

## Why it works

Change size confounds the comparison between documentation presence and later fixes. The paper does not measure where review time pays back. Measured per pull request, documented changes drew 79% more file-attributed fixes inside 30 days, a mean of 3.78 against 2.11. Those pull requests are also 3.9 times larger, and "Larger PRs touch more files, offering more surface for later fixes to attach to" ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)).

Holding exposure at one changed code file across 177,743 file-changes flips the sign back. A drifted file draws a later same-file fix 15.3% of the time against 14.1% at 30 days, and 16.6% against 14.9% at 90 days ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)). Size is the exposure term the paper controls for, and the review trigger it recommends. That recommendation is not a measured review-payback result. Documentation presence varies by task type, and the authors are explicit that "This attribution is temporal, not causal" ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)).

## What the numbers support instead

- Trigger human review on change size. The recommendation to organizations names size, with more than five changed files as its example threshold ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)).
- Read drift as a risk marker rather than a verdict. The authors ask you to "treat drift itself as a risk signal", and decline to call the rate agent-specific: "Lacking a human baseline, we do not claim this rate is specific to agents" ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)).
- Repay the files that already drifted. A file changed without documentation is re-documented within 90 days 24.0% of the time, against 48.2% for one changed with it ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)). The advice to agent developers is to prompt agents to document "previously-undocumented files they revisit, not only files they create".

## When this backfires

This critique does not remove the need to ask for relevant documentation. The paper's conclusion still asks that agents "treat documentation co-change as a first-class signal rather than an optional by-product" ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)). Ask in the prompt and review rubric. The paper rejects documentation presence as the review trigger; its construct limitations also matter when designing a merge gate.

I read a presence check as defensible where presence tracks need, such as a published API reference that must change with every behavior change. Keeping documentation in-tree avoids counting out-of-repository updates as drift.

Two conditions weaken the case for a blanket gate.

- Drift is highest on refactor and fix work, 77.5% on refactoring against 55.2% on features, and the authors allow that "internal fixes and refactorings may also less often need a documentation change" ([arXiv:2610.27381v1](https://arxiv.org/abs/2610.27381v1)). A blanket gate may block hardest where documentation is less often needed.
- The effect it chases is 1.2 to 1.7 percentage points against file-level fix rates of 14.1% to 16.6%.

A presence target can also be gamed. Thoughtworks describes the same risk for coverage targets: "the team might game the metric by writing tests that check the same behaviour so that they can achieve the target coverage" ([Thoughtworks](https://www.thoughtworks.com/insights/blog/agile-project-management/questionable-metrics-for-measuring-product-quality)).

## Example

**Before — the check clears on any touched file:**

```bash
# Any markdown file in the diff satisfies the gate
git diff --name-only origin/main... | grep -qE '\.md$|^docs/'
```

A one-line `CHANGELOG.md` edit clears this. A 40-file internal refactor that needs no documentation fails it. That pairing is the paper's construct threat, reproduced as CI.

**After — size triggers review and drift feeds a queue:**

```bash
# Review trigger on change size, the paper's recommended variable
n=$(git diff --name-only origin/main... | wc -l)
[ "$n" -le 5 ] || gh pr edit --add-reviewer "$REVIEW_TEAM"
```

Drifted files go onto a scheduled documentation pass instead of blocking the merge, which is the repayment direction the paper asks agent developers to prioritize.

## Key Takeaways

- 63.2% of 29,669 agent pull requests changed code with no documentation file in the same diff, and the label counts any documentation file, needed or not.
- The paper recommends change size as the human-review trigger and drift as a risk signal. It does not test merge gates.
- The file-level fix gap is 1.2 to 1.7 percentage points once exposure is held at a single file. The pull-request-level comparison points the other way because documented pull requests are 3.9 times larger.
- Track already-drifted files in a repayment queue. Their measured re-documentation rate was 24.0%, against 48.2% for files changed with documentation.
- The check counts wiki or hosted-portal updates as drift because it cannot see those files. A gate based on that label can block documented work.

## Related

- [Diff-Coverage Gating for Agent-Authored Pull Requests](../../verification/diff-coverage-gate-agent-prs.md) — a gate on the agent's own diff that the evidence does support, and the contrast that makes this one a proxy.
- [Post-Merge Fix Signals for Agent Merges](../../verification/post-merge-fix-signals-agent-merges.md) — follow-up fix rates measured against a human baseline, which this paper lacks.
- [Continuous Documentation as an Agent-Driven Practice](../../workflows/continuous-documentation.md) — the scheduled realignment pass that repays accumulated drift.
- [Documenting Code the Agent Can Already Read](documenting-code-the-agent-can-read.md) — when a documentation update buys nothing for the agent that reads the file.
- [AST-Grounded Critic Loop for Documentation Maintenance](../agent-design/ast-grounded-doc-critic-loop.md) — checking that a documentation change reflects the code, which presence cannot.
