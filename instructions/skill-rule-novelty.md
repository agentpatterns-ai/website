---
title: "Skill Rule Novelty: Add What the Skill Does Not Name"
term: "Skill Rule Novelty"
description: "An added skill rule moves an agent only when it names a command or path the skill lacked, and the measured gain is discounted by loading and applicability."
tags:
  - instructions
  - skills
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - skill revision novelty test
  - new-token rule test
  - skill rule expected value
last_reviewed: 2026-10-06
maturity: emerging
---

# Skill Rule Novelty: Add What the Skill Does Not Name

> A skill rule can only pay when it names a command or path the file does not already mention. Restating buys almost nothing.

Before adding a rule to a `SKILL.md`, check whether the token it names already appears in the file. Across 2,608 first/last revision pairs from 3,159 real skills, the gain from an added rule sits almost entirely with rules that introduce something the old version lacked. A new token lifts compliance from a baseline of 0.05 by +0.51 to +0.66; a rule about a token the skill already named starts at 0.61 and lifts it by +0.08 (95% CI +0.03 to +0.12) pooled over 107 probes, and the authors note part of the difference may be headroom, the room left above a high old-version rate ([Wang et al., 2026](https://arxiv.org/abs/2610.04832v1)). The headline figure averages both kinds: "Across 16 open-weight models, an added rule raises compliance in a single answer by +0.41 on average."

## When this applies

Three conditions carry the effect, and all three have to hold.

1. The rule names a command, path, flag, or identifier the skill does not mention. On the 23 sandbox tasks whose old skill already contained the required token, the study detected no gain in whether the agent took the action (Qwen 3.5-9B +0.00, 27B +0.06, Claude Sonnet 4.5 −0.13).
2. Real requests will need the rule. Of 1,454 later in-scope commit-rule pairs, "25% need the rule" (95% CI 14-40%), while every request pays the added input tokens.
3. The harness will put the body in front of the model. Under on-demand loading, "the action gain falls from +0.23 to +0.12": about 51% retained across four agents and 38% across three open models.

## Running the arithmetic before you edit

Multiply the conditional effect by how often it fires. The paper's own scenario puts an in-scope request at about 0.10 in single-answer compliance (0.25 × 0.41, 95% CI of the product 0.05 to 0.17) and about 0.06 in the required action of the four sandbox agents (0.25 × 0.23). Apply the loading discount and a rule in a skill the agent opens on demand is worth half of that again.

The cost on the other side is small. A single answer costs 18 to 19% more input tokens, and a sandbox episode showed no detectable change at all, −2.3 to +3.0% with every interval spanning zero, because the longer prompt bought fewer steps. "The old version costs 37 to 57% more tokens per episode than none", so whether to carry the body dominates whether to edit it.

Deletion is not the free inverse. Removing a rule lowered compliance with it by 0.27 to 0.33 on each of eight models, about three quarters of what adding one gained, so the authors tell maintainers: "Before deleting a rule, check that the agent should no longer follow it, since deletions are followed too."

## Why it works

The rule supplies information, and it binds that information to an action. Exposure alone does not substitute. Where the agent's own context already showed the token but the old skill lacked it, the revision still added +0.31 (95% CI +0.20 to +0.42), and Qwen 3.5-27B's old-skill agent, where it had seen the token in its own command output, still gained +0.19 (95% CI +0.08 to +0.29) from the new one ([Wang et al., 2026](https://arxiv.org/abs/2610.04832v1)). The gain is also not the document growing. "Unrelated text of the same length has no detectable effect", while stripping the rule line out of the new version cost about 0.21. Stating the rule adds +0.15 (95% CI +0.12 to +0.19) over a sentence naming the same token without an imperative, which is the distance between telling an agent a path exists and telling it to read that path.

## When this backfires

- The agent never opens the skill. Vercel measured the route itself as unreliable: "In 56% of eval cases, the skill was never invoked." The skill scored 53% on default behavior against a 53% baseline, while a docs index in `AGENTS.md`, an index that points at doc files rather than the documentation itself, passed every task ([Vercel, 2026](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)). No rule inside an unread file matters.
- The skill already fills the window. The gain falls from 0.424 at low occupancy to 0.270 once the skill takes three quarters of a model's usable context, and about two fifths of the short-answer effect survives in a 40k-token agent context.
- The rule is a prohibition, a conditional, or a permission guardrail. The study's literal filter keeps 17% of candidate directives and under-represents those classes.
- The agent is a frontier reasoning model. Every model answered with thinking disabled, and Claude Sonnet 4.5's human-judged correctness moved only +0.06 (95% CI −0.06 to +0.18) on 72 pairs, underpowered rather than null.
- Instructions as a whole may not pay. A separate evaluation found that providing repository context files "does not generally improve task success rates, while increasing inference cost by over 20% on average" ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v3)). Novelty says which rule is worth adding, not that the file is worth having.

## Example

In the `juxt/allium` repository, "a rule to run allium check shrinks the answer from 201 to 81 tokens and raises compliance from 0.07 to 0.99" ([Wang et al., 2026](https://arxiv.org/abs/2610.04832v1)). The command was absent from the old skill, so the rule was the only place the agent could learn it. Output got shorter because a model told which command to run stops hedging between candidates.

The counter-case is the same study's overhead tally. For one rule-model pair in five "the prompt grows but we detect no change in compliance" (95% CI 16.1-24.2%). Of the 55 rules that at least half the models scored that way, 27 were already followed without the rule and 28 were ignored whether present or not. The first group needs a removal test; the second needs rewriting.

## Key Takeaways

- Grep the skill for the token before you write the rule. A token already in the file predicts no gain in whether the agent acts.
- Never quote the headline +0.41 as what your skill will gain. It is a conditional effect measured on requests that need the rule, with the body already in the prompt; production meets neither condition by default.
- Carrying a skill body costs 37 to 57% more tokens per episode and revising one costs almost nothing per episode, so budget the decision to load rather than the decision to edit.
- Deleting a rule removes about three quarters of the compliance an equivalent addition buys. Treat removal as a behavioral change and test it.

## Related

- [Cost-Aware Skill Rewriting](cost-aware-skill-rewriting.md) — which lines to keep when a skill has to get shorter.
- [The No-Op Test](behavioral-no-op-test.md) — the empirical check that settles whether a line earns its place; novelty is the prior that predicts the result.
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — why a gain shrinks as the file grows against the window.
- [Agent Context File Evolution](agent-context-file-evolution.md) — the maintenance loops around files that only ever grow.
- [Pre-Execution Skill Selection](pre-execution-skill-selection.md) — scoring a skill's layers before it runs, instructions included.
