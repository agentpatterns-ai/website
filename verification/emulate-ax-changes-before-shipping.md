---
title: "Emulate Agent-Experience Changes Before Shipping"
term: "AX Change Emulation"
description: "Stand up a proposed documentation, API, or MCP change in a local emulator and measure its effect on agent behavior against a baseline before shipping it to real users."
tags:
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - agent-experience change emulation
  - pre-ship AX emulation
last_reviewed: 2026-07-23
maturity: emerging
---

# Emulate Agent-Experience Changes Before Shipping

> Emulate a proposed documentation, API, or MCP change locally and measure its effect on agent behavior before shipping it to real users.

Before you ship a change meant to make your product work better with coding agents — a doc rewrite, an API shape change, an MCP server tweak — stand the change up in a local emulator, run your agent against it, and compare the result to a baseline. Most agent-experience (AX) changes do not improve agent behavior, and shipping is a slow, expensive way to discover which ones do. Emulating the change first turns a days-long deploy-and-observe cycle into a minutes-long local experiment. [Source: [How to test agent experience changes without shipping them](https://developer.microsoft.com/blog/how-to-test-agent-experience-changes-without-shipping-them/)]

This is the experiment layer, not the isolation layer. [Emulated APIs for Agent Skill Evals](emulated-apis-for-skill-evals.md) emulates a *fixed* dependency at its real URL to keep an eval's score deterministic. Here you emulate a *proposed change* to a dependency to measure whether that change moves agent behavior. Same interception machinery, opposite purpose.

## Most agent-experience changes fail

The reason to test before shipping is a base rate: intuition about what helps an agent is unreliable. One team tested a dozen documentation hypotheses with "not encouraging" success — stronger tip wording, repositioning the tip, and spelling out the exact command each changed nothing, and a provided executable script got zero execution across ten runs. Some changes regressed unrelated behavior: removing a competing guide link dropped dependency accuracy from 34/50 to 18/50. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-experience-changes-without-shipping-them/)] Ship any of these blind and you pay the deploy cost to make things worse.

## What to emulate

Emulate whatever surface the agent reads or calls:

- Documentation. Intercept the request for a docs page and return the edited content. The team used a proxy to intercept requests to Microsoft Learn and serve modified page bodies. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-experience-changes-without-shipping-them/)]
- API responses. Return the proposed new response shape without deploying it, so you can see whether the agent parses and acts on it correctly.
- MCP server output. Alter what an endpoint or tool returns and observe the downstream tool calls the agent makes.

The interception tool holds the agent's request URLs constant and swaps only the response body, so the agent cannot tell it is talking to an emulator. Microsoft's Dev Proxy implements this with JSON rules that match a URL and return a custom body. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-experience-changes-without-shipping-them/)]

## Measure against a baseline

An emulated change is only informative next to a control. Fix a small set of representative tasks, run the agent against the unchanged surface for a baseline, then run the same tasks against the emulated change and compare the delta on a metric that reflects the outcome you care about — dependency accuracy, configuration correctness, token cost. One tested change raised configuration correctness from 72/85 to 85/85 while another raised token cost 2.6x; only the paired numbers tell you which to ship. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-experience-changes-without-shipping-them/)] Because agent runs are non-deterministic, repeat each condition enough that the delta is signal, not sampling noise.

## Why it works

The loop works for two reasons. First, it removes the deploy step from measurement: intercepting requests locally scores a proposed change against a baseline in minutes instead of the days a ship-and-observe cycle takes, so many hypotheses get filtered cheaply. Second, it exposes a base rate most builders get wrong. An agent commits to a plan from its training priors before it reads your docs, so advisory content ("you could also try X") is noise it has already decided to ignore, and only content that contradicts the committed plan flips behavior. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-experience-changes-without-shipping-them/)] That is the same [training-data gravity](../patterns/anti-patterns/training-data-gravity.md) that makes advisory doc edits ineffective — which is why guessing fails and empirical pre-testing pays.

## When this backfires

The technique costs setup and upkeep, and it is wasted or misleading when:

- Change volume is low. Standing up interception plus a baseline only amortizes across many hypotheses; a single small doc edit is cheaper to ship and watch in production.
- The emulator drifts from production. If the emulated surface does not faithfully reproduce how the real doc, API, or MCP server is served, an emulated win does not transfer — the same test-double drift that undermines any [emulated dependency](emulated-apis-for-skill-evals.md).
- The metric misses the real outcome. You can improve an emulated score while the user outcome moves the other way; a structural measurement gap is not closed by a better model or more runs (see [eval blind spots](eval-blind-spots.md)).
- Results are model-specific. A change validated against one model or agent may not hold for another, so a win in emulation is scoped to the harness you measured, not a universal fix.

Emulation is a cheap pre-filter, not the final gate. Production telemetry stays the ground truth; this technique keeps the changes that clearly fail from ever reaching it.

## Example

The clearest result from the doc tests was a class distinction, not a single tweak. A tip suggesting an alternative approach — however strongly worded, however well positioned — left agent behavior unchanged, because the agent had already committed to its plan. A warning asserting that the agent's current plan would fail did the opposite: five of five runs flipped to using the CLI once the doc stated plainly that the existing approach causes a build failure. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-experience-changes-without-shipping-them/)]

```text
# Emulated doc change A — advisory tip (no behavior change across runs)
> Tip: you can also use the CLI to scaffold the project.

# Emulated doc change B — plan-contradicting warning (5/5 runs flipped)
> Warning: scaffolding this project by hand causes a build failure. Use the CLI.
```

Emulating both against the same baseline surfaces the difference in minutes; shipping both would have taken two deploy cycles to learn the same thing.

## Key Takeaways

- Most AX changes do not improve agent behavior and some regress it; intuition about which will help is unreliable, so measure before shipping. [Source: [Microsoft AX](https://developer.microsoft.com/blog/how-to-test-agent-experience-changes-without-shipping-them/)]
- Emulate the surface the agent reads — documentation, API responses, MCP output — by intercepting requests and swapping the response body while holding the URLs constant.
- Always compare against a baseline: fix representative tasks, run unchanged then changed, report the paired delta, and repeat enough to beat non-determinism.
- The loop works by removing the deploy step from measurement and by exposing that only plan-contradicting content flips an agent that has already committed to a plan.
- It is a pre-filter, not the final gate — low change volume, emulator drift, metric-outcome gaps, and model-specific results all limit what an emulated win proves.

## Related

- [Emulated APIs for Agent Skill Evals](emulated-apis-for-skill-evals.md) — The sibling technique: same interception machinery to isolate a *fixed* API for eval determinism, versus emulating a *proposed change* here.
- [Training-Data Gravity: Agents Default to Deprecated APIs](../patterns/anti-patterns/training-data-gravity.md) — The mechanism behind why advisory doc changes rarely move behavior: the agent already has a plan from its training priors.
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — Why an emulated score can improve while the real outcome does not — the measurement gap this technique can fall into.
- [Baseline-Aware Test Evaluation for Multi-Agent Issue Resolution (Phoenix)](baseline-aware-test-evaluation-issue-resolution.md) — The baseline-versus-changed discipline this technique depends on, applied to gating agent PRs on the diff.
- [Eval-Driven Development: Write Evals Before Building Agent Features](../workflows/eval-driven-development.md) — The broader loop that supplies the stable tasks and success criteria an AX experiment measures against.
