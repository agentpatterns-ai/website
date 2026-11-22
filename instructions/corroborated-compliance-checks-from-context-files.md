---
title: "Corroborated Compliance Checks for Agent Context Files"
term: "Corroborated Compliance Check"
description: "Generate one executable check per context-file rule, accept it only when independently generated checks agree on fixtures, and skip commits it cannot inspect."
tags:
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - dual-agreement compliance scripts
  - per-instruction compliance checks
  - generated compliance checks for AGENTS.md
last_reviewed: 2026-11-22
maturity: emerging
---

# Corroborated Compliance Checks for Agent Context Files

> A generated check for a context-file rule is accepted when independent checks agree with it on fixtures, and runs only on commits it can inspect.

A corroborated compliance check is an executable script, generated from one context-file rule, that a pipeline accepts only after independently generated scripts agree with it on independently generated test fixtures. Voria et al. built it for AGENTS.md-style rules and accepted a script for 4,123 of 6,552 explicit, actionable, observable instructions (62.9%) ([Voria et al., 2026, §4.2.1](https://arxiv.org/abs/2611.13709v1)).

## How a script earns acceptance

The pipeline writes one script per rule, because rules on one topic often prescribe mutually exclusive requirements (§3.4.1). For each rule, Qwen2.5-Coder-14B-Instruct at temperature 0.8 generates ten candidate scripts and ten fixture pairs. A fixture pair is a compliant and a non-compliant synthetic commit. Every script runs against every fixture (§3.4.2).

A script is accepted only when it clears two bars (§3.4.3):

- Correctness: it passes at least two fixtures.
- Corroboration: its passed fixtures overlap at least 60% with those of the best-performing script.

Neither bar works alone. The first accepts a script that satisfies one fixture by chance. The second accepts two scripts wrong in the same way (§3.4.3).

The CodeT method this adapts groups scripts with identical verdicts. In the authors' pilot, exact-match convergence essentially never happened, so they fixed both thresholds on it, without separate calibration (§3.4.3). Of 2,429 excluded rules, 997 had a script that cleared the correctness bar and no peer that agreed with it (§4.2.2).

## The applicability filter

Generated scripts tend to be permissive by default. They look for a violation and report compliance when they find none (§3.5.1). 2,569 of the 4,123 accepted scripts (62.3%) return True on a commit that touches no relevant files (§4.2.2).

The filter comes from the check's own fixtures. Collect the file extensions (or basenames) in the winning fixtures, and call a commit applicable if it touches a matching file. A rule that concerns only the commit message or branch applies to every commit. A commit that fails the filter adds no observation, compliant or otherwise (§3.5.1).

## Failure modes that survive acceptance

A manual spot-check of 94 accepted scripts, judged by one author, found 67 (71.3%) correct (§3.4.3, §4.2.2). The authors call passing both bars "evidence of, not a guarantee of, a correct operationalization" (§4.2.2).

The most common error hardcodes an example from the context file, such as a filename or type name, as a literal requirement. A hardcoded example typically makes the check stricter than its rule, which would bias compliance down. Vacuous passes bias it up. The authors cannot quantify the net effect (§6).

## A different design: ContextCov

[ContextCov (Sharma, 2026)](https://arxiv.org/abs/2603.00822v2) compiles AGENTS.md constraints into Tree-sitter AST queries, PATH shims that intercept prohibited shell commands, and architecture validators over a dependency graph. A generated check must pass syntax checks and a dry run, and developers can edit stored checks before deployment (§3.3).

On SWE-bench Lite with GPT-5.2, ContextCov reached 88.3% constraint compliance, against 67.0% for a vanilla agent and 50.3% for LLM reflection. ContextCov intercepted violations inside the agent loop, while the baselines were scored with the executable oracle after the run. The author generated the AGENTS.md files from each repository's documentation, lint configuration, and CI files (§4.1, §4.3). That figure compares agent configurations, not check correctness. For check quality, the paper reports 82.81% extraction precision on 384 sampled violations (§4.2).

## What to do

1. Generate one check per rule, with several candidate scripts and fixture pairs. Accept on a correctness floor plus agreement, and keep the fixtures with the check.
2. Derive applicability from those fixtures. Report "not applicable" as its own outcome, never as a pass.
3. Review accepted checks, starting with literals copied from the rule's own examples. Review alone is weak: developers judged 73.9% of correct generated postconditions right and 49.0% of incorrect ones ([Kaufman et al., 2026](https://arxiv.org/abs/2607.08885v1)); see [Generated Assertion Signoff](../patterns/anti-patterns/generated-assertion-signoff.md).
4. Send rules that leave no trace in a commit to a hook or process gate. Voria et al. give "run the linter before committing" as a rule with no checkable trace (§5.1).

## When this backfires

- Both thresholds were fixed on one pilot (§3.4.3), and the study used one open-weight 14B model. Other models may give different results (§6).
- A rule with several valid implementations gets one accepted reading (§6).
- Matching by extension counts any file of the right type, and the filter is only as complete as its fixtures (§6).
- 2,070 of the 4,123 accepted checks (50.2%) never met an applicable commit (§4.3.1).

## Key Takeaways

- Accept a check on two bars: a correctness floor stops chance passes, and agreement with a peer stops a lone wrong script.
- Derive applicability from the check's fixtures. 62.3% of accepted scripts return True on commits they cannot inspect.
- An accepted check was correct in 67 of 94 sampled cases.

## Related

- [Per-Instruction Compliance in Agent Context Files Is Bimodal](per-instruction-compliance-is-bimodal.md)
- [Generated Assertion Signoff](../patterns/anti-patterns/generated-assertion-signoff.md)
- [Dual-Executable Specifications](../verification/dual-executable-specifications.md)
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md)
- [Enforce the Rules Your Code Cannot Show](per-rule-enforcement-budget.md)
