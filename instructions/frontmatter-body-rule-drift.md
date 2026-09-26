---
title: "Frontmatter and Body Rule Drift in Agentic Workflows"
term: "Frontmatter-Body Rule Drift"
description: "A limit written in both a workflow file's frontmatter and its prose body is two rules. Most maintenance edits touch one region, so the copies diverge."
tags:
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - two-region rule duplication
  - workflow spec region drift
last_reviewed: 2026-09-24
maturity: emerging
---

# Frontmatter and Body Rule Drift in Agentic Workflows

> A rule stated in both a workflow file's configuration and its prose is two rules, and most edits touch only one of them.

An agentic workflow file holds two regions that look like one document and behave like two artifacts. The YAML frontmatter sets triggers, permissions, tools, and output caps, and the runtime enforces it. The Markdown body instructs the agent, and only the agent's compliance enforces it. Put a firm limit in the frontmatter, use the body to say when the limit applies, and if you also state the number there, change both regions in one commit.

## When to duplicate and when not to

State the limit once, in configuration, when the agent does not need the number to decide what work to do. A cap on comments, labels, or pull requests sits here, where the configuration provides "controlled limits per operation" ([GitHub](https://github.github.com/gh-aw/reference/safe-outputs/)).

Restate it in the body when the limit shapes the agent's plan. If a workflow may open three issues and the agent does not know, it investigates twelve candidates and pays for nine it cannot publish. Here the duplicate earns its cost, and the fix is a paired edit, not a deletion.

None of this helps if your automation has no configuration the runtime enforces. A cron job that pipes a prompt into an agent CLI has one region, so the first job is building an enforcement point.

## Why it works

The two regions are enforced by different parties. GitHub's Safe Outputs reference states that "Safe outputs enforce security through separation: agents run read-only and request actions via structured output, while separate permission-controlled jobs execute those requests". That happens "all without giving the agentic portion of the workflow any write permissions" ([GitHub](https://github.github.com/gh-aw/reference/safe-outputs/)). A frontmatter cap holds whatever the agent decides. A sentence in the body holds only if the agent obeys it.

Maintenance is what makes duplication expensive. Khelifi et al. tracked 8,575 changes across 348 gh-aw Markdown files from 43 repositories, selecting files with at least 120 days of observed activity. Over the first four months they report that "44.8% affect only frontmatter, 37.8% only the body, and 17.3% both" ([Khelifi et al., 2026](https://arxiv.org/abs/2609.27263v1)). A rule written twice survives only if every later edit touches both regions, and roughly four edits in five touch one. Size does not reveal the divergence either: in those repositories, one-third of content-changing file events left the line count unchanged.

The same split explains why reading the prose tells you little about what a workflow enforces. The study built its taxonomy from each sampled file's latest snapshot, "coding only its Markdown body without expanding imports or inferring instructions from YAML frontmatter". Its 25.0% safety figure, measured over 288 labeled files, therefore counts safety prose and not safety enforcement. The authors say as much: the gap identifies "areas for closer review without establishing that corresponding runtime protections are absent".

## When this backfires

- The rule has no configuration key. A Go API reviewer told to "do not flag it solely because the shape is idiomatic to Go" has nowhere to move that rule ([Khelifi et al., 2026](https://arxiv.org/abs/2609.27263v1)). Stripping unenforced prose on principle deletes the judgment the workflow exists to apply.
- Removing the prose copy costs more than it saves. Lulla et al. ran agents on 124 pull requests across 10 repositories with and without an `AGENTS.md`, and report that "the presence of AGENTS.md is associated with a lower median runtime (Δ28.64%) and reduced output token consumption (Δ16.58%), while maintaining a comparable task completion behavior" ([Lulla et al., 2026](https://arxiv.org/abs/2601.20404v2)). Operational facts stated in prose can pay for themselves.
- The efficiency evidence points the other way on a different metric. Gloaguen et al. evaluated SWE-bench tasks carrying LLM-generated context files alongside issues from repositories with developer-committed ones, and report that "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average" ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v2)). Runtime and output tokens are not inference cost, so neither result settles the other. Measure your own workflow.
- Upstream files are not yours to arrange. In their wider sample of 365 projects with generated workflows, Khelifi et al. found 108 (29.6%) referencing Markdown from another repository for at least one workflow ([Khelifi et al., 2026](https://arxiv.org/abs/2609.27263v1)). Your convention about which region holds what does not survive a recompile against a file another team maintains.
- Quiet workflows do not drift. Two regions edited once in six months carry no divergence risk, and the pairing rule costs attention for nothing.

## Example

The triage comment reviewer in `dotnet/aspnetcore` states the same cap twice ([Khelifi et al., 2026](https://arxiv.org/abs/2609.27263v1)). The body tells the agent to "post at most one comment". The frontmatter sets it:

```yaml
safe-outputs:
  add-comment:
    max: 1
```

Khelifi et al. recommend keeping the pair aligned: "Developers should use supported configuration controls for firm limits, while using body instructions to explain task-specific conditions and expectations. When a rule appears in both regions, they should keep the two consistent as the workflow evolves" ([Khelifi et al., 2026](https://arxiv.org/abs/2609.27263v1)). Raise the cap to three and edit only the YAML, and the body now understates what the workflow will do.

## Key Takeaways

- Treat a workflow file's frontmatter and body as two artifacts sharing one filename.
- Firm limits belong in configuration, because a separate permission-controlled job applies them, not the agent.
- A duplicated limit is justified when the agent must plan against it, and then both copies change in one commit.
- Auditing the prose alone measures what a workflow asks for, never what it enforces.

## Related

- [Hooks for Enforcement vs Prompts for Guidance](hooks-vs-prompts.md) — which rules belong in an enforcement layer at all
- [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md) — the rule types agents comply with, and the ones they do not
- [Multi-Layer Specification Redundancy as a Robustness Budget](multi-layer-specification-redundancy.md) — when repeating a requirement across layers helps
- [GitHub Agentic Workflows](../tools/copilot/github-agentic-workflows.md) — the two-file architecture and its safe-output controls
