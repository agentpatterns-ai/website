---
title: "Encoding AI Writing Tells as a Prose Style Contract"
term: "AI Writing Tells"
description: "A catalog of AI writing tells works as a revision standard for all prose. Which entries to enforce mechanically, and which carve-outs to write first."
aliases:
  - Better Tropes catalogue
  - AI writing tells
  - sentence-shape style rules
tags:
  - instructions
  - tool-agnostic
last_reviewed: 2026-08-21
maturity: emerging
---

# Encoding AI Writing Tells as a Prose Style Contract

> A catalog of AI writing tells belongs in the instruction file as a revision standard for all prose, never as an authorship test.

Adopt a tell catalog under two conditions: it governs every piece of prose regardless of who wrote it, and only the entries with a narrow false-positive surface become blocking checks. [Better Tropes](https://github.com/fromfireside/better-tropes) is the reference set, "a catalogue of 49 AI writing tells, each with a plain rewrite", released under CC BY 4.0 with the instruction to "Paste it into a system prompt, a `CLAUDE.md`, a Cursor rule, or an agent skill." Under those conditions it gives reviewers words for an objection that otherwise arrives as taste.

## The layer most style guides skip

A house style guide usually governs word choice: banned marketing verbs, active voice, plain alternatives to Latinate vocabulary. The tell catalog puts 8 of its 49 entries there. The other 41 sit under Sentence Structure, Paragraph Structure, Tone, Formatting, Composition, and Whole-Piece Patterns ([Better Tropes](https://github.com/fromfireside/better-tropes)). Sentence Structure names the shapes reviewers keep noticing without being able to say what they noticed: the "It's Not X - It's Y" antithesis, the rule-of-three cadence, the empty analysis tail (a sentence trailing off into `, ensuring…`), and anaphora.

Scope the claim honestly. Across 284 interpretable linguistic features, outputs from 27 models, and ten text domains, "many previously proposed indicators prove strongly context-dependent, with the exception of measures of lexical richness, which remain robust signals across model families and text domains" ([arXiv:2606.04177v1](https://arxiv.org/abs/2606.04177v1)). The durable authorship signal is lexical. What sentence shape buys is a name for a defect and a rewrite that fixes it.

## Why it works

Model prose converges on a small set of constructions because preference tuning rewards familiarity. Zhang et al. identify "typicality bias in preference data, whereby annotators systematically favor familiar text as a result of well-established findings in cognitive psychology" and show "it plays a central role in mode collapse" ([arXiv:2510.01171v4](https://arxiv.org/abs/2510.01171v4)). Annotators rate the more conventional of two adequate responses higher, and alignment sharpens the output distribution onto those conventions. Sentence architecture is where the sharpening shows, because one page repeats it dozens of times. Stylometry finds the same residue, attributing classification performance to "individual overused words, as well as a greater grammatical standardisation of LLMs with respect to human-written texts" ([arXiv:2507.00838v2](https://arxiv.org/abs/2507.00838v2)).

## What to enforce mechanically

Sort the entries by false-positive surface. How bad a tell reads is the wrong sort key, because it says nothing about whether a check can decide the case. An em-dash count per paragraph, a literal "not only… but also", a trailing `, ensuring` clause, an emoji used as a heading marker: each is a regular expression with a decidable answer, and each belongs in a linter that blocks. Rule-of-three cadence, uniform paragraph rhythm, and heading inflation need a human to read a section and judge it, so they belong in a review rubric and in the instruction file the drafting agent reads. Pasting all 49 into that file spends rule budget on top of everything else it carries ([The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)).

Shipping the judgement half as a blocking check is the expensive mistake. An overload of alerts produces "alert fatigue", where developers "become desensitized to warnings, potentially overlooking critical issues" ([arXiv:2511.10323v1](https://arxiv.org/abs/2511.10323v1)). Wrong findings are not the only ones ignored: across 1,425 Java projects, "contrary to expectations, false positives account for a minor proportion of suppressions" ([arXiv:2311.07482v1](https://arxiv.org/abs/2311.07482v1)). Unclear findings get suppressed too, so advisory severity is the right home for anything a writer cannot resolve in one edit.

## Write the carve-outs before the bans

The authors say "it works unmodified, but it works better tuned to your workflow", because "a technical blog post is not a social post is not a listicle" ([Better Tropes](https://github.com/fromfireside/better-tropes)). On a reference corpus that caveat decides the whole adoption. At least five entries name things the format requires: The Definition Opener, The Restated Heading, The Signposted Conclusion, Heading Inflation, and Invented Concept Labels. A documentation site opens on definitions, restates its heading as a summary line, carries dense retrievable headings, and names the concepts it defines.

Terminology carries the same risk. A ban aimed at inflated abstraction nouns will reach a page about agent harnesses and strip the word "harness". Write the exemption list next to the rule, in the same file the agent reads.

## When this backfires

- Applied to code review. Detection of machine-written code collapses on the mixed case that describes every agent-assisted diff. The CoDet-M4 study's best model scores 98.65 F1 in-domain and 39.36 F1 on code combining human- and machine-written portions, where the authors write "our best model completely fails the task" ([arXiv:2503.13733v2](https://arxiv.org/abs/2503.13733v2)). Scope the contract to prose.
- Used as an authorship test. Across six experiments, "participants (N = 4,600) were unable to detect self-presentations generated by state-of-the-art AI language models", and their judgments were "hindered by intuitive but flawed heuristics" the authors then show to be "predictable and manipulable" ([arXiv:2206.07271v4](https://arxiv.org/abs/2206.07271v4)). A reviewer treating a tell as evidence of authorship inherits that error rate.
- Expected to keep firing. The stated deployment is a system prompt, so a model given the catalog stops producing the listed shapes. Their absence then proves nothing, and whatever replaces them is unlisted.
- Adopted unmodified on a reference corpus. Enforcement without the carve-outs above deletes the definition openers, summary lines, and coined terms the format depends on.
- Calibrated once. Structural indicators are "strongly context-dependent" across model families ([arXiv:2606.04177v1](https://arxiv.org/abs/2606.04177v1)), so a rule set tuned on one model generation decays against the next.

## Example

Two entries from the same catalog, one mechanical and one not.

The antithesis frame has a literal shape, so one grep finds every instance in a docs tree:

```bash
grep -rnEi "(is|are|was|were) not (an?|the) [^,.]+, it'?s" docs/
```

**Before** — a specimen the check catches, carrying a term the word-choice bans must not touch:

> The harness is not a convenience layer, it's a contract between the agent and the repository.

**After** — the positive claim, with "harness" left alone:

> The harness is a contract between the agent and the repository.

Uniform rhythm is the other kind. Three consecutive paragraphs of four medium sentences each read as template slots, and no regular expression separates that from a section where four sentences is the right length. A reviewer settles it in one read; a linter reports a number nobody can act on. Put the first entry in the build and the second in review.

## Key Takeaways

- Adopt the catalog as a standard for all prose in the repository. Scoping it to agent-written text turns a style rule into an authorship claim the evidence does not support.
- Sort entries by whether a writer can resolve the finding in one edit. That predicts whether a rule survives contact with a review queue better than how serious the tell is.
- Draft the exemption list in the same commit as the ban, and keep both in the file the drafting agent reads, so the agent never has to guess which technical terms are safe.
- Budget for recalibration when the drafting model changes, and read a tell that stops firing as evidence the model learned the rule.
- Preserve the CC BY 4.0 attribution wherever the catalog's text lands, including a system prompt or an instruction file in a private repository.

## Related

- [Standards as Agent Instructions for AI Agent Development](standards-as-agent-instructions.md) — the general case: one precise document serving human reviewers and agents alike
- [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md) — why the judgement half of the catalog needs CI or required review rather than a prompt line
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md) — the enforcement mechanism for the mechanically-checkable subset
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — the rule-count cost of pasting all 49 entries into the file the agent loads
- [Slop Detectors Fail as Per-Item Review Gates](../verification/slop-detection-as-review-gate.md) — the measured case against treating any of these signals as an authorship gate

## Sources

- [fromfireside/better-tropes](https://github.com/fromfireside/better-tropes) — the 49-entry catalog, its seven sections, its CC BY 4.0 license, and the system-prompt deployment its authors recommend.
- [arXiv:2510.01171v4](https://arxiv.org/abs/2510.01171v4) — Zhang et al., "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity".
- [arXiv:2606.04177v1](https://arxiv.org/abs/2606.04177v1) — El Attar et al., "A Systematic Analysis of Linguistic Features in AI-Generated Text Detection Across Domains and Models".
- [arXiv:2507.00838v2](https://arxiv.org/abs/2507.00838v2) — Przystalski et al., "Stylometry recognizes human and LLM-generated texts in short samples".
- [arXiv:2206.07271v4](https://arxiv.org/abs/2206.07271v4) — Jakesch, Hancock, Naaman, "Human heuristics for AI-generated language are flawed".
- [arXiv:2511.10323v1](https://arxiv.org/abs/2511.10323v1) — Kószó et al., "A Large-Scale Collection Of (Non-)Actionable Static Code Analysis Reports".
- [arXiv:2311.07482v1](https://arxiv.org/abs/2311.07482v1) — Liargkovas et al., "Quieting the Static: A Study of Static Analysis Alert Suppressions".
- [arXiv:2503.13733v2](https://arxiv.org/abs/2503.13733v2) — "CoDet-M4: Detecting Machine-Generated Code in Multi-Lingual, Multi-Generator and Multi-Domain Settings".
