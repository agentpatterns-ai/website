---
title: "Verified Norm Packages for Repository Contribution Rules"
term: "Verified Norm Package"
description: "Extract repository contribution rules once, verify each against repository evidence, and index them at the paths they govern; grade them on compliance."
aliases:
  - norm package
  - repository norm acquisition
  - verified repository norms
tags:
  - instructions
  - context-engineering
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-07
maturity: emerging
---

# Verified Norm Packages for Repository Contribution Rules

> A patch that passes 171 functional checks can still skip the changelog entry the repository requires.

A verified norm package is a set of repository rules extracted before any task starts, checked against repository evidence and filed under the paths it governs. One record carries four fields: the rule, the artifacts it governs as paths or globs, the condition that activates it, and any exception ([He et al., 2026, §3.1](https://arxiv.org/abs/2610.07757v1)). The package also records where the evidence was found, separately from the scope, because "a test may provide evidence about a production API without restricting the norm to test files".

## Reach for it under these conditions

Three conditions decide whether this is worth building.

- Your measure is contribution compliance, not pass rate. Across DeepSeek, Qwen, and Gemini on RepoNormBench, norm packages raised Contribution Norm Compliance Rate by 31.64–45.44% relative to a baseline with no generated guidance ([He et al., §4.2](https://arxiv.org/abs/2610.07757v1)). Observed functional success was 5.79–9.09 percentage points higher against the same baseline, and "None of the six functional-success comparisons reaches the 0.05 threshold" ([He et al., §4.3](https://arxiv.org/abs/2610.07757v1)). On resolve rate alone this evidence returns a null.
- Your rules are obligations to deliver rather than behavior to preserve. Contribution compliance covers six norm categories: authored tests, documentation, changelogs, inline changes, style, and typing. The behavioral half barely moved, since "The paired 95% intervals for Behavioral NCR include zero in all six comparisons" ([He et al., §4.2](https://arxiv.org/abs/2610.07757v1)).
- The repository changes slowly enough to keep the package true. "Repository changes can make packages stale", and incremental updating "is not yet sufficiently optimized for repository evolution" ([He et al., §5](https://arxiv.org/abs/2610.07757v1)).

## What verification actually checks

Grounding the quote is the easy half. The verification step also checks the stated scope: "A candidate requiring pytest for all existing tests would exceed that statement even if its quote were correctly grounded" ([He et al., §3.2](https://arxiv.org/abs/2610.07757v1)). It separates requirements from descriptive facts, so "a single workflow occurrence does not establish a repository-wide obligation".

Rejection needs counterevidence in the current code: "Historical evidence cannot independently establish acceptance or rejection" ([He et al., §3.4](https://arxiv.org/abs/2610.07757v1)). Version-control history can qualify a rule; it cannot carry one.

## Why it works

Agents miss many of these rules because the task does not name them. Jinja's changelog requirement "was not stated in the task description", and the patch for that task passed all 171 functional checks without updating CHANGES.rst ([He et al., §2.1](https://arxiv.org/abs/2610.07757v1)). The Tiktoken patch "passed all 18 functional checks for the task but failed the surrogate-recovery norm check" ([He et al., §2.2](https://arxiv.org/abs/2610.07757v1)).

Generated repository documentation does not close that gap. CodeWiki documentation moved Overall NCR by +0.12%, -2.72%, and +1.31% relative to the unguided baseline across the three models ([He et al., §4.2](https://arxiv.org/abs/2610.07757v1)). The authors read it as documentation that leaves "the agent to identify which statements impose obligations on its changes", while a norm record arrives with "explicit scope, conditions, and supporting evidence" ([He et al., §4.2](https://arxiv.org/abs/2610.07757v1)). An independent study splits the same way: "instructions in the context files are well followed by coding agents, repository overviews, although popular and recommended by model providers, are not helpful" ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v3)). A scoped, conditioned record is an instruction. A wiki page is an overview.

RepoNorm indexes a rule by its scope, so `tests/**` is filed under `tests/`. The agent reads the package entry document, then follows the path page for the file it is changing ([He et al., §3.5](https://arxiv.org/abs/2610.07757v1)).

## Example

A sketch of one record, built from the Jinja facts above. The scope glob, condition, and exception text are our illustration. Jinja's `CONTRIBUTING.rst` is the evidence the paper cites.

```yaml
rule: Code changes include an entry in CHANGES.rst
governs: [src/jinja2/**, CHANGES.rst]   # illustrative glob
condition: the change alters behavior users can observe
exception: none stated
evidence: CONTRIBUTING.rst        # kept apart from the scope
```

The agent starts at the package entry document. It then opens the path page for `src/jinja2/filters.py`, finds this record, and adds the changelog entry its patch skipped.

## When this backfires

- Coverage is thin at the precision you want. The default view hit 86.00% sampled precision and covered 21.88% of the authors' 160-norm reference set in full (39.38% in full or part). Admitting more candidates reached 52.50% full coverage (78.13% in full or part) at 75.17% sampled precision ([He et al., §4.4](https://arxiv.org/abs/2610.07757v1)). An entry counted as correct only when every field was accurate.
- A large package creates a selection problem. Benefits "depend on agents selecting and applying relevant norms, which they may overlook among many entries" ([He et al., §5](https://arxiv.org/abs/2610.07757v1)). The wider view held 6,277 readable entries across 14 packages ([He et al., §4.4](https://arxiv.org/abs/2610.07757v1)).
- The coding run gets more expensive. Acquisition averaged 9.18 minutes per package. Across the three models, the norm-package runs used 33.65% more recorded coding tokens than the unguided baseline, on token records the authors describe as incomplete ([He et al., §4.5](https://arxiv.org/abs/2610.07757v1)).
- The tested envelope is narrow: six relatively small repositories, three coding models, one agent harness, and "Source analysis currently supports Python" ([He et al., §5](https://arxiv.org/abs/2610.07757v1)).
- A hand-written list may beat it. If you can state your real obligations in a short file, write them yourself. Providing context files "does not generally improve task success rates, while increasing inference cost by over 20% on average" ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v3)).

## Key Takeaways

- Functional tests and contribution obligations are separate outcomes. Joint success means the patch passed the tests and every applicable norm check on a task that had one. It reached 8.26% of 121 tasks at best, with DeepSeek ([He et al., §4.3](https://arxiv.org/abs/2610.07757v1))
- Report compliance per norm category, not as one figure. Here the aggregate hid a contribution gain that sat beside a behavioral null
- Pick your point on the precision-coverage curve on purpose, because the default setting here buys accuracy by shipping fewer rules
- Give the package a refresh trigger before you build it. Staleness is the failure mode the evaluation does not measure
- Build one only if your repository is stable, your rules are delivery obligations, and you will measure compliance rather than resolve rate

## Related

- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — the task-success question this page deliberately does not re-argue
- [Probe-and-Refine Tuning of Repository Guidance for Coding Agents](probe-and-refine-guidance-tuning.md) — the other published method for producing a guidance artifact, tuned against probes rather than verified against evidence
- [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md) — the hand-written alternative, placed by directory rather than by verified scope
- [Transcript-Gradable Agent Rules](transcript-gradable-agent-rules.md) — how to write a rule whose compliance you can check afterwards
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — why a package that grows without bound stops helping
