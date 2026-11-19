---
title: "Stale Bug-Reference TODOs as Coding Agent Distractors"
term: "Stale Bug-Reference TODOs"
description: "Bug-linked TODOs sat in 13% of Google's agent file-reading sessions. Unprompted bug detours added 70% more steps. Delete closed-ticket TODOs only after a history check."
aliases:
  - stale TODO comments
  - agent distraction from stale TODOs
tags:
  - anti-pattern
  - context-engineering
  - tool-agnostic
last_reviewed: 2026-11-09
maturity: emerging
---

# Stale Bug-Reference TODOs as Coding Agent Distractors

> Bug-linked TODOs can send coding agents on unprompted detours; at Google, sessions with such a detour ran 70% more steps.

A stale bug-reference TODO is an inline `TODO(bug/...)` or `FIXME(bug/...)` comment that outlives the ticket it points to. A developer skims past it. A coding agent reads it while researching the task, and sometimes acts on the ticket ID by looking up the bug or editing the code. Google measured unprompted detours on bug-linked TODOs of any ticket status across millions of sessions, including their cost ([Saccone and Garikapati, Google Developers Blog](https://developers.googleblog.com/agent-distraction/)).

## When the evidence applies

Google's numbers transfer to your codebase only where these hold:

- Your TODOs carry ticket IDs. Google picked bug-linked TODOs because "the linked bug ticket acts as the canonical record" ([Google](https://developers.googleblog.com/agent-distraction/)). Free-text TODOs were not measured.
- Your agent can search the tracker or the code. In Google's worked example the agent ran "multiple Code Search and internal knowledge search queries for the bug" ([Google](https://developers.googleblog.com/agent-distraction/)).
- Nobody asked the agent to work on that ticket. A lookup the developer asked for is the task itself.

## The pattern

A team closes the ticket and leaves the comment, because the ticket holds the real status and human readers skip the comment. Google found that "TODOs tend to be left behind long after the underlying bug is resolved or abandoned" ([Google](https://developers.googleblog.com/agent-distraction/)).

## Why it fails

Agents ignore most encounters. The cost sits in a small share that the agent acts on without being asked ([Google](https://developers.googleblog.com/agent-distraction/)):

| Measure | Value |
|---|---|
| File-reading sessions that exposed the agent to a bug-linked TODO or FIXME | 13% |
| Encounters the agent ignored | 94% |
| Encounters where the agent acted on the bug ID | 6% |
| Share of those actions the developer did not ask for | 83% |
| Unprompted detours on a closed ticket | 41% (32% fixed or verified, 9% obsolete or won't-fix) |
| Unprompted detours on an open ticket | 57%, and 39% of these edited code |

The two halves fail differently. On a closed ticket the agent researches work that is already fixed or abandoned. On an open ticket it expands scope to "investigate or modify an issue the developer never asked to touch".

Google controlled for developer, codebase complexity, task type, model tier, files read, prompt length, and the step where the reference appeared. Unprompted detours still added 70% more steps, 77% more tokens, and 105% more wait time per session, all at p<0.0001 ([Google](https://developers.googleblog.com/agent-distraction/)).

## Why it works

The authors offer an explanation they did not test: "What is easy for humans to skim past in code, agents see as a call to action" ([Google](https://developers.googleblog.com/agent-distraction/)). The bug ID gives the agent something to look up, and in Google's second example it ran search queries for the bug before editing code. The regression ties detours to cost, but the design is observational. It does not explain why agents act on 6% of encounters and ignore the other 94%.

Deleting the reference removes the thing the agent would look up. Google's cleanup agents first found references whose tickets were marked fixed or obsolete. Status alone "was not enough to determine if the TODOs in the codebase were load-bearing or not". The agents also read the history of the bug, the file, and changes to the codebase. They sent a deletion for review only when they confirmed the TODO "and the intent behind the TODO was obsolete". Over six months the cleaner removed thousands of references, "exceeding 95% acceptance from human reviewers" ([Google](https://developers.googleblog.com/agent-distraction/)).

## When this backfires

- A sweep by ticket status alone deletes comments that still carry intent, which is why Google's agents read history first ([Google](https://developers.googleblog.com/agent-distraction/)).
- Deletion reaches only the closed-ticket share. Google's cleaner targeted references "marked as fixed or obsolete", while 57% of unprompted detours hit open tickets whose TODOs stay in the code ([Google](https://developers.googleblog.com/agent-distraction/)).
- Comments as a class help. Vitale and colleagues report that comments raise LLM automated bug-fixing accuracy "by up to threefold when present in both phases" ([arXiv:2601.23059v1](https://arxiv.org/abs/2601.23059v1), abstract). Remove the dead reference, not comments in general.
- The cost figures cover unprompted detours only, which were 83% of actions. When the developer asks about the ticket, the TODO is the right context.
- Your repository may not pay the cost. The evidence is one company's codebases and agents, published as a blog post. A young repository with few aged TODOs has little to clean.

## Example

Google published two trajectories ([Google](https://developers.googleblog.com/agent-distraction/)). In the first, an agent investigating an unrelated bug read `SurfaceControlTest.java` and found `// TODO(bug/XXX)`. The bug was fixed in 2023, and the agent spent the following steps digging into it.

In the second, an agent found a TODO in the bug it was investigating and decided, unprompted, to fix it. It ran Code Search and internal knowledge queries for the bug, then changed the `ModelDownloaderV1` code. Later the human challenged the scope creep, and the model admitted it was an incorrect increase in scope. The authors call both detours "trivial to minor", but "real distractions costing time, tokens, and human intervention".

## Key Takeaways

- Bug-linked TODOs of any ticket status appeared in 13% of file-reading sessions. Check ticket status before treating a reference as obsolete.
- Find out whether you pay the cost by cross-referencing the TODOs agents read against ticket status and the user's prompt, as Google did.
- Delete a reference only after the bug, file, and code history confirm its intent is dead. Ticket status alone deletes load-bearing comments.
- Cleanup cannot remove the whole cost. Open-ticket TODOs stay in the code, and they drew 57% of unprompted detours.

## Related

- [Seeding Agent Context](../../context-engineering/seeding-agent-context.md) — recommends TODO markers as a way to steer agents; this page measures the same channel after the ticket closes
- [Comment Content as Code-Generation Context](../../context-engineering/comment-content-as-generation-context.md) — a comment written for a different problem costs pass@1, the generation-side twin of this detour
- [Stale AI Configuration Artifacts (Context Rot)](stale-ai-configuration-artifacts.md) — the same decay in instruction files rather than code comments
- [Pattern Replication Risk](pattern-replication-risk.md) — agents follow what they find in the repository, including code flagged for removal
- [Distractor Interference: Why Relevance Is Not Enough](distractor-interference.md) — the broader finding that related but inapplicable context pulls the model off the task in front of it
