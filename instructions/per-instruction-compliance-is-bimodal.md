---
title: "Per-Instruction Compliance in Agent Context Files Is Bimodal"
term: "Bimodal Instruction Compliance"
description: "Of 2,053 checked context-file rules, 54.4% were always followed and 37.3% never. Three agents, generated checkers, no counterfactual. Verify each rule, not a sample."
tags:
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - bimodal rule compliance
  - all-or-nothing instruction compliance
last_reviewed: 2026-11-19
maturity: emerging
---

# Per-Instruction Compliance in Agent Context Files Is Bimodal

> Most rules in agent context files were followed in every checked commit or in none, so sampling a few rules misses the ignored ones.

Compliance with a context-file rule is usually all or nothing. Voria et al. checked 2,053 instructions from files such as AGENTS.md against agent commits. 54.4% were followed in every applicable commit, 37.3% in none, and 8.3% fell in between ([Voria et al., 2026, §4.3.2](https://arxiv.org/abs/2611.13709v1)). The 59.8% mean hides that split, because the median is 100%.

Limits:

- The 2,053 instructions are 13.8% of 14,902 extracted candidates (§5.1).
- The median instruction met 3 applicable commits, and 540 (26.3%) met exactly one (§4.3.2).
- Generated scripts judged each commit, and 67 of 94 sampled scripts (71.3%) were correct (§4.2.2).
- No run lacked the instruction, so a followed rule may be a model default (§6).
- Only Copilot, Claude Code, and Codex commits in public GitHub repositories are covered (§3.2).

## How the study measured compliance

The authors mined 621 context-file snapshots linked to 6,541 agent commits in 268 repositories (§1). Of 14,902 candidate instructions, 6,552 were explicit, actionable, and observable (§4.1.1). 4,123 (62.9%) of those got an accepted measurement script (§4.2.1), and 2,053 (49.8%) met at least one applicable commit, giving 18,594 instruction-commit observations (§4.3.1).

Qwen2.5-Coder-14B-Instruct wrote the scripts (§3.4). 2,569 of the 4,123 accepted scripts (62.3%) return True on a commit that touches no relevant files (§4.2.2). The authors call their figures "an optimistic estimate" and the non-compliance rate a floor (§4.2.2).

## What held up under the paper's own checks

- The split. At 3 or more applicable commits (n=1,144) the share of instructions at 0% or 100% was 87.3%. At 5 or more (n=819) it was 86.2%, against 91.7% in the full sample (§4.3.3).
- Testing against implementation. Implementation Details rules had a mean of 63.6% and a median of 100% (n=1,022). Testing rules had a mean of 49.2% and a median of 37.5% (n=270; Table 8). It is the one category gap significant at every threshold (§4.3.3).
- Process rules drop out of the measurement. "run the linter" is the paper's own example of an unobservable rule (§4.1.1). Build and Run falls from 8.8% to 2.9% of the dataset at that step (Table 3).
- Development Process (mean 34.0%, n=50) is not established. Its three significant full-sample comparisons do not survive Bonferroni correction at 3 or more or 5 or more applicable commits (§4.3.3).
- Agents differ. Copilot's mean was 66.0%, Claude Code's 52.2%, and Codex's 51.2% (Table 9). Copilot against Claude Code holds at every threshold and Copilot against Codex does not (§4.3.3). Neither controls for each agent's category mix (§5.2).

## Why spot-checks fail

A reviewer who samples a few rules and finds them followed learns little about the 37.3% never followed. The authors say "Checking a handful of rules therefore gives little assurance about the rest" (§5.2).

The paper tests no cause for why a rule lands in either group and leaves causes to future work (§7). The claim rests on the shape of the distribution, and says nothing about rule count, position, or wording. In a controlled benchmark, unaided refuse and handoff rules reached 0% for all four agent-model pairs ([Yang, He and Zhou, 2026](https://arxiv.org/abs/2607.26819v1)); [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md) covers it. Voria et al. do not code rule type.

## What to do

1. Treat each rule as its own tested unit. For each rule that leaves a trace, keep a check that returns a verdict per agent commit.
2. Gate each check on applicability. A commit that touches no relevant file yields no verdict, not a pass.
3. Track the pass rate per rule and per agent. Move rules sitting at 0% into a hook or CI gate ([Hooks vs Prompts](hooks-vs-prompts.md)).
4. Re-run the baseline when you change agent or model.
5. Review LLM-generated checks first. 3 in 10 were wrong here, and reviewers catch wrong generated assertions poorly ([Generated Assertion Signoff](../patterns/anti-patterns/generated-assertion-signoff.md)).
6. Test whether the file causes the behavior with the [Behavioral No-Op Test](behavioral-no-op-test.md).

## When this backfires

- Rules that leave no trace in a commit cannot be checked this way. [Per-Rule Enforcement Budget](per-rule-enforcement-budget.md) covers them.
- 2,070 of the 4,123 operationalized instructions (50.2%) never met an applicable commit (§4.3.1). Where the relevant files rarely change, a check yields no signal.
- Unreviewed generated checks can show green for rules nobody checks (§4.2.2).
- A check on a rule the model follows anyway adds CI cost and says nothing about the context file.

## Key Takeaways

- Report compliance per rule and per agent. The file-wide mean of 59.8% sits between the two groups and describes few individual rules.
- Rules at 0% are candidates for a hook or CI gate.
- The result is observational, from three agents and 13.8% of candidate rules. Run your own counterfactual before crediting the file.

## Related

- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md)
- [Per-Rule Enforcement Budget](per-rule-enforcement-budget.md)
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md)
- [Configuration File Structure Does Not Drive Compliance](configuration-file-structure-compliance-gap.md)
- [Behavioral No-Op Test](behavioral-no-op-test.md)
- [Generated Assertion Signoff](../patterns/anti-patterns/generated-assertion-signoff.md)
- [Dual-Executable Specifications](../verification/dual-executable-specifications.md)
