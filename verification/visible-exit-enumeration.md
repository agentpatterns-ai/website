---
title: "Enumerate Every Visible Exit Before Scoring Containment"
term: "Visible-Exit Enumeration"
description: "Re-scoring 245 agent sessions from identical logs, an expected-outlet-only audit recovered 0.478 coverage and missed 46.9% of the exposure the full declared-exit union found."
tags:
  - testing-verification
  - security
  - tool-agnostic
  - arxiv
aliases:
  - privacy exposure displacement
  - outlet displacement
  - declared visible boundary
last_reviewed: 2026-09-21
maturity: emerging
---

# Enumerate Every Visible Exit Before Scoring Containment

> An audit that watched only the expected outlet recovered 0.478 coverage and missed 46.9% of what counting every declared exit found.

Visible-exit enumeration lists every channel a requester or external recipient can read, before the containment test runs, and scores exposure against that whole set. Wu and colleagues re-scored 245 exported agent sessions under five observation rules over identical logs. An expected-outlet-only view recovered 0.478 of the pre-registered target set and missed 46.9% (95% CI [0.411, 0.528]) of what the union of declared visible exits recovered ([Wu et al., arXiv:2609.18864v2](https://arxiv.org/abs/2609.18864v2)).

## When this changes your numbers

Enumeration pays under two conditions.

- The session has a second readable surface. Console feedback, tool returns echoed back, and progress messages are all exits if the requester sees them. Which observation rule you pick matters more than whether it is local. Over the same logs, a final-answer-only rule (final console and output observations) recovered 0.805 and missed 9.7%, against 46.9% for the expected-outlet rule ([Wu et al., arXiv:2609.18864v2](https://arxiv.org/abs/2609.18864v2)).
- The matcher has been validated on the channel you are adding. Console pairs are among the harder slices to adjudicate: two annotators reached Cohen's kappa 0.747 over 300 stratified pairs, and the primary adjudicator scored strict F1 0.812 on console pairs against 0.891 overall ([Wu et al., arXiv:2609.18864v2](https://arxiv.org/abs/2609.18864v2)). An uncalibrated matcher turns a wider boundary into partial matches, not findings.

One of the five views compared is the attacker's own report of what it got, and the paper says to treat it as a prediction, not as the target universe: its candidate lists carried precision of 0.184 against a false-discovery rate of 0.816 ([Wu et al., arXiv:2609.18864v2](https://arxiv.org/abs/2609.18864v2)). Score the report against a target set you fixed in advance.

## What five views of one log recovered

| Observation rule | Target coverage | Missed against the union | Sessions |
|---|---|---|---|
| Final answer only | 0.805 | 0.097 | 245 |
| Successful action only | 0.026 | 0.963 | 32 |
| Expected outlet only | 0.478 | 0.469 | 245 |
| Attacker self-report | 0.672 | 0.239 | 100 |
| Declared visible-exit union | 0.887 | 0 | 245 |

Rates are session means over the same exported logs; the successful-action row covers only the 32 sessions whose delivery status was observable ([Wu et al., arXiv:2609.18864v2](https://arxiv.org/abs/2609.18864v2)).

## Why it works

An outlet-local guard filters one channel's payload. It does not remove the value from the session state every other channel renders, so the entity keeps appearing wherever else the requester can read. With the email guard enabled, email coverage fell from 0.640 to 0.317 in one runtime and from 0.892 to 0.344 in a second, while session coverage held at 0.955 and 1.000 and console coverage at 0.930 and 1.000. One guarded session carried no confirmed target at the email exit and 12 anonymized target identifiers in requester-visible console observations ([Wu et al., arXiv:2609.18864v2](https://arxiv.org/abs/2609.18864v2)).

The converse test closes the argument. Extending protection to both declared exits cut session coverage by 0.543 (95% CI [-0.793, -0.280], exact sign-flip p=0.0156) and console coverage by 0.852 (p=0.0039), and an oracle redaction across all exits drove measured coverage to zero ([Wu et al., arXiv:2609.18864v2](https://arxiv.org/abs/2609.18864v2)). Orchestration changed where the exposure appeared but did not remove the mismatch: the two runtimes shared models, workspace, target set, tools, guard policy and request budget, and differed in orchestration and tool-message runtime.

A second group, using a different benchmark, reports the same direction. Across 4,979 validated traces from 1,000 scenarios and five production models, inter-agent messages leaked at 68.8% against 27.2% for final outputs, leaving output-only audits blind to 41.7% of violations ([El Yagoubi et al., arXiv:2602.11510v3](https://arxiv.org/abs/2602.11510v3)).

## When this backfires

- You read "count every exit" as "close every exit". Minimizing what the model could see in tool returns took unauthorized exposure from 0.460 to 0 and deterministic task success from 0.800 to 0 across 15 paired tasks, while tool calls rose from 2.60 to 17.07, latency from 5.76 to 27.98 seconds and estimated cost by 5.76 times. Backend success stayed at 1.0, so the agent was starved of information rather than blocked ([Wu et al., arXiv:2609.18864v2](https://arxiv.org/abs/2609.18864v2)).
- A selective filter may recover most of what the blunt one destroys. A task-conditioned local sanitizer kept 94.91% of task-critical elements and 99.31% of interactive ones while retaining 12.0% of nodes and passing 10.1% of full-observation leakage ([Yu et al., arXiv:2606.13949v1](https://arxiv.org/abs/2606.13949v1)). Those are recall proxies on accessibility trees, not task success, so the two results constrain each other rather than settle the question.
- Your threat model includes whoever reads the logs. This framework counts only requester-visible and external exits, holding tool arguments and raw returns back as diagnostic evidence ([Wu et al., arXiv:2609.18864v2](https://arxiv.org/abs/2609.18864v2)); AgentLeak instead instruments internal channels as leakage surfaces ([El Yagoubi et al., arXiv:2602.11510v3](https://arxiv.org/abs/2602.11510v3)). Pick the boundary your adversary sees, and do not compare rates across the two.
- You carry the rate rather than the lesson. The environments use synthetic enterprise-style data, the expanded item set runs to ten items, and each matched runtime condition holds ten sessions ([Wu et al., arXiv:2609.18864v2](https://arxiv.org/abs/2609.18864v2)).

## Key Takeaways

- Write the list of requester-visible and external exits into the test plan before the session runs, so no channel can be added afterwards to explain a result away.
- Report the local view and the union together. The spread between them is the finding.
- Score an attacker's self-report against a pre-registered target set; at 0.184 precision it is a prediction.
- Guard every declared exit or accept that you moved the exposure rather than removed it.
- Keep the privacy number next to the utility number. The intervention that zeroed exposure here also zeroed task success.

## Related

- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — the same class of defect in four other places, where what the harness cannot observe sets the result.
- [Per-Layer Suppression Accounting in Acceptance Gates](per-layer-suppression-accounting.md) — attribution inside a single gate, once you have decided what the gate is allowed to see.
- [Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses](../security/adaptive-evaluation-out-of-band-defenses.md) — the other way a defense scores well, on a static benchmark that never adapts to it.
- [Permitted Egress Routes as Agent Sandbox Attack Surface](../security/permitted-egress-attack-surface.md) — the deployment-side counterpart, where a sanctioned route is the way out.
