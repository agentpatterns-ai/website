---
title: "Delegating Multi-Hunk Bug Repair to Coding Agents"
description: "Multi-hunk bugs need edits in several places. Enumerate every edit site first, treat new failures in untouched files as missed edits, and set any budget cap from your own runs."
tags:
  - workflows
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-30
maturity: emerging
---

# Delegating Multi-Hunk Bug Repair to Coding Agents

> Multi-hunk bug repairs fail when agents miss edit sites, so list every site before the agent edits.

A multi-hunk bug is a single defect whose fix spans several separate edit regions, often across files. Coding agents repair these less often as the regions spread apart. Nashid et al. ran four agents over 404 multi-hunk bugs (372 Java, 32 Python) and found repair accuracy "consistently declines with increasing bug dispersion and complexity (hunk divergence and spatial proximity)" ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)).

The Java bugs ran between September and November 2025 and the Python bugs between April and May 2026. The study began with Claude Code 2.0.13, Codex 0.21.0, Gemini-cli 0.10.0, and Qwen Code 0.0.11. The authors saw Claude Code and Qwen Code auto-update during the study. Treat the rankings as a snapshot, not a current comparison.

## When this applies

The actions below apply when one defect needs the same or related change at several locations. They add little for a bug fixed by one edit. The budget cap applies only if you have run history for your own agent and task mix, and it pays most for agents that fail often. The conditions where it backfires are listed near the end of this page.

## What the study measured

Accuracy on the 404 bugs: Claude Code (Sonnet 4.5) 92.82%, Codex (GPT-5) 87.38%, Gemini-cli (2.5 Flash) 43.07%, and Qwen Code (qwen3-coder-flash) 26.98% ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)).

Failed repairs cost more than successful ones. In dollars, a failed attempt cost 1.3 to 5.4 times a successful one, and failed runs averaged 723.91 s against 285.57 s ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)). For input tokens the direction depends on the agent:

| Agent | Failed vs. successful input tokens |
|-------|------------------------------------|
| Codex | +32.5% |
| Qwen Code | +44.1% |
| Gemini-cli | +440.4% |
| Claude Code | 69.4% fewer new input tokens, 110.5% more cache read tokens |

The Claude Code row reverses because of prompt caching. Its failed runs still produced 55.1% more output tokens ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)). Codex token counts are estimates: the tool does not log them, so the authors counted them with tiktoken.

## Steps

### 1. Score difficulty before you delegate

Count the hunks the fix probably needs and how many files they touch. Every agent in the study fixed bugs with lower hunk divergence more often than bugs with higher divergence, with failing repairs reaching a median of 0.47 for Claude Code, Codex, and Gemini-cli ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)).

File count alone is a weak signal. Of the 12 bugs no agent fixed, 58.33% were cluster-type bugs, and the authors conclude that "physical co-location of changes does not guarantee a successful repair by coding agents" ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)).

### 2. Enumerate the edit sites first

Ask the agent to list every location the change touches before it edits anything. The paper's recommendation is direct: "When a bug requires repeated changes across multiple locations, agents should first identify the full set of relevant locations before applying edits." It suggests a call-site enumeration step using repository search or static analysis, then a check during editing that every site is covered ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)).

You can do this yourself in the prompt: run the search, paste the list, and tell the agent to tick each entry off.

### 3. Trace downstream uses after an entry-point fix

The authors describe a common failure: "these agents apply entry-only fixes: they adjust the input but do not follow how that change affects the rest of the function" ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)). After the first fix, tell the agent to follow the changed value through the rest of the function and its callers.

### 4. Read new failures in untouched files as missed edits

The paper's advice: "when new test failures appear in files the agent did not modify, they should be treated as contextual cues of missing edits" ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)). When a test fails in a file the agent never opened, add that file to the site list instead of asking for a patch to the test.

### 5. Watch for the failure signature of your agent

The study found two failure modes: "over-modification without validation and over-exploration without action". It also found that no single pattern covers every agent. Gemini-cli "requires reducing excessive modification and increasing validation, while Claude Code requires reducing excessive search and increasing code modification" ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)).

For Gemini-cli the observable sign is a run of consecutive writes with no build or test between them. Three consecutive writes made up 11.55% of the three-step tool-call windows in failed repairs against 4.50% in successful ones ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)). Interrupt a run that shows the sign for your agent, and ask for a build or test before the next edit.

### 6. Cap the budget from your own history

Failed runs run long because "failures do not terminate early; agents persist through multiple unsuccessful attempts before giving up" ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)). A cap can cut that spend. The paper tests no cap, so treat this step as an inference from two findings and not a measured result.

Set the cap above the range where your agent normally succeeds. Devstral's ablation shows why. Raising the iteration limit from 30 to 50 lifted the resolve rate from 36.8% to 46.8%, and going from 50 to 100 gave no gain ([Devstral, v1](https://arxiv.org/abs/2509.25193v1)). A cap below the working range removes successes.

Meter the counter your harness spends. On a cache-heavy harness, a cap on new input tokens does not track the extra spend of a failing run, because failed runs average fewer new input tokens (245 against 799) while cache reads rise. For calibrated stopping and static cap design, see [early termination and warm restart](../loop-engineering/early-termination-and-warm-restart.md) and [loop budgeting](../loop-engineering/loop-budgeting.md).

## Why it works

Multi-hunk failures come from coordination, not from writing a single hunk badly. Agents "focus on local context and fail to apply the change to all required locations", so a list of sites and a follow-the-value step supply what the agent would otherwise skip ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)). Localization does not guarantee repair either: at least one agent found the right location for 7 of the 12 unsolved bugs, and none fixed them ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)). Finding the site is one step, and editing every site is another.

## When this backfires

- The agent already succeeds often. Claude Code and Codex reached 92.82% and 87.38% here, so failures are a small share of their spend. From the paper's Table 7 per-bug costs and Table 3 counts, a derived estimate puts failures at about 13% of Claude Code spend and about 20% of Codex spend (the paper does not state these figures). A tight cap saves little there and cuts late successes.
- The bug is dispersed. Claude Code and Codex still fixed 86.67% and 73.33% of the most dispersed (Fragment-class) bugs in the study. A flat cap set for typical bugs may cut some of those successes.
- You copy a cap from another agent. The failed-run gap runs from +32.5% to +440.4% across agents, so a number tuned for one agent is uncalibrated for another.
- The token gap reflects harder bugs. Failures cluster on high-divergence bugs, so extra spend may come from task difficulty and not from wasted persistence.
- A developer is waiting. Watching for the failure signature in step 5 is cheaper than a global budget, and the paper asks tool builders to engineer agents to detect unproductive repair paths and "fail fast".
- The Python results are thin. The Python subset has 32 bugs, and the authors caution that results on the benchmark may be sensitive to the limited sample size. Claude Code's regression reduction falls from +2.47 on Java to -1.43 on Python ([Nashid et al., v3](https://arxiv.org/abs/2511.11012v3)).

## Key Takeaways

- List every edit site before the agent edits, and have it tick each off.
- A new test failure in a file the agent did not touch points to a missed edit.
- Failed multi-hunk runs cost more for Codex, Qwen Code, and Gemini-cli, but Claude Code reverses the new-input-token gap under caching.
- The study tests no budget cap. Set one from your own run history, above the range where runs normally succeed.
- Failure signatures differ by agent, so one stopping rule does not fit all of them.

## Related

- [Early Termination and Warm Restart](../loop-engineering/early-termination-and-warm-restart.md)
- [Loop Budgeting](../loop-engineering/loop-budgeting.md)
- [Failure Trajectory Recovery Window](../patterns/agent-design/failure-trajectory-recovery-window.md)
- [Per-Task Agent Routing](../patterns/agent-design/per-task-agent-routing.md)
- [Per-Task Verification Budget](per-task-verification-budget.md)
