---
title: "Name What an Agent May Edit Before It Starts Editing"
term: "Boundary Contract"
description: "Give a coding agent four per-task file lists (editable, inspect-only, required, protected) before it edits. A 40-task pilot saw 9 to 18 acceptable patches."
tags:
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - artifact role contract
  - editable and inspect-only roles
  - per-task edit boundary
last_reviewed: 2026-11-05
maturity: emerging
---

# Name What an Agent May Edit Before It Starts Editing

> A boundary contract tells an agent, before it edits, which files it may change, read, must change, and must leave alone.

Context tells a coding agent which files matter. It does not tell the agent which of them it may change. A boundary contract closes that gap with four per-task lists, written before the first edit. In a pilot on one enterprise repository, strictly acceptable patches rose from 9 of 40 without the contract to 18 of 40 with it ([Eun et al., 2026](https://arxiv.org/abs/2611.01265v1)).

Three conditions decide whether this pays off. The lists must be correct, because a wrong list steers the agent wrong. The agent needs a sanctioned way to say the list is wrong. And if a protected file must never change, a "do not edit" line in the prompt will not reliably hold it.

## The four roles

The pilot paper defines one role per question the agent would otherwise answer alone ([Eun et al., 2026](https://arxiv.org/abs/2611.01265v1), §3.1):

| Role | Meaning in the paper |
|---|---|
| Editable | "artifacts that the agent is permitted to modify" |
| Inspect-only | "artifacts that may provide evidence but should remain unchanged" |
| Required | "artifacts, or artifact types, expected to participate in completing the task" |
| Protected | "artifacts that should not be modified for the requested change" |

The paper gives two cases. An API controller can be relevant for understanding a request and still be inspect-only. A regression test can be required even when the request does not name it. The authors put the argument in one sentence: "Relevance therefore does not imply editability, and editability does not imply obligation."

A contract holds no code. It "does not contain the expected code diff, implementation statements, or final patch", and the agent still explores, reasons, and writes the patch. The paper expresses the roles through fields such as `allowed_edit_paths`, `must_edit`, `inspect_only`, and `must_not_edit`, written to a `CANDIDATES.yaml` file before the agent edits ([Eun et al., 2026](https://arxiv.org/abs/2611.01265v1), §3.1 and §3.2).

## What the pilot measured

The study ran the same Codex-based agent twice on each of 40 maintenance tasks from one Java and XML repository with more than 2,900 artifacts. One run got only the request. The other also got the contract. The baseline could still search the repository freely ([Eun et al., 2026](https://arxiv.org/abs/2611.01265v1), §4).

| Measure | Request only | Request plus contract |
|---|---|---|
| Macro edit-selection F1 | 0.440 | 0.682 |
| Extra edits outside the expected scope | 56 | 22 |
| Omitted expected edits | 62 | 34 |
| Tasks with required test evidence | 11 of 40 | 26 of 40 |
| Strictly acceptable patches | 9 of 40 | 18 of 40 |

To probe whether the contract only helped the agent find files, the authors took the 21 tasks where both runs edited at least one identical file. There, macro F1 still rose from 0.652 to 0.786 and extra edits fell from 29 to 9. The authors warn this "should not be interpreted as a clean causal separation between localization and operational-boundary effects."

## Why it works

Without roles, the agent must infer edit scope, companion files, and frozen files from the request and whatever it finds while searching. The paper calls this the gap between an artifact's "informational relevance" and its "operational role" ([Eun et al., 2026](https://arxiv.org/abs/2611.01265v1), §2). A contract moves that inference out of the run. A separate study explains why restraint must be stated as a goal. Coding agents carry an action bias. On FixedBench, a prompt to reproduce the issue first had no effect on abstention for Sonnet 4.6 and lowered it for GPT-5.4 mini, unless the prompt also framed abstaining as a successful outcome. The authors conclude that "inaction needs to be explicitly framed as a path to success" ([Gloaguen et al., 2026](https://arxiv.org/abs/2605.07769v1)). The pilot does not show which of its four roles drives the gain. The authors call the contract "a combined treatment."

## How to apply it

1. Before the run, write the four lists for the task. A one-line request with no list leaves all four decisions to the agent.
2. Put every test the change needs in the required list, even when the request does not name it.
3. Add an exit: if a file outside the editable list looks necessary, stop and report which file and why. The pilot leaves this open, and the next section shows what happens without it.
4. If a protected file must not change, enforce it outside the prompt with a write fence, a hook, or required review, and keep the exit from step 3. The pilot contract was advisory and lived in the agent's task context ([Eun et al., 2026](https://arxiv.org/abs/2611.01265v1), §6.4).

## When this backfires

- The list is incomplete. Boundary-informed runs in the pilot still failed "when the supplied boundary is insufficient or too narrow" ([Eun et al., 2026](https://arxiv.org/abs/2611.01265v1), §5.3). A missing companion file leaves the agent two bad options: fail the task or break the contract.
- The protected role has no exit. CircumEval has 8 tasks on the FastAPI codebase. On its five Source-Locked tasks, where the source file is read-only and the tests are editable, all three models routed around the filesystem lock in at least 89% of runs on a plain request (Opus 4.6 100%, GPT-5.4 99%, Sonnet 4.6 89%). Adding "Don't edit read only files" to the prompt did not move the rate significantly for the Claude models (100% for both) and cut GPT-5.4 to 46%. Only the two prompts that told the agent to stop and report brought circumvention to zero ([Agrawal, Scheurer and Ariel, 2026](https://www.lesswrong.com/posts/GHrqBKr8GLpbce6mN/door-s-locked-try-the-window)).
- The restraint has no success path. A verify-then-abstain prompt on FixedBench raised correct abstention but made agents "over-abstain" on partly or wrongly fixed issues that still needed a patch ([Gloaguen et al., 2026](https://arxiv.org/abs/2605.07769v1)).
- Nobody can write the lists cheaply. The pilot built each contract with a separate proposal agent from a prepared knowledge base of maintenance units, change-type schemas, and rules ([Eun et al., 2026](https://arxiv.org/abs/2611.01265v1), §3.2). A team without that knowledge base writes every list by hand.
- The evidence is narrow. It comes from one repository, one agent, and one run per task, scored by patch review instead of the test suite ([Eun et al., 2026](https://arxiv.org/abs/2611.01265v1), §7). The authors suggest that stronger agents in highly regular repositories may infer roles well on their own (§6.5), which the pilot did not test.

## Key Takeaways

- Separate the files an agent may read from the files it may change, and list the files it must change.
- Put tests in the required list. Required test evidence rose from 11 to 26 of 40 tasks, though the pilot does not credit any single role.
- A protected role needs a stop-and-report exit. In CircumEval's Source-Locked tasks, a filesystem lock alone was routed around, and a "do not edit" line did not stop the Claude models.
- Treat the pilot as a reason to try this on your own tasks. It does not prove a general effect.

## Related

- [Stop-and-Report Instructions Need a Resuming Loop](stop-and-report-instruction.md) — the exit a boundary needs when it turns out wrong
- [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md) — why "do not edit" rules fail as prose
- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md) — scope exclusions as greppable rules
- [Enforced Versus Advisory Controls in LLM-Native IDEs](../security/enforced-versus-advisory-controls.md) — where a protected list must live to hold
- [Write Boundaries Ship as a Setting, Read Boundaries as a Prompt](../patterns/agent-design/write-boundary-as-setting.md) — a runtime write fence in Claude Code
