---
title: "LLM Code Review Overcorrection for AI Agent Development"
description: "LLMs systematically flag correct code as non-compliant; more detailed review prompts make the misclassification rate worse, not better. arXiv:2603.00539"
aliases:
  - "code review false positives"
  - "fix-guided verification filter"
tags:
  - agent-design
  - testing-verification
---

# LLM Code Review Overcorrection

> LLMs systematically flag correct code as non-compliant; more detailed review prompts make the misclassification rate worse, not better.

## The Problem

[arXiv:2603.00539](https://arxiv.org/abs/2603.00539) documents a systematic failure mode in LLM-based code review: overcorrection. LLMs consistently misclassify correct implementations as non-compliant with requirements. The misclassification is not random noise — it is a directional bias toward finding problems.

Counterintuitively, prompts that require the model to explain its reasoning and propose corrections produce *higher* misjudgement rates than simpler prompts. The added detail amplifies the problem rather than improving reliability.

## The Risk in Review Pipelines

A review agent operating as sole authority blocks correct code from merging. The downstream effects: engineers dismiss LLM comments as noise, real defects get buried in false positives, and review latency increases as developers refute valid-code rejections.

## Why LLMs Overcorrect

The [arXiv:2603.00539](https://arxiv.org/abs/2603.00539) authors' taxonomy of false rejections shows four categories account for 87.2% of cases: Logic Error (48.2%), Added Requirement (14.1%), Boundary Error (13.2%), and Misread Specification (11.7%). These are semantic failures — models construct plausible critiques without falsifiable counterexamples.

The mechanism behind each category is the same: when a model must explain its verdict and propose a correction, it rationalizes rejection through invented problems rather than applying balanced judgment. Hallucinated constraints drive the "Added Requirement" class — the model introduces requirements absent from the specification. Unverified logic-error claims drive the "Logic Error" class — the model asserts failure modes without a falsifiable counterexample. "Boundary Error" and "Misread Specification" reflect a stricter interpretation of the requirement, against which the literal spec then fails.

Explanation-requiring prompts amplify this: forcing a reasoning chain before the verdict locks the model into its initial misread. Generating a critique becomes the path of least resistance; the rationale anchors the verdict toward rejection, and each subsequent reasoning step compounds the error rather than reconsidering the premise. Binary prompts avoid this commitment.

## Fix-Guided Verification Filter

The research proposes a countermeasure: treat the LLM's proposed fix as an executable counterfactual. Run both the original and the fix against the test suite:

- Both pass: the LLM found a style difference, not a defect — do not block
- Original fails, fix passes: flag substantiated — accept the finding
- Both fail: fix is also broken — escalate to human review

This filter converts the bias into a falsifiable test. It requires that proposed fixes are executable — review prompts must elicit code-level fixes, not prose descriptions.

## Mitigations

- **Never use LLM review as sole authority**: all verdicts require either human confirmation or execution-based validation
- **Apply the fix-guided verification filter**: run original and proposed fix against tests before acting on any flag
- **Avoid explanation-requiring prompts** when the goal is a binary pass/fail verdict; binary prompts produce fewer false positives than explanation prompts
- **Track false positive rate**: if the LLM flags more than a threshold of code that humans subsequently approve, treat the reviewer as miscalibrated

## Example

The fix-guided verification filter can be applied in a CI pipeline. When the review agent flags code as non-compliant, both the original and the proposed fix are executed against the test suite before any action is taken.

```python
# review_filter.py
import subprocess

def run_tests(code_path: str) -> bool:
    result = subprocess.run(
        ["pytest", code_path, "--tb=no", "-q"],
        capture_output=True
    )
    return result.returncode == 0

def apply_fix_guided_filter(original_path: str, fix_path: str) -> str:
    original_passes = run_tests(original_path)
    fix_passes = run_tests(fix_path)

    if original_passes and fix_passes:
        return "false_positive"   # style difference only; do not block merge
    if not original_passes and fix_passes:
        return "substantiated"    # defect confirmed; accept the review finding
    return "inconclusive"         # fix is also broken; escalate to human reviewer
```

A verdict of `"false_positive"` means the model found a stylistic difference, not a defect — the original code should not be blocked. Only a `"substantiated"` result justifies acting on the LLM's flag.

## When This Backfires

The fix-guided verification filter depends on executable tests. Without a test suite, both branches of the counterfactual are unverifiable and the filter cannot distinguish false positives from real defects. Specific failure conditions:

- **No test suite / no test coverage**: the filter requires that tests exist and run against the submitted code; a codebase with low or missing test coverage cannot use execution as evidence
- **Non-deterministic tests**: flaky tests produce inconsistent pass/fail results for the same code, making the original-vs-fix comparison unreliable
- **Sparse coverage**: both original and fix pass regardless of correctness; `false_positive` verdicts become unreliable
- **Style-only codebases**: if the team's review bar is stylistic rather than functional, LLM review may still flag genuine style regressions that tests never catch; the filter will classify these as false positives and suppress valid signals
- **Prose-only fixes**: natural language corrections are not runnable; review prompts must elicit code-level fixes
- **Large test suites**: two suite executions per flag adds latency that may outweigh the benefit for low-severity findings

Without automated tests, fall back to binary pass/fail prompts and require human confirmation for all flags.

## Key Takeaways

- LLM overcorrection is systematic and directional — models bias toward flagging, not toward accuracy
- More detailed review prompts increase misjudgement rates; explanation generation reinforces the wrong initial verdict
- The fix-guided verification filter uses execution as evidence to validate or refute a review flag
- LLM reviewers must never be sole authority; all verdicts need human confirmation or execution validation

## Related

- [Agent-Assisted Code Review](../code-review/agent-assisted-code-review.md)
- [Trust Without Verify](trust-without-verify.md)
- [Agentic Code Review Architecture](../code-review/agentic-code-review-architecture.md)
- [Committee Review Pattern](../code-review/committee-review-pattern.md)
- [Law of Triviality in AI PRs](law-of-triviality-ai-prs.md)
- [Yes-Man Agent](yes-man-agent.md)
- [PR Scope Creep and Review Bottleneck](pr-scope-creep-review-bottleneck.md)
