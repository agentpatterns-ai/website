---
title: "Policy Wording Tests for Coding-Agent Instruction Files"
term: "Policy Wording Compliance Tests"
description: "Test direct and explanatory policy wording on the agent configurations you run. A marker-comment study finds conditional wording weaker, with limited scope."
tags:
  - instructions
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-06
maturity: emerging
---

# Policy Wording Tests for Coding-Agent Instruction Files

> Policy wording tests compare compliance on the same tasks, so teams can evaluate instruction phrasing without assuming one style works across agents.

Policy wording is an experimental input when testing an agent instruction file. A study appended four versions of one marker-comment rule to repository context files. It held placement and surrounding text fixed ([Tsuchida et al., v1](https://arxiv.org/abs/2611.04367v1)).

## What the experiment establishes

The study selected 86 tasks from 10 repositories and ran three repetitions per style and configuration. Its rule required `# @tracked` directly below every added or modified Python function's `def` line. Compliance required every affected function in a session to carry the marker. Sessions with no affected functions were excluded ([method](https://arxiv.org/abs/2611.04367v1)).

Claude Code 2.1.227 with `claude-opus-5` had 82 retained tasks: direct wording scored 78.0%, explanatory 77.2%, and conditional 64.2%. Direct and explanatory wording each beat conditional wording significantly; they did not differ significantly from each other ([results](https://arxiv.org/abs/2611.04367v1)).

Other configurations changed the ranking. Direct wording led for `claude-sonnet-5`; explanatory wording led for `gpt-oss-120b` on qwen-code. Qwen3-Coder-Next showed no significant style effect. One sentence represented each style, so wording and length remain confounded with style ([results and limitations](https://arxiv.org/abs/2611.04367v1)).

## Apply the result without changing policy scope

Use direct wording as a candidate, then compare it with a version that explains the reason. Keep the triggering condition when it defines a real permission boundary. Removing that condition changes the policy rather than testing its phrasing.

For a local evaluation:

1. Choose a rule with an observable outcome.
2. Keep the rule's meaning, file position, and tasks fixed across variants.
3. Repeat runs on each model and harness you actually use.
4. Report excluded sessions and the unit of compliance alongside the score.

Those steps follow the study's controlled comparison. They do not imply its percentages transfer to security rules, another language, or a newer runtime.

## Separate compliance from correctness

Passing the marker check does not establish that the code solves its task. Score task correctness separately. If a requirement must hold on every accepted change, add a mechanical check where possible; do not treat a better wording score as enforcement.

The useful outcome is a tested instruction for a named configuration, with the remaining failure rate visible.

## Key Takeaways

- Preserve policy meaning when comparing wording.
- Name the harness and model beside any compliance result.
- Keep mechanical acceptance checks separate from prompt experiments.

## Related

- [Configuration File Structure Compliance Gap](configuration-file-structure-compliance-gap.md) — a different set of instruction-file variables
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md) — move checkable requirements into execution controls
- [Specification Portability Across Agents](specification-portability-across-agents.md) — test a shared specification across runtimes
