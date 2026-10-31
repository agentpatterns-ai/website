---
title: "Identifier-Only Context Poisoning in Code Completion"
term: "Identifier-Only Context Poisoning"
description: "NameTrap studies how renamed identifiers in incomplete Python files steer coding agents toward scanner-detected weaknesses in their completions."
tags:
  - security
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-28
maturity: emerging
---

# Identifier-Only Context Poisoning in Code Completion

> Identifier-only context poisoning uses names in incomplete code to steer an agent's completion toward a targeted weakness.

NameTrap tests this threat in Python files whose scanner-flagged lines have been removed. The retained input contains renamed identifiers, without explicit instructions or vulnerable statements. The measured weakness appears in the agent's later completion ([Chang et al., 2026](https://arxiv.org/abs/2610.34253v1)).

## The boundary between names and requirements

An agent completing an incomplete file uses surrounding names as evidence of intended behavior. NameTrap changes that evidence while leaving the missing implementation for the victim to write. Researchers screen unmodified baselines before the attack; retained files yield no target-CWE finding in 10 baseline completions. The attacker then retains the first identifier-only candidate whose single local probe completion triggers the target CWE ([sections 3.2 and 3.3](https://arxiv.org/html/2610.34253v1#S3.SS3)).

Our interpretation is that this selection procedure limits generalization to arbitrary repositories. The rates describe selected inputs, with up to 10 renaming passes per file ([sections 3.2 and 3.3](https://arxiv.org/html/2610.34253v1#S3.SS2)).

The defensive implication is to distinguish an identifier's suggestion from an authorized requirement. [Authority confusion](authority-confusion-untrusted-context.md) concerns which source can authorize an action. Here, the narrower question is whether source-code names justify the behavior an agent adds. NameTrap proposes treating identifiers as untrusted context; it does not validate a complete enforcement mechanism ([section 5](https://arxiv.org/abs/2610.34253v1)).

## What the experiment measures

The study covers 6 agents and 10 language models. Its candidate pool contains 200 Python files from 31 projects before per-configuration baseline screening. Its four target classes are CWE-78, CWE-79, CWE-327, and CWE-502. These results concern incomplete-file completion under the study's selection procedure ([NameTrap, sections 3.2 and 4.1](https://arxiv.org/abs/2610.34253v1)).

Table 2 reports overall gross attack success rates (ASR) of 22.5% (OpenHands) to 56.0% (Aider). These six-agent results use Qwen-3.5-27B-AWQ-4bit; the corresponding parseable range is 23.4% to 56.0%. Table 3 separately compares 10 models across OpenCode, Claude Code, and Codex ([Tables 2 and 3](https://arxiv.org/html/2610.34253v1#S3.T2)).

Unless stated otherwise, bait construction and victim evaluation use the same agent-model configuration, including Tables 2 and 3 ([section 4.1](https://arxiv.org/html/2610.34253v1#S4.SS1)). RQ5 separately reports cross-model transfer for CWE-78; those results concern that target and the tested model pairs ([section 4.6, Table 5](https://arxiv.org/html/2610.34253v1#S4.SS6)).

Gross ASR includes all evaluated trials in its denominator; parseable ASR includes only outputs the scanners can analyze. Excluding malformed outputs changes the denominator. Neither measure establishes successful exploitation: success uses a target-CWE finding from Bandit or Semgrep at medium severity or higher ([NameTrap, section 4.1](https://arxiv.org/abs/2610.34253v1)).

## Clean inputs and uncertain defenses

The input scan and completion scan answer different questions. NameTrap's bait has no target vulnerable statements for a scanner to report. A later finding concerns newly generated code. This result does not show a scanner missing an existing vulnerability in the bait ([NameTrap, RQ7](https://arxiv.org/abs/2610.34253v1)).

Scanner-based success also inherits false-negative limits. A completion with no finding is not proof of safe behavior. [Treating a clean static scan as security evidence](../patterns/anti-patterns/static-clean-as-security-evidence.md) explains the separate gap between rule matches and runtime confirmation.

NameTrap's generic security reminder does not consistently prevent vulnerability introduction. The authors propose treating names as untrusted and scanning generated changes before commit. Those proposals are not validated mitigations in this study. A scan adds a check on the completion, with the coverage limits above ([NameTrap, RQ6 and section 5](https://arxiv.org/abs/2610.34253v1)).

## Example

In RQ6, Claude Code with Claude Haiku 4.5 records 100.0% gross ASR on CWE-502 with and without the security reminder. This is a reported unsafe-deserialization result in generated completions, under the study's scanner-based criterion ([section 4.7, Table 6](https://arxiv.org/html/2610.34253v1#S4.SS7)).

For Claude Code bait, Appendix B reports that none of the seven analyzers detects the targeted CWE across 108 bait/control pairs; the appendix does not break out this Haiku 4.5 CWE-502 case ([Appendix B](https://arxiv.org/html/2610.34253v1)). Record the reminder as a prompt change and inspect the completed output separately from the identifier-only input.

## Key Takeaways

- Scope the evidence to selected incomplete Python files and the tested agent-model configurations.
- Review the generated completion separately from the input; preserve scanner and denominator limits when reporting results.
- Treat identifier distrust and generated-change scanning as proposed defenses that still need validation.

## Related

- [Treating a Clean Static Scan as Security Evidence](../patterns/anti-patterns/static-clean-as-security-evidence.md) — scanner false negatives and runtime confirmation.
- [Authority Confusion](authority-confusion-untrusted-context.md) — the boundary between context and authorization.
- [Improper Output Handling](improper-output-handling-downstream-sinks.md) — checks where generated output reaches an execution or interpretation boundary.
- [Context Poisoning](../patterns/anti-patterns/context-poisoning.md) — a distinct anti-pattern in which hallucinations become premises; this page concerns adversarial identifier changes.
