---
title: "Continuous Agent Improvement: Iterating on Agent Quality"
term: "Continuous Agent Improvement"
description: "Turn observed agent failures into reviewed configuration changes. Preserve run evidence, check scorer errors, and compare replay and regression results."
tags:
  - workflows
  - agent-design
  - instructions
  - tool-agnostic
  - factory-engineering
last_reviewed: 2026-11-06
maturity: emerging
---

# Continuous Agent Improvement: Iterating on Agent Quality

> Continuous agent improvement turns observed failures into proposed changes, with evidence and regression review before adoption.

Continuous agent improvement is an observe, classify, update, and verify cycle for shared agent configuration. Use it when reviewers can inspect the failure, check the scorer, and compare a candidate against the current configuration. Warp's [improvement guidance](https://docs.warp.dev/factories/measure-and-improve/) documents this reviewed cycle; it does not establish safe autonomous improvement.

Related lesson: [Define "Done" First](https://learn.agentpatterns.ai/workflows/define-done-first/).

## Why failure scores need investigation

A failed score does not identify the cause. Anthropic's evaluation guidance describes Terminal-Bench tasks whose tests expected a script path that the task never specified. Correcting that mismatch requires examining the task and grader before changing agent behavior. [Anthropic's evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

Warp documents two repair targets: application code and version-controlled factory prompts, skills, and configuration. Its improvement PRs link failing runs and scorer results. Use that distinction when deciding whether a defect warrants a product fix or a shared configuration proposal. [Warp self-improvement](https://docs.warp.dev/factories/measure-and-improve/self-improvement/).

## Four implementation layers

This tool-agnostic workflow connects execution evidence, a proposed change, and a review decision. The layers below adapt [Warp's improvement cycle](https://docs.warp.dev/factories/measure-and-improve/) and [Anthropic's evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

### Layer 1: Observe and preserve evidence

Start with a failed run or a reviewer correction. Preserve the task and resulting artifact before proposing a fix. Compare scorer judgments with human review and inspect the underlying runs, as [Warp recommends](https://docs.warp.dev/factories/measure-and-improve/). Use [agent debugging](../observability/agent-debugging.md) to inspect execution evidence.

Attach this evidence-to-change checklist to the proposal. It is an editorial synthesis of the cited guidance, not a separately validated protocol:

| Evidence | What to record |
|---|---|
| Task and result | Task specification, run link, output artifact, expected behavior, and actual acceptance result |
| Scorer | Scorer version, criteria, rationale, and human agreement or disagreement |
| Execution configuration | Model, tools, supplied context, and configuration revision |
| Diagnosis | Proposed cause, supporting evidence, and alternative explanations |
| Candidate | Patch link, affected layer, and reason for the change |
| Verification | Fixed replay inputs, repeated outcomes, baseline comparison, and broader regression results |
| Decision | Reviewer, adoption or rejection rationale, and follow-up production observation |

The run-to-patch link follows [Warp's improvement PRs](https://docs.warp.dev/factories/measure-and-improve/self-improvement/). Input preservation and baseline comparison follow its [benchmark guidance](https://docs.warp.dev/factories/benchmarks/). Record missing evidence as a limitation; do not fill the checklist with assumed results.

### Layer 2: Classify the suspected cause

Treat an agent-authored diagnosis as a hypothesis. Check the artifact against the specification and scorer rationale. Anthropic's documented grading defects support checking the evaluator itself before accepting its failure label. [Anthropic's evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

Choose the repair target from the evidence:

| Suspected failure location | Proposed repair |
|---|---|
| Product code | Correct the delivered application and test the defect |
| Task specification | Clarify the intended outcome and expose any changed acceptance criteria |
| Scorer | Correct an invalid criterion or grading defect; review the scoring change separately |
| Supplied context or instructions | Propose a scoped change to shared guidance |
| Tool behavior or factory policy | Propose a tool or orchestration change with its own verification |

This triage combines [Warp's application and factory distinction](https://docs.warp.dev/factories/measure-and-improve/self-improvement/) with [Anthropic's task and grader checks](https://www.anthropic.com/research/demystifying-evals-for-ai-agents). Keep a product repair separate from any proposed shared configuration repair. Require evidence for each; a product defect alone is insufficient justification for a new shared rule.

### Layer 3: Update one candidate

Propose the smallest change that tests the hypothesis. Keep the baseline revision and record the reason for the edit. Warp recommends changing one configuration at a time and retaining comparison inputs. [Warp benchmarks](https://docs.warp.dev/factories/benchmarks/).

Evaluate removals as well as additions. Claude Code's guidance recommends pruning generated instructions and omitting information the agent can infer from code. [Claude Code best practices](https://code.claude.com/docs/en/best-practices). As a maintenance policy, propose removing ineffective, obsolete, or redundant instructions. Retain the removal rationale and compare outcomes before adoption. This combines that pruning advice with [controlled comparison](https://docs.warp.dev/factories/benchmarks/); it does not promise that shorter instructions improve results.

### Layer 4: Verify and review before adoption

Replay the triggering task with fixed inputs and compare the candidate with the baseline. Run repeated trials and broader regression cases. Anthropic recommends repeated trials because model outputs vary, and regression evaluations to check that existing capabilities still work. [Anthropic's evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

If replay still fails, revisit the hypothesis, intervention, and run variation. A recurrence alone does not isolate which explanation failed. Keep this diagnostic uncertainty visible in the review, consistent with Anthropic's guidance on [task defects and repeated trials](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

Submit the patch with its evidence and regression comparison for review. Record the decision, then compare later production runs with the original baseline after adoption. [Warp's review guidance](https://docs.warp.dev/factories/measure-and-improve/) and [benchmark follow-up](https://docs.warp.dev/factories/benchmarks/) describe these steps. Use [Factory Engineering](../factory-engineering/index.md) for the wider measurement and promotion context.

## Staleness and drift

Shared instructions need maintenance after the failure that produced them. Claude Code recommends pruning instructions that duplicate what the agent can infer from code ([best practices](https://code.claude.com/docs/en/best-practices)).

As a proposed maintenance policy, periodically review rules against current commands, paths, and repository behavior. Record the original failure, affected configuration revision, candidate change, verification results, and later recurrence. Batch observations before changing a shared rule; one failure can start investigation without establishing a general rule. Keep obsolete guidance out of the baseline used for comparison.

## Triggers and constraints

A failed scorer, manual review, or scheduled inspection can start investigation. Warp supports scheduled and ad hoc improvement runs; its scheduling defaults are product settings, not validated thresholds for changing shared configuration. [Warp self-improvement](https://docs.warp.dev/factories/measure-and-improve/self-improvement/).

For this workflow, authorize investigation and a proposal first. Require a review decision before adopting the candidate. Warp's documentation permits `reviewerType: none`, so its product description does not establish an unavoidable human gate. Passing selected benchmark tasks does not establish success or safety on untested tasks. [Warp self-improvement](https://docs.warp.dev/factories/measure-and-improve/self-improvement/); [Warp benchmarks](https://docs.warp.dev/factories/benchmarks/).

## Why it works

Preserved inputs make a comparison inspectable. Repeated trials account for output variation; regression cases check whether a targeted repair damages existing behavior. Scorer calibration ties the verdict to the intended result. These mechanisms support reviewing a candidate, without guaranteeing an improvement. [Warp benchmarks](https://docs.warp.dev/factories/benchmarks/), [scorer calibration](https://docs.warp.dev/factories/measure-and-improve/), and [Anthropic's evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

## When this backfires

Append-only instruction changes can add cost without a demonstrated benefit. An evaluation of LLM-generated repository context files found no significant performance effect and increased inference costs in its tested settings. The authors also report no significant effect of file length. These findings support testing changes; they do not prove that pruning causes better outcomes. [Evaluating AGENTS.md, v3](https://arxiv.org/abs/2602.11988v3).

Tuning only to the triggering failure leaves other behavior unchecked. Include broader regression cases, and keep task or scorer changes visible so a changed acceptance rule cannot masquerade as a product repair. [Anthropic's evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

Maintenance also takes time. Mitchell Hashimoto reports that initial agent corrections took longer than doing the work himself. He later describes changing instructions and tools in response to failures. This is independent practitioner experience, not a controlled team-factory experiment. [Hashimoto's adoption account](https://mitchellh.com/writing/my-ai-adoption-journey).

## Example

Anthropic's long-running web-app experiments provide a documented failure-to-configuration case. The team observed Claude marking features complete without adequate testing. It added browser testing tools and explicit instructions to test as a user would. [Anthropic's harness experiments](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents).

The public account supports this partial case record:

| Field | Documented evidence |
|---|---|
| Observed failure | Premature completion after inadequate testing |
| Changed layer | Harness tools and testing instructions |
| Reported outcome | The agent identified and fixed bugs that code inspection alone missed |
| Residual limitation | Browser-native alert dialogs remained invisible through Puppeteer MCP |

These are the team's reported observations. The account does not provide a complete original-run, configuration-revision, acceptance, and controlled-replay record for this change. It illustrates shared configuration repair, with public evidence gaps. It does not establish complete verification or autonomous safety. [Anthropic's testing account](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents).

## Key Takeaways

Use these editorial review decisions with the checklist above:

- If human review and the scorer disagree, return the proposal for diagnosis before deciding on the configuration patch.
- If replay evidence remains incomplete, record which adoption questions remain unanswered and what evidence the next review needs.

These decisions apply [scorer calibration](https://docs.warp.dev/factories/measure-and-improve/) and [evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents); they are not a validated promotion protocol.

## Related

- [Test Factory Changes on Representative Work Before Promotion](../factory-engineering/controlled-factory-experiments.md)

- [Factory Engineering](../factory-engineering/index.md) — measurement and promotion context
- [Failure-Driven Iteration](failure-driven-iteration.md) — repair the current task using tool feedback
- [Skill Library Refinement Loops](skill-library-refinement-loops.md) — evaluate changes to shared skills
- [Scheduled Instruction File Fact-Checker](instruction-file-fact-checker.md) — inspect instructions for stale claims
- [Prompt Tinkerer](../patterns/anti-patterns/prompt-tinkerer.md) — instruction changes without a tested diagnosis
