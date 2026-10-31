---
title: "Optional Runtime Tool Access for Fault Localization"
term: "Optional Runtime Tool Access"
description: "On short, precisely specified programs, instructing runtime-tool use costs 14.7-27.0x the tokens of no tools and beats optional access by at most 0.6 accuracy points. Provision the probe and the debugger; say nothing about using them."
tags:
  - testing-verification
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - "discretionary debugger access"
  - "unprompted runtime tool provisioning"
last_reviewed: 2026-10-29
maturity: emerging
---

# Optional Runtime Tool Access for Fault Localization

> On short, precisely specified, single-fault programs, keep runtime tool access optional and do not instruct its use. Instruction cost 14.7 to 27.0 times no-tools tokens.

Provision runtime tools without a prompt that tells the agent to reach for them. In a controlled fault-localization study, the instruction rather than the tool carried nearly all the cost, and agents left to choose bought the cheap evidence and skipped the expensive kind.

## When this applies

The result is measured in one narrow regime. Check all four conditions first.

1. The programs are short and self-contained. Admitted reference solutions had median non-empty line counts of 8, 11, and 19 across Easy, Medium, and Hard, drawn from LeetCodeDataset ([Daxerer et al., 2026](https://arxiv.org/abs/2610.36015v1)).
2. A precise specification ships with the code. Every case paired the faulty program with its original problem description, left unchanged by design, because localization needs a statement of intended behavior.
3. The defect is a single statement. The study seeded 610 single-line faults across five fault types, one per faulty program, and the prompt told the agent that exactly one bug had been injected.
4. The backbone is a current frontier model. Three were tested: Sol 6.1, Luna 6, and Qwen 3.8.

Outside these conditions, re-measure tool value. One repository-scale repair study found a large debugger gain: Claude 3.7 Sonnet resolved 37.2% of SWE-bench-Lite in rewrite mode, 48.4% with a `pdb` tool, and 52.1% when `pdb` arrived only after the fifth rewrite attempt ([Yuan et al., 2025](https://arxiv.org/abs/2503.21557v1)). The localization study concedes the boundary itself: its findings "do not generalize directly to multi-file repositories, incomplete specifications, or multi-statement defects, where the relevant state may not fit in the model's context and interactive debugging has shown larger gains" ([Daxerer et al., 2026](https://arxiv.org/abs/2610.36015v1)).

## What the measurement shows

Across 65,376 episodes on 610 untransformed and 3,022 behavior-preserving-transformed programs, three settings were compared: no tools, optional tools, and tools plus a two-sentence instruction to gather runtime evidence first. Transformed programs are the harder half, so the table reports those.

| Setting | Accuracy (Luna 6 / Qwen 3.8 / Sol 6.1) | Tokens per episode |
|---|---|---|
| No tools | 96.7% / 97.9% / 99.9% | 2.0k / 5.0k / 1.7k |
| Optional tools | 98.2% / 99.1% / 99.9% | 3.3k / 38.3k / 4.9k |
| Instructed tools | 98.8% / 99.2% / 99.9% | 55.0k / 73.5k / 32.2k |

"Without tools, all three agents operated near the accuracy ceiling", reaching 98.2% to 99.9% on the untransformed originals ([Daxerer et al., 2026](https://arxiv.org/abs/2610.36015v1)). Optional access then captured most of what was left. Instruction captured the rest, measured against optional access: "Instructing agents to use the tools raised the share of transformed episodes with a debugger action from 0.2 to 6.2% up to 41.7 to 100.0%, but raised accuracy by only +0.6 points for Luna 6 and +0.0 points for Qwen 3.8."

The bill is measured against no tools at all. Under instructed use, token counts ran "11.2 to 29.7 and 14.7 to 27.0 times no-tools" on untransformed and transformed programs respectively, and wall time "5.6 to 7.7 and 5.3 to 7.7 times" ([Daxerer et al., 2026](https://arxiv.org/abs/2610.36015v1)).

The surface agents declined was the interactive debugger specifically, taking debugger actions "in 0.0 to 0.9% of episodes on untransformed programs and 0.2 to 6.2% on transformed programs" ([Daxerer et al., 2026](https://arxiv.org/abs/2610.36015v1)). What they did instead split by model. Sol 6.1 and Qwen 3.8 ran a script against chosen inputs, in 98.4% and 93.6% of their transformed optional episodes. Luna 6 called no tool at all in 87.9% of its own, and ran only probes in 11.8% — and still gained +1.5 points over no tools.

## Why it works

One execution answers the question static reading gets wrong, and stepping answers it again more slowly. The two transformation recipes that cost accuracy rewrote loops and wrapped conditions in double negations. Because the prompt stated that exactly one fault had been injected, a doubly negated condition reads as that fault to a static reader. It cost them: 71.4% of Luna 6's and 68.2% of Qwen 3.8's new errors named one, on constructs making up 7.8% and 4.4% of lines. "Running the program shows that the condition evaluates as intended, which explains why both tool-enabled settings closed almost the entire accuracy gap between representations" ([Daxerer et al., 2026](https://arxiv.org/abs/2610.36015v1)).

So the evidence the agent needs is one observed value, and running the program yields it in a single turn. Breakpoints and stepping reach the same value over many: Luna 6 averaged 12.5 debugger actions per instructed transformed episode, 41.7% of them stepping ([Daxerer et al., 2026](https://arxiv.org/abs/2610.36015v1)). An instruction to gather runtime evidence does not say which evidence is cheap, so the agent buys the expensive kind.

The same study prices scaffolding against the obvious alternative. Sol 6.1 with no tools at all, at "99.9% accuracy, 5.2 s, 3.41 US dollars per 1,000 transformed episodes", was both more accurate and faster than Luna 6 or Qwen 3.8 with instructed debugging, at "98.8% in 47.0 s and 99.2% in 350.4 s". The conclusion for builders: "multi-turn debugging scaffolding on self-contained code cannot substitute for a stronger base model and is most cost-effective when left optional rather than forced by prompt instructions."

## How to provision

- Register the execution tool and the debugger together, with documentation, and leave the system prompt silent on when to use either.
- Report tokens and wall time per episode beside accuracy. The accuracy deltas here are fractions of a point and the cost deltas are multiples, so a single-metric dashboard hides the trade.
- Ship a tool that runs the specification's examples rather than a bare probe. Most probe scripts only printed output. Between 1.2% (Sol 6.1) and 25.6% (Qwen 3.8) "checked the return value via an in-script assertion or equality test instead of only printing outputs to inspect", so the authors suggest "dedicated tools that run specification examples automatically could further reduce probing overhead."

## When this backfires

- Repository-scale bugs. Carrying "leave it optional" to a multi-file bug tunes on the regime where the answer does not matter. debug-gym measures that regime and finds `pdb` worth 11 points to Claude 3.7 Sonnet ([Yuan et al., 2025](https://arxiv.org/abs/2503.21557v1)).
- Weaker or open-weight backbones. In debug-gym, `pdb` from the episode start moved GPT-4o from 19.1% to 17.2% and GPT-4o-mini from 4.0% to 3.5%, which the authors read as early debugger access harming weaker models. Llama-3.3-70B-Instruct went the other way, 2.4% to 4.0% ([Yuan et al., 2025](https://arxiv.org/abs/2503.21557v1)), so neither provisioning posture transfers without re-measurement.
- Missing or vague specifications. Without a statement of intended behavior there is nothing to compare an observed value against, and running the program resolves nothing.
- Agents that over-invoke anyway. Sol 6.1 ran probes in 98.4% of its optional transformed episodes while already localizing 99.9% without tools. Removing the instruction stops you mandating evidence; it does not stop the agent buying evidence it does not need.
- Token budgets loose relative to the cost of a missed fault. Instructed use never collapsed here: forced-answer rates stayed at or below 0.3% and no-answer rates at or below 0.1%. Where Luna 6's extra +0.6 points over optional access is worth its extra tokens, instruct it and pay.

## Key Takeaways

- Price the tool and the instruction separately. Optional access used 1.65 to 7.66 times the no-tools tokens on transformed programs; instructing use cost 14.7 to 27.0 times and beat optional access by at most +0.6 points.
- Static localization on short, precisely specified, single-fault programs runs at 96.7% to 99.9%, so little is left for a debugger to win.
- Agents given a choice reject interactive stepping, not execution: debugger actions in 0.2 to 6.2% of optional transformed episodes, against probe runs that outnumbered debugger actions for all three models.
- The strongest model with no tools beat weaker models with instructed debugging on accuracy and wall time, which prices scaffolding against a model upgrade rather than against doing nothing.
- One repository-scale repair study found a debugger benefit: `pdb` moved Claude 3.7 Sonnet from 37.2% to 48.4% on SWE-bench-Lite.

## Related

- [Execution Budgeting in Agentic Program Repair](execution-budgeting-program-repair.md) — The adjacent question: how often a repair agent should run tests, once execution is in the loop at all.
- [Verification as a Tool, Not an Instruction](tool-provided-verification.md) — The same availability-versus-prompting split measured on reference checking, where the ordering came out differently.
- [Function-Level Debugger Interfaces for Coding Agents](../tool-engineering/function-level-debugger-interfaces.md) — What to build once a debugger is worth shipping, which is the repository-scale case this page excludes.
- [Precise Debugging: Measure Edit Precision, Not Just Test Pass Rate](precise-debugging-benchmark.md) — Why a localization metric and a repair metric answer different questions.
- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — Ordering cheap evidence ahead of expensive evidence as an explicit pipeline rather than a prompt.
