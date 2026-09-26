---
title: "Rerunnable Claim Graph as Shared Agent Memory"
term: "Rerunnable Claim Graph"
description: "Publish each unattended agent's result as a Git commit a peer can check out and rerun, so verification costs a checkout instead of a reconstruction. The record does not stop duplicate work on its own."
tags:
  - multi-agent
  - memory
  - tool-agnostic
  - arxiv
aliases:
  - research DAG
  - shared claim record
  - commit-addressable claims
last_reviewed: 2026-09-20
maturity: emerging
---

# Rerunnable Claim Graph as Shared Agent Memory

> A rerunnable claim graph stores each agent's result as a commit a peer can check out and rerun, so independent verification costs a checkout.

Run several unattended agents on one problem and each session starts from nothing, so more agents tend to mean more duplicated search rather than more discovery. A rerunnable claim graph makes the commit the unit of sharing: every result, insight, hypothesis, verification, and report is an immutable commit whose parent edges say what it builds on, and no filesystem, runtime, or conversation passes between workers ([Zhang et al., 2026](https://arxiv.org/abs/2609.18094v1)). Four conditions decide whether that record earns its cost.

## When this pays off

The conditions come from the first sustained run of this design, a 13-worker collective that published 1,703 contributions over 11 days and 19 hours with no assigned tasks and no central planner ([Zhang et al., 2026](https://arxiv.org/abs/2609.18094v1)).

1. A deterministic evaluator a peer can rerun. Workers scored against a fixed 200-text evaluator, and same-hardware reproductions came back bit-identical. Where the outcome is a judgement call, a verification node is an opinion with a commit hash attached.
2. A stated reproduction tolerance. Cross-hardware reruns on A100 against H100 differed by up to 1.3e-3 bits per byte, so a claimed gain below that gap files noise as progress. The brief defined what counted as a confirmed verdict.
3. Publication from a fresh checkout. The brief required every contribution to run from a clean checkout and commit everything needed to reproduce it, which turns "check out and rerun" into a real option rather than a promise in a description.
4. Credit that only another account can grant. A contribution's score sums weighted follow-on work authored by someone else, so a worker cannot manufacture standing by extending its own branch.

## How the record is built

A code-bearing contribution carries the full repository state alongside its description, tags, optional metric, and parent set. Because identity is a commit hash and parentage is Git parentage, the history is append-only and acyclic by construction ([Zhang et al., 2026](https://arxiv.org/abs/2609.18094v1)). Reserved tags give the graph enough shared meaning to query: `result`, `insight`, `hypothesis`, `report`, and `verification`, which carries the rule "Exactly one target; never one's own work" and scores +20, +10, or -20 for a confirmed, partial, or failed reproduction.

The run's 1,703 records split into 1,124 scored results, 284 insights, 203 hypotheses, 165 verifications, and one report; 53 carried an explicit negative-result tag. The verifications covered 95 distinct targets, and none reported a failure.

## Why it works

Two causes, worth keeping apart. Rerunnability is the first. Checking out a claim hands you the exact artifact that produced the number, so an independent check costs a checkout and a rerun instead of a reconstruction, which is what made 165 verifications affordable. Credit from downstream use is the second. The score counts only children authored by other accounts, and the authors are blunt that it "is not a truth signal" but encodes a narrower claim, that "work that others have reproduced or built on is more actionable than work that has only been voted for" ([Zhang et al., 2026](https://arxiv.org/abs/2609.18094v1)).

The strongest evidence is what nobody asked for. From 28 April onward, more than 400 contribution descriptions declared a prediction band before the result, and later workers closed follow-ups that earlier workers had named. The authors attribute that to the brief's reproducibility requirement and to the visibility of other accounts' posts, not to any instruction.

## When this backfires

The record stores claims. It does not allocate attention, and the same run shows what that costs.

- Duplicate work continues. Of 696 pairs of different accounts posting identical scores, 63% are within an hour of each other. The authors state it plainly: "A shared leaderboard did not stop duplicate work, and the graph is heavily exploitation-biased" ([Zhang et al., 2026](https://arxiv.org/abs/2609.18094v1)).
- Visibility concentrates the population. More than a third of all activity sat in one semantic cluster, and for five days the workers refined one recipe by about 1e-5 bits per byte per step while each read the same leaderboard. A human broke it by deploying clustering and diversity-aware ranking views mid-run, after which the first sub-1.90 result arrived the next morning ([Zhang et al., 2026](https://arxiv.org/abs/2609.18094v1)).
- Front-loaded search makes the record overhead. The first 18 scored contributions account for about 98% of the total improvement; the remaining 1,106 bought 0.03 bits per byte ([Zhang et al., 2026](https://arxiv.org/abs/2609.18094v1)).
- A central store can cost diversity outright. Decentralized per-agent memory beat "the strongest centralized memory baseline" by up to 23.8% average accuracy at up to 49% fewer tokens, on the argument that one shared repository collapses agent diversity ([Hao et al., 2026](https://arxiv.org/abs/2605.22721v1)).
- Long-lived fleets need governance. Stale propagation, contradiction persistence, and provenance collapse are three of the four failure modes named for shared fleet memory ([Margalit et al., 2026](https://arxiv.org/abs/2606.24535v1)).

One limit is the authors' own. They did not run the same models and compute without the shared graph or against a plain leaderboard, so nothing here shows the record caused the discovery rather than filing "the same parallel waste more neatly" ([Zhang et al., 2026](https://arxiv.org/abs/2609.18094v1)). Treat the design as promising and unproven.

## Example

Each session repeated the loop the two-page project brief describes, which the paper summarizes as "read analyze, pick a parent, fetch and check out that exact commit, make one change, evaluate, commit everything needed to reproduce, push with a description and metric, then post whatever else it had learned as an insight, hypothesis, or verification before analyzing again" ([Zhang et al., 2026](https://arxiv.org/abs/2609.18094v1)).

```text
agora analyze                    # frontier, thin clusters, unverified claims, open hypotheses
git fetch && git checkout <sha>  # the exact commit behind the number you build on
                                 # make one change, run the evaluator
git commit -a                    # everything needed to reproduce, metric in the description
                                 # push the contribution, then analyze again
```

The step that moved the run from 1.9304 to 1.9228 bits per byte added a second donor model. Descriptions in the run state the parent and its score, the single change, and the measured result.

## Key Takeaways

- Make the commit the unit of sharing, not the transcript. A peer can rerun a commit; nobody reruns a chat log.
- Budget for a verification tag with a cross-account rule, or the graph accumulates claims nobody checked.
- Check that your effect sizes clear your reproduction tolerance before building the record. Below that tolerance, the graph archives noise.
- Plan a second mechanism for attention. Workers reading one leaderboard spent five days refining a single recipe.
- If you adopt this, measure it: run the same models and compute against a plain leaderboard, because nobody has, and buy the record on verification cost rather than on a promised gain in discovery.

## Related

- [Decentralized Memory for Self-Evolving Multi-Agent Systems](decentralized-memory-multi-agent.md) — the counter-case, which argues a shared repository collapses agent diversity
- [Context-Graph Shared Memory for Multi-Agent Systems](context-graph-shared-memory.md) — shared state as typed triples for retrieval, with no artifact to rerun
- [File-Based Agent Coordination](file-based-agent-coordination.md) — file locks for task exclusivity, the mutual-exclusion half of the same problem
- [Persistent Shared Search Sub-Agent for Output-Token Reuse](persistent-search-subagent.md) — a different cure for redundant work, applied to repository lookups
- [Git-Bound Memory for the Agentic Development Lifecycle](../agent-design/git-bound-memory.md) — binding one team's decision history to commits for later retrieval
