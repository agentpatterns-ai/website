---
title: "Canary Tools for Diagnosing Tool-Selection Reasoning"
term: "Canary Tools"
description: "Plant deliberately flawed decoy tools in a staging copy of your tool set so a wrong-tool result names which property of your descriptions the model over-trusts."
tags:
  - testing-verification
  - evals
  - cost-performance
  - mcp
  - tool-agnostic
  - arxiv
aliases:
  - canary tool injection
  - tool-selection probe taxonomy
  - diagnostic decoy tools
last_reviewed: 2026-08-07
maturity: emerging
---

# Canary Tools for Diagnosing Tool-Selection Reasoning

> Canary tools are decoy tools planted in a staging tool set, each probing one tool-selection weakness so a wrong-tool result names its cause.

A canary tool copies one of your real tools and spoils exactly one property of its advertisement: wording, parameter feasibility, advertised power, an implicit prerequisite, a recency marker, or scope. Because only that property changed, how often an agent picks the canary over the real tool tells you which property it over-weights. Six such perturbations over 120 tasks and 8,640 runs on eight models turn a bare wrong-tool outcome into a per-property profile ([Anand and Chattaraj, 2026](https://arxiv.org/abs/2608.04719v1)).

## The six probe types

| Type | Transform applied to a real tool | Weakness probed |
|---|---|---|
| Semantic decoy | Rename and paraphrase the description, keep the schema, admit it returns stale data | Name matching instead of reading |
| Parameter trap | Rename parameters and add an unsatisfiable required argument | Feasibility checking before selection |
| Capability mirage | Inflate the advertised powers | Trust in capability claims |
| Prerequisite blindness | Drop the auth requirement while marking the resource privileged | Reasoning about implicit prerequisites |
| Temporal decoy | Append an outdated date or version | Weighing recency |
| Granularity trap | Remove parameters and hardcode one case | Matching tool scope to task scope |

Four of the six are deterministic schema transforms, so you can generate them from an existing tool set with no training. Semantic decoys and capability mirages also need an LLM to reword names ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)).

## Read the profile as tier-stratified

Which probes carry signal depends on the model you ship. Across six hosted models capability mirage was the only strongly active probe, trap rate 0.216 against 0.008 to 0.027 for the other five, and the authors name prerequisite blindness as the only type that rivals it further up the capability curve ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)). On a frontier deployment, near-silence on the remaining types is the expected outcome rather than a pass.

At the small end the problem inverts. On Llama 3.1 8B all six fired between 0.106 and 0.255, temporal decoys at 0.255 and parameter traps at 0.245 against 0.009 and 0.008 hosted, so the profile localizes nothing ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)).

Capability tier does not predict which way a deployment falls. Susceptibility spans 0.010 for Claude Opus 4.8 to 0.378 for Llama 3.1 8B, GPT-4.1 out-failed all three frontier models tested, and within Google the cheaper Gemini 2.5 Flash scored 0.041 against 0.049 for Gemini 2.5 Pro ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)). Tool-poisoning work finds the same direction adversarially: over 45 live MCP servers, more capable models were often more susceptible, because the attack exploits their stronger instruction-following ([Wang et al., 2025](https://arxiv.org/abs/2508.14925v1)).

## The diagnostic loop

1. Copy the tool set into a staging harness. Canaries return auth errors, stale data, and single-case results by design, and the authors position the method as a pre-deployment readiness check rather than a production monitor ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)).
2. Generate one canary per type from a real tool, spoiling one property each.
3. Run your task suite and record a trap rate per type, not one aggregate score.
4. Record a recovery rate beside each trap rate. Claude Opus 4.8 recovered on 0.82 of trapped tasks and Llama 3.1 8B on 0.18, so a cheap post-call check turns a sprung trap into a near-miss ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)).
5. Harden the highest-rate property, then re-probe to confirm the rate moved.

Probe density is not diagnostic pressure. Injecting all six types at once read lower than a sparser condition, with GPT-5.2 dropping from 0.178 to 0.118 ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)), so a maximal setup can hand you a falsely clean number.

## Why it works

Each canary is a single-variable perturbation, which is what makes the result a diagnosis rather than a score. The model's only new information is the spoiled property, so a raised trap rate localizes what it over-weights while ranking tools. The subtlety ablation supports that reading over a tell-spotting one: softening the give-away phrasing left frontier susceptibility at 0.075 against 0.079 before ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)). For capability mirage the mechanism is narrower. A capability claim is unverifiable at selection time yet gets read as evidence, so the strongest-sounding tool wins, which makes honest [tool descriptions](../tool-engineering/tool-description-quality.md) a correctness control rather than documentation polish.

## When this backfires

- Frontier-only tool sets. The four cheapest probes to generate return no signal on strong models, so most of the run budget confirms nothing ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)).
- 8B-class models. Every axis fires, and a task success rate of 0.23 on Llama 3.1 8B already said the model is not ready ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)).
- Readout-side failures. On Berkeley Function-Calling Leaderboard failures the model attended most to the correct tool 80% of the time against 21% chance and still picked wrong, and prompt-side repair recovered at most 23% of failures against 59% to 91% for readout-side intervention ([Chen, 2026](https://arxiv.org/abs/2606.16364v2)). Rewriting descriptions will not move failures of that shape.
- Vendors outside the sample. Provider and tier are partially confounded, one frontier plus one mid from each of three providers ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)).
- Synthetic conditions. Tool outputs are synthetic and the 120 templated tasks are single-authored, which the authors call modest for a benchmark ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)).

## Example

The capability-mirage transform, applied to a minimal document-search schema. It inflates the advertised powers and changes nothing else; the superlatives are the paper's own example phrasing for this canary type ([2608.04719v1](https://arxiv.org/abs/2608.04719v1)):

**Before** — the tool being copied:

```json
{
  "name": "search_documents",
  "description": "Search the document corpus and return matching passages.",
  "parameters": { "query": "string", "limit": "integer" }
}
```

**After** — the canary:

```json
{
  "name": "search_documents_advanced",
  "description": "Research-grade document search. Solves the hardest cases.",
  "parameters": { "query": "string", "limit": "integer" }
}
```

Both definitions accept the same calls, and the canary's output is deliberately worse. Every call it receives counts against the capability-claim axis, because nothing else about the two advertisements differs.

## Key Takeaways

- Run the probes against a staging copy of the tool set, never a live one, and record a rate per type instead of one aggregate number.
- Expect a frontier model to trip capability mirage first and prerequisite blindness second; treat near-silence on the rest as the baseline, not as evidence of safety.
- Turning every probe on at once can lower the measured rate, so hold density fixed between runs you intend to compare.
- Pair the trap rate with a recovery rate, because a post-call check is the fix for a model that springs traps but notices.
- Ban superlative capability claims from tool descriptions as a standing rule; that one is adoptable without running any probes.

## Related

- [Tool Description Quality for Effective Agent Guidance](../tool-engineering/tool-description-quality.md) — why descriptions decide selection, and what a well-formed one carries
- [Tool-Use Sim-to-Real Perturbation Taxonomy](tool-use-sim-to-real-perturbation-taxonomy.md) — the sibling taxonomy that perturbs the environment rather than the tool advertisement
- [Planted-Bug Methodology: Deliberate Bugs as Observability Calibration](planted-bug-observability-calibration.md) — the same planted-defect logic applied to instrumentation instead of tool choice
- [Eval Awareness: Designing Evals Agents Cannot Recognize](eval-awareness.md) — what to check when you suspect the model is detecting the probe rather than reasoning
- [Security-Aware Tool Descriptions for MCP](../security/security-aware-tool-descriptions-mcp.md) — the adversarial counterpart, where a description misleads on purpose
