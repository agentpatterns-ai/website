---
title: "Per-Step Preconditions and Postconditions in Skill Files"
term: "Per-Step Skill Specifications"
description: "Give each skill step a precondition and a postcondition so a reviewer can compare declared intent against implementation. It finds defects; it enforces nothing."
aliases:
  - skill preconditions and postconditions
  - per-step skill contracts
  - ExpectSpec and FactSpec
  - Hoare-style skill specification
tags:
  - instructions
  - tool-agnostic
  - skills
  - arxiv
last_reviewed: 2026-09-09
maturity: emerging
---

# Per-Step Preconditions and Postconditions in Skill Files

> Write each skill step's precondition and postcondition where the step has a checkable output, so a reviewer can compare declared intent against implementation.

Give each step in a `SKILL.md` two lines: what must hold before it runs, and what must be true after. That hands a reviewer or a checker two descriptions of the same step, derived separately, and the comparison between them is what finds defects. SkillSpec confirmed 763 defects across 239 of 515 real-world skills that way, at 61.2% precision ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)).

## When this pays

Three conditions decide whether the two lines return anything.

- The step produces something checkable. SkillSpec reaches 67.1% precision on code defects against 55.4% on workflow defects, because "executable code exposes explicit behavioral signals" whereas "workflow defects depend more heavily on contextual interpretation" ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)). A postcondition over a prose judgment step gives you much less to compare against.
- The skill bundles scripts with instructions. 91.6% of code defects were implementations departing from established intent, so the mismatch lives where the two artifact types meet ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)).
- More than one person writes or reviews the library. A human or a tool has to read the conditions for the cost to come back.

Where the step is a judgment call with no verifiable output, keep the prose and spend the effort on a runtime check.

## The two descriptions

SkillSpec names both halves as classical Hoare triples, `{Pre} C {Post}`, where `C` is the step's behavior. The ExpectSpec "captures the behavior prescribed by the complete declared intent and its constraints". The FactSpec is read off the implementation "under deliberately masked intent", so the fact-side reading cannot quietly echo what the skill already promised. A discrepancy between them "constitutes a defect hypothesis rather than proof of incorrectness" ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)).

How much intent to hide is the design question, and it cuts both ways: "Exposing the surrounding intent may bias factual extraction toward the expected behavior, whereas excessive masking may remove the context needed to interpret the implementation correctly" ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)).

## Why it works

Constraints scattered through narrative prose produce no per-step expectation, so there is no second description and nothing to compare. The mismatch is then absorbed at runtime rather than failing, which is what the paper means by "silent failures masked by the underlying model" ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)). Writing the condition beside the step creates the missing half. How the two are then compared matters as much as having both: reasoning across all four intent-mask views confirmed 261 defects at a 48.2% confirmation rate, against 228 to 236 for any single view, without a larger candidate pool ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)).

## What the comparison finds

The confirmed defects split by artifact type, and the split tells you where to look ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)):

| Category | Workflow defects | Code defects |
|---|---|---|
| Requirement error | 149 (43.1%) | 7 (1.7%) |
| Implementation deviation | 90 (26.0%) | 382 (91.6%) |
| Semantic conflict | 61 (17.6%) | 0 (0.0%) |
| Constraint omitted | 46 (13.3%) | 28 (6.7%) |

Prose steps fail at requirement formulation. Code steps drift from intent already stated. The same two lines catch different defects on each half.

## When this backfires

- Read as enforcement. A declared precondition does not get honored. Across SLBench's 86 executable cases, unsafe rates ran from 35.1% (Claude Code with Opus 4.7) to 70.2% (Codex with GPT-5.5), with violations producing privacy leaks and incomplete cleanup ([arXiv:2607.09016v1](https://arxiv.org/abs/2607.09016v1)). Pair the lines with a hook or validator that stops the action.
- Expected to fix compliance by wording alone. SLBench rewrote skills to make the relation salient and violations fell from 11 of 12 cases to 5 of 12, with annotators having already marked 0 of 12 originals ambiguous ([arXiv:2607.09016v1](https://arxiv.org/abs/2607.09016v1)). Wording halves the problem and leaves the rest to model capability.
- Added to an already-crowded instruction file. Two lines per step multiplies rule count, and "even the best frontier models only achieve 68% accuracy at the max density of 500 instructions" ([IFScale, arXiv:2507.11538v1](https://arxiv.org/abs/2507.11538v1)). See [the instruction compliance ceiling](instruction-compliance-ceiling.md).
- The declared intent is itself wrong. SkillSpec "evaluates only the intent expressed in skill artifacts and cannot determine whether it fully captures the author's latent intent" ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)). A faithful specification over a mistaken requirement passes clean.
- Triage capacity is the constraint. At 61.2% precision roughly two flags in five cost review time and return nothing. Recall is not measurable either: "We can estimate precision over reported and validated candidates but cannot measure recall" ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)).

## Example

**Before** — the constraint is real but scattered, and nothing pins it to the step that must honor it.

```markdown
## Publishing

This skill publishes the built page. Publishing is destructive, so
be careful with the target branch. Always work from a clean tree.

1. Build the page with `make build`.
2. Run `scripts/publish.py --branch <name>`.
```

**After** — each step carries its own two lines, and `publish.py` can now be read against them.

```markdown
## Publishing

1. Build the page with `make build`.
   - Requires: `git status --porcelain` is empty.
   - Ensures: `site/index.html` exists and is newer than `docs/`.
2. Run `scripts/publish.py --branch <name>`.
   - Requires: `<name>` is not `main` or `production-deploy`.
   - Ensures: the command exits non-zero if the branch check fails.
```

The second `Requires` line is falsifiable in one grep of `publish.py`. If the script accepts any branch name, the ExpectSpec and the FactSpec disagree and a reviewer sees it without running anything. The `Ensures` line is what a hook then enforces.

## Key Takeaways

- Write the two lines only where the step has a verifiable output. On a prose judgment step there is nothing to check them against ([arXiv:2609.06052v1](https://arxiv.org/abs/2609.06052v1)).
- The comparison finds the defect, not the writing. One description of a step tells you nothing.
- Attach them to prose steps to catch requirement errors, to code steps to catch drift from intent already stated.
- Keep enforcement somewhere else. A precondition line is what a reviewer reads; a hook is what stops the action.
- Budget the triage before rolling this across a library, and start on the skills that ship scripts.

## Related

- [Contractual Skill Files](contractual-skill-files.md) — the governance-field schema for the whole skill, where these per-step conditions are the finer-grained layer underneath
- [Skill File Linting](skill-file-linting.md) — the mechanical structural checks to run before any semantic comparison is worth the cost
- [Typed Pseudocode for Skill Libraries](typed-pseudocode-skill-libraries.md) — counter-evidence that a type contract alone can test below the prose it replaced
- [Skill Specification Violation Fuzzing](../verification/skill-specification-violation-fuzzing.md) — the dynamic half, which finds the runtime violations a static comparison cannot
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — why adding two lines per step can cost more compliance than it buys
