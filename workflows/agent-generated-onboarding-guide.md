---
title: "Agent-Generated Onboarding Guide as a Durable Artefact"
description: "Use an agent to synthesise a teammate ramp-up guide from the repository, then version-control the artefact and regenerate on architectural change rather than writing onboarding docs by hand."
term: "Agent-Generated Onboarding Guide"
tags:
  - workflows
  - agent-design
  - human-factors
  - claude
aliases:
  - agent-generated ramp-up guide
  - agent synthesised onboarding artefact
last_reviewed: 2026-06-12
maturity: adopted
---

# Agent-Generated Onboarding Guide as a Durable Artefact

> An agent synthesises a teammate onboarding guide from the repository; you version-control that artefact and regenerate it on architectural change rather than on a calendar.

## Artefact, not conversation

An agent that reads a codebase can answer onboarding questions live — see [Agent-Powered Codebase Q&A and Onboarding](codebase-qa-onboarding.md). The artefact variant is the complement. A live Q&A session disappears when the newcomer closes the terminal. The artefact is instead a single structured document that you review, commit, and reuse.

Claude Code shipped `/team-onboarding` in the week of 2026-04-06 to 2026-04-10 "for packaging your setup" ([Claude Code documentation index](https://code.claude.com/docs/llms.txt)). The command is one implementation of the artefact pattern. The durable shape is tool-agnostic: any agent that can read the repository and a curated set of usage traces can produce the same output.

| Dimension | Interactive Q&A | Generated artefact |
|---|---|---|
| Lifespan | Single session | Version-controlled, persists |
| Audience | One newcomer | Every future teammate |
| Drift source | None (regenerated each query) | Bounded by regeneration cadence |
| Review surface | Nothing to review | PR-sized document |
| Failure mode | Newcomer asks wrong question | Unreviewed hallucinations enter history |

## Artefact shape

A ramp-up guide an agent produces typically covers five sections:

- Entry points — top-level scripts, service binaries, `main` functions, CI entrypoints
- Hot files — modules changed most often in the last N months, and the directories where most pull-request review time builds up
- Conventions — naming patterns, directory layout, test structure, commit style
- Must-read history — commits that introduced current architectural invariants, post-mortems, ADRs
- Glossary — project-specific vocabulary mapped to the modules and types that implement it

The Claude Code best-practices guide frames this kind of durable artefact — `/init` "analyzes your codebase to detect build systems, test frameworks, and code patterns, giving you a solid foundation to refine" and the resulting CLAUDE.md "compounds in value over time" when checked into git ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)). The onboarding guide is the reader-facing sibling to CLAUDE.md: CLAUDE.md tells future agents how to behave; the ramp-up guide tells future humans how to read the code.

## Why synthesise instead of Q&A

An agent with codebase search and file-reading tools can assemble a repository-wide view in one synthesis pass, then compress it into a map people can read. [RepoAgent (arXiv 2402.16667)](https://arxiv.org/abs/2402.16667) formalises this as a framework for LLM-generated repository-level documentation, motivated by the observation that hand-written docs drift from implementation within weeks. The artefact amortises the comprehension cost: you review once, and it serves every later reader.

The durable form also enables patterns the [conversational form](codebase-qa-onboarding.md) cannot:

- A newcomer can read it before their first terminal session, so they arrive with a mental model rather than constructing one from cold.
- Reviewers can audit the claims the artefact makes, catching errors early rather than letting them spread through individual onboarding sessions.
- Git history of the artefact itself becomes a signal — when the file changes significantly between regenerations, that is a prompt to tell the team about the architectural shift.

## Regeneration cadence

Calendar-based regeneration (monthly, quarterly) creates churn without reliably matching code change. Tie regeneration to architectural events instead:

- Merge of a change that introduces or removes a service boundary
- Migration that reshapes the data model or top-level directory layout
- Breaking dependency upgrade that changes conventions
- Onboarding of a new team member — the existing guide is re-run, diffs are reviewed, staleness is caught against fresh eyes

```mermaid
graph TD
    A[Architectural change merges] --> B[Trigger regeneration]
    C[New teammate starts] --> B
    B --> D[Agent synthesises guide]
    D --> E[Maintainer reviews diff against previous version]
    E --> F[Commit to repo]
    F --> G[Teammate reads durable artefact]
    G --> H[Flags stale sections as new questions surface]
    H --> B
```

Regeneration-on-trigger bounds drift by the frequency of significant change rather than by an arbitrary calendar. Between triggers, the artefact is stable enough to cite.

## When this backfires

The artefact pattern has specific failure conditions. Prefer the interactive Q&A form, or skip onboarding tooling entirely, when any of these apply:

- Solo or two-person teams — there is no audience downstream of the author. Regeneration and review cost more than the onboarding time they save.
- Rapidly-changing [greenfield codebases](agent-driven-greenfield.md) — the artefact is stale before the next teammate arrives. Live Q&A works better because it reflects current code.
- Teams without review discipline — unreviewed generated guides become a hallucination vector. Agents fabricate file paths and invent architectural rationale. The Claude Code best-practices guide warns that over-specified auto-generated docs make agents "ignore half of it because important rules get lost in the noise," and the same noise confuses humans ([Claude Code best practices](https://code.claude.com/docs/en/best-practices)).
- Codebases dominated by tacit knowledge — the agent reads only what is in the repo. It cannot extract judgments that live in senior engineers' heads. The artefact will look complete while missing the conventions that actually matter. Pair with [encoding tacit knowledge](encoding-tacit-knowledge.md) rather than relying on synthesis alone.
- Over-reliance that deepens comprehension debt — if newcomers read only the artefact and never look at the source, [comprehension debt](../anti-patterns/comprehension-debt.md) builds up. Treat the guide as a map, not a substitute for the terrain.

## Review discipline

Treat the generated guide like any agent output: the artefact must pass review before it enters the repo. Specific checks:

- Verify that every file path and symbol name the guide references exists in the current tree.
- Cross-check architectural claims (service boundaries, dependency directions) against the import graph or configuration.
- Check historical claims (who introduced a pattern, why a convention exists) against `git log` rather than the agent's summary, because agents confabulate history readily.
- Confirm the conventions the guide lists match what the team does today, not what it did when the pattern first appeared.

The review is lighter than writing the guide from scratch, heavier than rubber-stamping. That is the trade the artefact pattern buys.

## Example

A platform team maintaining a payments service regenerates their ramp-up guide whenever the service topology changes.

The trigger is a PR that splits the capture module into two services. The merge hook invokes the agent:

```bash
claude /team-onboarding --out docs/onboarding/ramp-up.md
```

The agent produces a structured ramp-up: a Markdown file with the five sections above. Entry points list the new binary for the split-out service. Hot files come from the last 90 days of commits, excluding generated code. Conventions list the processor-adapter naming pattern and the event-sourcing layout.

In review, the module owner compares the diff against the previous version. Two sections changed materially: the entry-points section now lists two services instead of one, and the glossary adds "capture sidecar" with a link to the new module. The reviewer spot-checks three claims against the code. The first entry point exists at the claimed path, and the second is correct. A claimed "retry policy convention" is accurate in two adapters but overgeneralised as universal, so the reviewer corrects the phrasing to "retry policy convention in processor adapters, see `adapters/stripe.ts` for the canonical example."

The corrected artefact then lands as `docs/onboarding/ramp-up.md`. The next teammate who joins reads it before opening their first file.

When that teammate starts, the agent regenerates the guide once more and the team reviews the diff. Stale sections surface against a fresh reader's questions, which become the next round of corrections.

## Key Takeaways

- The artefact pattern shifts onboarding from repeated individual Q&A to one-shot synthesis plus amortised review, producing a version-controlled map that survives across teammates.
- The durable artefact typically covers entry points, hot files, conventions, must-read history, and glossary — the reader-facing content an agent with repository access produces from the same scan that generates CLAUDE.md.
- Tie regeneration to architectural events, not the calendar — this bounds drift by significant change rather than by a fixed cadence.
- The pattern fails on solo teams, rapidly-changing greenfield code, review-less cultures, and tacit-knowledge-heavy codebases; prefer interactive Q&A or skip the tooling in those conditions.
- Review the generated guide the way you review agent code output: verify claims against the tree, check history against `git log`, and flag overgeneralisations rather than merging the first pass.

## Related

- [Agent-Powered Codebase Q&A and Onboarding](codebase-qa-onboarding.md) — the interactive complement to the artefact pattern
- [Team Onboarding for Agent Workflows](team-onboarding.md) — team-coordination onboarding, distinct from the artefact
- [Encoding Tacit Knowledge into Agent Improvement Loops](encoding-tacit-knowledge.md) — captures judgments the generated guide will miss
- [Continuous Documentation](continuous-documentation.md) — the broader drift-detection pipeline the ramp-up guide can plug into
- [Getting Started with Instruction Files](../instructions/getting-started-instruction-files.md) — CLAUDE.md and AGENTS.md are sibling artefacts to the ramp-up guide
- [Pre-Execution Codebase Exploration](pre-execution-codebase-exploration.md) — the reader-side skill the guide accelerates
- [Comprehension Debt](../anti-patterns/comprehension-debt.md) — the primary failure mode when newcomers substitute the guide for code reading
- [Three Knowledge Tiers](../instructions/three-knowledge-tiers.md) — how the ramp-up guide fits alongside hot, warm, and cold knowledge
