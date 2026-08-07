---
title: "Generated Questionnaires: Eliciting Someone Else's Context"
term: "Generated Questionnaire"
description: "When a decision is blocked on knowledge in another person's head, have the agent draft a questionnaire for them rather than guess at the gap itself."
tags:
  - context-engineering
  - claude
aliases:
  - to-questionnaire
  - discovery questionnaire
  - questionnaire generation
last_reviewed: 2026-08-06
maturity: emerging
---

# Generated Questionnaires: Eliciting Someone Else's Context

> Turn a blocked decision into a questionnaire aimed at the one person who holds the missing context, instead of letting the agent guess.

A generated questionnaire is a Markdown document the agent writes for one named human to fill in, covering the questions neither you nor the codebase can answer. Matt Pocock's `to-questionnaire` skill implements it: you supply the recipient and what you need back, and the skill drafts `to-questionnaire-<slug>.md` in the current directory for that person to answer async or to work through with you in a meeting ([AI Hero, The /to-questionnaire Skill](https://www.aihero.dev/skills-to-questionnaire)).

## Reach for it only when the answers live in another head

The technique earns its round trip under one condition: the knowledge blocking you sits with a specific person, such as a client, a domain expert, or a colleague on another team. AI Hero publishes the routing test ([AI Hero](https://www.aihero.dev/skills-to-questionnaire)):

| The answers are in… | Reach for |
|---|---|
| Your own head, unsharpened | [Grill Me](../patterns/agent-design/grill-me-technique.md) |
| The codebase | Codebase exploration |
| Someone else's head | A generated questionnaire |
| Nobody's head yet | A prototype to react to |

That test is the whole decision. A questionnaire and [Grill Me](../patterns/agent-design/grill-me-technique.md) do not differ on delivery format: grilling already asks in rounds, the whole frontier at once and recomputed from your answers. What separates them is whose head the answers are in ([AI Hero](https://www.aihero.dev/skills-to-questionnaire)).

## Interrogate the send, not the subject

The skill asks two things and then stops asking: who the document is going to, which fixes tone and how much orienting context it must carry, and what you need back, which becomes the checklist the finished document is measured against. Interviewing you about the topic would be pointless, because not knowing the topic is why you are writing to someone else. There is no ingest step either, so running the skill after a stalled grilling session works only because the transcript is already in the same conversation ([AI Hero](https://www.aihero.dev/skills-to-questionnaire)).

## What the document contains

The output is framed as a discovery questionnaire, on the premise that you lack the context and the recipient holds it ([AI Hero](https://www.aihero.dev/skills-to-questionnaire)):

- A purpose line naming the decision riding on the answers, plus context for a recipient who was never in your head.
- Questions ordered most-important-first under themed headings, because async delivery may buy you only one pass.
- One idea per question, never compound, each with an answer stub beneath it.
- Explicit permission to answer "I don't know", plus a closing catch-all asking what you failed to ask about.

Two omissions are deliberate. The questions form a flat grouped list rather than a tree that skips section D based on the answer to A, and one run produces one document for one person. Delivery stays manual ([AI Hero](https://www.aihero.dev/skills-to-questionnaire)).

## Why it works

Handing the drafting to the model costs nothing in question quality. Across two controlled experiments on requirements elicitation, GPT-4o-generated follow-up questions were rated "no worse than the human-authored questions with respect to clarity, relevancy, and informativeness", and they outperformed human-authored questions when the generator was guided by common interviewer mistake types ([Requirements Elicitation Follow-Up Question Generation, arXiv 2507.02858v1](https://arxiv.org/abs/2507.02858v1)).

The value comes instead from the send-not-subject constraint. The recipient and the return list are the two facts you can still supply while missing the topic, and that list gives every generated question a target to aim at. The flat output has its own stated reason, that a model planning more than two or three questions ahead of a real answer plans badly ([AI Hero](https://www.aihero.dev/skills-to-questionnaire)). One idea per question is ordinary survey practice, where compound questions "are difficult for respondents to answer and often lead to responses that are difficult to interpret" ([Pew Research Center, Writing Survey Questions](https://www.pewresearch.org/writing-survey-questions/)).

## When this backfires

The knowledge is tacit rather than statable. Across 34 customer–analyst interviews, ambiguity arising in the live exchange proved "often a resource for discovering tacit knowledge" rather than an obstacle to it ([Ferrari, Spoletini and Gnesi, Requirements Engineering 21:333–355](https://link.springer.com/article/10.1007/s00766-016-0249-3)). A one-pass document has no ambiguity-detection loop, so an expert who cannot articulate what they know returns confident, incomplete answers. Book the call instead.

The answers were never in someone else's head. Grill yourself when the gap is in your own thinking, and explore the codebase when it sits there; a questionnaire for either buys a round trip to close questions you could have closed in-session.

Several people hold different parts of the answer. The document is pitched at one recipient, so three holders means three runs and reconciling the partial answers yourself. The same applies to a decision due before an async round trip completes, and to a team that already has a house format — the author concedes that makes the skill unnecessary ([AI Hero](https://www.aihero.dev/skills-to-questionnaire)).

Automating elicitation also buys scale rather than accuracy. An LLM running elicitation interviews made "a similar number of errors compared to human interviewers" across 33 simulated stakeholder interviews ([LLMREI, arXiv 2507.02564v1](https://arxiv.org/abs/2507.02564v1)).

## Example

The skill is user-invoked, and the agent will not reach for it on its own ([AI Hero](https://www.aihero.dev/skills-to-questionnaire)):

```
/to-questionnaire
```

It asks the two send questions, then writes the file. The template it fills has a fixed skeleton: a title, a purpose statement, metadata naming who the document is from, who it is to, and how to use it, a context section, answering instructions, themed question sections, and the catch-all close ([mattpocock/skills, to-questionnaire SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/productivity/to-questionnaire/SKILL.md)).

AI Hero publishes acceptance checks for the result, and they are the useful part to run against a draft ([AI Hero](https://www.aihero.dev/skills-to-questionnaire)):

- The skill asks about the recipient and about what you need back, then stops asking. A question about the subject itself means it has gone off the rails.
- Every item you named as "what I need back" traces to a question in the file.
- The questions read as aimed at what the recipient knows, not as your own open questions copied down verbatim.
- Someone who was never in the conversation could read the file and know why they got it and by when to reply.
- The answers that come back are usable input for a new grilling round, rather than a fresh set of questions.

## Key Takeaways

- Route on where the answers live: your own head calls for [Grill Me](../patterns/agent-design/grill-me-technique.md), the codebase calls for exploration, another person's head calls for a questionnaire
- The skill interviews you about the recipient and what you need back, never about the topic you do not know
- The output is a flat, single-recipient Markdown file you deliver yourself; branching and multi-recipient routing were considered and left out
- Better questions are not the payoff, since LLM-generated elicitation questions rate no worse than human-authored ones and no better without mistake-type guidance
- Skip it when the missing knowledge is tacit, because the live ambiguity a questionnaire removes is what surfaces knowledge an expert cannot state

## Related

- [Grill Me: Developer-Initiated Plan Interrogation](../patterns/agent-design/grill-me-technique.md) — the same elicitation move aimed at your own head, delivered as a live session rather than a file
- [Daily-Use Skill Library: Encoding Your Process as Agent Skills](../workflows/daily-use-skill-library.md) — the skill pack this technique ships in
- [Interactive Clarification for Underspecified Tasks](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) — the agent-initiated version, which resolves the minimum gap needed to proceed
- [Discoverable vs Non-Discoverable Context for Agents](discoverable-vs-nondiscoverable-context.md) — why knowledge held only in a person's head never reaches the agent unprompted
- [Ubiquitous Language for AI Plans](../instructions/ubiquitous-language-for-ai-plans.md) — aligning the vocabulary the answers come back in with the codebase
