---
title: "Seller-Written Tool Listings as a Capability Signal"
term: "Seller-Written Listings as a Capability Signal"
description: "In a constructed tool market, competing sellers inflated descriptions and one seller model caused severe selection failures. The authors propose execution records to check claims."
aliases:
  - tool description inflation
  - seller agent description inflation
  - tool listing capability claims
tags:
  - anti-pattern
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-26
maturity: emerging
---

# Seller-Written Tool Listings as a Capability Signal

> Competing seller agents accumulate claims their tools do not deliver, so a shelf ranked on their listings can stop predicting capability.

The measured risk concerns competing tools presented through seller-controlled descriptions. The study tests a constructed market, so its results do not describe live registry failure rates.

## What the study measured, and what it did not

Tang and colleagues built Amazon and Instagram shelves, each with ten real [Apify](https://apify.com/) tools. Pre-recorded executions defined capability. Seller agents saw competing descriptions and selection counts, with instructions to increase selections. Claude Code and Codex acted as buyers. Five seller models produced 20 markets and 166,320 buyer choices ([arXiv:2610.28454v1](https://arxiv.org/abs/2610.28454v1)).

Nothing was published to the store; no real buyer saw the descriptions. Prices were held equal. Buyers saw "no vendor name, no input schema, no usage count and no price" ([source](https://arxiv.org/abs/2610.28454v1)).

Sellers rewrote descriptions in 77–100% of turns. Every market claimed more fields than the original listings. Amazon listings began at 0.4 overclaimed fields per description. Final-five-round averages reached 0.9 to 1.6 for four seller models and 5.6 for Gemini 3.8 Flash. Overclaimed fields fail on most execution targets ([source](https://arxiv.org/abs/2610.28454v1)).

## Why it works

Seller incentives reward selection, while buyers cannot check descriptions. In four markets, all using the same seller model, descriptions converged and first-position selection rose to 61–79%. Elsewhere it was 8–25%. Amazon success fell from 88–89% to 29–31%; Instagram success fell from 74–80% to 40% ([source](https://arxiv.org/abs/2610.28454v1)).

## What to rank on instead

The authors propose showing execution-derived field records beside descriptions. This would let buyers check claims. They also measure unsupported claims, defined against vendor sample output. In each collapsed market, that count exceeded the mild-market maximum within three rewrites, at or before the first success decline ([source](https://arxiv.org/abs/2610.28454v1)). This is a warning signal in the experiment, not a tested detection threshold for other registries.

## When this backfires

- Rewrites also helped. Eleven of sixteen mild markets finished above initial success. Freezing descriptions would discard those improvements ([source](https://arxiv.org/abs/2610.28454v1)).
- Severe collapse occurred with one of five seller models. Preserve that scope when estimating risk.
- Other shelves can expose the non-text signals this experiment withheld.
- The capability matrix was fixed before trading. A deployment needs to check whether later tool changes invalidate its records.
- Capability varied widely on this Amazon shelf. Random choice reached 28% success, perfect routing 98%, and four tools answered no questions ([source](https://arxiv.org/abs/2610.28454v1)).

## Example

**Before — shelf ranked on vendor-written listing text**: one Amazon market ran Gemini 3.8 Flash sellers against Claude Code as the buyer. A seller-contact database there answers none of the 360 questions. Its listing opens by describing a seller database and gets no selections. From round four, the seller copies the product scrapers' opening sentence and field list. The tool then receives up to 53 selections per round. The seller twice reverts to describing a database. Each time, selections stop until it copies the product scrapers again. In four other markets with that buyer and product sheet, the tool finishes with a database description and no selections ([arXiv:2610.28454v1](https://arxiv.org/abs/2610.28454v1), Appendix H).

**After — seller objective requests honest claims**: the authors reran that market for ten rounds. An added sentence asks sellers to claim only fields their tool returns. With Gemini 3.8 Flash sellers, task success reached 94%, and weak tools lost 0.1% of questions. The neutral objective averaged 41% and 22.7% across three seeds, over rounds 5 to 9 ([source](https://arxiv.org/abs/2610.28454v1), Appendix F). Under GPT-5.6 Sol sellers all three objectives landed within a point of each other. The authors note their results "describe specific model versions and should not be read as a verdict on any provider" ([source](https://arxiv.org/abs/2610.28454v1), Ethics Statement).

## Key Takeaways

- Read a competitor-facing tool listing as advertising rather than documentation, once several tools chase the same request and text is the only discriminator.
- Monitor claims absent from vendor sample output. The count rose early in every collapsed market, but validate any intervention threshold on your own tools.
- Log which position the agent picked. The study shuffled tool order for every question, and shuffling did not prevent collapse ([§3.2](https://arxiv.org/abs/2610.28454v1)). These buyers took the first-listed tool 8–25% of the time while descriptions still discriminated, and 61–79% once they did not.
- For platform operators, the authors propose execution records ([Discussion](https://arxiv.org/abs/2610.28454v1)). Date any record used to assess a listing. The buyer cannot check a claim that costs nothing to make, and a record older than the vendor's last release cannot either.
- Size the response to one paper and one research group, with the severe case in one seller model of five.

## Related

- [Blind Tool Deference: Agents Parroting Callable Tools](blind-tool-deference.md) — the buyer-side half, where the agent accepts a tool's output instead of judging it
- [Multi-Tool Threshold Poisoning Against MCP (ShareLock)](multi-tool-threshold-poisoning-mcp.md) — description text as an attack surface, where the author is hostile rather than merely competing
- [Task Completion as Tool Certification (Silent Tool Rot)](task-completion-as-tool-certification.md) — why one successful call is not evidence a tool returns the right answers
- [Tool Cloning and Provenance Assessment](../../tool-engineering/tool-cloning-provenance-assessment.md) — the other way registry text overstates what a marketplace holds
- [Tool Description Quality](../../tool-engineering/tool-description-quality.md) — writing descriptions for your own agents, where no rival is reading them
