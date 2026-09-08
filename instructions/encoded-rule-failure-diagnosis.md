---
title: "Why an Encoded Rule Still Fails After a Passing Eval"
term: "Encoded-Rule Failure Diagnosis"
description: "A rule that passes your eval and still fails in production has one of four defects, and only one of them is the wording most teams rewrite first."
tags:
  - instructions
  - context-engineering
  - tool-agnostic
aliases:
  - encoded rule failure diagnosis
  - rule not reducing recurrence
  - diagnosing a rule that does not stick
last_reviewed: 2026-09-07
maturity: emerging
---

# Why an Encoded Rule Still Fails After a Passing Eval

> A rule that passes your eval and keeps failing in production has four candidate defects, and wording is only one of them.

Encoded-rule failure diagnosis is what you run when the correction is already in the instruction file, the eval suite is green, and people keep making the same correction by hand. Vercel treat the production count as the verdict: "Once we encode a fix, that count should start falling. When it does not, something about the fix is wrong" ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)). Running that count as a rate and retiring rules on it belong to the [error-class governance loop](../workflows/instruction-library-governance-loop.md). This page answers the question that loop leaves open: which of four things is wrong.

## When to trust the production signal over the eval

Two conditions decide whether the disagreement is informative at all.

The complaint stream has to come from people obliged to the output. Vercel gather theirs from Slack threads, GitHub review comments, and Figma, from colleagues who have to ship the artifact ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)). Anonymous end-user feedback is a different instrument. Across two deployed research tools carrying over 200,000 queries, "Explicit thumbs feedback is too sparse (fewer than 2% of reports) and less predictive of return than link clicks" ([Haddad et al., 2026](https://arxiv.org/abs/2602.23335v1)).

The failure also has to repeat across models. Vercel keep one out of the rules "when a single model fails in a way the others don't" ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)). One model diverging is a harness question first.

## The four defects

Vercel name four candidates. The rule "might be unclear, it might not be loading when it is needed, the stylesheet might not have a primitive that can express it, or it might need a deterministic check instead of prose" ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)). Their stylesheet is the vocabulary their rules name; substitute whatever yours do.

| Defect | What to check | What fixes it |
|---|---|---|
| Unclear | Can two readers disagree about whether an output satisfies it? | Rewrite as an observable decision |
| Not loading | Was the file in context on the runs that failed? | Fix the trigger, scope, or file layer |
| Inexpressible | Does the model have a named class, token, or API to obey the rule with? | Publish the primitive first |
| Wrong medium | Can a check detect the failure over rendered output? | Move it out of prose |

Rewriting the wording is what most teams reach for and only the first of the four. The other three fail identically: the eval passes, the rule reads well, the output does not change. Check loading first; it is the cheapest to confirm.

Take the inexpressible case. Vercel published a stylesheet of documented classes and tokens because agents "kept inventing their own typography, spacing, and layout", and `design.md` names those classes ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)). A rule asking for something the model has no vocabulary to produce is not a wording problem.

## Why it works

Eval and production disagree because they measure different things. Fu and colleagues call the failure mode prompt distributional overfitting: rewriting a prompt against generated feedback accumulates "narrow sample-specific rules" that generalize poorly. A holdout drawn from the same set does not expose it, because "the optimized prompt may still perform well on held-out samples from the training distribution, but degrades on OOD inputs such as harder task variants or related-but-shifted tasks" ([Fu et al., 2026](https://arxiv.org/abs/2605.21318v1)). So a green eval is evidence of fit, not of scope. Their method treats scope as unobservable on any fixed sample and uses "recurrence frequency as a monotone empirical proxy" for it ([Fu et al., 2026](https://arxiv.org/abs/2605.21318v1)), which is the same estimator pointed at real requests.

## When this backfires

- The complaint count is the only evidence you have. Thumbs "sit mostly in the tails of the satisfaction distribution", and a naive average over them "can land 40-50 percentage points away from true system quality" ([Morandi and Viswanathan, 2026](https://arxiv.org/abs/2605.12177v1)). A flat count can mean the rule failed or that people stopped bothering.
- The failure is mechanically checkable. Run the check over production output instead; it cannot decline to report.
- Each round appends a rule. Adherence falls with density, to 68% accuracy at 500 instructions on the best of 20 models across seven providers ([IFScale, 2025](https://arxiv.org/abs/2507.11538v1)). Pair the loop with [rule lifecycle metadata](rule-lifecycle-metadata.md) so rewrites replace rather than accumulate.
- Volume is too low to read a trend. Vercel's file took "well over 200 runs" to author ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)); a few artifacts a month is noise.

## Key Takeaways

- Do not close out a correction on a green eval. The signal that it worked is the failure not coming back in real requests.
- Confirm the file was loaded on the failing runs before you touch the wording. Three of the four defects are not wording.
- A rule the model has no named primitive to obey cannot be fixed by rephrasing. Publish the vocabulary first.
- Hold a single-model failure out of the rules until it repeats on another model.
- Where a deterministic check can catch the failure, the check replaces the diagnosis rather than informing it.

## Related

- [The Error-Class Governance Loop for Instruction Libraries](../workflows/instruction-library-governance-loop.md) — the loop this diagnosis sits inside: recurrence as a rate over attempts, the retirement pathway, and who owns the cut list.
- [Rule Lifecycle Metadata for Prunable Instruction Surfaces](rule-lifecycle-metadata.md) — what to record at write time so a rule that fails diagnosis has a defensible deletion path.
- [Agent Context File Evolution: Treating ACFs as Configuration Code](agent-context-file-evolution.md) — the file-level maintenance discipline, including the compact pass that keeps repeated rewrites from growing the surface.
- [Encoding Product-Design Taste into Agent Context](encoding-product-design-taste.md) — the in-repo instruction file these corrections land in, and why design rules need observable forms.
- [Probe-and-Refine Tuning of Repository Guidance for Coding Agents](probe-and-refine-guidance-tuning.md) — the offline counterpart, refining guidance against synthetic probes rather than production complaints.
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — the density limit that bounds how many diagnosis rounds you can answer with more prose.
