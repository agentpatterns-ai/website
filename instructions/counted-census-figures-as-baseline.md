---
title: "Audit Your Agent File Against Counted Census Figures, Not Coded Ones"
term: "Counted-Figure Baseline"
description: "Zarzycki's census of 22,854 popular GitHub repositories counts adoption and file history from the API but codes content with a language model. Calibration of a separate borrowed instruction-type codebook moved Build and Run from 78.5% to 49%."
tags:
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - instruction file census baseline
  - AGENTS.md census baseline
  - counted versus coded census figures
last_reviewed: 2026-10-27
maturity: emerging
---

# Audit Your Agent File Against Counted Census Figures, Not Coded Ones

> A census counts some figures from the GitHub API and codes others with a language model; only the counted ones can become a target.

Zarzycki's census walked 22,854 popular, active GitHub repositories and read every root AGENTS.md and CLAUDE.md it found ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)). It is a good baseline to audit your own instruction file against, and it is unusually explicit about which half of its own output it trusts. Two conditions decide whether any single figure in it can be a target. First, the figure has to come from something the GitHub API settles, not from a category a model assigned. Second, your repository has to sit inside the frame the census drew.

Miss the first and you chase a number that calibration moved from 78.5% to 49%. Miss the second and you benchmark a library against a population where libraries are under-represented. Even the counted figures are frame-dependent rather than settled, which is the first item under [when this backfires](#when-this-backfires) and the reason this is a question to ask rather than a column to trust.

## The two halves of a census

| Counted from the API | Coded by a model |
|---|---|
| Whether a root AGENTS.md or CLAUDE.md exists | Whether a line is a rule, a description, or a reference |
| Which of the two names a repository uses, and which points at the other | Which subject area a rule is about |
| Word count and Markdown structure | Whether a directive carries a reason |
| Commit count and whether the file was edited after creation | What a collaboration rule requires or prohibits |
| Whether the text matches a known generator signature | What kind of project the repository is |

The left column is a file lookup or a history query. The right column is a classification, and a classification is only as good as the agreement between the classifier and a reader who would act on it.

### What the left column says

Of the 22,854 repositories in the frame, 6,006 (26.3%) carry a root AGENTS.md, a root CLAUDE.md, or both. Adoption runs from 23.2% in the lowest star tier to 59.6% of the 89 most-starred repositories, and by language from 40.8% of TypeScript projects to 13.0% of C projects ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)).

The file-name question has a clear answer. 2,566 adopters have only AGENTS.md, 1,052 only CLAUDE.md, and 2,388 both. Among those with both, CLAUDE.md defers to AGENTS.md through a link, an import, or a pointer in 1,540 repositories, the reverse in 182, and only 598 keep two files with content of their own. If you maintain two independent files, you are in a quarter of the two-file population, and the [instruction file ecosystem](instruction-file-ecosystem.md) page covers the convergence layouts that get you out.

The size question also has an answer: the median instruction set runs 818 words, with the 10th and 90th percentiles at 163 and 3,010. The files are maintained too. 81.8% were edited after creation, and 80.0% of AGENTS.md files and 67.7% of CLAUDE.md files carry more than one commit ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)).

One figure in this column comes with its own warning. 948 instruction sets (15.8%) match a signature associated with an `/init` command, 692 of them the opening line of `claude /init`, and the author declines to generalize it: "Detection is uneven across tools: claude /init leaves a verbatim line, Codex's /init only a set of headings, and other tools no signature at all, so these shares mainly measure Claude Code's generator" ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)). A counted figure can still be a measurement of one vendor.

### What the right column says, and what it cost to check

The content shares read well. On average a repository's statements are 52.6% rules, 29.8% descriptions, and 17.6% references. Rules concern code conventions in 74.4% of instruction sets, build and delivery in 72.6%, and agent workflow in 67.3%. 74.0% of directives carry no reason, while 82.9% of instruction sets give a reason at least once and only 10.8% of repositories cite an incident or evidence ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)).

Every one of those numbers came from a language model reading the files, and the paper says so on the same line as the first of them: "These are model-defined categories: human agreement is 82–83% for description versus rule (references excluded) and 43–50% for subject areas" ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)).

The check behind those ranges is small, and the paper states its limits rather than burying them. A single reviewer, the study's author, coded 60 statements blind. The reviewer "coded 60 of the 100 drawn, then stopped because the work took longer than planned", and the appendix adds that "A single coder gives no measure of agreement between humans". Within that sample, the blind reading matched the models on 82–83% of description-versus-rule calls, 62–67% of the three-way kind (κ 0.33–0.40), 43–50% of the 10 subject areas, and 32–37% of the 57-value subject taxonomy ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)).

Appendix A.7 is where the split stops being a caution and becomes a number. The author re-applied the 16 instruction types of an earlier study, calibrated against that study's 324 human-labeled files, and corrected for over-labeling. Build and Run fell from 78.5% raw to 49% corrected, with a 95% interval of 27 to 61. Configuration & Environment fell from 63.3% to 39%. Maintenance rose from 53.9% to 84%, with an interval of 55 to 100 ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)). After correction, six types had shares similar to the human-coded reference in a different sample; seven were more common, two less common and one unclear. The samples differ in frame and date, so similarity does not validate the coding ([Table 9](https://arxiv.org/abs/2610.31715v2)). A coded share can move by tens of points, and you cannot tell in advance which ones will.

## Why it works

Agreement between models does not establish agreement with a human reader. The census ran Sonnet against Opus at κ 0.76–0.89 by dimension and Haiku against Sonnet at 0.47–0.81. On project type, Haiku agreed with Sonnet at κ 0.82 and with the human reviewer's blind check at κ 0.43 (95% CI 0.23–0.63). The paper draws the conclusion itself: "Agreement among models alone therefore offers limited assurance that their categories match a human interpretation." Its own threats section names a plausible shared bias: "The models analysed files of their vendor's format; they may treat Claude-specific conventions differently from others, which we could not test directly" ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)).

The divergence is not spread evenly, and that is what makes the split operational rather than a blanket discount. Coarse binaries survived, at 82–83% on description versus rule. Fine topic assignment did not, at 32–37% on the 57-value subject taxonomy. The reason is a property of the genre, and the author states it plainly: "a command list with comments read as a rule, because in this genre one line often describes, refers and instructs at once" ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)). An instruction file does several things per line. A classifier has to pick one, and a reader picks differently.

## How to apply it

Before you make a census figure a target for your own file, ask three questions in order.

1. Was it counted or coded? If the figure is a file lookup, a word count, or a commit count, it is counted. If it names a category (a rule, a subject, a reason, a project type) it is coded, and its value is a lead for a conversation rather than a target.
2. Is my repository in the frame? The frame is public repositories with at least 1,000 stars, pushed to within 90 days, not forks and not archived, in thirteen named languages, on 2026-10-16 ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)). Nested agent files are out of scope entirely.
3. Is my project in the over-represented slice? Projects about LLMs, generative AI, or agents are 27.9% of adopters against 13.3% of matched controls, an odds ratio of 2.76 within star tier and language, falling to 1.54 once age and activity are held fixed and agent-tooling projects are excluded. Libraries sit at OR 0.58 and documentation repositories at 0.50 ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)).

Question 3 runs on coded figures, which is deliberate and worth being explicit about. Project type was classified by a model and the paper scopes it accordingly: "so type contrasts are indicative; AI focus is more reliable", putting the latter at κ 0.80. That is the right strength for this use. A coded figure is a reason to doubt a frame, and never a target inside one.

A worked case. The 74.0%-of-directives-carry-no-reason figure is the most quotable number in the paper and the one most likely to become a target. It comes from the rationale dimension. The blind human check did not cover that dimension, and the paper warns: "These checks do not validate every subsequent category or stance assignment" ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)). Use it as the prompt it supports — go and look at whether your own rules say why — rather than as a percentage to drive down. The practice of attaching a reason to each rule stands on its own argument, which [rule lifecycle metadata](rule-lifecycle-metadata.md) makes. This census tells you the practice is uncommon, and it measured no effect: "Whether reasons or emphasis change what agents do remains open."

## When this backfires

- You read "counted" as "settled". The census reports 81.8% of instruction sets edited after creation, then notes that a sibling study "found that half of their AGENTS.md files had never changed". The census reports these different edit shares without reconciling the populations. Adoption behaves the same way. The paper's own related work reports "adoption estimates from 5% of mature repositories" up to 21.7% of agent-using ones, against its own 26.3%, under other definitions ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)). Counted means no model assigned a category. It does not mean frame-independent.
- The counted figure has a known blind spot you skipped. Internal validity names two: "History covers only files that survive at the snapshot, and path history does not follow renames; a rename check bounds the second effect." The paper estimates that renames explain 3.8% of AGENTS.md-first cases (95% CI 2.6–5.3). The adoption snapshot sits four weeks after Claude Code began reading AGENTS.md, so "recent shares may reflect that change" ([Zarzycki, 2026](https://arxiv.org/abs/2610.31715v2)).
- You discard the coded half entirely. Six of the sixteen calibrated instruction types had shares similar to the human-coded reference in a different sample. Broad subject areas had only 43–50% human agreement. Use those topics as prompts for inspection; the paper reports no rank-order reliability result.
- You expect the census to tell you what to write. It makes no effect claims and offers no practitioner recommendations. Every "you should" on this page is this site's argument about how to read a descriptive study, and the three-question check is ours, not the author's.
- You apply the split to a study that never published its calibration. This census is auditable because its author ran a human check and reported the acceptance rates, the stopping point, and the single-coder limitation. A corpus study with no human-coded sample gives you nothing to sort its figures by, and the honest move is to treat its whole content half as a lead.

## Key Takeaways

- Of 22,854 repositories with 1,000+ stars and a push in the last 90 days, 6,006 (26.3%) carry a root AGENTS.md or CLAUDE.md. It is a file lookup, so it is a baseline for that frame and not for open source generally.
- Calibrating the borrowed 16-type instruction codebook against 324 human-labeled reference files moved Build and Run from 78.5% to 49%, with an interval of 27 to 61. That change concerns this codebook and sample.
- On project type, the study's cheapest model agreed with its mid-tier model at κ 0.82 and with its single human coder at κ 0.43, so model consensus bounds reproducibility and not validity.
- Inside the coded half there is a gradient worth knowing: human agreement held at 82–83% on the description-versus-rule binary and fell to 32–37% on the 57-value subject taxonomy, so the finer the category, the less the share means.
- The adopter population over-represents LLM and agent projects (27.9% against 13.3% of matched controls) and under-represents libraries (OR 0.58), so check your project type before treating the census as what open source does.

## Related

- [Public Rules-File Corpora as Evidence](rules-file-corpus-evidence.md) — the same discipline applied to `.cursorrules` corpora, which explicitly scopes itself away from the AGENTS.md population this census measures
- [Empirical Baseline: How Developers Configure Agentic AI Coding Tools](empirical-baseline-agentic-config.md) — a second repository-scale baseline, covering configuration mechanisms rather than instruction-file content
- [Agent Context File Evolution: Treating ACFs as Configuration Code](agent-context-file-evolution.md) — the edit-history half of this census read as a maintenance argument
- [Project Instruction File Ecosystem](instruction-file-ecosystem.md) — the convergence layouts behind the split between pointer files and independent ones
- [Rule Lifecycle Metadata for Prunable Instruction Surfaces](rule-lifecycle-metadata.md) — the practice that the 74.0% no-reason figure describes the absence of, argued on its own evidence
