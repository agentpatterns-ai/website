---
title: "Catastrophic Remembering: Instruction Files That Only Grow"
term: "Catastrophic Remembering"
description: "Agent instruction files grow without bound because appending a rule is cheap while safely deleting one is exponential once its rationale decays."
tags:
  - anti-pattern
  - instructions
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - instruction file divergence
  - unbounded CLAUDE.md growth
last_reviewed: 2026-08-12
maturity: emerging
status: current
---

# Catastrophic Remembering: Instruction Files That Only Grow

> An instruction file diverges when adding a rule stays cheap and removing one becomes unaffordable, because the reason the rule exists is gone.

Catastrophic remembering is the unbounded growth of an agent instruction file driven by an asymmetry between two edits: appending an instruction costs O(1), while establishing that an existing instruction is safe to delete costs O(2^|D|) in a file of |D| instructions once its original rationale has decayed. Across 1,867 repositories and 247,694 instruction lifetimes, these files grew 226% over their tracked history and gained 4.9 net instructions per commit ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)).

## Disambiguation

"Catastrophic remembering" already names something else in continual learning: a model's worsening ability to discriminate between data from different tasks ([arxiv 2102.11343v1](https://arxiv.org/abs/2102.11343v1)). This page uses the 2026 agentic-coding sense, where a human maintainer keeps an instruction nobody can verify the need for.

## The pattern

An agent does something wrong. You add a line to CLAUDE.md or AGENTS.md and the behavior improves, so the line stays. It records the fix and nothing about the failure that prompted it. Months later the file has passed the observed median of 39 instructions and no one can say which lines still carry weight, so nothing comes out ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)).

Wholesale rewrites are the observed release valve, and they do not hold: growth runs at 4.1% per commit before a rewrite and 4.9% after one ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)).

## Why it fails

Deletion is a judgment about counterfactual harm, and redundancy is what makes it expensive. An instruction is excess only when removing it changes no outcome you care about. Because instructions overlap, dropping one can look harmless when a sibling line covers the same constraint today, so verifying superfluity means testing subsets rather than probing the file once with the line removed ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)). That subset search is the exponential.

The measurement separates this from ordinary drift. Staleness predicts that older instructions get deleted more often, since they describe code that has moved underneath them. The observed hazard runs the other way: the log-hazard of deletion falls 0.032 per commit of instruction age (95% CI [−0.047, −0.019]), and the slope survives adjustment for content heterogeneity ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)). A file keeps its oldest lines because nobody can justify removing them, the failure [stale AI configuration artifacts](stale-ai-configuration-artifacts.md) does not explain.

## Why it works

Recording an instruction's rationale collapses the search. When the line carries which failure it was added for and what happened afterwards, checking whether the rule is still needed means re-running that one failure, at O(1) instead of O(2^|D|) ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)). A comment removes nothing and changes no instruction, so one maintainer can adopt the habit without asking anyone. In a controlled reconstruction task, excess instruction count fell from +211.3% to +1.4% over 51 steps; on real-world prose constraints from WildIFEval, satisfaction rose from 50.4% to 62.0% over three rounds ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)).

Content is what carries that effect. Comment-shaped noise landed inside the control's error bar, and a narrative of attempts with no record of their outcomes was the worst arm measured, at +70.0% excess against a +60.4% control ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)).

## What to write instead

Write the why beside the rule at the moment you add the rule. Three elements carry the result: the failure you observed, how often it recurred, and what changed once the line was in place. Dropping the recurrence count alone costs 37% of the reduction ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)).

In Claude Code the comment is free at inference. Block-level HTML comments in CLAUDE.md are stripped before the content reaches the model's context, so they spend no tokens and stay visible to a maintainer reading the file ([Claude Code memory documentation](https://code.claude.com/docs/en/memory)). Cursor documents rule contents going into the model context with no stripping step ([Cursor rules documentation](https://cursor.com/docs/context/rules)), so budget for the tokens there or keep the rationale in a sidecar file the agent never loads.

## Example

**Before — rules with no recoverable rationale:**

```markdown
- Always run `make lint` before committing.
- Never use `pip`; use `uv`.
```

**After — the same rules with the why attached, in the shape the protocol asks for:**

```markdown
<!-- 2026-03-04: CI failed on unformatted imports 4 times in two weeks.
     Lint failures on main dropped to zero after this line landed.
     Retire once the pre-commit hook covers formatting. -->
- Always run `make lint` before committing.

<!-- 2026-05-19: an agent installed a denylisted package via `pip install`
     twice, bypassing the lockfile. No recurrence in three months.
     Retire once the dependency hook matches bare `pip`. -->
- Never use `pip`; use `uv`.
```

The dates and counts stand in for your own incident record. What transfers is the shape: each comment names the failure, its recurrence, and the outcome, so the next maintainer can test the rule rather than guess at it.

## When this backfires

- Files below a few dozen instructions. With ten rules you can test them one at a time, and the controlled experiment used minimum covers of two to three against a real-world median of 39 ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)).
- Retroactive application. The rationale for the lines already in your file is the thing that decayed, and a comment reconstructed from a guess is a fabricated license to delete.
- Narrative without outcomes. Recording why someone tried something, with no record of what followed, measured worse than writing nothing ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)).
- Safety-relevant rules. The author recommends keeping a person in the deletion path and holding these instructions out of scope until the protocol is tested on them ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)).
- Teams that will not sustain it. Around half the repositories that adopt architecture decision records hold only one to five, which the authors read as the concept being tried rather than adopted ([Buchgeher et al., IEEE Access 2023](https://doi.org/10.1109/ACCESS.2023.3287654)). A half-commented file reads as though the uncommented rules are the unjustifiable ones.
- Comments decay too. Keeping comments in sync with the code they document takes sustained time and attention, and the largest study of how the two co-evolve mined 1.3 billion syntax-tree changes across 1,500 systems to find where the inconsistencies get introduced ([Wen et al., ICPC 2019](https://doi.org/10.1109/ICPC.2019.00019)). The paper measures neither the maintenance burden of its own comments nor their staleness ([arxiv 2608.11095v1](https://arxiv.org/abs/2608.11095v1)).
- You already have evals. Where a suite scores the behavior your instructions protect, deleting a line and re-running answers the question directly. That is the argument [prompt debt](prompt-debt.md) makes.

## Key Takeaways

- Growth comes from what never leaves: the deletion hazard falls with instruction age, the opposite of what staleness predicts.
- Write the failure, the recurrence count, and the outcome beside each rule as you add it; a story with no outcome measured worse than no comment at all.
- The habit is prospective. It buys nothing for the rules already in your file, and it never licenses an unreviewed deletion.

## Related

- [Stale AI Configuration Artifacts (Context Rot)](stale-ai-configuration-artifacts.md) — the drift explanation this result rules out as the driver of unbounded growth
- [Configuration Smells in AGENTS.md Files](configuration-smells-agents-md.md) — the six recurring defects that accumulate inside the file
- [Prompt Debt](prompt-debt.md) — the competing remedy, specifying behavior with evals instead of prose
- [Deletion Avoidance](deletion-avoidance.md) — the same asymmetry one level down, where agents guard code instead of removing it
- [Reducing System-Prompt Token Bloat](../../context-engineering/system-prompt-bloat-reduction.md) — trimming the shipped prefix, a different object from the instruction file
- [The Error-Class Governance Loop for Instruction Libraries](../../workflows/instruction-library-governance-loop.md) — the standing cycle that puts the recurrence count to work and retires the rule it justifies
