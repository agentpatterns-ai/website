---
title: "The Merge-Conflict Resolution Skill: What to Encode"
term: "Merge-Conflict Resolution Skill"
description: "Encoding merge-conflict resolution as a named agent skill: trace each side to its primary source, run the repo's own checks, then commit."
tags:
  - tool-engineering
  - skills
  - code-review
  - tool-agnostic
aliases:
  - resolving-merge-conflicts skill
  - conflict resolution skill file
last_reviewed: 2026-08-25
maturity: emerging
---

# The Merge-Conflict Resolution Skill: What to Encode

> A conflict-resolution skill file pays off where commit history carries intent and the checks fail on a bad resolution.

A merge-conflict resolution skill is a named procedure an agent runs against an in-progress merge or rebase. It works hunk by hunk, traces each side back to the commit, pull request, or ticket that produced it, runs the project's own checks, and finishes with a commit ([AI Hero](https://www.aihero.dev/skills-resolving-merge-conflicts)). Writing it as a file rather than a prompt is the point: the same two steps run on every conflict.

## When it earns its keep

Two repo properties decide whether the file is worth writing.

History has to carry intent. The opening step reads commit messages, pull requests, and tickets to reconstruct why each side exists. In a repo of squashed merges and `wip` subjects there is nothing to read, so the step degrades to what an unprompted agent already does: "produce a plausible resolution from the diff alone and stop there" ([AI Hero](https://www.aihero.dev/skills-resolving-merge-conflicts)).

The check suite has to fail on a bad resolution. Verification catches only what the repo can already catch, and that is less than people assume: generated unit tests used as partial specifications detected nine of 28 semantic conflicts in one evaluation ([arXiv:2310.02395v1](https://arxiv.org/abs/2310.02395v1)).

## What the file encodes

The value sits in two steps the file "will not let the agent skip: reading why each side exists, and running the checks afterwards" ([AI Hero](https://www.aihero.dev/skills-resolving-merge-conflicts)).

Primary sources come before the diff. The failure mode it exists to kill is resolution by flag: "`--ours`, `--theirs`, or hand-deleting whichever block looks less important, so the markers go away and the build compiles. That resolution can be syntactically perfect and still silently drop a change somebody made on purpose" ([AI Hero](https://www.aihero.dev/skills-resolving-merge-conflicts)). Reading the history first turns two blocks of text into two intents, and both are kept wherever they are compatible.

The repo's checks run before the commit, because "a merge is the easiest place in git to produce code that satisfies both branches and passes neither's tests" ([AI Hero](https://www.aihero.dev/skills-resolving-merge-conflicts)).

There is no escalation branch. Where two sides are genuinely incompatible, the agent picks the side matching the merge's stated goal and names the trade-off. `--abort` "is not an option it has: the merge is always carried to a finished commit" ([AI Hero](https://www.aihero.dev/skills-resolving-merge-conflicts)). Whether the merge should happen is decided before invoking the skill. If you want a person in the decision loop, that is a different contract, described in [Agent-Proposed Merge Resolution](../code-review/agent-proposed-merge-resolution.md).

## Why it works

A conflict hunk is under-determined: neither side records a reason for its own existence, so resolving from the diff alone is a guess. Across 7,938 real conflict hunks from 1,439 GitHub repositories in 11 languages, "the best models correctly resolve less than 60% of merge conflicts" ([arXiv:2605.25890v1](https://arxiv.org/abs/2605.25890v1)). Naming the procedure does not raise that ceiling. It changes what the agent reads before guessing, and who verifies the result.

The verification half carries more weight than it looks. On real Java conflicts from ConflictBench, an LLM judge "accepted 4 of the 5 resolutions that fail the deterministic structural check, evidence that structural correctness must not be delegated to an LLM" ([arXiv:2607.27674v1](https://arxiv.org/abs/2607.27674v1)). An agent grading its own merge is unreliable, so the file names the repo's checks as the gate rather than letting the model declare itself finished.

## When this backfires

- Shallow or low-signal history. No linked pull request and a `wip` commit subject leave the intent step with no input, so it buys nothing over the diff-only resolution the agent would have produced unprompted ([AI Hero](https://www.aihero.dev/skills-resolving-merge-conflicts)).
- One session resolving another session's conflict. Batching every branch's conflicts onto a single agent "throws away exactly the context step 2 of this skill has to go and reconstruct" ([AI Hero](https://www.aihero.dev/skills-resolving-merge-conflicts)). The session that wrote the change should do the merge.
- Conflicts left by a large refactor that landed after ten branches forked from it. "A large rename landing after ten branches have forked off it is the case that stays expensive" ([AI Hero](https://www.aihero.dev/skills-resolving-merge-conflicts)), and the skill does not make it cheap. The fix is scheduling, covered in [Concurrent Agent Pull Requests and Merge-Conflict Cost](../workflows/concurrent-agent-pr-merge-conflicts.md).
- A merge you have not decided to complete. With no abort branch, invoking the skill converts an open question into a commit.

One caveat comes from the skill's own author rather than a critic. Matt Pocock calls the gain over a capable unprompted model "a thin margin over a good model, and it is meant to be", and passes on a reader's prediction that this is "a whole skill that becomes a no-op as models improve" ([AI Hero](https://www.aihero.dev/skills-resolving-merge-conflicts)). Treat the file as insurance against a skipped step, not a correctness upgrade.

## Key Takeaways

- The file is worth writing when commit history carries intent and the check suite fails on a bad resolution. Missing either one starves one of its two steps.
- Encode two steps and resist adding more: trace each side to its primary source before touching the diff, then locate and run the repo's own checks before the commit.
- The deterministic check is the load-bearing half. An LLM judge accepted 4 of 5 structurally invalid resolutions ([arXiv:2607.27674v1](https://arxiv.org/abs/2607.27674v1)), so the agent cannot certify its own merge.
- The procedure has no human-escalation branch by design. It picks a side, names the trade-off, and commits, so decide whether the merge should happen before you invoke it.
- Best models resolve under 60% of real conflicts correctly ([arXiv:2605.25890v1](https://arxiv.org/abs/2605.25890v1)). A written procedure changes what the agent reads first, not that ceiling.

## Related

- [Agent-Proposed Merge Resolution](../code-review/agent-proposed-merge-resolution.md)
- [Concurrent Agent Pull Requests and Merge-Conflict Cost](../workflows/concurrent-agent-pr-merge-conflicts.md)
- [Skill Authoring Patterns](skill-authoring-patterns.md)
- [Skill as Knowledge Pattern](skill-as-knowledge.md)
- [Skill Authoring as Software Engineering: What Transfers](skill-authoring-software-engineering.md)
