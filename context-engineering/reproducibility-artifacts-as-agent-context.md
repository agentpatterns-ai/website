---
title: "Reproducibility Artifacts as Agent Context"
term: "Reproducibility Artifacts as Agent Context"
description: "Tests, commit history, repository layout, instructions, and decision records double as agent context, but each loads through a different channel and only the non-discoverable slice belongs in always-on instructions."
aliases:
  - reproducible research as context engineering
  - research artifacts as agent context
tags:
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-11
maturity: emerging
---

# Reproducibility Artifacts as Agent Context

> Reproducibility artifacts double as agent context, but each loads through a different channel, and only the non-discoverable slice belongs in always-on instructions.

The artifacts a project maintains so a stranger can rerun its work are the same artifacts an agent reads to work in it. Two conditions decide what that is worth. The five reach the agent through different channels at different costs, so treating them as one block of always-on context spends budget on items that should be executed or queried instead. And the argument inverts when the agent's job is to check the claim an artifact asserts rather than build on it.

## Five artifacts, five loading channels

Lorena Barba tabulates five artifacts against a context category each: the agent instruction file as always-on semantic memory, the test suite as executable semantic memory, commit history as episodic memory, repository structure as pre-processed context, and the decision record as static context, where "settled questions are not relitigated" ([arXiv:2609.11728v1](https://arxiv.org/abs/2609.11728v1)). Her table costs each artifact by what it takes to produce. It does not cost what it takes to keep in context, and those are different budgets.

| Artifact | Context role | How it reaches the agent | What it charges |
|---|---|---|---|
| Instruction file | Always-on semantic memory | Loaded whole, every session | Tokens, unconditionally |
| Decision record | Static context | Read when a settled question resurfaces | Tokens, on demand |
| Commit history | Episodic memory | Queried through `git log` | Tokens, on demand |
| Repository structure | Pre-processed context | Walked with the agent's own file tools | Turns, not tokens |
| Test suite | Executable semantic memory | Run as a self-check, not read | One tool call |

Only the first row charges on every session whatever the task, and it is also the row that grows: a study of 2,303 context files from 1,925 repositories found them "not static documentation but complex, difficult-to-read artifacts that evolve like configuration code" ([arXiv:2511.12884v2](https://arxiv.org/abs/2511.12884v2)).

Apply the test from [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md) row by row and the set splits. Layout and commit history are discoverable, so describing them in always-on context pays twice for one fact. The decision record survives outright, because reasoning nobody committed cannot be recovered from the tree.

## Why it works

Barba's mechanism is that reproducibility practice externalizes an author's tacit knowledge into durable, legible artifacts, and an agent is the extreme case of the reader they were written for, because it arrives "with no shared history at the start of every session"; the artifact "does not know whether the stranger consulting it is human or machine" ([arXiv:2609.11728v1](https://arxiv.org/abs/2609.11728v1)). The paper argues this and measures nothing.

The nearest independent support is behavioral. On SocSci-Repro-Bench, 221 reproduction tasks across four disciplines, two frontier coding agents reproduced a large share of published social-science findings from the data and code alone ([arXiv:2606.11447v1](https://arxiv.org/abs/2606.11447v1)). Two corpora show developers already writing down most of the same set, under different labels. Matt Nigh's analysis of over 2,500 `agents.md` files reports that the top tier covers "commands, testing, project structure, code style, git workflow, and boundaries" ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)). The 2,303-file study finds test procedures in 75.9% of files, implementation detail in 70.8%, and architecture in 68.1% ([arXiv:2511.12884v2](https://arxiv.org/abs/2511.12884v2)). Both count what developers wrote. Neither measures whether it helped, which is the standing caution in [Public Rules-File Corpora as Evidence](../instructions/rules-file-corpus-evidence.md).

## When this backfires

### The agent is verifying, not producing

Supplying the artifact that states the expected result biases the agent toward producing that result. When Alizadeh et al. handed agents the original paper PDF alongside the replication materials, Claude Code's accuracy on non-reproducible tasks fell from 100.0% to 63.3% and Codex's from 100% to 90.0%; the agents "tend to extract the expected numerical output rather than correctly diagnosing an execution failure" ([arXiv:2606.11447v1](https://arxiv.org/abs/2606.11447v1)). More context made overall performance better and diagnosis worse.

### Everything lands in the instruction file

Describing all five artifacts in the always-on file charges per-session tokens for four that are executed or queried. [Context Budget Allocation](context-budget-allocation.md) covers the trade; [Agent Context File Evolution](../instructions/agent-context-file-evolution.md) covers the drift that follows.

### The artifacts are agent-written and unread

Barba names this failure directly: "A test you do not read is worthless; a decision record you did not reason through records nothing you know" ([arXiv:2609.11728v1](https://arxiv.org/abs/2609.11728v1)). A generated suite raises the coverage number and lowers the signal.

### The repository is short-lived

The cost case is bound to the timescale of a codebase. A prototype discarded in three weeks never reaches the horizon where commit discipline or a decision record repays its cost.

### Regeneration does not reproduce

Barba raises this against her own case: "AI generation is probabilistic; models change underneath you; the same prompt on the same code may produce different output next month." Her answer is that the argument runs at a different layer: "The claim is not that the path by which code came to exist is reproducible; it is that the code, once it exists, is legible, tested, and accounted for" ([arXiv:2609.11728v1](https://arxiv.org/abs/2609.11728v1)). That holds for the test suite, which pins behavior whatever wrote it. It holds less well for the instruction file and the decision record, whose worth is the reasoning they carry rather than a behavior anything can re-run.

## Key Takeaways

- Sort reproducibility artifacts by loading channel before deciding what to write down. Only the instruction file charges tokens on every session, so that is the row to ration.
- Name the layout and the log in the instruction file; do not transcribe them. The agent's own file and git tools supply the rest.
- Write the decision record first if you write only one artifact. It is the one whose content no tool can recover.
- Withhold the artifact that asserts the answer when the agent's task is to verify it. Paper access cut Claude Code's accuracy on non-reproducible tasks from 100.0% to 63.3% ([arXiv:2606.11447v1](https://arxiv.org/abs/2606.11447v1)).
- Treat the convergence argument as a position, not a result. The corpus studies behind it count authorship rather than effect.

## Related

- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md) — the test that splits the five artifacts into always-on and on-demand
- [Context Budget Allocation](context-budget-allocation.md) — what a token preloaded into always-on context displaces
- [Agent Context File Evolution](../instructions/agent-context-file-evolution.md) — how instruction files grow once every convention lands in them
- [Public Rules-File Corpora as Evidence](../instructions/rules-file-corpus-evidence.md) — why corpus convergence is authorship evidence, not efficacy evidence
- [Encoding Tacit Knowledge into Agent Improvement Loops](../workflows/encoding-tacit-knowledge.md) — eliciting the judgment that never reached an artifact
