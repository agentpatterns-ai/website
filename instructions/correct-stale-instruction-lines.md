---
title: "Correct Stale Instruction Lines Instead of Deleting Them"
term: "Stale Instruction Documentation Debt"
description: "A stale test command in AGENTS.md sent agents to a dead path in 78 of 80 runs while agents still fixed the bug in nearly every run; correcting the line removed every detour and deleting it left some."
tags:
  - instructions
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - stale instruction line
  - instruction file documentation debt
  - stale AGENTS.md path
last_reviewed: 2026-11-18
maturity: emerging
status: current
---

# Correct Stale Instruction Lines Instead of Deleting Them

> Correct a stale instruction line on a step most tasks share, because deleting it leaves some agents guessing and task success hides the cost.

A stale line in `AGENTS.md` or `CLAUDE.md` is documentation debt: the repair is a one-line edit, and every later session that reaches the line pays again. In a controlled study of 732 Claude Code runs, a stale test command sent agents to a folder that no longer existed in 78 of 80 runs, and "with the corrected line, no run did" ([Mehtiyev et al., 2026, arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). Agents still fixed the bug in nearly every run, so a success-only evaluation scores all three versions of the line the same.

## When the line matters

The study ran three real stale lines from open-source repositories, each in a stale, corrected, and removed version, on 22 tasks with two models ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). Use of the stale path depended on the task more than on the line itself: 78 of 80 runs for a test command, 55 of 80 for a procedure, and "none of the 84 in the Location case" ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). No Location task needed the file that line named.

Check lines on shared steps first. Every fix ends with running the tests, so the stale test command reached nearly every run. In the Location case, agents already had the right file within two calls from the task report, package listing, or tests. None consulted the stale location. The paper states the ranking as a hypothesis, because three cases cannot separate the kind of line from its repository ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)).

## Correct the line, do not delete it

Deletion looks like the cheap repair. It removed most of the effect and left the rest: "With the line deleted, agents used the stale path in 1 of 80 runs in the Command case and 20 of 80 in the Procedure case, against 78 and 55 with the stale line and none with the corrected line" ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). In the Procedure case, agents guessed the old folder from the code's structure.

Deletion also kept the effort cost. On the test command, Sonnet "used as many tool calls without the line as with the stale one (7.8 per run in both, against 5.8 with the corrected line" ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). Without the line, it had to work out the test command itself.

## Find stale paths with a script

A path in an instruction file is checkable. "Stale paths are also cheap to find: a script can check whether a path exists, although deciding whether a missing path is an error still needs judgment" ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). Unlike a stale convention, no one has to decide whether the file or the code is right. Run the check in CI, and review each hit before you edit.

Do not wait for the next routine edit of the file to catch it. Each stale line in the study survived every later edit of its file: 2, 13, and 4 edits ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)).

## Stop the silent pass

The stale test command produced a check that tested nothing and reported success. "In 64 of the 80 stale runs in the Command case, at least one call on the stale path ran no tests, and Claude Code flagged none of these calls as an error: every run that ran the command piped its output through tail or head, so the shell reported success" ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). In 19 of Sonnet's 40 stale runs, the first check of the fix ran no tests.

The shell rule behind it is documented: "The exit status of a pipeline is the exit status of the last command in the pipeline, unless the `pipefail` option is enabled" ([GNU Bash manual](https://www.gnu.org/software/bash/manual/html_node/Pipelines.html)). Two of the paper’s four proposed safeguards, none evaluated, apply here: set `pipefail`, and treat "no tests ran" as a failure ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). For the second, pytest gives an empty run its own status, "Exit code 5: No tests were collected", so a wrapper can fail on the code instead of reading the output ([pytest docs](https://docs.pytest.org/en/stable/reference/exit-codes.html)).

## Why it works

The loaded file fills a missing starting point, and agents take it without saying so. "Before their first stale call, agents cited the instruction file in 2 of the 133 runs that used the stale path and opened it in none" ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). A corrected line gives the right starting point. A removed line leaves the gap, and the agent fills it by guessing from the code's structure, sometimes back to the old path.

Agents recover from the dead path and leave the line in place. They reached the current target in 130 of 133 encounters, and "No instruction file was edited in any of the 732 runs" ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). The file remained stale despite recovery; the final reply named the mismatch in 21 of 133 encounters.

## When this backfires

- The measured cost is small. The only resolvable effort difference was Sonnet on the test command, and its 95% interval excluded zero "though not after correcting for the number of estimates" ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). Haiku's runs varied too widely to show one.
- A corrected line is a new line to keep current. If the path moves often, deletion plus the existence check may cost less than repeated corrections. The study did not measure the effort of either repair ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)).
- Lines off the task path earn nothing from correction. Correction and deletion had the same measured effect in the Location case ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)).
- A missing path is sometimes correct, such as generated output. Treat the existence check as a review queue, not an auto-fix.
- Hidden diagnostics still hinder diagnosis. Haiku redirected stderr with `2>/dev/null` in 16 of its 38 stale-path Command runs ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)). That redirection hides the message but preserves the command's exit status. With `pipefail` enabled, a nonzero status still makes the pipeline fail ([GNU Bash manual](https://www.gnu.org/software/bash/manual/html_node/Pipelines.html)).
- The evidence is two models from one vendor in one harness, three cases, and 22 mostly small seeded bugs. The authors ask readers to treat the results "as evidence about these cases rather than as general rates" ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)).

## Example

The study's pyflow case shows one line in all three versions. Its `AGENTS.md` listed `pytest tests/ifds` for the IFDS tests. The tests moved to `tests/analysis/ifds` in July 2026, and the line survived two later edits of the file ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)).

On one seeded bug, a negated condition, Claude Sonnet 5.5 found and fixed the bug the same way in every version. Verification differed. The corrected run checked the fix in one call. The removed run took two. The stale run ran the documented command, piped through `tail`, which ran no tests and reported success, then needed two more test attempts. All three runs passed the final check on the original tests ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)).

The repair is one line:

```diff
- pytest tests/ifds
+ pytest tests/analysis/ifds
```

## Key Takeaways

- Rank stale lines by how many tasks pass through them. A stale test command reached 78 of 80 runs; a stale code location no task needed reached none ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)).
- Correcting a stale line removed every stale-path operation in the study. Deleting it left 21 of 160, and Sonnet's tool-call count on the test command did not drop.
- An evaluation that scores only the final patch misses this debt. In four Command tasks all 15 Sonnet runs produced the same patch byte for byte ([arXiv:2611.09802v1](https://arxiv.org/abs/2611.09802v1)).
- Run agent shells with `pipefail`, and fail a test step that collected no tests.

## Related

- [Stale AI Configuration Artifacts (Context Rot)](../patterns/anti-patterns/stale-ai-configuration-artifacts.md) — how often instruction files carry stale code references, and the consistency checker that finds them
- [Code Precedence Over Stale Instruction Files](code-precedence-over-instruction-files.md) — the stale convention case, where no script can tell which half is wrong
- [Scheduled Instruction File Fact-Checker](../workflows/instruction-file-fact-checker.md) — an agent that checks instruction-file claims against the codebase on a schedule
- [The No-Op Test](behavioral-no-op-test.md) — deciding by behavior whether a line earns its place
- [Agent Context File Evolution](agent-context-file-evolution.md) — the update triggers that keep a file in step with code moves
