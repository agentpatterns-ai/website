---
title: "Treating a Clean Merge as Compatibility Evidence"
term: "Clean-Merge Compatibility Assumption"
description: "A clean merge reports that two patches edited different text. On constructed Django tasks, a blind agent's patch merged with a concurrent interface change and still broke the tests in 105 of 108 runs."
aliases:
  - clean merge as compatibility evidence
  - semantic coordination gap
  - passes alone, fails together
tags:
  - anti-pattern
  - multi-agent
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-23
maturity: emerging
---

# Treating a Clean Merge as Compatibility Evidence

> A clean merge means the two patches edited different text, and they still broke tests in 105 of 108 constructed Django runs.

A merge that reports no conflict tells you the patches touched different lines. It says nothing about whether they still agree on what the code means. Three conditions have to hold together before that gap costs you anything. Two or more agents start from the same base commit and "solve their assigned tasks independently", neither seeing the other's finished edit, and one of them changes a contract the other depends on ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). Miss any one and the risk is not there.

## The two rates in this paper are not the same number

Xia, Wu and Park built `stale`, a benchmark that runs one test suite over each patch alone and over the pair combined, counting only failures that appear when the patches are combined ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). It reports two very different results, and quoting the alarming one alone misrepresents the work.

The constructed tier pairs a script with an agent, so only one side is a model: "One patch makes a scripted interface change; an agent writes the other patch, which uses the helper" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). Across 36 such tasks on 12 real Django helpers, "In the blind condition, GPT-5.5 produced interference in 105/108 runs (97%), with failures on all 12 helpers despite clean textual merges" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). On 417 validated pairs of already-merged Django pull requests, "Of 834 runs on 417 validated Django pairs, only one had" a nonzero interference count ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)).

The authors read the second number as a fact about the data, not about the mechanism: "These results suggest that merged PR history is a poor source of examples of unresolved parallel changes: development and review may have already made the patches compatible" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). They are equally blunt about the first: the constructed results "do not estimate its frequency or severity in everyday parallel development" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). Read 97% as proof that the mechanism reaches production helpers, not as a rate to expect in your repo.

## Why it works

A textual merge reconciles the regions each side edited. A dependency that crosses regions is invisible to it, so "a clean merge does not guarantee correct behavior" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). In the paper's motivating example one worker adds a price cache with invalidation while the other adds a bulk-write path: "The failure arises because A introduces an invariant that B's new write path violates: every price update must invalidate the corresponding cache" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). Neither patch is wrong alone, and neither edit region overlaps the other.

What the second agent lacks is information, not capability. On the synthetic tier a message "averaging about 130 tokens" dropped mean interference from 2.50 to 0.04 ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). The same template-generated message on the constructed Django tasks recovered "89/108 runs (82%)", and among message-conditioned patches that still merged cleanly "Recovery reached 93%" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). The paper reports no token count for that second tier, so treat 130 tokens as the size that sufficed on synthetic helpers rather than a budget for real ones. The content is narrow and mechanical either way: "The message states the new helper names, required arguments, or return types" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). No plan, no rationale, no diff.

## Checking for it badly invents it

The authors got their own grading wrong first, in two ways worth copying as a checklist. Agents edited test files, and each patch was scored against only its own task's tests while the merged pair was scored against both. Both inflated the count, because "Using different tests for individual and merged patches can falsely suggest interference" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). The fix held: "After removing agent test edits and running the combined test set in every condition, nearly all apparent interference disappeared" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). Without that discipline the check produces false alarms faster than findings.

## When this backfires

- Agents already work on disjoint symbols. With no shared contract between in-flight tasks there is nothing to go stale, and a combined-suite protocol is pure overhead.
- The shared code has thin behavioral tests. Interference is visible only through tests, and "Both measures depend on test coverage" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). The paper picked "12 helpers that can be unit-tested"; an untested helper returns a false all-clear.
- You broadcast work in progress. The 82% recovery assumes a complete description of a finished edit, and "recovery with messages generated during parallel work remains untested" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). A plan or a half-written patch is an unmeasured input.
- The change adds a required argument. Told about one, "the agent sometimes edits the helper definition itself, creating a textual conflict" ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)). Noisy beats silent, but it is not a clean pass.
- More than two agents are in flight. The benchmark studies pairs, and its authors flag that with more tasks a failure may need three changes together before it shows up ([arXiv:2609.25396v1](https://arxiv.org/abs/2609.25396v1)).

## Example

The paper's price-cache figure, run as two agent branches on one repo.

**Before** — merge cleanliness is the gate:

```bash
git merge --no-ff agent-a/cache-prices   # no conflict
git merge --no-ff agent-b/bulk-update    # no conflict
pytest tests/test_pricing.py             # only agent B's task tests
```

Agent B's patch passes its own tests, so the pair ships. The cache invariant agent A introduced is never exercised by that file.

**After** — one suite, run in all three conditions:

```bash
# built from both tasks' tests, reapplied from the repo after discarding agent test edits
SUITE="tests/test_pricing.py tests/test_cache.py"

git checkout base && git merge --no-ff agent-a/cache-prices && pytest $SUITE  # solo A
git checkout base && git merge --no-ff agent-b/bulk-update  && pytest $SUITE  # solo B
git checkout base && git merge --no-ff agent-a/cache-prices agent-b/bulk-update && pytest $SUITE
```

Interference is what the third run fails and neither solo run failed. A failure that already appeared in a solo run belongs to that patch and gets excluded from the count.

## Key Takeaways

- A no-conflict merge is a statement about text. Behavioral agreement between two agents' patches needs a test run on the combined code.
- Keep the 97% and the 1-in-834 together. The constructed tasks show the failure is real on real helpers, the mined pull-request history shows reviewed work rarely retains it, and neither number predicts your repo.
- Run one test suite in all three conditions, each patch alone and the pair combined, and count only failures that are new in the combined run.
- Discard agent edits to test files before grading. Scoring patches against different suites manufactures interference that was never there.
- Where agents must share a symbol, hand the later one a short description of the finished change. It recovered 82% of the constructed Django failures, and about 130 tokens was enough on the synthetic tier.

## Related

- [Concurrent Agent Pull Requests and Merge-Conflict Cost](../../workflows/concurrent-agent-pr-merge-conflicts.md) — the textual half of the same collision, with measured conflict rates and a coordination ladder.
- [Pre-Write Change Intent Admission (Claim Plane)](../multi-agent/pre-write-change-intent-admission.md) — preventing the collision by declaring write scope before coding, instead of detecting it after the merge.
- [Coordination Channel Policy for Multi-Agent Coding](../multi-agent/coordination-channel-policy.md) — how agents should exchange the change description this page argues for.
- [Multi-Agent Shared State Isolation Anomalies](multi-agent-shared-state-isolation-anomalies.md) — the same stale-assumption family when the shared thing is mutable memory rather than source code.
- [Worktree Isolation](../../workflows/worktree-isolation.md) — the isolation that creates the blind condition in the first place.
