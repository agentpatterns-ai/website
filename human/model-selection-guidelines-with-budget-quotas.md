---
title: "Model Selection Guidelines with Budget Quotas"
term: "Guideline-and-Quota Model Governance"
description: "A central team publishes task-to-model guidelines and admin settings cap spend per department and person, so the engineer still chooses and the budget stays bounded."
tags:
  - human-factors
  - tool-agnostic
  - cost-performance
  - model-routing
aliases:
  - guideline-plus-quota model governance
  - administrative model budget caps
  - task-to-model selection guidelines
  - per-department AI usage limits
last_reviewed: 2026-10-12
maturity: emerging
---

# Model Selection Guidelines with Budget Quotas

> Publish task-to-model selection guidelines, bound spend with administrative quotas per department and person, and leave the per-task choice with each engineer.

Reach for this when your constraint is budget predictability and adoption rather than per-task optimality. It needs no routing code, so a team whose only instrumentation is a billing console can run it. It bounds what you spend; it tells you nothing about cost per completed task, because nothing in the arrangement measures that.

## How the guideline and the quota divide the work

A central team tests the models and publishes which tier suits which work. LegalOn Technologies gave that job to an internal AI-powered Development CoE: "AID CoE tested and monitored models, while managers shared its findings with their teams. This enabled each engineer to independently choose the most suitable model for each task" ([OpenAI](https://openai.com/index/legalon-halves-codex-costs)). The engineer keeps the decision. The guideline moves only the starting tier, away from "using the highest-capability model for every task" toward starting light and escalating with complexity.

Administrator settings carry the enforcement: "monthly usage limits for departments and individuals", plus budget caps "at the department, group, and individual levels" ([OpenAI](https://openai.com/index/legalon-halves-codex-costs)). LegalOn set those caps unevenly on purpose. "The established LegalOn business was asked to improve cost efficiency by up to approximately 20%, while new businesses in the launch phase received generous budgets to encourage active use of AI." The asymmetry is the part worth copying, because it takes the cut from where extra spend was buying least.

### What the figures do and do not say

The case reports a 65% reduction in estimated daily costs, and two conditions travel with it. It attributes the figure to three changes at once: "Together, model selection, feature restrictions, and budgets tailored to each business reduced estimated daily costs by approximately 65%" ([OpenAI](https://openai.com/index/legalon-halves-codex-costs)). Fast mode was the restricted feature. The same page's summary then credits something else, "A 65% reduction in estimated daily costs compared with GPT-5.5 by choosing among GPT-6 and 6.1 models", which is a model-generation upgrade sitting on top of the governance change. Neither reading isolates the guideline and the quota. The 20% is a target asked of one business unit, not a measured company result.

## Why it works

The cap and the guideline do different jobs, and the split is the mechanism. A platform-enforced budget bounds the aggregate whether or not any single choice was right. On GitHub's equivalent surface, "if any budget with Stop usage when budget limit is reached enabled is exhausted, additional usage is blocked" ([GitHub Docs: Setting up budgets](https://docs.github.com/en/billing/tutorials/set-up-budgets)). Compliance is not load-bearing, so the guideline is free to be advisory. It only has to shift a default.

The T2MO framework treats the arrangement as the first of four routing stages and opens with it: "Stage one is a static policy plus developer guidance matrix with confidence tiers", followed by a shadow-mode classifier, a verified cascade, and a full router ([arXiv:2608.08528v2](https://arxiv.org/abs/2608.08528v2)). You buy spend predictability now and keep the option of [routing inside the system](../patterns/agent-design/routing-break-even.md) later.

## When this backfires

Overlapping caps can block people unexpectedly. GitHub's billing docs advise avoiding overlapping budgets for a product and a SKU, or an organization and a repository, "so that users are not unexpectedly blocked from using a feature that they rely on". The per-user cap has no softer mode: "This option is not available for user-level budgets, which always enforce a hard stop." The per-user cap is also "the first check in the evaluation sequence", so the engineer doing the most valuable work is the one who stops ([GitHub Docs](https://docs.github.com/en/billing/tutorials/set-up-budgets)).

Three further conditions:

- Difficulty that does not track task type. T2MO grades GLM 5.2 in-harness. It passes the easy, medium, and difficult Git Workflow cells at 100%, 100%, and 47%, against 100%, 50%, and 25% on Frontend and UI. The two subcategories "carry near-identical traffic yet reach *opposite* decisions" ([arXiv:2608.08528v2](https://arxiv.org/abs/2608.08528v2)). No readable tier table expresses that.
- Nothing measuring cost per completed task. Starting light moves cost into retries and waiting rather than removing it: "a model with a lower token price can still be more expensive end-to-end if it fails often enough to force retries on a stronger incumbent" ([arXiv:2608.08528v2](https://arxiv.org/abs/2608.08528v2)). Both halves report success while that quantity moves unobserved.
- A stale tier table. The tiering is a snapshot of one vendor's lineup, and each release invalidates part of it. LegalOn's answer was a standing team monitoring usage and adjusting limits, a recurring headcount cost rather than a one-off document.

The strongest case against the pattern is a cascade, which removes the hard problem instead of delegating it. It "removes the need for ex ante difficulty prediction in many categories", because a failed cheap attempt escalates automatically "before the developer notices" ([arXiv:2608.08528v2](https://arxiv.org/abs/2608.08528v2)). Where you have cheap verifiers, build that instead.

## Example

GitHub Copilot under usage-based billing exposes scopes that map onto the three levels LegalOn used. A bundled AI credits budget can be scoped to "the whole enterprise, a single organization, a single cost center, or per user" ([GitHub Docs](https://docs.github.com/en/billing/tutorials/set-up-budgets)). A cost center maps onto a department or group, and a per-user budget onto an individual.

Precedence runs from narrow to broad. A cost center user-level budget "sets one per-user amount for all current and future members, and overrides the universal budget for them", and an individual budget "overrides both the universal budget and any cost center user-level budget for that user". An individual budget can expire at the end of the current billing cycle or on a date you choose. That is how you grant a temporary raise without a permanent one.

To copy LegalOn's asymmetry: set a universal per-user budget as the floor, raise it by cost center for launch-phase teams, and tighten the mature business by its target percentage. All three user-level budgets always hard-stop, but the most specific one wins for each person, so each person meets one stop. A separate cost center budget on metered charges can stay alert-only ([Copilot budgets](https://docs.github.com/en/copilot/concepts/billing-and-usage/organizations-and-enterprises/budgets)).

## Key Takeaways

- Separate the bound from the advice. The quota is enforced by the platform and needs no compliance; the guideline is advisory and only has to move a default starting tier.
- Set budgets unevenly by business stage. A uniform percentage cut takes capacity from the team where extra spend was worth most.
- Expect one user-level hard stop per person. GitHub applies the narrowest user-level budget (individual, then cost center, then universal), and no user-level budget can be made advisory. Cost center and organization budgets can alert without stopping, but they cap only metered charges after the shared pool is gone.
- Instrument cost per completed task before you claim a saving, or escalations absorb it while both the quota and the guideline report progress.
- Treat this as stage one. The next rung predicts the route without acting on it, so you can measure the guideline against a classifier before replacing it.

## Related

- [Routing Break-Even: When a Cheaper Model Actually Pays](../patterns/agent-design/routing-break-even.md) — the in-system version of this decision, priced against the router's own judging cost
- [Progressive Spend Threshold Alerting for Agent Cost Governance](../patterns/agent-design/progressive-spend-threshold-alerting.md) — soft caps with staged alerts, the alert-only half of a budget scope
- [Copilot vs Claude Billing Semantics](copilot-vs-claude-billing-semantics.md) — what a seat buys once both vendors meter tokens, and how their spend-limit scopes compare
- [Rolling Out CLI Coding Agents at Organization Scale](org-scale-cli-agent-rollout.md) — the adoption side of the same problem, and which numbers justify the spend a quota then bounds
- [Auto Model Selection](../patterns/agent-design/auto-model-selection.md) — handing the per-task choice to the harness instead of to a person reading a document
