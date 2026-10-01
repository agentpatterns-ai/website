---
title: "Tool-Schema Bias: Measure the Interface Before You Ship"
term: "Tool-Schema Bias"
description: "Functionally equivalent tool schemas produce very different agent success rates. Measure candidate schemas on about 100 of your own queries."
aliases:
  - schema bias
  - action-space shaping
  - tool schema sensitivity
tags:
  - tool-engineering
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-30
maturity: emerging
---

# Tool-Schema Bias: Measure the Interface Before You Ship

> Two tool definitions exposing the identical executable action can produce agent success rates at opposite ends of the scale. That gap is tool-schema bias.

Tool-schema bias is systematic variation in an agent's task success across tool schemas that expose the same executable actions and reach the same environment states. An executable rewriting framework applied nine operators to one native schema, checked every variant against the native actions and final states, and ran eleven models on up to 32 variants. The finding: "success rates range from complete failure to 97% depending solely on the schema" ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)). Two conditions bound what to do about it: the effect concentrates in a few of the schema decisions, and it belongs to the model you measured rather than to schemas in general.

## Which schema changes move the number

Most measurements come from a synthetic environment of 12 domains, 168 native operations, and 2,748 task queries, scored by exact match against the gold actions ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)). The nine operators sort into three tiers, and every quoted effect in the table below is from that paper.

| Schema change | Reported effect |
|---|---|
| Merge tools behind one discriminator argument | The costliest single-call change. "Splitting largely preserves native-schema performance, whereas fully merging tools reduces success by a median of 19 points" across the nine open-weight models |
| Split a tool by the value range of an argument | Largely preserves native performance, per that same comparison |
| Reorder arguments, strip descriptions, nest arguments, namespace tool names | Near-inert. These "leave every model close to its native score"; opaque function names hurt "the smallest Qwen2.5 model", a sensitivity that "vanishes with scale" |
| Spread one action over dependent calls, as a transaction protocol or a schema-discovery step does | The worst tier. These "collapse most earlier-generation models, often to near zero, and only the newest generation absorbs them" |
| Add a resolver call that converts a value to a handle | The exception in the other direction. Models that follow it "score at or above their native rate" |

Two effects hide inside the merge tier. At a fixed tool count, "grouping semantically related operations is consistently better than random or deliberately mismatched grouping". And the argument form of a merged tool matters. The nested argument form "costs every model 19 to 73 points", including models that lose under 7 points on the flat form ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)).

Newer models shrink the effect without closing it. The two closed models tested were gpt-6-luna and GLM-5.3-Flash, with no Anthropic model in the set, and each moved by 32 points across equivalent schemas. Their weak spots were the variants that expose a large catalog, class dispatch and namespaced names, not the cross-call protocols ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)).

## What it costs to find out

Guessing from the schema text does not work. Two query-free probes, written automatically from the schema's own descriptions and argument values, ranked variants at a Spearman correlation of 0.52 and 0.57 against full-set success. About one hundred target queries per candidate schema lifted that correlation to 0.81, and even 36 queries reached 0.72, "so the probes fall short because they omit the tasks, not because they are small" ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)).

Draw that sample from the traffic your agent will see. A ranking measured on the paper's synthetic tasks did not predict the ranking on τ²-bench ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)), so a borrowed sample can order your candidates wrongly.

One prompt-side lever survives when the schema belongs to somebody else. Describing a variant's calling convention in a single sentence moved one 4-billion-parameter model from 0.36 to 0.64 on the fully merged schema and from 0.07 to 0.52 on schema discovery, and had no noticeable effect on the other variants ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)).

## Why it works

Part of the bias is a failure to write the right action in the presented schema. In the failure analysis, a model "sometimes invokes the correct native action but fails to write it in the presented schema", and the largest such gap lands on the fully merged catalog, "driven by the Qwen3 and smaller Qwen2.5 models, which keep calling native tool names" ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)).
The training analysis points the same way. Fine-tuning on native-schema demonstrations "keeps native performance but does not repair the hard variants, so the repair comes from seeing a variant during training rather than from more tool-use practice" ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)). Practice at tool use does not make a model insensitive to the schema. Seeing that schema does.

Three of the seven failure modes the authors catalog are silent: the episode ends with too few native actions, too many, or the wrong argument values, with nothing rejected. Schema discovery mostly fails that way ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)), so no runtime error marks those episodes.

## When this backfires

- Your agent does open-ended work through a shell. Across 11,700 trajectories on repository-level issue fixing, six tool architectures left resolve rate flat: "The overall task resolve rate is similar across tool architectures for a given actor model" ([Xu et al., arXiv:2608.11386v1](https://arxiv.org/abs/2608.11386v1)). Run-to-run consistency moved instead.
- You measure the inert operators. A cycle spent on argument order, description text, or per-tool argument nesting returns nothing on the models the paper tested.
- You switch models and keep the tuned schema. Each model family is sensitive to different representations, and the authors state that "schema bias cannot be fixed once for all" ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)).
- You assume the native schema is the safe default. On the airline domain of τ²-bench, most earlier-generation models scored higher under some alternative schema than under the native one. On retail, the native schema was the best or near-best choice for almost every model ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)).
- You want a number for a model the paper never ran. The authors bound their own claim: "most measurements come from a controlled synthetic environment and a finite set of models, so the size of the effect on other benchmarks and model families remains to be established" ([Liu et al., arXiv:2609.34971v1](https://arxiv.org/abs/2609.34971v1)).

## Key Takeaways

- Sort a schema decision into its tier before you spend an eval on it. Tool-set partitioning and cross-call protocol hold the points; per-tool surface rewrites do not.
- Budget about 100 queries per candidate schema, drawn from the agent's own task distribution. A probe built from the schema text ranks them only moderately well.
- Re-measure after a model upgrade. The ranking is a joint property of the model, the schema, and the queries.
- Where a vendor's schema is fully merged or needs a discovery step, try one sentence on its calling convention in the prompt, then measure whether that closes the gap.

## Related

- [Tool Architecture Moves Consistency, Not Resolve Rate](tool-architecture-consistency-lever.md) — the conflicting result on open-ended coding work, where reorganizing tools moved consistency and left resolve rate flat
- [Consolidate Agent Tools](consolidate-agent-tools.md) — the case for merging tools, which this page prices in success points
- [Tool Minimalism and High-Level Prompting](tool-minimalism.md) — how many tools to expose, as against how to shape the ones you keep
- [Tool Description Quality for Effective Agent Guidance](tool-description-quality.md) — the description text, which this measurement places in the near-inert tier
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md) — designing out the off-schema call instead of measuring what it costs
