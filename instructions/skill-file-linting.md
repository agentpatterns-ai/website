---
title: "Skill File Linting: Which Three Checks to Run First"
term: "Skill File Linting"
description: "Three mechanical checks catch most SKILL.md structural defects. When the gate pays, what it buys, and why a green result is not a safety verdict."
aliases:
  - SKILL.md linting
  - skill defect checks
  - skill hygiene gate
tags:
  - instructions
  - tool-agnostic
  - skills
  - arxiv
last_reviewed: 2026-08-11
maturity: emerging
---

# Skill File Linting: Which Three Checks to Run First

> Three mechanical checks on a SKILL.md catch most structural defects, buying routing and review hygiene rather than a safety verdict.

Start a skill linter with three rules: a description of at least 30 characters shaped `[Verb] [what]. Use when [trigger].`, no H1 heading that repeats the frontmatter name, and code and examples moved out of the body into supporting files. Measured across 138,133 deduplicated SKILL.md files from 20,556 repositories, those three cover 71.9% of detected defect instances while flagging 85.9% of skills ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)).

## When the gate pays

Three conditions decide whether the gate returns anything.

| Condition | Why it matters |
|---|---|
| Selection is already failing | Below the scale where the agent picks the wrong skill, routing hygiene guards a problem that has not started. See [Skill Loadout Curation](../context-engineering/skill-loadout-curation.md). |
| Several people author into one library | A mechanical check keeps description shape consistent across authors. |
| Skills are generated, not hand-written | Agent-authored skills carry measurably more defects (below), and a generation loop outruns human review. |

## The three checks

Each rule targets one high-prevalence defect class ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)).

| Check | What it flags | Share of corpus |
|---|---|---|
| Description shape | Missing, too-short, or non-functional trigger guidance in frontmatter | 52.3% |
| Name-as-heading | Frontmatter `name` repeated as the body's H1 | 44.3% |
| Externalized resources | Bodies over 60% code, or carrying more than eight example blocks. See [CLI-First Skill Design](../tool-engineering/cli-first-skill-design.md) for the target shape | 37.0% |

The full taxonomy runs to 31 checks and flags 91.8% of the corpus ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)); the subset reaches most of those defects far more cheaply.

## What a green result does not tell you

These checks read structure and never execute the skill, so three failure classes pass straight through.

Fuzzing 402 deployed skills with benign inputs found 120 of them (29.9%) violating rules they declare in their own text ([arXiv:2605.13044v1](https://arxiv.org/abs/2605.13044v1)). Where two skills serve the same capability, description quality does not decide which variant fires; within-family representative selection does, and removing it raises the harmful-sibling rate at top-3 from zero to 0.236 ([arXiv:2606.10388v1](https://arxiv.org/abs/2606.10388v1)). A GPT-4o-mini repair pass over 200 defective skills fixed 58.4% of detected defects while introducing 0.06 new ones per skill, and fixed 0% of safety bypass patterns and injection attempts ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)).

Treat the gate as a precondition for review, never a substitute for [skill evals](../verification/skill-evals.md) or runtime enforcement.

## Agent-authored skills need it most

Provenance is the study's strongest quality signal. Spec-aware skills average 1.83 defects against 3.00 for spec-unaware ones. Of the 19,857 skills marked as AI-generated, 14.4% of the corpus, the average rises to 3.23 defects against 2.34 for unmarked ones. The gap concentrates where it hurts: safety defects appear in 18.9% of AI-marked skills versus 8.2% of unmarked, and portability defects in 12.8% versus 4.6% ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)). A loop like [introspective skill generation](../workflows/introspective-skill-generation.md) should carry the gate on its output path rather than in a quarterly sweep.

## Why it works

Two mechanisms sit behind the recommendation, and only one is measured. The prioritization result is arithmetic on a long tail: defect instances concentrate in three classes, so three checks reach 71.9% of them. That ordering follows prevalence, not harm. The routing mechanism is measured directly. A selector sees the description before any body loads, so a description with no trigger guidance offers nothing to match a task query against. On a BM25 index over roughly 20,000 skills, routing-clean skills reached 88.5% hit@1 and 0.906 MRR against 82.6% and 0.855 for routing-defective ones. Name-and-path-only queries collapsed both arms to about 25%. The description does the work, not the filename ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)).

## When this backfires

- Semantic selection. The 5.9-point gap was measured under lexical BM25 retrieval, and the authors expect it to compress under the LLM-based selection production harnesses use ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)).
- Chasing body size for speed. Shrinking bodies targets context overhead, which measures as indistinguishable from zero next to skill shadowing ([arXiv:2605.24050v2](https://arxiv.org/abs/2605.24050v2)). Externalizing code buys reviewability and reuse, not agent throughput.
- Security and role-specialized skills. Regex detectors fire legitimately on injection patterns inside security-auditing skills and on persona redefinition inside specialized roles ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)), so a blanket gate produces its worst false-positive rate on the files most worth reading.
- Reading the corpus as your library. 47.0% of repositories contribute exactly one skill, and one repository supplies 12.9% of the corpus ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)). The 91.8% headline describes publishing habits as much as authoring quality.

## Example

A carefully written skill can still trip one of the three checks. The `check-arxiv-tou` skill in this site's own harness carries a description in exactly the shape the description check asks for, and an H1 that restates its own name.

**Before** — frontmatter and opening of `.claude/skills/check-arxiv-tou/SKILL.md`:

````markdown
---
name: check-arxiv-tou
description: Validate arxiv API Terms of Use compliance — no hosted e-prints,
  full abstracts, or endorsement claims. Invoke when adding arxiv citations or
  after arxiv-scrape. Skip when pages cite no arxiv papers.
---

# Check arxiv ToU

Validates that docs pages and scripts comply with the arxiv API Terms of Use.
````

The description passes. It opens on a verb, names what it validates, and carries both an invoke-when trigger and a skip condition. The H1 fails, spending the reader's first line restating `name`.

**After** — the heading carries what the frontmatter does not:

````markdown
# Six arxiv Terms-of-Use rules for docs pages and scripts

Ordered by severity, from hosted e-prints (CRITICAL) through missing
abstract-page links (HIGH) to endorsement language (MEDIUM).
````

Two of the three checks are this cheap to clear. The third, externalizing code, changes the file's shape rather than its wording, which is why it is worth running as a gate instead of a style note.

## Key Takeaways

- Run three checks before adopting a 31-check standard: description shape, no name-as-H1, and externalized code and examples ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)).
- Expect the first pass to flag most of the library. At corpus scale the three rules flag 85.9% of skills, so budget for a bulk fix rather than a handful of exceptions ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)).
- The measured payoff is lexical retrieval hygiene worth about six points of hit@1, and the authors expect it to shrink under semantic selection ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)).
- Gate generated skills hardest. AI-marked skills carry 2.3 times the safety defects and 2.8 times the portability defects of unmarked ones ([arXiv:2608.08453v1](https://arxiv.org/abs/2608.08453v1)).
- Never read green as safe. Auto-repair fixes none of the safety class, and 29.9% of deployed skills breach their own declared rules on benign input ([arXiv:2605.13044v1](https://arxiv.org/abs/2605.13044v1)).

## Related

- [Contractual Skill Files](contractual-skill-files.md) — a governance schema for the same file; this page is the mechanical floor beneath it
- [Skill Authoring Patterns](../tool-engineering/skill-authoring-patterns.md) — the canonical description-craft and implementation-shape catalog that these checks enforce a subset of
- [Skill Authoring as Software Engineering](../tool-engineering/skill-authoring-software-engineering.md) — which construction principles independent measurement supports, and why guidance without a detector changes nothing
- [Skill Library Technical Debt](../tool-engineering/skill-library-technical-debt.md) — library-level defects that per-file linting cannot see
- [Skill Specification Violation Fuzzing](../verification/skill-specification-violation-fuzzing.md) — the behavioral layer a structural gate leaves untouched
