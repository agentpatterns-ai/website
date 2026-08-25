---
title: "The Citizen-Agent-Expert Operating Model for AI Coding"
term: "Citizen-Agent-Expert Operating Model"
description: "A three-tier operating model where citizens build, agents execute, and experts govern the guardrails that let generated code reach production safely."
tags:
  - human-factors
  - tool-agnostic
aliases:
  - citizens build agents execute experts govern
  - three-tier operating model for AI teams
last_reviewed: 2026-08-20
maturity: emerging
---

# The Citizen-Agent-Expert Operating Model for AI Coding

> A three-tier operating model where citizens build, agents execute, and experts govern the guardrails that let generated code reach production.

The citizen-agent-expert model describes where engineering value moves when AI writes most of the code: non-specialists can originate work, agents execute it, and experienced engineers own the guardrails, platforms, and feedback loops that decide whether the result reaches production. The framing comes from Rachel Laycock, CTO at Thoughtworks, who proposed the phrase "citizens build, agents execute, experts govern" as a description of a change in role weighting rather than a set of new job titles ([Laycock, martinfowler.com, 2026](https://martinfowler.com/rachels-ramblings/citizens-agents-experts.html)).

## The three tiers

Citizens are the people closest to a problem who can now hold a specification and get a working application from it. An executive prototypes an internal workflow, a domain expert wires a chatbot, an analyst builds a small automation. Twelve months ago they could not have shipped code at all ([Laycock](https://martinfowler.com/rachels-ramblings/citizens-agents-experts.html)).

Agents are the execution surface. They write, refactor, test, and iterate code at speeds a human keyboard cannot match. Laycock relays one production shape from a peer conversation: "one team described spending the day designing a specification, letting agents work overnight and reviewing the results the next morning". The account puts the weight on the humans rather than the pipeline — "deciding what good looked like, making trade-offs and judging whether what came back was actually what they wanted" ([Laycock](https://martinfowler.com/rachels-ramblings/citizens-agents-experts.html)).

Experts are experienced engineers whose leverage moves from writing every feature to creating the environment in which thousands of features can be built safely by other people and by agents. Their work is guardrails, platforms, engineering practices, and feedback loops. This is the discipline named ["rigor relocation" in the harness-engineering literature](../patterns/agent-design/harness-engineering.md).

## Where the boundary sits

The gate is production admission. Laycock places it precisely: "the moment that application becomes something the business depends on, the questions change completely. Is customer data protected? What happens when a dependency fails? Can someone else understand this system in two years' time? Will it survive an audit?" ([Laycock](https://martinfowler.com/rachels-ramblings/citizens-agents-experts.html)). Before that moment a citizen-built app is real software solving a real problem; after it, the questions the expert tier owns become load-bearing.

This is the same boundary the corpus's [delegated-autonomy boundary artifacts](../patterns/agent-design/delegated-autonomy-boundary-artifacts.md) describe at the tool layer. The three-tier model is the organizational form of that boundary. It names who is authorized to originate on each side of the gate and what artifacts hold the line.

## Why it works

As agents drive the cost of code production toward zero, engineering scarcity relocates from authorship to the gates that decide whether generated code deserves to run in production. Laycock names the relocation directly: "what feels scarce now is good engineering judgement: knowing what good looks like, understanding the risks and knowing when something that works is actually safe to trust in production" ([Laycock](https://martinfowler.com/rachels-ramblings/citizens-agents-experts.html)). Martin Fowler's rigor-relocation framing supplies the same mechanism in tool terms: discipline moves to constraint design, verification systems, and intent specification when the model does the typing ([Fowler: Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)).

Faros AI data on high-adoption teams quantifies where the relocation lands. They report 98% more pull requests merged while review times ran 91% longer, so generation roughly doubled while review capacity stayed flat ([Osmani: The 80% Problem](https://addyo.substack.com/p/the-80-problem-in-agentic-coding)). Three roles fall out of this pattern rather than from titling. Citizens become anyone who can hold a specification. Agents become the execution surface. Experts become the tier that owns the guardrails, platforms, and feedback loops the other two run on.

## When this backfires

The model degrades in five stated conditions.

- Understaffed expert tier. When citizens can ship apps in a weekend but the expert tier still reviews one pull request at a time, governance becomes a bottleneck. Either every launch delays, or the sanctioned path gets bypassed for shadow AI. AI agents inside citizen-development platforms create audit exposures such as unmonitored connectors, hidden data propagation, and cross-environment jumps that scale with agent activity rather than citizen headcount ([Finzi, Forbes, 2026](https://www.forbes.com/councils/forbestechcouncil/2026/01/16/how-ai-agents-in-citizen-development-will-create-a-governance-crisis/)).
- Governance retrofitted after adoption. Three prior citizen-development waves (spreadsheets, low-code, robotic process automation) each decentralized building successfully and then stalled because each tool produced its own silo of logic, access, and information that nothing else could see or trust ([Chavez-Mattos, MindStudio, 2026](https://www.mindstudio.ai/blog/why-citizen-development-finally-works)). Applying the three tiers to an already-fragmented estate produces theatre.
- Expert tier detached from execution. If experts only govern and never build, they lose the calibration to know whether the agent's output is safe. The corpus records this as [skill atrophy in the review layer](skill-atrophy.md); METR measured developers taking "19% longer than without" while still believing "AI had sped them up by 20%" — a 39-point gap between perception and measurement, by subtraction ([METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)).
- No production-admission gate. The boundary Laycock names is "the moment that application becomes something the business depends on" ([Laycock](https://martinfowler.com/rachels-ramblings/citizens-agents-experts.html)). Without a defined path from prototype to production, the three tiers describe nothing enforceable.
- Throw-it-over-the-wall degradation. Laycock flags the antipattern by name: "people build stuff and throw it to engineers to fix, that is a total antipattern" ([Laycock](https://martinfowler.com/rachels-ramblings/citizens-agents-experts.html)). The model collapses into two-tier queueing (citizens generate, experts refactor) with none of the governing-by-construction it requires.

## Example

An insurance firm gives its analysts a Copilot-style agent to build internal apps. In one quarter, the sanctioned catalog grows from three to forty tools. The two-engineer platform team was staffed for the old ratio: it hand-reviews each new deployment and cannot keep up. Analysts start bypassing the team, standing up unreviewed integrations directly against production databases.

The team re-baselines around the three tiers. It adds a production-admission checklist that every citizen-built app runs before it can touch customer data. It publishes a shared platform of vetted connectors, an audit log of agent-initiated changes, and a rollback path any analyst can trigger. The two engineers grow into a small platform group whose work is guardrails rather than features. Citizens keep shipping at their own pace; experts stop being the review bottleneck and become the environment citizens ship into. The rate of new tools stays flat; the rate of production-safe tools rises.

## Key Takeaways

- The citizen-agent-expert model is a change in where engineering value sits when agents write most of the code, not a set of new job titles.
- The gate between the citizen tier and the expert tier is production admission — the moment an app becomes something the business depends on.
- Experts govern with guardrails, platforms, engineering practices, and feedback loops rather than by writing every feature.
- The model breaks when the expert tier is understaffed, retrofitted after adoption, detached from execution, missing a production gate, or reduced to fixing what citizens throw over the wall.

## Related

- [The Review Bottleneck Migration](bottleneck-migration.md) — the economic reading of the same shift: where the delivery constraint moves once generation gets cheap
- [Intent-Centric Engineering: Oversight Over Authorship](intent-centric-engineering.md) — the operating model that describes what the expert tier's work becomes once agents author the code
- [Delegated-Autonomy Boundary Artifacts (AJR and ADP)](../patterns/agent-design/delegated-autonomy-boundary-artifacts.md) — the tool-layer form of the boundary the three-tier model draws at the org layer
- [Risk Architecture for AI-Native Engineering Teams](risk-architecture-ai-native-teams.md) — the ownership, escalation, and assurance side of the same shift
- [AI Abundance Reshapes Software Engineering Identity](ai-abundance-engineering-identity.md) — the identity-side reading of why generation cheapens and judgement gets scarce
- [Author-to-Reviewer Role Inversion in AI-Assisted Teams](author-to-reviewer-role-inversion.md) — the staffing and measurement inversion the model implies for the expert tier
- [Verification-Gated Agent Autonomy via Automated Review](../patterns/agent-design/verification-gated-agent-autonomy.md) — the mechanized gate that makes production admission tractable at citizen-tier volume
