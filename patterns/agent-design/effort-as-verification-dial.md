---
title: "Effort as a Verification Dial: What a Higher Level Buys"
term: "Effort as a Verification Dial"
description: "Effort buys self-verification and edge-case testing. Raise it where hidden cases decide the result, keep it low where the risk is a misread requirement."
tags:
  - agent-design
  - cost-performance
  - claude
  - reliability
aliases:
  - effort as a verification dial
  - verification-keyed effort selection
  - choosing an effort level by work type
last_reviewed: 2026-10-01
maturity: emerging
status: current
---

# Effort as a Verification Dial: What a Higher Level Buys

> Effort buys the model's own verification and edge-case testing, so a higher level pays where hidden cases decide the result.

An effort level is an allowance of compute the model spends checking its own work and deciding things you left unspecified. Thariq Shihipar ran the same build tasks at several levels on Opus 5.5 and read the Terminal-Bench 3.0 results for Opus 5.5 and Fable 5.1. His finding: "effort was a great way of modulating how much verification and edgecase testing Claude did and how much of its own judgement it used" ([Shihipar, claude.dev, 2026](https://claude.dev/blog/spending-your-effort/)). So the selection question is what your remaining risk is made of.

## The condition that decides it

Raise the level when the remaining work is finding cases you have not thought of. Keep it low when the remaining work is agreeing on what to build.

Terminal-Bench 3.0 splits along that line: "increasing effort tends to reduce failures due to missing edgecases (purple blocks), but does not fix when the model has the wrong approach (blue blocks)" ([Shihipar, 2026](https://claude.dev/blog/spending-your-effort/)). Over 370 attempts at each setting, Fable 5.1 cut missed-case failures from 59 to 24 between low and max. Wrong-call failures fell only from 133 to 107, and one sub-kind moved the other way: picked the wrong reading rose from 25 to 47. Median spend tripled over the same interval, 73k tokens to 222k. The failure labels come from a model judge and are approximate, so read the direction rather than the digits.

## Where it pays, by category

Fable 5.1 pass rates by task category on Terminal-Bench 3.0, low effort to top effort, as the source's Figure C pools them ([Shihipar, 2026](https://claude.dev/blog/spending-your-effort/)):

| Category | Tasks | Low | Top |
|---|---|---|---|
| Security | 7 | 64% | 87% |
| Hardware | 5 | 34% | 75% |
| ML | 13 | 54% | 73% |
| Science | 15 | 41% | 61% |
| Software | 20 | 43% | 56% |
| Media | 4 | 18% | 30% |
| Operations | 10 | 12% | 22% |

Security and hardware gain 23 and 41 points, and those are the categories where an undiscovered case is most of the task. Operations gains 10 and finishes lowest, under a figure captioned "Rulebook-style work stays low".

Figure C pools settings because categories are small: "Low effort pools each model's two lowest settings, top effort its three highest". The runs are Anthropic's own, at 5 attempts per task, with Fable 5.1's production safety interventions off and the security tasks offline. The counts therefore do not line up with the public leaderboard.

## Why it works

The allowance is spent on checking, so the payoff is capped by how much of the difficulty is discoverable by checking. On the `html-js-filter` sanitizer task, a low-effort attempt wrote a filter in roughly one pass and tested it against a single hand-written page, in about 2 minutes. A high-effort run finishing in about 33 minutes "adversarially reviewed its first draft, then read the installed parser's source to check for bugs", ran a standard XSS suite, and wrote a fuzzer ([Shihipar, 2026](https://claude.dev/blog/spending-your-effort/)). Checking finds cases. It cannot correct a requirement the model read wrong, and a longer chain has more opportunity to attach to irrelevant material ([Inverse Scaling in Test-Time Compute, arXiv:2507.14417v2](https://arxiv.org/abs/2507.14417v2)).

The same allowance covers judgement, which is why a thin prompt turns it into decisions on your behalf: "higher effort levels will get more work done but Claude will also make more assumptions on my behalf" ([Shihipar, 2026](https://claude.dev/blog/spending-your-effort/)). Asked for a fitness tracker with no further detail, low effort returned a log and a simple graph in 1.5 minutes. Max effort spent 67 minutes and added a heat chart.

## When this backfires

- Rulebook-bound work. Operations stayed the weakest category at top effort, because the gap is knowledge of the rule rather than coverage of cases ([Shihipar, 2026](https://claude.dev/blog/spending-your-effort/)). Checking does not teach the model a filing rule it never had.
- The requirement is misread rather than under-verified. Picked-the-wrong-reading failures nearly doubled from low to max ([Shihipar, 2026](https://claude.dev/blog/spending-your-effort/)), which is consistent with, though not shown to be, the distraction failure that paper reports for Claude models: as reasoning lengthens, "Claude models become increasingly distracted by irrelevant information" ([arXiv:2507.14417v2](https://arxiv.org/abs/2507.14417v2)).
- You plan to iterate on a thin prompt. The author's own split: "If I wanted a simple base to iterate from, low effort would get it done. Max effort would be if I wanted Claude's best one shot" ([Shihipar, 2026](https://claude.dev/blog/spending-your-effort/)).
- The run is bounded by wall clock rather than tokens. On Terminal Bench 2.0, a `gpt-5.2-codex` harness "running only at `xhigh` scored poorly at `53.9%` due to agent timeouts compared to `63.6%` at `high`" ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)).
- You are setting one default for a mixed fleet. Over 21,730 rollouts on 9 models and 9 benchmarks, the Holistic Agent Leaderboard reports "higher reasoning effort reducing accuracy in the majority of runs" ([arXiv:2510.11977v1](https://arxiv.org/abs/2510.11977v1)). The curves above come from one vendor's runs on two models; the leaderboard figure is a population average.

## Example

The `mvcc-lsm-compaction` task asks for a fix to a storage-engine bug from its crash report without breaking compaction. Opus 5.5 went from 0/5 at low to 4/5 at xhigh, and the traced runs show where the extra time went ([Shihipar, 2026](https://claude.dev/blog/spending-your-effort/)):

**Before** — low effort, about a minute per attempt: Claude "would edit the code before building it or running the reproducer, and did not check that its new test would have caught the original bug."

**After** — xhigh effort, about 11 minutes: Claude "reproduced the crash first, wrote a randomized test against a reference that never compacts, and checked that its tests failed on half-finished fixes."

Every step the xhigh run added is a check, which is the shape of task where the dial earns its cost. Switch per task or mid-session with `/effort` in Claude Code; the newest Claude models respond to effort "without breaking the prompt cache", so a change inside one session does not pay for a cold prefix ([Shihipar, 2026](https://claude.dev/blog/spending-your-effort/)).

## Key Takeaways

- Classify the remaining risk before you pick a level: undiscovered cases call for more effort, an unsettled requirement calls for a conversation.
- Place your own work against the category table before you trust a default. The low-to-top spread ran 41 points in hardware and 10 in operations.
- Budget the dial for coverage. Missed-case failures more than halved while wrong-call failures barely moved.
- Specify the task before you raise the level on a thin prompt, because higher effort makes more assumptions on your behalf.
- Measure your own queue before you standardize on a level. The vendor curves cover two models, and the 21,730-rollout average runs the other way.

## Related

- [Reasoning Budget Allocation: The Reasoning Sandwich](reasoning-budget-allocation.md) — varying the same dial across phases of one run rather than across tasks.
- [Dispatch-Time Reasoning Level for Delegated Agents](dispatch-time-reasoning-level.md) — picking the level when the run leaves your view and you cannot correct it.
- [Reasoning Effort Over Tool Scaffolding for First-Try Reliability](reasoning-effort-over-tool-scaffolding.md) — the competing claim on the same budget.
- [Interactive Effort Sliders: Per-Turn Reasoning-Budget Controls](interactive-effort-sliders.md) — the operator surface this selection runs on.
- [Know When Not to Add Structured Reasoning](../anti-patterns/reasoning-overuse.md) — the cost side of raising the dial by default.
