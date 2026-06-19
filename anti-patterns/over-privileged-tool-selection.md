---
title: "Trusting Model-Level Privilege Restraint at Tool Selection"
term: "Over-Privileged Tool Selection"
description: "Mainstream LLM agents pick higher-privilege tools when a lower-privilege variant suffices; transient failures push the rate higher, and general safety alignment does not reliably hold the line."
aliases:
  - over-privileged tool selection
  - privilege-blind tool selection
  - model-side privilege restraint
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-19
maturity: emerging
status: current
---

# Trusting Model-Level Privilege Restraint at Tool Selection

> Agents pick higher-privilege tools at selection time when lower-privilege variants suffice — 32-65% on open models — and transient failures push it higher.

## The Anti-Pattern

Provisioning one tool per capability and trusting the model to "use it sensibly" leaves privilege selection to a prior the model was never trained to maintain. ToolPrivBench measures **Over-Privileged Tool Use Rate (OPUR)** across 544 scenarios in eight domains where each task is solvable by *either* a standard or a higher-privilege variant. Qwen3-8B picks the higher-privilege tool **64.9%** of the time; LLaMA-3.1-8B **55.9%**; DeepSeek-v3.2 **31.8%**. Only Claude 4.6 Sonnet drops to **~2.6%**, and that is the outlier, not the deployment-default behaviour for mid-tier or open-weight stacks ([Yang et al., 2026](https://arxiv.org/abs/2606.20023)).

The failure repeats across five recurring shapes — Authority Escalation, Safety Bypass, Scope Expansion, Data Over-Exposure, Temporal Persistence — each accounting for **16-26%** of observations ([Yang et al., 2026](https://arxiv.org/abs/2606.20023)). Independent corroboration: GrantBox runs agents against real-world tool integrations and measures an **84.80% attack success rate** for privilege misuse under prompt-injection conditions ([GrantBox, 2026](https://arxiv.org/abs/2603.28166)) — agents do not exercise restraint on production tools even when low-privilege paths exist.

## Why It Works

The mechanism is a **selection prior under reasoning-tax pressure**. Tools advertising broader capability score higher on "solves the request" because their descriptions cover a larger envelope; the model picks whichever description anchors most strongly. General safety RLHF tunes refusal of unsafe *requests*, not selection between two *legal* tools with different blast radii ([Yang et al., 2026](https://arxiv.org/abs/2606.20023)).

Transient failures amplify the rate. After a tool returns an error, the agent enters corrective-reasoning mode and reaches for a variant that "cannot fail" — the highest-privilege one — by the same dynamic that makes [error frames a trusted authority channel](tool-error-implicit-authority.md). Privilege-aware SFT+RL post-training pulls Qwen3-8B from 64.9% → **27.0%** and Qwen3-4B-Think to **18.9%**, but does not eliminate it ([Yang et al., 2026](https://arxiv.org/abs/2606.20023)) — a learnable selection bias, not a missing capability.

## Example

**Before — one tool per capability, model picks freely:**

```yaml
# Tool catalog: capability covered once, broadest variant
tools:
  - name: query_db                   # holds read+write+admin
    permissions: [select, insert, update, delete, grant]
```

A read-only intent ("show last week's orders") goes to `query_db`; on a transient timeout the agent retries the same tool, holding admin scope for the entire trajectory. The harness logs one `query_db` call; nothing on the trace says the actual operation was a `SELECT`.

**After — tiered variants and an explicit escalation gate:**

```yaml
tools:
  - name: query_db_read              # SELECT only
    permissions: [select]
  - name: query_db_write             # add INSERT/UPDATE
    permissions: [select, insert, update]
  - name: query_db_admin             # full set; requires escalation token
    permissions: [select, insert, update, delete, grant]
    requires_escalation: true

# Harness rule: escalation_token only minted after explicit user confirmation
# OR a deterministic classifier ruling the lower tiers insufficient.
```

The model still chooses, but the catalog forces a sufficient-low-privilege option to exist for read intents; the admin tier is gated by something outside the model's selection prior. This is [permission-framework-over-model](../security/permission-framework-over-model.md) applied at the tool-catalog layer.

## When This Backfires

The corrective discipline — tier every capability, gate every escalation — is over-engineering in four cases:

- **Frontier-tier model on a low-blast-radius path.** Claude 4.6 Sonnet's ~2.6% OPUR plus a sandboxed runner makes tiered variants almost pure maintenance overhead ([Yang et al., 2026](https://arxiv.org/abs/2606.20023)).
- **Tools without a meaningful low-privilege twin.** An irreducibly admin-only API gains nothing from a synthetic "try low first" preamble — every call routes to the high tier anyway, with one guaranteed failure prepended.
- **Ephemeral, credential-free runners.** A throwaway container destroyed after the task already bounds the blast radius by environment; layering tiered tools duplicates [blast-radius-containment](../security/blast-radius-containment.md) without adding signal.
- **No transient-failure surface.** Idempotent tools that hard-fail with no recoverable error stream remove the post-failure escalation amplifier — the dominant lift the paper measures vanishes.

The pattern is load-bearing when the deployment uses a mid-tier or open-weight model, the tool catalog spans tiers with real blast-radius differences, and the trajectory includes recoverable errors.

## Key Takeaways

- Across mainstream open models, agents select higher-privilege tools 32-65% of the time when a sufficient lower-privilege alternative exists; only frontier-tier RLHF reliably pulls the rate near zero ([Yang et al., 2026](https://arxiv.org/abs/2606.20023)).
- The fix is structural: tiered tool variants per capability plus an explicit escalation gate outside the model's selection prior — not "tell the agent to prefer low privilege" in the system prompt ([GrantBox, 2026](https://arxiv.org/abs/2603.28166)).
- Privilege-aware SFT+RL reduces but does not eliminate the rate; treat it as a complement to harness-layer gating, not a replacement.

## Related

- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md) — the runtime-layer enforcement this anti-pattern shows the model cannot substitute for.
- [Permission Framework Over Model](../security/permission-framework-over-model.md) — the constructive complement: privilege decisions belong outside the model.
- [Trusting Tool Error Messages as Implicit Authority (Error-Path Injection)](tool-error-implicit-authority.md) — the corrective-reasoning mechanism that amplifies escalation after transient failures.
- [Prompt-Only Tool Access Control](prompt-only-tool-access-control.md) — adjacent failure: relying on prompt rules to enforce tool boundaries rather than harness-level deny rules.
- [Action-Selector Pattern](../security/action-selector-pattern.md) — architectural defence that eliminates the selection surface where the catalog allows it.
