---
title: "RAMP: Committed AI Configuration and the Quality Cost"
term: "RAMP"
description: "RAMP grades repositories by the AI configuration they commit. Agent-first repos with none show twice the cognitive-complexity rise after adopting agents."
aliases:
  - Repository AI Maturity Profile
  - RAMP maturity model
  - committed AI configuration maturity
tags:
  - instructions
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-27
maturity: emerging
---

# RAMP: Committed AI Configuration and the Quality Cost

> Agent-first repositories with no committed AI configuration take about twice the cognitive-complexity hit after adopting coding agents.

RAMP (Repository AI Maturity Profile) is a four-level scale that grades a repository by the AI configuration files its team has committed. Denisov-Blanch et al. built it from "441 private GitHub repositories from 27 commercial organizations", then re-estimated an existing coding-agent adoption panel within each level. Among agent-first repositories, Level 1 saw cognitive complexity rise 52.70% after adoption against 26.68% at Level 2 or above, and warnings rise 24.08% against 14.04% ([arXiv:2608.25241v1](https://arxiv.org/abs/2608.25241v1)).

## The four levels

| Level | Name | Committed artifacts |
|---|---|---|
| 1 | Unconfigured | No AI-related files |
| 2 | Grounded prompting | Behavioral rules, tool settings, architecture docs, coding standards |
| 3 | Agent-augmented | Named agents with tool restrictions, reusable commands, domain guides |
| 4 | Orchestration | Multi-agent workflows, phased pipelines, execution logs |

Almost all of the measured difference sits at the first step. 83.1% of repositories introduce artifacts at exactly one level, Level 4 never appears in the development sample, and the median wait to a first validated artifact is 633 days among the 87% of repositories with measurable pre-adoption history. 73.8% of artifacts are committed once and never modified ([arXiv:2608.25241v1](https://arxiv.org/abs/2608.25241v1)).

## Conditions the number depends on

The 2x ratio is not a general fact about configuration files. These scoping conditions travel with it.

- The contrast is identified only among agent-first repositories, meaning teams that adopted autonomous agents with no prior IDE-based AI tool experience. If your team already ran Copilot or Cursor, the paper offers no effect size for you.
- The outcomes are "SonarQube proxies rather than direct measures of defects or maintainability", and the event study extends six months after adoption, a horizon the authors say "cannot rule out later self-correction" ([arXiv:2608.25241v1](https://arxiv.org/abs/2608.25241v1)).
- Maturity is not randomly assigned. The authors list correlated engineering discipline, model capability, and reverse causality as live alternatives, and report that commit velocity still correlates with maturity at rho=0.269 ([arXiv:2608.25241v1](https://arxiv.org/abs/2608.25241v1)).
- The primary contrast dichotomizes at Level 1 versus Level 2+, and the authors flag under conclusion validity that "a boundary chosen after inspecting outcomes could overstate the gradient" ([arXiv:2608.25241v1](https://arxiv.org/abs/2608.25241v1)). They report four-level, combined, and binary groupings as robustness checks.
- Velocity does not separate the strata cleanly. Commit frequency rose 37.6% at Level 1 and 27.5% at Level 2 or above ([arXiv:2608.25241v1](https://arxiv.org/abs/2608.25241v1)), so configuration is not free speed alongside better quality.

## Why it works

The paper names three candidate channels and says its design "cannot distinguish among them": artifacts as direct guardrails on agent output, artifacts as markers of broader engineering discipline, and artifacts as a shared reference that speeds team learning ([arXiv:2608.25241v1](https://arxiv.org/abs/2608.25241v1)). Only the guardrail channel has independent support, and only for part of the file. Gloaguen et al. split context files by content type and found that "instructions in the context files are well followed by coding agents, [while] repository overviews, although popular and recommended by model providers, are not helpful" ([arXiv:2602.11988v2](https://arxiv.org/abs/2602.11988v2)). A stated constraint the agent reads and obeys bounds the shape of what it emits, which shows up in complexity and warning counts without showing up in whether the task got solved.

Xu et al. corroborate the direction weakly. They identify agent adoption by a repository's first config-file commit, making their whole adopter population Level 2 or above by construction, and their difference-in-differences estimate puts the complexity rise at "about +11% on a cognitive metric for Python, a quarter of the prior estimate" ([arXiv:2607.01810v1](https://arxiv.org/abs/2607.01810v1)). That sits nearer RAMP's Level 2+ figure than its Level 1 one.

## When this backfires

- Your governance lives outside version control. The authors note that practice also lives in "wikis, onboarding material, review checklists, and pull-request gates, none of which our pipeline can see", so "some repositories we label Level 1 are well governed by means we cannot observe" ([arXiv:2608.25241v1](https://arxiv.org/abs/2608.25241v1)). Committing files to move a level buys nothing there.
- You fill the file with architecture tours. Level 2 admits "architecture or design docs", which is the content Gloaguen et al. found unhelpful while raising inference cost by over 20% on average ([arXiv:2602.11988v2](https://arxiv.org/abs/2602.11988v2)).
- You are already past the [compliance ceiling](instruction-compliance-ceiling.md). Climbing a level means adding artifacts, and a factorial study over 1,650 Claude Code sessions found that "none of the four structural variables" it tested "produces a detectable contrast after multiple-testing correction" ([arXiv:2605.10039v1](https://arxiv.org/abs/2605.10039v1), covered in [Configuration File Structure Compliance Gap](configuration-file-structure-compliance-gap.md)). Rewriting the file does not recover adherence that rule volume already spent.
- You treat the file as done. The set-and-forget rate above describes what teams do, not what works, and a study of 2,303 context files found them "not static documentation but complex, difficult-to-read artifacts that evolve like configuration code" ([arXiv:2511.12884v2](https://arxiv.org/abs/2511.12884v2)). The populations differ, so both can hold, and neither licenses a stale rules file ([Agent Context File Evolution](agent-context-file-evolution.md)).

There is a case against acting on RAMP at all. The closest thing to controlled evidence points the other way. Gloaguen et al. varied context files across models, agents, and both generated and developer-committed sources, and found no general gain in task success. The two results are still compatible. One measures whether the agent solves more issues, the other the shape of what it writes over six months.

## Example

A single `AGENTS.md` usually carries both content types, and only one of them has evidence behind it. Both blocks below are quoted verbatim from the same file, the `AGENTS.md` of the repository that publishes this page.

**Before** — line 3, a repository overview, the type Gloaguen et al. measured as unhelpful:

```markdown
Training content for experienced developers leveling up with AI coding assistants. Tool-agnostic principles with Claude Code, GitHub Copilot, and Cursor coverage. Built on MkDocs Material; published to `agentpatterns.ai`.
```

**After** — line 16, a constraint on a real tool, the type agents were measured to follow:

```markdown
- **Package manager**: `uv` — never `pip` (a PreToolUse hook blocks bare `pip`).
```

The second states a rule the agent can violate and names the enforcement that catches it when the agent ignores the file. The first states nothing an agent could disobey. Both halves matter. The guardrail channel is the only one with independent support, and a rule with nothing behind it still rests on compliance the [structure study](configuration-file-structure-compliance-gap.md) found no way to raise.

## Key Takeaways

- Commit the rules file before adopting agents. Most teams never add a second level, so the first commit is the governance decision rather than a starting point they iterate on.
- Write constraints, not architecture tours. Only the instruction half of a context file has independent evidence behind it.
- Do not read the 2x ratio as a promise. It is an observational contrast among agent-first repositories, measured on static-analysis proxies, and the authors present it as hypothesis-generating.
- Keep the gates that bind regardless of what the agent read. Configuration is cheap insurance, not a substitute for review, tests, and static analysis.

## Related

- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — the benchmark evidence that context files do not raise task success
- [Empirical Baseline: Agentic AI Coding Tool Configuration](empirical-baseline-agentic-config.md) — which configuration mechanisms teams actually use, without outcome measures
- [Agent Context File Evolution](agent-context-file-evolution.md) — the maintenance discipline, and the study that conflicts with RAMP's set-and-forget rate
- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md) — which rule types survive contact with an agent
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — why adding artifacts to climb a level can cost adherence
