---
title: "Fleet-Level Irreversibility Budgets for Agent Effects"
term: "Irreversibility Budget"
description: "A shared account of residual risk that a runtime charges before each irreversible effect commits, and the fleet size below which it buys you nothing."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - fleet-level irreversibility budget
  - cross-agent admission control
  - residual-loss budget
last_reviewed: 2026-09-04
maturity: emerging
---

# Fleet-Level Irreversibility Budgets for Agent Effects

> An irreversibility budget denies the effect that would tip a whole fleet past its risk limit, which no per-action gate can see.

An irreversibility budget is a running balance of residual loss that a runtime keeps per principal and charges before an effect leaves the process. Each effect is priced at the loss left over "after available compensation, recovery, and revocation have been applied". The charge lands on every ledger along the path from the agent to its workflow to the tenant, and the next effect is denied once any of those balances would pass its allocation ([Mohammadi and Bindschaedler, 2026, arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)). Three conditions decide whether it is worth building, and the first rules most fleets out.

## When this applies

The numbers below come from a discrete-event simulation of a fifty-agent procurement fleet, 300 runs per arm, rather than from a deployed system.

### Fleet size

Local per-call caps plus per-agent rate limits are "safe at ten agents". They overdraw a $250k tolerance by 2.4x at fifty agents, 9.7x at two hundred, and 48x at a thousand, because aggregate demand scales while every agent stays individually compliant ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)). Below roughly ten concurrent actors, tighten the per-agent cap and skip the ledger.

### Effects that differ in what they cost you

Pricing by residual loss rather than face value is what buys back throughput. The typed ledger executes 1.8x the value of a face-value cap and 1.7x the strongest pooled cap, and that gain shrinks to 1.2x "as effect classes converge" ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)). If a reverted commit and a customer email cost you the same, a flat cap gets most of that for none of the pricing work.

### A trigger the fleet shares

Across 38,452 public trajectories from tau-bench and AgentDojo, "which external effect fires is task-determined rather than agent-specific". A single planted prompt injection "propagates the same external effect across 84% of a heterogeneous fleet on average (minimum 48%)" ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)). Agents watching one queue, one alert, or one poisoned document are the case this targets.

## What the runtime charges

Three properties do the work, and dropping any one loses the bound.

The charge lands before the effect commits. A circuit breaker that halts the fleet once observed loss reaches the limit still ends at 1.03x tolerance with instant observation, and 2.2x at a fifty-tick lag ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)).

The charge attaches to exposure rather than to call count. Splitting one $1.5M action into many sub-cap ones reaches 3.9x tolerance past local gates; the ledger admits $459k of it "however finely the attacker splits it" ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)).

The runtime assigns the effect type rather than reading one from the caller: "A compromised workflow can therefore propose a final transfer, but it cannot declare that transfer refundable, because it never supplies the label." What the registry cannot resolve is charged at the most expensive matching class ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)).

## Why it works

A per-effect gate is a predicate over one effect, and the quantity you care about is a sum over effects. Tuning the local check never recovers the global one, which the paper puts in a line: "no per-call gate can see the running sum, so none can deny the marginal purchase that tips the fleet over" ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)). That is a different question from the one a [permission check](capability-declarations-for-agent-actions.md) answers. Access control decides whether an action is allowed; the budget denies an allowed action because the aggregate would overdraw.

Keeping the sum is cheap: reserve-then-confirm across the three-level path costs 2.6 microseconds at the median and 240 bytes per live reservation, measured in memory on one host with no persistence ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)).

## When this backfires

- Your prices are wrong and nothing tells you. Charges set at half the true value overdraw in 32% of runs; charges at four times throttle execution down to 5% of proposed value. Underpricing fails silently and overpricing fails visibly, so charges have to err high ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)).
- Someone lies about an effect type. Misdeclaring colluding transfers as refundable reopens the cap to $1.0M and overdraws in 77% of runs ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)). The registry and its auditors hold the guarantee, not the ledger.
- The shared trigger also depresses recovery. A burst that drops the recovered fraction from 0.75 to 0.25 makes additive charging overdraw in 59% of runs "while the ledger believes itself safe". Detecting it late does not help: a ten-tick lag inside a fifty-tick burst "is no better than no detector at all" ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)).
- The fleet stops instead of overdrawing. A budget equal to tolerance admits 14% of the correlated burst, and doubling the budget reintroduces overdraw in as many as 33% of runs ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)). An independent cumulative-admission protocol reports the same shape: on 500 requests that are each individually valid, it "limits autonomous execution to 2 out of 500 (0.4%)" ([Fernandez, 2026, arXiv:2603.18829v10](https://arxiv.org/abs/2603.18829v10)).
- Your losses have no common unit. Data exposure, availability damage, and reputational harm "resist a common scalar in a way money does not" ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)). Value-at-risk does not rescue that: it "fails to reward diversification, as it is not 'subadditive'" ([Tasche, 2002, arXiv:cond-mat/0203558v3](https://arxiv.org/abs/cond-mat/0203558v3)), so sub-budgets do not sum to a sound parent bound.
- The budget authority spans hosts. "A budget that can be double-spent provides telemetry rather than control", and a hard budget needs coordination on every spend that would violate it ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)).

## Example

The paper's running case is fifty procurement agents. Each "owns one product line and may place supplier orders up to $50k under a per-agent rate limit", against a tenant that "tolerates $250k of unhedged exposure over a trading day" ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)). Purchase value is log-normal with a median near $15k and the recovered fraction averages 0.75, so the runtime charges each order 0.52 times its value, the 95th-percentile residual loss.

On an ordinary day nothing binds. Then a supplier price-spike alert makes buying rational for all fifty at once. Every order still clears its own $50k cap and its rate limit, and the fleet lands at 2.4x the $250k tolerance. The ledger denies the order whose 0.52v charge would cross the balance and settles near 0.48x instead ([arXiv:2609.00275v1](https://arxiv.org/abs/2609.00275v1)).

## Key Takeaways

- Count your concurrent actors first. At ten, per-agent caps already hold; the measured failure starts around fifty.
- The cheap version is one number: what your agents commit together if a single trigger fires them at once. Exceeding what you can absorb is the problem, ledger or no ledger.
- The guarantee covers declared charges, never realized loss. A ledger fed bad prices reports a safety it does not have.
- Set charges conservatively and let the throttling complaints arrive. The opposite error produces no complaints at all.

## Related

- [Per-Run Budget Reservation for Coding Agent Model Calls](per-run-budget-reservation.md) — the same reserve-before-commit shape over dollars, inside one run
- [Agent-Client Admission Control for Agentic Traffic](agent-client-admission-control.md) — throttling against your own quota rather than against risk
- [Rollback-First Design](rollback-first-design.md) — choosing the undo first, which is what sets an effect's residual charge
- [Approval Gate Granularity in Agent Pipelines](approval-gate-granularity.md) — what batching approvals does and does not remove
- [Capability Declarations for Agents That Act on Data](capability-declarations-for-agent-actions.md) — declaring an action's reversibility class where the runtime reads it
