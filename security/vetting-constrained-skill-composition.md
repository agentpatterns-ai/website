---
title: "Vetting-Constrained Skill Composition"
term: "Vetting-Constrained Composition"
description: "A standalone vetting engine is a filter an attacker can search under. Refining two marketplace skills toward one harmful joint outcome raised the average harm rate from 27.9% to 73.8% while average pass rates stayed above 92%."
tags:
  - security
  - agent-design
  - tool-agnostic
  - anti-pattern
  - skills
  - arxiv
aliases:
  - adaptive composition attack
  - standalone vetting constraint
  - vetting-pass composition evidence
last_reviewed: 2026-10-06
maturity: emerging
---

# Vetting-Constrained Skill Composition

> Tuning a skill composition so each skill still passes standalone vetting turns the vetting engine into a constraint the attacker searches under.

[Zhou et al. (2026)](https://arxiv.org/abs/2610.05943v1) measured this on 560 skill pairs drawn from 4,000 public skills collected from SkillHub and ClawHub, across eight cybersecurity behaviors. The setup was an OpenClaw agent, 70 pairs per behavior, the facilitated prompt condition. On DeepSeek-V4-Flash the average trial-level harm rate ran 27.9% for the unmodified composition and 73.8% once both skills were refined (Table 1). The method discards any candidate composition "containing a skill that fails standalone vetting" (§5.3), with SkillSafe as the constraint engine.

## What a per-skill pass certifies

A skill's capability space is the set of ordered arrangements over its capabilities ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1), Definition 1). Composing two skills therefore yields arrangements that interleave both and appear in neither skill's own space (Theorem 2). Theorem 3 places the unsafe arrangements in that difference set alone, where they "cannot be directly observed under standalone vetting".

The green check is an accurate statement about one artifact's own capability space. Read as a statement about the set you installed, it reports on a space it never examined.

## Why it works

The containment result explains why the pass is silent. What makes it exploitable is that a vetting verdict is cheap and repeatable, so it can be searched under. The paper's steering module generates five candidate pairs per round and discards any candidate composition "containing a skill that fails standalone vetting" (§5.3) ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1)). It keeps the candidate whose execution trace moved furthest toward the target. What it edits is coordination rather than capability: "small, targeted adjustments to how existing benign capabilities exchange information, follow execution order, or maintain state during joint execution". That cost a mean of 42.1 added instruction tokens over 2.6 rounds (Table S1).

Pass rates stay high but not at 100%. The authors report that "most optimized skills are still regarded as benign when examined independently". Averaged across the eight behaviors, the retained skills still pass at 93.8% on SkillSafe, 97.1% on the Cisco Skill Scanner and 92.1% on Tencent CSC SkillScan ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1), Table 2). The originals passed at 98.2%, 98.0% and 98.2%. The authors read the same table as evidence that "individual skill inspection alone does not reliably reflect the security risk produced when the same skills are executed together".

Capability coverage is the precondition and not the cause. Random pairing from the same corpus averaged 3.1% direct-composition success, against 17.0% for capability-directed selection ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1), Table 3). Both figures come from the strict benign prompt condition. Refinement "cannot create capabilities that are absent from the selected pair".

## What a harness owner does about it

- Move the verdict to the installed set, and read it from side effects. The paper's sandbox scores a run by whether it produced the target environmental consequence, "rather than by the agent's textual response alone" ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1)). Tool actions, state changes, and what left the sandbox are the evidence; the transcript is not.
- Re-run that verdict per backbone model. The same pairs under the same condition averaged 27.9% on DeepSeek-V4-Flash and 9.7% on GPT-4o-mini for direct composition ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1), Table 1), so a composition verdict expires on a model swap.
- Keep the permission envelope, because neither attack touches it. "Neither DCA nor ACA expands the permission scope of the underlying model" ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1)). Deny-by-default egress and capability isolation bite without anyone predicting which pair arrives.
- Treat a capability union as triage. [Wang et al. (2026)](https://arxiv.org/abs/2606.00448v1) flagged 22.25% of 211,575 individually-safe pairs on union alone, then audited a 200-unit stratified sample: "roughly one in five flagged pair-pattern hits is a real compositional risk" (18.2%, 95% CI 11.3% to 27.4%). That rate is at the (pair, pattern) annotation level. The authors give a separate pair-level point estimate of 4.05% under a co-validation assumption, so the union rate is a shortlist and not a count of risky pairs.

## When this backfires

- Registry-scale enumeration. 651 individually-safe skills form 211,575 pairs ([Wang et al., 2026](https://arxiv.org/abs/2606.00448v1)). Sandboxed co-execution fits an installed set and never a pair space, which is why that paper argues for "install-time compositional checks and capability isolation as complements to per-skill scanning".
- Single-author internal libraries. The threat model assumes an adversary with the same access to the repository and agent interface as an ordinary user ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1)). Where one team authors and reviews every skill, nobody operates the refinement loop, and the per-skill pass is weak evidence rather than a defeated control.
- Explicitly malicious requests. Holding one request fixed and varying only the installed skills, over six cross-vendor models at three runs each, [Wang et al. (2026)](https://arxiv.org/abs/2606.00448v1) found response-level compliance highest with no skills installed (17/18) and no higher for the risky pair (11/18) than for an unrelated pair (12/18). Their own reading is that "a composition fixes which capabilities are reachable, while the host model decides whether to use them". Where the request already names the action, refusal behavior is the control that applies.
- An unreconciled constraint in the primary source. SkillSafe is the stated RRS constraint, yet its post-refinement pass rate averages 93.8%, with cells down to 90.0%. The paper does not reconcile this, so treat the pass rates as measured and the reading that every retained skill passed as unconfirmed.
- A dangling cross-reference in the primary source. The Table 1 caption cites a Table 4 and a Table 4c absent from the v1 HTML, so treat its figures as scoped to the facilitated prompt and nothing wider.

## Example

The paper's own verdict procedure is the thing worth copying. Its Skill Reaction Chamber executes a candidate skill pair with a fixed agent inside an isolated sandbox, then records the trace: "tool actions, state changes, and externally observable consequences" ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1)). The run is scored on whether the target environmental consequence appeared. The agent's own account of what it did never enters the decision.

Translated to a harness, that is a different review object from the one a marketplace badge covers. The badge is issued per artifact, before install, by an engine that reads files. The run-level check is issued per installed set, after install, by diffing what left the sandbox against what the task needed. The run-level check costs one run per pair you actually installed, and a quadratic pair space for a registry. That is why the installed set is where it stays affordable.

## Key Takeaways

- A standalone vetting pass reports on one artifact's capability space. The unsafe cross-skill arrangements sit in the difference between the composed space and the individual ones, where "cannot be directly observed under standalone vetting" is a theorem rather than an observed limitation ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1)).
- The paper's method uses the engine as a constraint inside the attacker's search. Refining both skills raised the average trial-level harm rate from 27.9% to 73.8% under the facilitated prompt, and average pass rates after refinement stayed at 92.1% to 97.1% across three commercial engines ([Zhou et al., 2026](https://arxiv.org/abs/2610.05943v1)).
- A diff-size review will not catch it. The refinement averaged 42.1 added instruction tokens and granted no new permissions, so the artifact looks the same size and the same shape afterwards.
- Capability coverage selects candidates without deciding the outcome, so an inventory of what two skills can do is a shortlist and not a verdict.
- The pair is not the whole cause. Under one fixed explicit request, [Wang et al. (2026)](https://arxiv.org/abs/2606.00448v1) measured response-level compliance of 17/18 with no skills installed, 11/18 with the risky pair and 12/18 with an unrelated pair, over six models at three runs each.
- In [Zhou et al. (2026)](https://arxiv.org/abs/2610.05943v1) Table 1, the average trial-level harm rate for direct composition under the facilitated prompt was 27.9% on DeepSeek-V4-Flash and 9.7% on GPT-4o-mini, so re-run an effect-based verdict on a model swap.
- The affordable defense covers the installed set. A capability union is a triage filter whose flags audit out at 18.2% validity per (pair, pattern) hit, and the permission envelope is the control that does not require predicting which pair arrives.

## Related

- [Skill Composition Risk in Agent Ecosystems](skill-composition-risk.md) — the runtime half of the same gap, with three named modes for how composed context fuses
- [The Skill Closure Declaration Gap](skill-closure-declaration-gap.md) — the same mismatch one level down, between a skill root and what one run of it reaches
- [Single-Decision Approval of Vendor Skill Suites](single-decision-suite-approval.md) — what happens when the review unit itself is handed to the skill author
- [Monotonic Capability Attenuation for Composition-Safe Tool Use](monotonic-capability-attenuation.md) — the runtime control for capability budgets that intersect through composition
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — the permission-envelope frame this page leans on
