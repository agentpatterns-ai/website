---
title: "Trusting a Skill Scanner's Verdict as a Security Judgment (Green-Check Fallacy)"
term: "Green-Check Fallacy"
description: "A skill scanner's pass or fail is a signal, not a security decision — static scans over-flag useful skills and miss novel or image-encoded threats, so read the findings rather than obey the score."
aliases:
  - green checkmark fallacy
  - scanner verdict as security decision
  - skill scanner over-trust
tags:
  - anti-pattern
  - security
  - skills
  - tool-agnostic
last_reviewed: 2026-07-23
maturity: adopted
---

# Trusting a Skill Scanner's Verdict as a Security Judgment (Green-Check Fallacy)

> A skill scanner's green check means no pattern matched, not that the skill is safe: a signal to weight, not a verdict to obey.

Agent skills ship as installable artifacts — a `SKILL.md` plus scripts, hooks, and manifests — and static scanners now vet them before install. Treating the scanner's pass or fail as the security decision is the anti-pattern. A green check reports that no known-bad pattern matched; a red flag reports that one did. Neither answers whether the skill is safe to run in your context, and both fail in predictable directions.

Reaching for a scanner is reasonable, because the threat is real: Snyk's ToxicSkills audit of 3,984 published skills found 36.82% carried at least one security flaw and 76 were confirmed malicious payloads ([Snyk, 2026](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/)). At that scale no team reads every skill by hand. The mistake is not scanning; it is letting the scanner's number stand in for the review it did not perform.

## Both directions fail

- False rejection — a red flag on a safe skill. NVIDIA's SkillSpector gave an 871-line GitHub-automation skill 20 static findings, 16 from a single rule firing on the skill's own reason to exist: transmission to `api.github.com`. Roughly 80% were false positives, and the model-analysis passes cut it to 4 real findings ([Towards Data Science, 2026](https://towardsdatascience.com/from-green-checkmark-to-real-judgment-auditing-ai-agent-skills-with-skillspector/)). The finding count tracked capability, not intent. Static analysis behaves this way everywhere: 71 to 88% of SAST findings are false positives, and 22% of teams have disabled security tooling outright from the fatigue ([Pixee, 2026](https://www.pixee.ai/blog/sast-false-positives-reduction)).
- False confidence — a green check on a dangerous skill. Static scans match known patterns, so novel or hidden threats pass clean. The SkillCamo attack renders malicious instructions as images that rewritten skill docs reference as setup steps, and it evades six baseline scanners at 78 to 100% success, against 0% for the same attack in plain text ([Wang et al., 2026](https://arxiv.org/abs/2606.18198v1)). NVIDIA states plainly that SkillSpector is static-only and cannot detect all runtime exploitation vectors ([NVIDIA, 2026](https://docs.nvidia.com/skills/scanning-agent-skills)).

## Why it works (the mechanism)

Two independent causes pull a pass or fail away from a security judgment. Static analysis cannot run the skill, so it over-approximates — it assumes worst-case data flow and flags any capability that could be misused, which is why useful skills draw findings for doing their job ([Pixee, 2026](https://www.pixee.ai/blog/sast-false-positives-reduction)). Its mirror image is pattern matching that misses anything semantic, novel, or image-encoded ([Wang et al., 2026](https://arxiv.org/abs/2606.18198)). Then a pass or fail collapses that multi-dimensional result into one bit and throws away the actual signal — which findings fired, why, and in what context. As SkillSpector's author puts it, "the score is lossy compression; the difference between stages is the signal ... not in the number itself" ([Towards Data Science, 2026](https://towardsdatascience.com/from-green-checkmark-to-real-judgment-auditing-ai-agent-skills-with-skillspector/)). Substituting the compressed output for the analysis is the automation-bias failure.

## When this backfires

The corrective — read the findings and decide, do not obey the verdict — has limits, and over-correcting into "scanners are useless" is its own mistake:

- At ecosystem scale, a scanner is the only triage that runs. Refusing to act on its output because it is imperfect leaves you reviewing nothing or installing blind, both worse — and the scanner caught the malicious fixtures a human skim would miss ([Snyk, 2026](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/)).
- For a low-capability, well-scoped skill — read-only, no shell, no network — a clean scan does track low risk, and a full manual audit spends judgment the tool already covered.
- Better tooling narrows the gap rather than proving scanning futile: SkillSpector's semantic passes recovered precision that its static layer alone lost to false positives ([Towards Data Science, 2026](https://towardsdatascience.com/from-green-checkmark-to-real-judgment-auditing-ai-agent-skills-with-skillspector/)). Weight the scanner higher as its analysis deepens; keep the decision human.

## Example

**Before — green check read as the go-ahead:** a skill scans clean, so it is installed. Its malicious step was rendered as a "workflow diagram" image the static scanner never parsed, and the multimodal agent reads and executes it at runtime ([Wang et al., 2026](https://arxiv.org/abs/2606.18198)). The pass certified "no pattern matched," which was never the same as "safe."

**After** — the verdict is an input, not the decision: the scan runs first as triage, then a reviewer reads what fired and what did not (an unexplained bundled image, a network sink the skill's purpose does not need, a permission beyond its declared scope) and weights those against the skill's stated function before installing.

## Key takeaways

- A green check means no known pattern matched; a red flag means one did. Neither decides whether the skill is safe in your context.
- Scanners fail both ways: they over-flag useful skills (about 80% false positives on a real skill; 71 to 88% across SAST) and miss novel or image-encoded threats (78 to 100% evasion by SkillCamo).
- The pass or fail number tracks a skill's capability, not its intent; the signal lives in which findings fired and why, which the score throws away.
- Do not over-correct into not scanning — at ecosystem scale the scanner is the only triage that runs. Read its findings, weight them, and keep the decision human.

## Related

- [Model Confidence as Security Verification (Security Calibration Gap)](model-confidence-as-security-verification.md) — the model-output twin: a model's own confidence does not track security either, so it triages review and never gates it.
- [Judging Agent Safety by Task Completion (Action-Boundary Violations)](judging-agent-safety-by-task-completion.md) — another substitution of a machine signal for a safety judgment: a completed task is not a safe one.
- [Trust Without Verify](trust-without-verify.md) — the general form: accepting a clean-looking output because it looks clean, of which the green check is the scanner case.
- [Skill Supply Chain Poisoning](../../security/skill-supply-chain-poisoning.md) — the threat the scanner is meant to catch, and why install-time signatures are only part of the defense.
- [Vetting Tool Definitions for Exfiltration Signatures](../../security/vetting-tool-definitions-before-install.md) — the manual-judgment complement: what to read in a definition that no pass or fail captures.
