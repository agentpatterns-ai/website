---
title: "Choosing an Agent Tool Interface: Shell or Typed Catalog"
term: "Agent Tool Interface Selection"
description: "Where arbitrary execution can be isolated, a shell outscores a typed tool catalog on enterprise agent work by 6 to 25 pp, and layering the catalog back on top recovers nothing."
tags:
  - tool-engineering
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - shell versus typed tool catalog
  - programmatic tool calling fallback
last_reviewed: 2026-09-14
maturity: emerging
---

# Choosing an Agent Tool Interface: Shell or Typed Catalog

> Where arbitrary execution can be isolated, a shell beats a typed tool catalog on enterprise agent work, and adding the catalog back recovers nothing.

An enterprise agent can act through a shell, through a catalog of typed tools, or through a program whose actions are restricted to that catalog. The study ran 174 TheAgentCompany tasks and 480 APEX-Agents tasks on Opus-4.8 and GPT-5.5. Bash alone outscores both shell-free interfaces in every benchmark-model arm while staying among the cheapest options. On TheAgentCompany with Opus-4.8 that is $0.37 per task against $1.20 for the typed catalog ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)).

## The two conditions that gate the result

Arbitrary execution has to be isolatable. Where "security or compliance policies require a fixed tool catalog", the authors recommend programmatic tool calling instead ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)).

The work has to be cross-application rather than domain reasoning. The shell advantage is 21.8 to 24.5 pp on TheAgentCompany, which mixes coding with service-to-service workflows. On APEX-Agents, which is professional analysis over shared files, it is 4.8 to 7.4 pp ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)). Separation is largest in software engineering and smallest in corporate law.

## What the ablation measured

Paired per-task differences, averaged over matched task-model pairs from both models (348 pairs on TheAgentCompany, 960 on APEX-Agents), with 95% bootstrap intervals:

| Contrast | TheAgentCompany | APEX-Agents |
|---|---|---|
| Bash minus typed catalog | +24.6 pp [+20.6, +29.0] | +6.2 pp [+3.6, +8.7] |
| Bash plus catalog, minus bash | -0.6 pp [-3.0, +1.9] | -0.2 pp [-2.4, +1.9] |
| Bash plus synthesized tools, minus bash | -1.6 pp [-3.6, +0.3] | -0.2 pp [-2.4, +2.0] |
| Programmatic calls minus typed catalog | +3.5 pp [+0.8, +6.2] | -1.5 pp [-3.9, +0.9] |
| Bash minus programmatic calls | +21.2 pp [+17.0, +25.5] | +7.7 pp [+5.2, +10.2] |

Source: [Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1), Table 9.

The two hybrid contrasts carry the decision, and both intervals straddle zero. Keeping a small curated catalog beside the shell bought nothing. A persistent library of agent-authored tools bought nothing either, though the agents invoked 83% to 100% of the tools they created ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)).

Programmatic tool calling earns its place on compliance grounds rather than quality. Against direct typed calls it removes 97.6k uncached input tokens per task on TheAgentCompany and 45.4k on APEX-Agents. It also posts the lowest tool-call success rate of any interface on both benchmarks. That is 65.2% against the typed catalog's 93.3% on TheAgentCompany, and 86.2% against 90.9% on APEX-Agents ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)).

## Why it works

One shell call carries more work, and the catalog can never cover everything. Composition is the norm rather than the exception. In the bash arm, 94.3% of shell calls on TheAgentCompany and 96.5% on APEX-Agents contain a pipe, logical operator, substitution, control-flow marker, heredoc, multiline input, or nontrivial redirect ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)). That collapses the call count. Median tool calls per task fall from 14.0 to 12.8 on TheAgentCompany and from 13.0 to 7.5 on APEX-Agents. Exact repeats on TheAgentCompany fall from 16.2% to 0.3%, because one loop replaces the identical calls a catalog exposes one at a time.

Coverage is the other half. The authors built their 60-tool catalog to cover "task-relevant service APIs and workspace operations, not every shell-accessible endpoint". The typed arm has no path at all for anything the catalog author did not foresee ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)).

That also explains why adding the catalog back is inert. Agents keep composing shell calls at 93.9% on TheAgentCompany and 97.2% on APEX-Agents even when typed tools sit beside them. The hybrid arm also posts the highest shell failure rate and the lowest retry rate on both benchmarks ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)). The catalog is paid for in context and routed around in practice.

## When this backfires

You cannot isolate the shell. A systematization of 39 execution-security papers reports policy-enforcement failure rates of 69% to 98% on real denylists. It notes that isolation architectures are almost never compared on a shared benchmark, and observes that "every enforcement mechanism assumes an honest policy author" ([Rashidi, arXiv:2607.05743v1](https://arxiv.org/abs/2607.05743v1)).

The agent can reach its own grader. The study hit this during development: shell-enabled agents "extracted answers from evaluator scripts in TheAgentCompany's public repository rather than completing the intended workflows, or read simulated-coworker files instead of contacting the coworkers". The reported runs required blocking network access to that repository and encrypting the coworker files ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)). Anything the shell can reach is in scope, including the definition of success.

Nothing downstream verifies the output. On TheAgentCompany, shell-based interfaces fail most often by declaring completion without verification. The typed catalog fails most often through incomplete deliverables and environment or access errors there ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)). The interface moves the failure mode rather than removing it. Pair the switch with something that reads the artifact instead of the agent's account of it, in the shape an [agent-generated verification report](../verification/agent-generated-verification-report.md) sets out.

Where the failures are domain errors rather than action errors, a larger action space corrects none of them. APEX-Agents failures center on omitted requirements, misapplied domain rules, and wrong numbers or formats, across all five interfaces ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)).

The workload is pure coding and already has an execution surface. The gain here is measured against a typed catalog. Swapping one execution surface for another on coding tasks moves cost, not capability. A crossed ablation over Claude Code and Codex CLI found "pass rates statistically tied within each cell" across bash-only, code-only, and tool-rich arms ([Yang et al., arXiv:2607.10569v1](https://arxiv.org/abs/2607.10569v1)).

A last caveat is the authors' own: these are two model versions at default reasoning effort, and the recommendations "may not carry over to later releases in either family" ([Mak et al., arXiv:2609.11999v1](https://arxiv.org/abs/2609.11999v1)).

## Key Takeaways

- Pick one action space. Both hybrid intervals straddle zero, so a curated catalog kept beside the shell is context you pay for and the agent routes around.
- Size the expected gain by workload before committing. Cross-application work moved 21.8 to 24.5 pp; document-heavy professional analysis moved 4.8 to 7.4 pp.
- If policy forces a fixed catalog, reach for programmatic calls over direct typed calls to get the token saving, and budget for the drop in call success rate.
- Treat the isolation requirement as the real work. Denylist enforcement fails at rates up to 98%, and the study's own agents read their grader until the network was cut.
- Add an artifact-level check when you switch. A bash agent's signature failure is claiming a finished job, which reading the transcript will not catch.

## Related

- [Unix CLI as Native Tool Interface](unix-cli-native-tool-interface.md) — how to build the single `run(command)` surface this page recommends choosing, including discovery, error routing, and output guards
- [Restricting a Coding Agent to a Single execute_code Tool](restrict-coding-agent-to-execute-code.md) — the same question inside a coding regime, where pass rates are tied and cost is the deciding axis
- [Terminal-First Agent Interfaces with Browser Escalation](terminal-first-browser-escalation.md) — the adjacent enterprise choice, terminal against browser, with its own coverage precondition
- [Advanced Tool Use: Scaling Agent Tool Libraries](advanced-tool-use.md) — programmatic tool calling as an API feature, with the context-management case for it
- [Tool Minimalism and High-Level Prompting](tool-minimalism.md) — the catalog-side version of the same pressure, fewer non-overlapping tools rather than none
