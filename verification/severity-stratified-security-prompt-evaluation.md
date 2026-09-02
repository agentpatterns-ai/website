---
title: "Severity-Stratified Evaluation of Security Prompts"
term: "Severity-Stratified Prompt Evaluation"
description: "Security-oriented prompts shift generated-code weaknesses from high severity to low while barely moving the total, so judge a prompt-based security intervention on a severity-stratified metric and check the output for silent construct substitution."
tags:
  - testing-verification
  - security
  - tool-agnostic
  - arxiv
aliases:
  - severity redistribution
  - security prompt evaluation
last_reviewed: 2026-08-29
maturity: emerging
---

# Severity-Stratified Evaluation of Security Prompts

> For GPT-4o, security prompts moved weaknesses from high severity to low while barely moving the total, so an unstratified count reads that as improvement.

Score a security-oriented prompt on the severity distribution of every finding, not on a headline count. Across 424 security-sensitive Python tasks scanned with Bandit and CodeQL, adding structural and security guidance to a GPT-4o prompt redistributed weakness severity without consistently reducing overall prevalence ([Urmi et al., 2026](https://arxiv.org/abs/2608.24857v1)). A count-based metric calls that a win. The same prompts did nothing of the kind to LLaMA 3.1-8B.

| Severity band | GPT-4o, structured | GPT-4o, adversarial-aware | LLaMA 3.1-8B, same progression |
|---|---|---|---|
| High | 20.8% | 13.6% | 21.2% to 24.4%, no trend |
| Low | 32.0% | 43.5% | no consistent shift |

## What actually changed

Three effects run together here, and only one is about security.

Compliance moved most. GPT-4o returned 338 invalid outputs of 424 under a minimal prompt and 37 to 52 under the four structured variants, taking the analyzable sample from 86 files to roughly 380 ([Urmi et al., 2026](https://arxiv.org/abs/2608.24857v1)). That is a large usability gain, and it changes the denominator every later security ratio uses.

CWE composition shifted next. CWE-94 (improper control of code generation) fell from 10.1% to 4.1% of GPT-4o findings while CWE-78 (OS command injection) rose from 43.9% to 49.7%. [Kharma et al. (2026)](https://arxiv.org/abs/2605.24298v1) replicate the pattern across five models and four languages: chi-square tests find "no statistically significant reductions in vulnerability frequency or density across prompt methods", while CWE composition shifts systematically.

Security guidance also rewrote code the task asked for, and no metric records it. Under the security-guided variants, 60% to 67% of sampled GPT-4o outputs altered or removed an explicitly requested construct, against 20% under the plain structured prompt. Observed substitutions: AST-based evaluation for `eval()`, `subprocess` for `os.system` ([Urmi et al., 2026](https://arxiv.org/abs/2608.24857v1)).

## Why it works

Prompts change how a model implements a task. They do not change what the task requires. Urmi et al. put the split directly: prompt refinement "can influence implementation choices (e.g., avoiding dynamic execution patterns) but cannot reliably mitigate insecure implementations embedded in task semantics (e.g., command execution or deserialization)" ([2026](https://arxiv.org/abs/2608.24857v1)). Dynamic-execution weaknesses fall because a safer construct exists to swap in. Command injection persists because a task that must shell out has nowhere safer to go.

The swap is the drift. Every substitution that removes a high-severity finding is the same edit that returns code you did not request, seen from the other side. Nothing flags it: the static analyzer scores the code it receives and never compares it against what you asked for.

## What to measure instead

- Report findings per severity band, never as one total. A summed metric cannot separate a real reduction from a redistribution.
- Condition on generation compliance. Fix the count of valid outputs before comparing weakness rates, or normalize per valid output. Otherwise a refusal-rate improvement reads as a security improvement.
- Diff the generated code against the requested construct on a sample. Drift is visible only by inspection, and 15 sampled tasks per configuration was enough for Urmi et al. to detect it.
- Say which metric a claimed reduction came from. [Bruni et al. (2025)](https://arxiv.org/abs/2502.06039v1) cut GPT-4o's scanner-agreed vulnerable-sample rate from 7.43% to 3.27% with a one-sentence security prefix. That metric counts only the CWE each scenario was built to induce, and stratifies no severity. Both results can hold at once.

## When this backfires

Treating every prompt-side gain as illusory costs a cheap control, and the result is narrower than it first reads.

- Small open-weight models do not redistribute, per the table above, and they can lose compliance for the trouble. LLaMA 3.1-8B invalid outputs rose from 51 to 150 at the adversarial-aware variant ([Urmi et al., 2026](https://arxiv.org/abs/2608.24857v1)).
- Redistribution is still worth something. If your exposure is dominated by the high band, trading it for low-band noise at constant count reduces expected damage, and a one-sentence prefix costs nothing to keep.
- Targeted single-CWE work is where prompting does measurably reduce. Hardening one known weakness class and measuring that class directly puts you in [Bruni et al. (2025)](https://arxiv.org/abs/2502.06039v1) territory, not this one.
- The measurement itself is bounded. Bandit and CodeQL "do not directly assess runtime behaviour or exploitability", the study is Python-only, and each configuration was generated once, so variance is unestimated ([Urmi et al., 2026](https://arxiv.org/abs/2608.24857v1)).

## Key Takeaways

- Security-oriented prompts redistribute weakness severity instead of removing weaknesses, so an unstratified total is the wrong instrument for judging one ([Urmi et al., 2026](https://arxiv.org/abs/2608.24857v1)).
- Report per-severity bands and condition on generation compliance, or a refusal-rate fix gets scored as a security fix.
- Security guidance rewrote an explicitly requested construct in 60% to 67% of sampled GPT-4o outputs, a fidelity cost no security metric reports.
- A reduction claim is interpretable only with its metric attached: whole-distribution counts barely move while a targeted-CWE rate falls 56% ([Bruni et al., 2025](https://arxiv.org/abs/2502.06039v1)).

## Related

- [Prompt as Security Knob](../patterns/anti-patterns/prompt-as-security-knob.md) — The same conclusion reached from prompt fragility: semantic-preserving perturbations flip secure output to vulnerable, so the prompt is never the guarantee.
- [Security Knowledge Priming for Code Generation (SPARK)](../instructions/security-knowledge-priming.md) — Corroboration from the priming side: a CWE cue shifts the CWE distribution rather than eliminating weaknesses.
- [Security Drift in Iterative LLM Code Refinement](../security/security-drift-iterative-refinement.md) — A different drift: security regressions accumulate across fix-test iterations while functional tests keep passing.
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — The umbrella page for measurement gaps a stronger model cannot close.
- [Action-Graded Severity for Agent Red-Team Outcomes](action-graded-severity-red-team-outcomes.md) — Severity stratification applied to red-team results, where a 0% attack success rate can still hide cross-scope leakage.
