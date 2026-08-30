---
title: "Trajectory Poisoning of Promoted Agent Skills (PoisonedEvolution)"
term: "Trajectory Poisoning of Promoted Agent Skills"
description: "Self-evolving skill systems open a trust boundary at the promotion step; gate on the provenance of the supporting evidence, which requires a contributor identity substrate to measure."
aliases:
  - self-evolving skill poisoning
  - evidence promotion trust boundary
  - provenance-aware evidence gate
  - trajectory poisoning attack
tags:
  - security
  - skills
  - memory
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-29
maturity: emerging
status: current
---

# Trajectory Poisoning of Promoted Agent Skills (PoisonedEvolution)

> Poisoning a self-evolving skill system means poisoning its evidence: three consistent attacker records in thirty promoted a hostile behavior in 25 of 25 trials.

Any system that distills agent trajectories into persistent skills opens a trust boundary at the promotion step. PoisonedEvolution attacks that step: the attacker never edits the skill bank, but contributes trajectory records shaped so the evolver judges the behavior they carry worth keeping, and the evolver writes the skill itself ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)). Inspecting the finished skill checks the wrong artifact, because a good-faith evolver produced it from evidence that satisfied its own criteria.

## When this applies

The threat model needs three conditions, and a system missing any one is not exposed:

- Trajectories become persistent instructions. A skill bank, an evolved `SKILL.md`, or a rules file read as guidance rather than as history.
- Promotion is automatic. A human reviewing each promoted diff is the boundary; the attack targets pipelines where an evolver decides alone.
- An outsider can contribute records blind. The attacker reads installed skills and supplies a bounded fraction of trajectories, but cannot inspect the private pool, the filter, or the evolver prompt ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)).

Under those conditions the attack embedded target behaviors in 546 of 600 trials (91.0%) on the SkillClaw pipeline at 10% attacker support. Exposure varied by evolver, from 100 of 100 trials on DeepSeek-V3.2 to 70 of 100 on GPT-5.4 ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)).

## The three gates a poisoned behavior must clear

Poisoning succeeds only when all three hold ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)):

| Condition | What must happen | Who controls it |
|---|---|---|
| Inclusion | Poisoned records pass the ingestion filter into the evolver's stream | Defender's filter |
| Evolution attribution | The evolver credits the behavior as a reusable pattern rather than noise | Surface features of the evidence |
| Realization | The behavior survives summarization and merge into the emitted skill diff | Evolver's synthesis |

Attribution is the bottleneck, and it is the one an attacker steers directly.

## Why it works

Promotion is a judgment made from surface features of the evidence, and each feature is attacker-writable ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)):

- Recurrence. At a pool of 30 records, one attacker record promoted in 5 of 25 trials, two in 21 of 25, three in 25 of 25. One record reads as an accident. Three consistent ones read as accumulated practice.
- Causal framing. The record shows the behavior clearing an obstacle, or shows its absence causing a failure. Binding it to a task outcome that way moved promotion from 8 of 25 to 25 of 25.
- Domain-aligned encoding. Wording the behavior as a legitimate workflow step reached 25 of 25, against 0 of 25 through an auxiliary channel.

Neither dilution nor utility monitoring closes the gap. Three attacker records still promoted in 22 of 25 trials at a pool of 100, which is 3% support, and the poisoned skill scored 20.0% hard accuracy against 18.0% for no skill on the same split, so it read as an improvement ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)).

Contributor diversity is the one property a single-origin attacker cannot manufacture. A pilot gate requiring multi-user or multi-cluster support before promotion, rejecting majority dominance and penalizing high text overlap, took a single-cluster attack from 25 of 25 embedded to 0 of 25 while still admitting a genuine five-session diverse control ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)).

## When this backfires

The gate is preliminary, and its preconditions are stronger than they look:

- Single-contributor pools have nothing to measure. The gate admits evidence only on multi-user or multi-cluster support ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)). In a solo developer's harness, or a loop that folds its own transcripts back into a rules file, every record shares one origin, so the gate stops self-evolution instead of filtering it.
- Coordinated accounts mimic diversity. The authors state that authentic provenance is not trustworthy provenance; several accounts or deliberately varied sessions produce the signal the gate looks for ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)).
- Grouping is assumed rather than detected. The pilot receives evidence already grouped into candidates. Coarse grouping blocks legitimate multi-contributor support; fine grouping splits one attacker's sessions into apparently distinct clusters ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)).
- Some pipelines already suppress the attack. Trace2Skill's outcome-split analysts and hierarchical consolidation held success to 369 of 600 (61.5%) with no provenance gate, and safety-weakening payloads to 28 of 150 (18.7%) ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)). A gate bolted onto that architecture buys less for the same cost.
- The evidence is one cycle deep. Experiments stop after a single evolution cycle and measure artifact-level embedding rather than runtime compromise, so feedback from an already-poisoned skill into the next cycle is unmeasured ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)). EvoMal measures that propagation step with a planted skill instead of a synthesized one. A retrieved malicious skill becomes the template an agent imitates while writing a new one. The payload survives into the skill the agent then stores and runs ([EvoMal, arXiv 2026](https://arxiv.org/abs/2608.25776)). The paper credits that imitation to banners, benign-looking structural elements in the retrieved skill. The attacker plants skills in the library and never invokes them.
- Counting agreement is a fragile signal in this family. [Forged reasoning trace attacks](forged-reasoning-trace-memory-attack.md) defeat a consensus-anomaly detector by flooding a store with mutually-citing entries until the poison is the majority. A gate keyed on how much evidence agrees inherits that weakness; the diversity gate survives because it keys on distinct origins.

Artifact-level checking retains value as a second layer. [Semantic intent validation](semantic-intent-validation-skills.md) catches a promoted skill whose stated purpose contradicts its observable steps, and it needs no identity infrastructure, which matters wherever the provenance signal is unavailable.

## Example

The evaluation's supply-chain canary replaces the package registry with a loopback address. It reaches the skill by riding the attribution shape, not by looking malicious. Records come in two routings. A success-routed record shows an obstacle, then the behavior clearing it, then the task completing. A failure-routed record shows the behavior absent, the task failing, and the behavior named as the repair. In both, the behavior sits at a plausible workflow locus: an input prerequisite, a recovery step, or an output validation ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)). Stated abstractly, that is the shape a defender looks for:

```
Success-routed record, repeated across sessions
  obstacle   a step of the genuine task fails
  behavior   the canary action, at a plausible workflow locus
  outcome    the task completes

Failure-routed record
  omission   the canary action is absent
  outcome    the task fails
  repair     the canary action is named as the fix
```

The skill the evolver writes from those records reads as ordinary engineering advice, and nothing in its text marks it as poisoned. So the check belongs upstream of synthesis, applying the pilot's three criteria to the evidence instead:

```yaml
# Evidence gate applied before skill synthesis
promotion_gate:
  min_distinct_contributors: 3      # distinct sessions or accounts, not records
  max_single_contributor_share: 0.5 # reject majority dominance
  max_pairwise_text_overlap: 0.8    # penalize near-identical inputs
  on_fail: quarantine_for_review    # never a silent drop
```

Three near-identical records from one origin fail the first and third rules. The same behavior observed by three unrelated sessions passes, which is the separation the pilot's five-session diverse control demonstrated ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)).

## Key Takeaways

- The checkpoint that matters in a self-evolving skill system is evidence promotion. The emitted skill text carries no marker of poisoning because a good-faith evolver wrote it.
- Attribution is the attacker's target, and its three drivers are recurrence, causal framing, and domain-aligned wording. All three live in records the attacker authors ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)).
- Volume is not the lever. Three consistent records in thirty reached 25 of 25 promotion, and 3% support still reached 22 of 25 ([Chen et al., 2026](https://arxiv.org/abs/2608.05563v1)).
- A gate keyed on distinct contributors, rather than on agreement counts, is the transferable defense. Deploy it where sessions or accounts are separable, and run artifact checking alongside it.
- Treat your own harness as an instance of this pipeline. A routine that distills session transcripts into a rules file is a one-contributor promotion path, which is the configuration the gate cannot protect.

## Related

- [Skill Misevolution in Self-Updating Skill Libraries](skill-misevolution-lifecycle-gates.md) — what happens downstream of promotion: the same artifact followed through retrieval into a fresh session, with the one-cycle limit above lifted
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — the registry-side sibling, where malicious text arrives inside the skill instead of being synthesized from poisoned evidence
- [Forged Reasoning Trace Attacks on Agent Memory (FARMA)](forged-reasoning-trace-memory-attack.md) — poisoned traces read back at retrieval time, plus the amplification technique that inverts consensus defenses
- [Semantic Intent Validation for Agent Skills](semantic-intent-validation-skills.md) — the artifact-level layer this page treats as insufficient alone, and still worth running
- [Experience Graphs as Structured Memory for Self-Evolving Agents](../patterns/agent-design/experience-graphs-self-evolving-agents.md) — the benign version of the same pipeline, including its trusted-writer precondition
- [Gate Agent Writes to Executable Config](gate-agent-writes-to-executable-config.md) — the control for the in-repo case, where an agent promotes its own output into files that later steer it
