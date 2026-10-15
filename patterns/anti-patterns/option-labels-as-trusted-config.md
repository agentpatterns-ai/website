---
title: "Treating a Gate Model's Option Labels as Trusted Configuration"
term: "Option-Channel Attack"
description: "Where a caller packs the option names into a typed decision model's input, renaming the permissive option drives fail-open rates to 93-100% on four of six models tested, on each model's worst policy, with the policy and the judged text untouched."
tags:
  - anti-pattern
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - option-channel attack on a guardrail model
  - option labels as an attack surface
  - renaming the permissive option
last_reviewed: 2026-10-12
maturity: emerging
---

# Treating a Gate Model's Option Labels as Trusted Configuration

> Some callers pack a gate model's option labels into its input, and renaming the permissive option then opens it while the policy stays correct.

A typed decision model reads a piece of text and returns a probability over caller-defined options, each carrying a short label and a written definition, and generates no text. Deployments put one between a proposed tool call and its execution: it reads the call and the policy, and answers allow or block. The anti-pattern is to treat the judged text as hostile, which it is, while the option labels arrive from a config file and get read as configuration. Azizi, Baghaei Potraghloo and Pedram renamed only the permissive option. They left its definition correct and the judged text byte-identical. They report that this "raises that rate to between 93% and 100% on the four models that place the label in their input" ([Azizi et al., 2026](https://arxiv.org/abs/2610.12292v1)). Those rates are each model's worst policy over a vocabulary of candidate labels, and two of the four already failed open at 90% or more with the honest label.

## When the channel is open

The attack needs a path by which an untrusted string becomes a label. The paper names four: the typed question is assembled from a configuration file, from a policy document fetched at run time, from a schema a tool supplies, or by the agent writing its own gating questions ([Azizi et al., 2026 §4](https://arxiv.org/abs/2610.12292v1)). Where the question is a fixed literal in reviewed source and none of those four applies, the option channel has no entry point, and your exposure is the text channel alone.

Whether the label reaches the network at all is a property of the calling library rather than the weights. Two of the six models evaluated on the synthetic suite record an effect of exactly zero. Their caller packs the sequence from the definitions and uses the label only as a dictionary key: "It reaches the network only in the fallback case where no definition was supplied" ([Azizi et al., 2026 §6.3](https://arxiv.org/abs/2610.12292v1)). Read your gate's calling code before you reason about its robustness.

## Why it works

Correct block decisions are made by a small margin, so a small shift reverses them. Over the 338 items one gate correctly blocked across three public screening tasks, the median probability of block is 0.57, 97.0% of those decisions fall below 0.70, and the highest observed is 0.82. The authors draw the consequence: "an attack has to move the probability only a few hundredths to reverse the decision" ([Azizi et al., 2026 §6.4](https://arxiv.org/abs/2610.12292v1)). A renamed label supplies that shift without touching any attribute the policy is defined over.

The effect is not confined to security vocabulary, which is what makes it hard to filter. Sweeping 198 candidate labels for the permissive option on the one policy where that gate is accurate on clean input, labels naming a security action averaged 57% fail-open against 0% for the honest naming, neutral tokens such as `option_2` reached 37%, and the unrelated noun `obsidian` reached 100% ([Azizi et al., 2026 §6.3](https://arxiv.org/abs/2610.12292v1)). It is cheap: averaged over all six policies, trying labels in random order reached an expected 84% after five tries and 90% after ten on laya-td, against 60% honest. Labels also transfer. An attacker who can query one model of a family gets the effect on a sibling it never touched ([Azizi et al., 2026 §6.3](https://arxiv.org/abs/2610.12292v1)).

The attack costs the most on the best gate in the study. A `Qwen2.5-7B` readout had a mean honest fail-open rate of 5% and blocked every violation on four of the six policies; renaming the permissive option `remediate` took it to 100% on all six. The authors draw the conclusion directly: "The attack is not a weakness of small encoders, and it costs the most where the gate is otherwise worth deploying" ([Azizi et al., 2026 §6.3](https://arxiv.org/abs/2610.12292v1)).

## What the mitigations cost

Every figure in this table comes from the same study ([Azizi et al., 2026 §7, §8, §9](https://arxiv.org/abs/2610.12292v1)). Where a cost is given for one policy, that policy is `unauth_irrev`, the one synthetic policy on which the measured gate is accurate before any attack.

| Measure | What it does | Measured cost |
|---|---|---|
| Rewrite labels to `A` and `B` at the call site | Closes the option channel completely, and is the cheapest measure tested | Clean fail-closed on one policy rises from 25.3% to 36.0% |
| Pass parsed policy fields instead of the raw trace | Only defense that never lost the matched comparison, winning 16 of 18 cells | Refuses 68.7% of permitted actions on one policy; an adaptive attacker reaches 100% fail-open on four of the five typed models |
| Instruct the model to ignore the option names | Does almost nothing on the three typed models (99% attacked vs 98% undefended on laya-td); on the Qwen2.5-7B readout it removes the best label the undefended attack had found | Buys query budget only: on Qwen2.5-7B a fresh sweep returns 100% fail-open on all six policies using `harpsichord` |

Two habits that look like safety nets are measured and do not hold. Escalating low-confidence decisions does not find reversed ones. Across 1410 reversals the pooled margin was 0.149 before the attack and 0.151 after. At a review budget of 10% of traffic "the fail-open rate under attack falls only from 60% to 54%" ([Azizi et al., 2026 §6.5](https://arxiv.org/abs/2610.12292v1)). Nor is the returned probability a risk dial. On one policy, moving the threshold from 0.50 to 0.40 took the clean fail-closed rate from 26.0% to 70.7%. It bought a drop in attacked fail-open from 68.7% to 10.0%. At 0.30 the gate blocked every item ([Azizi et al., 2026 §6.4](https://arxiv.org/abs/2610.12292v1)).

One free fix sits outside that table. State the blocking condition as a property that is present rather than as a negation. Negated phrasing such as "the destination host does not end in .internal.corp" produced fail-open rates of 100% on two policies ([Azizi et al., 2026 §6.1](https://arxiv.org/abs/2610.12292v1)).

## Where a rule replaces the model

The most useful result argues the model away. Applying each policy with a deterministic rule over the same parsed field values that the strongest defense requires "reaches 100% accuracy on all six policies". The fail-open rate is zero under both attacks ([Azizi et al., 2026 §7.1](https://arxiv.org/abs/2610.12292v1)). The authors state the implication as a test you can run against your own gate: "Where the input can be parsed well enough to protect the model, it can be parsed well enough to decide without the model."

They also bound it. The synthetic suite is built so every attribute its policies name appears in the trace, which is what makes a rule possible. The paper says that a rule solving it "is a property of the construction rather than evidence that these tasks are easy in general" ([Azizi et al., 2026 §7.1](https://arxiv.org/abs/2610.12292v1)). On the three public screening tasks no field parses into a decidable value, so there is no rule to substitute.

## When this backfires

- Dropping the gate rather than demoting it. The paper's own recommendation keeps it: these models "can reduce how many cases reach a reviewer, but on this evidence they should not be the component that decides" ([Azizi et al., 2026](https://arxiv.org/abs/2610.12292v1)). A team that deletes the pre-filter raises reviewer load and closes no channel.
- Generalizing from these subjects to every model-based safeguard. The study covers open-weight models between 151M and 421M parameters plus a `Qwen2.5-Instruct` baseline, and does not measure the commercial model that introduced the interface ([Azizi et al., 2026 §10](https://arxiv.org/abs/2610.12292v1)). Anthropic's Constitutional Classifiers++ is a two-stage cascade that escalates suspicious exchanges to more expensive classifiers, and reports production-grade robustness after more than 1,700 hours of red teaming while "maintaining a 0.05% refusal rate on production traffic" ([Constitutional Classifiers++, 2026](https://arxiv.org/abs/2601.04603v1)).
- Treating label-invariance as robustness. It closes this channel and nothing else. Pooled over all six policies, the label-invariant `von` recorded a 41.1% attack success rate under the six-line distraction attack, above `laya-en` at 24.2% ([Azizi et al., 2026 §6.3](https://arxiv.org/abs/2610.12292v1)).
- Taking these rates as worst cases. The attacks draw from a fixed text pool and a fixed vocabulary, so the authors state that "the numbers reported here are lower bounds on what is achievable" ([Azizi et al., 2026 §10](https://arxiv.org/abs/2610.12292v1)).

## Example

Three questions to ask of a gate you already run, in this order.

1. Can any string outside reviewed source reach an option label? Trace the typed question back to where it is assembled. A config file, a fetched policy document, a tool-supplied schema, or an agent writing its own question each put the label in reach.
2. Does your calling library pack the label into the model's input? Read the call-site code rather than the model card. If it does, rewrite labels to canonical placeholders there and keep the definitions.
3. Do the fields your policy names parse into values? If they do, write the rule and keep the model as a volume reducer in front of a reviewer. If they do not, the gate stays probabilistic and you need a control behind it that does not read text.

## Key Takeaways

- The option labels passed to a typed decision model can reach the model as input rather than staying configuration, and your calling library decides which. The deployment literature barely checks it: one evidence review found that "only 1 of 27 tests whether a decision is invariant to the names given to the options" ([Azizi et al., 2026 §3](https://arxiv.org/abs/2610.12292v1)).
- Report fail-open and fail-closed separately before trusting any rate. One gate in the study held the lowest fail-open rate in its table alongside a 100% fail-closed rate, because it blocked almost every input ([Azizi et al., 2026 §6.1](https://arxiv.org/abs/2610.12292v1)).
- Whether the label reaches the network is a calling-library choice, so two implementations of the same interface differ by the whole attack.
- Deployed gates lean on escalating the least confident cases and on a threshold matched to a risk appetite, and this study measures both away ([Azizi et al., 2026 §6.4](https://arxiv.org/abs/2610.12292v1)). Budget for a reviewer rather than for tuning.
- Where the policy fields parse, code the rule and demote the model to a pre-filter; where they do not, put a deterministic control behind the gate instead of tuning its threshold.

## Related

- [Classifier-Gated Auto-Permission for Cloud-IDE Coding Agents](../agent-design/classifier-gated-auto-permission.md) — the affirmative pattern this page supplies a failure mode for: it splits the allow decision between a classifier and a human, and its reviewer-injection surface includes the option labels
- [A Guard Hook Approves the Truncated Input It Was Handed](guard-approves-truncated-input.md) — the other way a gate rules correctly on the wrong input, where the judged text was silently cut rather than the labels renamed
- [Treating a Model-Judged Hook as a Deterministic Control](model-judged-hook-as-deterministic-control.md) — the same mistake one layer out, counting a model's verdict as part of the deterministic hook layer
- [Splitting the Drift Judge from the Advisor (LivePlan)](../agent-design/judge-advisor-split.md) — the shape this page argues for, with a deterministic component deciding and the model advising
- [Model Confidence as Security Verification](model-confidence-as-security-verification.md) — why the returned probability is not the risk dial a threshold setting assumes
