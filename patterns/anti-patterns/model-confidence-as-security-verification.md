---
title: "Model Confidence as Security Verification (Security Calibration Gap)"
description: "Treating a model's own confidence in its generated code as evidence the code is secure — confidence does not track security, so use it for review triage, never as a deployment gate."
term: "Model Confidence as Security Verification"
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
aliases:
  - security calibration gap
  - model self-assessed security
  - confidence as security gate
last_reviewed: 2026-07-01
maturity: emerging
status: current
---

# Model Confidence as Security Verification (Security Calibration Gap)

> A model's confidence in its own code does not track whether the code is secure, so using it as verification ships vulnerabilities.

Using a model's own security judgment — a verbalized "this is secure," a high token probability, or just polished output — as the gate that clears code for merge is the failure mode. Confidence and actual security diverge widely, and the gap widens in real multi-file codebases. Treat confidence as a signal to prioritize human review, never as the review itself.

## When this applies

This applies wherever a model's self-reported or implied confidence is the main thing between generated code and a deployed path: agent PRs merged because the model was confident and the code compiles, "improve this until you are sure it is secure" loops, or a pipeline that auto-approves outputs above a confidence threshold. It does not apply to throwaway scripts with no production path, or to pipelines where independent security scanning and human review of sensitive paths already gate every diff.

## The failure mode

- Confidence overshoots security by a wide margin. On self-contained security tasks, expected calibration error (the gap between stated confidence and true accuracy) reaches 0.46–0.48 for GPT-4o-mini and 0.41–0.42 for Qwen3-Coder-Next; even the best-calibrated model tested, Gemini-2.0-Flash, sits at 0.25–0.26 ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).
- High confidence routinely rides on insecure code. At confidence of 0.8 or above, output is still insecure 33.9% of the time for GPT-4o-mini and 38.3% for Qwen3-Coder-Next ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).
- The problem is not a toy artifact. Across 100+ models on 80 tasks, models chose the insecure coding path 45% of the time, with no improvement over time even as functional correctness rose ([Veracode 2025 GenAI Code Security Report](https://www.veracode.com/blog/genai-code-security-report/)).

## Why it works (the mechanism)

Verbalized and token-probability confidence come from the same generative distribution that produced the code, so they reflect fluency and plausibility, not an independent security analysis — the model grades its own homework ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)). Security properties are static code patterns a model can sometimes recognize, but its confidence signal does not track them, which produces the large overconfidence gap measured as calibration error. That gap is insensitive to sampling temperature, so it is an internal property of how confidence is produced, not a knob you can tune away ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).

## When this backfires

The corrective rule — never let model confidence stand in for independent verification — has real limits:

- Confidence is useful as a relative triage signal: it can rank which outputs a human should review first. The same study that condemns confidence-as-gate endorses confidence-as-triage ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).
- Repository-level, multi-file contexts are where the gate fails hardest — false trust in high-confidence insecure code rises to 70–90%, so self-contained benchmarks understate the risk and any threshold tuned on them will not transfer ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).
- Automated repair loops do not rescue it: models flag risky samples but cannot fix them, with roughly 0% success on vulnerabilities that need an insecure API swapped for a secure one, plus over 60% functional breakage ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).

## Mitigations

- Gate deployed paths on independent security scanning (SAST or equivalent), not on the model's stated confidence. Confidence at best reorders the review queue.
- Collect functional confidence and security confidence separately; a single combined query contaminates the security estimate with execution uncertainty ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).
- Require human review on sensitive paths — auth, crypto, deserialization, query construction, and data sinks — where automatic repair fails and API-level changes are essentially unfixable by the model.

## Example

Before, with merge gated on the model's own security confidence:

```text
Agent output:
  def load_config(path):
      import pickle
      return pickle.load(open(path, "rb"))

  Self-assessment: "This is secure. Confidence: 0.92."
```

The confidence is 0.92, the code runs, so the pipeline auto-approves. It ships an insecure deserialization sink — the high-confidence-yet-insecure case that lands 33–38% of the time above the 0.8 threshold ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).

After, with confidence used only to triage and an independent gate deciding:

```text
Agent output + confidence 0.92
      │
      ├─ confidence → review-priority queue (triage only)
      │
      └─ SAST gate → flags pickle.load on untrusted input (CWE-502)
                   → human review required on the deserialization path
                   → merge blocked until fixed
```

The confidence still orders the review queue, but the deserialization finding — not the model's self-assessment — decides whether the code merges.

## Key takeaways

- A model's confidence in its own code does not track whether the code is secure; calibration error reaches 0.46–0.48 on tested models ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).
- Roughly a third of high-confidence (≥0.8) outputs are still insecure — a confidence threshold is not a security gate ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).
- The gap widens in real multi-file codebases, where false trust rises to 70–90%, so benchmark-tuned thresholds do not transfer ([Siddiq et al., 2026](https://arxiv.org/abs/2606.31159)).
- Industry-scale testing agrees: models pick the insecure path 45% of the time and are not improving ([Veracode 2025](https://www.veracode.com/blog/genai-code-security-report/)).
- Use confidence to prioritize human review; gate deployed paths on independent scanning plus human review of sensitive code.

## Related

- [Prompt as Security Knob](prompt-as-security-knob.md) — The input-side twin: prompt phrasing does not guarantee secure output either, so verification must sit on the output.
- [Trust Without Verify](trust-without-verify.md) — The general form: accepting agent output because it looks polished, of which confidence-as-verification is the security case.
- [The Test Homogenization Trap](test-homogenization-trap.md) — Model-generated tests share the model's blind spots, so self-generated checks give the same false security assurance.
- [Blind Tool Deference: Agents Parroting Callable Tools](blind-tool-deference.md) — Adopting a tool's output wholesale instead of judging it; the same uncritical trust applied to tool results.
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — Declaring done on the first signal of progress, the temporal cousin of declaring code secure on the first confident answer.
- [Overtrusting Human Sign-Off on Generated Assertions](generated-assertion-signoff.md) — The reviewer-side twin: a human's confidence in a generated assertion does not track whether it is correct either.
- [Trusting a Skill Scanner's Verdict as a Security Judgment (Green-Check Fallacy)](skill-scanner-verdict-not-security-judgment.md) — The tool-side twin: a scanner's pass/fail does not track a skill's safety, so it triages the review rather than replacing it.
- [Audit-Budget Allocation for Agent Fleets](../../verification/audit-budget-allocation-agent-fleets.md) — Qualifies the triage use endorsed here: measure whether the confidence signal discriminates before letting it order a review queue.
