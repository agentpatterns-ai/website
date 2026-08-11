---
title: "Verification Capacity Saturation: Three Levers, One Default"
term: "Verification Capacity Saturation"
description: "When agents generate changes faster than gates can check them, a saturated station admits three levers: add capacity, throttle intake, or lower the bar."
tags:
  - testing-verification
  - workflows
  - tool-agnostic
aliases:
  - verification saturation
  - verification throughput trilemma
  - review capacity saturation
last_reviewed: 2026-08-09
maturity: emerging
status: current
---

# Verification Capacity Saturation: Three Levers, One Default

> A saturated verification station admits exactly three responses, and declining to choose picks the third whenever the gate degrades instead of blocking.

Verification capacity saturation is the state where changes reach a gate faster than the gate clears them, so a queue forms and delivery falls back to the speed of the slowest checker in the chain. Addy Osmani names the response set: scale the verification system, reduce the rate at which agents generate changes, or lower the quality bar, and "from a scaling perspective, we need to be ready to do all of these things" ([Osmani, "Agentic Code Quality", 2026](https://addyo.substack.com/p/agentic-code-quality)). Two conditions decide whether that framing fits your pipeline, and both are cheap to check first.

## Condition one: saturated, not merely congested

Saturation means the arrival rate has passed the service rate, so the backlog grows run over run with no stable ceiling. Below that point queue time is driven by high utilization combined with high variability, and it responds to smaller batches and steadier arrivals with no change in capacity, intake, or standards ([Kingman, 1961](https://doi.org/10.1017/S0305004100036094)). Measure the backlog across several runs before reaching for a lever: a long but stable queue is a batch-size problem, not a capacity problem.

## Condition two: the gate degrades rather than blocks

The claim that picking no lever picks the third only holds where the gate can quietly give way. Human review gives way measurably: defect discovery runs 70 to 90 percent at 200 to 400 lines per sitting and falls off past that, with defect density dropping above 500 lines per hour ([SmartBear](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/)). [PR scope creep](../patterns/anti-patterns/pr-scope-creep-review-bottleneck.md) traces what happens to changesets that cross the threshold. Push more volume at a fixed reviewer and inspection per change shortens on its own. A [deterministic gate](deterministic-guardrails.md) has no such give. When a red check blocks the merge outright, inaction produces diverging cycle time instead of a lower bar, and a team hunting for a quality regression there will find nothing.

## Why it works

The response set is closed because it describes a queue, not a preference. As the arrival-to-service ratio approaches one, waiting time scales with the shrinking gap and the backlog diverges ([Kingman, 1961](https://doi.org/10.1017/S0305004100036094)), and only three things move that ratio back: the service rate, the arrival rate, and the work each item demands. Lowering the quality bar is the third of those, since less work per item is a shorter service time.

Which station saturates follows from the same arithmetic. Agents raise the arrival rate without touching the reviewer's measured service rate, so the ratio crosses one at the human first, which is the [bottleneck migration](../human/bottleneck-migration.md) seen from the queueing side. Because that gate degrades, the queue clears by shortening inspection, and the third lever arrives without anyone choosing it. The field data matches: higher AI adoption correlates with a rise in both delivery throughput and delivery instability, and time saved in creation is reallocated to auditing and verification ([DORA, 2026](https://dora.dev/insights/balancing-ai-tensions/)).

## The three levers

| Lever | What it changes | Unavailable when |
|-------|-----------------|------------------|
| Scale verification | Raises service rate through more automated checks or more reviewers | The added capacity is unreliable, so false rejects convert throughput into rework |
| Throttle generation | Lowers arrival rate so verification catches up | Delivery commitments make a slower change stream unacceptable |
| Lower the quality bar | Cuts work per item so service time falls | Blast radius is wide or the change is hard to reverse |

## Place constraints asymmetrically

Uniform strictness pays for verification you do not need. Osmani's second move is to vary it deliberately: "in some places we might want to give them more freedom as long as we keep tighter constraints in others. By providing tighter constraints where we care the most, we can maximize our throughput without sacrificing quality" ([Osmani, 2026](https://addyo.substack.com/p/agentic-code-quality)). Spread the checks along the loop rather than stacking them at the end, since back-pressure "ideally exists throughout the loop, not as a single review at the very end of all the work" (same source). The stations to spread them across are the ones already in the pipeline: "compilers rejecting invalid code, tests failing, security policies blocking bad practices, CI declining to deploy" (same source). Each cheap filter upstream cuts the volume reaching the expensive station, relieving its ratio without moving any lever globally, and that is what lets you hold human attention for the cases automation cannot settle.

## When this backfires

- Capacity added with model-based reviewers can shrink effective throughput. LLMs frequently misclassify correct code as non-compliant, and prompts requiring explanations and proposed fixes raise the misjudgment rate rather than lowering it ([Jin and Chen, arXiv:2603.00539v1](https://arxiv.org/abs/2603.00539v1)), so rework absorbs the nominal gain.
- Irreversible or high-blast-radius work removes two options. Security fixes, schema migrations, and payment paths cannot lower the bar and cannot defer verification past the merge boundary, which leaves throttling or genuine investment.
- Congestion misread as saturation sends you to the wrong prescription. Reduce batch size and arrival variability before spending on capacity.
- Asymmetric placement without a risk model relaxes constraints on the path that turns out to matter, so the gain is bounded by how well your map of where defects land matches where they actually land.
- Relocating verification past the merge boundary removes the station from the path rather than moving its ratio, so it sits outside the three levers; for reversible changes it is a real option, and calling it a lower bar misreads it. It needs fast detection: Osmani relays a practitioner account of a fully automated code factory run for about four months during which no human looked at the code, which then took painstaking manual debugging to pinpoint the failure ([Osmani, "Software Factories, Light and Dark", 2026](https://addyosmani.com/blog/software-factories/)).

## Example

The curl project hit saturation on inbound security reports. Confirmed vulnerabilities had run north of 15 percent of submissions in earlier years, then fell below 5 percent from 2025 as AI-generated reports flooded in, and Stenberg describes the mental toll the triage load put on the project ([Stenberg, 2026](https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/)).

Read against the three levers, curl chose intake. The response it announced was not added triage capacity, the post separately rejects charging researchers for submissions, and a security project cannot lower the bar. So it cut the arrival rate at the source, ending the bug bounty on 31 January 2026 and removing monetary rewards "in an attempt to remove the incentives for submitting made up lies," while moving intake to GitHub private vulnerability reporting (same source). Being ready to pull all three levers is the posture; having one left is the more common situation.

## Key Takeaways

- Confirm the backlog is growing rather than merely long before treating it as saturation; a stable queue responds to smaller batches instead.
- The three levers are closed for a saturated station because they exhaust the ways to restore a stable arrival-to-service ratio.
- Soft gates default to the third lever silently; deterministic gates stall instead, so the symptom you look for depends on which kind you run.
- Adding model-based review capacity can raise nominal throughput while false rejects consume the gain.
- Asymmetric constraint placement buys capacity where it matters, and its payoff is bounded by the accuracy of your risk map.

## Related

- [Verification Capacity as the Agent Quality Ceiling](verification-capacity-quality-ceiling.md) — the standing framing this page specializes: that page treats capacity as the thing setting the ceiling, this one starts once the ceiling has been hit and the question is which lever to pull
- [Agent Backpressure: Automated Feedback for Self-Correction](../patterns/agent-design/agent-backpressure.md) — where verification signals come from, before throughput becomes the constraint
- [WIP=1 and Little's Law: Kanban Throughput Theory for Agent Task Design](../patterns/agent-design/wip-1-littles-law-agent-throughput.md) — the queueing identity applied to a single agent's task stream
- [The Software Factory Model: Industrializing Agent Loops](../workflows/software-factory-model.md) — the production model whose review gate is the station that saturates
- [Audit-Budget Allocation for Agent Fleets](audit-budget-allocation-agent-fleets.md) — how to order the review queue once capacity is genuinely fixed
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the gate type that blocks rather than degrades under load
