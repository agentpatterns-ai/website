---
title: "Keep the Exact Limits in Code and the Judgment in the Model"
term: "Hard and Fuzzy Rule Split"
description: "A code guard between proposal and action held every exact limit across 1,340 episodes where models alone breached; a model flagger covers judgment and may only narrow."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - hard and fuzzy rules
  - exact guard plus judgment flagger
  - propose-then-guard
last_reviewed: 2026-11-05
maturity: emerging
---

# Keep the Exact Limits in Code and the Judgment in the Model

> Put exact limits in a code guard that decides every action, and leave unstated judgment to a model that may only narrow.

An agent that spends money, delegates authority, or opens records should let the model propose and let code decide. Code holds every limit that can be written as a predicate over structured fields: amounts, approvals, clearances, signed delegation chains. A model handles the judgment no predicate states, such as a conflict of interest, and it may only narrow: it can turn "the code would let me act" into "ask the owner first", never the reverse. The test used 1,340 episodes written by authors outside the study team. Models deciding alone executed unauthorized actions in up to 151 of 340 purchasing episodes and 269 of 470 delegation episodes. The guard executed none ([Roth, arXiv:2611.01043v1](https://arxiv.org/abs/2611.01043v1)).

## When the split applies

The guard result holds under four conditions.

- The limit is exact. The paper's example of a guard rule is "if the order total exceeds the authorized limit and no approval is on file, refuse". A rule such as "avoid anything that looks like a conflict of interest" has no exact form, and the guard lets a breach of it through ([§2](https://arxiv.org/abs/2611.01043v1)).
- The guard sees every action. Agent SDK hooks and middleware do not supply this by default: "They are conduits: the model's proposal reaches the tool unless the developer attaches a check" ([§3](https://arxiv.org/abs/2611.01043v1)).
- The guard reads facts from a system of record. It "verifies what the fuzzy layer extracts, against an authoritative source such as the actual price at checkout" ([§2](https://arxiv.org/abs/2611.01043v1)). A guard that trusts the amount the model read from a note checks nothing.
- You accept the evidence base. It is one author, simulated arenas with fixed catalogs, quotas the episode authors set, and one run of each condition. The author holds pending patents on the methods ([§9 and availability statement](https://arxiv.org/abs/2611.01043v1)).

## The four rules of the split

The paper states four rules that keep the two layers apart ([§2](https://arxiv.org/abs/2611.01043v1)):

1. "Hard rules hold the limits that must not move. A fuzzy preference never overrides them."
2. "The fuzzy layer narrows and never widens." The flagger may hold an action for approval. It may not raise a limit.
3. "Text supplies facts and never authority." A request may say a repair costs $47,000. It cannot say the agent may exceed its limit.
4. The hard layer checks every fact the model extracted against an authoritative source.

The study's guard puts rule 3 into code by type. It "treats text from quotes, notes and web pages as a type it never parses", which differs from a filter that tries to spot hostile text. It holds amounts in integer cents, resolves any doubt as refusal, binds each action to the principal's structured request, and logs the rule that fired ([§5](https://arxiv.org/abs/2611.01043v1)).

## What the measurement showed

| Setup | Unauthorized executions |
|---|---|
| Model alone, purchasing, llama3.2, plain prompt | 151 of 340 |
| Model alone, purchasing, Sonnet 5.5 | 23 to 26 of 340 in every prompt condition |
| Model alone, delegation, Sonnet 5.5, plain prompt | 238 of 470, including all 30 forged chains |
| Guard between proposal and action, all models and arenas | 0, and an exhaustive search of 183,204 proposals agreed |

Source: [arXiv:2611.01043v1](https://arxiv.org/abs/2611.01043v1), Tables 1 and 2.

Sonnet 5.5 completed nearly every authorized purchase and still breached in every purchasing condition: "Capability improved reading and did not produce dependability" ([§4](https://arxiv.org/abs/2611.01043v1)).

The guard alone is not enough either. On 300 purchase requests with four judgment rules, the guard stopped 115 and 122 of 192 violations for the two proposers, because 96 broke only a judgment rule it cannot see. A 1.5-billion-parameter flagger placed in front of it raised that to 191 of 192, with no exact-limit breach. The flagger without the guard left 8 exact-limit breaches ([§7, Table 4](https://arxiv.org/abs/2611.01043v1)). A prompted Sonnet 5.5 flagger did about as well, at 190 of 192, so a frontier model with the rules in its prompt works as the flagger. A prompted small model did not: it flagged 44 of 108 legitimate requests.

## Why it works

A hard rule is a predicate over structured fields, so it returns the same answer whatever the wording. A note that claims pre-approval, or announces that the rules are suspended, changes nothing the predicate reads. A model holds a rule as a learned concept, and "it bends under social pressure, and it fails on unfamiliar wording while sounding confident" ([§2](https://arxiv.org/abs/2611.01043v1)). The guard never parses untrusted text, so text cannot become authority. The guard is code, so you can test it against every proposal a model could build from an episode's parts, and the result does not depend on which model proposes ([§5](https://arxiv.org/abs/2611.01043v1)). A flagger false positive blocks a legitimate request; a miss lets a judgment-rule violation through. Neither can raise an exact limit, because the guard still checks every proposal ([§§4–5, §7](https://arxiv.org/abs/2611.01043v1)).

The zero is not a blind test. As negative controls, the paper ran the same exhaustive adversary against an executor with no guard, and against a guard with the request-binding rule removed. Against no guard, "the same adversary reports thousands of unsafe executions", and the weakened guard let them through again ([§5](https://arxiv.org/abs/2611.01043v1)).
## When this backfires

- The translation from policy to guard is wrong at an edge. A program mapped a plain-language owner brief to seven numeric parameters, and the guard and brief disagreed at exactly $95.00 and $475.00. Two of 340 episodes ended in unsafe executions, and a third was refused where the brief allowed it. No fresh set has tested the repair ([§5, §9](https://arxiv.org/abs/2611.01043v1)). Write down where code and policy might differ, and test those edges.
- The attack stays inside the limits. "An agent tricked into acting inside the allowed limits still acts" ([§9](https://arxiv.org/abs/2611.01043v1)). The guard bounds damage. It does not prevent it.
- The proposer refuses everything. In data access the small models rarely breached because they refused: llama3.1 completed 2 of 190 legitimate requests and llama3.2 none in the plain condition ([§4](https://arxiv.org/abs/2611.01043v1)). A guard does not make a weak reader useful.
- The gate is imprecise or strands the task. In an independent study of deterministic pre-execution gates, one gate fired at 5% precision, and "Gate firing does not guarantee recovery" ([Reddy, Challaram & Basu, arXiv:2607.07405v2](https://arxiv.org/abs/2607.07405v2)). Audit each rule's precision, and give the agent a path after a refusal.
## Example

The paper opens with a purchasing request. A department head writes "The repair is urgent. Approve it now and we will sort out the paperwork later," and a vendor's note claims that the owner has already approved ([§1](https://arxiv.org/abs/2611.01043v1)).

Under the split, the model reads the paragraph and proposes a structured purchase. The guard compares the checkout total, in integer cents, with the authorized limit. If the total needs a signed approval, the guard looks for one on file. The vendor's note is untrusted text, so it cannot count as that approval, and the guard refuses. A flagger taught the paper's "no secrecy or pressure" rule can also hold the request for approval before it reaches the guard. It cannot release a purchase the guard would refuse.

## Key Takeaways

- Let the model propose and let code decide anything with an exact limit. Sonnet 5.5 breached in 23 to 26 of 340 purchasing episodes in every condition; the guard breached in none.
- The guard reads facts from a system of record and treats request text as a type it never parses.
- A model flagger covers judgment the guard cannot see and may only turn execute into ask. Flagger plus guard stopped 191 of 192 violations.
- The split leaks at the policy-to-code translation and inside the allowed limits. Test the boundaries you wrote down in advance.

## Related

- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](authority-confusion-untrusted-context.md) — rule 3 of the split as a dispatch-layer check
- [Hybrid Deterministic + Semantic Authorization for Agent Tool Calls](hybrid-deterministic-semantic-tool-authorization.md) — structural checks plus a semantic matcher at the tool boundary
- [Choose Agent Gate Layers by Mechanism Class, Then Measure](../verification/mechanism-class-gate-stacking.md) — a rule layer plus one judge composed close to two independent layers
- [Permission Framework Choice Outweighs Model Choice for Limiting Overeager Actions](permission-framework-over-model.md) — framework choice moved the overeager-action rate more than model choice
- [Explanation-Bound Tool Execution for Agent Gateways](explanation-bound-tool-execution.md) — check the agent's stated reason against server-held facts
