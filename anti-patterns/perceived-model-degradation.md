---
title: "Perceived Model Degradation: Why Vibes Are Not Evals"
description: "Why teams report LLM quality declining over time, five competing explanations, and how to replace gut feel with version pinning and eval suites."
tags:
  - cost-performance
  - testing-verification
aliases:
  - "vibes vs evals"
  - "LLM drift perception"
---

# Perceived Model Degradation

> "The model is getting dumber" — the recurring complaint after every major release. The real problem is not that models degrade; it is that teams have no way to tell whether they actually did.

## The Pattern

Within weeks of any model release, user forums fill with reports that quality has declined. The complaints are persistent, cross-provider, and structurally identical every time.

The anti-pattern is not the degradation itself — some may be real. The problem is that teams cannot distinguish genuine regression from perception bias, so they either panic-switch models without evidence or dismiss real problems as "just vibes."

## Why It Happens

Plausible causes include post-training adjustments (providers iterate on deployed models without announcing changes), confirmation bias (users selectively notice failures as novelty wears off — consistent with OpenAI VP Peter Welinder's [statement](https://twitter.com/npew/status/1681578562419056641)), A/B routing, and weight quantization `[unverified]`. None has definitive proof. Without your own measurements, you cannot act on any.

A key distinction: **LLM drift** (behavioral changes over time) is not the same as **degradation** (inability to solve previously solvable problems). Chen, Zaharia, and Zou ([2023](https://arxiv.org/abs/2307.09009)) documented GPT-4 accuracy dropping from 84% to 51% on prime identification — but critics noted this measured a preference shift, not a reasoning decline `[unverified]`.

## What to Do Instead

### Pin model versions

Anthropic's [model versioning guidance](https://docs.anthropic.com/en/docs/about-claude/models) recommends pinning to a specific dated snapshot in production. Alias endpoints (`claude-sonnet-4`, `gpt-4o`) follow the latest snapshot — treat every version change as a potential breaking change.

### Build golden-query eval suites

Maintain task-specific prompts with known-good expected outputs. Run them on every model version change and on a schedule. See [Golden Query Pairs](../verification/golden-query-pairs-regression.md) for implementation details.

### Use statistical tests, not eyeballing

A 2025 paper proposes [McNemar's test adapted for LLMs](https://arxiv.org/html/2602.10144) to distinguish genuine degradation from statistical noise, detecting drops as small as 0.3%.

### Separate capability evals from regression evals

Anthropic's eval framework distinguishes two types `[unverified]`:

- **Capability evals** target tasks the agent struggles with (low initial pass rate) — these track improvement
- **Regression evals** maintain a near-100% baseline — these detect degradation

A drop on a regression eval is a signal. A drop on a capability eval may just be noise.

## Decision Checklist

Before reacting to perceived degradation:

- [ ] Are you using a pinned model version or a floating alias?
- [ ] Do you have eval results from before and after the perceived change?
- [ ] Is the sample size large enough for statistical significance?
- [ ] Have you controlled for prompt changes, context changes, and tool changes on your side?
- [ ] Can you reproduce the degradation on a specific, repeatable test case?

If you cannot answer yes to at least three of these, you are operating on vibes.

## Example

A team using the `claude-opus-4` floating alias notices their summarization quality “feels worse” after a model update. Without pinned versions or evals, they can’t confirm whether a real regression occurred.

**Before (vibes-driven reaction):**

```
# No pinning, no evals
client = Anthropic()
response = client.messages.create(
    model="claude-opus-4",  # floating alias — silently changes on every release
    ...
)
# "Quality seems worse this week" → team debates switching to GPT-4o
```

**After (evidence-driven response):**

```python
# Pin to a specific snapshot
model = "claude-opus-4-20250514"

# Run regression eval suite on every deploy
def run_regression_evals(model: str) -> dict:
    results = {}
    for prompt, expected in GOLDEN_QUERIES.items():
        response = client.messages.create(model=model, messages=[{"role": "user", "content": prompt}])
        results[prompt] = score(response.content[0].text, expected)
    pass_rate = sum(results.values()) / len(results)
    assert pass_rate >= 0.95, f"Regression detected: {pass_rate:.1%} pass rate (threshold: 95%)"
    return results
```

When the team suspects degradation, they run the eval suite against the pinned version and the previous snapshot. If the pass rate drops below 95%, they have evidence. If not, the complaint is perception bias.

## Related

- [Golden Query Pairs as Continuous Regression Tests](../verification/golden-query-pairs-regression.md)
- [Eval-Driven Development](../workflows/eval-driven-development.md)
- [Trust Without Verify](trust-without-verify.md)
- [Demo-to-Production Gap](demo-to-production-gap.md)
- [The Anthropomorphized Agent](anthropomorphized-agent.md) — misattributing context overload to agent fatigue rather than session state
