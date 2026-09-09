---
title: "Benign Skill Wording That Steers Package Hallucination (Neutral Prompting Attack)"
term: "Neutral Prompting Attack"
description: "A skill that asks only for imagination and exhaustiveness raised one model's package-hallucination rate from 4.54% to 78.99%. It names no package and gives no malicious instruction, so static scanners and human reviewers have nothing to match."
tags:
  - security
  - tool-agnostic
  - arxiv
  - skills
  - supply-chain
aliases:
  - neutral prompting attack
  - hallucination steering in agent skills
  - benign skill wording attack
last_reviewed: 2026-09-08
maturity: emerging
---

# Benign Skill Wording That Steers Package Hallucination (Neutral Prompting Attack)

> Skill wording that only asks for imagination and exhaustiveness raised one model's package-hallucination rate from 4.5% to 79%, with no malicious instruction to detect.

A Neutral Prompting Attack (NPA) is a persistent instruction artifact, usually a skill file, whose text names no package and asks for nothing forbidden, and which still makes the agent invent dependencies far more often than it otherwise would. On Qwen2.5-Coder-32B-Instruct, NPA "raises Hallucination ASR from 4.54% under Normal Skill to 78.99% on LLM_LY, and from 3.53% to 57.76% on LLM_AT", two prompt sets built around Python packages ([arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2)). The attacker registers the names that start appearing, and the ordinary [slopsquatting](slopsquatting-hallucinated-package-names.md) chain runs from there.

Two conditions decide whether this matters to you. You have to load skills, rules files, or project templates that someone outside your team wrote. And your agent's install path has to accept a package name that no human endorsed. Close the second and the paper's own strict-allowlist row measures 0.00% on both attack metrics. Close the first and there is no artifact left to carry the wording.

## What is different about it

Three attacks share the same registry endgame and differ in what the defender can see.

| | Slopsquatting | Dependency steering | Neutral prompting |
|---|---|---|---|
| Source of the bad name | The model's own prior | A skill naming the target package | A skill naming nothing |
| Attacker control of rate | None, enumerate what exists | High, one package | High, the whole distribution |
| What a scanner can match | Nothing, no artifact | Target package reference | Nothing |
| Reference | [arXiv:2406.10279](https://arxiv.org/abs/2406.10279) | [arXiv:2605.09594v1](https://arxiv.org/abs/2605.09594v1) | [arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2) |

The middle column is what this site covers under [skill supply-chain poisoning](skill-supply-chain-poisoning.md), where the skill carries a payload or a target. Neutral prompting removes the artifact and keeps the effect. The authors build it by mutating an ordinary skill through "three evolutionary operations: Rewrite, Inject, and Framing", scored on how often the model emits a nonexistent package name ([arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2)).

## Why it works

The authors give an additive account: "creativity-oriented instructions broaden the model's candidate space, while exhaustiveness-oriented instructions pressure the model to avoid omissions even when grounded knowledge is insufficient", and their combination "encourages speculative package generation" ([arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2)). The second half carries the weight. A demand for completeness turns "I know of no library for this" into an emitted name, because the instruction has priced omission higher than invention.

The explanation is behavioral, and the authors say so: the analysis rests on output behavior rather than internal mechanistic study. It describes what the wording does to the output distribution, not why the model responds that way.

## What the measurements cover

The effect survives the trip from a benchmark into a running agent. Running the skill in three closed-loop harnesses, the paper reports generated hallucination, proposed install, and executed install rates of 84.01%, 88.03%, and 90.77% in Claude Code; 80.96%, 75.81%, and 82.29% in OpenHands; and 65.59%, 61.40%, and 60.34% in OpenCode. Every normal-skill figure in the same table sits below 3.5% ([arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2)).

Transfer is real but uneven. The cross-model table lifts GPT-5 from 1.28% to 29.29% hallucination attack success and Nemotron-3-Nano-30B-A3B from 37.22% to 47.01%, while Llama-3.1-8B-Instruct moves only from 16.43% to 17.74% ([arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2)). Treat the headline figures as the ceiling for a well-fitted target, not the number to expect on your model.

Detection is where the result bites. "Static analysis tools fail to flag the generated Skills as malicious, while among LLM/agent-based tools, only Snyk Agent Scan can detect them" ([arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2)). Ten computer-science students grading on a 7-point suspicion scale rated a normal skill 1.0, an unoptimized NPA 5.0, and the stealth-optimized variant 1.2, and all ten said they would enable that variant. A clean scan and a clean read carry no information here, which is the same trap as [trusting a skill scanner's verdict](../patterns/anti-patterns/skill-scanner-verdict-not-security-judgment.md).

Stealth can cost the attacker, which is the defender's leverage, though not reliably. Folding Snyk evasion into the optimization loop (NPA-Snyk) dropped pip-install attack success on Qwen2.5-Coder-32B-Instruct from 50.63% to 8.32%, roughly five sixths of the payoff. On Gemma-3-12b-it the same variant went the other way, from 17.44% under a normal skill to 53.69% ([arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2)). Pressure on detection buys something on some targets, and you cannot count on which.

## Which controls hold

Ranked by what the paper measured, against an unprotected baseline of 57.76% hallucination and 50.63% pip-install attack success on the same model and dataset ([arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2)):

- Strict allowlist: 0.00% and 0.00%. It closes the vector and costs dependency flexibility, which is the whole trade.
- Package-existence check: 59.60% and 51.12%. No reduction. The paper reports the number without a cause; the reading that fits the sibling evidence is that existence stops being a useful predicate once someone registers the name first, which is [the documented slopsquatting sequence](slopsquatting-hallucinated-package-names.md).
- Lockfile-enforced install: the allowlist predicate applied per project, and the control the [slopsquatting page](slopsquatting-hallucinated-package-names.md) already recommends.
- Inference-time mitigation: retrieval grounding cuts the cross-model average package-hallucination rate from 29.7% to 18.1%, while decoding-only defenses give "inconsistent protection under adversarial prompting", with rates rising by up to 45 percentage points ([arXiv:2608.22652v1](https://arxiv.org/abs/2608.22652v1)). Useful as depth, useless as the only layer.

## Example

A gate here has to answer whether a human committed this name, which is a different question from whether the package exists. Two `uv` flags divide on that line, and the difference is easy to get backwards.

**Before** — the manifest gains a dependency and nothing compares it to the lockfile:

```bash
$ uv sync --frozen          # datasets-cache-utils was just added to pyproject.toml
Audited in 0.00ms
```

`uv sync --help` (uv 0.8.17) describes `--frozen` as "Sync without updating the `uv.lock` file", and that is all it does: the added name produces no install and no error, because nothing compared the two files.

**After** — the lockfile has to agree with the manifest:

```bash
$ uv sync --locked
  × No solution found when resolving dependencies:
  ╰─▶ Because datasets-cache-utils was not found in the package registry and
      your project depends on datasets-cache-utils, we can conclude that your
      project's requirements are unsatisfiable.
```

`--locked` asserts "that the `uv.lock` will remain unchanged", so in CI it forces every new name through a `uv lock` run and a lockfile diff someone reads. Once the attacker registers the name the resolution stops failing, and that diff is the control that remains.

## When this backfires

Treating this as a new skill-review problem is the wrong response for most teams.

- You already install from a lockfile, an internal mirror, or an allowlist. A skill-review program aimed at this attack buys nothing on top of the control the paper measured at 0.00%.
- You author every skill internally. The attack needs an instruction artifact you did not write, and reviewing your own skills for suspicious wording finds nothing, because the wording is not suspicious.
- You work outside Python. The authors state the evaluation covers Python packages and that generalization to JavaScript and Rust is unclear.
- You start deleting quality wording from your own skills. The paper optimizes wording adversarially against a hallucination score. It never shows that asking your own agent to be thorough harms you.
- You adopt a registry existence check as the answer. That is the one control the paper measured as ineffective here.

The marginal risk may also be small. A user who installs a third-party skill has already granted it persistent instruction authority over the agent, which in most harnesses includes shell execution. Nudging the package-name distribution is a smaller capability than the ones that skill already holds.

## Key Takeaways

- Wording that asks only for imagination and exhaustiveness raised hallucination attack success from 4.54% to 78.99% on Qwen2.5-Coder-32B-Instruct, with no package named and no malicious instruction present ([arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2))
- Static scanners have nothing to match, and ten of ten human evaluators rated the stealth variant 1.2 on a 7-point suspicion scale and would enable it, so a clean review is not evidence
- A strict allowlist measured 0.00% on both attack metrics; a package-existence check measured 59.60% against a 57.76% unprotected baseline, which is no reduction at all
- Evading the one scanner that detected the attack cut pip-install attack success from 50.63% to 8.32%, so pressure on detection still costs the attacker most of the payoff
- Two conditions make this yours: third-party skill intake, and an install path that accepts an unendorsed name

## Related

- [Slopsquatting: Hallucinated Package Names as a Supply-Chain Vector](slopsquatting-hallucinated-package-names.md) — the passive case this attack turns active; the attacker there enumerates a fixed prior instead of moving it
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — the same delivery channel carrying a payload, which is what makes it detectable and this variant not
- [Trusting a Skill Scanner's Verdict as a Security Judgment (Green-Check Fallacy)](../patterns/anti-patterns/skill-scanner-verdict-not-security-judgment.md) — why a pass on a skill with no artifact to match tells you nothing
- [Semantic Intent Validation for Agent Skills](semantic-intent-validation-skills.md) — the intake-gate layer, and its limit when the intent under review is benign
- [Judging a Skill's Honesty by the Validity of Its Output](../patterns/anti-patterns/judging-skill-honesty-by-output-validity.md) — the same class of payload-free skill steering aimed at a different target: which real candidate wins, rather than how often a nonexistent name appears
- [Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface](agent-emitted-dependency-ranges.md) — the third agent-authored-manifest failure, where the name is real and the range admits a future compromise

## Sources

- [arXiv:2605.29354v2](https://arxiv.org/abs/2605.29354v2) — Hsu, Yu, Huang, Sakuma, "Harmless Yet Harmful: Neutral Prompting Attacks for Stealthy Hallucination Steering in Agent Skills"
- [arXiv:2605.09594v1](https://arxiv.org/abs/2605.09594v1) — Liu et al., "Trust Me, Import This: Dependency Steering Attacks via Malicious Agent Skills", the targeted sibling attack
- [arXiv:2608.22652v1](https://arxiv.org/abs/2608.22652v1) — Djire et al., "Evaluating Inference-Time Defenses against Package Hallucination in LLM-Generated Code"
- [arXiv:2406.10279](https://arxiv.org/abs/2406.10279) — Spracklen et al., USENIX Security 2025, the baseline package-hallucination measurement
