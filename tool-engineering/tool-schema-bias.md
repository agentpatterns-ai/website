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
last_reviewed: 2026-10-19
maturity: emerging
---

# Tool-Schema Bias: Measure the Interface Before You Ship

> Two tool definitions exposing the identical executable action can produce agent success rates at opposite ends of the scale. That gap is tool-schema bias.

Tool-schema bias is systematic variation in an agent's task success across tool schemas that expose the same executable actions and reach the same environment states. An executable rewriting framework applied nine operators to one native schema, checked every variant against the native actions and final states, and ran eleven models on up to 32 variants. The finding: "success rates range from complete failure to 97% depending solely on the schema" ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)). Two conditions bound what to do about it: the effect concentrates in a few of the schema decisions, and it belongs to the model you measured rather than to schemas in general.

## Which schema changes move the number

Most measurements come from a synthetic environment of 12 domains, 168 native operations, and 2,748 task queries, scored by exact match against the gold actions ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)). The operators change tool grouping, individual tool representation, or dependencies across calls. Every quoted effect below comes from that paper.

| Schema change | Reported effect |
|---|---|
| Merge tools behind one discriminator argument | The costliest single-call change. "Splitting largely preserves native-schema performance, whereas fully merging tools reduces success by a median of 19 points" across the nine open-weight models |
| Split a tool by the value range of an argument | Largely preserves native performance, per that same comparison |
| Reorder arguments, strip descriptions, nest arguments, namespace tool names | Near-inert. These "leave every model close to its native score"; opaque function names hurt "the smallest Qwen2.5 model", a sensitivity that "vanishes with scale" |
| Spread one action over dependent calls, as a transaction protocol or a schema-discovery step does | The worst tier. These "collapse most earlier-generation models, often to near zero, and only the newest generation absorbs them" |
| Add a resolver call that converts a value to a handle | The exception in the other direction. Models that follow it "score at or above their native rate" |

Two effects hide inside the merge tier. At a fixed tool count, "grouping semantically related operations is consistently better than random or deliberately mismatched grouping". And the argument form of a merged tool matters. The nested argument form "costs every model 19 to 73 points", including models that lose under 7 points on the flat form ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)).

Newer models shrink the effect without closing it. The paper calls its two API-tested models closed: gpt-6-luna and GLM-5.3-Flash, and each moved by 32 points across equivalent schemas. Their weak spots were the variants that expose a large catalog, class dispatch and namespaced names, not the cross-call protocols ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)).

The same question returns after deployment, when the interface drifts underneath an agent you already shipped. One paper measures that case and splits the blame: "Ablations show that candidate-set drift, especially distractor tools, accounts for most observed damage, while description and schema edits alone are less harmful" ([arXiv:2610.23342v1](https://arxiv.org/abs/2610.23342v1)). That leaves the near-inert tier above standing and moves the exposure to the candidate tool list. Its authors report that a training-free validate-and-repair layer lifts success from 0.717 to 0.813 on DICE-300 and from 0.580 to 0.805 on BFCL-200 ([arXiv:2610.23342v1](https://arxiv.org/abs/2610.23342v1)). On Qwen3.5-9B, their primary model, the layer recovered 19 of 22 and 33 of 45 drift-induced failures ([arXiv:2610.23342v1](https://arxiv.org/abs/2610.23342v1)). A same-protocol BFCL replication on Qwen3.5-35B-A3B runs 0.635 to 0.845 ([arXiv:2610.23342v1](https://arxiv.org/abs/2610.23342v1)). These results come from Qwen3.5 models. Section 6.7 also reports weaker portability evidence from Llama-4-Scout and a GPT-4o-mini sanity check.

## What it costs to find out

Guessing from the schema text does not work. Two query-free probes, written automatically from the schema's own descriptions and argument values, ranked variants at a Spearman correlation of 0.52 and 0.57 against full-set success. About one hundred target queries per candidate schema lifted that correlation to 0.81, and even 36 queries reached 0.72, "so the probes fall short because they omit the tasks, not because they are small" ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)).

Draw that sample from the agent's target task distribution ([Liu et al., §7](https://arxiv.org/abs/2609.34971v2)).

One prompt-side lever survives when the schema belongs to somebody else. Describing a variant's calling convention in a single sentence moved one 4-billion-parameter model from 0.36 to 0.64 on the fully merged schema and from 0.07 to 0.52 on schema discovery, and had no noticeable effect on the other variants ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)).

## Why it works

Part of the bias is a failure to write the right action in the presented schema. In the failure analysis, a model "sometimes invokes the correct native action but fails to write it in the presented schema", and the largest such gap lands on the fully merged catalog, "driven by the Qwen3 and smaller Qwen2.5 models, which keep calling native tool names" ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)).
The training analysis points the same way. Fine-tuning on native-schema demonstrations "keeps native performance but does not repair the hard variants, so the repair comes from seeing a variant during training rather than from more tool-use practice" ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)). Practice at tool use does not make a model insensitive to the schema. Seeing that schema does.

Three of the seven failure modes the authors catalog are silent: the episode ends with too few native actions, too many, or the wrong argument values, with nothing rejected. Schema discovery mostly fails that way ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)), so no runtime error marks those episodes.

## When this backfires

- Your agent does open-ended work through a shell. Across 11,700 trajectories on repository-level issue fixing, six tool architectures left resolve rate flat: "The overall task resolve rate is similar across tool architectures for a given actor model" ([Xu et al., arXiv:2608.11386v1](https://arxiv.org/abs/2608.11386v1)). Run-to-run consistency moved instead.
- You measure the inert operators. A cycle spent on argument order, description text, or per-tool argument nesting returns nothing on the models the paper tested.
- You switch models and keep the tuned schema. Each model family is sensitive to different representations, and the authors state that "schema bias cannot be fixed once for all" ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)).
- You want a number for a model the paper never ran. The authors bound their own claim: "most measurements come from a controlled synthetic environment and a finite set of models, so the size of the effect on other benchmarks and model families remains to be established" ([Liu et al., arXiv:2609.34971v2](https://arxiv.org/abs/2609.34971v2)).

## Key Takeaways

- Sort a schema decision into its tier before you spend an eval on it. Merging or splitting tools changes tool-set partitioning. These grouping changes and cross-call protocols carry the largest measured effects.
- Budget about 100 queries per candidate schema, drawn from the agent's own task distribution. A probe built from the schema text ranks them only moderately well.
- Re-measure after a model upgrade. The ranking is a joint property of the model, the schema, and the queries.
- Where a vendor's schema is fully merged or needs a discovery step, try one sentence on its calling convention in the prompt, then measure whether that closes the gap.

## Related

- [Tool Architecture Moves Consistency, Not Resolve Rate](tool-architecture-consistency-lever.md) — the conflicting result on open-ended coding work, where reorganizing tools moved consistency and left resolve rate flat
- [Consolidate Agent Tools](consolidate-agent-tools.md) — the case for merging tools, which this page prices in success points
- [Tool Minimalism and High-Level Prompting](tool-minimalism.md) — how many tools to expose, as against how to shape the ones you keep
- [Tool Description Quality for Effective Agent Guidance](tool-description-quality.md) — the description text, which this measurement places in the near-inert tier
- [Poka-Yoke for Agent Tools](poka-yoke-agent-tools.md) — designing out the off-schema call instead of measuring what it costs
