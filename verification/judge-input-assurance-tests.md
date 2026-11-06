---
title: "Input Assurance Tests for What an LLM Judge Actually Reads"
term: "Input Assurance"
description: "A renderer dropped every tool call and left 53 of 60 judged steps blank while hashes matched. Four tests check that judge inputs meet their contract."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - judge input assurance
  - judge input contract testing
  - input-assurance obligations
last_reviewed: 2026-11-05
maturity: emerging
---

# Input Assurance Tests for What an LLM Judge Actually Reads

> A renderer left 53 of 60 judged steps blank while hashes matched and checkers passed, so test the judge's input directly.

Input assurance is evidence that the text an LLM judge reads meets the evaluation's requirements. Xia and colleagues define it as "what evidence establishes that a judge’s input meets the evaluation’s requirements" and split it into four obligations: required content survives rendering, each checker covers its stated requirements, a failed check stops later use, and the judge reads the bytes last checked ([arXiv:2611.02676v1](https://arxiv.org/abs/2611.02676v1)). The technique applies when software sits between recorded agent runs and the judge, such as a renderer that turns structured trajectories into text packets, checkers, and a staging step that copies packets for the judge.

## What went wrong in one pipeline

The renderer kept message text and dropped the structured `tool_calls` field. An agent step that acted only through a tool call therefore rendered blank, in "26 of 30 error targets and 27 of 30 comparison targets (53 of 60)" ([arXiv:2611.02676v1](https://arxiv.org/abs/2611.02676v1)). Every packet still matched its recorded hash, because "a hash shows only that the bytes are unchanged".

The omission moved a reported result. For one judge configuration, full trajectories raised error flags by 13 more on error steps than on correct steps. With calls restored, that contrast fell to 2, a reduction of 11 with a 95% cluster-bootstrap interval of 0.17 to 0.53 per trajectory ([arXiv:2611.02676v1](https://arxiv.org/abs/2611.02676v1)). The judges never pointed at the gap: "A consensus error flag does not reveal whether the target action was present in the packet, and an abstention does not identify the missing call."

The other three obligations failed in mutation cases and integration tests:

- Both separately written checkers matched calls to results in one direction only. "Both checkers verified that each call had a result, but not that each result had a call."
- One checker hashed the text it had just loaded and compared it with a hash of that same text, so "this comparison cannot detect a changed file."
- In an integration test, a packet from a build that exited with an error still reached the stub standing in for the judge. Staging passed "because the failed build had written the packet and its manifest hash from the same altered text."
- A packet changed after staging was read as changed. Staging also normalized CRLF to LF before hashing, so a line-ending change passed its check.

## The four tests

Each test runs without live judge calls. A recording stub stands in for the judge and hashes whatever it reads ([arXiv:2611.02676v1](https://arxiv.org/abs/2611.02676v1), Section VI).

| Obligation | Test |
|---|---|
| Required content survives rendering | Render a message with empty text and an action held only in a structured field. Check the action's name, arguments, and position against the source, and check that excluded fields such as benchmark labels stay absent. |
| Checkers cover their requirements | Write a passing and a failing case for each requirement, at the pipeline step it covers. "For one-to-one relations, test both directions: a call without a result and a result without a call." |
| A failed check stops later use | Make a required check fail while old packets remain, then run the normal downstream entry point. Nothing from the failed run, and no stale output, may reach the stub. |
| The judge reads the bytes last checked | Change a staged packet after staging, and separately after the last check before dispatch. Require refusal in both cases. |

"Each test includes a valid input that must stay accepted." The paper's three added controls (stop on failure, exact-byte checks before use, reverse call matching) stopped 18 of 19 constructed fault cases before the stub read a packet. The nineteenth was a stale script that never ran ([arXiv:2611.02676v1](https://arxiv.org/abs/2611.02676v1)).

## Why it works

Each integrity signal answers a narrower question than the evaluation asks. A hash proves the bytes did not change after someone hashed them. "A manifest written by a failed build can match its defective output exactly, so a matching hash does not authorise use" ([arXiv:2611.02676v1](https://arxiv.org/abs/2611.02676v1)). A checker covers only the properties, files, and steps it reads, and two checkers written from one plan can share its blind spots. The judge cannot localize the fault either, because "the answer schema had no category for defective input". On the 26 blank error steps in packets ending at the judged step, one configuration abstained in every draw, while the other four flagged 7 to 20 of them as errors (Section V). Each obligation therefore needs its own evidence: comparison with source records, violating cases, integration tests that continue past a failure, and byte checks at the point of use.

## When this backfires

- The contract is wrong for the goal. The pipeline required valid JSON arguments, but the authors note that "malformed calls should be preserved when their behaviour is being judged" ([arXiv:2611.02676v1](https://arxiv.org/abs/2611.02676v1)). A strict check then deletes the behavior under test.
- Rendering more is not the same as rendering what is required. In AgentRewardBench, "including both accessibility trees and screenshots yields a lower performance than including only the screenshot" ([arXiv:2504.08942v2](https://arxiv.org/abs/2504.08942v2)). Test 1 checks the fields the contract names. It does not justify putting every field in the packet.
- The check runs on the wrong participant set. Simulated users made 40 of the cohort's 311 calls, and a matcher that read assistant messages only flagged all 40 of their results as unmatched ([arXiv:2611.02676v1](https://arxiv.org/abs/2611.02676v1)).
- The evidence is thin. The paper studies "one pipeline selected after its rendering omission was found", and its fault cases were "written with knowledge of the code" ([arXiv:2611.02676v1](https://arxiv.org/abs/2611.02676v1)). Transfer to screenshot or accessibility-tree inputs is planned and not yet tested.

## Key Takeaways

- Before comparing judge configurations, diff each rendered packet against its source record for every field the contract requires.
- Report abstentions separately from "no", and count flags on steps labeled correct, as secondary signs of a blank input.
- Give every downstream step a hard dependency on the check before it, and verify hashes where the judge reads, not only at staging.

## Related

- [Reading a Tool-Call Judge's Rejection as an Argument Defect](../patterns/anti-patterns/derivation-gap-tool-call-judges.md) — the judge-side failure when the input omits the source of a correct value
- [State-Integrity Checks for an Eval Oracle](oracle-integrity-checks-eval-harness.md) — the grader-side counterpart, where the oracle changes the state it grades
- [Measure the Judge Before You Freeze a Gate on It](judge-instrument-stability-check.md) — replay byte-identical requests to measure the judge's own noise floor
- [Mutation Testing for LLM Judges](mutation-testing-llm-judges.md) — inject named defects to score the judge rather than its input pipeline
- [Auditing Agent Tool Chains for Silent Partial Success](tool-chain-silent-failure-audit.md) — the same dropped-content failure one layer down, in a tool's response
