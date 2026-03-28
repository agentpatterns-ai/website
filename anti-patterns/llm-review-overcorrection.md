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

A review agent that operates as the sole authority will block correct code from merging. The downstream effects:

- Engineers learn to dismiss LLM review comments as noise, defeating the purpose of automated review
- Real defects get buried in a high volume of false positives
- Review latency increases as engineers spend time refuting valid-code rejections

## Fix-Guided Verification Filter

The research proposes a countermeasure: when the LLM flags code as non-compliant, treat its proposed fix as an executable counterfactual. Run both the original code and the proposed fix against the test suite:

- If both pass: the original code was likely correct; the LLM found a style difference, not a defect
- If original fails, fix passes: the flag is substantiated; proceed with the review finding
- If both fail: the LLM's proposed fix is wrong; do not accept the review verdict without human examination

This filter converts the model's "problem finding" bias into a falsifiable test. It requires that proposed fixes are executable — review prompts must elicit code-level fixes, not prose descriptions.

## Mitigations

- **Never use LLM review as sole authority**: all verdicts require either human confirmation or execution-based validation
- **Apply the fix-guided verification filter**: run original and proposed fix against tests before acting on any flag
- **Avoid explanation-requiring prompts** when the goal is a binary pass/fail verdict; binary prompts produce fewer false positives than explanation prompts
- **Track false positive rate**: if the LLM flags more than a threshold percentage of code that humans subsequently approve, treat the reviewer as miscalibrated

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
