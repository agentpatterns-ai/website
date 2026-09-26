---
title: "Task Category as the Security Review Routing Key"
term: "Task-Category Review Routing"
description: "Generated-code security findings cluster by what the task does far more than by which assistant wrote it, so route review depth by task category and keep model choice a separate, semantically graded decision."
aliases:
  - task-type security review routing
  - category-based security review allocation
tags:
  - testing-verification
  - security
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-19
maturity: emerging
---

# Task Category as the Security Review Routing Key

> Across one 54-sample study, generated-code security findings varied three to six times more by task category than by which tool wrote the code.

Route security review of agent-generated code by what the code does, not by which assistant produced it. Two conditions decide whether that pays. Your agents work across several task categories, so there is variance to route on. And model selection stays a separate decision, graded by something other than a static analyzer — the instrument that makes the tool axis look small in the first place.

## What the measurement shows

AlJanah generated 54 Python functions: three tools (ChatGPT, Gemini, DeepSeek) across six tasks in three categories, each prompted three ways. Bandit 1.9.4 scored every function, with low, medium and high findings weighted 1, 2 and 3 ([arXiv:2609.18658v1](https://arxiv.org/abs/2609.18658v1)).

| Tool | Input processing and file handling | Authentication and account recovery | Internal service communication | Overall |
|---|---|---|---|---|
| ChatGPT | 3.00 | 0.33 | 2.67 | 2.00 |
| Gemini | 3.50 | 0.00 | 3.33 | 2.28 |
| DeepSeek | 5.50 | 0.66 | 2.17 | 2.78 |

The three tools sit within 0.78 points of each other in the last column. Across any row the categories span 2.67 points for ChatGPT, 4.84 for DeepSeek. The axis you would route review on is three to six times wider than the one you would procure on.

SafeGenBench reproduces the shape over 13 models, 558 prompts and 12 languages. Within Gemini-2.5-Pro, category accuracy runs from 9.09% on resource issues to 81.48% on memory safety. Zero-shot overall accuracy across the 13 models runs 27.78% to 46.42% ([arXiv:2506.05692v3](https://arxiv.org/abs/2506.05692v3)). That is a 72-point within-model spread against a 19-point cross-model one.

## Why it works

The insecure option lives in the library surface the task forces the code to touch. Compare the prompt wording across categories. Every prompt for the two internal-service tasks tells the model the service uses a self-signed certificate. The paper scopes that category to "scenarios involving certificate validation and secure communication". Every prompt for the two verification-code tasks instead restricts the implementation to the Python standard library ([arXiv:2609.18658v1](https://arxiv.org/abs/2609.18658v1), §IV-A and Appendix A). One framing puts certificate validation in play on every attempt. The other leaves a safe standard-library route open at no extra cost. The scores track that split: authentication came in at 0.00 to 0.66, internal service communication at 2.17 to 3.33. Input handling, whose six prompts all hand the function a user-provided file, came in highest at 3.00 to 5.50.

Three tools from three vendors converged on the same per-category ordering. That is what you see when the task's idiom set decides the outcome rather than the model. Rephrasing a task also moved its score: "prompts belonging to the same task did not always produce similar outcomes" ([arXiv:2609.18658v1](https://arxiv.org/abs/2609.18658v1)).

## When this backfires

- The instrument shrinks the tool gap. SafeGenBench scored identical code two ways. Across 13 models, its static-analysis judge spread 6.63 points zero-shot (85.66 to 92.29) while its semantic judge spread 21.32 points (30.47 to 51.79). The authors' reading: "the accuracy scores assigned by the SAST-Judge exhibit relatively small variance across different models and experimental settings, whereas the scores given by the LLM-Judge show substantial differences" ([arXiv:2506.05692v3](https://arxiv.org/abs/2506.05692v3)). Use task category to allocate review, never to call model choice cheap.
- A low score describes the tool population, not the category. Authentication and account recovery scored lowest because all three models took the safe path there. The paper's threat model still counts "authentication and account recovery mechanisms" in its attack surface ([arXiv:2609.18658v1](https://arxiv.org/abs/2609.18658v1)). The two SafeGenBench judges also flag near-disjoint weakness classes: the static side leads on CWE-915 and CWE-79, the semantic side on CWE-1104 and CWE-778 ([arXiv:2506.05692v3](https://arxiv.org/abs/2506.05692v3)). Logic flaws such as insufficient logging sit on the side a static analyzer misses.
- The score counts findings, not exploits. Scanning 190 candidate functions from six Python projects for command injection, Bandit returned 81 true positives against 103 false positives, a measured precision of 44% ([arXiv:2505.15088v1](https://arxiv.org/abs/2505.15088v1)). That figure covers one weakness class rather than the whole rule set, and it is reason enough to read a severity-weighted total as a ranking, not a magnitude.
- A concentrated task mix leaves nothing to route. If almost everything your agents write falls in one category, the taxonomy costs maintenance and allocates nothing.
- No scarcity, no benefit. Where review already covers every change at full depth, routing adds a classification step and removes no work.

## Key Takeaways

- Build the routing table from categories you can name at ticket time, such as untrusted input parsing, archive and file handling, and outbound service calls. Tool identity does not need a column.
- Grade models on a semantic check, not on the static-analysis totals you route with. The two instruments disagree about cross-model spread by roughly a factor of three.
- Treat a category's low defect rate as a fact about the tool population that produced it. Re-measure after a model change, and hold a floor of review on high-consequence categories whatever the score says.
- Route on the ranking and budget on something else. A scanner total orders the categories against each other, and a published precision measurement for Bandit, on command injection, came in at 44%.

## Related

- [Risk-Based Task Sizing for Agent Verification Depth](risk-based-task-sizing.md) — the general case: scale verification depth to task risk, classified by file path
- [Severity-Stratified Evaluation of Security Prompts](severity-stratified-security-prompt-evaluation.md) — why an unstratified finding count misreads a security intervention as an improvement
- [Audit-Budget Allocation for Agent Fleets](audit-budget-allocation-agent-fleets.md) — what happens to a ranked review queue once the ranking signal stops discriminating
- [Root Causes of Vibe-Coded Application Vulnerabilities](../security/vibe-coded-vulnerability-root-causes.md) — the defect rates that survive prompt and harness changes
- [Security Drift in Iterative LLM Code Refinement](../security/security-drift-iterative-refinement.md) — how security regressions accumulate while functional tests stay green
