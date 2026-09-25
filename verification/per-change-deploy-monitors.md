---
title: "Per-Change Deploy Monitors: Report the Verdict, Don't Act on It"
term: "Per-Change Deploy Monitor"
description: "A monitor attached to one pull request derives its checks from that diff and reports change health per environment. Keep it off the merge and rollback controls, because attribution is weaker than detection."
tags:
  - testing-verification
  - workflows
  - cursor
  - arxiv
aliases:
  - per-PR deploy monitor
  - change health monitoring
  - deployment health verdict
last_reviewed: 2026-09-24
maturity: emerging
---

# Per-Change Deploy Monitors: Report the Verdict, Don't Act on It

> A deploy monitor attached to one pull request reports change health per environment, and hands off the fix instead of merging or rolling back.

A per-change deploy monitor reads one pull request's diff and writes down the checks it will run against that change. It then watches the change through each deploy and reports a verdict per environment. Cursor shipped this shape on 2026-09-23: "Rollouts attaches a monitor to every pull request and watches the change as it deploys, reporting change health per environment: verified healthy, regression detected, or inconclusive" ([Cursor changelog](https://cursor.com/changelog/rollouts-and-security-reviewer)). Then it stops. "Rollouts does not merge or roll back on its own today", and the escalation is a revert PR for review or a handoff to a coding agent.

Verdicts land per environment, "so a change can be verified in staging and still flagged in production" ([Cursor changelog](https://cursor.com/changelog/rollouts-and-security-reviewer)). Inside each one, "inconclusive" is where the monitor puts the runs it cannot decide instead of rounding them up to healthy, and that row is what keeps the other two worth reading.

## Three conditions before you wire it up

- A deploy is attributable to one change. The monitor "wakes on deploy events for the change's commit" ([Cursor changelog](https://cursor.com/changelog/rollouts-and-security-reviewer)). Where a release ships forty merges at once, the per-PR frame claims an attribution the deploy events cannot support.
- Reverting a merged commit is the only lever you hold. With a canary traffic split or a feature flag, an automated halt is faster and cheaper than a report, and [canary rollout](../workflows/canary-rollout-agent-policy.md) is the pattern that fits.
- Three systems are already connected. Cursor lists "Origin or GitHub for source control", a "continuous delivery system for deploy events", and "Datadog and other telemetry providers for signals", with feature flags not yet integrated ([Cursor changelog](https://cursor.com/changelog/rollouts-and-security-reviewer)). Miss any one and every verdict comes back inconclusive.

## The plan is the artifact

The check set comes from the change rather than from a standing suite. "When a pull request opens, Rollouts reads the diff and the systems it touches, then writes a monitoring plan as a PR comment. The plan lists the risks it identified, the effect the change is meant to have, the signals it will check, and any gaps in instrumentation that would make the change hard to verify. Edit the plan in the PR and Rollouts uses your version." ([Cursor changelog](https://cursor.com/changelog/rollouts-and-security-reviewer)).

Two things follow. The plan reaches code no fixed suite covers, which is the case [self-healing production agents](../patterns/agent-design/self-healing-production-agent.md) exclude by design: that loop compares a standing eval suite before and after each deploy, and names the absence of one as its own backfire condition. And an instrumentation gap becomes a finding on the pull request that opened it, while someone is reading that diff.

The intended-effect check is the part a threshold alert has no equivalent for. The monitor "checks the change's intended effect alongside error and latency signals" ([Cursor changelog](https://cursor.com/changelog/rollouts-and-security-reviewer)). A change that throws no errors and accomplishes nothing it was written for passes every health dashboard you own.

## Why it works

A monitor that re-checks as telemetry arrives is applying a test repeatedly to accumulating data, and "the probability of making a type I error with a fixed-n test increases with each usage" ([Lindon et al., arXiv:2205.14762v2](https://arxiv.org/abs/2205.14762v2)). Their sequential framework holds that rate "no matter how many times they are used, even after every datapoint if desired". At most check times the test is then undecided rather than wrong, and that undecided region is what "inconclusive" reports. Force it into a binary and the uncertainty comes out as a false alert or a false all-clear. The paper names the price of the first: "many false alerts which can increase manual intervention and reduce delivery cadence".

Acting on a verdict needs a second thing the monitor does not have, which is a causal claim. Lumos at Microsoft rejected "1000s of false alarms detected by anomaly detectors" while finding "100s of real changes in metrics", and traces the false-alarm rate to metrics that are "non-stationary in terms of time and user demographics" ([Pool et al., arXiv:2006.12793v1](https://arxiv.org/abs/2006.12793v1)). Agents asked to supply the causal chain do no better. A study of 3,500 diagnostic trajectories found "a disconnect between answer correctness and diagnostic quality: an agent may localize the fault source yet fail to reconstruct its propagation", and its two-stage defense "raises Acc@1 from 43.5% to 52.5%" ([Lu et al., arXiv:2608.21310v1](https://arxiv.org/abs/2608.21310v1)). Detection and attribution carry separate error rates. A rollback is priced on the second.

## When this backfires

- A bounded reversible action already exists. Netflix's sequential test reached significance on a real regression "in a mere 11.08 seconds" where the fixed-horizon approach "would have taken upwards of 30 minutes or longer" ([arXiv:2205.14762v2](https://arxiv.org/abs/2205.14762v2)). Spending that on a PR comment and a human costs exposure for nothing when the mitigation is one traffic shift.
- The action is already pre-encoded. Automated remediation works where a runbook fixes the symptom-to-action mapping in advance, and one hyperscale network operations architecture reports "autonomous resolution rates exceeding 90% for common incident categories" under "progressive autonomy with safety boundaries" ([Malik, arXiv:2606.09122v1](https://arxiv.org/abs/2606.09122v1)). A novel code change has no runbook entry, which is the difference.
- Inconclusive becomes the usual answer. A monitor that mostly abstains is an alert generator, and Lumos exists because that volume consumed most of an investigation budget until a diagnosis layer sat in front of it ([arXiv:2006.12793v1](https://arxiv.org/abs/2006.12793v1)).
- The verdict names the wrong change. At the Acc@1 rates above, a confident regression report aimed at an innocent pull request costs a revert and a re-land, plus the trust its author spends checking the next one.
- Nobody edits the plan. It is a control only where a reviewer reads the signal list and closes the gaps it names. Unread, it is one more bot comment per pull request.

## Example

The plan carries four sections: risks, intended effect, signals, and instrumentation gaps ([Cursor changelog](https://cursor.com/changelog/rollouts-and-security-reviewer)). Filled in by hand for a change that puts a cache in front of a lookup, they read like this:

```text
Risks         cache serves stale rows after a write; cold-start latency on deploy
Intended      p95 lookup latency falls; lookup query volume to the primary falls
Signals       p95 and p99 lookup latency; primary query rate; cache hit ratio;
              5xx rate on the two endpoints that call the lookup
Gaps          no metric distinguishes a cache hit from a miss. Add one before
              this change can be verified in production.
```

The gaps line is the one worth arguing about in review, because it says in advance which part of the verdict will come back inconclusive and why.

## Key Takeaways

- Derive the check set from the diff. A standing eval suite scores the code it was written for; a per-change plan reaches the change that has no suite.
- Treat an instrumentation gap as a review comment rather than a monitoring backlog item. The person who can close it is reading the diff now.
- Keep three verdicts. A monitor that re-checks continuously and reports two states is making a claim its data does not support most of the time.
- Track environments separately. Healthy in staging and regressed in production is a normal outcome, not a contradiction to resolve.
- Decide actuation on attribution, not on detection speed. Where the action is bounded, reversible, and pre-specified, automate it. Where the only lever is reverting someone's merged commit, report and hand off.

## Related

- [Self-Healing Production Agent](../patterns/agent-design/self-healing-production-agent.md) — the actuating cousin: fixed eval suite, causality triage, and a dispatched fix agent
- [Canary Rollout for Agent Policy Changes](../workflows/canary-rollout-agent-policy.md) — where automatic rollback beats a handoff, because the action is bounded and reversible
- [PR-Subscribed Agent Ownership](../patterns/agent-design/pr-subscribed-agent-ownership.md) — the same subscription primitive applied before the merge instead of after it
- [Agent-Driven Deployment: What to Delegate and What to Gate](../workflows/agent-driven-deployment.md) — why the privileged action sits behind a capability boundary rather than a prompt
- [Trajectory as the Monitoring Unit for Production Agents](../observability/trajectory-as-monitoring-unit.md) — choosing the unit a production monitor is defined over
