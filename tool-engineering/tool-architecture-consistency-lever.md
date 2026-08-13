---
title: "Tool Architecture Moves Consistency, Not Resolve Rate"
term: "Tool Architecture"
description: "Reorganizing how an agent's tools are exposed, with capabilities held constant, moves run-to-run consistency while the task resolve rate stays flat."
aliases:
  - tool interface architecture
  - agent tool organization
  - structured low-level tool interfaces
tags:
  - tool-engineering
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-13
maturity: emerging
---

# Tool Architecture Moves Consistency, Not Resolve Rate

> Reorganizing how an agent's tools are exposed moves its run-to-run consistency, while its resolve rate stays about where it was.

Tool architecture is the design dimension covering how an agent's capabilities are organized and exposed to the model, held apart from what those capabilities are. A controlled comparison of six tool architectures on repository-level issue fixing found that the interface changes agent behavior. It ran 11,700 trajectories across three actor models, with the underlying information and actions held similar ([Xu et al., arXiv:2608.11386v1](https://arxiv.org/abs/2608.11386v1)). The variable it changes is not the one most teams measure.

## The measurement that moves

The study reports that "the overall task resolve rate is similar across tool architectures for a given actor model," which the authors expected because the setups were designed to minimize capability differences ([Xu et al., arXiv:2608.11386v1](https://arxiv.org/abs/2608.11386v1)). What separates the architectures is pass^k, the probability that k repeated attempts at the same instance all succeed. Against a bash-only baseline, structured low-level interfaces improved consistency by up to 4.7x.

A team whose dashboard shows pass@1 will rebuild its tool layer and watch nothing move.

## Which of the six generalized

The setups ran over SWE-bench Live with 65 problem instances and 10 rollouts each ([Xu et al., arXiv:2608.11386v1](https://arxiv.org/abs/2608.11386v1)).

| Setup | What it adds to bash | Reported effect |
|---|---|---|
| Atomic | Repository search, bounded file viewing, targeted string replacement, file creation | The only setup with a uniformly positive consistency effect across all three actors |
| Python | Executable Python blocks in place of tool calls | Similar task performance, 41.6% fewer steps, 56.3% lower token usage |
| NLSearch | Natural-language queries returning code snippets | Access to relevant files up more than 11%, at the cost of lower precision |
| HypoTrack | Recording a hypothesis and its confidence | Limited effect on actor behavior |
| Scratchpad | Emitting free-form thinking | Limited effect on actor behavior |
| BashOnly | Nothing; unconstrained shell only | Baseline |

Only Atomic held up everywhere. The paper states that "the remaining setups do not show the same cross-actor regularity," with NLSearch and HypoTrack improving consistency for some actors and reducing it for others ([Xu et al., arXiv:2608.11386v1](https://arxiv.org/abs/2608.11386v1)). Atomic is the only one of the six a team could adopt without measuring first.

## Why it works

Structured low-level tools buy consistency by deleting a class of mistakes the agent makes on the way to the fix, rather than by making it a better engineer. The authors name the route: "a plausible mechanism for Atomic's consistency gains is that it reduces low-level environment-interaction errors." Their three categories are a tool aimed at a nonexistent target, an edit that leaves the program broken, and a malformed shell, sed, or awk invocation. For the weakest actor tested, Atomic cut mis-edit errors from 1.64 to 0.19 per trajectory and wrong-syntax errors from 0.96 to 0.01 ([Xu et al., arXiv:2608.11386v1](https://arxiv.org/abs/2608.11386v1)).

That explains the gradient across models. A tool removes errors in proportion to how often the actor commits them, so the largest pass^k gain landed on the 30-billion-parameter open-weight actor and shrank on the strongest one. The authors bound the claim themselves, noting that the analysis "does not directly test the causal link between environment-interaction errors and task-level inconsistency" ([Xu et al., arXiv:2608.11386v1](https://arxiv.org/abs/2608.11386v1)). Treat it as a well-evidenced correlation with a plausible route.

The efficiency result has a separate and cleaner cause. A Python interface keeps intermediate results in variables and control flow inside the block, so one action expresses what several tool calls expressed before. The paper confirms that "Python does not introduce new action capabilities."

## When this backfires

- Your metric is pass@1 on a frontier model. Resolve rate does not move, and the gain on the strongest actor tested was a fraction of the gain on the weakest. The payoff can sit below the tool layer's maintenance cost.
- A human reviews every diff. Repeat-run consistency pays off in CI, eval gates, and unattended re-runs. Where someone reads each output before it lands, variance is already absorbed.
- You adopt an architecture other than Atomic on the strength of this result. Four of the six setups either failed to generalize across actors or came out close to inert.
- You expected a scratchpad tool to help. Recording intermediate reasoning is cheap to add and was measured here as close to a no-op.
- Capability is the bottleneck. Capabilities were held similar by construction, so reorganizing an interface adds nothing an agent was missing outright.

One counter-position deserves stating plainly. [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) reports over 74% on SWE-bench Verified while having "no tools other than bash." Bash-only clears a high bar, so the argument for structured tooling has to rest on variance rather than on capability.

## Key takeaways

- Name the metric a tool-layer change is meant to move before building it. If the answer is resolve rate, the evidence here does not support the spend.
- Instrument pass^k, or any repeated-attempt statistic, on either side of an interface change. A single-run benchmark cannot see the effect at all.
- Expect a smaller return as your actor model gets stronger, and re-measure after a model upgrade rather than assuming the gain persists.

## Related

- [Agent-Computer Interface (ACI)](agent-computer-interface.md) — the HCI framing this result sits inside, including the earlier finding that interface design moves pass@1
- [Tool Minimalism and High-Level Prompting](tool-minimalism.md) — how many tools to expose, as against how to organize them
- [MCP-vs-CLI Cost Ratios Are a Property of the Scaffolding](mcp-cli-cost-ratio-scaffolding-bound.md) — why a published interface number describes someone else's harness
- [Lexical-First Retrieval for Agentic Search](lexical-first-retrieval-for-agentic-search.md) — relevant to the natural-language search setup and its precision cost
- [Token-Efficient Tool Design](../token-engineering/token-efficient-tool-design.md) — the per-call output-size lever, distinct from the whole-interface one
