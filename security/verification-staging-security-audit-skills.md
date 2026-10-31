---
title: "Verification Staging for Security Audit Skills"
term: "Verification Staging"
description: "A security audit skill's finding is a candidate, not a verdict: 37 public skills over 100 real kernel CVEs got class, function, and statement all right in 11.1% of 14,800 runs."
tags:
  - security
  - testing-verification
  - skills
  - claude
  - arxiv
aliases:
  - "verification stage in security skills"
  - "candidate verification for audit skills"
last_reviewed: 2026-10-23
maturity: emerging
status: current
---

# Verification Staging for Security Audit Skills

> A security audit skill's finding is a candidate: across 14,800 runs only 11.1% got the vulnerability class, function, and statement all right.

Researchers ran 37 public security skills through Claude Code against 100 real Linux kernel CVEs from June 2026, across four models, for 14,800 runs ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)). The task was narrowed before the agent started: "The model is provided with the case's target file paths and asked to inspect them for security vulnerabilities". These rates describe this file-guided C review setup; they do not establish a lower bound for other auditing tasks.

## Where the detection ladder drops

The study scored each criterion separately, then jointly: "Across all skill-guided model-case runs, 24.4% locate the correct functions, 18.3% identify both the correct function and responsible statement, 15.7% identify the correct CWEs, and produce 11.1% fully correct results" ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).

The drop between rungs changes how you use the output. Reaching the function does not mean isolating the operation, and doing both does not mean naming the weakness: "Among the runs with correct function-and-statement localization, 39.4% still fail to identify the correct vulnerability class" ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).

Rates differ across skills and underlying models. Across the 37 skills "the fully correct rate ranges from 3% to 15.75%", and on identical procedures across the four models "Fully correct rates range from 5.54% to 20.19%" ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).

## Why it works

Higher-performing skills use different analysis methods but share a structural rule: nothing becomes a finding without an intervening check. "Although these skills use different procedures, all require the initial hypothesis to undergo an additional semantic or verification step before it becomes a final finding" ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).

The failure taxonomy identifies gaps in evidence analysis and investigation coverage. Unanalyzed evidence is the largest mechanism at 29.3% of failure labels; coverage-control gaps in the procedure follow at 15.8%. The study also observes that "lower-performing skills more often begin with a narrower analytical lens, such as predefined sinks, resource operations, trust boundaries, or targeted search expressions" ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).

Candidate generation and candidate confirmation want to be separate stages. A system built to find bugs rather than measure skills reaches the same split: TitanCA runs a "four-module architecture, i.e., matching, filtering, inspection, and adaptation" and reports that, applied in open-source software, it "has discovered 203 confirmed zero-day vulnerabilities and yielded 118 CVEs" ([arXiv:2604.17860v3](https://arxiv.org/abs/2604.17860v3)).

## What to put in the procedure

The study names four design implications. Cover more than the opening search: "Require analysis of related callers, callbacks, initialization, error, cleanup, and teardown paths rather than relying on a narrow initial search." Make the unsafe relation explicit: agents often reach the right operation without constructing the ownership, lifetime, bounds, or synchronization relation that makes it unsafe. Hold candidates open: "Keep unresolved candidates active until decisive evidence is checked". And write the steps down rather than leaving them to the model: "Specify analysis steps, decision conditions, evidence requirements, and stopping rules to reduce reliance on model-specific implicit reasoning" ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).

## When this backfires

- Non-local bug classes. Out-of-bounds write and read were the two best classes, at 39.53% and 29.19% fully correct. Improper locking was the worst, and the shape of that failure is the useful part: "Although 8.7% of runs reach the correct function, only 1.8% identify the responsible statement" ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).
- A small gain on Haiku-4.5. Refining the five best skills raised its fully correct rate from 3.4% to 4.4%, a gain of 1.0 percentage point ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).
- Expecting the procedure to carry the failure budget. Refinement removed almost every procedural defect the taxonomy could see: "Under the baseline skills, skill-level limitations (S1-S7) account for 8.67% of unsuccessful runs. After refinement, this share falls to only 0.06%." Total failures fell from 1,879 to 1,776. The authors state the boundary plainly: "revising SKILL.md can improve the analysis procedure and remove deficiencies in the guidance provided to the agent, but it cannot directly eliminate limitations in how the underlying model retrieves evidence, constructs relations, interprets code, or carries out the prescribed procedure" ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).
- Diminishing returns from iterating a skill. The first revision carried "84.1% of the overall net increase of 44 runs achieved by the selected skill versions", though "Later rounds still provide meaningful gains for some skills" ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).

The joint criterion cuts the other way too, as the authors note: it "may understate partially useful analyses" ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).

## Key Takeaways

- A skill's report names a candidate. Keep a verification stage between candidate generation and final reporting. Even correctly localized runs had a 39.4% class-error rate.
- Higher-performing skills all verify hypotheses before reporting; lower-performing ones more often start with a narrow lens.
- Budget the model alongside the skill. The same procedures ran 5.54% to 20.19% fully correct across four models.
- Measure gains after each revision. The first revision delivered most of the gain, but later rounds helped some skills ([arXiv:2610.25705v1](https://arxiv.org/abs/2610.25705v1)).
- Scope these figures to Linux-kernel C, ten CWE classes, and a file-guided setting before carrying them to another stack.

## Related

- [Harness Composition for Scaled Security Audits](security-audit-harness-composition.md)
- [Always-On Agentic PR Security Review](always-on-pr-security-review.md)
- [Three-Depth In-Session Security Review](three-depth-in-session-security-review.md)
- [Ranking Skill Sources for Review by Copy Out-Degree](skill-source-audit-ranking.md)
- [Root Causes of Vibe-Coded Application Vulnerabilities](vibe-coded-vulnerability-root-causes.md)
