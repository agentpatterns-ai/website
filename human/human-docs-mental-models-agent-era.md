---
title: "Human-Facing Docs in the Agent Era: Mental Models Over Reference"
description: "When agents absorb the machine-readable doc load, the residual job of human-facing documentation is mental models, intent, design exclusions, and trust calibration — not exhaustive reference."
tags:
  - human-factors
  - tool-agnostic
aliases:
  - human-centric documentation
  - human documentation in the agent era
last_reviewed: 2026-06-13
maturity: adopted
---

# Human-Facing Docs in the Agent Era: Mental Models Over Reference

> When the reader is paired with an agent, human docs shift from exhaustive reference to mental models, design intent, and trust calibration.

Human-facing documentation has a distinct residual job once agents absorb the machine-readable load (AGENTS.md, `llms.txt`, structured API specs). The shift is not "write less" but "write for the resource that is now scarce" — practitioner attention spent on intent, trade-offs, and what the tool deliberately excludes. Drew Breunig sets this out in five rules drawn from rewriting the [DSPy docs](https://dspy.ai/getting-started/program-dont-prompt/) with a documentation skill ([Breunig, 2026-05-31](https://www.dbreunig.com/2026/05/31/what-do-humans-need-from-docs.html)).

## When this applies

The reframing is correct only under specific conditions. Lead with these before adopting any of the five rules:

- The audience is paired with an agent at read time. Tutorials, internal platform docs, and open-source tool docs read alongside Claude, Copilot, or Cursor. "Agents can find the details" is a load-bearing assumption — it must actually be true for the reader.
- The surface is not itself a contract. Mental-model docs are not a substitute for a contractual reference. Regulated SDKs, audited public specs, and breaking-change-SLA-bound APIs need the parameter table because the parameter table is the artifact.
- Stale-training-data risk is bounded. When the agent's training data lags the surface, the human reviewer needs the authoritative reference the agent did not have — see [Designing for Agent Consumers (Agent Experience)](../tool-engineering/designing-for-agent-consumers.md) §"Keep machine-readable signatures current and discoverable."

Outside those conditions the recommendation backfires — see [when this backfires](#when-this-backfires) below.

## The five rules

Each rule names what the human reader uniquely retains value from once an agent handles the rest ([Breunig, 2026](https://www.dbreunig.com/2026/05/31/what-do-humans-need-from-docs.html)):

1. Build mental models, not a reference. Humans need a structural picture of what the tool is, how its parts relate, and where it fits. Agents enumerate; humans orient. [Reference enumeration](../tool-engineering/designing-for-agent-consumers.md) optimizes for the wrong reader.
2. Teach the art of the possible. Show what the tool enables so the reader can prompt the agent with the right intent. A reader who does not know capability `X` exists cannot direct an agent to use it.
3. Explain the why. Intent is the layer the agent cannot reconstruct from code alone. A reader who understands why a tool exists "can reason beyond the obvious"; a reader who only sees `what` is stuck at the literal surface.
4. Detail the design decisions. What the tool deliberately chose not to do is high-signal context. Exclusions [narrow the search space](../instructions/agents-md-as-table-of-contents.md) the agent — and the human supervising it — would otherwise wander.
5. Do not optimize for completeness. Introduce only what builds an effective mental model. The temptation to enumerate nuances is the failure mode being corrected; trust the agent to surface the rest.

Breunig states the goal directly: "The goal is to prepare your audience to prompt an agent effectively" ([Breunig, 2026](https://www.dbreunig.com/2026/05/31/what-do-humans-need-from-docs.html)).

## Distinguishing the doc surfaces

The five rules apply to prose docs aimed at humans. Three adjacent surfaces have different jobs and different rules; the categories are not interchangeable.

| Surface | Reader | Job | Site coverage |
|---------|--------|-----|---------------|
| Human-facing docs (this page) | Practitioner, often paired with an agent | Mental models, intent, design exclusions | — |
| Project instruction file | Agent beginning a task in this repo | Pointer map to conventions, constraints, commands | [AGENTS.md: Project-Level README](../standards/agents-md.md), [AGENTS.md as a Table of Contents](../instructions/agents-md-as-table-of-contents.md) |
| Curated site index | Agent navigating this site at inference time | Top-level index of canonical pages | [llms.txt: Spec, Adoption, and Honest Limitations](../geo/llms-txt.md) |
| Agent-consumable SDK/CLI/API | Agent calling the product surface | Machine-legible signatures, structured errors, headless reachability | [Designing for Agent Consumers (Agent Experience)](../tool-engineering/designing-for-agent-consumers.md) |

Conflating them produces predictable failures: a reference rewritten as an AGENTS.md crowds the agent's context with prose intent; an AGENTS.md rewritten as a mental-model doc strips the literal commands the agent needs to run.

## Skills as human-facing docs

Breunig's adjacent observation: "no one wanted to write documentation, but everyone is writing skills." Four reasons explain the asymmetry — the agent drafts most of the skill, it can be iterated as it is used, it delivers value immediately, and rough drafts are tolerated. Skills double as documentation, and "crack open a library or product's skill and you're often reading documentation that's better than their website" ([Breunig, 2026](https://www.dbreunig.com/2026/05/31/what-do-humans-need-from-docs.html)).

Anthropic defines a skill as "folders of instructions, scripts, and resources that an agent loads dynamically to improve performance on specialized tasks" ([Anthropic Support](https://support.claude.com/en/articles/12512176-what-are-skills)). Simon Willison's parallel observation about system prompts — "they act as a sort of unofficial manual for how best to use \[AI\] tools" ([Willison, 2025](https://simonwillison.net/2025/May/25/claude-4-system-prompt/)) — extends the same logic: artifacts written for the agent often beat the human-targeted docs at the human's job, because the agent-targeted register forces the intent, the constraints, and the design exclusions to the surface.

The convergence is diagnostic, not prescriptive. When a skill reads better than the docs, the docs were over-serving completeness — the five rules above are the correction, not the destination.

## Why it works

The mechanism is asymmetric attention cost. Agents enumerate, index, and recall reference material on demand — "agents can find the details" ([Breunig, 2026](https://www.dbreunig.com/2026/05/31/what-do-humans-need-from-docs.html)) — while practitioner attention is bounded and cannot be regenerated within a session. Loading scarce human attention with what an agent retrieves trivially wastes the scarce resource. The reader who holds the why can supervise an agent across an unbounded set of details; the reader armed only with a flat reference must re-derive intent every time. The skills-double-as-docs signal corroborates this: when one artifact serves both the agent and the human well, the human doc was paying for completeness the agent already supplied.

## When this backfires

The five rules invert under conditions where the reference is the contract or where the agent is not a reliable retrieval partner:

- Reference-as-contract surfaces. Public SDKs with breaking-change SLAs, regulated APIs, and audited specs need the parameter table as a verifiable artifact. A mental-model doc cannot adjudicate whether a field is named `ttl_seconds` or `max_age_seconds` — the spec must.
- Reviewer-of-last-resort workflows. When a human is auditing agent output as the final gate (security review, compliance audit, paper review), "agents can find the details" assumes the agent's details are right. The human needs the authoritative reference the agent did not have, especially when the agent's training data is stale relative to the surface — the same staleness failure mode documented in [Designing for Agent Consumers](../tool-engineering/designing-for-agent-consumers.md).
- Onboarding without an agent in the loop. Interview prep, offline reading, regulated environments without agent access. Mental-model-only docs assume every reader is paired with an agent at read time.
- Skills that bloat context. Skills double as docs only when written to the same standard as the prose docs they replace. Badly written skills "bloat and poison your context" ([Breunig, 2025-06-22](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)); a stripped-down human doc rewritten in the agent register and then loaded by the agent inherits the same failure. The five rules require editorial discipline, not less work.

## Example

Breunig built `scaffold-docs`, an opinionated skill that operationalizes the five rules into a three-tier structure ([scaffold-docs on GitHub](https://github.com/dbreunig/scaffold-docs-skill)):

1. Getting Started — a narrative tutorial covering a single representative use case.
2. Diving Deeper — one file per topic, organized around intent and design decisions (not API surface).
3. Reference — [per-module API spec](../tool-engineering/designing-for-agent-consumers.md), lookup-oriented.

Two structural choices reinforce the five rules. First, the tutorial is single-use-case — Breunig refuses to enumerate use cases in the mental-model layer; the agent does that on demand. Second, the Diving Deeper tier is organized by intent, not API surface, so the human reader reaches design decisions without traversing a reference they did not need. The skill builds each section in passes — structure first, then headers and topic sentences, then full prose — and "the agent pauses for your review between passes and does not advance until you approve" ([Breunig, 2026](https://www.dbreunig.com/2026/05/31/what-do-humans-need-from-docs.html)), keeping the human in the editorial loop the five rules require.

## Key Takeaways

- The residual job of human-facing docs is mental models, intent, design exclusions, and [trust calibration](visible-thinking-ai-development.md) — not exhaustive reference. Agents retrieve details on demand.
- The pivot is conditional on the audience being paired with an agent at read time and the surface not being a contractual reference. Reference-as-contract surfaces and reviewer-of-last-resort workflows still need the table.
- Human-facing docs, [project instruction files](../standards/agents-md.md), curated site indexes, and agent-consumable SDK surfaces are four different artifacts with four different jobs. Conflating them produces predictable failures.
- Skills frequently read better than the docs they ostensibly support — a diagnostic signal that the original docs were over-serving completeness, not a prescription to replace docs with skills.

## Related

- [Designing for Agent Consumers (Agent Experience)](../tool-engineering/designing-for-agent-consumers.md) — The complementary discipline on the agent-facing surface (SDK, CLI, errors, docs an agent calls).
- [AGENTS.md: Project-Level README for AI Coding Agents](../standards/agents-md.md) — Project instruction file as orientation for the agent, distinct from human-facing prose.
- [AGENTS.md as a Table of Contents, Not an Encyclopedia](../instructions/agents-md-as-table-of-contents.md) — Why agent-facing project files fail when written as exhaustive reference.
- [llms.txt: Spec, Adoption, and Honest Limitations](../geo/llms-txt.md) — The curated site index agents consume at inference time.
- [Visible Thinking in AI-Assisted Development](visible-thinking-ai-development.md) — Documenting intent across commits and PRs as a sibling discipline to documenting intent in prose docs.
- [Marking Which Artifacts Are for Humans or Agents (Landmarking)](landmarking-human-vs-agent-artifacts.md) — The prior question: which artifacts have a human audience at all, agreed as a team convention.
