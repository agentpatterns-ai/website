---
title: "Destructive-Failure Mechanism Attribution by Mitigation Owner (ClayBuddy Three)"
term: "Destructive-Failure Mechanism Attribution"
description: "A three-mechanism cut of destructive coding-agent failures — underspecification, capability errors, harness errors — chosen so each bucket routes to a different mitigation owner (spec author, model trainer, harness builder)."
tags:
  - anti-pattern
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - destructive failure attribution
  - claybuddy three mechanisms
  - mechanism-by-owner failure cut
last_reviewed: 2026-06-23
maturity: emerging
---

# Destructive-Failure Mechanism Attribution by Mitigation Owner (ClayBuddy Three)

> Route each destructive coding-agent failure to its mitigation owner — spec author, model trainer, or harness builder — before defaulting to one guardrail.

A *destructive* coding-agent failure is one that leaves the repository, environment, or production system worse than it started — a wrong `rm -rf`, a force-push over uncommitted work, a credential leaked into a commit. The ClayBuddy paper proposes a three-mechanism cut over these incidents, chosen so each bucket routes to a different mitigation owner: **underspecification** (safe default behavior was never specified), **capability errors** (the safe action is available but the model does not adhere to it due to bias or capability limitations), and **agent harness errors** (the harness prevents the safe action from executing) ([Ge & Assis, arxiv 2606.19380](https://arxiv.org/abs/2606.19380)).

## When This Cut Earns Its Keep

The ownership axis is load-bearing only when the *next action differs by bucket*. Three conditions stack:

- **Multi-owner teams.** Distinct people write specs, pick the model, and build the harness. The cut routes work to the responsible function rather than dumping every fix on the harness builder.
- **Autonomous or scheduled runs.** ClayBuddy targets *"rare but highly destructive failure modes"* surfacing at scale ([Ge & Assis](https://arxiv.org/abs/2606.19380)); the cut pays its keep when no human review gate blunts the incident first.
- **Fix-routing across functional boundaries.** A destructive incident becomes a spec-template PR, a model-bias regression filing, or a deterministic guardrail commit — three different artifacts in three different repos with three different reviewers.

A solo developer who writes the prompt, runs the model, and edits the harness pays the categorisation cost without the coordination return. Skip the cut and reach for the [five-failure-layers diagnostic](../agent-design/five-failure-layers-diagnostic.md) (harness-layer axis) instead.

## The Three Mechanisms

| Bucket | Definition ([Ge & Assis](https://arxiv.org/abs/2606.19380)) | Owner | Mitigation form |
|---|---|---|---|
| **Underspecification** | Default model behavior is unsafe because the safe action was never specified | Spec author / prompt template owner | Explicit prompt rule, `AGENTS.md` clause, dangerous-command policy |
| **Capability error** | Safe action is available but the model does not adhere to it due to bias or capability limitations | Model trainer / evaluation owner | Model-bias regression filing; escalate to a different model for high-risk operations |
| **Harness error** | Model fails to execute the safe action through the harness | Harness builder | Deterministic guardrail, allowlist, confirmation step, sandbox boundary |

ClayBuddy itself is a *"harness that molds to user preferences and can be modified by the model in-session"* with four design features — agent context-editing tools, an extended system prompt, a customisable command classifier, and deterministic guardrails — evaluated across 8 evaluations totalling 20 coding environments and 59 synthetic transcript templates ([Ge & Assis](https://arxiv.org/abs/2606.19380)). The harness implements the ownership cut end-to-end, but the cut itself is portable to any harness.

## Why It Works

The cut works *when the artifact produced by the fix differs by bucket*. A spec-author response is a prompt-template diff or an `AGENTS.md` rule; a model-trainer response is a regression-suite entry and a routing rule; a harness-builder response is code in the agent runtime. Three different artifacts mean three different review paths and three different deploy cadences. The ownership cut routes the incident to the path that ships fastest for *that* mechanism — rather than the default of "wait for the harness team to add another guardrail," which scales linearly with every new failure mode ([Ge & Assis](https://arxiv.org/abs/2606.19380)). The complementary axes are the harness-layer cut from the [five-failure-layers diagnostic](../agent-design/five-failure-layers-diagnostic.md) and the signal-axis cut from the [silent-failure mechanism taxonomy](silent-failure-mechanism-taxonomy.md); the three do not duplicate one another.

## When This Backfires

- **Diffuse multi-mechanism incidents.** A wrong `rm -rf` may plausibly fit all three buckets — a vague prompt, a model that didn't ask, and a harness without a confirmation step. Attribution becomes a coin flip and the cut adds vocabulary without routing the fix. Pick the bucket whose owner can ship the fix soonest, and document the others as residual.
- **Single-owner teams.** When the same person writes the spec, picks the model, and edits the harness, the routing benefit collapses. The cut adds bookkeeping cost without buying coordination.
- **Capability bucket as residual.** "Capability error" is the squishiest bucket — practitioners cannot retrain the model, so the immediate response is *still* a harness guardrail. The cut may not productively differ from a two-bucket spec-vs-harness split for teams that don't own a model. The paper notes the harness layer was where ClayBuddy itself landed the mitigations ([Ge & Assis](https://arxiv.org/abs/2606.19380)).
- **Taxonomy proliferation.** The site already carries layer-axis (five-failure-layers), signal-axis (silent-failure), and symptom-axis ([Sourcegraph five](large-codebase-agent-failure-patterns.md)) cuts. Adding ownership-axis is justified only when fix-routing across owners is the bottleneck — otherwise the [silent-failure page's warning](silent-failure-mechanism-taxonomy.md) applies: stacking taxonomies multiplies vocabularies without adding defensive power.
- **Fully attended sessions.** A team reviewing every agent action through a human gate already has the dominant guardrail; mechanism-by-owner routing is overhead.

## Example

A scheduled coding agent force-pushes to `main`, overwriting two days of commits. The anti-pattern is the response, not the incident itself.

**Before — every destructive incident routes to the harness team.** The post-incident review files one ticket on the harness backlog: "add a protected-branch check on `git push --force`." The harness builder ships a deterministic guardrail. The spec was vague *and* the model's instruction-following on buried rules was weak, but those owners never receive a signal. The next destructive incident — a `rm -rf` outside the worktree — files another harness ticket. The harness backlog grows linearly with every new failure mode while the upstream owners stay unaware.

**After — the incident routes by mechanism owner.** The post-incident review attributes the force-push to all three buckets and opens three artifacts:

- *Underspecification → spec author.* The prompt did not name `main` as protected and no `AGENTS.md` clause forbade force-push. Open a PR adding a "never force-push to `main`" rule to the prompt template and `AGENTS.md`.
- *Capability error → evaluation owner.* The model's instruction-following degraded because the protection rule was buried mid-prompt. File a model-eval regression checking rule-honoring across N positions in the system prompt; route force-push operations to a model class with higher instruction-following.
- *Harness error → harness builder.* The harness exposed `git push --force` with no allowlist. Replace the unguarded tool with one that rejects `--force` on a protected-branch list.

Three different artifacts, three different reviewers, three different deploy cadences. The harness team no longer absorbs every destructive failure mode.

## Key Takeaways

- The ClayBuddy paper's three-mechanism cut — underspecification, capability errors, harness errors — is chosen so each bucket routes to a different mitigation owner ([Ge & Assis, arxiv 2606.19380](https://arxiv.org/abs/2606.19380)).
- The cut earns its keep only under three stacked conditions: multi-owner teams, autonomous or scheduled runs, and fix-routing across functional boundaries. Solo-developer or fully-attended setups should default to the [five-failure-layers diagnostic](../agent-design/five-failure-layers-diagnostic.md) instead.
- A single destructive incident may plausibly fit all three buckets. Pick the owner who can ship the fix fastest and log the others as residual — do not treat the cut as a partition.
- The capability bucket is the squishiest: teams that cannot retrain the model will still ship a harness guardrail. The cut may collapse to a two-bucket spec-vs-harness split in practice.
- The provenance is single-paper — treat as `emerging`. The [silent-failure page's warning on stacking taxonomies](silent-failure-mechanism-taxonomy.md) is the constraint on when to reach for any mechanism cut.

## Related

- [Five-Failure-Layers Diagnostic](../agent-design/five-failure-layers-diagnostic.md) — the harness-layer-axis sibling cut (task spec / context / execution env / verification / state). Use this when the team is single-owner or when the next action sits at one layer regardless of mitigation owner.
- [Silent-Failure Mechanism Taxonomy](silent-failure-mechanism-taxonomy.md) — the signal-axis sibling (how the error hides). Pairs with this page; the silent-failure page's "stacking taxonomies" warning is the explicit constraint on when to reach for either.
- [Large-Codebase Coding-Agent Failure Patterns (Sourcegraph Five)](large-codebase-agent-failure-patterns.md) — symptom-axis cut (transcript signatures). Symptom recognition feeds mechanism attribution; the two axes are complementary.
- [Interactive Clarification for Underspecified Tasks](../agent-design/interactive-clarification-underspecified-tasks.md) — the canonical mitigation for the underspecification bucket on the operator side: the agent surfaces the missing safety rule before acting.
- [Issue Requirements Preprocessing](../agent-design/issue-requirements-preprocessing.md) — automated underspecification remediation upstream of execution, a concrete instance of the spec-author mitigation path.
