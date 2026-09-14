---
title: "Treating a Clean Static Scan as Security Evidence"
term: "Static-Pass Dynamic-Fail"
description: "Sandboxed exploit tests confirmed vulnerabilities in 83 of the 235 probed Python files that Bandit and Semgrep both cleared, and the confirmation rate swings from 5.4% to 33.7% depending on the corpus."
aliases:
  - static-pass dynamic-fail
  - SPDF gap
  - clean SAST run as a security gate
tags:
  - anti-pattern
  - security
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-11
maturity: emerging
---

# Treating a Clean Static Scan as Security Evidence

> A clean static scan means no rule matched, and a runtime exploit stage confirmed vulnerabilities in 83 of 235 clean files it probed.

Reading a green Bandit and Semgrep run as the security gate for agent-written Python is the mistake. Two conditions set the cost. The code needs an input path an attacker controls, and your scanner configuration needs to be the one you think it is.

## The rate depends on which corpus you read

Pourleyli and colleagues put 1,355 Python samples through a composite gate of Bandit 1.8.4 and Semgrep 1.155.0. 654 came out with zero findings. An LLM stage named 394 candidates across 235 of those files, and a sandboxed exploit stage confirmed 83. The paper reports that as a "conservative pipeline yield of 12.69% (83/654)", rising to an "inclusive yield of 14.53% (95/654)" once partial confirmations count ([arXiv:2609.10762v1](https://arxiv.org/abs/2609.10762v1)). Both are yields rather than prevalence, because only 235 of the 654 clean files were ever probed.

The per-corpus rates use a different denominator, candidate file-CWE pairs, and they diverge: 33.7% on RedCode (adversarial), 28.6% on CyberNative (seeded with vulnerabilities), 5.4% on SecurityEval (a curated benchmark). RedCode alone supplied 315 of the 394 candidate pairs (79.9%) and 106 of the 120 confirmations (88.3%) ([arXiv:2609.10762v1](https://arxiv.org/abs/2609.10762v1)). The authors say the aggregate "should therefore be read as an upper-leaning estimate driven by adversarial and vulnerability-seeded code, not as a direct prediction of how often statically clean code from realistic generation tasks will prove exploitable" ([arXiv:2609.10762v1](https://arxiv.org/abs/2609.10762v1)). 5.4% is the figure closest to ordinary generation work, and quoting the aggregate without that caveat overstates the paper.

## Why it works

A static analyser matches patterns over source it never runs, so a property that exists only during execution gives a rule nothing to match. The paper puts it as "vulnerabilities dependent on adversarial inputs, execution context, or exploit chaining may evade static checks while remaining exploitable in practice", and locates the misses in "semantic properties, randomness quality, cryptographic strength, authorization logic, and resource consumption, that resist syntactic pattern matching" ([arXiv:2609.10762v1](https://arxiv.org/abs/2609.10762v1)). Resource-exhaustion cases "only became apparent during execution", while weak-randomness code "often appeared functionally correct or unsuspicious to security patterns, while violating underlying security assumptions". The confirmed classes follow: uncontrolled resource consumption (CWE-400) at 27 confirmations, weak PRNG (CWE-338) at 15, insufficiently random values (CWE-330) at 14, weak password hashing (CWE-916) at 9.

Do not extend that into a claim that static tools cannot see weak randomness. Bandit ships B311, which reports "Standard pseudo-random generators are not suitable for security/cryptographic purposes" at LOW severity ([PyCQA/bandit 1.8.4](https://github.com/PyCQA/bandit/blob/1.8.4/bandit/blacklists/calls.py)). Zero findings in a class the tool has a rule for is a reason to check the invocation.

## When this backfires

- The code has no adversarial input path. CWE-400 was the largest confirmed class ([arXiv:2609.10762v1](https://arxiv.org/abs/2609.10762v1)), and it needs an attacker who controls input size.
- Your scanner is filtered. `bandit -ll` reports "only issues of a given severity level or higher" ([PyCQA/bandit 1.8.4](https://github.com/PyCQA/bandit/blob/1.8.4/bandit/cli/main.py)), so LOW rules like B311 never fire. The gap you measured is your own flag.
- You read a confirmation as independent, or as severe. One model ran both detection and verification, which the authors flag for "correlated reasoning errors and a degree of self-confirmation", and the confirmed set is "dominated by denial-of-service and weak-randomness weaknesses" that are "among the lower in direct impact" ([arXiv:2609.10762v1](https://arxiv.org/abs/2609.10762v1)).
- The sandbox is too small for the class. In networkless 256 MB containers, 46 inconclusive verdicts "may reflect environmental limits rather than the absence of a vulnerability" ([arXiv:2609.10762v1](https://arxiv.org/abs/2609.10762v1)). A not-triggered verdict is not a clean bill.

## Example

**Before — the composite scan is the merge gate, at MEDIUM and above:**

```yaml
- run: bandit -r src/ -ll
- run: semgrep --config=rules/ --error
# both green, merge
```

`-ll` suppresses every LOW finding, including B311 on weak randomness, and neither tool executes the code.

**After — the filter comes off and the execution-dependent classes get their own check:**

```yaml
- run: bandit -r src/          # no -ll, so B311 and the other LOW rules report
- run: semgrep --config=rules/ --error
- run: pytest tests/security/  # input-size paths for CWE-400
```

## Key Takeaways

- A clean composite scan is one layer of evidence. The study's exploit stage confirmed 83 of the 235 clean files it probed, a 12.69% yield over the whole clean set.
- Take the number from the corpus that matches your work. 5.4% on the curated benchmark is the realistic-generation figure; 33.7% came from adversarial code.
- Check the invocation before you conclude the tool is blind. Bandit has a weak-PRNG rule, and `-ll` hides it.
- Aim any runtime checking at resource consumption, randomness and password hashing first. CWE-400, CWE-338, CWE-330 and CWE-916 carried 65 of the 120 confirmations.

## Related

- [Trusting a Skill Scanner's Verdict as a Security Judgment](skill-scanner-verdict-not-security-judgment.md) — the same green-check error on installable skills rather than on generated code.
- [Model Confidence as Security Verification](model-confidence-as-security-verification.md) — when the unreliable evidence is the model's own confidence instead of a tool's clean output.
- [Artifact-Only Verification Hides Skipped Skill Steps](artifact-only-verification.md) — the general case for measuring what ran, not only what the output looks like.
- [Deterministic Guardrails Around Probabilistic Agents](../../verification/deterministic-guardrails.md) — what a deterministic gate does buy, and where its reach stops.
- [The Security Review Gap in AI-Authored PRs](../../code-review/security-review-gap-in-ai-prs.md) — the human half of the same gate, where reviewer heuristics miss AI-specific CWE clusters.
