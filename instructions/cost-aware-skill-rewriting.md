---
title: "Cost-Aware Skill Rewriting: Preserve Operational Anchors, Not Skill Tokens"
term: "Cost-Aware Skill Rewriting"
description: "Rewriting a skill is an economic trade-off, not pure compression — stripping sparse operational anchors (a CLI flag, a validation threshold, a recovery rule) makes the agent explore and retry, raising total cost despite a shorter document."
tags:
  - instructions
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - operational anchor preservation
  - cost-aware skill compression
last_reviewed: 2026-06-13
maturity: emerging
---

# Cost-Aware Skill Rewriting: Preserve Operational Anchors, Not Skill Tokens

> Rewriting a skill is an economic trade-off — stripping sparse operational anchors makes the agent explore and retry, raising total cost despite a shorter document.

## When This Applies

Apply the anchor-preservation framing only when both conditions hold:

- The skill contains sparse operational anchors: single-line items the base model cannot reconstruct from training. An API constructor, a CLI flag, a validation threshold, a file-format convention, a formula, or a recovery rule ([Xing et al., 2026](https://arxiv.org/abs/2606.09421)).
- The agent can recover when those anchors are missing — a validator, a retry, or an exploration loop runs when the first attempt fails.

For pure-prose skills (style guides, taxonomies) or fire-and-forget workflows, generic [Prompt Compression](../context-engineering/prompt-compression.md) is the right strategy.

## The Three Anchor Classes

Different skills hold different operational anchors. The Xing et al. paper identifies three rewriting strategies, each preserving a different class, and finds **"no universally dominant template"** — the right strategy depends on the task family ([arxiv:2606.09421 §3](https://arxiv.org/html/2606.09421)):

| Anchor class | What it preserves | Wins on |
|---|---|---|
| **API/code anchoring** | Imports, API calls, object construction, commands, code snippets | Implementation-heavy tasks where one wrong constructor triggers a debugging cycle |
| **Workflow guarding** | Ordered steps, validation checks, constraints, named pitfalls | Procedurally-drifting tasks where step reordering produces silent failures |
| **Rule/formula anchoring** | Definitions, formulas, thresholds, schemas, conventions | Scientific and rule-governed tasks where one mis-stated threshold invalidates the output |

A skill profile — token count, code ratio, validator markers, API call frequency — determines which strategy fits. A learned task-conditioned policy that picks the strategy from these structural features reduces total agent cost by **7.0%** and downstream agent-token cost by **6.0%** on a 20-task held-out evaluation; in cross-model transfer across 86 tasks, reductions average **14.7%** and **13.7%** ([arxiv:2606.09421 §4](https://arxiv.org/html/2606.09421)).

## Why It Works

With the anchor present, the agent commits the correct decision in one inference step; absent it, it enumerates candidates, runs them, observes failure, and retries. Each exploration step is a full inference whose generated tokens are priced above the prompt tokens it replaced. Input-token reduction overstates the saving because total cost tracks output length, which compression can inflate — one benchmark showed up to 56× output expansion under aggressive compression ([Compression Method Matters, arxiv:2603.23527](https://arxiv.org/abs/2603.23527)). The deleted skill text is a few hundred input tokens, often KV-cache hits; the exploration overhead is thousands of uncached output tokens. A [randomized production trial of generic prompt compression](https://arxiv.org/pdf/2603.23525) documented exactly this asymmetry: aggressive compression (r≈0.2) *increased* total cost by 1.8% via output-token explosion despite cutting input by ~80%.

## The Diagnostic

Before rewriting a skill, walk the body line-by-line and answer for each candidate cut:

1. **Is this an operational anchor?** A single-line piece of operational knowledge the base model cannot guess — a specific flag like `--canary 10`, a threshold, a constructor argument, a file path, or a recovery rule.
2. **Would the agent fail or retry without it?** If yes, the anchor pays for itself in saved exploration cost. Keep.
3. **Is this surrounding explanation that contextualises the anchor?** Cut. Keep the anchor; drop the framing.
4. **Is this an example that *implicitly* defines the anchor?** Cut only if the anchor is named explicitly elsewhere — non-actionable body content is the safe cut, but an example carrying an otherwise-unstated convention is an anchor in disguise ([SkillReducer, arxiv:2603.29919](https://arxiv.org/abs/2603.29919)).

This is the inverse of generic prompt compression's compression test ("can I remove a word without losing meaning?"). The cost-aware test is: **can I remove this without forcing the agent to discover it by trial?**

## Example

A verbose, implementation-heavy section with three anchors buried in prose:

```markdown
## Deploying to staging

When you want to deploy to the staging environment, you should use the
`stage-deploy` CLI. It is important that you pass the `--canary 10` flag,
which limits the initial rollout to 10% of staging traffic and prevents
a full-fleet bad-deploy. The deploy script will print a deploy ID once
the canary is healthy; you must capture this ID because the rollback
command requires it. If the canary fails health checks within five
minutes, you should not retry — the failure is logged in
/var/log/stage-deploy.log and the correct response is to investigate
the log entry, not re-run the deploy.
```

**API/code anchoring** rewrite — drops the explanation, keeps the three anchors (the flag, the deploy-ID capture rule, the no-retry recovery rule):

```markdown
## Deploying to staging

- Deploy: `stage-deploy --canary 10`
- Capture the printed deploy ID — required for rollback
- On canary failure within 5 minutes: read `/var/log/stage-deploy.log`. Do not retry.
```

Same operational content, ~70% fewer tokens, anchors intact. Dropping "do not retry" too would save a few more input tokens but risk a multi-thousand-token retry loop — net cost up.

## When This Backfires

The anchor-preservation framing has real costs that the 7.0% headline win must justify:

- **Pure-prose skills with no sparse anchors** — style guides, taxonomies, convention lists. Nothing operational to preserve; the profiler-rewriter-evaluator overhead pays for nothing. Use [Prompt Compression](../context-engineering/prompt-compression.md) directly.
- **Selection-bottlenecked libraries** — when descriptions get truncated to fit a character budget and the agent picks the wrong skill, in-skill anchors are unreachable. Fix [description craft](../tool-engineering/skill-authoring-patterns.md) first ([Anthropic best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
- **Rapidly-changing APIs** — preserved anchors that go stale within weeks actively misdirect the agent. A stale anchor is worse than an absent one; pair preservation with an explicit update cadence, or accept exploration cost. See [Skill Library Technical Debt](../tool-engineering/skill-library-technical-debt.md).
- **Fire-and-forget workflows** — without a validator, retry, or exploration loop, anchors aimed at preventing debugging cycles cost tokens for no payoff.
- **The "less-is-more" baseline** — [SkillReducer](https://arxiv.org/abs/2603.29919) achieves 48% description and 39% body compression while *improving* functional quality by 2.8% (mean cross-model retention 0.965), attributing the gain to reduced context-window distraction. For libraries of bloated human-written skills, the simpler "compress hard, keep code-fenced blocks intact" heuristic captures most of the value. Anchor-preservation wins only where exploration overhead exceeds compression-distraction overhead.

## Key Takeaways

- A rewritten skill is cheaper only when it preserves the **sparse operational anchors** that prevent exploration, debugging, and retry — not because it has fewer tokens.
- Three anchor classes cover most skills: **API/code anchoring** (constructors, flags), **workflow guarding** (ordered steps, validators), **rule/formula anchoring** (thresholds, schemas). No template wins universally — a learned policy that matches the strategy to the skill's structural profile cut total agent cost by 7.0% on a held-out evaluation.
- The mechanism is the asymmetry between cached input savings and uncached output overhead — the saved skill tokens are cheap, cacheable input, while each forced exploration step spends uncached output tokens.
- The diagnostic test is "can I remove this without forcing the agent to discover it by trial?" — the inverse of generic compression's "without losing meaning?" test.
- For pure-prose skills, fire-and-forget workflows, or libraries bottlenecked at selection rather than execution, fall back to [Prompt Compression](../context-engineering/prompt-compression.md).

## Related

- [Prompt Compression: Maximizing Signal Per Token](../context-engineering/prompt-compression.md) — the lexical-density technique the cost-aware approach explicitly contrasts with
- [Skill Authoring Patterns: Description to Deployment](../tool-engineering/skill-authoring-patterns.md) — sibling guidance on description craft, Gotchas, and skill composition
- [Skill as Knowledge Pattern](../tool-engineering/skill-as-knowledge.md) — what a skill should *contain*; this page covers what to *remove*
- [Cost-Aware Tracing for Skill Distillation](../observability/cost-aware-tracing-skill-distillation.md) — the trace-side instrumentation that makes anchor-preservation decisions measurable
- [Skill Library Technical Debt](../tool-engineering/skill-library-technical-debt.md) — library-level debt patterns including stale anchors and missing validators
