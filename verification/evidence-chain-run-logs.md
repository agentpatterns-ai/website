---
title: "Evidence-Chain Run Logs: Bracket the Reported Symptom"
term: "Evidence-Chain Run Log"
description: "Pair every agent tool call with its actual result and bracket the change with one machine-readable measurement of the reported symptom, taken before and after."
aliases:
  - "evidence chain run log"
  - "symptom bracketing"
  - "before/after measurement bracket"
tags:
  - testing-verification
  - observability
  - workflows
  - tool-agnostic
last_reviewed: 2026-08-02
maturity: emerging
---

# Evidence-Chain Run Logs: Bracket the Reported Symptom

> Pair each agent tool call with its actual result, and bracket the change with the same machine-readable measurement before and after.

An evidence-chain run log is a per-run record that pairs every tool request the agent made with the result that came back — files read, patch applied, build output. It wraps the run in one machine-readable measurement of the reported symptom, captured identically before the patch and after it. That replaces the agent's claim that it fixed something with two observations of the same number across a known change. In the source article's worked example, a button overflowing its card measured `overflowRightPx: 29` before the patch and `overflowRightPx: 0` after ([Towards Data Science, 2026](https://towardsdatascience.com/how-to-debug-ai-coding-agents-when-they-change-the-wrong-thing/)).

The scope is one run, not a corpus. [Trajectory decomposition](trajectory-decomposition-diagnosis.md) scores search, read, and edit stages across an eval set to find where a class of runs fails; the evidence chain proves that this run resolved this complaint. A [verification ledger](verification-ledger.md) records whether the checks ran — the bracket records whether the reported symptom moved.

## When this earns its cost

The discipline pays off under four conditions. Skip it when any one fails, because the evidence stops discriminating.

- The reported symptom has a machine-readable measurement — a DOM geometry query, an HTTP status, a parsed log line, an exit code. If you can only judge the symptom by looking at it, the bracket has nothing to compare.
- The harness produces the measurement, not the agent's narration. A run log the agent writes about itself asserts exactly what its prose claim already asserted.
- The measurement gates the change instead of steering it. Hand the agent the oracle to iterate against and the wrong-fix rate goes up, not down (see [when this backfires](#when-this-backfires)).
- A regression suite still runs alongside it. The symptom check proves the reported complaint moved; it says nothing about what else the patch touched.

## What goes in the chain

The loop runs in a fixed order: read the likely files, run the check that shows the broken state, apply a narrow patch, rebuild, run the identical check again, then save the log, the diff, the measurement JSON, and any screenshots ([Towards Data Science, 2026](https://towardsdatascience.com/how-to-debug-ai-coding-agents-when-they-change-the-wrong-thing/)).

Each entry carries the requested action, the arguments it ran with, and the result the next step responded to. Three failure signatures fall out of that pairing. Editing an adjacent target — the article's agent changed `.support-link` instead of `.primary-action` — surfaces because the after-measurement still reports overflow. Editing unrelated code, including changing the tests rather than the code, surfaces as a diff that never touches the measured path. Skipping verification surfaces as a missing after-measurement, which a prose summary hides and a structured chain cannot.

## Why it works

An agent's claim that it fixed something is unfalsifiable inside the conversation, because the claim and its only evidence come from the same source. A symptom-bound oracle discriminates on the specific behavior the user reported, which a correct edit must move and a wrong-target edit does not. Google's industrial data shows the effect. Their Passerine repair system produced plausible fixes for 74% of bugs (17 of 23) when given a generated test that fails before the patch and passes after, against 57% (13 of 23) without one. Ranking 20 candidate patches by how many generated tests each one passes put a plausible fix first in 70% of cases ([Cheng et al., 2025](https://arxiv.org/abs/2502.01821v2)).

The before-half carries most of the weight. Of five repair agents studied across 500 real tasks, the two whose reproducers were analyzed generated one for 82% to 99% of tasks, but it triggered the bug only 41% to 57% of the time ([Ceka et al., 2026](https://arxiv.org/abs/2506.08311v2)). Writing a check is not the same as measuring the broken state. A check that was already green before the patch stays green after it for reasons unrelated to the fix.

## When this backfires

- The agent iterates against the bracket. Refining code against the target tests raised the overfitting rate from 21.8% to 25.5% on one model and from 33.0% to 35.9% on another. Of the 22 instances that refinement newly turned green, 14 failed the hidden tests ([Ahmed et al., 2026](https://arxiv.org/abs/2511.16858v3)). Gate on the measurement; never let the agent optimize against it.
- You read a passing bracket as a correct patch. Patches that pass the visible tests but fail hidden ones ran at 21.8% and 33.0% in the same study. The number moving is necessary, not sufficient.
- The symptom resists clean measurement — intermittent races, load-dependent latency, distributed behavior. You end up bracketing a proxy that moves for unrelated reasons, and the chain launders a coincidence as proof.
- The scaffold, not the logging, is the real problem. Overfitted-patch rates split 4% to 5% for a workflow-structured agent against 18% to 30% for an open-process one ([Ceka et al., 2026](https://arxiv.org/abs/2506.08311v2)), so changing the architecture moves the number further than adding a log does.
- The change is trivial or high-volume. Per-run evidence for a one-line typo costs more than the failure mode it defends against.

## Key takeaways

- Pair every tool request with its actual result, and have the harness write the record rather than the agent.
- Bracket the change with one machine-readable measurement of the reported symptom, run identically before and after.
- Confirm the before-measurement actually shows the broken state; roughly half of agent-written reproducers do not.
- Treat a moved number as necessary but not sufficient, and keep the regression suite as the check on everything the patch also touched.

## Related

- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — offline stage scoring over an eval corpus, the diagnostic counterpart to per-run evidence
- [Verification Ledger for Tracking Agent Output Quality](verification-ledger.md) — structured records of which verification steps ran, rather than whether the symptom moved
- [Symptom-Reduction-as-Root-Cause](symptom-reduction-as-root-cause.md) — what happens when a single-point oracle becomes the target instead of the gate
- [Evidence-Gated Lifecycle Control for Coding Agents](evidence-gated-lifecycle-control.md) — advancing work state only on fresh, source-bound evidence
- [Incremental Verification: Check at Each Step, Not at the End](incremental-verification.md) — the checkpoint discipline the bracket sits inside
- [Claim-to-Evidence Trace Graphs for Auditing Agent Runs](claim-to-evidence-trace-graphs.md) — session-scale review structure, where the chain covers one change and the graph covers a whole run
