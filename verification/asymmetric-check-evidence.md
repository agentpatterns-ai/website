---
title: "Reject on a Failing Check, Never Accept on a Passing One"
term: "Asymmetric Check Evidence"
description: "After a fail-on-base check, a generated test still failing on an agent's patch rejected it at 0.82 precision in the test stage of a 121-trace held-out Python run; the same test passing accepted at 0.30, so let a pass decide nothing."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - asymmetric check evidence
  - directional review evidence
  - reject-only review gate
last_reviewed: 2026-10-03
maturity: emerging
---

# Reject on a Failing Check, Never Accept on a Passing One

> On 121 traces, 89 defective, a checked failing test rejected at 0.82 precision. A passing test accepted at 0.30, so let a pass decide nothing.

Wire the two directions of a review gate differently. A check-backed failure can decide a rejection on its own; the same check passing cannot decide an acceptance. Guo and colleagues measured both directions of the generated-test stage inside one deployable review cascade. The set was 121 held-out GPT-5.4 traces, 89 of them defective, from the SWE-bench Lite and Verified subsets. Their result: "A checked test that still fails on the patch has reject precision 0.82, while a passing test has accept precision 0.30. A patch-caused failure can therefore support rejection, but one passing test cannot establish correctness" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)).

Those two figures belong to that stage, not to the cascade as a whole. End to end it scored "Defect catch is 0.76 on the held-out set and 0.80 on the Gemini set", with over-rejection "0.66 and 0.67, respectively" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)).

## Conditions the rule depends on

The asymmetry is a property of partial checks, so three conditions decide whether it applies to yours.

- The check is partial. Under official execution evidence, five of six reviewers improve on both catch and over-rejection, and "GPT-OSS-120B and GPT-4.1 decide all 122 traces correctly". Qwen-2.5-72B is the exception: "its catch rises, but its over-rejection does not improve". That condition is a diagnostic, not an option, because "Our strongest result uses official evidence unavailable in deployment" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)).
- The failing test already cleared a fail-on-base check. The cascade keeps a generated test "only if it first fails on the unpatched repository because the requested behavior is missing" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)), which is the [bug-discriminating evidence](bug-discriminating-validation-evidence.md) rule turned on the reviewer's own probe.
- The error is attributable to the patch. "A static or execution error can support an automatic rejection only when the patch caused it." Skip that filter and "the static analysis rejects two correct development-set patches", while an unrelated execution error "causes the reviewer to reject four of five correct patches" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)).

## What each outcome licenses

| Check outcome | What the gate may decide | Basis |
|---|---|---|
| Empty diff | Reject | Cascade Stage 0 |
| Patch-caused static or execution error | Reject | Cascade Stage 1, subject to the attribution filter |
| Generated test fails after the fail-on-base check | Reject | Reject precision 0.82 |
| Generated test passes | Nothing | Accept precision 0.30 |
| No check applies | Send it to a reviewer and leave `uncertain` available | 19 of the cascade's 21 held-out false rejections arose here |

The check-decided rows cover a minority of traffic: "On the held-out set, Stages 0–2 decide 36/121 traces" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)). The authors decline to recommend their own accept arm: "The Stage 2 pass rule records the frozen evaluation policy; it is not a recommended acceptance rule".

What crosses into the last row is specified too: "Only unresolved cases should reach the reviewer, with the patch, check results, and needed context; uncertain must remain available" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)). A probe result the gate could not act on travels as context, never as a verdict.

## Why it works

One generated test is a partial specification, and its two outcomes do not weigh the same against it. A failure exhibits a concrete behavior the patch does not satisfy, which settles the disputed requirement. A pass covers only what that test checks. The paper names the cause: "A passing test is weaker (accept precision 0.30), because one generated test covers much less behavior than an official suite", which it calls "the deployable form of the oracle problem" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)). Differential testing of SWE-bench patches that already pass their tests finds the same gap from the other side, at "on average, 29.6% of plausible patches can be differentiated from their oracle patches" ([arXiv:2503.15223v2](https://arxiv.org/abs/2503.15223v2)).

Presenting the evidence better is no substitute for checking it. Organized but unverified notes move the two rates together instead of separating them: "On real traces, structured but unchecked evidence raises both defect catch and false rejection", and "Structured evidence does not separate catch from over-rejection for any of the six reviewers" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)). A rising catch rate is the point of a review gate, so the defect is that catch cannot rise on its own. On the design set GPT-4.1 "catches 0.91 of defects while rejecting 0.86 of acceptable patches" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)).

A larger reviewer is not the lever either. On the same unchecked structured evidence, Qwen3-235B's defect catch was 0.28, below Llama-3.1-8B's 0.70, which the authors report as "an observational model comparison, not an estimate of the causal effect of scale" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)).

## When this backfires

- An over-specified probe fails the agent patch and the reference fix alike, so the reject arm blocks correct work. "Gold cross-execution is what detects this class: a probe that fails the reference solution is over-specified regardless of what it does on the agent patch", and "On the design set this class accounts for the probe-driven share of cascade over-rejection" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)). No deployment holds a reference fix, so nothing local detects it.
- Most patches in your repository are fine. A reject precision is relative to the defect share of the set it was measured on, and the 0.82 came from 121 traces of which 89 were defective. The authors bound the generality themselves: "Real-defect results are limited to the Python GPT-5.4 and Gemini sets" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)).
- Held-up correct work is your expensive failure. False rejection is the shortfall the authors close on: "Current generated checks fall short: held-out over-rejection is 0.66, and one passing test cannot establish correctness" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)). Strengthening the reject arm does not touch that.
- The check-decided stages reach few traces. Stages 0 to 2 decide 36 of 121, so the other 85 go to the reviewer, and the authors report the cascade's "measured advantage is coverage, not lower risk or higher accuracy on those traces" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)). Giving the accept arm no decision moves more traces to that reviewer; the paper does not measure how many.
- Your checks are decisive and you route their result back through a model anyway. In each audited over-rejection under grounded evidence, "the rationale says official execution failed, while the cited evidence says it passed", so the authors' instruction is blunt: "Do not make the smallest models read it again" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)).

## Example

Two cases from the benchmark run the rule in both directions.

For django-12308 the generated probe failed on the base repository and passed on the agent patch, so the cascade accepted. Yet the official suite rejected that patch. The authors read it this way: "The probe tests one official failure in admin_utils, but not all of the required behavior: a grounded pass proves less than a grounded fail" ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)). A gate wired to this rule never reaches that accept: a pass sets no decision, and the trace goes to a reviewer with the probe result attached as context.

In the mirror case, django-12497, the probe failed on the agent patch and on the gold reference alike, because "the probe demands behavior beyond what the issue requires". The cascade rejected a patch the official suite passes ([arXiv:2610.01023v1](https://arxiv.org/abs/2610.01023v1)). This rule does not save the patch, because it licenses exactly the rejection that went wrong. That is what the reject arm costs, and it is detectable only with a reference fix you do not have.

## Key Takeaways

- Wire the reject arm to a mechanical decision and give the accept arm none. A passing probe is a reason to keep looking, never a reason to close.
- Apply the patch-attribution filter before the gate fires. In the authors' ablation, skipping it rejected two correct development-set patches on static analysis and four of five correct patches on an unrelated execution error.
- Keep `uncertain` returnable, and count how many cases land there. That stage is where this cascade's false rejections concentrated, so forcing it to choose moves errors rather than removing them.
- Re-measure the precision against your own defect base rate before setting a threshold on it. The published figure comes from a set where most patches were defective.
- Spend the next increment of budget on a sharper check rather than a larger reviewer. The authors put it as prioritizing "reliable checks and safer handling of unresolved cases over larger reviewers alone".

## Related

- [Bug-Discriminating Validation Evidence for Repair Agents (BSG-VA)](bug-discriminating-validation-evidence.md) — the fail-on-base check this rule takes as a precondition, applied inside the agent's own validation step
- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — ordering gates by cost, the other axis a cascade gets designed on
- [Evidence-Bundled Agent PRs: Sizing the Reviewer's Effort](evidence-bundled-agent-prs.md) — what to hand a human reviewer once the automatic stages have abstained
- [Name the Check That Passed Before Accepting AI Code](named-check-over-evaluation-confidence.md) — the same discipline for a human acceptance, recorded per change
- [Feedback as Capability Equalizer](../patterns/agent-design/feedback-capability-equalizer.md) — the generator-side version of evidence outweighing model size
- [Require the Metric the Optimization Should Move](expected-metric-gate-performance-prs.md) — the performance case, where the check is a number rather than a pass or fail
