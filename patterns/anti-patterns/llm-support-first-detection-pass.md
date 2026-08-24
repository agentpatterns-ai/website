---
title: "LLM Support During the First Detection Pass"
term: "First-Pass LLM Support"
description: "Novice inspectors who consulted ChatGPT while making their first pass over a requirements document scored about 8% lower on defect detection and improved less between sessions."
tags:
  - anti-pattern
  - human-factors
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - assisted first-pass review
  - concurrent LLM inspection support
  - LLM-assisted defect detection pass
last_reviewed: 2026-08-24
maturity: emerging
status: current
---

# LLM Support During the First Detection Pass

> Novice inspectors who used an LLM during their first inspection pass scored about 8% lower on defect detection, and improved less between sessions.

Give a novice reviewer an assistant to consult while they work through a document for the first time and their defect detection gets worse. In a crossover experiment with 34 students, the group working without ChatGPT scored about 8% higher on macro-averaged F1 for requirements-smell detection ([Broccia et al., 2026](https://arxiv.org/abs/2608.21298v1)). The credibility intervals around the two group averages still overlap, so this is a measured direction, not a settled effect size.

## What was measured, and under what conditions

Every figure below is from that experiment ([Broccia et al., 2026](https://arxiv.org/abs/2608.21298v1)).

- Novice inspectors. 34 Computer Engineering bachelor students, grouped by self-reported proficiency in requirements inspection and in using LLMs.
- Detection, not triage. Classifying an already-detected smell as harmful or harmless showed virtually no effect, and neither did task duration.
- Unstructured, concurrent use. Participants had ChatGPT available during the inspection itself, on GPT-4o and GPT-4.1 family models, in May 2025.
- Simplified artifacts. Two game requirements documents (Arkanoid, 40 requirements with 21 smells; Snake, 39 with 19), each requirement carrying at most one smell.

The authors bound their own claim: the simplifications "limit the external validity of the results beyond novice inspectors in controlled educational contexts" ([Broccia et al., 2026](https://arxiv.org/abs/2608.21298v1)).

The second result is about learning. Both groups got better between the two sessions, but the group that started without the assistant improved by about 12% and the group that started with it by about 7% ([Broccia et al., 2026](https://arxiv.org/abs/2608.21298v1)). The paper's summary box gives the pair as 6% against 12%, so read the gap as roughly halved.

## Why it works

A reviewer handed a list of candidate defects works the list instead of the document. Tufano et al. recorded over 50 hours of code review by 29 experts and found that reviewers given an automatically generated review "tend to focus on the code locations indicated by the LLM rather than searching for additional issues in other parts of the code" ([Tufano et al., 2024](https://arxiv.org/abs/2411.11401v3)). That anchoring fits the shape of the requirements result. Detection falls because coverage of the unflagged material falls; classification is untouched because it only ever runs on defects already found.

The Broccia authors reach for a related explanation, delegation rather than anchoring. Participants "may have delegated part of the inspection effort to the LLM", which they ground in the automation-bias literature ([Passi and Vorvoreanu, 2022](https://www.microsoft.com/en-us/research/publication/overreliance-on-ai-literature-review/)). The learning result gets a thinner one: early assistance "short-circuiting the reflective processes through which novice inspectors internalize inspection strategies and quality heuristics". That is an interpretation of a sequence effect, not a measured mechanism.

## When this backfires

- Experienced inspectors. The study measured novices, and its authors call for replication "with professional inspectors and more complex industrial requirements".
- Triage and severity work. LLM support had virtually no measured effect on classifying detected smells, so extending the caution past detection extends it past the evidence.
- Assistance that shifts rather than subtracts. Tufano's experts starting from an automated review found more low-severity issues than a fully manual process, just not more high-severity ones ([Tufano et al., 2024](https://arxiv.org/abs/2411.11401v3)).
- Reviews that are not the last line of defense. The cost is the defects the human would otherwise have caught, and tests or a second reviewer downstream absorb most of it.

## Example

**Before — assistant consulted during the detection pass:**

```text
1. For each item, ask the assistant whether it contains a defect.
2. Record what the assistant names, and move on.
```

**After** — assistant as an independent second pass:

```text
1. Inspect the whole document by hand. Record findings.
2. Run the assistant over the same document, without showing it your findings.
3. Diff the two lists and investigate the disagreements.
```

Step 2 keeps coverage: the human pass finishes before any model output is visible, so there is no list to anchor on. That is the direction the paper's practice implications point at, restricting LLM use to "post-inspection review or justification refinement" rather than "as a primary aid during initial defect detection" ([Broccia et al., 2026](https://arxiv.org/abs/2608.21298v1)). The diff arrangement itself was not tested; the paper names staged use and leaves the design to future work.

## Key Takeaways

- Consulting an LLM during a first detection pass cost novice inspectors about 8% of macro-averaged F1, with the two groups' credibility intervals still overlapping ([Broccia et al., 2026](https://arxiv.org/abs/2608.21298v1)).
- The loss is confined to detection. Severity classification and task duration were unaffected, which is what the anchoring mechanism predicts.
- Starting with the assistant roughly halved the improvement between sessions.
- Run the assistant as a second pass and diff it against the human's findings, not alongside the human's first read.

## Related

- [Tab-Accept Rate as a Proxy for Critical Engagement](tab-accept-critical-engagement-gap.md) — the same novice-complacency family, measured on code completions instead of a review pass
- [Blind Tool Deference: Agents Parroting Callable Tools](blind-tool-deference.md) — the agent-side version, where the deferring party is the model rather than the person
- [Trust Without Verify: Skipping Agent Output Checks](trust-without-verify.md) — accepting output because it looks right, with no independent check
- [LLM Code Review Overcorrection for AI Agent Development](llm-review-overcorrection.md) — the opposite failure in the same review step, where the model flags correct work
- [LLM Static Verification Against Natural-Language Requirements](../../verification/llm-static-verification-natural-language-requirements.md) — the model checking requirements on its own, with no human pass to displace
