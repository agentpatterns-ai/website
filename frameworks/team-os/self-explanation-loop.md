---
title: "Self-Explanation Loop"
description: "A prompting pattern that asks the coding agent to justify structural and tooling choices so the user builds the mental model to curate them — bounded by well-documented failure modes when LLM explanations inflate confidence without building skill."
tags:
  - human-factors
  - instructions
  - tool-agnostic
---

# Self-Explanation Loop

> Ask the agent to justify its structural and tooling choices — but lead with the conditions under which the returned explanation can inflate confidence without building real competence.

The loop is simple in shape: after an agent proposes a structural or tooling decision, the user asks *why this, and what would change if we chose the alternative?* The returned answer is the learning artifact, not the code. This inverts the default user→agent query direction — from *produce X* to *justify X against its alternatives* — so the user commits a hypothesis before hearing the rationale. On a Team OS repo, where a non-engineer is the long-term curator of agent-chosen conventions, a repo they cannot explain is a repo they cannot evolve.

Treat the page as a **qualified** technique. The underlying cognitive mechanism is strong; applying it through an LLM surface is where the failure modes live.

## Caveats — Read First

Four conditions under which the loop backfires:

- **Illusion of Explanatory Depth (IOED).** In a three-arm N=102 study, participants who received GPT explanations showed the largest gap between predicted and actual explanation quality — objectively producing *less accurate, shorter, lower-vocabulary* explanations than the no-GPT arm ([Sciety preprint](https://sciety.org/articles/activity/10.31234/osf.io/8psgf_v1)). Fluent agent prose triggers cognitive ease; the feeling of understanding runs ahead of any understanding itself.
- **Post-hoc rationalisation.** The agent's stated reason for "why YAML" is not guaranteed to be the computation that produced the choice. The faithfulness literature documents LLM justifications that are persuasive and causally unrelated to the mechanism behind the answer ([arXiv 2603.01190](https://arxiv.org/html/2603.01190)).
- **Performance ≠ learning.** In AI-assisted programming education, students outperformed controls on the task but showed *no* pre–post knowledge gain — the explanation produced completion, not transfer ([ScienceDirect 2025](https://www.sciencedirect.com/science/article/pii/S2666920X25001778)).
- **Scaffolding threshold.** Self-explanation effects are smaller for less-prepared learners when working-memory load is high ([Bisra et al. 2018](https://link.springer.com/article/10.1007/s10648-018-9434-x)). A non-engineer asked to self-explain an unfamiliar tooling choice while still learning git is below the threshold the mechanism requires.

## The Mechanism

Generating an explanation forces constructive inference across prior knowledge and new material, producing stronger schemas than reading an identical explanation passively. The meta-analytic effect across 5,917 learners and 69 effect sizes is *g = .55*, with prompted self-explanation beating provided explanation and periodic prompting beating one-shot ([Bisra et al. 2018](https://link.springer.com/article/10.1007/s10648-018-9434-x)). The foundational result — that high-explainers outperform low-explainers via constructive inference — is [Chi et al. 1994](https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1803_3).

Direct evidence this generalises to coding-agent use comes from the [Anthropic (Shen & Tamkin 2026) RCT, N=52](https://www.anthropic.com/research/AI-assistance-coding-skills): "conceptual inquiry" (ask *why*) and "hybrid code-explanation" patterns scored ~65% on the skill quiz against ~40% for full-delegation patterns.

## The Prompting Pattern

Hannah Stulberg names the pattern verbatim: *"I have a feature index in the repo as a YAML file. If someone didn't understand why this was a YAML file, I would ask Claude to explain the benefits"* (Aakash Gupta podcast, 1:17:16, [transcript](https://www.aakashg.com/hannah-stulberg-podcast/)). Formalised in the companion write-up: *"when you encounter a file you do not understand — explain why this is a YAML file and not markdown"* ([source](https://www.news.aakashg.com/p/claude-code-team-os)).

The **escalation prompt** — the one upgrade over a bare "why?" — is *"what are 2–3 alternatives and when would each win?"* This forces the agent onto a tradeoff surface that is harder to confabulate coherently and returns falsifiable conditions the user can test later.

## Scope: When to Ask

Only for decisions the user will curate long-term:

- Tool and format choices (YAML vs Markdown, JSON vs TOML).
- Folder layout and ownership boundaries.
- `CLAUDE.md` placement and hierarchy.
- Plan-mode gates and naming conventions.

Not for every output. If the user can already name the alternative and one reason it is worse, skip the loop — running it anyway burns review budget without new schema formation.

## Escalation — Three Alternatives

- **Defer to convention.** For community-stable defaults (YAML for structured config, folder-per-function in a small team), accept the scaffold and spend the cognitive budget on strategy instead. Wins when the decision is well-understood and the team is on the critical path.
- **Ground-truth-first explanation, then interrogation.** For users below the scaffolding threshold, reverse the order: have the agent teach the baseline vocabulary first, then ask *why*. This is [deliberate AI-assisted learning](../../human/deliberate-ai-learning.md) applied to tooling.
- **Critic agent review.** Instead of the user interrogating the decision, a second agent critiques the plan before execution ([critic-agent plan review](../../agent-design/critic-agent-plan-review.md)). Wins when speed matters more than the user's long-term curation skill.

## Example

The canonical artifact is Stulberg's *"why is this a YAML file?"* moment. She has a feature index checked in as YAML. A teammate who inherits the repo cannot adapt the file without understanding the choice, so the prompt goes to Claude: *"explain why this is a YAML file and not markdown."* The agent returns a tradeoff — structured key/value access versus free-form prose — and the escalation prompt forces it to name at least one condition under which Markdown would have been correct. The teammate can now (a) predict what would have to change to justify Markdown and (b) defend the YAML choice to a third party a week later. Those two checks are the falsifiability tests that distinguish real comprehension from fluent agreement.

## Key Takeaways

- The loop asks the agent to justify structural choices so the user builds the mental model to curate them — the artifact is the explanation, not the code.
- Lead with caveats. IOED amplification, post-hoc rationalisation, and the performance/learning gap are documented failure modes of LLM-mediated self-explanation.
- The escalation prompt — *"2–3 alternatives and when would each win?"* — is the one prescriptive upgrade over a bare "why?", because tradeoff surfaces are harder to confabulate.
- Scope to structural and tooling decisions the user will curate long-term, not every agent output.
- Verify with two checks: can the user predict the losing alternative, and can they defend the decision to a teammate a week later? Without both, the loop terminates in fluent agreement.

## Related

- [Team OS](index.md) — the framework this page composes into
- [Deliberate AI-assisted learning](../../human/deliberate-ai-learning.md) — the general active-learning frame this page specialises
- [Strategy over code generation](../../human/strategy-over-code-generation.md) — why the curator's leverage lives above the output
- [Critical instruction repetition](../../instructions/critical-instruction-repetition.md) — the complementary instruction-side mechanism for retention
- [Plan mode for knowledge artifacts](plan-mode-knowledge-artifacts.md) — the sibling pattern that gates *production*; this one gates *acceptance*
