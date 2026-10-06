---
title: "Treating a Detector's Benchmark Score as Deployment Evidence"
term: "Detector Benchmark Transfer Gap"
description: "The top prompt-injection detector on BIPIA caught 2.1% of AgentDojo injections at 1% FPR. Detection rank barely transfers between benchmarks."
aliases:
  - detector benchmark transfer gap
  - prompt-injection detector selection
  - guardrail leaderboard score
tags:
  - anti-pattern
  - security
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-05
maturity: emerging
---

# Treating a Detector's Benchmark Score as Deployment Evidence

> Across fifteen detectors, detection rank on one prompt-injection benchmark barely predicted rank on another, because a score mostly measures resemblance to training inputs.

This applies wherever the inputs a detector was trained or scored on differ in form from the inputs it will screen. The paper's cases run from BIPIA prose against tool output to AgentDojo against tau-bench, where both are tool output ([Liu, 2026 §5.3](https://arxiv.org/abs/2610.03448v1)). The gap is also confined to the detection rate. False alarms on benign tool outputs rank consistently across unrelated agent benchmarks ([Liu, 2026 §5.1](https://arxiv.org/abs/2610.03448v1)), so that column still earns its place.

## Detection rank does not transfer

A 2026 study scored fifteen released detectors and two task-aware judges on replayed AgentDojo and tau-bench tool outputs and on BIPIA ([Liu, 2026 §4](https://arxiv.org/abs/2610.03448v1)). Kendall's tau between detection ranks was 0.01 for BIPIA against AgentDojo, 0.28 between the two agent benchmarks, and 0.31 for BIPIA against tau-bench. None reached significance across fifteen detectors, so moderate transfer is not ruled out either ([Liu, 2026 §5.2](https://arxiv.org/abs/2610.03448v1)).

"PIGuard catches 95.1% of BIPIA injections at 1% FPR and 2.1% of AgentDojo injections" ([Liu, 2026 §1](https://arxiv.org/abs/2610.03448v1)). At the same 1% false-positive threshold, Prismor scored 72.2% on AgentDojo and 15.2% on tau-bench. Sheltron went the other way, 20.1% to 95.2% ([Liu, 2026 §5.2](https://arxiv.org/abs/2610.03448v1)). A 2025 evaluation of nine open guardrails had concluded from BIPIA that PIGuard detects indirect injection effectively ([Liu, 2026 §2](https://arxiv.org/abs/2610.03448v1)).

## False positives on tool outputs do transfer

Rank by false-positive rate on AgentDojo predicted rank on tau-bench at Kendall tau 0.67, p=0.001 ([Liu, 2026 §5.1](https://arxiv.org/abs/2610.03448v1)). False positives on prose predicted neither. "ProtectAI v2 flags 0.5% of web pages and 1.2% of emails but 30.1% of AgentDojo tool outputs" ([Liu, 2026 §5.1](https://arxiv.org/abs/2610.03448v1)), and 66.9% of tau-bench's.

Count the cost in tasks. The study marks a task blocked when the detector flags any of its tool outputs ([Liu, 2026 §3](https://arxiv.org/abs/2610.03448v1)). On AgentDojo, ProtectAI v2 and PIGuard flagged 30.1% and 29.5% of benign outputs and "would stop 69.1% and 59.8% of tasks" ([Liu, 2026 §5.1](https://arxiv.org/abs/2610.03448v1)).

## Why it works

A detector learns instruction-bearing text together with the container it arrived in. Benchmark scores "mostly measure this resemblance rather than a general ability to detect injections" ([Liu, 2026 §1](https://arxiv.org/abs/2610.03448v1)). One controlled test separates form from memorization. PIGuard's training split holds 53 of 62 InjecAgent attack instructions, as 111 short prompts rather than as text inside tool responses. Inside tau-bench tool outputs the two groups came out level. "PIGuard detects 52.1% of the outputs carrying an attack it was trained on and 55.8% of those carrying one of the 9 attacks it was not" ([Liu, 2026 §5.3](https://arxiv.org/abs/2610.03448v1)). Having seen the attack text did not help when the surrounding input was new.

Horizon-Labs is the converse. Its training set includes five public datasets of injections planted in documents and tool responses. An audit of all five found no BIPIA attack string, no AgentDojo attack template and no InjecAgent instruction. It still led both agent benchmarks, at 82.2% and 100.0% detection at 1% false positives ([Liu, 2026 §5.3](https://arxiv.org/abs/2610.03448v1)).

## When this backfires

- Both agent environments are simulations returning synthetic YAML and JSON. Format alone moves false-positive rates, so your absolute numbers will differ ([Liu, 2026 §6](https://arxiv.org/abs/2610.03448v1)).
- Every attack came from a benchmark template. The paper calls its detection rates upper bounds against an adaptive attacker ([Liu, 2026 §3](https://arxiv.org/abs/2610.03448v1)).
- Replay needs a task suite with known-correct tool calls, which is what makes the outputs benign by construction ([Liu, 2026 §4.2](https://arxiv.org/abs/2610.03448v1)).
- Some detectors did rank consistently. Prompt Guard 2 scored 69.4% and 57.9% (86M) and 60.9% and 60.8% (22M) across the two agent benchmarks ([Liu, 2026 §5.2](https://arxiv.org/abs/2610.03448v1)).
- System-level defenses such as CaMeL keep untrusted data away from the planner. They do not rely on recognizing an injection, so the paper states its detector findings do not apply to them ([Liu, 2026 §7](https://arxiv.org/abs/2610.03448v1)).
- A shared benchmark is the other route. [PromptShield](https://arxiv.org/abs/2501.15145v2) curates one for training and evaluating deployable detectors, carrying conversational and application-structured data. Its authors used insights from that curation to fine-tune a detector, and report its gains in the low false-positive regime.

## Example

Two checks in the order the paper recommends ([Liu, 2026 §6](https://arxiv.org/abs/2610.03448v1)), plus one free fix ([Liu, 2026 §5.5](https://arxiv.org/abs/2610.03448v1)).

1. Replay your agent's own ground-truth tool calls with no model in the loop. Score every output, then report the share of tasks that lose at least one. This needs no attack corpus, because the outputs are benign by construction.
2. Read the detector's model card for the form of its training inputs before you read anyone's score. A card describing short prompts predicts the PIGuard result above. A card describing documents and tool responses with planted instructions predicts the Horizon-Labs one.
3. Fix the serialization, which costs nothing. Removing YAML keys so PIGuard saw only values lowered its false-positive rate on AgentDojo from 20.0% to 6.7%, at unchanged detection. For Sheltron, declaring a tool output as `tool_result` instead of `other` "lowers its FPR on clean tool outputs from 28.6% to 10.6% on AgentDojo" ([Liu, 2026 §5.5](https://arxiv.org/abs/2610.03448v1)).

None of that rescues the detection side. After any of these format changes, neither PIGuard nor ProtectAI v2 exceeded 15% detection at 1% false positives on AgentDojo's matched set ([Liu, 2026 §5.5](https://arxiv.org/abs/2610.03448v1)).

## Key Takeaways

- Detection rank on a public injection benchmark is a weak guide to detection rank on another one. Kendall's tau ran 0.01 to 0.31 across fifteen detectors, none of it significant.
- Measure false positives on your own tool outputs first. That axis ranked consistently across two unrelated agent benchmarks and converts directly into tasks the agent cannot finish.
- Audit the form of the training inputs, not the overlap in attack strings. PIGuard had already seen 53 of 62 InjecAgent attacks. Inside tau-bench tool outputs it caught them no better than the 9 it had not seen.
- Strip serialization keys and declare the input type before you change detector. The false-positive win is free, and it does not lift detection at 1% false positives.
- Keep the detector as one filter among system-level defenses. On BIPIA's task-irrelevant group the best result outside the BIPIA-trained PIGuard was Prompt Guard 1, at 39%. Every other approach caught at most 20% ([Liu, 2026 §5.4](https://arxiv.org/abs/2610.03448v1)).

## Related

- [Mid-Trajectory Guardrail Selection for Multi-Step Tool Calls](../../security/mid-trajectory-guardrail-selection.md) — the other axis a guard model gets picked on, where efficacy tracked structured-data competence rather than safety training
- [Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses](../../security/adaptive-evaluation-out-of-band-defenses.md) — the failure this page does not cover, where a static benchmark overstates robustness against an attacker who targets the defense
- [Recover the Six Measurement Choices Behind an Attack Success Rate](../../verification/asr-comparability-audit.md) — what else hides inside one published security number
- [Single-Layer Prompt Injection Defense](single-layer-injection-defence.md) — why a detector belongs alongside system-level defenses rather than in place of them
- [Treating Memory-Injection Rate as Security Evidence](memory-injection-rate-as-security-evidence.md) — the same selection error one layer over, where the metric a defense improves and the exposure move independently
