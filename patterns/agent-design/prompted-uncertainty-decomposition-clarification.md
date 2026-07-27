---
title: "Prompted Uncertainty Decomposition for Clarification Routing"
term: "Prompted Uncertainty Decomposition"
description: "Elicit action confidence and request uncertainty as two separate prompted scalars so a black-box agent asks the user only when ambiguity lives in the spec rather than the model's own plan."
tags:
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - prompt-based uncertainty decomposition
  - decomposed verbalized confidence for clarification
last_reviewed: 2026-06-21
maturity: emerging
---

# Prompted Uncertainty Decomposition for Clarification Routing

> Elicit action confidence and request uncertainty as two separate prompted scalars so a black-box agent asks the user only when ambiguity lives in the spec.

Use this technique when the agent runs against a closed model API, the action space is not a typed tool schema, and a human is available to answer mid-task — and only then. Outside those conditions the prompted scalars are unreliable enough that the question becomes "did the agent ask because it was uncertain, or because it was overconfident in being uncertain?"

## The routing problem the decomposition solves

Clarification seeking is not a confidence problem; it is a routing problem. The agent must decide between 'act on what I have' and 'ask the user'. A single uncertainty number cannot distinguish the two failure modes that drive each branch: uncertainty about the model's own next action — fixable by tools, reflection, or a stronger model — and uncertainty about user intent, fixable only by asking. Collapsing them gives a router that fires the wrong branch on a routine basis ([Matsnev, arXiv:2606.19559](https://arxiv.org/abs/2606.19559)).

The decomposition replaces one scalar with two prompted scalars per step:

| Scalar | Question to the model | Routes to |
|---|---|---|
| `action_confidence` | "How confident are you that this is the correct next action and arguments?" | Continue, reflect, or escalate to a stronger model — not the user |
| `request_uncertainty` | "How confident are you that the user's request is unambiguous enough to act on?" | Ask the user when this drops below threshold |

Asking gates on the second scalar alone. Low action confidence with high request clarity means the agent is the bottleneck; asking the user buys nothing. High action confidence with low request clarity means the spec is the bottleneck; asking is the only fix.

## Why it works

The mechanism is causal: asking the user is only useful when the missing information is in the user. The decomposition is the cheapest available test for that condition on a black-box API. The same split shows up in interactive coding benchmarks where effective agents separate navigational gaps (resolvable by reading code) from informational gaps (resolvable only by the user), and the gain comes from routing each gap to the right channel ([Vijayvargiya et al., arXiv:2502.13069](https://arxiv.org/abs/2502.13069)). Matsnev formalizes that split into two prompt-elicited scalars and reports a 73% clarification-F1 improvement over single-signal ReAct+UE on ALFWorld-Clarification across five backbones ([Matsnev, arXiv:2606.19559](https://arxiv.org/abs/2606.19559)).

The deployment shape makes production use practical: no logprobs, no multi-sampling, no fine-tuning, no extra inference call. That keeps it compatible with closed chat APIs and inside the per-turn latency budget — the constraint set under which most prior uncertainty-estimation work is unusable ([Matsnev, arXiv:2606.19559](https://arxiv.org/abs/2606.19559)).

## When this backfires

The signal is only as trustworthy as the prompt-elicited scalar underneath it, and verbalized confidence has well-documented calibration problems that bound where the decomposition can pay back.

RLHF-tuned production models. Verbalized confidence elicited from instruction-tuned LLMs is systematically overconfident across model families ([Xiong et al., arXiv:2306.13063](https://arxiv.org/abs/2306.13063)), and post-RL miscalibration is severe enough that recovery requires a dedicated calibration restoration step ([survey of black-box calibration, arXiv:2412.12767](https://arxiv.org/pdf/2412.12767)). In that regime both scalars are noise: the agent will either over-ask or under-ask regardless of true ambiguity. Re-calibrate against held-out ambiguous prompts before trusting the threshold.

Typed tool schemas. When the action space is a fixed tool manifest, the structured-uncertainty alternative operates directly over tool parameters using Expected Value of Perfect Information and reports 7-39% higher coverage with 1.5-2.7× fewer clarifications than prompting baselines ([Suri et al., arXiv:2511.08798](https://arxiv.org/abs/2511.08798)).

Headless or autonomous runs. The decomposition's value is the act of asking. In CI or scheduled sessions there is no human at the other end, so the low-request-clarity branch routes to assumption or halt anyway. A [task-feasibility-awareness](task-feasibility-awareness.md) check on the action-confidence branch is closer to the actual control the run needs.

High question-cost domains. Threshold-based gating has no cost model. When each clarification round is expensive — slow user, paid support agent, batched async loop — pair the threshold with a per-ask budget cap or fold it into a value-of-information gate before deploying.

Irreversible actions. When every action is high-blast-radius, the right control is not uncertainty estimation — it is gating each action behind explicit human confirmation ([deferred permission pattern](deferred-permission-pattern.md)). Spending tokens on a scalar that could itself be wrong adds risk without reducing it.

## Example

A configurable system prompt fragment that elicits both scalars on the same turn the agent proposes a tool call:

```text
After you propose the next tool call, answer two questions on a 0-10 scale.
Output strict JSON: { "action": ..., "args": ..., "action_confidence": N,
"request_uncertainty": N }.

action_confidence: how sure are you that THIS action with THESE arguments is
correct given the current request? Reasons for low confidence: missing
information you could find by exploring, possible errors in your plan,
multiple plausible next actions.

request_uncertainty: how sure are you that the USER REQUEST is unambiguous
enough to act on? Reasons for high uncertainty: missing required fields,
multiple reasonable interpretations, conflicting constraints, terminology
that depends on the user's domain.
```

The router consumes the JSON and dispatches:

| `action_confidence` | `request_uncertainty` | Route |
|---|---|---|
| ≥ 7 | ≤ 3 | Execute |
| < 7 | ≤ 3 | Reflect, re-plan, or escalate model — do not ask |
| ≥ 7 | > 3 | Ask the user a targeted question about the ambiguous field |
| < 7 | > 3 | Explore first (resolve navigational gap), then re-evaluate |

The two-axis table is the load-bearing part. A single-scalar router collapses rows 2 and 3 — the two cases the decomposition exists to distinguish.

## Key Takeaways

- Clarification is a two-way routing problem; one uncertainty scalar cannot route it correctly because action uncertainty and spec uncertainty have different fixes.
- Elicit the two scalars by prompt on the same turn the agent proposes its action — no logprobs, no extra inference, no fine-tuning.
- The technique pays back specifically on black-box APIs with untyped action spaces and a human in the loop; outside those conditions, a structured-uncertainty or feasibility-awareness route dominates.
- Verbalized confidence in RLHF-tuned models is overconfident by default — calibrate the threshold against held-out ambiguous prompts before trusting it.
- Pair the threshold with a per-ask cost term in high-question-cost domains; bare threshold gating has no cost model.

## Related

- [Interactive Clarification for Underspecified Tasks](interactive-clarification-underspecified-tasks.md) — the behavioral pattern this technique signals; that page covers when an agent should ask, this page covers how it decides
- [Task Feasibility Awareness](task-feasibility-awareness.md) — sibling capability that gates on tool availability rather than spec ambiguity; pairs cleanly with low action-confidence routing
- [Assumption Propagation](../anti-patterns/assumption-propagation.md) — the failure mode when the request-uncertainty signal is absent or ignored
- [Agent Pushback Protocol](agent-pushback-protocol.md) — structured agent-initiated clarification on request quality; consumes the same request-uncertainty signal
- [Deferred Permission Pattern](deferred-permission-pattern.md) — the right control when every action is irreversible and uncertainty estimation adds risk without reducing it
