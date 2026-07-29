---
title: "Skill Authoring as Software Engineering: What Transfers"
term: "Skill Authoring as Software Engineering"
description: "Treat a skill as a software artifact — single responsibility and interface separation have measured payoffs, token economy does not, and two questions decide skill versus hook."
aliases:
  - software engineering approach to skills
  - skills as software artifacts
  - skill authoring discipline
tags:
  - tool-engineering
  - instructions
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-07-29
maturity: emerging
---

# Skill Authoring as Software Engineering: What Transfers

> Software-engineering discipline improves skill authoring where selection reliability is the constraint — single responsibility and interface separation transfer, token economy does not.

Treating a skill as a software artifact means applying single responsibility, separation of interface from implementation, low coupling, and economy in a shared token budget, with behavioral evaluation standing in for deterministic tests ([Destefanis, 2026](https://arxiv.org/abs/2607.25032)). The framing is argued, not measured — the paper presents no experiments — so the useful question is which of its principles have an independent evidence channel and which do not.

## When the framing pays

The discipline is conditional. Three things decide whether it returns anything.

| Condition | Why it matters |
|---|---|
| The library is large enough for selection to fail | Agent performance degrades "by up to 21% when scaling from a small set of helpful skills to a 202-skill library" ([Song and Wei, 2026](https://arxiv.org/abs/2605.24050)). Below roughly 30 candidates, retrieval precision holds and there is nothing to recover ([Gan and Sun, 2025](https://arxiv.org/abs/2505.03275)). |
| Several people author into the same library | A shared construction standard is what keeps descriptions from colliding across authors who never read each other's files. |
| Something automated checks the result | Guidance alone does not change practice. Across 238 real-world skills, "over 99% of SKILL.md files contain at least one skill smell", and once introduced they "rarely disappear as skills evolve" ([Gao et al., 2026](https://arxiv.org/abs/2607.01456)). |

## Which principles transfer

All four principles come from the same source ([Destefanis, 2026](https://arxiv.org/abs/2607.25032)); they do not carry the same weight.

| Principle | Verdict | What backs it |
|---|---|---|
| Single responsibility | Transfers | A skill scoped to one class of task "is selected more reliably, while one that does several things has a diffuse description that matches less well". The payoff is discriminability at selection time, not modularity. |
| Interface separated from implementation | Transfers | Metadata is the interface, the body and bundled files the implementation. The split is temporal — the selector reads only metadata first — so the two are paid for at different moments. |
| Low coupling | Transfers as documentation only | Skills should not rely on another skill's internal behavior or output format, and dependencies should be stated. Nothing verifies this at load time. |
| Token economy | Demote | Contradicted by measurement (below). |

Token economy is the odd one out. Song and Wei separated library-growth damage into two channels and measured each: skill shadowing "grows with library size and significantly contributes to the performance degradation", while context overhead "remains small and indistinguishable from zero" ([Song and Wei, 2026](https://arxiv.org/abs/2605.24050)). Trimming a skill body targets the channel that measures near zero.

Testing transfers "only in a qualified form" — a language model executes the skill, so authoring is checked by behavioral evaluation against rubrics rather than deterministic unit tests ([Destefanis, 2026](https://arxiv.org/abs/2607.25032)).

## Two questions for choosing the mechanism

A skill is one of several ways to shape agent behavior, alongside memory files, slash commands, subagents, external tools, and hooks. "Two questions separate them: who decides that the mechanism runs, and what guarantee it provides" ([Destefanis, 2026](https://arxiv.org/abs/2607.25032)).

The first asks who holds the trigger — the model matching a description, the user naming it, or the runtime firing on an event. The second asks what you get when it runs: advice the model may follow, or a guarantee it cannot skip.

The resulting rule is short. "If a step depends on judgement, varies with context, or encodes domain procedure, put it in a skill. If a step must happen every time the triggering event occurs, put it in a hook" ([Destefanis, 2026](https://arxiv.org/abs/2607.25032)). Both axes generalize past that pair — a subagent buys context isolation, a slash command moves the trigger to the user — which makes the questions portable where a [tool-specific decision tree](../tools/claude/extension-points.md) is not.

## Why it works

Single responsibility works through selection interference, not code hygiene. An agent picks a skill by matching the request against every preloaded description, so scope decides how many siblings compete for that match. Shadowing is "the primary bottleneck when expanding the skill libraries" while context expansion is not ([Song and Wei, 2026](https://arxiv.org/abs/2605.24050)). Narrow scope earns its keep by making one description win cleanly — which is why the principle survives even though its software-engineering justification does not.

## When this backfires

- Guidance without a detector. Best-practice advice is already near-universally violated ([Gao et al., 2026](https://arxiv.org/abs/2607.01456)); adding another standard without an automated check changes nothing.
- Optimizing the token budget first. Shortening bodies targets a channel measured as indistinguishable from zero, leaving the dominant loss untouched ([Song and Wei, 2026](https://arxiv.org/abs/2605.24050)).
- Small libraries. Under roughly 30 candidates the degradation single responsibility protects against has not started ([Gan and Sun, 2025](https://arxiv.org/abs/2505.03275)), so the discipline costs attention and returns nothing.
- Reading a passed evaluation as a runtime guarantee. Fuzzing 402 marketplace skills found 120 (29.9%) violate their own declared specifications on benign inputs ([SEFZ, 2026](https://arxiv.org/abs/2605.13044)). A well-structured declaration is not an enforced one.
- Fast-moving domains. The authoring investment binds a snapshot of a tool or API; skills over churning surfaces go stale faster than the discipline pays back.

The strongest case against the framing is that skills are prompts, not programs: a probabilistic selector chooses them and a non-deterministic interpreter runs them, so low coupling cannot be checked and single responsibility cannot be enforced. That case holds wherever the analogy has no measurement behind it. It fails for single responsibility, where the selection channel is measured directly.

## Example

Song and Wei's worked case shows what a diffuse description costs at selection time. In their mario-coin-counting task the library contains a skill named `video-frame-extraction`, "whose description superficially matches the query better than the provided helpful skill", and the agent invokes that wrong skill in every trajectory they ran ([Song and Wei, 2026](https://arxiv.org/abs/2605.24050)).

The failure lands before either skill body is read, because the selector compares descriptions only. That is the case for treating the description as an interface: the fix is to narrow the scope and rewrite the description so it stops matching queries the skill cannot serve. No amount of editing the intended skill's body would have rescued the run.

## Key Takeaways

- The source paper is normative and reports no experiments ([Destefanis, 2026](https://arxiv.org/abs/2607.25032)), so treat its principles as hypotheses and check each against independent measurement.
- Single responsibility and interface separation transfer, on the selection-time mechanism rather than the modularity argument.
- Demote token economy — context overhead measures as indistinguishable from zero next to skill shadowing ([Song and Wei, 2026](https://arxiv.org/abs/2605.24050)).
- Two questions pick the mechanism: who decides it runs, and what guarantee it provides. Judgement-dependent steps become skills; must-happen-every-time steps become hooks ([Destefanis, 2026](https://arxiv.org/abs/2607.25032)).
- Pair any authoring standard with an automated detector, because published guidance alone leaves over 99% of real skills non-compliant ([Gao et al., 2026](https://arxiv.org/abs/2607.01456)).

## Related

- [Skill Authoring Patterns](skill-authoring-patterns.md) — the canonical practice catalog for description craft, implementation shapes, and troubleshooting; this page supplies the construction principles behind it
- [Skill Loadout Curation for Coding Agents](../context-engineering/skill-loadout-curation.md) — the session-time counterpart, and the home of the shadowing evidence used here
- [Contractual Skill Files](../instructions/contractual-skill-files.md) — a fixed governance schema for review; complementary to principles for construction
- [Classical SE Patterns as Agent Design Analogues](../patterns/agent-design/classical-se-patterns-agent-analogues.md) — the same transfer question asked of GoF and SOLID at the system level rather than the artifact level
- [Skill Evals](../verification/skill-evals.md) — the behavioral evaluation layer that stands in for deterministic tests
- [Claude Code Extension Points](../tools/claude/extension-points.md) — a tool-specific decision tree over the same mechanism choice
