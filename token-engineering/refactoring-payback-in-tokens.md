---
title: "Measuring Refactoring Payback in Tokens"
description: "Replay one frozen change prompt in a fresh sub-agent after every refactoring step and record the input tokens — agents carry nothing between runs, so the comparison stays clean."
tags:
  - token-engineering
  - cost-performance
  - tool-agnostic
last_reviewed: 2026-08-13
maturity: emerging
---

# Measuring Refactoring Payback in Tokens

> Agents never learn between runs, so replaying one change prompt after each refactoring step measures refactoring payback in tokens directly.

Replay one representative change prompt in a fresh sub-agent after every refactoring step and record the input tokens it consumes. The falling number is the refactoring's payback. The design works because an agent carries nothing between runs, so every replay meets the same information. The same protocol on a human engineer would be contaminated by learning ([Giles Edwards-Alexander on the economic benefit of refactoring](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)).

Run it under three conditions: the module has one file far larger than its siblings, you expect to keep changing that module, and you can throw away every replayed change. Outside those, the instrumentation costs more than it tells you.

## The replay loop

Edwards-Alexander, CTO for Europe, Middle East and India at Thoughtworks, ran this loop over a 17,155-line Rust data access layer inside a roughly 150,000-line application written entirely by agents ([experiment writeup](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)):

1. Write a refactoring plan for the target module.
2. Craft one representative change and freeze it as a single prompt.
3. Run that prompt in a sub-agent, record its token cost, then throw the change away.
4. Apply one refactoring step.
5. Re-run the identical prompt in a fresh sub-agent, record the cost, throw the change away.
6. Repeat from step 4, recording tokens, time to execute, and lines of code after every step.

## What one run measured

Input tokens for the same change fell from 159,564 at baseline to 27,360 after the fifteenth step, a saving of 83% ([results table](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)). The largest single file fell with it, 17,155 lines down to 3,695. Total lines in the module barely moved, 17,155 to 16,608, and total Rust lines across the application held near constant, 50,359 to 49,812.

Three qualifications travel with those numbers.

- Gains are not monotonic. Steps 5 and 6 pushed input tokens to 171,251, above baseline, with time per change at 1,353 seconds.
- Output tokens barely moved, 1,705 to 2,113: "the refactoring did not make the representative change smaller", and output carries the higher price.
- The counts are approximations. The author reports that Claude "doesn't provide reliable methods for counting tokens live", so the sub-agent counted characters sent and received and divided by four ([method notes](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)).

## Why it works

Edwards-Alexander is explicit that read volume, not code volume, is the mechanism: "This saving is because the agent has to read less code. But it is not because there is less code to read... the agent must be able to successfully identify the smallest subset of files necessary to read" ([mechanism discussion](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)). Refactoring pays when it leaves seams the agent can select against.

Arbitrary splitting does not produce those seams. The same writeup warns that "randomly cutting the file into smaller files is unlikely to help as much: even if each file were smaller, the agent would be forced to read through many files looking for the relevant code". The splits that paid off arrived after extract-function and extract-class passes had surfaced a repeating core to split along.

Controlled work finds the same navigation mechanism at a smaller effect size. Across 660 Claude Code trials on six matched repository pairs, Trivedi and Schmitt found cleaner code cut file revisitations 34% and token use 7 to 8%, with pass rate unchanged ([arxiv:2605.20049v1](https://arxiv.org/abs/2605.20049v1)).

## When this backfires

- The arithmetic is thin. The published saving is 39.7 cents per change at Sonnet 5 input pricing, and the author could not count what the refactoring itself consumed, bounding it at five million tokens and about eight hours of mostly unattended running ([further work](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)). Break-even needs many more changes to that module.
- The largest file is already modest. The published effect needed a 17,155-line starting point ([step table](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)); a module whose biggest file is 800 lines has no comparable drop available.
- The change class is output-heavy. Output tokens did not move across the fifteen steps, so work dominated by writing code rather than reading it shows little of this effect.
- Nothing holds the gain. Cursor adoption across open-source projects produced "a substantial and persistent increase in static analysis warnings and code complexity" ([He et al., MSR '26](https://arxiv.org/abs/2511.04427v3)), so the largest file regrows without a standing complexity gate.
- The result is one run. Each step was measured once, and the author reports that generation noise "is hiding any variance caused by changes in the factoring of the code" ([limitations](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)). Report your own figures as a range ([Seed-Variance Reporting](../verification/seed-variance-reporting.md)).

## Example

The instrumentation lives inside the change prompt. Edwards-Alexander's representative-change prompt ended by requiring the sub-agent to emit exactly this block, filled in with real values, and to stop without committing ([appendix](https://martinfowler.com/articles/exploring-gen-ai/refactoring-economic-benefit.html)):

```json
{
  "files_read": [
    {"path": "src/firestore.rs", "chars": 123456}
  ],
  "response_chars": 7890
}
```

Characters divided by four gave the token approximation. The `files_read` list is the more useful half of that payload: it names the files the agent chose to open, which is the quantity a refactoring is supposed to move.

## Key Takeaways

- Freeze the representative change prompt before the baseline run. A prompt edited mid-experiment invalidates every earlier row.
- Plot largest-file lines against input tokens per change. Total lines barely moved across the published run, so it is the wrong column to watch.
- Sequence the plan so file splits land last, after the extract passes have exposed a repeating core to split along.
- Keep the rows that go the wrong way. Steps 5 and 6 cost more than the baseline, and averaging them away hides which refactorings paid.
- Count what the refactoring itself consumed. The published experiment did not, which is why its return on investment is still open.

## Related

- [Code Cleanliness as an Agent Cost Lever](code-cleanliness-agent-cost-lever.md) — the controlled minimal-pair result this method extends, and the page that names the missing return-on-investment study
- [Token-Cost Profiling and Reduction for Always-On Agentic Workflows](token-cost-profiling-always-on-workflows.md) — the instrument-attribute-fix-verify loop this replay protocol slots into
- [Semantic Density Optimization for Agent Codebases](../context-engineering/semantic-density-optimization.md) — the codebase-side changes that raise task-relevant tokens per byte
- [Seed-Variance Reporting and Measurable-Range Eval Design](../verification/seed-variance-reporting.md) — reporting a single-run agent result honestly as a range
- [Discovery-Only Refactor Pass](../workflows/discovery-only-refactor-pass.md) — the read-only scan that produces the ranked candidate list this experiment starts from
