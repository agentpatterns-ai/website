---
title: "Eval Difficulty as a Product Smell"
term: "Eval Smell"
description: "Hard-to-write evals usually signal a product that was not designed for users to verify — redesign the artifact for checkability before scaling the scorer."
tags:
  - testing-verification
  - tool-agnostic
  - evals
aliases:
  - hard-to-eval product smell
  - verifiability-first product design
last_reviewed: 2026-07-23
maturity: emerging
---

# Eval Difficulty as a Product Smell

> Trouble writing an eval signals the product was not designed for users to verify — redesign the artifact for checkability before scaling the scorer.

When an AI feature resists evaluation, the first move is to redesign the artifact so users can verify outputs the way a domain expert would. Hamel Husain frames the difficulty itself as a diagnostic: "Artifacts that are hard for you to verify are often hard for users too. In the worst case, users have to redo the work from scratch to verify the output" ([Hamel Husain — "It's Hard to Eval" Is a Product Smell](https://hamel.dev/blog/posts/eval-smell/), 2026-06-29). The eval gap is downstream of a verifiability gap in the product.

## How to read the smell

Three product moves recur across Hamel's worked examples (an AI data agent, a K-12 PE lesson planner, and a workers-comp medical-report generator):

- Surface provenance. Show where each part of the answer came from with a link the user can open. A number that ships without its query is unverifiable; the same number paired with the SQL and the metric definition can be cross-checked in seconds ([Hamel Husain — eval-smell](https://hamel.dev/blog/posts/eval-smell/)).
- Break the artifact into smaller acceptable units. The lesson-planner sketch goes from "generated plan, accept or reject" to "vetted plan plus two diffed edits, accept or reject each." Reviewers judge a few diffs against a trusted anchor, not a whole document from scratch.
- Use progressive disclosure for verification context. Chat-level answer up front, full notebook or trace behind a tab. Verification surface grows with the user's doubt, not with the artifact's size.

The four-question diagnostic Hamel proposes turns the smell into a design checklist:

1. What does the user actually need to check?
2. What trusted thing can they compare it against?
3. What signals or heuristics do experts use to aid verification?
4. What smaller units can the user accept, edit, or reject?

If the answers are thin, the product surface is the gap, not the rubric.

## How it connects to evals

A verifiable product gives evals tractable units to score. Once a lesson plan is reduced to a vetted anchor plus two labelled edits, the eval can grade retrieval-anchor sensibility and per-edit constraint compliance — concrete units against concrete inputs. Whether an automated or LLM-judge scorer then grades those units reliably is a separate downstream question — Hamel Husain's companion piece takes up whether automated evals actually hold up in practice ([Hamel Husain — "Do Automated Evals Work?"](https://parlance-labs.com/blog/posts/auto-evals.html)). The same applies to [grade agent outcomes, not execution paths](grade-agent-outcomes.md): outcome graders work because the product exposes a checkable final state. Designing for verification is the upstream version of writing evals first; the [eval-driven development workflow](../workflows/eval-driven-development.md) only pays off once the artifact has units to evaluate.

Coding agents already use the pattern. Cursor records a short video of UI changes and [Devin's testing-and-recordings docs](https://docs.devin.ai/work-with-devin/testing-and-recordings) walk through how the agent produces video proof so reviewers can verify without reproducing the change. The diff plus the recording is the checkable artifact; the eval grades the diff, not the agent's reasoning.

## Why it works

Verification used to happen incidentally during creation — a colleague wrote a query and checked their own numbers as they went. With AI in the loop, the artifact arrives finished and verification becomes the rate-limiting step ([Hamel Husain — eval-smell](https://hamel.dev/blog/posts/eval-smell/)). A product that ships an opaque artifact forces the user to redo the work to trust it and forces the eval engineer to score something the product was never designed to make scorable. Exposing provenance, decomposing the artifact, and progressively disclosing context drops verification cost for both audiences at once. The design heritage predates AI — needfinding ([Patnaik & Becker, 1999](https://onlinelibrary.wiley.com/doi/10.1111/j.1948-7169.1999.tb00250.x)) and sensemaking ([Russell, Stefik, Pirolli, Card, 1993](https://www.markstefik.com/wp-content/uploads/2014/04/1993-Cost-Structure-of-Sensemaking1.pdf)) — but the AI shift is that verification is no longer incidental, it is the reviewer's main job.

## When this backfires

The smell is a heuristic, not a theorem. Four conditions where pushing for verifiability adds cost without value:

- The artifact's value is inseparable from its holistic form. A legal opinion, a creative narrative, or a research synthesis loses what makes it useful when broken into accept/reject diffs. Hamel acknowledges this on the workers-comp report: "You might object that a fifty-page opinion is hard to verify. That is true, and the product should not pretend otherwise" ([Hamel Husain — eval-smell](https://hamel.dev/blog/posts/eval-smell/)). The fix there was a workflow refactor (research-assistant pattern) rather than slicing the report.
- The product is mid-life and users trust the existing surface. Adding provenance everywhere can read as "the system is suddenly unsure of itself" and erode trust. Stage the rollout against a clear failure-mode story.
- Verification labour is asymmetric. When verification itself is expert-bound (medical, legal, regulated finance), exposing every claim with provenance can make review more expensive — the reviewer must now check every cited source. Expose only a small, high-leverage subset of `accept/reject diff` checks.
- The domain has no trusted reference points. Hamel's pattern leans on "compare against a vetted source." Greenfield domains, novel research, or first-of-kind synthesis have nothing to anchor against; invest in scoring expertise instead, accepting that some artifacts are intrinsically hard to verify.

## Example

A data agent ships in two iterations. The first iteration is the smell ([Hamel Husain — eval-smell](https://hamel.dev/blog/posts/eval-smell/)):

Before — only the answer:

```
> What was net revenue for Product A last quarter?
> Net revenue for Product A last quarter was $4.21M.
```

There is nothing on the surface to check. To verify, the user has to redo the analysis from raw tables. The eval team is asked to score "is $4.21M correct?" against a moving warehouse — no tractable unit, no anchor.

After — verifiable artifact:

```
> What was net revenue for Product A last quarter?
> Net revenue for Product A last quarter was $4.21M.
> Adapted from "Quarterly revenue review" by Priya Nair, Jun 28, 2026 [Open]
>
> Assumptions
> - Metric definition: gross - returns - discounts (governed definition)
>
> Intermediate calculations
> - Returns netted out: -$0.7M (no trusted source)
> - Unique customers: 12,480 (183 unmatched between CRM and Billing)
>
> [Open as notebook] for the full SQL, the region breakdown, and the two
> cells the agent could not verify.
```

Now the user has a fast check (does the metric definition match what finance uses?), a known-good anchor (Priya's vetted analysis), an itemised "what I could not verify" list, and an escape hatch into the full notebook for deeper review. The eval team has tractable units: anchor-retrieval sensibility, metric-definition match against the governed source, and per-claim provenance presence ([Hamel Husain — eval-smell](https://hamel.dev/blog/posts/eval-smell/)).

## Key takeaways

- "Hard to eval" usually points at the product surface, not the scoring rubric. Redesign for verification before scaling the scorer.
- The three reusable moves are exposing provenance, breaking the artifact into smaller acceptable units, and using progressive disclosure for verification context.
- The four-question diagnostic — what to check, what to compare against, what experts use, what smaller units are reviewable — turns the smell into a design checklist.
- Verifiability-first design feeds [eval-driven development](../workflows/eval-driven-development.md) downstream by giving evals concrete units to grade.
- The pattern is a heuristic, not a theorem: holistic artifacts, mid-life products with established trust, asymmetric verification labour, and greenfield domains can all break the move.

## Related

- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md) — the upstream version: define evaluable success criteria before code, so the artifact ships with verification surface.
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — outcome grading works because the product exposes a checkable final state; the same design move at the eval layer.
- [Generative Provenance Records for Tool-Using Agents](generative-provenance-records.md) — the deterministic version of "show where each part came from," structured for machine verification.
- [The Prompt Tinkerer Anti-Pattern in Agent Workflows](../patterns/anti-patterns/prompt-tinkerer.md) — the related anti-pattern of fixing scoring or instruction debt instead of the underlying product or structural gap.
- [Evaluator Templates: Portable Primitives for Agent Eval Suites](evaluator-templates.md) — generic scoring templates only carry so far; domain quality still needs the verifiable units this page argues for.
