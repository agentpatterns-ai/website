---
title: "Domain-Scoped Parallel Exploration for Multi-File Change Localization"
description: "Partition a coding agent's repository exploration along domain seams when the change spans subsystems — the win is context isolation, not parallelism itself."
tags:
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - domain-scoped exploration
  - parallel file localization for multi-file changes
last_reviewed: 2026-06-12
maturity: emerging
---

# Domain-Scoped Parallel Exploration for Multi-File Change Localization

> Partition a localization agent's exploration along domain seams when a change actually spans multiple subsystems — the win is context isolation.

The pattern applies under three conditions: the change touches files in multiple subsystems, the repository has identifiable domain boundaries an upfront partitioner can name, and the localization phase is what you are optimizing — not end-to-end repair. Outside those conditions, sequential priority-scheduled exploration matches or beats the parallel design at lower token cost ([arXiv:2502.00350](https://arxiv.org/abs/2502.00350), [arXiv:2503.22424](https://arxiv.org/abs/2503.22424)).

## What the Pattern Does

A localizer that follows this pattern runs in three stages:

1. **Partition** — an upfront analyzer reads the issue text plus a high-level repository map and emits a set of domain scopes (e.g. `playbooks/`, `inventory/`, `modules/network/` in an ansible-shaped codebase). Each scope is a hypothesis about *where* the change might land.
2. **Explore in parallel within each scope** — one sub-agent per scope traverses only its own subtree, returning a short ranked list of candidate fix files plus a one-paragraph justification. Each sub-agent's full exploration trace stays inside its own context, the defining property of [sub-agents and fan-out](../multi-agent/sub-agents-fan-out.md).
3. **Aggregate** — the orchestrator merges the ranked lists, applies cross-scope de-duplication, and produces the final file-level prediction. Test files surface as evidence, not as fix targets, because each sub-agent already labeled them in context ([arXiv:2606.11976](https://arxiv.org/abs/2606.11976)).

The naive alternative — a single agent with unrestricted file-system access — over-predicts test files because it sees them and confuses them with fix targets. The paper's evaluation on SWE-Bench Pro using ansible found a domain-scoped parallel design with Haiku-class models achieved the highest micro F1 among comparable systems ([arXiv:2606.11976](https://arxiv.org/abs/2606.11976)).

## Why It Works

The active ingredient is **context isolation along semantically meaningful seams**, not parallelism. A single-context agent's attention budget over a large repository is bounded; once its context fills with files from one subsystem, files in a second subsystem fall out of attention. Splitting exploration by domain gives each sub-agent a narrower hypothesis space, and each sub-agent's *distilled summary* — not its raw exploration trace — is what reaches the orchestrator, the same isolate-then-distil move as [discrete phase separation](discrete-phase-separation.md). The orchestrator's working context never sees the test files the sub-agent already filtered out.

This is the same mechanism Anthropic's sub-agent guidance describes for breadth-first research: "each subagent might explore extensively, using tens of thousands of tokens or more, but returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)" ([Anthropic: effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)). For localization specifically, the paper isolates the mechanism further: their own ablation shows multi-agent *consultation* — sub-agents talking to each other — provides no measurable benefit while substantially increasing token cost ([arXiv:2606.11976](https://arxiv.org/abs/2606.11976)). The partition does the work; the cross-talk does not.

## When This Backfires

The conditions under which sequential alternatives win:

- **Single-subsystem changes.** When the issue actually localizes to one module, parallel domain agents are token waste. OrcaLoca's priority-scheduled sequential design reached 65.33% function-match on SWE-bench Lite — a benchmark dominated by single-file fixes — without any parallel decomposition ([arXiv:2502.00350](https://arxiv.org/abs/2502.00350)).
- **Repositories without clear domain seams.** Monolithic or poorly-modularized codebases give the partitioner no useful boundaries. The partitioner becomes a single point of failure: a wrong split sends every sub-agent searching the wrong subtree, and the orchestrator has no signal to recover. Anthropic's multi-agent post explicitly flags this: "some domains that require all agents to share the same context or involve many dependencies between agents are not a good fit for multi-agent systems" ([Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)).
- **Frontier models that already frontload exploration.** When the runtime model aggressively explores the repository in early steps and orients quickly to multi-subsystem structure, the marginal value of structured parallelism falls — the same diminishing-returns curve [pre-execution codebase exploration](../workflows/pre-execution-codebase-exploration.md) hits with strong runtime agents.
- **Anything past localization.** For the repair phase, sub-agents need shared context — a fix in module A may depend on a contract in module B. The paper's own data shows that for multi-agent designs extended past localization, consultation gives no measurable benefit and adds token cost ([arXiv:2606.11976](https://arxiv.org/abs/2606.11976)). [Agentless](agentless-vs-autonomous.md) hands localization off to a single repair pass for exactly this reason.

Sequential alternatives — priority-scheduled action selection ([OrcaLoca](https://arxiv.org/abs/2502.00350)), iterative broad-then-deep call-graph search ([CoSIL](https://arxiv.org/abs/2503.22424)), or hierarchical localize-then-repair ([Agentless](https://arxiv.org/abs/2407.01489)) — are the safer default when those conditions are not met.

## Example

The contrast below shows a single-context localizer over-predicting test files versus a domain-scoped split that filters them in-scope. The setting is the paper's ansible exemplar from SWE-Bench Pro.

**Without the pattern — naive single-context localizer**

```
Issue: "Variable interpolation fails when inventory groups override
        module defaults during play execution."

Agent trace:
  read playbooks/example.yml          # finds use of vars
  read tests/unit/test_vars.py        # confuses with fix site
  read tests/unit/test_inventory.py   # confuses with fix site
  read inventory/group_vars/all.yml
  read modules/cloud/aws_ec2.py       # irrelevant subsystem
  ... context fills with low-signal files ...
  predict: tests/unit/test_vars.py, tests/unit/test_inventory.py,
           inventory/group_vars/all.yml
```

The single agent reads test files and emits them as predictions because they sit in the same context as the issue text. Naive file-system access degrades localization through exactly this over-prediction failure mode ([arXiv:2606.11976](https://arxiv.org/abs/2606.11976)).

**With the pattern — domain-scoped parallel exploration**

```
Partitioner output:
  - scope: inventory/        hypothesis: group-var override resolution
  - scope: playbooks/        hypothesis: variable evaluation in plays
  - scope: lib/ansible/vars/ hypothesis: interpolation engine

Sub-agent: inventory/        returns: [inventory/manager.py rank 0.6]
                             notes: test files seen and excluded
Sub-agent: playbooks/        returns: [no strong candidate, rank 0.2]
Sub-agent: lib/ansible/vars/ returns: [lib/ansible/vars/manager.py rank 0.9,
                                       lib/ansible/template/__init__.py rank 0.7]
                             notes: test files seen and excluded

Orchestrator merge:
  predict: lib/ansible/vars/manager.py,
           lib/ansible/template/__init__.py,
           inventory/manager.py
```

Each sub-agent filtered its own test files before returning. The orchestrator's context never saw them, so they could not be promoted as predictions.

## Key Takeaways

- The pattern is *conditional*: multi-subsystem change, clear domain seams, localization phase only.
- The mechanism is context isolation along semantic seams — not parallelism. Multi-agent consultation adds cost without benefit ([arXiv:2606.11976](https://arxiv.org/abs/2606.11976)).
- A wrong partition is fatal: the partitioner is the single point of failure.
- For single-subsystem issues and for repair-phase work, sequential approaches ([OrcaLoca](https://arxiv.org/abs/2502.00350), [CoSIL](https://arxiv.org/abs/2503.22424), [Agentless](agentless-vs-autonomous.md)) match or beat parallel exploration at lower cost.
- Naive file-system access without scoping over-predicts test files; any localizer needs *some* mechanism to label test files in context.

## Related

- [Agentless vs Autonomous: When Simple Beats Complex](agentless-vs-autonomous.md) — Sequential two-phase localize-then-repair as the baseline parallel exploration must beat.
- [Discrete Phase Separation](discrete-phase-separation.md) — The same isolate-then-distil mechanism, applied across phases rather than across domain scopes.
- [Sub-Agents and Fan-Out](../multi-agent/sub-agents-fan-out.md) — The general fan-out primitive this pattern specializes for localization.
- [Scaffold Architecture Taxonomy for Coding Agents](harness-design-dimensions.md) — Where domain-scoped exploration sits in the control-architecture / tool-interface / resource-management taxonomy.
- [Pre-Execution Codebase Exploration](../workflows/pre-execution-codebase-exploration.md) — The complementary upfront-enhancement pattern; both share the same diminishing-returns curve against frontier models.
