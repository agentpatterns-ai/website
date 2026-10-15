---
title: "Irreducibility Triage: What to Write Down for Agents"
term: "Irreducibility Triage"
description: "Rank agent-facing artifacts by whether a better model could ever supply their content. Adequacy criteria, renegotiated domain knowledge, and a system's intended trajectory are the three kinds no corpus holds."
aliases:
  - irreducible knowledge triage
  - artifact durability triage
  - what to write down for agents
tags:
  - instructions
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-14
maturity: emerging
---

# Irreducibility Triage: What to Write Down for Agents

> Triage agent artifacts by whether a better model could ever supply the content. What no corpus holds is what keeps paying.

## When this triage applies

Use it when you hold more agent-facing artifacts than you can keep current and must pick which get the maintenance budget. It ranks durability across model upgrades. It does not tell you whether an artifact changes the agent's behavior on today's task, and the two answers often disagree.

## Two kinds of artifact content

Fuggetta splits what a coding agent lacks into a layer models can take in and a core they cannot. Specification methods, architectural styles and testing frameworks sit in the first layer, a "reducible surface" that "specialized models can absorb" ([Fuggetta, 2026](https://arxiv.org/abs/2610.10226v2), §2). General domain knowledge belongs there too, reachable through retrieval or domain training. Repository-level patterns are partly absorbable too. Customizing on two private enterprise repositories "helps models to learn the underlying patterns specific to the repository". The code completions of moderately sized customized models "can be significantly better than those of uncustomized models of much larger capacity" ([Finkler et al., 2026](https://arxiv.org/abs/2602.05780v1)).

Three kinds of content sit in the second layer. Whether this specification is adequate for this system needs "a domain-grounded reference the model cannot generate" ([Fuggetta, 2026](https://arxiv.org/abs/2610.10226v2), §2). Organization-specific knowledge is continuously renegotiated and never fully consistent (§2). The system's intended trajectory "does not exist until the software engineer reasons it into existence" (§2). The claim about all three is categorical: "evaluative judgment, organizational knowledge, and a system's future trajectory cannot be distilled from any corpus" (§3).

Fuggetta's own artifact list sits on the second layer by construction. He names two mechanisms. The operational one, the engineer supplying artifacts, maps to the irreducible core, while embedding method in the agent's design covers the reducible layer (§4). A specification supplies "the criterion of adequacy" the model cannot generate for itself, a domain constraint record holds the organization-specific core. An Architecture Decision Record carries "the design choices that accumulate over the system's life, along with the why and the intended trajectory that no session context preserves" (§5). Those three sit on the irreducible side and keep their value when you switch models. A page restating the reducible surface is a maintenance cost whose payoff falls as models and customization improve.

## Why it works

Statelessness is why artifacts matter at all: cross-session memory stores prior exchanges rather than accumulated know-how, so a decision taken last Tuesday and a specification agreed last month share the same fate. Of both, "none becomes usable knowledge unless it has been reified as an artifact" ([Fuggetta, 2026](https://arxiv.org/abs/2610.10226v2), §2). Absence from every corpus is why some artifacts outlast a model generation. The paper calls this structural rather than historical, and says plainly that reification "narrows the vacuum without closing it" (§3).

This is deduction, not measurement. Fuggetta states the method: "we adopt a logical and epistemological approach" (§2). Treat the ordering as a reasoned prior, not a measured effect size.

## When this backfires

Durability is the wrong axis when the agent is violating a rule right now. Across 2,031 sessions on six frontier models, under default framing all six showed "instruction compliance rates of 0%", and "Claude Sonnet 4 verbally agrees ten out of ten times then bypasses in all ten" ([Shin, 2026](https://arxiv.org/abs/2605.01771v1), abstract). The same abstract reports the gap is selective, with 97% compliance on audit trails where rationale is rewarded. The paper attributes that spread to reward-signal alignment, not to user instruction. The instruction-side fixes it does measure are a correction prompt ("a single correction prompt achieves 100% repair under default framing (30/30)", Exp 5, §4.2) and interleaved reporting ("raised ICR from 0% to 52–100% for five of six models (Llama excepted)", Exp 7, §4.3). Rank by measured behavior change when the horizon is this sprint.

Three more conditions:

- The reducible line moves under you. Customization absorbs the repository-specific patterns a document would restate ([Finkler et al., 2026](https://arxiv.org/abs/2602.05780v1)), so the payoff of a conventions page falls as customization is adopted, while a design rationale record keeps its value.
- An unmaintained artifact stops being a reference. Fuggetta says any lifecycle can be supported by an AI engine "provided the artifacts are present and continuously maintained" (§5), and that all four knowledge levers "require reification" (§3), and the agent reading them is "without intrinsic reference for correctness or future orientation" (§3), so nothing in the loop notices a stale domain constraint record.
- The trajectory may not exist yet. Fuggetta's point is that it comes into being only when the engineer reasons it out (§2), so an artifact written earlier records a guess rather than a decision.

## Key Takeaways

- Sort your artifact list by one question — could any training corpus hold this content? — then maintain from the top. The files at the bottom are the ones to measure for deletion, not the ones to delete on sight.
- Durability and present-day effect are different axes. Rank by durability for maintenance budget, by measured behavior change for this sprint's output.
- Repository customization moves the line for repository-specific patterns, so re-run the triage when you adopt it.
- The argument is derived from a model of what an LLM is, not measured, so weight it as a prior and keep your own compliance measurements.

## Related

- [Skill Rule Novelty: Add What the Skill Does Not Name](skill-rule-novelty.md) — tests novelty against the file's own tokens, the complement to testing it against any corpus.
- [Knowledge Gap or Skill Gap: Triage Before Writing Context](knowledge-gap-vs-skill-gap-triage.md) — decides whether to write context at all, before this triage ranks what you wrote.
- [Constraint Encoding Does Not Fix Constraint Compliance](constraint-encoding-compliance-gap.md) — the compliance axis this triage deliberately does not cover.
- [Encoding Tacit Knowledge into Agent Improvement Loops](../workflows/encoding-tacit-knowledge.md) — elicitation technique for the organization-specific core.
- [Rigor Relocation: Engineering Discipline with AI Agents](../human/rigor-relocation.md) — where engineering effort lands once agents write the code.
