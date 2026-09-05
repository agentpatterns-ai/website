---
title: "Judging a Skill's Honesty by the Validity of Its Output"
term: "Output-Validity Trust"
description: "A steered skill holds its declared task and a 100% valid-output rate while moving which candidate wins, so compare selection rates with and without it."
aliases:
  - output-validity trust
  - covert policy steering
  - skill policy integrity
tags:
  - anti-pattern
  - security
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-04
maturity: emerging
---

# Judging a Skill's Honesty by the Validity of Its Output

> A skill can keep its declared task and a 100% valid-output rate while moving which candidate the agent picks, so no single run looks wrong.

Output-validity trust is accepting that a third-party skill pursues the objective it declares, because its runs finish, its output matches the interface, and the task still completes. A skill rewritten to favor someone else's candidate produces exactly that evidence. SkillShift, a black-box framework that edits a skill's policy text without inserting any target command, moved product recommendation from 37.33% to 81.33% attacker-favored selection and Python dependency selection from 0.67% to 63.33%, both "while maintaining 100.00% VR," the paper's valid-output rate ([Li et al., 2026](https://arxiv.org/abs/2609.02564v1)).

Scanning the artifact does not recover the signal. "None of the six quantitative detectors distinguishes the SkillShift Attack Skills from their paired clean Skills," and yet "four detectors flag Direct-Skill Injection in each domain (66.7%)" — the overt control in the same experiment ([Li et al., 2026](https://arxiv.org/abs/2609.02564v1)).

## Conditions this applies under

- The skill ranks candidates from an enumerated set. The measured domains were two fixed-candidate tasks: which product to recommend, and which Python package to depend on ([Li et al., 2026](https://arxiv.org/abs/2609.02564v1)). Where the agent writes code instead of choosing from a list, there is no selection rate to compare.
- The choice carries a cost you would not accept, such as a dependency the team then maintains for years. If the pick reverses in one command, the steering is cheap to undo and cheaper to ignore.
- You can state the preferences the skill is allowed to hold. Rates move for honest reasons too, so a delta means nothing without a declared baseline: the clean shopping arm already chose the target 37.33% of the time before any edit ([Li et al., 2026](https://arxiv.org/abs/2609.02564v1)).

## Why it works

The skill never changes what the agent may pick, only how it scores what it may pick. The paper models the agent as an implicit comparison over candidates and states that SkillShift "changes how existing evidence is weighted without modifying the evidence itself" ([Li et al., 2026](https://arxiv.org/abs/2609.02564v1)). The edits are ordinary skill material: framing that raises the salience of one attribute, a tie-breaker for near-equal candidates, worked examples that fix how those criteria get applied. Every candidate stays feasible and the output interface is untouched, so each run is defensible on its own terms and a per-run check has nothing to fail on.

The deviation lives in the distribution instead. No single pick falls outside the authorized set; the rate at which one candidate wins is what moves. Static scanning misses that for the reason a reviewer does: no override instruction, no payload, only selection criteria that read like the rest of the file. Swapping the model does not clear it, because the frozen policies "transfer without further optimization across heterogeneous LLM backends and agent environments" ([Li et al., 2026](https://arxiv.org/abs/2609.02564v1)).

## What to measure instead

Run one query set twice, with the skill loaded and without it, and compare how often each candidate wins. Then perturb the candidates and re-run: rename the favored option, reorder the list, exchange attributes between two candidates. The paper names those tests directly, arguing that "Defenses should incorporate behavioral auditing through Clean–Attack comparisons and counterfactual tests such as candidate reordering, name replacement, and attribute exchange" ([Li et al., 2026](https://arxiv.org/abs/2609.02564v1)). A preference that survives a rename is tracking an attribute. One that follows the name is tracking the name.

## When this backfires

- The delta is not separable from honest guidance. Any opinionated skill moves the same number by design. A study of brand competition in LLM recommendation puts the boundary plainly: "adversarial attacks can be detected and blocked by platforms, but the dilemma we study cannot be easily fixed because each brand's content is individually legitimate" ([Chu and Hou, 2026](https://arxiv.org/abs/2606.17443v2)).
- The clean arm is not a neutral arm. In that study, with product specifications held equal, the known brand "is recommended every single time," and authority-style marketing language was "worth +0.17 rating points" ([Chu and Hou, 2026](https://arxiv.org/abs/2606.17443v2)). The baseline you compare against already leans.
- A gate downstream of the choice is cheaper. Where an allowlist, a license check, or a reviewed lockfile diff already inspects the pick, the steering meets a control the team needs anyway.
- The evidence base is narrow: "Our evaluation is limited to two fixed-candidate domains, three runs per query, and detector case studies under specific configurations" ([Li et al., 2026](https://arxiv.org/abs/2609.02564v1)). Three runs per query is thin ground for a pass-or-fail verdict in your own pipeline.

## Example

**Before — every check the skill is given comes back clean.** A dependency-selection skill installs from a registry and returns a valid package name with a rationale on every run. Reviewers read the diff for the chosen package and find nothing unusual, because no single choice is unusual.

**After — the choice distribution is the artifact under test.** The team keeps a fixed set of dependency queries and runs them with and without the skill. A skill that moves one package from near-never to a majority of picks gets read line by line, whichever way the scan came back.

## Key Takeaways

- A valid output and a completed task do not say which objective the skill served: SkillShift held a 100.00% valid-output rate at 81.33% and 63.33% attacker-favored selection.
- Scanners miss it because nothing in the file is anomalous. The same detectors caught the explicit-injection control in four of six cases.
- The evidence you need is distributional. Compare selection rates with and without the skill, then re-run with the favored candidate renamed and the list reordered.
- The comparison yields a verdict only where you can state which preferences the skill may hold. Otherwise you get a delta that honest guidance produces too.
- Where an allowlist or a reviewed lockfile already gates the choice, put the control there and spend nothing on the audit.

## Related

- [Trusting a Skill Scanner's Verdict as a Security Judgment (Green-Check Fallacy)](skill-scanner-verdict-not-security-judgment.md) — the scanner case, where a pass compresses real findings into one bit; here the scan has no finding to compress.
- [Artifact-Only Verification Hides Skipped Skill Steps](artifact-only-verification.md) — the sibling gap in output checking: there the agent skips a mandated step, here it completes every step and picks differently.
- [Skill Over-Trust: Treating Topical Relevance as Evidence a Skill Helps](skill-over-trust.md) — the same withheld-skill comparison, run to attribute cost and failure rather than to test policy integrity.
- [Semantic Intent Validation for Agent Skills](../../security/semantic-intent-validation-skills.md) — checking documented intent against observable behavior, which a skill whose declared task really is preserved will pass.
- [Skill Supply-Chain Poisoning](../../security/skill-supply-chain-poisoning.md) — the registry-level threat model and the install-time controls that sit upstream of any behavioral audit.
