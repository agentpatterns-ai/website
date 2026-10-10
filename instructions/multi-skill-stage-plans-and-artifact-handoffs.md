---
title: "Stage Plans and Artifact Handoffs for Multi-Skill Tasks"
term: "Stage Plan and Artifact Handoff"
description: "Tell an agent holding three or more skills each stage's objective and, for five or more skills, the files each skill hands on. A bare use order adds less."
aliases:
  - skill organization instructions
  - stage plan
  - dependency DAG for skills
  - multi-skill orchestration instructions
tags:
  - instructions
  - tool-agnostic
  - skills
  - arxiv
last_reviewed: 2026-10-09
maturity: emerging
---

# Stage Plans and Artifact Handoffs for Multi-Skill Tasks

> Give an agent with three or more skills stage objectives, and add named artifact handoffs at five or more skills.

A stage plan divides a multi-skill task into ordered stages, and each stage names the skills to use and the intermediate objective they must reach. An artifact handoff goes one step further: it names the file one skill saves and the next skill reads, and it tells the next skill to run only when that file exists. In one study of 41 tasks with the skill set held fixed, both beat a bare use order in all three model and harness configurations tested ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)).

## When the evidence applies

The result is narrower than the headline. Check these conditions before you write plans for a skill library.

| Condition | What the study found |
|-----------|----------------------|
| The task supplies 3 or more skills | The study used only 41 tasks with at least three skills. It says nothing about one or two. |
| The task has 5 or 6 skills | DAG beat Stage Plan by 12.12, 3.03, and 9.09 points across the three configurations. At four skills the two were identical in every configuration. |
| You can write the plan by hand | The authors built every instruction by hand from the task description and the skills, and a second author checked them. Automatic plan generation was not tested. |
| Late steps rarely force changes to early ones | A DAG tells each node to run only when its required artifacts are available, so it fixes the decomposition before the run starts. |

Outside these conditions, start from the plain skill set and add structure only when a task fails.

## The four schemes

The study compared four ways of presenting the same skills ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)).

- Flat gives the agent the skills with no organization instructions.
- Sequence adds a use order.
- Stage Plan adds ordered stages, each with the skills to use and an intermediate objective.
- Dependency DAG adds nodes that each represent one use of a skill, with prerequisite artifacts named and later nodes told to run only when those artifacts exist.

## What the numbers show

Pass rates in percent for the three configurations, from Table 7 of the paper ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)):

| Configuration | No skill | Flat | Sequence | Stage Plan | DAG |
|---------------|----------|------|----------|------------|-----|
| GPT-5.5 + Codex | 44.72 | 52.03 | 52.85 | 55.28 | 58.54 |
| DeepSeek-V4-Flash + OpenClaw | 34.96 | 39.84 | 47.97 | 51.22 | 51.22 |
| Qwen3.5-27B + OpenCode | 11.38 | 21.14 | 21.95 | 25.20 | 27.64 |

The paper states that "Stage Plan and Dependency DAG yield greater downstream utility than Sequence across all three configurations". DAG improves over Flat by 6.50, 11.38, and 6.50 points. For DeepSeek, DAG ties Stage Plan at 51.22, so it is the tied-highest score there and not the highest.

A use order alone does little for GPT and Qwen, where Flat to Sequence moves under one point. DeepSeek differs. Sequence alone lifts it 8.13 points, which is most of DAG's 11.38-point gain. Do not generalize that order adds little.

## How big the gaps are

Each task is worth 2.44 points, because 1 divided by 41 is 0.0244. Stage Plan beats Sequence by 2.43, 3.25, and 3.25 points, so roughly one task per configuration. Each task ran three times per condition, and the paper reports no significance test for Table 7 (the task-count conversion here is my arithmetic from the table).

The 5 to 6 skill split is thinner. The paper warns that "The five- and six-Skill groups contain six and five tasks, respectively, so group differences may also reflect task composition." One full task flip across those 11 tasks is 9.09 points, so the 3.03-point DeepSeek gap is a third of one task's runs.

AgentSkillOS points the same way from a different design. With the identical oracle skill set, flat skill invocation in Claude Code "performs significantly worse than AgentSkillOS with DAG orchestration" ([arXiv:2603.02176v1](https://arxiv.org/abs/2603.02176v1)). That test used 30 tasks and an LLM pairwise judge. It compared a whole orchestration system, including planning calls, against flat invocation, so it does not isolate the instruction text the way the first study does. The system also generates its own DAG from predefined strategies, which makes it the one data point on automatic plans.

## Why it works

A named intermediate artifact is a saved checkpoint. The agent can re-read it, find an error that only shows up downstream, and rerun the earlier step. In the study's jpg-ocr-stat task, the DAG required saving OCR text from one skill and then extracting structured fields from it for a workbook skill. GPT + Codex passed 0 of 3 runs under Flat, Sequence, and Stage Plan, and 3 of 3 under DAG. In one passing run the agent "inspects the extracted fields, reads the OCR text for the corresponding receipts, then reruns field extraction, updates the field file, and rebuilds the workbook". The authors conclude that "These artifacts support both cross-Skill result transfer and correction before delivery." ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)).

This mechanism rests on case trajectories. No ablation removes artifact saving while holding everything else fixed. The paper gives no separate trajectory for why Stage Plan beats Sequence, so treat the intermediate-objective explanation as untested.

## How to apply it

1. Count the skills the task supplies. Below three, skip the plan.
2. Write one stage per skill group, naming the skills and the objective the stage must reach.
3. For five or more skills, or for a task where an early extraction can be wrong, name the file each skill saves and tell the next skill to start only when that file exists.
4. Review the plan against the skill descriptions, as the study's second author did.

## Example

A receipt task supplies `image-ocr` and `xlsx`, plus a third skill for field validation. The plan below is illustrative and is not one of the study's instruction sets.

**Before** — a use order:

```markdown
Use image-ocr, then field-validate, then xlsx.
```

**After** — stages with handoffs:

```markdown
Stage 1. Run image-ocr on every receipt. Save the text to ocr/<receipt>.txt.
Stage 2. Run field-validate only when ocr/<receipt>.txt exists. Save
fields.json with one record per receipt.
Stage 3. Run xlsx only when fields.json exists. Before you deliver,
compare each row against its OCR text and rerun Stage 2 if they differ.
```

The last line of Stage 3 is what the saved files make possible.

## When this backfires

- A task with three or four skills pays the authoring cost of a DAG and gets nothing over a Stage Plan. The two scored identically in the four-skill group in every configuration.
- Prescribed procedures can burden an agent. The same paper says "recommended procedures can become an execution burden when agents struggle to implement or adapt them." A DAG is a stricter procedure, and the study does not test whether it causes that failure ([arXiv:2610.08875v2](https://arxiv.org/abs/2610.08875v2)).
- A hand-written DAG turns an agent run into a fixed workflow. Anthropic advises "finding the simplest solution possible, and only increasing complexity when needed" ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)).
- A strong model on a small skill set may not need it. GPT + Codex gains 6.50 points from Flat to DAG, about 2.7 tasks of 41, with no significance test.
- Steps that feed back into earlier steps break a fixed graph. The related compositional-routing page covers the cascading failure of pre-committed decompositions.

## Key Takeaways

- Default to a stage plan with an intermediate objective per stage once a task supplies three or more skills.
- Add named artifact handoffs for five or more skills or for tasks that need late correction. The 5 to 6 skill evidence comes from 11 tasks.
- A bare use order helped DeepSeek by 8.13 points and GPT and Qwen by under one point, so test it on your own model.
- The margins between schemes are about one task of 41 and carry no significance test.
- Every plan in the study was hand-built, and the cost of writing and freezing one is yours.

## Related

- [Compositional Skill Routing for Large Skill Libraries](../context-engineering/compositional-skill-routing.md) — how to pick skills from a large library, which comes before organizing the ones you picked
- [Execution Lineage: DAG of Artifacts vs Agent Loops](../patterns/agent-design/execution-lineage-dag.md) — replay and revision of artifact DAGs, a different concern from instructing a fixed skill set
- [Per-Step Preconditions and Postconditions in Skill Files](per-step-skill-preconditions.md) — contracts inside one skill, where this page covers the handoffs between skills
- [Skill Lift](../verification/skill-lift.md) — measuring whether a skill helps at all before you organize several
