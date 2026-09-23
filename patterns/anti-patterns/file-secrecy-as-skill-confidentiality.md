---
title: "Treating File Secrecy as Skill Confidentiality"
term: "File Secrecy as Functional Secrecy"
description: "A disclosure-shaped output filter blocked 3 of 4 explicit disclosure probes and 0 of 252 ordinary task responses. Hiding a skill's files hides its text, not the function the text implements."
aliases:
  - behavioral skill reconstruction
  - skill leakage
  - functional secrecy of agent skills
tags:
  - anti-pattern
  - security
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-22
maturity: emerging
---

# Treating File Secrecy as Skill Confidentiality

> Hiding a skill's files hides its text. The function stays observable in the answers the skill gives, where disclosure filters barely reach.

This matters where three things hold at once. An outside party sends the skill task requests. The skill body carries logic the base model cannot reproduce from the public description. That logic is compact and deterministic: thresholds, table entries, composition rules, short procedures. Drop any one and file secrecy comes closer to sufficient. Internal skills, and skills whose value is a judgement no exact-match oracle scores, sit outside every result below.

## What the two standard defenses cover

Both defenses were built against disclosure, meaning an attacker who asks the agent to print its `SKILL.md`. Measured against ordinary task requests instead, they read the wrong signal. An input intent classifier and an output lexical-overlap filter caught all 4 explicit disclosure probes in one evaluation. Over 252 task-valid probes from a reconstruction run against the same victim, the input detector flagged 17 (6.7%) and the output filter blocked none, because those responses carry little lexical overlap with the skill body ([Hua et al. 2026 §6](https://arxiv.org/abs/2608.04192v2)).

Vaguer public descriptions are the other reflex, and they do not pay. Rewriting all 21 mined skill descriptions to a task-only or vague form produced a median change in attack success rate of 0 pp, protecting 3 skills by at least 20 points and harming 4 by the same margin, while routing recall fell from 99.5% to 96.2% ([Hua et al. 2026 §6](https://arxiv.org/abs/2608.04192v2)). You pay in routing and get a coin flip.

## What leaks, by what the body encodes

Median attack success rate across a 30-skill suite, grouped by the skill's dominant hidden component, with the fraction of skills recovered above their majority-class floor ([Hua et al. 2026 §5.1](https://arxiv.org/abs/2608.04192v2)):

| Hidden component | Median ASR | Above floor |
|---|---|---|
| Rule composition | 87% | 3/3 |
| Threshold and decision rules | 83% | 4/5 |
| Lookup tables and data | 82% | 7/10 |
| Procedures and algorithms | 77% | 4/6 |
| Numeric formulas | 43% | 3/6 |

The recovered clones are substitutes rather than copies, scoring 74–100% ASR at 35–59% token precision against the skill body ([Hua et al. 2026 §5.1](https://arxiv.org/abs/2608.04192v2)). A working replacement sharing little text with the original is also one a text-overlap filter never sees.

## Why it works

A skill offered as a service has to answer ordinary requests, and every answer is a labeled input-output pair for the function the hidden body implements. The usable interface and the leak channel are one interface. Tramèr et al. named the same tension for prediction APIs a decade ago: "The tension between model confidentiality and public access motivates our investigation of model extraction attacks" ([Tramèr et al. 2016](https://arxiv.org/abs/1609.02943v2)). Skills add a second channel nobody can close, since the public advertisement exists so the agent can route tasks to the skill, and that same text narrows the space of plausible implementations ([Hua et al. 2026 §3.2](https://arxiv.org/abs/2608.04192v2)).

A second group reached the same conclusion through a different observation channel. SigLeak contrasts skill-enabled and skill-disabled execution trajectories, and its authors report that "benign execution trajectories can expose proprietary procedural knowledge" ([Geng et al. 2026](https://arxiv.org/abs/2607.25560v2)).

## When this backfires

- Recovery is bounded, and the bounds are real. A 230-entry private codebook stayed at 0% ASR under a 24-probe budget, which the authors attribute to coverage rather than to any defense ([Hua et al. 2026 §5.1](https://arxiv.org/abs/2608.04192v2)). If your asset is a large dataset and your interface meters queries, the economics may already favor you.
- Disclosure defenses are scoped, not wasted. Pipeline defenses at input, inference, and output "substantially reduce leakage" against the disclosure attack they were built for, though the same authors add that "the attack remains inexpensive and repeatable, and a single successful attempt is sufficient to compromise the protected skill" ([Wang et al. 2026](https://arxiv.org/abs/2604.21829v2)).
- There is nothing validated to buy instead. The source states that "no customized defense is available for now" and lists cross-session identity controls, cumulative query monitoring, output coarsening, and private routing representations as untested directions ([Hua et al. 2026, Limitations](https://arxiv.org/abs/2608.04192v2)). Read any vendor claim in this space as unmeasured.
- The evidence does not come from commercial deployments. Every evaluated skill body was a public artifact, and "proprietary services, paid marketplaces, and in-the-wild evaluations remain outside the study" ([Hua et al. 2026, Limitations](https://arxiv.org/abs/2608.04192v2)). The exposure is real; its size in your product is not measured.

## Example

The fix is a placement decision, and it splits on why the logic is secret.

The source uses a traffic classifier for the same illustration: the advertisement exposes the task and its input fields, while "the hidden body specifies the exact detection thresholds and the logic that combines them" ([Hua et al. 2026 §3.2](https://arxiv.org/abs/2608.04192v2)).

**Before** — the skill ships its detection cutoffs in the body, and the product story is that customers cannot see them:

```markdown
<!-- SKILL.md, hidden from the customer; thresholds illustrative -->
Flag a session as suspicious when entropy > 7.4 AND packet-rate > 220/s.
Escalate at entropy > 7.9 regardless of rate.
```

Every classification a customer requests is a labeled point on that boundary. Threshold and decision rules are the second most recovered component class in the suite, at an 83% median ([Hua et al. 2026 §5.1](https://arxiv.org/abs/2608.04192v2)).

**After** — sort the logic by what its secrecy is doing.

- Commercially valuable and compact. Accept that a customer can rebuild it, and compete on what a clone does not inherit: data freshness, support, and the update that lands next month. Do not price the skill as a moat.
- Security-critical. Re-derive the control so it holds once the cutoff is known, the same rule [OWASP applies to system prompts](../../security/system-prompt-not-a-secret-store.md). A threshold that works only while nobody knows it was never a control.
- Genuinely large and private. Keep it behind an interface that authenticates the caller and accounts for queries across sessions rather than per request. This is the direction the source recommends and has not evaluated, so treat it as a hypothesis you monitor.

If you are buying rather than authoring, the same table is a purchasing note. A vendor's proprietary logic is worth roughly what its component class says it is worth, and for compact rule and threshold skills that is not much.

## Key Takeaways

- File secrecy and functional secrecy are separate properties. The same two filters caught 4 of 4 explicit disclosure probes and 17 of 252 ordinary task probes ([Hua et al. 2026 §6](https://arxiv.org/abs/2608.04192v2)).
- Sort your skill bodies by what they encode before deciding what to protect. Rule composition, thresholds, and lookup tables sat at 82–87% median ASR, numeric formulas at 43% ([Hua et al. 2026 §5.1](https://arxiv.org/abs/2608.04192v2)), so the compact rule is the exposed one.
- Vaguer descriptions are not a control. Median ASR change of 0 pp, 3 skills protected against 4 harmed, routing recall down 3.3 points ([Hua et al. 2026 §6](https://arxiv.org/abs/2608.04192v2)).
- Any skill logic whose secrecy is load-bearing for security belongs somewhere that does not answer arbitrary task requests, and the control it backs should survive disclosure anyway.
- No defense for this channel has been validated. Query accounting across sessions is the direction the source names as future work, so measure it yourself before relying on it.

## Related

- [System Prompt as Secret Store (OWASP LLM07)](../../security/system-prompt-not-a-secret-store.md) — the same boundary error one layer down, where the hidden text does leak; this page covers the case where it never leaks and the function is rebuilt anyway
- [Adversarial-Only Threat Modeling for Agent Data Leakage](adversarial-only-leakage-threat-modelling.md) — benign requests leaking the user's data, the mirror image of benign requests leaking the provider's logic
- [Credential Hygiene for Agent Skill Authorship](../../security/credential-hygiene-agent-skills.md) — the authoring-time decision about what belongs in a skill body at all
- [Embedding Inversion: Vector Stores as a Source-Text Disclosure Surface](../../security/embedding-inversion-vector-store-disclosure.md) — another artifact whose confidentiality claim does not survive what the system must expose to be useful
- [Judging a Skill's Honesty by the Validity of Its Output](judging-skill-honesty-by-output-validity.md) — the consuming team's side, for what observing a third-party skill's answers can and cannot establish
