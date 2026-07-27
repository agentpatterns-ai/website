---
title: "LLM Self-Review Failure in Code Modernization Tasks"
term: "LLM Self-Review Failure"
description: "Asking an LLM to verify behavior preservation of its own migration output misses 31.7% of semantic drift cases — independent of model capability."
tags:
  - testing-verification
  - anti-pattern
  - tool-agnostic
  - arxiv
aliases:
  - self-review code modernization
  - articulate but wrong self review
last_reviewed: 2026-06-02
maturity: emerging
---

# LLM Self-Review Failure in Code Modernization Tasks

> LLM self-review of its own code modernization misses ~31.7% of silent semantic drift, and the miss rate does not improve with model capability.

Self-review by the producing model is not a reliable safety check for code modernization. Across 1,980 Python 2→3 attempts on 11 production LLMs, self-review missed 31.7% of behavior-changing outputs. That includes cases where the same model articulated the exact Py2/Py3 semantic distinction that broke the code, then certified it as preserving behavior ([Reddy et al., arXiv:2605.21537](https://arxiv.org/abs/2605.21537)).

## The pattern

Modernization agents typically generate the migrated code, then ask the same model to confirm behavior is preserved. The second step looks like a check, so teams treat it as one. They gate merges on the self-approval and skip behavioral tests when the LLM says the migration is safe. The cost shows up later as silent drift in production.

## Why it fails

The primary study measured drift in 39.7% of attempts on "semantic-trap" snippets — Py2 code where naive modernization changes observable behavior — versus 7.0% on controls. On drift cases, asking the producing model to verify its own output caught only 68.3% ([Reddy et al., arXiv:2605.21537](https://arxiv.org/abs/2605.21537)).

Three findings make this structural, not a model-quality gap:

- Drift rates ranged 5.6%–46.7% across 11 production LLMs and did not correlate with model capability or cost — frontier models failed alongside cheap ones
- The same problematic snippets failed across nearly all models, concentrated on numeric-semantics edges — the difficulty lives in the input, not the model
- Models that correctly explained the Py2/Py3 semantic distinction in chat still approved their own buggy output ([Reddy et al., arXiv:2605.21537](https://arxiv.org/abs/2605.21537))

## Why it works

The mechanism is post-hoc rationalization, not independent reasoning. Once a model has emitted output, asking it to review that output triggers reasoning from the chosen output rather than toward an answer. The chain of thought that produced the buggy translation tends to produce a plausible-sounding justification for it. Huang et al. found the same effect in reasoning tasks: intrinsic self-correction without external feedback can degrade accuracy ([Huang et al., ICLR 2024, arXiv:2310.01798](https://arxiv.org/abs/2310.01798)). Knowing the rule is not the same as applying it to your own output. A separate dispatch — different model, isolated session, or behavioral test — must do the verifying.

## When this backfires

Self-review is not uniformly worthless:

- Mechanical-only changes: pure syntactic migrations sit near the 7.0% control-snippet floor, so the semantic-trap class is essentially empty
- No behavior oracle available: when the target codebase has no runnable tests or executable spec, self-review is the only signal at all — a weak signal beats none, provided downstream code is not treated as verified
- Throwaway or sandbox code: one-off scripts and prototypes where drift cost is bounded, so independent verification is uneconomic

The failure mode is using self-review as the safety check on production migrations, not its existence.

## Example

Before — self-review as the safety check:

```python
def migrate(snippet: str, model) -> str:
    migrated = model.complete(f"Modernize this Py2 code to Py3:\n{snippet}")
    verdict = model.complete(
        f"Does this migration preserve behaviour?\n"
        f"Original:\n{snippet}\nMigrated:\n{migrated}\n"
        f"Answer yes or no."
    )
    if "yes" in verdict.lower():
        return migrated  # silent drift ships when verdict is wrong
    raise ValueError("Self-review rejected migration")
```

The same model that produced `migrated` certifies it. On semantic-trap snippets this misses 31.7% of drift cases ([Reddy et al., arXiv:2605.21537](https://arxiv.org/abs/2605.21537)).

After — independent verifier plus behavioral test:

```python
def migrate(snippet: str, producer, reviewer, oracle_tests) -> str:
    migrated = producer.complete(f"Modernize this Py2 code to Py3:\n{snippet}")
    # 1. Different model reviews — no access to producer's chain of thought
    verdict = reviewer.complete(
        f"Compare semantics. Flag any observable behaviour change.\n"
        f"Original:\n{snippet}\nMigrated:\n{migrated}"
    )
    # 2. Behavioural oracle — run both against the same inputs
    if not oracle_tests.behaviour_matches(snippet, migrated):
        raise ValueError("Behavioural drift detected")
    if "flag" in verdict.lower():
        raise ValueError(f"Reviewer flagged: {verdict}")
    return migrated
```

The reviewer is a separate principal — different model or, at minimum, a fresh session with no access to the producer's reasoning. The oracle is the load-bearing check; the second LLM is a cheap filter. Capability gains do not substitute for either ([Reddy et al., arXiv:2605.21537](https://arxiv.org/abs/2605.21537)).

## Key Takeaways

- Self-review by the producing model misses ~31.7% of semantic drift during code modernization and the miss rate is independent of model capability or cost
- The failure is structural — a model that can articulate the relevant semantic rule still approves its own violation of it
- Mitigate with two independent signals: a different reviewer (different model or isolated session) and a behavioral oracle (tests or executable spec); both are needed
- Frontier models do not fix this — capability investments do not substitute for independent verification

## Related

- [LLM Code Review Overcorrection](llm-review-overcorrection.md) — the complementary failure: detailed-prompt LLM review produces false *positives* on third-party code; self-review here produces false *negatives* on own output
- [Trust Without Verify](trust-without-verify.md) — the general anti-pattern of accepting polished agent output without independent checks
- [The Test Homogenization Trap](test-homogenization-trap.md) — why LLM-generated tests share the same blind spots as the LLM-generated code they cover
- [Prior Dominance Over Feedback](prior-dominance-over-feedback.md) — why feedback loops amplify the original output instead of correcting it
- [Documentation-Guided Legacy Migration](../../workflows/documentation-guided-legacy-migration.md) — workflow that pairs migration with an external behavioral oracle
