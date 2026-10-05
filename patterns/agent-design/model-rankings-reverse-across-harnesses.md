---
title: "Model Rankings Reverse Across Agent Harnesses"
term: "Harness-Dependent Model Ranking"
description: "Swap the harness and the better model can become the worse one, so evaluate the model and harness together rather than importing a leaderboard rank."
aliases:
  - harness-dependent model ranking
  - model-harness pair as evaluation unit
  - ranking reversal across harnesses
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-03
maturity: emerging
---

# Model Rankings Reverse Across Agent Harnesses

> Swap the harness and the better model can become the worse one, so benchmark the configuration you will ship rather than the model alone.

Measure the pairing when the harness is still yours to change. How much the harness matters depends on the model. The same study moved Claude Opus 5 by about 11 points on the general-terminal and professional-workflow collections and 27 on Terminal-Bench 4. It moved DeepSeek V4 Pro less on Terminal-Bench 4 than on either of the others. Two other studies measured smaller harness effects again.

A campaign of 66 configurations put four configurable harnesses (OpenHands, DeepSeek Harness, PI, openJiuwen) against five models on three benchmarks, plus the native Codex-GPT and Claude Code-Claude pairings. Its headline result is a reversal: "Model rankings reverse across harnesses". The recommendation follows from it: "A more natural practice is to select the model and harness for the benchmark and task at hand, and to evaluate each runtime support within that configuration" ([Li et al., arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)).

## Where the reversal is big enough to matter

On the 63-task non-H100 subset of Terminal-Bench 4, Claude Opus 5 and GPT-6 Astra trade places depending on the scaffold. "Claude drops from 57.14% with OpenHands to 30.16% with PI, whereas GPT rises from 49.21% to 60.32%, shifting the Claude-minus-GPT gap by 38.09 percentage points" ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)). A leaderboard row naming only the model gives you neither number.

That spread is not uniform. Across the five harnesses it ran under, Claude Opus 5 scores 0.6889 to 0.5821 on TUA-Bench and 0.5428 to 0.4348 on ALE-CLI, against 0.5714 to 0.3016 on Terminal-Bench 4 ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)). That is roughly 11 points on the first two collections and 27 on the third. DeepSeek V4 Pro runs the other way, with 6.35 points on Terminal-Bench 4 against 10.66 on TUA-Bench and 10.26 on ALE-CLI.

The winner also moves with the task: "The highest-scoring harness changes across collections for four of five models". One pairing held throughout, so persistence is possible: "openJiuwen gives Kimi its highest score on all three benchmarks, by 5.61 to 11.11 points" ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)).

## Vendor provenance is not a shortcut

Claude Code records Claude's highest score on TUA-Bench and ALE-CLI, by 3.50 and 1.14 points over the strongest evaluated alternative. On Terminal-Bench 4, OpenHands leads it by 7.94 points. For GPT the native option never wins: "Codex never records the highest GPT score; openJiuwen or PI exceeds it on each collection" ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)). So a vendor's own agent is sometimes the best way to run its model, and never reliably.

Cost moves on its own axis. On Terminal-Bench 4, "GPT-6 Astra scores 60.32% with PI at $4.66 per task but 52.38% with DSH at $19.94 per task" ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)). [Pricier-Per-Token Models That Cost Less Per Task](../../token-engineering/pricier-per-token-cheaper-per-task.md) owns that ordering.

## Why it works

The model supplies the repair. The harness decides whether the failure arrives as something repairable. Across ten matched OpenHands-against-PI pairs on Terminal-Bench 4 covering 192 coded failure events, 180 of the responses were model-initiated. The authors draw the consequence: "Models start almost all repairs themselves, so much depends on whether the harness hands failures back in a form the model can use" ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)).

Two defaults carry much of the measured gap. One harness ships no default shell timeout, so "34 PI runs on TB4 and TUA sat blocked in a final command that never returned and produced no signal at all". Another ends a run on repeated identical failing actions, and "this ended 55 runs, 48 of them Kimi re-issuing an edit call without its required content argument, and only one of these runs scored above zero" ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)). Neither default is good or bad by itself. A bounded shell matters least to a model that sets its own: "GPT-6, which sets explicit timeouts on 56–67% of its PI shell calls, obtains its best TB4 and ALE scores under PI's minimal scaffold". Kimi is the other case, "penalized by the OpenHands editor and by PI's unbounded and non-resuming behavior". Fit is that match, between a model's error habits and the harness's failure-return behavior, and one ranking cannot carry it.

Harness-Bench reaches the same conclusion about the reporting unit from 5,194 execution trajectories on a separate benchmark: "agent capability should be reported at the model-harness configuration level rather than attributed to the base model alone" ([Yao et al., arXiv:2605.27922v1](https://arxiv.org/abs/2605.27922v1)).

## When this backfires

- Two studies measured the harness term much smaller. On a 50-task Terminal-Bench Pro subset with two models and three harnesses, "paired within-model pass-rate differences remain 0–8 percentage points (95% paired-task bootstrap CIs include zero except for the largest gap)" ([Vats and Golev, arXiv:2607.22585v1](https://arxiv.org/abs/2607.22585v1)). On Agents' Last Exam, "model choice moves the score more than harness choice": the model sweep under a fixed OpenClaw harness spans 18.0 points, against harness sweeps of 6.0 points for GPT-5.5 and 5.3 for Claude Opus 4.7 ([Huang and Sun, 11 June 2026](https://agents-last-exam.org/blogs/harness-matters)). Where one of those settings is yours, it governs.
- One counted run per task. The authors state the limit: "Model settings, tools, and execution budgets are not uniformly matched, so the observed differences do not isolate the causal effect of any single component, and run-to-run variance is not measured" ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)). A reversal reproduced once is not yet a result.
- A benchmark winner can lose your domain. Within ALE-CLI, and for Kimi K3 alone, "openJiuwen leads PI by 24.83 points over 19 life-science tasks and by 11.99 points over 12 business/finance tasks, but trails by 2.32 points over 18 computing/math tasks" ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)).
- The grid costs real money. Claude Opus 5 over the 99 ALE-CLI tasks cost $498.26 under OpenHands and $323.34 under PI ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)). At a few tasks a day, four arms on one model and one benchmark are unlikely to repay themselves.
- The win may be one default you could change in place. The configurations differ in tools and budgets as well as in harness, so an advantage traced to an unbounded shell is cheaper to fix than to migrate for. On a single-vendor CLI where no migration is possible, [Per-Model Harness Tuning](per-model-harness-tuning.md) is the axis still open.

## Example

Kimi K3 passed the TUA task 056-move-textbox-left under openJiuwen and failed it under PI, and both runs hit the same bug. The model piped a GIMP script into an interactive invocation without a closing quit call, which leaves GIMP waiting for input. Under PI the shell had no default timeout and the model set none. The call never returned and the run received no further signal. It ended at the 40-minute deadline with no output file. Under openJiuwen the shell's 300-second limit returned the hang as a timeout. The model then diagnosed the cause itself. It found that the output image had already been written and verified it pixel by pixel. The authors note the openJiuwen run "was partly fortunate that the hung call had already written its output" ([arXiv:2610.00917v1](https://arxiv.org/abs/2610.00917v1)).

Nothing about Kimi's capability separates the two runs, which is why a model-only score predicts neither outcome.

## Key Takeaways

- Scope the grid before you fund it. Pick the two harnesses and one benchmark closest to your workload; the full cross is where the cost lives, not the finding.
- Ask any published rank which harness produced it, and treat an unanswered question as no evidence about your configuration.
- Shortlist by your model's error habits rather than by harness feature count. Ask which of your failures currently arrive as silence, then check whether a candidate harness bounds them.
- Put the measurement's own bill next to the saving you expect from it, and stop if the bill wins.
- Trace an advantage to a component before you migrate. A shell timeout is a configuration change; a harness swap is a rewrite.

## Related

- [Per-Task Agent Routing Across Coding Harnesses](per-task-agent-routing.md) — routes on cost and failure profile and argues against routing on capability, from the study whose within-model pass-rate gaps were 0 to 8 points.
- [Per-Model Harness Tuning](per-model-harness-tuning.md) — what to change inside one harness once the model is fixed.
- [Task Shape Decides What a Heavier Agent Harness Buys](task-shape-harness-payoff.md) — the heavier-against-lighter axis, held against model strength.
- [Model-Set Parity: Reading Harness Efficiency Claims](model-set-parity-harness-claims.md) — the matching rule for reading someone else's published cross-harness figure.
- [Isometric Harness Ablation](isometric-harness-ablation.md) — how to attribute a measured advantage to a single harness component.
