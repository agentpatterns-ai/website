---
title: "Separate Ignored Injections From Refused Ones Before Reading an ASR as Defense"
term: "Injection Failure Composition"
description: "Across 33,000 audited trajectories from eleven small open-weight agents, 76-80% of failed prompt injections were ignored rather than refused, and swapping one system-prompt policy for its opposite moved pooled InjecAgent ASR from 0.22% to 43.05%."
tags:
  - testing-verification
  - security
  - tool-agnostic
  - arxiv
aliases:
  - injection failure composition
  - untriggered default
  - ignored versus refused injections
last_reviewed: 2026-10-19
maturity: emerging
---

# Separate Ignored Injections From Refused Ones Before Reading an ASR as Defense

> Across 33,000 audited trajectories from eleven small open-weight agents, 76-80% of failed injections were ignored rather than refused.

Label how each attack failed before you read a low attack success rate as evidence of a boundary. Zarif and colleagues audited 33,000 trajectories from eleven open-weight agents on InjecAgent and AgentDojo with a label-blind judge. Pooled ASR at the FP16 baseline was 8.09% and 11.96%, so most agents looked secure. The benchmarks recorded 14,699 AgentDojo and 15,274 InjecAgent trajectories as failed attacks. "In 76.3% and 80.3% of them, the agent ignored the injection, while Genuine Refusal accounts for only 18.0% [17.4, 18.6] and 17.2% [16.6, 17.8]" ([Zarif et al., arXiv:2610.23254v1 §4.1](https://arxiv.org/abs/2610.23254v1)).

## The conditions this applies under

The audit covers small open-weight agents of 2 to 14 billion parameters on static injections from two synthetic single-agent benchmarks. Three limits travel with it.

- Size. The one frontier comparison, Kimi K3, refused 96.6% and 99.0% of its failed attacks, and that run "is one run of one model and does not establish a scaling trend" ([Zarif et al., arXiv:2610.23254v1 Limitations](https://arxiv.org/abs/2610.23254v1)). In that single frontier run, refusal dominated.
- Coverage. The system-prompt conditions ran only on InjecAgent and task completion only on AgentDojo, so neither result has been shown on the other benchmark.
- Attacker model. Injections were static templates placed only in tool output. Adaptive attacks reach higher success rates, which the authors read as making the finding conservative.

## What the split tells you that the rate does not

Refusal leaves a record and silence does not: "only refusal is observable: operators can log it, while ignoring leaves no trace" ([Zarif et al., arXiv:2610.23254v1 §1](https://arxiv.org/abs/2610.23254v1)). At 8% ASR with four fifths of the failures inert, the agent's own output gives an operator nothing to alert on.

Noticing the attack does not predict declining it. The judge flagged recognition in 4,740 AgentDojo and 5,688 InjecAgent trajectories, and the agent executed the attacker's action anyway in 28.9% [27.7, 30.2] and 16.9% [16.0, 17.9] of them. On AgentDojo that rate spans 82.6% for Ministral-14B to 2.0% for Ornith-9B ([Zarif et al., arXiv:2610.23254v1 §4.1](https://arxiv.org/abs/2610.23254v1)). Recognition is read from stated reasoning, so it is a lower bound.

Part of a low rate is an agent that never produced a usable action: LFM-2.6B scored 0.00% ASR with 735 invalid outputs out of 1,054 cases. Scoring task completion beside security separates that from a working agent, and of 16,273 audited AgentDojo episodes 21.7% were safe and failed the user's task.

## The matched-prompt test

Run the suite a second time under a matched permissive system prompt. The study's Interdict and Authorize prompts share identical templates and run 163 and 172 words. They differ in policy, and in length by nine words. On the 10,698 InjecAgent cases evaluated under both policies, a prompt permitting instructions in tool outputs raised pooled ASR to 43.05% [42.11, 43.99] against 8.09% at baseline. A matched prompt forbidding them lowered it to 0.22% [0.15, 0.33]. The authors conclude: "The two prompts differ by only nine words, so length cannot explain the gap" ([Zarif et al., arXiv:2610.23254v1 §4.2](https://arxiv.org/abs/2610.23254v1)). Spark-4B moved from 0.95% to 70.88%, and nine of the eleven agents shifted significantly under paired McNemar tests. The two that did not were producing mostly invalid outputs, or, for Ministral-14B, a "low response" that "remains unexplained". That distance tells you whether the model holds a boundary or the scaffold never asked it to act.

A longer prompt is not the risk. The three-rule source-boundary guardrail was the longest block the study added at 182 words, and it lowered pooled InjecAgent ASR from 9.69% to 0.95% across nine agents, two of which moved the other way. Quantization is the opposite case. FP8 and NF4 lowered pooled InjecAgent ASR to 7.50% and 6.35% with refusal rates flat. On AgentDojo, NF4 cut ASR by 2.33 points and safe-and-useful episodes by 3.97 points ([Zarif et al., arXiv:2610.23254v1 §4.2](https://arxiv.org/abs/2610.23254v1)).

## Why it works

The authors name the cause the Untriggered Default and test it as a prediction. An agent that separates instructions from data should barely move when a prompt permits them; an agent waiting to be told should jump. The measured 43.05%, 8.09% and 0.22% match the second shape, and the paper concludes: "Small agents appear secure under standard benchmarks not from robust instruction boundaries, but because default scaffolds leave injected instructions untriggered. In effect, the benchmark measures the scaffold's inertness rather than the model's safety" ([Zarif et al., arXiv:2610.23254v1 §5](https://arxiv.org/abs/2610.23254v1)). The composition itself was stable across precisions: it "holds at every precision and under every robustness check we ran" ([Zarif et al., arXiv:2610.23254v1 §4.1](https://arxiv.org/abs/2610.23254v1)).

## When this backfires

- You already enforce the boundary outside the model. A model-agnostic pair of tool-input and tool-output firewalls "achieves perfect security with high utility across all four public benchmarks": AgentDojo, Agent Security Bench, InjecAgent and tau-Bench ([Bhagwatkar et al., arXiv:2510.05244v2](https://arxiv.org/abs/2510.05244v2)). These are benchmark results. A model-only composition audit does not establish the deployed firewall's residual risk.
- Your instrument is one of the benchmarks under criticism. The same work reports "critical limitations in these existing benchmarks, including flawed success metrics, implementation bugs, and most importantly, weak attacks" ([Bhagwatkar et al., arXiv:2510.05244v2](https://arxiv.org/abs/2510.05244v2)). A composition measured on weak attacks inherits that weakness.
- The agent cannot reliably emit a tool call. Where mechanical breakdown dominates, the split rests on a small residue of trajectories.
- You cannot afford the sweep. The full study cost "about 557 GPU hours" across three precisions, two benchmarks and three prompt conditions ([Zarif et al., arXiv:2610.23254v1 Ethical considerations](https://arxiv.org/abs/2610.23254v1)), so a narrower run covers fewer of those axes.

## Key Takeaways

- In these two benchmarks, most failed attacks on the tested small open-weight agents produced no refusal. Ask for the refused share of failed attacks before reading the rate as a defense result.
- Pair every security run with a matched permissive prompt. On fixed weights the study measured 8.09% at baseline, 43.05% permissive, and 0.22% forbidding. The spread measures the boundary.
- An ignored injection leaves no trace, so an inert agent and a refusing agent at the same rate need different monitoring.
- Report task completion in the same table. In 21.7% of audited AgentDojo episodes the attack failed and so did the user's task.

## Related

- [Recover the Six Measurement Choices Behind an Attack Success Rate](asr-comparability-audit.md) — the companion rule for carrying an ASR between harnesses, where this page governs reading one number from one harness
- [Treating a Detector's Benchmark Score as Deployment Evidence](../patterns/anti-patterns/detector-benchmark-score-as-deployment-evidence.md) — the same transfer problem one layer out, measured on fifteen released injection detectors
- [Action-Graded Severity for Agent Red-Team Outcomes](action-graded-severity-red-team-outcomes.md) — grading what the agent did instead of scoring the attack as a binary
- [Single-Layer Prompt Injection Defense](../patterns/anti-patterns/single-layer-injection-defence.md) — why a system prompt is one layer and not the control
- [Covert Success Rate for Indirect Prompt Injection](../security/covert-success-rate-injection.md) — the matching split on the other side of the ledger, over injections that did run
