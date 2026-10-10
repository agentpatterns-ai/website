---
title: "Treating a Model Upgrade as a Security Improvement"
description: "A release that writes better code need not write safer code. Across 32 models in seven families, no family closed the functionality-security gap."
aliases:
  - model version change security assumption
  - compact tier security penalty
tags:
  - anti-pattern
  - security
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-07
maturity: emerging
---

# Treating a Model Upgrade as a Security Improvement

> Across 32 models in seven families, no family closed the gap between code that passes functional tests and code that also passes security tests.

A model version change is a security-relevant event. Functionality and security are scored by separate oracles, so "a sample can be functionally plausible but insecure", and a security gain "narrows the gap only when it outpaces the gain in functional plausibility". Following 32 LLMs across seven families over three successive releases each, [de Moura et al. (2026)](https://arxiv.org/abs/2610.08240v1) report that "Every family also narrows the gap significantly by its newest stage for at least one number of attempts per task, but none closes it". At the newest release, with one attempt per task, that gap "ranges from 0.13 (GPT-5.6 Sol) to 0.28 (Gemini 3.1 Pro)".

## What the trajectory licenses, and what it does not

Over a full trajectory the upgrade pays. A single step can go backwards. Qwen, Z.ai and Moonshot each widened the gap significantly at their middle release when fifty attempts per task were allowed, and "GPT-5.6 Luna is less secure than GPT-5 mini on most of the 16 categories" the study charts, which are "the 16 CWEs with the highest mean CVR". Significance turns on that attempt budget too: Google's newest release narrows the gap at fifty attempts and not at one. The authors' instruction is to "rerun their security checks whenever they switch versions".

Tier is weaker evidence still. In 13 of the 22 tier comparisons the two tiers did not differ significantly, and among the nine that did, "the compact model is less secure in eight of nine cases". On a separate 80-task benchmark a compact model came out ahead: "OpenAI's GPT-5 Mini achieved a 72 percent pass rate on security tests—the highest recorded to date. The standard GPT-5 followed closely at 70 percent" ([Veracode, 2025](https://www.veracode.com/press-release/veracode-research-reveals-openais-gpt-5-models-lead-the-way-in-secure-code-while-wider-industry-progress-stalls/)). Tier is not a fixed security cost, though, and the authors advise that "Developers should thus compare the security of both tiers of the version they adopt instead of inferring it from the tier".

## Why it works

Security belongs to the model, the language and the prompt context jointly, because the model takes whichever plausible path is shortest: "Models therefore follow the shortest path that the language or the prompt offers, whether that path is secure or not". The same weakness class then splits by language. Pooled over all 32 models, improper signature verification shows "a CVR of 0.73 in Go and 0.71 in C against 0.04 in Python", because "Almost every Python sample fixes the HMAC algorithm on CWE-347, because the library requires it". Unsafe deserialization inverts that pair, reaching "0.80 in Python and 0.00 in JavaScript", because there the Python prompt is the one offering the unsafe call. A new release changes which construct the model reaches for first, which is how security moves while functionality holds. That also gives the lever: "placing secure APIs in that context, such as a safe loader or a validation helper".

## When this backfires

- A dynamic security gate already runs on every change. The next pull request measures what a version-triggered check would, so the trigger earns its keep only where the check is manual or sampled.
- The weaknesses you care about are log injection or HTTP response splitting. Both "stay near the maximum in every family, tier, and stage", with one exception: on HTTP response splitting, OpenAI's middle release "lowers the rate in both tiers, and the flagship GPT-5 secures more than half of its functionally plausible samples, a gain that the newest stage partly loses". Veracode records log-injection pass rates "near 12 percent" on its own benchmark. So "code that writes logs or HTTP headers needs manual review whichever model produced it".
- Generated code lands inside a repository, not as a standalone function. CWEval isolates single functions, and the study leaves open "whether a larger context helps avoid the observed weaknesses". A repository-level benchmark reports that "The complexity in repository-level scenarios presents challenges for LLMs that typically perform well on snippet-level tasks" ([A.S.E, 2025](https://arxiv.org/abs/2508.18106v3)).
- You would re-measure on the public benchmark instead of your own tasks. The study flags contamination against itself: "CWEval predates most models we evaluate, so its tasks may have entered their training data."

## Example

In the models the authors inspected, "Python samples mostly reuse the unsafe Loader of PyYAML that the prompt imports" while "JavaScript samples use a YAML loader that is safe by default." In those Python samples, "every sample that passes it to yaml.load is insecure, while the one sample in five that calls yaml.safe_load instead is always secure".

**Before — the shortest path in context is the unsafe one:**

```python
# context the model completes against
import yaml
# model completes with: yaml.load(payload, Loader=yaml.Loader)
```

**After — the safe call is the one within reach:**

```python
# context the model completes against
from yaml import safe_load
# model completes with: safe_load(payload)
```

The JavaScript arm is the measured form of that edit: its loader is safe by default, and "CWE-502 reaches 0.80 in Python and 0.00 in JavaScript". The study did not run the edited-import Python variant, so swapping the import applies its recommendation rather than reproducing a result. Confirming the swap and catching the next model reaching for a different construct are the same gate.

## Key Takeaways

- Newer is safer in absolute terms across a whole trajectory. Across one release step, treat it as something to measure.
- Record the attempt budget alongside any gap figure. Three of the seven families widened the gap significantly at their middle release at fifty attempts, "with no corresponding change at k=1".
- Most tier comparisons show no significant difference. Where they do, "the compact model is less secure in eight of nine cases", so measure both tiers of the version you adopt rather than inferring from the tier.
- Log injection and HTTP response splitting need a reviewer or a sanitizing helper. One release in the study moved HTTP response splitting and then gave part of it back.
- A gap measured on isolated single functions is not a forecast for code generated inside a repository.

## Related

- [Cheaper-Per-Token Model Upgrades That Cost More Per Task](cheaper-per-token-costlier-per-task.md) — the same upgrade assumption, measured on cost per successful task instead of security.
- [Cost-Driven Model Routing Without Quality Monitoring](cost-routing-without-quality-monitoring.md) — what goes unseen when cheaper tiers carry traffic with no per-tier signal.
- [Treating a Clean Static Scan as Security Evidence](static-clean-as-security-evidence.md) — why the oracle you re-measure with decides what the number means.
- [Security Drift in Iterative LLM Code Refinement](../../security/security-drift-iterative-refinement.md) — the same functional-versus-security divergence inside one fix-test loop.
- [Capability-Pegged Security Re-Scans](../../security/capability-pegged-security-rescan.md) — the other direction, re-reviewing unchanged code when the scanner rather than the generator improves.
