---
title: "Cost-Inefficient Behaviors in Coding Agents"
term: "Cost-Inefficient Behaviors"
description: "Coding agents re-read code they already retrieved, rewrite near-identical scripts, and rerun unchanged tests; how much of the bill that carries depends on the harness, and removing the behavior is not the same as removing the cost."
tags:
  - anti-pattern
  - cost-performance
  - tool-agnostic
  - arxiv
  - long-form
aliases:
  - subsumed retrieval
  - similar script generation
  - test re-execution
  - cost-inefficient agent behaviors
last_reviewed: 2026-09-28
maturity: emerging
---

# Cost-Inefficient Behaviors in Coding Agents

> Three repeated behaviors showed up in 79.00% to 98.00% of coding tasks, at an average 6.86% to 22.75% of task cost depending on the harness.

Your agent re-reads a file a subagent already read, writes a fourth probe script almost identical to the third, and runs the same test again without having touched the patch. A study of 1,200 trajectories from Claude Code and Mini-SWE-Agent on 300 SWE-bench Verified tasks names those three behaviors, counts them, and attributes a share of task cost to each ([Hu et al., "Analyzing and Mitigating Cost-Inefficient Behaviors in Coding Agents", arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)). In this study the harness moved the cost share more than the model did: Claude Code 6.86% against 21.16% for Mini-SWE-Agent on the same Sonnet 4.6, and 21.16% to 22.75% across three models inside Mini-SWE-Agent. And the obvious fix, bolting on a tool that removed the behavior under Claude Code, made the bill go up in the same study.

## What the study counted

Three behaviors, each defined by a detector run over the trajectory:

- Subsumed retrieval: a retrieval whose returned content is fully covered by an earlier retrieval. The detector scans backward from each retrieval that returns at least five non-empty lines ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).
- Similar script generation: a script regenerated rather than edited, at line-level Jaccard similarity of at least 0.60 against the nearest preceding script. The authors set that threshold by manually inspecting 20 pairs per configuration ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).
- Test re-execution: repeated runs of the same tests inside one inter-patch window. The detector keeps the last run, on the grounds that it is "potentially decision-relevant", and flags every run before it ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

Prevalence below is the percentage of tasks showing the behavior at least once. Cost is the average share of per-task monetary cost attributed to it, computed from the tokens in each flagged action at the relevant model's own prices. Four configurations were measured: Claude Code with Sonnet 4.6 as the main model and Haiku 4.5 for subagents, and Mini-SWE-Agent with Sonnet 4.6, MiniMax-M3, or Qwen-3.5 Plus ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

| Behavior | Claude Code | MSA + S46 | MSA + MM3 | MSA + Q35+ |
|---|---|---|---|---|
| Subsumed retrieval | 64.33% / 5.01% | 87.33% / 8.42% | 92.33% / 7.88% | 89.33% / 11.41% |
| Similar script generation | 20.67% / 1.02% | 51.33% / 9.57% | 68.00% / 8.85% | 57.67% / 7.91% |
| Test re-execution | 49.67% / 0.83% | 69.00% / 3.17% | 83.00% / 5.39% | 66.00% / 3.43% |
| All three | 79.00% / 6.86% | 97.33% / 21.16% | 98.00% / 22.12% | 96.67% / 22.75% |

Each cell is tasks affected / average share of task cost, from Table 1 of [arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1).

Read the spread, not the maximum. The 22.75% belongs to one Mini-SWE-Agent configuration. The same three behaviors under Claude Code carried 6.86%, and the paper states that "CC consistently exhibits the lowest overall level of inefficiency" ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)). The authors put that down to the harness rather than the model: Claude Code's system prompt and tool abstractions suppress several of these behaviors before any intervention ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

## Why it works

Under Claude Code, half of subsumed retrieval crosses the subagent boundary. The paper reports that cross-agent subsumed retrieval "is unique to CC and accounts for 50.15% of its SubRetrv", because "CC offloads exploration to subagents, which return summaries rather than the retrieved code. So the main agent may re-retrieve the same region when needed later" ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

Script regeneration follows the artifact. Similar script generation "occurs 5.91–9.98× more frequently in MSA (2.54–4.29 vs. 0.43)" per task, and the authors call the gap consistent with a line in Claude Code's own system prompt. The difference, they write, "is consistent with CC's built-in instruction: 'NEVER create files unless they're absolutely necessary for achieving your goal.' This discourages persistent script creation and shifts toward ephemeral generation" ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

Test re-execution has no counterweight in Claude Code's built-in prompt. Here the authors report that "we find no built-in instruction that discourages re-running tests without updated patches or asks the agent to reuse previous test output", and call it "the one behavior where CC shows no clear advantage: 2.09 executions per task, the same magnitude as MSAS46 (2.51) and MSAQ35+ (2.10)" ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)). Its three named causes are gaps in repository-specific test knowledge, recovery of test output the agent failed to capture, and stalls where the agent reruns without advancing the patch.

The saving, when you get one, exceeds the behavior's own price tag. Relating task-cost change to behavior-attributed cost change, the authors fit slopes of 2.83 on the held-out Verified tasks and 1.33 on the SWE-bench Pro sample. They give two reasons. A shorter trajectory re-reads less cached context on every later call. Removing an action can also prevent unflagged follow-on actions, such as the reasoning that would have interpreted its output ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

## The behavior fell and the bill rose

Equipping Claude Code with CodeGraph, a structure-aware retrieval tool, cut the behavior and raised the bill: "Under CC, SubRetrv drops by over 75% on both benchmarks, yet cost rises by 8.30% on Verified-200 and robustly by 12.19% on Pro-100" ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)). Under Mini-SWE-Agent the behavior did not fall reliably: "Under MSA, SubRetrv increases in four of six settings", and the authors conclude that CodeGraph "neither consistently reduces SubRetrv nor improves task cost efficiency". Across the eight agent-and-benchmark settings the tool "yields no robust cost reduction but four robust increases of 8.39–28.14%". Robust is the authors' own term: they "classify an effect as robust at one-sided p<0.05, imposing a stricter threshold on single-run effects" ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

Two mechanisms did the damage, both measured under Claude Code. Each CodeGraph query "returns 8.2–16.6× more tokens than other retrieval actions", so fewer calls bought no fewer tokens. And the tool changed who did the work: "H45 subagent calls drop from 4.81 and 11.03 per task to zero on both benchmarks, while S46 main-agent calls change only slightly (−0.42% and +8.17%). Thus, roughly the same token volume shifts to S46, whose token price is 3× that of H45" ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)). The retrieval tool deleted the cheap model from the trajectory.

[Token Reduction Mistaken for Cost Reduction](token-reduction-not-cost-reduction.md) records the same gap on a different tool class, where a compressor removed tokens without removing dollars.

## What reduced the bill

Seven general behavioral principles, written by the authors and preloaded into the agent's system prompt. They include:

- State what you expect to find before a read.
- Check whether content is already in context before fetching it again.
- Make targeted edits rather than whole-file overwrites.
- Identify the repository's test runner before running tests.
- Persist reusable scripts rather than creating numbered variants.
- Stop when repeated actions produce no new evidence ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

Those beat the agent-written alternative. The authors also built configuration-specific sets of 23 to 41 operational rules by distilling each agent's own trajectories ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)), then compared the two:

> SynSkills robustly reduce average cost in three of eight settings by 8.86–22.32%, with no robust cost increase or Pass@1 degradation (Table 3). In comparison, DevSkills robustly reduce cost in six settings by 7.88–41.73%, nearly twice the maximum saving from SynSkills, with only one small Pass@1 drop (−1.50 pp for CC on Verified-200). ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1))

Attach the scope before you quote that range. The 41.73% is Mini-SWE-Agent with Sonnet 4.6 on the held-out Verified tasks. Under Claude Code the same seven principles gave 13.94% on that split and a 1.51% cut on SWE-bench Pro that the authors do not count as robust, and Mini-SWE-Agent with Qwen-3.5 Plus on Pro got 3.57% more expensive. Six of eight settings cut cost by a margin the authors call robust; two did not (Table 3, [arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

On task success the authors count one drop, of 1.50 pp. Table 3 also shows Claude Code down 2.33 pp on Pro and Mini-SWE-Agent with MiniMax-M3 down 2.17 pp on Verified, neither of which the paper counts against the intervention. Most approach cells ran once and are judged against a noise floor estimated from three baseline runs (Study Setup, [arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

For why the hand-written set won, the paper offers a hypothesis and labels it one: "One possible mechanism is that DevSkills encode higher-level, trace-agnostic guidance, whereas SynSkills retain low-level, trace-specific instructions" ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)). The synthesized rules described how to handle a failed string substitution or a shell quoting problem. The hand-written rule on scripts said to persist and revise them instead of creating similar variants.

## When this backfires

The detectors count these actions and price them. They do not establish that any individual instance was dispensable, and the Threats to Validity section grants it: "Parsing, labeling, and detection mechanisms may introduce detection errors despite explicit implementations and manual calibration." ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

- Your trajectories run long. Long-distance subsumed retrieval, where the two reads sit at least 10 steps apart, was most prominent in the configuration with the longest runs: 52.40% of its pairs, at 77.99 average steps against 29.99 to 58.06 for the others ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)). The paper's own rule concedes the case, and offers "content is too far back in context to rely on" as a valid reason to re-read.
- Your harness already constrains the agent. The gain under Claude Code was smaller than under the bare shell agent on Sonnet 4.6 (13.94% against 41.73% on Verified-200, 1.51% against 33.00% on Pro-100), and the authors explain the general pattern as "CC's system prompt and tool abstractions already suppress several inefficient behaviors, leaving less room for improvement" ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).
- Your repositories look nothing like SWE-bench. Every rule set came from SWE-bench Verified trajectories. Carried across, effects shrank: "All approaches also perform better overall on Verified-200 than Pro-100 in identified behaviors. For skill-based approaches, this partly reflects a generalization challenge, as the skills are derived from Verified trajectories and applied to Pro" ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).
- You want statistical certainty from this. Baselines and nine intervention settings ran three times; budget limited the rest to single runs judged against a noise floor transferred from the matching baseline. The authors say so plainly: "Robustness estimates rely on baseline-derived variability, which may not fully establish statistical significance." ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)). The CodeGraph numbers carry one more restriction: the tool could not run on 13 of the 100 Pro tasks, so its Pro results compare 87.

## Example

**Before** — the cost column read as a savings target:

```text
Finding: the three behaviors account for up to 22.75% of task cost
Action:  install a structure-aware retrieval tool to kill subsumed retrieval
Result:  under Claude Code, subsumed retrieval down >75%,
         task cost up 8.30% (Verified-200) and 12.19% (Pro-100, robust)
```

**After** — measured on your own harness, judged on the bill:

```text
1. Count the behaviors in your own trajectories. The per-configuration
   spread in the paper is 6.86% to 22.75%; your harness has one number,
   not the range.
2. Change one thing. For example, add a system-prompt rule to rerun tests
   only when code changes or new evidence warrants it.
3. Compare total billed cost and task success against the unchanged arm.
   A drop in the behavior count is not the result you are buying.
```

## Key Takeaways

- Under Claude Code the three behaviors together carried an average 6.86% of task cost across 300 SWE-bench Verified tasks; under three Mini-SWE-Agent configurations, 21.16% to 22.75% ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)). Quote the figure for the harness you run.
- Half of Claude Code's subsumed retrieval crosses the subagent boundary: exploration is delegated, a summary comes back, and the main agent re-reads the code itself later ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).
- Test re-execution is the one behavior where Claude Code shows no clear advantage, at 2.09 executions per task against 2.51 and 2.10 for two of the three Mini-SWE-Agent configurations ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).
- A structure-aware retrieval tool cut subsumed retrieval by over 75% under Claude Code. Cost rose 8.30% on Verified-200, which is not among the four robust increases the authors list (8.39-28.14%), and 12.19% on Pro-100 (robust), partly by shifting work off a subagent model priced at a third of the main one ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).
- Seven general behavioral rules in the system prompt robustly reduced cost in six of eight settings by 7.88% to 41.73%, against three of eight and at most 22.32% for rules the agent distilled from its own traces. The top of that range is one framework, one model, one benchmark split (Table 3, [arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).
- The detectors count repeated actions, and the mitigation experiment recorded one Pass@1 drop of 1.50 pp that the authors count ([arXiv:2609.30725v1](https://arxiv.org/abs/2609.30725v1)).

## Related

- [Token Reduction Mistaken for Cost Reduction](token-reduction-not-cost-reduction.md) — the same gap between a metric that moved and a bill that did not, measured on context compressors
- [Harness-Controlled Token Economics (The Harness Effect)](../../token-engineering/harness-token-economics.md) — why four configurations differ by more than 3x on the same three behaviors
- [Cheaper Per Token, Costlier Per Task](cheaper-per-token-costlier-per-task.md) — the pricing side of the subagent shift that made the retrieval tool more expensive
- [Request Shaping to Cut Wasted Agent Turns](../../token-engineering/request-shaping-wasted-turns.md) — the prompt-side lever against retrieval the agent did not need
- [Indiscriminate Structured Reasoning](reasoning-overuse.md) — the adjacent case of paid tokens that do not change the outcome
