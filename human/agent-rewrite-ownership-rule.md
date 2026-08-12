---
title: "Agent Rewrites Lose Meaning: The Ownership Rule for AI-Assisted Writing"
term: "No Lossless Transformation"
description: "Agent rewrites broaden claims and drop qualifiers in a measurable direction; the ownership rule that follows, and the conditions where a blanket rule costs more than it saves."
aliases:
  - no lossless transformations of natural-language text
  - AI writing ownership rule
  - stand behind every sentence
tags:
  - human-factors
  - tool-agnostic
last_reviewed: 2026-08-12
maturity: emerging
---

# Agent Rewrites Lose Meaning: The Ownership Rule for AI-Assisted Writing

> Agent rewrites can broaden the claims you made, so the ownership rule holds: you answer for every sentence you ship.

Ask an agent to polish a design doc and it hands back claims slightly broader than the ones you made. Sophie Alpert's internal engineering policy at Clay names the reason: "There are no lossless transformations of natural-language text — every rewrite and rephrase changes the meaning of your writing, and if this is done by an entity that doesn't have the most detailed mental representation of what you personally were trying to communicate, information will be lost" ([Alpert, 2026](https://sophiebits.com/2026/06/25/there-are-no-lossless-transformations-of-natural-language-text)). The policy that follows still permits AI, and it makes the author answerable for the result.

## Where the loss is large enough to matter

The loss is not uniform. Apply the rule where the cost is real:

- High-intent prose, where a hedge, a tense, or the order of two clauses carries the meaning. Design docs, RFCs, and incident retrospectives sit here.
- Documents one person writes and many people read. Alpert's arithmetic: "More time should be spent authoring a document than consuming it" ([Alpert, 2026](https://sophiebits.com/2026/06/25/there-are-no-lossless-transformations-of-natural-language-text)).
- Expand-from-a-prompt work. If a long document came from a short prompt, share the prompt ([Alpert, 2026](https://sophiebits.com/2026/06/25/there-are-no-lossless-transformations-of-natural-language-text)).

An edit pass that does not lengthen carries less risk, though Alpert notes meaning can still get obscured.

## The ownership rule

You answer for every line, including the ones a model wrote. Simon Willison singles this rule out as crucial, quoting Alpert: "It is your responsibility to make sure that the entire document is representative of your own thoughts before you share it. If a reviewer asks, 'What did you mean by this line?', it's not acceptable to reply with 'Oh sorry, AI wrote that, just ignore it.'" ([Willison, 2026](https://simonwillison.net/2026/Aug/11/there-are-no-lossless-transformations-of-natural-language-text/)).

That gives a workable split. Critique, questions, proofreading, and clarity checks return signal you act on yourself. Rephrase, massage, and expand return text you must now defend line by line. Verbatim model output stays allowed when you label it, which is how you float an idea without adopting it ([Alpert, 2026](https://sophiebits.com/2026/06/25/there-are-no-lossless-transformations-of-natural-language-text)).

## Why it works

A rewrite regenerates the choices your text under-determines: which qualifier survives, whether a finding stays past tense about a sample or becomes present tense about the world. Peters and Chin-Yee measured which way those choices go. Across 4,900 summaries of scientific texts, the worst performers overgeneralized in 26% to 73% of cases. LLM summaries also ran nearly five times likelier than human ones to carry broad generalizations (odds ratio 4.85, 95% CI [3.06, 7.70], p < 0.001) ([Peters and Chin-Yee, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12042776/)). Prompting explicitly for accuracy did not remove the effect. Scope restrictors go first, and only the author knows why one was there.

A second mechanism sits on the author's side. In a four-month EEG study of 54 participants, LLM-assisted essay writers showed the weakest brain connectivity of the three conditions, reported the lowest ownership of their own essays, and struggled to quote their own work accurately ([Kosmyna et al., 2025](https://arxiv.org/abs/2506.08872v2)). Someone who cannot quote their document cannot notice what the rewrite changed, which is why the rule has to be a stated duty. The same reasoning drives [delegating change descriptions to the agent](../patterns/anti-patterns/delegating-change-descriptions.md) and [the meat proxy](../patterns/anti-patterns/meat-proxy.md).

## When this backfires

- The author writes in a second language. One qualitative study reports that for second-language writers, model suggestions augmented their voice because AI "helped overcome their language barriers and better express ideas true to themselves" ([Technology, Knowledge and Learning, 2024](https://link.springer.com/article/10.1007/s10758-024-09744-3)). The sample is six students, so read it as a caution against a blanket rule.
- The draft is worse than the rewrite. In a preregistered experiment with 453 professionals on incentivized writing tasks, ChatGPT cut time by 40% and raised graded output quality by 18% ([Noy and Zhang, 2023](https://pubmed.ncbi.nlm.nih.gov/37440646/)). Fidelity is worth protecting only once the draft encodes intent.
- The artifact has no authorial intent to lose. Dependency-bump changelogs and docs for a feature an agent just wrote carry no privileged human mental model.
- The volume exceeds what a human can read. A per-sentence rule over an autonomous pipeline reinstates the bottleneck the pipeline removed. Attach ownership at the issue or the prompt instead.
- The model and settings are ones where drift is not measurable. GPT-3.5 Turbo and all three Claude models tested showed no significant generalization drift, and temperature 0 cut generalized conclusions by 76% against temperature 0.7 ([Peters and Chin-Yee, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12042776/)).

## Key Takeaways

- Name the direction of the loss in the policy. Rewrites broaden scope and drop hedges, so review qualifiers first rather than reading for tone.
- Write the rule as an answer a reviewer will accept. "AI wrote that" is not one.
- Put the split in the team's tooling, not just the policy. A critique prompt and a rephrase prompt should be separate saved commands so the choice is deliberate.
- Exempt low-intent and agent-authored artifacts explicitly, or the policy gets ignored wholesale at its first collision with a changelog.
- Lower the temperature before you lower the trust. Temperature 0 removed most of the measured drift, which is cheaper than a review mandate.

## Related

- [Delegating Change Descriptions to the Agent](../patterns/anti-patterns/delegating-change-descriptions.md) — the same loss applied to PR and commit descriptions, where the diff cannot carry intent
- [The Meat Proxy: Relaying Agent Output Without Reading It](../patterns/anti-patterns/meat-proxy.md) — forwarding unread model output pushes verification onto the receiver
- [Skill Atrophy: When AI Reliance Erodes Developer Capability](skill-atrophy.md) — the longer-run cost of routing thinking work through a model
- [Marking Which Artifacts Are for Humans or Agents (Landmarking)](landmarking-human-vs-agent-artifacts.md) — a readership contract that tells you which documents the ownership rule governs
- [Author-to-Reviewer Role Inversion in AI-Assisted Teams](author-to-reviewer-role-inversion.md) — why review capacity, not authoring speed, becomes the binding constraint
