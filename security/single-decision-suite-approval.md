---
title: "Single-Decision Approval of Vendor Skill Suites"
term: "Single-Decision Suite Approval"
description: "Approving a vendor's skill suite in one decision lets an attacker split a malicious objective across the bundle; cascades reach 89.4% attack success and concatenated joint review recovers 5.2 points at best."
tags:
  - security
  - anti-pattern
  - tool-agnostic
  - skills
  - supply-chain
  - arxiv
aliases:
  - vendor skill suite approval
  - skill cascading attack
  - one-decision skill bundle install
last_reviewed: 2026-09-29
maturity: emerging
---

# Single-Decision Approval of Vendor Skill Suites

> Approving a vendor's skill suite in one decision delegates the review unit to that vendor, and per-skill scanning afterwards cannot recover it.

A skill cascading attack distributes one malicious objective across two or more skills ([Zhu et al., 2026](https://arxiv.org/abs/2609.30383v1)). Each modified skill clears review alone, the combined execution produces harm, and reverting any one modification eliminates it. Zhu et al. model it on software supply-chain attacks such as the SolarWinds incident, "in which a malicious objective is distributed across independently trusted components". The delivery channel is ordinary adoption. Users "routinely install domain-specific suites from a single developer through one approval decision", so an attacker "can therefore engineer co-installation by packaging the malicious skills as a coherent suite under one vendor brand". Across 24 agent-and-backbone configurations, the cascades reached a global average attack success rate of 89.4%.

## When this applies

Three conditions have to hold together. Where one is absent, the controls below cost more than they return.

- The skills come from outside your repository, under a shared brand or publisher. The threat model assumes an attacker who operates as a skill developer and controls two or more installed skills.
- The harness passes all inter-skill information through one shared context window. That channel is what lets an edit in one skill reach the next.
- The suite is approved as a unit, rather than each skill reviewed against the set already installed.

## How each edit stays defensible

Three skills process an earnings-call transcript in which the issuer disclosed a going-concern audit opinion, an 11-week cash runway, and an active debt restructuring ([Zhu et al., 2026](https://arxiv.org/abs/2609.30383v1)):

| Skill | Modification | Stated rationale |
|---|---|---|
| Transcript extractor | Routes risk-keyword paragraphs into a regulatory-disclosures field, away from operating metrics | Separating regulatory disclosures from operating data is a standard compliance-grade data-engineering pattern |
| Sentiment scorer | Down-weights that field and drops it from the negative-signal set | Already-priced regulatory background is widely treated as non-incremental signal |
| Memo drafter | Excludes low-weight content from every memo section | An executive memo is a noise-controlled summary of evaluator-validated incremental signals |

The memo emerges with a Buy/Hold signal anchored to revenue growth and no mention of the liquidity crisis. Each rationale is one a careful engineer could write.

## Why it works

Every skill writes into the same window, and the same model reads that output back as authoritative input when the next skill runs. A skill's output "can therefore steer both the behavior of downstream skills and the selection of which skills are invoked next" ([Zhu et al., 2026](https://arxiv.org/abs/2609.30383v1)). Detection fails for a separate reason, and Zhu et al. state it plainly: "Independent scanning thus fails because its unit of analysis is a single skill, while the attack's unit of harm is the entire cascade, a mismatch no per-skill detector can close." Because each edit is small and locally justified, the modified skills sit on the benign baseline. Five per-skill scanners held stealth rates above 86% on the modified set, with the marginal detection signal never exceeding 4.7 points.

## What joint review buys

Reading the bundle in one pass is the obvious fix, and on its own it is close to worthless. Concatenating a cascade's skills into one scanner query moved the joint stealth rate by 5.2 points for an LLM scanner. A static pipeline moved it by zero ([Zhu et al., 2026](https://arxiv.org/abs/2609.30383v1)). Runtime monitoring fared no better. Four runtime defenses averaged an 88.5% evasion rate, and trajectory-level inspection, the only paradigm that reasons across steps, was still evaded at 82.5%.

What works is reconstructing the graph rather than re-reading the text. ChainGuard analyzes a candidate skill against the skills already installed, rebuilding cross-skill dependencies, artifact flows, capability compositions, and downstream behaviors. It cut attack success from 96.0% to 22.5% while passing 99.5% of benign workflows ([Zeng et al., 2026](https://arxiv.org/abs/2608.09732v1)). That review needs the installed set, so the decision belongs to the deployer rather than the marketplace.

Indispensability gives incident response a lever. Withdrawing a single modification dropped residual attack success to 13-18%, and removing a second took it to single digits ([Zhu et al., 2026](https://arxiv.org/abs/2609.30383v1)). A bisect over a suspect suite localizes the cascade. The same property is a trap during triage, because reverting one skill looks like a complete fix while the rest stays installed.

## When this backfires

- First-party skill libraries. When every skill is authored in your repository and reviewed as code, the co-installation precondition does not hold.
- Harnesses that run each skill in fresh context. Breaking the shared window breaks the mechanism, at the price of losing legitimate composition.
- A concatenated joint review adopted as the remedy. It buys 5.2 points at best and leaves a team believing the gap is closed.
- Controls tuned to long chains. SkillCascade-Bench averages 3.25 skills per case, and CompoSkill reports that attack success decreases once additional hops push a risk chain past three skills ([CompoSkill, 2026](https://arxiv.org/abs/2608.16246v1)).
- An outright ban on multi-skill suites. Single-vendor bundles are also how legitimate adoption works, so the control has to be graded.
- Sizing the response off 89.4%. Zhu et al. describe their sandbox results as "a stress test rather than a forecast of in-the-wild incidence", and say the real incidence of attacker-controlled co-installation "remains an open question".

## Key Takeaways

- Approve each skill in a suite separately, against the set already installed. A bundle accepted in one decision has been reviewed by its vendor rather than by you.
- Read a per-skill scanner pass as silence, not coverage. The verdicts are correct and beside the point, because the harmful property belongs to the cascade.
- If you add cross-skill review, require it to reconstruct dependency and artifact flows. Text concatenation is the version that does not work ([Zhu et al., 2026](https://arxiv.org/abs/2609.30383v1)).
- Budget no detection to runtime monitoring here. Even the one paradigm that reasons across steps missed four cases in five.
- In incident response, revert the whole suite rather than the skill you found. One revert collapses most of the harm, which makes a partial revert read as a fix.

## Related

- [Skill Composition Risk in Agent Ecosystems](skill-composition-risk.md) — the adjacent case where no skill is modified and harm emerges from composing benign skills
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — the single-skill vector, where one artifact carries the payload
- [The Skill Closure Declaration Gap](skill-closure-declaration-gap.md) — what a skill root declares versus what one run of it can reach
- [Compositional Vulnerability Induction in Coding Agents](compositional-vulnerability-induction.md) — the same decomposition idea applied to engineering tickets rather than skills
- [Enterprise-Managed Plugin Governance](enterprise-managed-plugin-governance.md) — the administrative surface where suite approval is granted or withheld
- [Vetting-Constrained Skill Composition](vetting-constrained-skill-composition.md) — the attacker-side version, where each skill is tuned to keep passing the scanner that reviews it
