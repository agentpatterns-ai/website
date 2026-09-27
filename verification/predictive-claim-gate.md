---
title: "Verify Agent Diagnoses and Fix Proposals Before Acting"
term: "Predictive-Claim Gate"
description: "A Claude-built codebase scored design-fix proposals 79.4% accurate, versus 94.3% for facts, narrowing to 93.4% once rejected proposals are excluded."
aliases:
  - predictive-claim gate
  - verify before adopting a fix proposal
  - claim-type verification gate
tags:
  - testing-verification
  - human-factors
  - claude
  - arxiv
last_reviewed: 2026-09-26
maturity: emerging
status: current
---

# Verify Agent Diagnoses and Fix Proposals Before Acting

> Verify an agent's diagnosis or fix proposal before you act on it, since it is a prediction and not a settled fact.

A checkable fact can be settled by reading the code the agent already wrote. A root-cause diagnosis or a design-fix proposal describes something that has not happened yet, so nothing in the current repository confirms it. A study of a 21,000-line Python codebase built entirely by Claude found that gap in the numbers: design-fix proposals were accurate 79.4% of the time against 94.3% for checkable facts, and the gap narrowed to 93.4% once proposals the developer had already turned down were excluded from the count ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)).

## What the data covers

The dataset is Extractor, a single reverse-engineering tool. "Extractor is 21,000 lines of production code with a comparably sized test suite, built over 210 commits and 25 sessions from 678 user instructions. It was entirely built using Claude AI models over a period of several weeks. No code, test, or commit in its history has human authorship" ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)). Two LLM scorers graded about 3,900 of 6,818 response components, and a human checked 200 deficient verdicts and a stratified sample of 200 clean ones (49 to 51 per category), agreeing with the AI verdicts 93.3% to 98.2% of the time by category ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)).

One developer, one codebase, and unusually heavy self-checking: 18.73% of that developer's instructions were classed as Validation, against 3.99% in a comparison corpus of IDE-chat instructions ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)). Read the numbers below as a rate from that project, not one that carries over unchanged to a thinner review habit.

## The gap between claim types

Table VIII in the paper scores four kinds of response component. The Claude scorer found:

| Claim type | Accuracy | Sample |
|---|---|---|
| Checkable fact | 94.3% | 2,321/2,461 |
| Mechanism explanation | 91.1% | 381/418 |
| Root-cause diagnosis | 89.3% | 275/308 |
| Design-fix proposal | 79.4% | 565/712 |

A second scorer, Codex GPT-5.6, landed close to these on every row ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)).

That 79.4% overstates the real gap. Most of it comes from one counting choice: a proposal the developer rejected counts against accuracy, even though nobody adopted it. "The Not-Adopted cases are therefore not really response errors, yet the table's Accurate column counts them against accuracy since they are neither confirmed working nor Unreproducible. Excluding the 107 Not-Adopted cases (95 for Codex) from the denominator, and counting only Adopted-Revised, Mixed and Failed as errors [...] gives an accuracy of 565/605 (93.4%) for Claude and 566/614 (92.2%) for Codex" ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)). Report both numbers: 79.4% as the paper's raw table entry, 93.4% as what remains once you count only proposals someone actually tried and found wrong.

## Why it works

The paper gives a verification-method reason the categories separate this way: "Checkable-fact and mechanism-explanation are settled using the commit the response was made against: by executing, searching, or reading code at that one point in time. Root-cause-diagnosis and design-fix-proposal instead require looking forward past that commit" ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)). A fact has a check available the moment it is stated. A diagnosis or proposal only gets checked once someone runs it forward, and that is the step a rushed reviewer skips. The paper stops short of claiming this fully explains the gap's size, calling design-fix-proposal "an inherently harder category to get right" in its own right ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)) — and most of the raw gap turned out to be the rejected-proposal counting choice above.

A second finding explains why review alone will not catch these errors before a commit. Mining 105 pytest runs from session transcripts found 15 (14.3%) that introduced a genuine coding error corrected before any commit: 8 were errors in the tests themselves, 4 in the production code, and 3 were failures to update a test after a correct change ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)). None of that shows up later: "Git history only records what was eventually committed; a bug Claude introduced, caught by a failing test, and fixed before ever committing leaves no trace there" ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)). A reviewer working from the commit log cannot see how many mistakes the test suite already absorbed.

## Example

The appendix gives a worked case of the technique. The agent proposed raising the constant `_SPARSE_MAX_INSNS` as a fix. Instead of adopting the proposal, "the user asks for this to be tested before deciding, and the AI runs the constant at 1000, 4000 and 30,000 instructions against the full test corpus (752 enums, 14,900 values): every enum gains zero additional values at any of the three settings. The constant was not the cause" ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)). The proposal read as plausible, and the agent stated it with no hedge. The check, not the confidence of the statement, is what showed it was wrong.

## When this backfires

- Without a test suite, the check has nothing to run against. The 14.3% pre-commit error rate surfaced only because the agent ran pytest on every change. Skip the suite and those same errors ship, and the reassuring half of this finding, that the same process which made a mistake also built the check that caught it, no longer holds.
- Do not trust the 94.3% figure at face value. A checkable fact is still wrong about 1 time in 18. The appendix example above works because the developer distrusted a plausible-sounding proposal; the same discipline still has to apply to facts, or the 21.6% to 23.0% of responses that hold at least one inaccurate component (rising to 29.5% once design-fix components are counted back in) will pass unchecked ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)).
- A passing test does not prove the code. Over half the caught pre-commit errors, 8 of 15, were bugs in the AI-written test itself, not the production code it tested. A green run can mean the test agrees with a wrong implementation.
- The finding does not generalize past this project on its own. The paper's own limitations section calls this "the main limitation of the work [...] confined to a single dataset" ([Leith, arXiv:2609.29744v1](https://arxiv.org/abs/2609.29744v1)), and an independent tracker weighing it against other evidence on AI coding reliability rates it as "corroborating color" rather than a strong result on its own ([jazzli/ai-native-sdlc issue #93](https://github.com/jazzli/ai-native-sdlc/issues/93)). A team with a thinner validation habit than this project's should expect the untiered error rate, not this one.
- The rates come from long, multi-session command-line work, not a short IDE-chat exchange.

## Key Takeaways

- Report the raw and adjusted design-fix numbers together: 79.4% counts proposals the developer already rejected as errors, and 93.4% counts only proposals someone tried and found wrong. Neither number alone tells the whole story.
- Keep a test suite wired into the same session as the agent, and keep the session transcript past the default 30-day deletion window if you want to audit pre-commit errors later. 15 of 105 pytest runs caught one that git history would never show.
- Read what a passing AI-written test actually asserts. In this dataset, more caught pre-commit errors lived in the test than in the code it was testing.
- Before you adopt a diagnosis or a design-fix proposal, ask for the check that would confirm it, the way the developer asked for `_SPARSE_MAX_INSNS` to be tested before deciding.
- Do not extend a lighter review to checkable facts because they scored higher. About 1 in 18 was still wrong.

## Related

- [Overtrusting Human Sign-Off on Generated Assertions](../patterns/anti-patterns/generated-assertion-signoff.md)
- [Completion Summary as the Oversight Surface](../patterns/anti-patterns/completion-summary-as-oversight-surface.md)
- [Transcript-Measured Review Coverage](transcript-measured-review-coverage.md)
- [Claim-to-Evidence Trace Graphs for Auditing Agent Runs](claim-to-evidence-trace-graphs.md)
- [Name the Check That Passed Before Accepting AI Code](named-check-over-evaluation-confidence.md)
