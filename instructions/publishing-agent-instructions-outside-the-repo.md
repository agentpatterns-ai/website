---
title: "Publishing Agent Instructions Outside the Repo (design.md)"
term: "Portable Instruction File"
description: "An instruction file read beside the code it governs leans on that code for meaning; published at a URL its subjective rules land differently in each model, so name primitives and write decisions in checkable form."
aliases:
  - public agent instruction file
  - portable instruction file for agents
tags:
  - instructions
  - context-engineering
  - tool-agnostic
last_reviewed: 2026-09-05
maturity: emerging
---

# Publishing Agent Instructions Outside the Repo (design.md)

> An agent instruction file published outside the repo loses the examples its words pointed at, so its subjective rules land differently in each model.

Vercel keeps a `product-design` skill in each repository so agents in that codebase match the house design. Reports and proposals get built in tools that cannot read those files, so they published `design.md`, one file at a public URL any agent can load. The first attempt was a straight port of the skill, and it did not survive the move ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)).

## When the rewrite is worth it

Porting is cheap and sometimes sufficient. Three conditions decide whether your file needs the harder treatment.

1. The guidance is subjective. Vercel's diagnosis lands on the vocabulary first: "Phrases like 'keep the layout clean' can really mean anything. What is 'clean'?" ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)). Procedural policy travels better; Vercel's own academy claims a sectioned operating-policy prompt copies "to a different agent, with different tools, and the policy still applies" ([Vercel Academy](https://vercel.com/academy/build-ai-agent-harness/structuring-agent-instructions)).
2. You have primitives to name. The rewrite works because the file can point at a published vocabulary of class names and tokens instead of describing an appearance. Without that layer there is nothing to name, and the rewrite decays back into adjectives.
3. The output is mechanically checkable. Deterministic checks over rendered pages are the measured half of the loop below. Where nothing can be checked in code, every iteration costs human review time.

## What replaces the missing examples

Vercel report the failure in first person: "while the prompt described our visual language just fine, every model reading it interpreted that description differently, generating vastly different pages from the same guidance." Their explanation is about the surroundings, not the wording. "Inside our codebases, an agent reads `product-design` surrounded by real components and shipped examples of the things it describes. But a public prompt includes none of that, leaving every model to rebuild our style from just words alone" ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)).

Two substitutions restore what publication stripped out.

A public stylesheet supplies a bounded vocabulary. It packages design-system primitives such as headers, tables, and stat strips as CSS at a public URL, and `design.md` documents the class names and tokens it provides. The agent never reads the stylesheet; it loads client-side when the page renders, so none of the CSS enters the model's context ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)).

Every decision is then written in a form something can check. Vercel's worked contrast is "Let evidence tables use the full available width" against "Make the table feel less cramped", since only one of those can be verified. Each correction lands in the narrowest place that enforces it. Judgment goes into the file as prose, reusable mechanics into the stylesheet, and a mechanically detectable failure into a deterministic check in code ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)).

## The loop that authored the file

Seven eval prompts from real use cases were frozen with their mock inputs and render settings. They include a renewal proposal, a benchmark report, and an interactive planning page. A round regenerates every scenario against the current file, and full rounds run all seven on Claude Opus 4.8 and on Codex with GPT-5.5. A failure that shows up in one model and not the others is kept out of the rules until it repeats. Building the file took "well over 200 runs", with blind A/B rounds at milestones deciding whether to keep, revise, or revert each change ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)).

The one number they publish is narrow. Three desktop scenarios were generated twice by Codex with GPT-5.5, first attempt kept. The pages built with `design.md` tripped 39 known failures against 91 without it, "which works out to 57% fewer in this test" ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)). Read what it compares: the file against no file, never the rewrite against the discarded port. Vercel add the caveats, that six pages is "far too small a sample to make claims about quality or reliability" and that every page in both sets still carried at least one failure serious enough to block shipping.

## Why it works

In the repo, the words in an instruction file point at retrievable artifacts. The agent resolves "clean" by opening the component the team shipped, so the file only has to name where to look. Publication deletes the referent and leaves the description, and each model then fills the gap from its own priors. Identical prompt text is not identical input: across six model families on a 37,346-example extraction benchmark, the same prompt spread results by 0.4 to 0.6 F1 ([Kotte, 2026](https://arxiv.org/abs/2601.06151v1)). Both substitutions restore reference instead of improving description. A documented class name denotes one thing in every model's reading of it, and an observable decision can be tested against the output ([Vercel, 2026-08-31](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)).

## When this backfires

- The file encodes procedure, not taste. An operating policy about scope and restraint copies across agents and keeps applying ([Vercel Academy](https://vercel.com/academy/build-ai-agent-harness/structuring-agent-instructions)). Rewriting one from scratch spends the eval budget on a file that was already portable.
- No primitives exist to point at. Without a published token or component vocabulary the rewrite has only adjectives available, and reproduces the port under a new name.
- The scenario set is fixed and has no holdout. A rule that helps one artifact can hurt another: appending generic rules to the user prompt dropped one model's RAG compliance from 26 of 30 cases to 9 of 30 ([Commey, 2026](https://arxiv.org/abs/2601.22025v2)). Seven frozen scenarios reward rules fitted to those seven.
- The volume is too low. Over 200 runs went into one file, which a one-off artifact never repays.
- The port was never measured. Vercel's account of its failure is first-person and carries no comparison, so treat "rewrite, do not port" as reported experience rather than a demonstrated result.

## Key Takeaways

- Sort your rules by whether they name a checkable thing before deciding to publish; the adjective-only ones are the ones that will not survive the move.
- Publish a vocabulary alongside the file so rules can name a primitive instead of describing an appearance.
- Keep the vocabulary out of context by loading the stylesheet at render time, not into the prompt.
- Freeze the scenarios and change one rule at a time, or you cannot attribute an output difference to the guidance.
- Hold back a scenario the file was never tuned on, since a fixed set rewards rules fitted to it.
- Run your rounds on more than one model family; a single-model failure is a harness question until it repeats.

## Related

- [Encoding Product-Design Taste into Agent Context](encoding-product-design-taste.md) — the in-repo half of the same system: what Vercel's `product-design` skill encodes and how it routes by mode.
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md) — why anchoring examples change what a rule means; publication is the case where the anchors are removed.
- [Hints Over Code Samples in Agent Prompts](hints-over-code-samples.md) — pointing at repo paths beats embedding samples, and that option disappears once the file leaves the repo.
- [Specification Portability Across Coding Agents](specification-portability-across-agents.md) — handing one agent's specification to another moves the output, so measure the swap against a baseline.
- [System Prompt Altitude: Specific Without Being Brittle](system-prompt-altitude.md) — the altitude that holds behavior steady across variation, which is the axis a public file has to get right.
