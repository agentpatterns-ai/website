---
title: "Treating Memory-Injection Rate as Security Evidence"
term: "Injection-Execution Dissociation"
description: "A prompt guard cut memory injection on the Claude Code harness from 83.3% to 6.7% while cross-session attack success moved 0.0 points. Injection and execution are separate properties."
aliases:
  - injection-execution dissociation
  - storage rate as agent security metric
  - memory poisoning injection rate
tags:
  - anti-pattern
  - security
  - memory
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-17
maturity: emerging
---

# Treating Memory-Injection Rate as Security Evidence

> Injection rate and execution rate move independently, so a memory defense can cut one to near zero and leave the other unchanged.

This holds where the store outlives the session and the agent can act on the world. If memory is session-scoped, or every write lands through review, the two stages collapse and injection rate is the whole risk. Otherwise a control that wins at its own layer proves nothing about the exposure.

## The two numbers that disagree

PMPA plants a rule in a benign external source, lets the agent write it to persistent memory, then triggers it a session later. Against a sandwich-style prompt reminder in its calendar scenario, injection success on the Claude Code harness fell from 83.3% to 6.7% on PDF and from 65.6% to 2.2% on image, while cross-session attack success went 96.7% to 96.7%, a change of 0.0 points. OpenClaw moved 1.1 ([Huang et al., 2026 §4.3](https://arxiv.org/abs/2609.13889v1)). Read the top line and the guard looks like a win.

The mirror failure is quieter. Injection succeeded in 100% of 2,520 attack runs across a 5,040-run factorial ([Leong, 2026 §3.1](https://arxiv.org/abs/2605.08442v5)), while execution over its nine models ranged from 0% to 95% with no correlation to storage rate ([Leong, 2026, abstract](https://arxiv.org/abs/2605.08442v5)). Every tested OpenAI model stored the rule at 97.5% or higher, including ones that never executed it, and the row sits there "invisible to runtime monitoring that only checks execution outcomes" ([Leong, 2026 §5.6](https://arxiv.org/abs/2605.08442v5)). GPT-5.1 measured 12.2% attack success against GPT-5's 1.9%, so execution safety is not stable across versions ([Leong, 2026 §5.6](https://arxiv.org/abs/2605.08442v5)).

## Why it works

The two stages sit across an authority boundary, so a control on one has no purchase on the other. At write time the rule is visibly part of someone else's document. Once stored it comes back as the agent's own prior state, and a reminder to confirm before acting on stored rules has nothing to mark it suspect. Defense effectiveness "is governed by where a defense sits relative to the attack's authority boundary, not by classifier quality" ([Leong, 2026, abstract](https://arxiv.org/abs/2605.08442v5)).

## When this backfires

- Reading a second number needs an oracle for which action is malicious; without an enumerable action set, injection rate is all you get.
- The dissociation is partly a measurement artifact. Leong ran no store-stage defense, so injection stayed at 100% in every arm, and PMPA's cross-session rate is conditional on poisoning.
- Knowing the second number does not tell you what to do. Removing the recall tool reached 0% on eight of nine models and inverted to 100% on the ninth, whose agent read the rule back off the source document instead ([Leong, 2026 §3.3](https://arxiv.org/abs/2605.08442v5)).
- Remediation is harder than deleting a row: one model split the payload across two keys in 37 of 40 runs ([Leong, 2026 §5.3](https://arxiv.org/abs/2605.08442v5)). The factorial rests on one malicious document at 40 runs per arm, with an archetype that failed to reproduce two months later ([Leong, 2026 §5.10](https://arxiv.org/abs/2605.08442v5)).

## Example

The gap is easiest to see in how the payload arrives. PMPA measured injection success by input modality, and the ranking inverts what hiding a payload would suggest:

| Input | Claude Code | OpenClaw |
|---|---|---|
| Plain text | 91.4% | 99.4% |
| PDF | 61.9% | 67.2% |
| Image | 47.5% | 54.5% |

Image and PDF need a parsing tool call first, and during it "the external content is more likely to be marked as untrusted" ([Huang et al., 2026 §4.1](https://arxiv.org/abs/2609.13889v1)). The prompt guard compounds with that boundary. It drove image injection to 2.2% on Claude Code and 0.0% on OpenClaw, while plain text stayed at 84.4% and 66.7%.

So the modality the write-side guard handles worst is the one an agent sees most, and a dashboard reporting the aggregate hides that. Waiting does not clear the rules already stored: after five intervening benign sessions, cross-session success on the Claude Code calendar scenario went from 96.7% to 93.3%, with "no consistent decrease" across settings ([Huang et al., 2026 §4.2](https://arxiv.org/abs/2609.13889v1)).

PMPA drove both harnesses with DeepSeek-V4-Flash, DeepSeek-V4-Pro and Qwen3-Max ([Huang et al., 2026 §3.4](https://arxiv.org/abs/2609.13889v1)). No Anthropic model was tested, so "66.9% on Claude Code" describes the harness under three third-party backbones, and quoting it as a property of Claude would be wrong.

## Key Takeaways

- A memory defense that reports how much injection it prevented has reported one of two numbers. On the Claude Code harness a guard moved injection 76.6 points and cross-session attack success 0.0 ([Huang et al., 2026 §4.3](https://arxiv.org/abs/2609.13889v1)).
- The reverse blind spot costs more later: execution-safe models still stored the rule at 97.5% or higher, and a version that regresses on execution re-arms every dormant row.
- The two stages come apart because they sit across an authority boundary. Placement decides a defense's outcome, not how well it classifies text.
- Give already-stored payloads their own remediation track. A guard that stops new writes does not touch them, and clearing the key you know about can leave the rest of the payload behind.
- Leong's factorial held injection at 100% by design, and PMPA's cross-session rate is conditional on poisoning, so read the dissociation as a warning about what your metrics can tell you rather than a measured effect size.

## Related

- [Dormant Memory Payloads Triggered by Sensitive Topics (Trojan Hippo)](../../security/trojan-hippo-memory-attack.md) — the attack shape this page measures, with write-policy and information-flow defenses costed against utility
- [Detecting Memory-Poisoning Exfiltration by Tool-Call Order](../../security/recall-before-send-memory-poisoning-detection.md) — an execution-stage signal for the second number, and its false-positive problem
- [Typed Memory Provenance and Assertion Release Gating](../agent-design/typed-memory-provenance-assertion-gating.md) — a control that governs both stages at once, evaluated on a conformance suite rather than an attack
- [The Recall Trap: Tuning a Code Retriever on Recall@k at a Fixed Slot Budget](recall-trap-retriever-tuning.md) — the same measurement error in retrieval, where the flag's own metric improves and the downstream task does not
- [Prompt-Only Tool Access Control](prompt-only-tool-access-control.md) — why the instruction layer keeps losing, which is the adjacent claim this page is careful not to make
