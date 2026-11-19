---
title: "Steering Agent Memory: Judge Salience, Then Correct with Dreaming"
term: "Salience-Steered Memory with Dreaming"
description: "Tell a frontier model what memory is for and let it choose what to save, then correct its notes offline against the transcripts. Older models need explicit read-and-test instructions."
tags:
  - agent-design
  - memory
  - context-engineering
  - claude
aliases:
  - dreaming memory correction
  - offline memory correction against transcripts
last_reviewed: 2026-11-09
maturity: emerging
---

# Steering Agent Memory: Judge Salience, Then Correct with Dreaming

> Let a strong model judge which memories to save, keep the transcripts, and correct its notes offline against them with dreaming.

This pattern holds under two conditions: the model is a recent frontier model, and the harness keeps raw session transcripts. Give the agent a memory store and say what memory is for, with no rule about what to write. Then run a background pass, called dreaming, that checks notes against the transcripts and rewrites the wrong ones. The same pass keeps the always-loaded layer small ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)).

## Match the steering to the model

On the CL-Bench database task, Anthropic told each model only that a memory folder was available. "That general guidance was enough for Opus 4.7 and Opus 5 to use memory effectively" ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)). A fixed rule to "record only failures" then cut the gain:

| Model | No memory | Memory folder | Change in memory gain under "record only failures" |
|---|---|---|---|
| Opus 5 | 0.564 | 0.828 | −0.234 |
| Opus 4.7 | 0.383 | 0.700 | −0.150 |
| Sonnet 4.6 | 0.330 | 0.364 | −0.020 |

Purpose-only guidance falls short on older models. Sonnet 4.6 often skipped its memory files and did not test its theories. Prompting it to read memory first and then test its theories raised its score from 0.364 to 0.641. Sonnet 5 read its memory before answering 9 out of 10 times with no prompt ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)). Tie the memory instruction to the model version, and re-test it at every model change.

Pokémon Red shows what good salience looks like. In one run each, at about 10,000 steps, Sonnet 3.7 had written 413 memory files across 225 folders and earned one badge. Fable 5 had written nine files in two folders plus `global.md`, and earned four badges. Fable 5 stored strategy, plans, and tested rules. Sonnet 3.7 also stored money and map position, which the screen shows every turn. At one point it spent 17 steps creating six files and deleting nine, with no game actions ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)).

## Correct notes against the transcript

An agent writes a note before it knows what the next session needs. Anthropic names the failure: "a note that's wrong from the start or that drifts as the environment changes can be read, and trusted, by Claude in a later session" ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)).

In one Pokémon run, Claude recorded the Mt. Moon PokéCenter on the wrong side of the mountain. With that note, it dropped off a one-way ledge back onto the route it came from three times, and never reached Cerulean City. A dreaming pass over the same memory folder checked the note against the session transcript and rewrote it. The corrected run reached Cerulean City at action 1,935 ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)).

## Promote little to the injected layer

Dreaming can also move a note into context the harness loads at every session start. Anthropic warns that "an incorrect note can be carried into every session", so the top layer must stay small, with detail moved down and links left behind ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)). Claude Code enforces a ceiling: it loads the first 200 lines or 25KB of `MEMORY.md`, whichever comes first, and nothing past that at session start ([Claude Code docs](https://code.claude.com/docs/en/memory)).

A dreaming-built wiki helped on merger questions that needed several documents, judgment, or math: 87% with the wiki against 73% with search alone. On a task where most criteria sat in one document it showed no clear gain, and on another it grew to 1.77 times the corpus ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)). [Wiki memory](wiki-memory-agent-maintained-knowledge-base.md) covers when to build one.

## Why it works

Writing down a rule predicts that its pattern "will be relevant again" ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)). A strong model predicts well enough that a fixed rule can discard notes its own judgment would keep. The prediction still sees only one session, so some notes are wrong. The writing session cannot check a note against what happened later. An offline pass can, because "The transcript gave Claude a ground truth to validate its memory against" ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)).

## When this backfires

- Older models with purpose-only guidance: Sonnet 4.6 gained 0.034 from memory until it got explicit read-first, test-theories instructions.
- Consolidation on every interaction: "memory utility first rises, then degrades, and can fall below the no-memory baseline" ([arXiv:2605.12978v2](https://arxiv.org/abs/2605.12978v2)). The authors advise keeping raw episodes and gating consolidation. A dreaming pass with no retained transcript has nothing to check against.
- Unpredictable workloads: sleep-time compute, which Anthropic names as the idea behind dreaming, "will be less effective" when queries are "challenging to predict or unrelated to the context" ([arXiv:2504.13171v1](https://arxiv.org/abs/2504.13171v1)).
- Unbounded dreaming: it costs compute, and checking every memory "might not be practical". Anthropic suggests targeting information likely to change, or tuning cadence to access frequency ([Anthropic, 2026](https://www.anthropic.com/research/components-of-agent-memory)).
- Thin evidence: the Pokémon comparisons are single runs from the model vendor.

## Key Takeaways

- For current frontier models, state what memory is for and leave the choice of what to write to the model. A "record only failures" rule cost Opus 5 0.234 of its memory gain.
- For older models, write the procedure: read memory before answering, then test each theory.
- Keep transcripts. They are the ground truth a dreaming pass corrects notes against.
- Gate dreaming and keep the injected layer to an index, because a wrong promoted note reaches every session.

## Related

- [Self-Correcting Memory: Evidence-Backed Claim Repair](self-correcting-memory-evidence-backed-claims.md) — deterministic staleness detection before a model rewrites a note
- [Wiki Memory: Agent-Maintained Compressed Knowledge Base](wiki-memory-agent-maintained-knowledge-base.md) — the representation layer dreaming can build
- [Tiered Memory Architecture](tiered-memory-architecture.md) — promoting facts from raw episodes to a curated tier on observed re-use
- [Memory Synthesis: Extracting Lessons from Execution Logs](memory-synthesis-execution-logs.md) — mining traces for lessons
- [Continual Learning for AI Agents](continual-learning-layers.md) — where memory sits among model, harness, and context updates
