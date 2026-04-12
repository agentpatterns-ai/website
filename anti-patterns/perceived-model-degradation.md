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

After every model release, user forums fill with reports that quality has declined — persistent, cross-provider, and structurally identical each time. The anti-pattern is not the degradation itself (some is real); it is the inability to tell the difference, causing teams to either panic-switch without evidence or dismiss real problems as vibes.

## Why It Happens

Candidate causes: post-training adjustments, confirmation bias (consistent with OpenAI VP Peter Welinder's [statement](https://twitter.com/npew/status/1681578562419056641)), A/B routing, and weight quantization. None has definitive proof.

**LLM drift** (behavioral change over time) differs from **degradation** (inability to solve previously solvable tasks). Chen, Zaharia, and Zou ([2023](https://arxiv.org/abs/2307.09009)) documented GPT-4 prime-identification accuracy dropping from 84% to 51% — the drop coincided with reduced chain-of-thought compliance, making root cause difficult to isolate.

## What to Do Instead

### Pin model versions

Per Anthropic's [model versioning guidance](https://docs.anthropic.com/en/docs/about-claude/models), pin to a specific dated snapshot in production. Alias endpoints (`claude-sonnet-4`, `gpt-4o`) silently follow the latest snapshot — treat each version change as a potential breaking change.

### Build golden-query eval suites

Maintain task-specific prompts with known-good outputs; run on every version change and on a schedule. See [Golden Query Pairs](../verification/golden-query-pairs-regression.md) for implementation.

### Use statistical tests, not eyeballing

[McNemar's test adapted for LLMs](https://arxiv.org/html/2602.10144) distinguishes genuine degradation from noise, detecting drops as small as 0.3%.

### Separate capability evals from regression evals

- **Capability evals** — low initial pass rate, track improvement
- **Regression evals** — near-100% baseline, detect degradation

A regression eval drop is a signal. A capability eval drop may be noise.

## Decision Checklist

Before reacting to perceived degradation:

- [ ] Using a pinned model version, not a floating alias?
- [ ] Eval results from before and after the perceived change?
- [ ] Sample size sufficient for statistical significance?
- [ ] Controlled for prompt, context, and tool changes on your side?
- [ ] Reproducible on a specific, repeatable test case?

Fewer than three "yes" answers means you are operating on vibes.

## Why It Works

Novel models get credit for wins; routine ones get blamed for failures. Eval suites substitute systematic sampling for selective memory — identical prompts against the same rubric produce a signal independent of observer bias. Pinned snapshots isolate change attribution: any observed difference originated in your code, prompts, or data, not a silent upstream update.

## When This Backfires

1. **Evals lag real usage.** Suites reflect the authoring-time distribution; shifted user behavior means a passing eval masks degradation on the live workload.
2. **Pinning delays improvements.** Pinning foregoes bug fixes and upgrades. Providers deprecate old snapshots; teams without a rotation policy face forced migrations with no baseline.
3. **Underpowered tests miss real regressions.** McNemar's test requires sufficient paired samples; sparse traffic or narrow suites cannot detect small but real drops.

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
