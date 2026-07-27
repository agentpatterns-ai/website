---
title: "Programming Language Choice Still Shapes Agent Artifacts"
description: "Coding agents reach every language, but the language you pick still decides performance ceiling, run cost, and how much verification you owe — budget both."
tags:
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - language choice for AI coding agents
  - polyglot agent verification budget
  - low-resource language verification gap
maturity: emerging
last_reviewed: 2026-06-16
status: current
---

# Programming Language Choice Still Shapes Agent Artifacts

> Agents reach every language, but the language you pick still decides performance ceiling, run cost, and verification effort.

Language choice is no longer a feasibility check for AI coding agents — frontier agents produce working systems in any language, including ones with no prior open-source examples ([Acher and Jézéquel, 2026](https://arxiv.org/abs/2606.13763)). It still decides the artifact's shape along four dimensions: strength ceiling, run cost, engineering effort, and the human-verification work you inherit. Prefer well-represented languages when artifact quality matters. Budget extra verification when something forces a long-tail target.

## The four dimensions language choice still decides

[Acher and Jézéquel (2026)](https://arxiv.org/abs/2606.13763) prompted Claude Opus 4.6 and Codex (GPT-5.2) to build chess engines from scratch across 17 languages — chess admits external Elo strength assessment against [Stockfish](https://stockfishchess.org) and feature-level inspection, so every artifact was measured the same way. Every category produced a working engine. The gaps were elsewhere:

| Dimension | Mainstream (Rust, C++, Java) | Specialized / Academic | Legacy / Esoteric |
|---|---|---|---|
| Playing-strength ceiling | ~1900–2200 Elo | ~1300–1700 Elo | 400–1500 Elo |
| Run cost per engine | $20–$110 | $30–$175 | $50–$474 |
| Prompt cycles required | 3–16 | moderate | 25–50 |
| Feature mix | bitboards, transposition tables, tapered evaluation | mostly present | material-only evaluation, no transposition tables |

Source: [Acher and Jézéquel, 2026](https://arxiv.org/abs/2606.13763). The agents reproduced the same conceptual blueprint (search, evaluation, board representation) in every language but adapted feature selection to the language's idiom — a Rust engine and a COBOL engine diverged at sub-feature granularity even when the prompt and agent were identical.

The pattern is independent of one paper. [MultiPL-E](https://arxiv.org/abs/2308.09895) reports pass@1 of 4.7 to 11.3 for Racket and 11.3 to 41.9 for Julia, versus more than 40 for Python on the same models — the same training-corpus asymmetry the chess study reproduces at task scale rather than function scale. The [Wu et al. (2024) survey](https://arxiv.org/abs/2410.03981) (111 papers, 2020 to 2024) names this gap "low-resource programming languages" and identifies data scarcity as the root cause.

## Why it works

Coding agents are next-token predictors over a training corpus where mainstream languages are over-represented by orders of magnitude. The asymmetry surfaces as shorter debug loops, fewer hallucinated library calls, and tighter feature selection in well-represented languages, and the opposite in long-tail ones. [Acher and Jézéquel (2026)](https://arxiv.org/abs/2606.13763) measure it directly: debug-prompt fractions exceed 0.4 for legacy and esoteric runs versus under 0.2 for mainstream, and library-evasion attempts cluster in DSL targets where the agent reaches for the represented-elsewhere fallback (a CSS run silently imported `python-chess` until supervision caught it).

## What to do with this

Two coupled decisions sit behind any agent-heavy build.

Pick the language for the agent's training-corpus density when quality matters. If the artifact has a strength ceiling, longevity expectation, or production load, choose a mainstream, well-represented language. The Bun runtime's [Zig-to-Rust migration](https://byteiota.com/bun-rust-rewrite-merged-the-13000-unsafe-block-problem/) ported 960,000 lines in six days at 99.8% test pass once the target was Rust — language choice is downstream of where the agent can converge.

Budget extra verification when steering into a long-tail language. The work you inherit grows the further the language sits from the mainstream:

- Refuse agent self-evaluation. Agents over-estimated their engine's Elo by 200 to 1100 points against an external gauntlet ([Acher and Jézéquel, 2026](https://arxiv.org/abs/2606.13763)). Run third-party benchmarks. Do not trust the agent's verdict on its own output.
- Watch for library evasion. The CSS-imports-`python-chess` pattern is the canonical tell. Audit dependency manifests and runtime imports as part of acceptance.
- Demand denser tests. Behavioral coverage anchors agent convergence — [coding-agent reversibility](coding-agent-reversibility.md) covers the test-density mechanism. Legacy and esoteric tiers need larger suites.
- Account for the cost multiplier. Exotic targets cost 10 to 25 times mainstream ([Acher and Jézéquel, 2026](https://arxiv.org/abs/2606.13763)).

## When this backfires

The language-density framing breaks in four cases:

- Throwaway artifacts. Prototypes and disposable code never hit the quality ceiling that the gap measures. Choose for team velocity instead.
- Mainstream-only stack switches. Within Python, TypeScript, and Go, the Elo and pass@1 gaps narrow sharply — [MultiPL-E](https://arxiv.org/abs/2308.09895) places all three near the top of its pass@1 distribution. Reviewer fluency and tooling familiarity dominate ([cross-tool translation](cross-tool-translation.md)).
- Domain-mandatory languages. Embedded C, Solidity, ladder logic, and hardware-description languages — the domain dictates the language. Apply the verification-budget half and skip the language-selection half.
- Reviewer-bottlenecked teams. When reviewer expertise sits in one language and the team cannot review the higher-density alternative, switching shifts the bottleneck rather than removing it.

The [agentic AI is abstracting away code](https://medium.com/agileinsider/agentic-ai-is-abstracting-away-code-real-edge-is-systems-thinking-f512c8e4e9e9) argument applies inside these cases; it does not apply at the performance-ceiling tier the chess study measures.

## Key Takeaways

- Language choice is no longer about whether an agent can produce a working system — agents reach every language, including those with no prior open-source example ([Acher and Jézéquel, 2026](https://arxiv.org/abs/2606.13763)).
- Language choice is still about strength ceiling, run cost, engineering effort, and feature mix — quantified by the chess study and corroborated by [MultiPL-E](https://arxiv.org/abs/2308.09895) and the [Wu (2024) survey](https://arxiv.org/abs/2410.03981).
- Agents over-estimate their own output by hundreds of Elo on long-tail languages — refuse self-evaluation, run external benchmarks.
- Pick for density when quality matters; budget verification when forced long-tail. The framing breaks for throwaway artifacts, within-tier switches, domain-mandatory languages, and reviewer-bottlenecked teams.

## Related

- [Coding-Agent Reversibility: Platform Choice as a Two-Way Door](coding-agent-reversibility.md) — the migration-decision twin; behavioral test coverage is the binding constraint when porting between languages.
- [Cross-Tool Translation: Learning from Multiple AI Assistants](cross-tool-translation.md) — when team velocity dominates the language-density edge.
- [Strategy Over Code Generation](strategy-over-code-generation.md) — artifact-shaping decisions sit upstream of agent speed.
- [Suggestion Gating: Why Fewer AI Completions Improve Developer Experience](suggestion-gating.md) — gating lower-density outputs is the same shape as steering away from low-resource languages.
