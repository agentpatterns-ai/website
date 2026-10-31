---
title: "Measure Tool-Name Resolution Before Adding Call Repair"
term: "Tool-Name Resolution Gate"
description: "A validate-and-repair layer in front of tool calls can only fix a call it can route to a tool. Count the invalid calls that name no visible tool first."
tags:
  - agent-design
  - tool-agnostic
  - tool-engineering
  - arxiv
aliases:
  - tool-name resolution gate
  - unresolved repair targets
  - repair-path resolvability
last_reviewed: 2026-10-21
maturity: emerging
---

# Measure Tool-Name Resolution Before Adding Call Repair

> This constrained repair layer needs a resolvable tool target, so measure how often your model names a visible tool first.

Count invalid calls that still name no visible tool after the candidate-set retry. These unresolved targets cannot enter constrained repair ([Chattopadhyay et al., arXiv:2610.23342v1](https://arxiv.org/abs/2610.23342v1), §6.7).

The layer needs no model training. SchemaShield-Lite validates the emitted call against the tool's required fields and argument structure, retries over the visible candidate set when the call omits a tool name, then issues one constrained repair call carrying the validation errors. On Qwen3.5-9B it moved accuracy under interface drift from 0.580 to 0.805 on a 200-example BFCL slice with no repair harms observed ([Chattopadhyay et al., arXiv:2610.23342v1](https://arxiv.org/abs/2610.23342v1)). On a different base model the same stack moved accuracy 0.030, because that model frequently failed to name a tool at all.

## The number to collect

The paper's own metric is the honest one: unresolved repair targets, meaning examples where the validator fired but no visible tool could be pinned, so no constrained repair could run. Four models, same non-oracle protocol, same BFCL-200 slice ([§6.1, §6.7](https://arxiv.org/abs/2610.23342v1)):

| Base model | Drifted | Repaired | Unresolved repair targets | Drift misses recovered |
|---|---|---|---|---|
| Qwen3.5-9B | 0.580 | 0.805 | 9 | 33/45 |
| Qwen3.5-35B-A3B | 0.635 | 0.845 | 1 | 33/38 |
| Llama-4-Scout | 0.635 | 0.665 | 43 | 1/11 |
| GPT-4o-mini | 0.840 | 0.860 | 0 | not reported |

For the GPT-4o-mini row the authors added provider-safe tool-name aliasing for OpenAI-style tool schemas, and they label that run a credibility check rather than a headline result.

Llama-4-Scout shows why model-specific measurement matters. Its gain is 0.030, with p=0.031. The authors name the cause: "this run exposes an important portability failure mode: the model omits the tool name frequently, leaving 43 unresolved repair targets and limiting recovery on the originally-correct slice to just 1/11 drift misses" ([§6.7](https://arxiv.org/abs/2610.23342v1)). Their reading generalizes past the one model, because "non-oracle repair quality depends heavily on the base model's ability to emit a usable tool name" ([§6.7](https://arxiv.org/abs/2610.23342v1)).

Collecting the number does not require building the layer. Replay calls your agent already got wrong, parse each one, and check the tool name against your current registry. Three buckets come out: names a visible tool, names nothing, names something outside the set. The first bucket can enter constrained repair immediately; a candidate-set retry can make additional calls resolvable.

A candidate-set retry moves calls out of the second bucket, and it is worth running before you conclude your model cannot be routed. Adding it took Qwen3.5-9B from 0.780 to 0.813 on DICE and 0.725 to 0.805 on BFCL, with unresolved targets falling from 35 to 15 and from 34 to 9 ([§6.1](https://arxiv.org/abs/2610.23342v1)). It did not rescue Llama-4-Scout, whose 43 is the count after the retry.

## Why it works

The validator emits a structured error report naming the offending field rather than a pass/fail bit, and the repair prompt carries that report alongside the invalid call. The authors localize the load-bearing component to "the validation error feedback loop combined with tool-constrained repair, not the canonical tool card presented at repair time" ([§6.5](https://arxiv.org/abs/2610.23342v1)).

Two baselines isolate that. A naive retry of the identical drifted prompt reached 0.727 on DICE and 0.610 on BFCL. A tool-list re-prompt that flags the call as invalid and lists the available tool names, while withholding the validation errors and the invalid call, reached only 0.753 and 0.625, against 0.813 and 0.795 for the full stack. The authors conclude: "The structured validation feedback, not merely knowing which tools are available, is therefore the load-bearing component" ([§6.2](https://arxiv.org/abs/2610.23342v1)).

The precondition falls straight out of that mechanism. Constraining a repair call to one tool requires a tool, so a missing name forces either a candidate-set retry or no repair at all.

## Prevention and recovery are separate purchases

A canonical tool card prepended to the initial prompt, with no validation and no repair, lifted the drifted BFCL score from 0.640 to 0.810. It recovered nothing: "the card-only configuration still never triggers the validator and recovers zero drift-induced failures, because its valid-but-imperfect outputs pass schema checking without entering the repair path" ([§6.5](https://arxiv.org/abs/2610.23342v1)). Its trigger rate was 0.0% on both benchmarks.

The card is drift prevention at prediction time and the validator is drift recovery after the fact. Dropping the card from the repair prompt cost nothing once a target was resolved, and validation-plus-retry without it scored 0.820 on BFCL against 0.795 for the full pipeline. Those rows are oracle-constrained upper bounds, so read them as mechanism evidence rather than deployment numbers. The card-only run covers Qwen3.5-9B alone. Whether the card helps a model with a high unresolved count, such as Llama-4-Scout, is untested.

## When this backfires

- Your count comes back high. There is no threshold to quote, because the paper reports 43 unresolved targets for Llama-4-Scout without reporting the total number of repair triggers and says only that the model omits the tool name "frequently" ([§6.7](https://arxiv.org/abs/2610.23342v1)). Read the count as a ceiling rather than a pass/fail test: that run bought 0.030 accuracy and recovered 1 of 11 drift misses.
- Drift barely hurts your model. GPT-4o-mini, once provider-safe tool-name aliasing was added for OpenAI-style schemas, fell only from 0.865 to 0.840 and repaired to 0.860, a gain "small and not significant on this 200-example slice (exact McNemar p=0.125)" ([§6.7](https://arxiv.org/abs/2610.23342v1)). The overhead is only measured on the primary model, so price it from there: Qwen3.5-9B paid 32.6% and 47.1% relative token overhead on its two runs. A separate instrumented Qwen rerun put repair calls at 13.0s against 9.3s for the drifted call, or roughly 3.5s expected added latency per example at its 27.0% trigger rate ([§6.1](https://arxiv.org/abs/2610.23342v1)).
- Your failures are valid but wrong. A call with correct syntax and a wrong value never trips the validator. Across the full slices, 63 of 85 DICE and 73 of 84 BFCL drift misses were validator-visible, so the remainder bypassed the repair path.
- The distractor tools are hostile rather than accidental. Repair does not establish tool provenance, and the authors ask you to "pair it with provenance checks on newly added tools" ([Broader impact](https://arxiv.org/abs/2610.23342v1)).
- Your scorer is strict string matching. Of 13 unrecovered cases in the oracle-constrained DICE sweeps on the three non-primary models, 11 were formatting or paraphrase artifacts and 2 were genuine failures. On Mistral-24B the drifted score (0.777) beat the original (0.740), and 15 of 23 apparent drift gains were strict-match artifacts. Strict matching can confound both damage and recovery measurements.
- Your drift does not look like theirs. The three operators are stale description examples, parameter renaming, and distractor tools, all author-designed. The ecological check is a manual audit of 11 Notion and Stripe changelog items from 2022 to 2026. Six map to the description and schema operators, three are close candidate-set analogues, and two fall outside the semantics-preserving scope. Type narrowing, enum replacement, and multi-tool refactors are untested.

## The alternative worth measuring

Grammar-constrained decoding can enforce a required tool-name field drawn from the candidate set, if the grammar encodes both constraints. Masking invalid tokens then prevents missing or out-of-set names. It carries its own tax. Constrained decoding "often reduces semantic correctness on reasoning-intensive tasks" ([§1](https://arxiv.org/abs/2603.03305v2)), because masking and renormalizing alters the model's distribution at every token. A draft-then-constrain fix recovers "+10.6 points (32.9 → 43.5) over standard CD evaluated over 6 models and 4 datasets" ([Figure 2](https://arxiv.org/abs/2603.03305v2)). That trades an unresolvable-name problem for a semantic-correctness problem, which is worth measuring on your own stack rather than assuming either way.

One scoping note on the same paper's drift ablation, where description rewording cost 0.013 accuracy against 0.047 for a single distractor tool. An independent study across 21 models finds the same ordering: description paraphrase (its Observation axis) costs less than 5%, and same-name or redundant distractors (its Action axis) cost 10 to 20 points. It adds a third axis, misleading metadata, at about 40% ([Zhou et al., arXiv:2605.11928v2](https://arxiv.org/abs/2605.11928v2)). The taxonomy page linked below carries the per-axis detail.

## Key Takeaways

- Count unresolved repair targets before you build the layer. The published range on one 200-example slice runs 0 to 43 across four models, and the 43 row gained 0.030 accuracy.
- A candidate-set retry reduced that count in the primary runs, worth 35 to 15 and 34 to 9 on the primary model's two slices. It did not rescue the model that omits names.
- Put the validator's field-level errors in the repair prompt, not just the tool list. Listing the available tools on its own reached 0.753 and 0.625, against 0.813 and 0.795 with the errors attached.
- Buy prevention and recovery separately. The canonical card lifted a drifted BFCL score 17 points and recovered zero failures, triggering the validator 0.0% of the time.
- The clean evidence is two Qwen models wide, and the authors say so: "the cleanest successful non-oracle evidence is still concentrated in the Qwen3.5 family" ([§8](https://arxiv.org/abs/2610.23342v1)).

## Related

- [Tool Schema Bias](../../tool-engineering/tool-schema-bias.md) — the same surface measured before deployment, where the question is which schema shape to ship rather than what to do when it moves.
- [Semantic Validation for Schema-Valid Agent Output](../../verification/semantic-validation-schema-valid-output.md) — the check that catches the valid-but-wrong calls this layer's validator lets through.
- [Belief Inertia After Tool-Map Drift](../anti-patterns/belief-inertia-after-tool-map-drift.md) — drift that changes tool semantics across a session, where the failure is retrieval rather than a malformed call.
- [Retry, Switch, or Abstain](retry-switch-abstain-recovery-policy.md) — the policy question one level up, once a tool call has failed and you choose between recovery moves.
- [Tool-Use Sim-to-Real Perturbation Taxonomy](../../verification/tool-use-sim-to-real-perturbation-taxonomy.md) — the perturbation axes these three operators sit inside, with the competing ranking of which axis hurts most.
