---
title: "Clarification Mode Amplifies Prompt Injection"
description: "Asking the agent to clarify ambiguity before acting raises prompt-injection success rates 10–30x; treat clarification as an attack surface, not a safety control."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - clarify-then-act injection
  - ask-user injection amplification
last_reviewed: 2026-05-27
---

# Clarification Mode Amplifies Prompt Injection

> A clarify-then-act turn opens a high-trust input channel that injected content can negotiate with. Across frontier models, prompt-injection success rates rise from 1–11% in standard execution to 24–63% under clarification ([ASPI, 2026](https://arxiv.org/abs/2605.17324)).

## Core Concept

Clarification-seeking — pausing to ask the user when a task is ambiguous — is widely treated as a safety win. On benign inputs it is. On adversarial inputs the inverse holds: the clarification turn lets injected content negotiate with the agent, amplifying vulnerability by an order of magnitude across frontier models ([ASPI, 2026](https://arxiv.org/abs/2605.17324)).

This is not a reason to stop asking clarifying questions. Uncertainty-aware clarification raises task-resolve rates on underspecified specs by 8 points on SWE-bench Verified ([Ask or Assume?, 2026](https://arxiv.org/abs/2603.26233)). It is a reason to treat the clarification channel like any other untrusted-input surface — with segment-level filtering and an ask_user-aware action gate.

## How It Works

The ASPI benchmark (728 task-attack scenarios, four frontier models) measures attack success rate (ASR) in two configurations: standard execution versus the same agent extended with an ask_user clarification tool. The ASR jump is the amplification effect ([ASPI, 2026](https://arxiv.org/abs/2605.17324)):

| Model | Standard ASR | Clarification ASR |
|-------|--------------|-------------------|
| o3 | 1.8% | 34.0% |
| Gemini-3-Flash | 2.2% | 35.7% |
| Gemini-3.1-Pro | 1.1% | 24.3% |
| Kimi K2.5 | 11.1% | 63.1% |
| Claude-Opus-4.7 | near-zero | near-zero |

Agents in clarification mode exhibit "TASK_AND_ATTACK" behaviour — integrating injected instructions into task context instead of rejecting them; judges mark responses "CONFUSED or PERSUADED" when adversarial content is treated as legitimate task data ([ASPI, 2026](https://arxiv.org/html/2605.17324)). Claude-Opus-4.7 is the one tested model that holds the gap closed — the property is model-specific, not architectural.

## Why It Works

The mechanism is **provenance collapse during solicited input**. When the agent issues `ask_user`, it expects the next message to be trusted clarification. Whatever fills that slot — including injected text relayed from an earlier tool output — enters context with raised trust. Injection defences trained on tool-output flows do not generalize: the agent is now reading a message it asked for, and treats it accordingly ([ASPI, 2026](https://arxiv.org/html/2605.17324)).

This is the same failure mode that makes clarification useful on benign inputs — the reply is weighted heavily against conflicting prior context. Helpfulness and injection resistance are independent properties; see [Discovering Indirect Injection Vulnerabilities in Your Agent](indirect-injection-discovery.md).

## Defences

ASPI evaluates two lightweight defences against Gemini-3-Flash's 35.7% baseline ([ASPI, 2026](https://arxiv.org/html/2605.17324)):

- **Prompt guard** (segment-level filter scanning both user and tool messages while preserving benign clarification content) → 27.0% ASR
- **Tool filter** (ask_user-aware restriction firing before agent action while maintaining clarification ability) → 23.9% ASR

Neither closes the gap. The architectural fix is an explicit action gate on the post-clarification turn — restricting which tools the agent may call between the clarification reply and the next pause point. This composes with the [Action-Selector Pattern](action-selector-pattern.md) and [Plan-Then-Execute](plan-then-execute-web-agents.md) (commit to a program before observing untrusted content).

## When This Backfires

The amplification effect only causes harm under specific conditions:

- **No untrusted content in the agent's context.** If the agent never reads external pages, emails, or third-party tool outputs, the injection vector does not exist regardless of clarification mode.
- **Lethal-trifecta legs are missing.** Injection only causes harm when the agent also has private-data access and egress. See [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md) — closing any one leg defangs the amplification.
- **Model handles solicited-input provenance correctly.** Claude-Opus-4.7 held near-zero ASR in both modes on ASPI; the property is measurable per model, not assumed ([ASPI, 2026](https://arxiv.org/html/2605.17324)).
- **Action gates restrict the post-clarification turn.** If consequential actions require a [confirmation gate](human-in-the-loop-confirmation-gates.md), a successful injection cannot ride elevated trust into a destructive call.

Removing clarification regresses the agent to silent assumption-making, which has its own large failure surface ([Ask or Assume?, 2026](https://arxiv.org/abs/2603.26233); [Ambig-SWE, 2026](https://arxiv.org/abs/2502.13069)). Keep clarification *and* layer defences.

## Key Takeaways

- Clarification-seeking is an attack surface, not a safety control. Standard injection benchmarks understate risk for any agent that asks clarifying questions ([ASPI, 2026](https://arxiv.org/abs/2605.17324)).
- The mechanism is provenance collapse: solicited input enters context with raised trust, and injected text rides that elevation.
- Two lightweight defences (segment-level prompt guard, ask_user-aware tool filter) narrow but do not close the gap; an explicit action gate on the post-clarification turn is the architectural fix.
- The amplification is model-specific. Measure your model's ASPI ASR before assuming clarification is safe in your stack.
- Do not remove clarification — it has documented benign-task benefit. Treat the clarification reply like any other untrusted input.

## Related

- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md)
- [Discovering Indirect Injection Vulnerabilities in Your Agent](indirect-injection-discovery.md)
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md)
- [Action-Selector Pattern: LLM as Intent Decoder with Deterministic Execution](action-selector-pattern.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
