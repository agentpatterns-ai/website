---
title: "Code-Health-Gated LLM Tier Routing"
description: "Use pre-computed code health metrics as a routing signal to assign SE tasks to cheaper model tiers — reserving expensive models for tangled, high-complexity files."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - code quality routing signal
  - code health tier routing
---

# Code-Health-Gated LLM Tier Routing

> Route software engineering tasks to the cheapest model tier whose output passes the same verification gate as the expensive model, using pre-computed code health metrics as the routing signal.

## The Routing Signal

Generic tier routing uses task type (file search vs. implementation vs. architecture) as the assignment signal. Code-health-gated routing uses a different input: the **health of the files the task will modify**, computed before any model call is made.

The hypothesis, proposed in [Madeyski (2026)](https://arxiv.org/abs/2604.07494), is that clean, well-structured files present lower intrinsic task complexity — lighter models can resolve issues in healthy code without quality regression, while tangled files with high coupling and cyclomatic complexity require heavier models.

This is a **research proposal with stated conditions, not measured outcomes**. The evaluation against SWE-bench Lite (300 tasks, 2,700 agent runs) is pending. Apply the design pattern with that caveat.

## Three-Tier Architecture

The framework defines three capability tiers mirroring commercial model families:

| Tier | Model class | Assigned to |
|------|-------------|-------------|
| Light | Haiku-class | High-CodeHealth files — healthy, low coupling |
| Standard | Sonnet-class | Mid-range or ambiguous health signals |
| Heavy | Opus-class | Low-CodeHealth files — high coupling, complexity |

Assignment happens **pre-generation** using features stored in a code health table, not at inference time.

## CodeHealth as a Routing Input

[CodeHealth](https://arxiv.org/abs/2604.07494) is a composite score (1–10) aggregating 25+ sub-factors:

- Cyclomatic complexity
- Coupling between modules
- File size
- Code duplication
- Naming consistency

Approximate thresholds used in the framework:

| Score range | Health category |
|-------------|-----------------|
| 9–10 | Healthy — candidate for light tier |
| 5–8 | Moderate — standard tier |
| 1–4 | Unhealthy — heavy tier |

The routing signal is the score of the **file(s) the patch will touch**, not the codebase average.

## Two Conditions for Cost Savings

Routing only saves cost when both conditions hold:

**Condition 1 — Cost gate**: The light tier's pass rate on routed tasks must exceed the inter-tier cost ratio. For Haiku→Opus at current API pricing, this ratio is approximately 20% — the light model must succeed on at least 20% of assigned tasks to avoid net cost increase.

**Condition 2 — Signal gate**: CodeHealth must discriminate task difficulty with a measurable effect size (p̂ ≥ 0.56). If code health scores do not reliably predict which tier a task needs, routing on them produces no gain.

Both gates must hold before routing pays off. Either condition failing makes the signal not predictive enough to justify routing overhead.

## The Verification Gate

The verification gate — test suite, linter, or type checker — is identical for all tiers. A light-tier output passes only when it meets the same bar as a heavy-tier output would.

```mermaid
graph TD
    A[Task arrives] --> B[Look up CodeHealth score]
    B -->|High: 9–10| C[Light tier model]
    B -->|Mid: 5–8| D[Standard tier model]
    B -->|Low: 1–4| E[Heavy tier model]
    C --> F[Verification gate]
    D --> F
    E --> F
    F -->|Pass| G[Accept output]
    F -->|Fail| H[Escalate to next tier]
    H --> F
```

The gate is deterministic — its output is the same whether the input came from the cheap or expensive model. This design separates the routing decision from the quality judgment.

## Routing Policies

Three routing approaches are described in the proposal:

**Heuristic thresholds** — assign tiers using CodeHealth score ranges directly. Transparent, auditable, no training required; threshold calibration depends on codebase characteristics.

**ML classifier** — train a classifier on code health sub-factors; use SHAP analysis to identify which sub-factors (e.g., cyclomatic complexity alone vs. composite) carry the most predictive weight, reducing instrumentation overhead.

**Perfect-hindsight oracle** — assigns each task retroactively to the cheapest passing tier. A theoretical ceiling used to quantify headroom above heuristic or ML policies.

## Applying the Pattern Without a Composite Score

Without a CodeHealth composite, proxy with a single metric that correlates with task complexity:

- **Cyclomatic complexity** (per function): average > 10 routes to heavy ([McCabe, 1976](https://doi.org/10.1109/TSE.1976.233837))
- **Module coupling** (fan-in/fan-out): high-coupling files route to heavy
- **File churn rate** (git log): frequent modification correlates with instability — route to heavy

The key constraint is unchanged: the verification gate must be deterministic and identical across all tiers.

## Limitations

- **No empirical results yet** — the SWE-bench Lite evaluation is pending; stated cost savings are theoretical conditions
- **Causal direction** — clean code may correlate with simpler specs and better test coverage independently, confounding the health signal as a predictor of model-tier need
- **Pricing sensitivity** — the 20% cost-gate threshold is calibrated to current Haiku/Opus pricing; changes invalidate it
- **Tier-dependent asymmetry** — Madeyski (2026) reports mid-tier models benefit from clean code while frontier models do not; the mechanism is not yet explained

## Example

A CI-integrated routing lookup in Python, using cyclomatic complexity as a proxy when no composite score is available:

```python
import subprocess
import anthropic

def get_complexity(filepath: str) -> float:
    """Return average cyclomatic complexity for a file using radon."""
    result = subprocess.run(
        ["radon", "cc", "-a", "-s", filepath],
        capture_output=True, text=True
    )
    # Parse "Average complexity: B (5.2)" -> 5.2
    for line in result.stdout.splitlines():
        if "Average complexity" in line:
            return float(line.split("(")[-1].rstrip(")"))
    return 1.0

def route_model(filepath: str) -> str:
    complexity = get_complexity(filepath)
    if complexity > 10:
        return "claude-opus-4-5"      # heavy tier
    elif complexity > 5:
        return "claude-sonnet-4-5"    # standard tier
    else:
        return "claude-haiku-4-5"     # light tier

# Usage: route the task before generating
model = route_model("src/billing/invoice.py")
client = anthropic.Anthropic()
response = client.messages.create(
    model=model,
    max_tokens=2048,
    messages=[{"role": "user", "content": task_prompt}]
)
```

The verification gate (test suite, linter) runs identically regardless of which model produced the patch.

## Key Takeaways

- Use file-level code health scores, pre-computed before generation, as a routing signal to assign SE tasks to cheaper model tiers
- Two conditions must hold: the light tier's pass rate must exceed the inter-tier cost ratio, and CodeHealth must show a measurable effect size (p̂ ≥ 0.56) on task difficulty
- The verification gate must be deterministic and identical for all tiers — this is the design constraint that makes tier equivalence measurable
- If no composite score is available, proxy with cyclomatic complexity or coupling as a simpler routing heuristic
- This is a research proposal (Madeyski, 2026) with pending empirical validation — treat stated cost savings as theoretical conditions, not measured outcomes

## Related

- [Cost-Aware Agent Design](cost-aware-agent-design.md) — generic task-to-tier routing by task type (exploration, implementation, architecture)
- [Heuristic-Based Effort Scaling](heuristic-effort-scaling.md) — effort scaling via prompt-encoded complexity tiers
- [Cross-Vendor Competitive Routing](cross-vendor-competitive-routing.md) — competitive routing across vendor agents for the same task
- [Agent Backpressure: Automated Feedback for Self-Correction](agent-backpressure.md) — using deterministic tooling (tests, linters) as self-correction feedback
- [Reasoning Budget Allocation](reasoning-budget-allocation.md) — allocating reasoning compute proportionally across agent phases
- [Evaluator-Optimizer Pattern](evaluator-optimizer.md) — generator-evaluator loop as a quality control mechanism
- [Verification-Centric Development](../workflows/verification-centric-development.md) — making verification the organizing principle of agent workflows
