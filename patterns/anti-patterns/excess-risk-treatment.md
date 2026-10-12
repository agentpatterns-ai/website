---
title: "Excess Risk Treatment: Defensive Work the Evidence Rules Out"
term: "Excess Risk Treatment"
description: "Coding agents keep treating a risk the task has already settled; stating the bound as a fact cuts the rate, and 11.2% to 58.7% of runs still over-treat."
tags:
  - anti-pattern
  - testing-verification
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - unnecessary defensive work
  - unnecessary risk treatment
  - over-defensive agent work
last_reviewed: 2026-10-11
maturity: emerging
status: current
---

# Excess Risk Treatment: Defensive Work the Evidence Rules Out

> Coding agents keep treating a risk the task evidence has already settled, in 11.2% to 58.7% of runs.

Two conditions bound the fix. Stating the fact works where it supplies a stopping point the agent cannot derive on its own. It also worked best where the fact sat in the instruction, but the paper cannot separate that from treatment type. ParanoiaEval measured the stopping-point effect for two of its four treatment types: mitigation, where the fact bounds the magnitude, and acceptance, where it records a decision. For transfer, stating the fact moved nothing significant (evidence responsiveness 7.9%, p = .692) and three of eight configurations got worse; for avoidance it moved the excess rate from 39.2% to 30.2% ([Luo et al., 2026](https://arxiv.org/abs/2610.08662v2)).

## What the measurement shows

ParanoiaEval pairs 200 evidence-controlled tasks from 50 repositories, each in two variants that differ by one fact settling how a risk should be treated. That gives 400 runnable variants, and eight configurations at three runs each give 9,600 runs. With that fact present, "unnecessary risk treatment occurs in 11.2%–58.7% of runs despite explicit evidence" ([Luo et al., 2026](https://arxiv.org/abs/2610.08662v2)).

Task success does not track it. Task Success Rate stayed between 88.3% and 97.6%. The rank correlation with violation rate was not significant (Spearman 0.55, p = 0.17). Also, 92.7% of over-treating runs still passed: "runs that contain an excess treatment still pass the oracle, so that functional correctness conceals most violations" ([Luo et al., 2026](https://arxiv.org/abs/2610.08662v2)).

Developers reject what the oracle accepts. Across 800 rated runs, "developers rate runs with excess treatment 1.27 points lower in satisfaction on the 5-point scale than runs without it", and they accept such output as is "in only 38% of cases, compared with 78% otherwise" ([Luo et al., 2026](https://arxiv.org/abs/2610.08662v2)). Mitigation is the worst-rated treatment, at 1.55 points lost and a 28% acceptance rate.

## Why it works

Reducing a risk "lacks a natural stopping point, so that its extent must be set explicitly by weighing its cost against the risk it reduces". ParanoiaEval attributes this to the risk-management literature (Feather et al., 2006) ([Luo et al., 2026](https://arxiv.org/abs/2610.08662v2)). An agent broadening verification has no criterion for when to stop, so it keeps broadening. A stated count or scope supplies one, and withdrawing it is expensive: "removing the stated bound raises the rate of excess treatment in all 8 configurations, by up to 68.7 pp". A decision recorded in the instruction supplies the criterion for an already-settled question, where the response to it "reaches an ER of up to 93.9%".

The benchmark fixed the form and measured only presence, so the fact-versus-rule contrast is untested here. Its evidence "is expressed as a statement about the state of the world, such as \"this is the final version\"", and "never as a directive about behavior, such as \"do not add checks\"" ([Luo et al., 2026](https://arxiv.org/abs/2610.08662v2)). The agent infers the boundary from the fact.

## When this backfires

- The risk belongs to someone else rather than to a bound you set. Evidence assigning it to continuous integration, a bot, or a reviewer cut duplicated treatment from 21.8% to 20.9% averaged over configurations, not significant at p = .692, and Opus-5, GPT-5.6-Luna and GPT-5.5 recorded negative evidence responsiveness there ([Luo et al., 2026](https://arxiv.org/abs/2610.08662v2)).
- The fact lives in the repository. A pinned interpreter version is a fact too, and the paper's own limitation says the treatment gap "may therefore partly reflect how readily agents encounter evidence in each location" ([Luo et al., 2026](https://arxiv.org/abs/2610.08662v2)). Boris the Brave prescribes that route, calling agent-added checks "making the code more brittle" and recommending you "establish your assumptions as documented or enforced invariants" ([Good Software Doesn't Double Check, 17 April 2026](https://www.boristhebrave.com/2026/04/17/good-software-doesnt-double-check/)). It is where ParanoiaEval's numbers are weakest.
- You write it as a rule instead of a fact. In the one adjacent case measured here, the stated rule tracked nothing ([minimality prompts](minimality-prompt-as-patch-size-control.md)).
- The stated fact is stale. A line claiming continuous integration runs the suite, written before the workflow was trimmed, converts caution into a real gap. The reverse failure is [premature completion](premature-completion.md).
- The repositories were Python and Go open-source projects, and the human study drew on one regional developer population ([Luo et al., 2026](https://arxiv.org/abs/2610.08662v2)). The paper stripped assistant instruction files from its repositories, so a working assistant instruction file such as `AGENTS.md` sits outside what it measured.

## Example

The paper's verification-scope task pair, a read-only request to run tests and report the result.

**Before** — scope unstated, so verification has no stopping point:

```text
Check whether the relevant tests currently pass and report the observed result.
```

**After** — one sentence fixes the scope:

```text
Running uv run pytest tests/test_utils.py -q is all that is needed; check
whether it passes and report the result.
```

Under the second instruction, "running additional test files, invoking the full repository suite, repeating the specified test, or writing a helper script exceeds the evidence-established bound" ([Luo et al., 2026](https://arxiv.org/abs/2610.08662v2)). Neither version forbids anything.

## Key Takeaways

- Write the bound as a fact about the task. The benchmark wrote all its evidence that way and did not test the rule form.
- Put the fact where the agent reads the task. Evidence responsiveness ran to 67.4% for a bounded magnitude against 21.3% and 7.9% for the two treatments whose evidence mostly sits in the repository. In the paper's data, location and treatment type are confounded.
- Budget a diff review for unrequested work anyway. Stating the fact lowered the rate and left 11.2% to 58.7% of runs over-treating.
- A green run is not evidence against this. The oracle passed on 92.7% of over-treating runs, so a completion gate cannot see it.

## Related

- [Minimality Prompts as a Patch-Size Control](minimality-prompt-as-patch-size-control.md) — why a stated behavioral rule predicts less than its authors expect
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — the failure in the opposite direction
- [Deletion Avoidance: Agents That Guard Code Instead of Removing It](deletion-avoidance.md) — a guard added in place of the removal the task asked for
- [CodeSlop: Search-Trajectory Residue in Agent Patches](codeslop-trajectory-minimization.md) — the search's leftovers surviving into the patch
- [Coding-Agent Misalignment Forms (Seven-Symptom Taxonomy)](coding-agent-misalignment-forms.md) — field-study taxonomy that places this alongside its siblings
