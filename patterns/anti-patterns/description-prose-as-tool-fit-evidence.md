---
title: "Reading Tool Fit Off a Provider-Written Description"
term: "Description-Framing Bias"
description: "Praise carrying no capability information moved tool pick rate by about 43 points on two preregistered models."
tags:
  - anti-pattern
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - description-framing bias in tool selection
  - sales text in tool listings
  - advertising to agents
last_reviewed: 2026-10-19
maturity: emerging
status: current
---

# Reading Tool Fit Off a Provider-Written Description

> Praise in a provider-written description shifted tool choices without adding capability evidence, and it beat task fit on numeric limits.

A registry listing is written by the provider who earns traffic when its tool gets picked, so "listings double as advertising" and the description your agent reads as a capability statement is promotional text ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)). The anti-pattern is letting that prose carry the fit decision. Wang built listing pairs differing in one factor and asked two small OpenAI models to call exactly one tool at temperature 0. Stacked praise, four phrases a script confirmed held no numbers, units, or capability words, "raised the share choosing the target by 44 points for nano and 43 for mini". The study did not establish a premium for checkability: for GPT-5.4-nano a verifiable specification came out 3.2 points behind a single superlative, with a 95% interval of [−9.1, +2.7] ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)).

## Where it bites

Stacked praise raised the target's share on the development and the sealed domains alike, though on the sealed ones no single kind of praise reached significance after correction. It beat task fit in one place only. Split the capability-conflict set by the kind of blocking limit and "neither model ever picked the incapable tool when its limit was a coverage or language restriction (7 development domains), with or without praise" ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)). Where the limit was a number too small for the task, stacked praise raised nano's picks of the incapable tool from 16% to 51%, and mini's from 0% to 21%. Both splits are post hoc on preregistered data.

Inside the numeric cases the damage tracked how hard the comparison was. With stacked praise nano picked the tool that could not do the job in 80% of file-management trials, where a 300 MB file met limits of 5 MB and 2 GB, and in 20% of email trials, where 120 recipients met limits of 3 and 500 ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)). The hard cases were unit mismatches or small shortfalls. In web search, where 5 results met a need for 15, nano failed in 68% of stacked-praise trials ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)).

List position is a separate effect, larger than praise and not reliably in one direction. With two identical listings "the first-listed tool's share was +72 points higher for nano and +72 for mini". Given two neutral listings in the exploratory study, the OpenAI models and DeepSeek took the first slot in 80% to 97% of trials, "but Claude picked it in only 21%: Claude favors the second slot" ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)).

## Why it works

Praise placed next to a numeric limit written in prose pulled picks toward tools that could not do the job. Without praise, nano picked the capable tool in 84% of prose trials and 88% of trials using structured fields. The estimated format effect was +3.1 points, with a 95% interval of [−2.5, +8.8] that includes zero ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)). Add praise and prose fell to 49% while fields held at 75%, an interaction of +22.5 points with an interval of [+14.4, +30.6]. The author states the mechanism: "the fields helped nano mainly by blunting praise; nano could compare numeric limits in prose when no praise sat beside them" ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)). Position decided the pick on the same logic, when the listings left the model nothing else to decide on: nano's order gap fell to zero whenever a coverage limit settled the choice.

## What a harness owner can change

Three moves follow from the measurements, and rewriting the provider's prose is not one of them.

1. Compare fit constraints outside the description. Where the request needs 120 recipients or a 300 MB upload, filter on a field you populate and verify rather than on a sentence the provider wrote. Fields carrying no sales text raised nano's correct picks on numeric limits from 49% to 88% ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)).
2. State limits in the units the request uses. The failures concentrated where "the limit was in other units than the request" or the shortfall was small ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)).
3. Set the order yourself instead of inheriting the registry's. Structure also shrank nano's order gap on numeric limits from −71 points to −20 ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)).

Do not substitute a warning in your system prompt for any of the three. In the exploratory study's three top consumer domains, a "Sponsored" label on the listing "lowered the share choosing the sales-heavy tool by 26 to 34 points in four of five models", while telling the model that some tools are commercial partners "moved one model of five (Claude, −12 points)" ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)).

## When this backfires

- The blocking constraint is categorical. "Praise never led either model to a tool lacking the needed region or language (8 applications, every format)" ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)). Moving a jurisdiction or language restriction into a field buys nothing this study can measure.
- Your tool set is a fixed internal allowlist with one candidate per job. Framing and position bias both need a choice between listings to act on.
- You treat description rewriting as the fix. Augmenting MCP tool descriptions across every rubric component "improves task success rates by a median of 5.85 percentage points", and in the same measurement "increases the number of execution steps by 67.46% and regresses performance in 16.67% of cases" ([Hasan et al., 2026](https://arxiv.org/abs/2602.14878v3)).
- You copy a mitigation built for interchangeable tools. Blankenstein and co-authors cut selection bias with "a lightweight mitigation strategy that first filters tools to a relevant subset and then samples uniformly" ([Blankenstein et al., 2026](https://arxiv.org/abs/2510.00307v2)). Their filter asks a smaller model for only the APIs "that can solve the given query". They tested the filter on a separate set of 1,000 queries with 8 candidates each, where 2 to 5 could solve the query. It reached a micro-precision of 0.9964 ([Blankenstein et al., 2026](https://arxiv.org/abs/2510.00307v2)). The paper does not say whether the other candidates failed on near-miss numeric limits like Wang's. Uniform sampling does not guarantee task fit if an incapable tool survives the filter.
- You generalize past the evidence. The preregistered results "cover two small models and two-tool registries, and analyses marked post hoc were chosen after seeing the data" ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)). The paper calls these results provisional until blind phrase ratings are complete. On the three sealed domains stacked praise still moved picks, by 35 points for nano and 31 for mini, but no single kind reached significance after correction.

## Example

The listing text below is the email stimulus from the format study, reproduced from the paper's Appendix E along with its query ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)). The Tool A and Tool B labels are added here for reference; the study omitted tool names and varied their order across trials. The request is: "Send the newsletter to all 120 subscribers on the mailing list in one message."

**Before — the limit sits in prose, behind four praise sentences:**

```text
Tool A: Quite simply the finest email sending tool anywhere. Relied on by a
large and growing community. Recognized by independent industry panels. The
smart choice for great outcomes. Sends an email message. Takes recipient
addresses, subject, and body. Returns a message ID and delivery status.
Maximum recipients per message: 3.

Tool B: Sends an email message. Takes recipient addresses, subject, and body.
Returns a message ID and delivery status. Maximum recipients per message: 500.
```

**After — the same facts as fields, with the provider text dropped:**

```text
Tool A: Function: Sends an email message. Takes recipient addresses, subject,
and body. Returns a message ID and delivery status.
Capability limit: Maximum recipients per message: 3.

Tool B: Function: Sends an email message. Takes recipient addresses, subject,
and body. Returns a message ID and delivery status.
Capability limit: Maximum recipients per message: 500.
```

Nothing about Tool A's capacity changed between the two forms. On this application nano picked the capable tool in 70% of trials given the first form and 95% given the second ([Wang, 2026](https://arxiv.org/abs/2605.23916v3)).

## Key Takeaways

- Treat a registry description as the provider's advertising copy, and put anything your harness needs to check somewhere the provider does not write.
- The study did not establish that checkability outperforms praise. Do not rely on adding numbers to a description as a sufficient mitigation.
- Praise reversed only numeric thresholds, and mainly where comparing one took a unit conversion or the shortfall was small. Categorical constraints held at 0% wrong picks in every format tested.
- Position is a separate and larger effect, and one of the five models tested favored the second slot. Do not assume the first candidate in a list is the one your agent leans toward.
- Structured fields helped mostly by separating the number from the sales text, so the cheaper version of this fix is to move your fit comparison out of the description entirely.

## Related

- [Treating a Gate Model's Option Labels as Trusted Configuration](option-labels-as-trusted-config.md) — the same mistake on a different channel, where a string that arrives as configuration reaches the model as input
- [Canary Tools for Diagnosing Tool-Selection Reasoning](../../verification/canary-tools-tool-selection-diagnosis.md) — how to find out which property of your own listings your model over-trusts
- [Blind Tool Deference: Agents Parroting Callable Tools](blind-tool-deference.md) — the matching failure one step later, trusting what a tool returns rather than how it sold itself
- [Multi-Tool Threshold Poisoning Against MCP (ShareLock)](multi-tool-threshold-poisoning-mcp.md) — the adversarial end of the same surface, where description text carries a reconstructed payload instead of sales copy
- [Tool Description Quality for Effective Agent Guidance](../../tool-engineering/tool-description-quality.md) — the affirmative case for writing good descriptions, which this page qualifies from the reader's side
