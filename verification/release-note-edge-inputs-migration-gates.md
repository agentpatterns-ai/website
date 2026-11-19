---
title: "Release-Note Edge Inputs for Migration Repair Gates"
term: "Release-Note Edge Input"
description: "When a runtime migration must keep old outputs, gate a model's repair on one input built from the release note; on typical inputs alone the gate released 0.410 of wrong repairs."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - accepted-but-wrong repairs
  - release-note edge-case input
  - silent migration failure gate
last_reviewed: 2026-11-18
maturity: emerging
---

# Release-Note Edge Inputs for Migration Repair Gates

> When a runtime migration must keep old outputs, gate a model's repair on one release-note edge input whose expected output comes from the old runtime.

A preregistered study of CPython, Node.js and SQLite upgrades measured how many wrong repairs a release gate ships. Over the complete repair space of 52 affected test tasks, an all-assertions gate on typical inputs released 0.410 of wrong repairs. One edge input written from the release note cut that to 0.065, and false rejection stayed at 0.010 ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)). Those figures cover choices among author-written fragments. Version 2 adds model-written programs executed in a container sandbox ([free-form addendum, section 6](https://arxiv.org/html/2611.08269v2#S6)).

## When this applies

The result holds under conditions narrower than "any migration":

- The old output is still the obligation. Every expected value comes from the old procedure on the old runtime, so the gate rejects a repair that adopts the new behavior on purpose.
- The old runtime can still run the old procedure on the new input. The study's input writer lost 13 inputs because "the old runtime raised an error" ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)).
- The headline rates describe a finite fragment menu. The free-form addendum also found lower false acceptance for two local models, with a smaller reduction for GPT-5.6-luna. It used different sampling and no revision round, so its rates are not directly comparable ([Chen et al., section 6](https://arxiv.org/html/2611.08269v2#S6)).

## How to build the gate

1. Read the release-note entry for the change your code touches, and choose one input at the documented boundary.
2. Run the old procedure on the old runtime with that input. Its output is the expected value. No model predicts it.
3. Confirm the unrepaired procedure fails a visible check on the new runtime. The study required this of every author edge input ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)).
4. Gate the repair on every requirement assertion over the typical inputs plus the edge input.

A model can write the edge inputs. One isolated GPT-5.6-luna call per task, seeing only the release note and the visible contract, reached 0.070 with up to three inputs. That curve was descriptive. On a menu enlarged to 1,491 fragments it passed a preregistered test at 0.053, with false rejection rising from 0.014 to 0.043 ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)).

Do not ask the writer which old outputs still bind. A preregistered guard kept only inputs the writer marked legacy-binding and reached 0.157, because "It discarded exactly the inputs that revealed the change" ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)).

## Why it works

A silent change keeps every call succeeding and moves only some results. Typical inputs often miss those results. On typical inputs, the unrepaired procedure failed a visible check in only 34 of 52 test tasks ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)). An input built from the release note targets the changed behavior, and the old runtime supplies its expected value without model judgment. The authors' reading is that "What makes a release gate adequate here is its inputs, not its assertion family" ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)). Keeping the model away from the oracle matters too. LLM test generators whose oracles are designed to pass can end up "validating bugs in the generated test suite and rejecting bug-revealing tests" ([Mathews and Nagappan, 2024](https://arxiv.org/abs/2412.14137v1)).

In the fragment stages, the effect reached model-selected repairs. Wrong releases per attempt fell from 0.233 to 0.057 for Qwen3-8B, 0.181 to 0.020 for gpt-oss-20b and 0.120 to 0.018 for qwen3.6-35b-a3b, with no fall in correct completion ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)). Self-tests written by the repairing model lowered wrong releases in every family, and none of those reductions survived Holm correction ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)).

## When this backfires

- Wrong code built to match legacy output on typical inputs. With 233 hard distractors added, the edge input still let 0.168 of the hard wrong programs through ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)).
- A weak input writer. Both local-model writers failed their preregistered tests, and the qwen3.6 writer raised false rejection to 0.083 against 0.010 ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)).
- A strong repairer gains less. GPT-5.6-luna released 22 wrong repairs of 456 on typical inputs and 7 with the edge input, a contrast that was descriptive only, with Holm p 0.499 ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)).
- Menu-dependent numbers. The authors state the headline shares "hold only for their own menus, and are not properties of a gate" ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)).
- Limited contract review. Three humans reviewed assertion strictness on 40 sampled contracts after the results were known; one reviewer was the first author. They upheld none of the 11 sampled AI strictness objections, but a majority rejected another contract. Other criteria lack human review, class-label disputes remain open, and the predeclared strong-evidence criterion was not met ([Chen et al., sections 5.5 and 9](https://arxiv.org/html/2611.08269v2#S9)).

## Example

Python 3.12 changed `sum()` to use "Neumaier summation to improve accuracy and commutativity when summing floats" ([Python 3.12 What's New](https://docs.python.org/3/whatsnew/3.12.html)). The paper lists this as a silent change: `sum()` "returns a more accurate float that no longer matches stored ledger totals" ([Chen et al., 2026](https://arxiv.org/abs/2611.08269v2)). A typical input does not reveal it:

```bash
$ python3.11 -c "print(sum([1.5, 2.25, 4.0]), sum([0.1]*10))"
7.75 0.9999999999999999
$ python3.12 -c "print(sum([1.5, 2.25, 4.0]), sum([0.1]*10))"
7.75 1.0
```

A gate on `[1.5, 2.25, 4.0]` passes a procedure that still calls `sum()`. The edge input `[0.1]*10`, with expected value `0.9999999999999999` from Python 3.11, blocks it. A repair that restores left-to-right addition, such as `functools.reduce(operator.add, xs, 0)`, prints `0.9999999999999999` on Python 3.12 and passes.

## Key Takeaways

- Write the edge input from the release-note entry, because typical inputs often miss the behavior a silent change moves.
- Take expected values from the old program on the old runtime. Never let a model predict an expected value or decide which old outputs still bind.
- Validate the input writer separately. Only GPT-5.6-luna passed the writer tests; the study tested no flagship-tier writer.
- Expect a remainder. One edge input still passed about one in six wrong programs built to match legacy output on typical inputs.

## Related

- [Bug-Discriminating Validation Evidence for Repair Agents (BSG-VA)](bug-discriminating-validation-evidence.md) — the same discriminator for bug fixes: a test proves nothing unless it fails on the unfixed code.
- [Training-Data Gravity: Agents Default to Deprecated APIs](../patterns/anti-patterns/training-data-gravity.md) — why agents reach for the pre-migration API in the first place.
- [Specification-Grounded Test Writing](specification-grounded-test-generation.md) — giving the test writer the rules, here the release-note entry, instead of the code.
- [Probing Unstated Constraints in Generated Code (Intent Violation Rate)](unstated-constraint-probes.md) — passing code that breaks a constraint no visible test names.
- [Reject on a Failing Check, Never Accept on a Passing One](asymmetric-check-evidence.md) — what a pass on a narrow gate does and does not license.
