---
title: "Marking Which Artifacts Are for Humans or Agents (Landmarking)"
description: "Agree a team-wide convention that marks which repository artifacts are written for people to understand and which exist only as context for agents, and back it with tooling."
term: "Landmarking"
tags:
  - human-factors
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - landmarking strategies in agent-written code
  - human-readable landmarks in code
last_reviewed: 2026-07-31
maturity: emerging
---

# Marking Which Artifacts Are for Humans or Agents (Landmarking)

> Landmarking is a team-agreed convention marking which repository artifacts are written for people to understand and which exist only as agent context.

Developers working with coding agents already invent these conventions privately. Elle O'Brien's contextual inquiry of scientific programmers found participants improvising personal schemes for marking which artifacts carry meaning for a human reader, and warns that "because each landmarking strategy is individually determined, conventions fragment across teams" ([O'Brien, 2026](https://arxiv.org/abs/2607.25975)). The technique is to make that scheme explicit and shared.

## When it pays back

Three conditions carry the overhead; outside them it is waste:

- More than one person reads the repository. The payoff is a second reader who needs to know where to spend comprehension effort. Solo exploratory work has none: O'Brien reports her own mental model breaking on exploratory analysis, ending in "committing haphazardly and without any real documentation" ([O'Brien, 2026](https://arxiv.org/abs/2607.25975)).
- The team's tooling is heterogeneous. A git-trailer convention is unusable by a colleague working through a chatbot, which is how roughly three quarters of the scientific programmers she surveyed work ([O'Brien, 2026](https://arxiv.org/abs/2607.25975)).
- The code outlives the session, so someone will return after the transcript is gone.

## The schemes people invent

O'Brien's four cases each route a reader's attention differently ([O'Brien, 2026](https://arxiv.org/abs/2607.25975)):

| Scheme | Marked human-readable | Left as agent context |
|--------|-----------------------|-----------------------|
| Commit message as journal | The message, written "like a journal entry" recording why the output was accepted | The diff itself |
| Merged diff as the unit | "Only what gets merged, the diff, is meant to be understood by a human" | Branch commits and transient specs |
| Spec-driven review | Iterated markdown specs committed with the change — "code is not reviewed, the specs are" | The implementation |
| Chat log plus growing script | Chat logs recording every choice explored | Agent comments left in code "for context for the agents in the future" |

None is wrong; the defect is that each is private, so a collaborator cannot tell which artifacts were written to be understood.

## Turning a private habit into a team artifact

Write the readership contract where agents and people both read it — the [AGENTS.md file or its per-directory variants](../instructions/agents-md-distributed-conventions.md) — stating per artifact class who must understand it and who reviews it.

Back it with something mechanical, because a social convention alone is weakly followed. Git carries one such marker: files tagged `linguist-generated` in `.gitattributes` are "suppressed in diffs" ([Linguist docs](https://github.com/github-linguist/linguist/blob/main/docs/overrides.md)), so review attention skips them without anyone opting in. Contribution policy is the other lever: among 118 AI policies across 1,000 popular GitHub repositories, 51% require disclosure and 74% a human in the loop ([Hora and Robbes, 2026](https://arxiv.org/abs/2605.16706)).

## Why it works

Review attention is scarce and routed by signals, so a shared readership marker concentrates comprehension effort on the artifacts carrying decision context. What gets lost without one is the decision shadow — "the constraints, rejected alternatives, and forward-looking context that shaped the decision", which a diff discards by construction ([Stetsenko, 2026](https://arxiv.org/abs/2603.15566)). Each of O'Brien's schemes preserves that shadow somewhere and tells its inventor where to look; sharing it extends the routing to everyone else ([O'Brien, 2026](https://arxiv.org/abs/2607.25975)). The evidence is a position argument from four cases and a survey of over 800 scientific programmers, not a controlled study.

## When this backfires

- Voluntary marking goes unfollowed. Across 14,300 commits in 7,393 repositories, 95.2% showed AI usage but only 29.5% disclosed it, ranging from 80.5% for one tool to 9.0% for another ([Kraishan, 2025](https://arxiv.org/abs/2512.00867)). A partial map reads as a complete one.
- Disclosure costs whoever complies: explicit attribution drew 23% more questions and 21% more comments, though sentiment stayed neutral ([Kraishan, 2025](https://arxiv.org/abs/2512.00867)).
- Marks drift from the code. Inconsistent annotation changes are "around 1.5 times more likely to lead to a bug-introducing commit than consistent changes" ([Radmanesh et al., 2024](https://arxiv.org/abs/2409.10781)). A stale "agent context only" marker is worse than none.
- The agent tier is still load-bearing. Labeling an artifact as agent context does not stop agents acting on it; it only lowers the human review bar on something that still runs. Where policy already requires human review of AI-assisted contributions ([Hora and Robbes, 2026](https://arxiv.org/abs/2605.16706)), a "nobody reviews this tier" rule conflicts with it.
- The convention is not portable. Strategies "are not necessarily interoperable" across collaborators, and what an agent recovers differs sharply between an unlimited and a constrained token budget ([O'Brien, 2026](https://arxiv.org/abs/2607.25975)).

## Example

Two halves of one contract. The mechanical half uses an attribute git already understands:

```text
# .gitattributes — files marked generated are suppressed in diffs
Api.js linguist-generated=true
```

The social half is the sentence the team agrees and commits, adapted from the merged-diff scheme: agents may commit freely on a branch, but only the squashed merge diff and its message are written to be understood by a person, and the branch commits are agent context ([O'Brien, 2026](https://arxiv.org/abs/2607.25975)). Written down, a new collaborator knows to read merges and skip branch history. Left implicit, they read everything or nothing.

## Key Takeaways

- Landmarking marks which repository artifacts are written for human understanding and which exist as agent context; the value is in the convention being shared, not in any one scheme.
- Four schemes observed in practice: commit message as journal, merged diff as the unit, spec-driven review, and chat log plus growing script ([O'Brien, 2026](https://arxiv.org/abs/2607.25975)).
- It pays back with multiple readers, heterogeneous tooling, and code that outlives the session; it is overhead in solo exploratory work.
- Back the convention with mechanism — `linguist-generated` suppression, review policy, CI — because voluntary disclosure ran at 29.5% against 95.2% actual AI usage ([Kraishan, 2025](https://arxiv.org/abs/2512.00867)).
- Stale marks are worse than absent ones: inconsistent annotations precede bug-introducing commits about 1.5 times more often ([Radmanesh et al., 2024](https://arxiv.org/abs/2409.10781)).

## Related

- [Human-Facing Docs in the Agent Era: Mental Models Over Reference](human-docs-mental-models-agent-era.md) — what to put in the artifacts you mark as human-readable, once the split exists.
- [Comprehension Debt: When Developers Understand Less of Their Own Codebase](../patterns/anti-patterns/comprehension-debt.md) — the individual comprehension gap this convention tries to keep from spreading across a team.
- [Visible Thinking in AI-Assisted Development](visible-thinking-ai-development.md) — commit and PR practices that make one of these schemes concrete.
- [Encode Project Conventions in Distributed AGENTS.md Files](../instructions/agents-md-distributed-conventions.md) — where a readership contract is written so agents and people both read it.
- [Agent Commit Attribution: Signed Commits and Agent Identity](../workflows/agent-commit-attribution.md) — the provenance half: marking which commits an agent authored, distinct from marking who an artifact is for.
