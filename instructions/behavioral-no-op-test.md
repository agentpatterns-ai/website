---
title: "The No-Op Test: Prune Agent Docs by Behavior, Not Length"
term: "Behavioral No-Op Test"
description: "Delete a line from an agent-facing document and rerun the task. If behavior does not move, the line was a no-op. Prune by behavior, not by length."
tags:
  - instructions
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - No-Op Test
  - Behavioral Deletion Test
last_reviewed: 2026-08-06
maturity: emerging
---

# The No-Op Test: Prune Agent Docs by Behavior, Not Length

> A no-op is a line the model already obeys by default. Delete it, rerun the task, and check whether behavior moved.

The no-op test decides whether a single line in an agent-facing document earns its place. Remove the line, rerun a task it governs, and compare the result against the unedited run. A line that changes nothing restates a default the model already holds, so it spends tokens and attention to buy nothing. The test covers every document an agent reads, because a skill, an `AGENTS.md`, a spec, and a ticket differ in packaging rather than in craft ([Pocock, writing-for-agents](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md)).

## When this applies

Spend the effort on token budget and maintenance, not on compliance. The one factorial study to manipulate configuration-file structure across 1,650 Claude Code sessions found no detectable contrast from file size, instruction position, file architecture, or contradictions between adjacent files ([McMillan, 2026](https://arxiv.org/abs/2605.10039v1)). Shorter files did not obey better, so [file structure is not the compliance lever](configuration-file-structure-compliance-gap.md).

Run each deletion against a task that exercises the line. A rule about recovery from a failed build reads as a no-op on any task where the build passes.

Exempt the constraints you repeat on purpose. Repeating an input prompt improved results across Gemini, GPT, Claude, and Deepseek without extra generated tokens or latency ([Leviathan et al., 2025](https://arxiv.org/abs/2512.14982v1)), which is the same finding behind [critical instruction repetition](critical-instruction-repetition.md).

## Running the test

1. Pick one candidate sentence.
2. Choose a task whose correct completion depends on that sentence.
3. Delete the whole sentence rather than trimming words inside it ([Pocock](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md)).
4. Run the task with and without the sentence, several times each.
5. Keep the sentence only if the runs diverge.

Asking an agent to shorten the document is not this test. Agents told to streamline optimize for length, because length is the thing they can see ([AI Hero](https://www.aihero.dev/skills-writing-for-agents)). Two reviewers who disagree about a no-op are disagreeing about the model's default, which a run settles and an argument does not.

## Context load and cognitive load

Every line and every pointer spends one of two budgets ([AI Hero](https://www.aihero.dev/skills-writing-for-agents)):

| Budget | Paid by | What it covers |
|---|---|---|
| Context load | The agent's window | Always-loaded material: an `AGENTS.md` line, a skill description, anything present every turn whether or not it fires |
| Cognitive load | The human | Knowing which documents exist and when to reach for each |

Most authoring decisions are this trade made in different places: split or not, inline or disclose. Material behind a pointer costs only the pointer's own line until it fires, so a rule that applies in one session out of ten pays context load the other nine. A third destination costs neither budget: the environment is a source of truth too, and a document that restates `package.json` scripts or `--help` output is a cache of a cheap lookup ([Pocock](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md)).

## Why it works

A no-op has zero expected effect on behavior by construction and a positive cost, so its removal is free. It needs a test because the default is a property of the model, not of the prose, and no reading tells you where the default sits. Instruction-following also degrades as instruction density rises, with the best frontier models reaching 68% accuracy at 500 instructions ([Jaroslawicz et al., 2025](https://arxiv.org/abs/2507.11538v1)), so dead lines compete for attention with live ones. The [instruction compliance ceiling](instruction-compliance-ceiling.md) is the budget this frees.

## When this backfires

- Sparse operational anchors read as no-ops. A CLI flag, a validation threshold, or a recovery rule shows no effect on a happy-path task, and removing it makes the agent explore and retry instead. Shorter skills can raise total cost for exactly this reason ([Xing et al., 2026](https://arxiv.org/abs/2606.09421)), which is the argument in [cost-aware skill rewriting](cost-aware-skill-rewriting.md).
- Compliance decay inside a session swamps the edit. In the same factorial study, each additional function the agent generated carried roughly 5.6% lower odds of compliance ([McMillan, 2026](https://arxiv.org/abs/2605.10039v1)). Shorter sessions fix that; rewriting the file does not.
- A pruned document is a calibration against one model. Qwen-tuned repository guidance applied to Nemotron scored 13.2% resolve rate against Nemotron's own 27.0% ([Shepard & Albrecht, 2026](https://arxiv.org/abs/2606.20512v2)), the tuning risk described in [probe-and-refine guidance tuning](probe-and-refine-guidance-tuning.md).
- The loop costs a model run per candidate line, and one run cannot separate a no-op from sampling variance. On a short document the audit costs more than it recovers.

## Example

The instruction "be thorough" fails the test on most tasks, because agents already attempt thoroughness. Deleting it changes nothing, which makes it a no-op rather than a weak instruction. The repair is a stronger word that beats the default, such as "relentless", not a different technique ([Pocock](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md)).

The same source names the opposite error. Doing the work once and asking the agent to write it up as a skill over-indexes on that single run, so the exemplars come out bound to those files and that repository ([AI Hero](https://www.aihero.dev/skills-writing-for-agents)). Keep the run as evidence, then write for the class of task.

## Key Takeaways

- Pick the probe task before the candidate line. A task that already succeeds cannot tell an anchor apart from a no-op.
- Run each variant several times. One run per variant measures sampling noise, not the line.
- Send what survives to the cheapest budget first: the environment, then a pointer, then always-loaded.
- Repeat the pass after a model change, since the defaults the document was calibrated against have moved.
- Never hand the pass to an agent as "streamline this" — that instruction names the wrong variable.

## Related

- [Configuration File Structure Does Not Drive Compliance](configuration-file-structure-compliance-gap.md) — the factorial study that bounds what pruning can buy
- [Cost-Aware Skill Rewriting: Preserve Operational Anchors, Not Skill Tokens](cost-aware-skill-rewriting.md) — why the shortest version of a document can cost the most
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — the density limit that makes freed budget worth having
- [Critical Instruction Repetition: Exploiting Primacy and Recency Bias](critical-instruction-repetition.md) — the constraints to exempt from single-source-of-truth
- [Rule Lifecycle Metadata for Prunable Instruction Surfaces](rule-lifecycle-metadata.md) — metadata that tells you which rules to test first
- [Against-Prior Accuracy: Score the Rules That Fight Defaults](../verification/against-prior-accuracy.md) — the same deletion probe pointed at a compliance score instead of a pruning decision
