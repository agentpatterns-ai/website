---
title: "Verification Surface: Match the Tool to the Failure"
term: "Verification Surface"
description: "A controlled study of 1,116 agent builds ranks self-check tools by reach and token cost: a boot probe costs less than no tool at all, a shell costs 2.35x, a linter bought nothing."
tags:
  - testing-verification
  - cost-performance
  - arxiv
  - tool-agnostic
aliases:
  - verification surface
  - agent self-check tools
  - tool reach and verification cost
last_reviewed: 2026-09-01
maturity: emerging
---

# Verification Surface: Match the Tool to the Failure

> A checking tool raises artifact quality only where its reach covers how the application fails, and the cheapest tool returns most per token.

The verification surface is the set of tools an agent can use to check its own work: a linter, a boot probe, a shell, a screenshot tool. Widening it does not buy quality in proportion. In a controlled study that held the model, the prompt, and the task fixed and varied only the tool list across 1,116 web-application builds, each tool moved the measure whose failures it could observe and left the rest flat ([Mehta, arXiv:2608.28795v1](https://arxiv.org/abs/2608.28795v1)).

## Conditions this holds under

The study measured seven web-application specs, six models, and four to five replicates per cell, with a single condition-blind human grading every build against a frozen rubric ([Mehta, arXiv:2608.28795v1](https://arxiv.org/abs/2608.28795v1)). Three conditions decide whether the ranking below transfers.

- Your artifact has something to boot. The cheapest win is a server that starts. A library, a data transform, or a CLI has no equivalent, and the base rate that makes the probe pay does not exist there.
- Your model still fails without help. The survival gain concentrated in two of six models, gemini-3.1-pro gaining 50 points and gpt-5.5 gaining 20, while the rest sat near 100 percent already. The paper is blunt about it: "the strongest model gained nothing from any tool, because it already scored perfectly on the API tasks while building blind. The weakest model gained 37 points once it was handed a shell."
- You can name the failure mode. Reach is only actionable if you know what breaks. Where you cannot guess, buy the wider surface.

## What each rung buys and what it costs

Median tokens per build across all 1,116 runs, against the quality each condition reached ([Mehta, arXiv:2608.28795v1](https://arxiv.org/abs/2608.28795v1)):

| Tools given | Median tokens | Builds that launched | What it adds |
|---|---|---|---|
| None | 262k | 86.5% (166/192) | Baseline |
| Linter and type checker | 276k | 84.4% (162/192) | Nothing measurable |
| Boot probe only | 214k | 99.5% (191/192) | Nearly every launch failure |
| Full shell | 615k | 99.0% (190/192) | Behavior under concurrency and restart |
| Shell plus screenshots | 674k | 99.4% (173/174) | A suggestive gain on visual layout |

The boot probe is the only configuration that costs less than handing the agent no tools at all. On the API-probed tasks the mean functional score runs "no_verification 81.9, static 78.3, boot_check 91.7, execution 94.2, and visual 92.6", and the split is lopsided: "Of the twelve functional points that separate blind builds from shell builds, ten arrive with the boot probe alone."

Above that rung the returns narrow and the price does not. The shell earns its remaining two points on probes that fire simultaneous requests, kill and restart the app, and check ordering under load. Screenshots reach one more class of defect, visible layout and interaction, and the paper reports that gain honestly as unproven: pooled across the two visually hard tasks it is "+6.9 points, 95 percent confidence interval [+0.8, +13.4], permutation p = .041, which does not survive the six-way family holm-corrected p (corrected p = .083)."

## Why it works

Two mechanisms run in opposite directions, which is why the ranking is not simply "more tools cost more". Take cost first. Agent bills are [input-dominated because the harness re-sends the conversation on every step](../token-engineering/harness-token-economics.md), so an agent that finishes in fewer steps pays less to re-read its own session. Boot-probe runs "finish in fewer steps than blind runs (a median of 17 against 19) and re-read far less (195 thousand input tokens against 247 thousand)" ([Mehta, arXiv:2608.28795v1](https://arxiv.org/abs/2608.28795v1)). One added tool lands cheaper than none because it shortens the session it has to pay for.

Quality is a question of observability. A tool changes the artifact only where it can see the defect, so each measure stops improving at the rung where the added reach runs out: once 99.5 percent of builds start, a stronger tool has no launch failures left to prevent. This is the same [feedback loop that makes agents self-correct](../patterns/agent-design/agent-backpressure.md), narrowed to what each signal can actually detect.

## When this backfires

- A linter is not verification here. The static condition "did no better than having no tools at all", and it was not even protected from the defect it exists to catch: ten builds shipped a frontend that could never render because of a parse error, and "Five of those ten were encountered in the static condition." One build called the linter once, got an error back because it had never wired the tool up, and never checked again. A tool the agent can decline to run has no reach at all ([Mehta, arXiv:2608.28795v1](https://arxiv.org/abs/2608.28795v1)).
- "Listens" is not "works". The boot probe confirms the server accepts connections and nothing more. The paper's graded defects include an SQL type error that crashes the summary endpoint on first call and a permanently false error banner, both passing the probe untouched ([Mehta, arXiv:2608.28795v1](https://arxiv.org/abs/2608.28795v1)).
- Screenshots lose where failures live in motion. On a log viewer with over 100,000 rows, the shell tops the ladder at 93.8 and screenshots fall behind at 91.7, because a still image of a stuttering list and a smooth one are the same image. The committed contrast for adding sight there is "−2.2 against the shell, interval [−12.5, +7.3]" ([Mehta, arXiv:2608.28795v1](https://arxiv.org/abs/2608.28795v1)).
- Letting the agent write its own tests instead is worse than handing it a shell. That arm scored "−16.1 points, 95 percent interval [−31.7, −1.7], p = .043" on the automated probes, negative for five of six models, and it stopped early with budget left: 369 thousand tokens against the shell's 810, 22 steps against 49. A model's tests encode its own understanding of the task, so a wrong understanding ships with a green suite. That is [assertion-free test theater](../patterns/anti-patterns/assertion-free-test-theater.md) arriving one level up ([Mehta, arXiv:2608.28795v1](https://arxiv.org/abs/2608.28795v1)).
- The evidence is one v1 preprint by one author. The human interface scores "come from a single grader", three tasks have no automated tests at all, and an independent study of tool-augmented agents in a different domain found "little consistent aggregate improvement" from tool access, with 93 percent of one agent's tool-solved problems also solved without tools ([Guo et al., arXiv:2606.02357v1](https://arxiv.org/abs/2606.02357v1)).

## Example

The linter result is the one that should change a habit. Static analysis is the reflexive first thing to hand an agent: cheap, familiar, already in the repo. In this study it cost 14k more median tokens than no tools, started slightly fewer builds, and scored slightly lower on behavior, all within noise. Then the frontend audit made it worse than a wash. Half the study's unrenderable frontends came from the one condition equipped to catch exactly that error ([Mehta, arXiv:2608.28795v1](https://arxiv.org/abs/2608.28795v1)).

A boot probe is a weaker tool by any static-analysis standard. It cannot read code and knows one fact. It left one launch failure in 192 builds where building blind left 26, at 48k fewer median tokens, and with the lowest run-to-run cost spread in the study at 47K tokens against the widest configuration's 408K ([Mehta, arXiv:2608.28795v1](https://arxiv.org/abs/2608.28795v1)). Reach beat sophistication.

## Key Takeaways

- Provision the verification surface against the failure mode you actually get, not against tool capability. A tool that cannot observe your defect class contributes nothing at any price.
- Start with the cheapest runnable check. A boot probe removed nearly every launch failure at roughly 35 percent of a full shell's token cost, and cost less than giving the agent no tools at all.
- Buy a shell when behavior under load, restart, or concurrency matters, and price it honestly at 2.35 times the no-tools baseline.
- Treat screenshots as cheap insurance on visually hard work, not as interaction testing. The gain did not survive correction for multiple comparisons, and it reversed on a task whose failures were measurable rather than visible.
- Decide the budget per model. The strongest model in the study gained nothing from any tool; the weakest gained 37 points from a shell.

## Related

- [Reasoning Effort Over Tool Scaffolding for First-Try Reliability](../patterns/agent-design/reasoning-effort-over-tool-scaffolding.md) — the same author's earlier observational study, which compared the reasoning dial against the tool dial; this page holds capability fixed and ranks the tools against each other
- [Verification Capacity as the Agent Quality Ceiling](verification-capacity-quality-ceiling.md) — the throughput question, how much checking you can run per hour; this page is the composition question, which checks to run at all
- [Incremental Verification: Check at Each Step, Not at the End](incremental-verification.md) — when to fire the checks this page selects
- [Agent Backpressure: Automated Feedback for Self-Correction](../patterns/agent-design/agent-backpressure.md) — the loop that consumes these signals
- [Assertion-Free Test Theater in Agent-Authored Patches](../patterns/anti-patterns/assertion-free-test-theater.md) — why an agent's own test suite is the weakest rung on this ladder
