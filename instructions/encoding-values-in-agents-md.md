---
title: "Encoding Values in AGENTS.md: Why Prose Without Verification Fails"
term: "Encoding Values in AGENTS.md"
description: "Developers operationalize ethics, fairness, accessibility, and sustainability by writing them into AGENTS.md — but corpus studies show these values are mostly absent, and prose without verification rarely changes agent behavior."
tags:
  - instructions
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - operationalizing ethics in AGENTS.md
  - values in agent context files
last_reviewed: 2026-06-02
maturity: emerging
---

# Encoding Values in AGENTS.md: Why Prose Without Verification Fails

> Values written as AGENTS.md prose rarely change agent behavior; pair each one with a verification command or move it to a lower enforcement layer.

## The empirical gap

Two recent corpus studies measured what developers encode in context files. Functional content dominates; values content is sparse.

| Category | Chatlatanagulchai et al. (2,303 files) | Mohsenimofidi et al. (466 OSS repos) |
|---|---|---|
| Implementation details | 69.9% | Top category |
| Architecture | 67.7% | 47 instances |
| Build / run commands | 62.3% | 40 instances |
| Error handling / debugging | 24.4% | — |
| Security | 14.5% | 6 instances |
| Performance | 14.5% | — |
| Accessibility, fairness, sustainability, tone | Not measured (rare) | None found |

Mohsenimofidi et al. classified instructions by writing style — descriptive, prescriptive, prohibitive, explanatory, conditional — and found no explicit ethical, accessibility, fairness, or tone instructions across the analyzed AGENTS.md files ([Mohsenimofidi et al., 2025](https://arxiv.org/abs/2510.21413)). Chatlatanagulchai et al. note the same gap: developers "provide few guardrails to ensure that agent-written code is secure or performant" ([Chatlatanagulchai et al., 2025](https://arxiv.org/abs/2511.12884v2)).

A later vision paper tempers how absolute that gap is. [Treude et al., 2026](https://arxiv.org/abs/2605.05584) report that developers already embed fairness, accessibility, sustainability, tone, and privacy guidance, framing AGENTS.md as a "developer-authored governance layer." But the authors defer the question that matters here — whether agents reliably follow those values — to future work. Values prose can be present without changing behavior, and that gap is what this page addresses.

## Why values-as-prose fails

```mermaid
graph TD
    A[Values written as prose<br>in AGENTS.md] --> B[Compliance ceiling<br>~68% on long rule sets]
    A --> C[Primacy bias<br>earlier rules win attention]
    B --> E[Values omitted on individual turns]
    C --> E
    E --> F[No verification step<br>catches the omission]
    F --> G[Documented value,<br>unchanged behavior]
```

Frontier models top out at roughly 68% accuracy at 500 simultaneous instructions, and earlier instructions are satisfied more reliably than later ones — primacy effects peak around 150–200 instructions ([Jaroslawicz et al. — How Many Instructions Can LLMs Follow at Once?](https://arxiv.org/abs/2507.11538v1)). A "be accessible" sentence in a 500-line AGENTS.md inherits both penalties. Gloaguen et al. add a direct cost: verbose AGENTS.md files reduce task success and add about 20% inference cost on SWE-bench Lite and AGENTbench ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v2)).

## Verification, not prose

Pair every value with a mechanical check the agent runs; reduce the AGENTS.md line to a pointer.

| Value | Prose-only (low signal) | Verification-paired (high signal) |
|---|---|---|
| Accessibility | "Write accessible UIs." | "After UI changes, run `pnpm test:a11y` (axe-core); fix violations before commit." |
| Licensing | "Respect open-source licenses." | "Run `pnpm licenses:check`; only `MIT`, `Apache-2.0`, `BSD-*` allowed." |
| Fairness in data | "Avoid biased datasets." | "Run `scripts/dataset-audit.py` on every new dataset; CI fails on parity-check failure." |
| Security | "Write secure code." | "Run `gitleaks detect` and `npm audit --omit=dev` before commit." |

This matches the broader finding that [guardrails beat guidance](guardrails-beat-guidance-coding-agents.md) — tool-specific commands are the only AGENTS.md content with reliable behavioral effect ([Chatlatanagulchai et al., 2025](https://arxiv.org/abs/2511.12884)).

## Where values actually belong

To enforce values, AGENTS.md is rarely the right layer. Each value usually has a lower-level mechanism:

- Permissions and sandboxes — deny rules enforce "do not exfiltrate data" without prose
- CI checks — accessibility linters, license scanners, dataset audits, dependency scans
- Pre-commit hooks — secret scanning, formatting, deny-rule enforcement
- Branch protection — "do not commit to main" becomes a server-side rule

AGENTS.md then references the mechanism: "Run `make check-a11y`. If it fails, do not propose merging." That works because the agent can verify the outcome. Prose still earns space when it is short and points to a mechanism; a long ethics preamble with no follow-through does not.

## When this backfires

Verification-pairing is the right default, but it has failure conditions:

- Not every value can be mechanized. "Use inclusive tone" has no clean linter, and forcing one yields a brittle matcher that misfires — worse than honest prose plus human review.
- Over-mechanization breeds checkbox theater. Reduce a value to "CI is green" and teams optimize the check, not the value: a passing `dataset-audit.py` can certify data that is fair on the measured axis and biased on an unmeasured one.
- Premature mechanisms misdirect. Wiring a check before the value is understood freezes a wrong proxy into CI, so some values are better left as reviewed prose until a faithful check exists.

Where no faithful, cheap check exists, prose pointing at human review beats a misleading green check.

## Example

A real "before" pattern, rewritten for verification.

Before — values as advisory prose:

```markdown
# AGENTS.md

## Our values

We care deeply about accessibility, sustainability, and inclusive language.
Please write code that respects these values.

## Build

pnpm install
pnpm build
```

After — values pinned to mechanisms:

```markdown
# AGENTS.md

## Build & verify

- pnpm install
- pnpm build
- pnpm test:a11y      # accessibility (axe-core); CI fails on violations
- pnpm licenses:check # sustainability/licensing (MIT/Apache-2.0/BSD-* only)
- pnpm test           # unit + integration

Run all four before proposing a commit. Do not propose merging if any fail.

See docs/a11y.md and docs/licensing.md for the underlying policies.
```

The "after" version contains the same values commitments. The difference is that every value points to a command the agent runs, the result of which the team can audit.

## Key Takeaways

- Corpus studies show developers rarely encode fairness, accessibility, sustainability, or tone in AGENTS.md; functional context dominates ([Chatlatanagulchai et al.](https://arxiv.org/abs/2511.12884), [Mohsenimofidi et al.](https://arxiv.org/abs/2510.21413))
- Values-as-prose inherits the [compliance ceiling](instruction-compliance-ceiling.md) and primacy bias — read by the model, applied unreliably, never verified
- Verbose AGENTS.md actively reduces task success and raises cost ~20% ([Gloaguen et al.](https://arxiv.org/abs/2602.11988v2)); adding values prose has a real cost
- Pair every value with a verification command, or move it to a lower-layer mechanism (permissions, CI, hooks, branch protection)
- Keep AGENTS.md as a pointer: short rule, named command, link to policy

## Sources

- [Chatlatanagulchai et al. — Agent READMEs: An Empirical Study of Context Files for Agentic Coding](https://arxiv.org/abs/2511.12884v2) — 2,303 context files; functional categories dominate, security/performance under 15%
- [Mohsenimofidi et al. — Context Engineering for AI Agents in Open-Source Software](https://arxiv.org/abs/2510.21413v4) — 466 OSS repos; five writing styles; no explicit ethical, accessibility, fairness, or tone instructions found
- [Gloaguen et al. — Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?](https://arxiv.org/abs/2602.11988v2) — verbose context files reduce success and add ~20% cost
- [Jaroslawicz et al. — How Many Instructions Can LLMs Follow at Once?](https://arxiv.org/abs/2507.11538v1) — frontier models top out at 68% at 500 instructions; primacy bias peaks around 150–200 instructions
- [Zhang et al. — Do Agent Rules Shape or Distort? Guardrails Beat Guidance in Coding Agents](https://arxiv.org/abs/2604.11088) — negative constraints help, positive directives hurt; ground for the verification-not-prose recommendation
- [Treude et al. — Operationalizing Ethics for AI Agents: How Developers Encode Values into Repository Context Files](https://arxiv.org/abs/2605.05584) — vision paper; finds developers already embed fairness/accessibility/sustainability/tone/privacy guidance, but defers whether agents adhere to it

## Related

- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md)
- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Critical Instruction Repetition](critical-instruction-repetition.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md)
- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
