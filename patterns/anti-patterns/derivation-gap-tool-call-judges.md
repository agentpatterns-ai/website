---
title: "Reading a Tool-Call Judge's Rejection as an Argument Defect"
term: "Derivation Gap"
description: "A judge rejects a correct tool-call argument whose source its input never showed, and ranks a visible wrong value above it."
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - derivation gap
  - out-of-view argument rejection
  - unreferenced tool-call argument
last_reviewed: 2026-10-16
maturity: emerging
---

# Reading a Tool-Call Judge's Rejection as an Argument Defect

> Burying the source of a correct argument drops AUROC from 91.89-99.88 to 39.80-49.03 across four judges, which then prefer the visible wrong value.

A tool-call judge's rejection is a fact about what its input contained. Ma and colleagues scored seven argument judges across three tool-calling benchmarks and found that a correct value is accepted less often when no text in the judge's input says what that value should be. They name the drop the derivation gap, and scaling the judge from 4B to 27B parameters does not remove it ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).

## When the gap bites

- The judge reads a trimmed transcript. The authors truncated on purpose, because harnesses do: "the OpenAI Agents SDK provides a trimmer that cuts tool outputs above 500 characters outside the last two turns" ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)). A value copied from an earlier tool return then matches nothing the judge can see.
- The value is a schema default nobody asked for. No truncation needed: "On FCRB nothing is cut, the default is written in the schema the judge reads, and correct defaults still carry the largest gap of any path" ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).
- A plausible wrong value sits in view. In a relocation test the judges did not hesitate. They switched: "Against the distractor in view alone, AUROC is between 26.71 and 39.88, so all four judges rank the wrong value they can see above the correct value that was cut" ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).

Where a request has no earlier calls, the first condition drops out: "On FCRB it is small, and defaults carry the largest gap" ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)). The default case survives.

## Why it works

The judge matches the candidate against text in its input that names the expected value, instead of deriving that value itself: "A judge scores a value higher when a reference in its input matches it, whether the value is right or wrong", and "It does not reliably rebuild the derivation on its own, even from the full history" ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).

Information in view is not a reference. On the uncut benchmark the default is printed in the schema the judge reads, and on the 142 of 185 correct defaults whose derived reference says the default applies, "a line that restates the schema default and lists which related words appear in the request changes acceptance by at most 6.18 points". Writing out the derivation raised acceptance "to between 73.02 and 88.06" on that same subset, which the reference itself selects ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).

## What to do instead

1. Record the derivation path beside each verdict, so a rejection on a cut tool return reads differently from one on a value the judge could see.
2. Check a schema default in code, with a string comparison. It needs no judge, and it carries the largest gap where nothing is truncated.
3. Derive the reference before the candidate is seen. In DeRef a separate model reads the uncut history and writes the expected value and its source into the judge input: "DeRef raises argument AUROC over Plain in all 12 pairs, by between 1.44 and 22.14 points, and every gain is significant" ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).
4. Do not reach for the full history first. It recovered three of four judges on the relocation test, but on the CFB values matching no span of the history "it raises AUROC for none of the three judges, and it lowers it for Jev by 2.83 points and for Qwen3-8B by 13.83 points" ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).

## When this backfires

A judge that follows a reference follows a wrong one just as willingly, so the fix inherits the defect.

- Swapping one value inside the reference reversed verdicts. On the two benchmarks whose wrong values came from real models, at a 0.5 threshold, "acceptance of correct values drops by between 15.36 and 57.07 points, and acceptance of wrong values rises by between 20.38 and 57.79 points". The deriver reads every tool return uncut, and the authors name the consequence: "a deriver that errs, or a tool return written to mislead it, could make a judge accept a wrong argument" ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).
- One gold value per argument is their data's assumption, not yours. "a reference that names it can lead judges to reject another value that is also correct" ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).
- A judge holding a prior belief about the value behaves the opposite way. Under swapped references in QA grading, "grading reliability drops sharply under swapped references across a broad set of judge models", because of "judges' over-reliance on parametric knowledge, leading judges to disregard the given reference under conflict" ([Lee et al., 2026](https://arxiv.org/abs/2601.07506v2)). Booking IDs and timestamps carry no such prior. Entity names in a financial query might.
- The deriver is a second full-history pass, 2.44 to 7.27 seconds per reference on the authors' hardware, shared by only 1.33 to 1.83 candidates. A pre-execution gate on a latency budget may have no room for it.

The authors do not call it solved: "We therefore see DeRef as support for review, not a replacement for it" ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).

## Example

The deriver prompt is the whole mechanism, and it is one instruction. Ma and colleagues give the deriver the request, every earlier call and return uncut, and the function and parameter lines of the call being judged, then ask:

> Before seeing any proposed value: what should the value of parameter {name} be in this call, and where in the context does it come from? Quote the source text if there is one, or say that the context does not determine it. Answer in at most 3 sentences.

Two properties do the work. The deriver never sees the candidate, so the reference cannot echo the value under test. And it is allowed to answer that the context does not fix the value, which is what keeps a reference from being invented for a value nothing determines ([Ma et al., 2026](https://arxiv.org/abs/2610.18497v1)).

## Key Takeaways

- Ask what the judge could see before asking whether the argument was wrong. The rejection is evidence about the input.
- Schema defaults are the one case you can take away from the judge entirely, and they carry the largest gap where nothing is cut.
- A truncated judge does not become uncertain. It ranks the visible wrong value above the correct one it cannot source.
- Supplying a derived reference moves the single point of failure onto the deriver, which reads every tool return uncut.
- Price the deriver before you plan on it: a second full-history pass, 2.44 to 7.27 seconds per reference, shared by 1.33 to 1.83 candidates.

## Related

- [A Guard Hook Approves the Truncated Input It Was Handed](guard-approves-truncated-input.md) — the mirror case, where a cut input makes a policy gate fail open instead of over-rejecting
- [When Your Agent's Verifier Reads the Same False Premise](verifier-reads-the-same-premise.md) — the other way a verifier's input decides its verdict, through a shared prompt rather than a cut transcript
- [Deciding an Agent Upgrade on a Frozen Judge's Verdict](frozen-judge-release-decisions.md) — what a path-dependent judge error does to a version comparison
- [Inference-Time Tool-Call Reviewer](../agent-design/inference-time-tool-call-reviewer.md) — the pre-execution review slot this gap sits in
- [Silent Adoption of Corrupted Tool Returns](silent-adoption-of-corrupted-tool-returns.md) — the upstream problem that makes an attacker-written tool return worth worrying about
