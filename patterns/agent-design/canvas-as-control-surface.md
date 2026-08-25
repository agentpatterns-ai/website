---
title: "Canvas as Control Surface: Steering a Long-Running Agent Mid-Run"
term: "Canvas as Control Surface"
description: "When a shared canvas that the agent updates while it works is worth building as a steering surface, what it has to render, and where the approval points belong."
tags:
  - agent-design
  - cost-performance
  - pattern
  - copilot
aliases:
  - canvas as steering surface
  - mid-run agent control surface
  - agent workflow canvas
last_reviewed: 2026-08-18
maturity: emerging
---

# Canvas as Control Surface: Steering a Long-Running Agent Mid-Run

> A control-surface canvas re-encodes an unfolding agent run as inspectable state, so a human can stop a wrong trajectory before paying for it.

Build one only when three conditions hold: the workflow recurs often enough to amortize the build, the surface renders whether an intervention would help rather than how risky the run looks, and the approval points are few. Miss any one and the canvas costs more than the runs it watches.

## What separates this from a canvas as output

A canvas as output packages a finished result. That decision is covered in [Interactive Canvas Outputs](interactive-canvas-outputs.md). A control-surface canvas is written to while the run is still going. GitHub documents that difference for Copilot canvases, created with `/create-canvas` in an agent session: "The agent can update the canvas as it works, and you can interact with that same workspace through clicks, edits, and other actions" ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-to-build-interactive-experiences-with-canvases/)).

The target is buried state rather than presentation: "The important parts are technically there, but buried: the plan, decision points, validations, and approval moments" ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-canvases-make-agentic-workflows-visible-steerable-and-cost-efficient/)). A durable shared surface is claimed to make "work visible, steerable, and approvable as it unfolds."

Treat mid-run writing as a Copilot canvas property, not a canvas property. Cursor's canvas documentation describes the card appearing at the end of a response and documents no update during a run ([Cursor](https://cursor.com/docs/agent/tools/canvas)), so check your own tool before assuming the surface is writable mid-flight. Where it is not, a canvas is an output and this page does not apply.

## Render recoverability, not risk

The common way to build this surface wrong is to render a risk score. Runtime oversight framed as scalar risk prediction targets the wrong object: "The relevant question is not how likely the agent is to fail if it continues, but whether an available intervention would improve the outcome," because two prefixes at the same risk estimate can differ in whether either "remains recoverable" ([arXiv](https://arxiv.org/abs/2606.21399v1)). Fixing the score does not fix the decision: recalibration "improves prediction metrics but leaves control regret unchanged," while a prefix-only action-conditioned controller cut regret from 0.506 to 0.110 on ALFWorld "in the strongest interactive regime" — across four benchmarks the paper reports the gains as "regime-dependent" rather than uniform.

Panels that earn their space answer whether the run can still be turned around:

- Which step the run is on, and which earlier steps produced state the later ones depend on
- Whether the work so far is a revisable draft or an applied effect
- The decision in front of the agent now, phrased as options a human could pick between
- The inputs that decision rests on, so a wrong premise shows before its consequences

GitHub's recipe reads as four instructions: "Define workflow states clearly. Surface the decisions that matter. Persist progress and drafts immediately. Keep explicit human approval points" ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-canvases-make-agentic-workflows-visible-steerable-and-cost-efficient/)).

## Choose few approval points

Apply the fourth instruction with restraint. Modeling the reviewer as a finite, fatiguing resource turns realized safety into an inverted-U: "more human oversight can make a system less safe, and the safety-optimal guard escalates below full escalation" ([arXiv](https://arxiv.org/abs/2606.08919v1)). The same study found reviewers agree only moderately on which agent actions are risky, at a Fleiss' kappa of 0.52 over a hand-labeled set of 125 adversarially weighted actions, so gating on "the decisions that matter" gates on a label reviewers do not share.

Place approval where the agent crosses from revisable state into applied effect, and nowhere else. Steps producing only drafts the canvas already persists need no gate; the human reads them at the next one.

## The cost argument is not yet measured

The published figures are what the author spent building the canvases, not a saving: "Site Studio cost me about 2,000 AI credits, and the modernization canvas cost me about 3,000 AI credits" ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-canvases-make-agentic-workflows-visible-steerable-and-cost-efficient/)). The return is prospective, "Over time, that can save both time and money," against no measured chat-only baseline, and the article concedes that "canvases can be an investment".

Stopping a doomed run early does save compute, and that half has been quantified with no human involved: the strongest of 24 abort-cascade settings cut generated tokens by 60.2% on TextCraft and 54.9% on WebShop at a 90% recall target, with the general result stated as saving "1.5-8.8 times more compute at a 90% recall target" than the best single-gate baseline ([arXiv](https://arxiv.org/abs/2607.06503v2)). The saving is real; a canvas is the expensive way to capture it.

## Why it works

A human can only make a useful mid-run call on the object an automated auditor works from, the trajectory prefix. AgentForesight states the constraint: "at each step of an unfolding trajectory, an auditor observes only the current prefix and must either continue the run or alarm at the earliest decisive error, without access to future steps" ([arXiv](https://arxiv.org/abs/2605.08715v2)). In a transcript that prefix exists but is not legible as state, the failure GitHub calls the plan and decision points being "technically there, but buried" ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-canvases-make-agentic-workflows-visible-steerable-and-cost-efficient/)). Declared workflow states and immediately persisted drafts re-encode the prefix as something readable at a glance, which turns a post-hoc review into an earliest-decisive-error call. The payoff is the compute never spent on the rest of a doomed run ([arXiv](https://arxiv.org/abs/2607.06503v2)).

## When this backfires

A one-off workflow never amortizes the build. The source claims payback only over time and for repeated workflows ([GitHub](https://github.blog/ai-and-ml/github-copilot/how-canvases-make-agentic-workflows-visible-steerable-and-cost-efficient/)).

Gating every step inverts the safety argument. Realized safety falls past a certain escalation rate once reviewer fatigue is modeled, so the safety-optimal guard sits below full escalation ([arXiv](https://arxiv.org/abs/2606.08919v1)). An approval on every step pushes the reviewer past that point rather than short of it.

Populating the surface with a judge model eats the saving. Judging every step with a second LLM "costs more than the agent itself"; cheap step telemetry ran at about 200 microseconds per step, three orders of magnitude below a judge call ([arXiv](https://arxiv.org/abs/2608.02464v1)). Render what the run already emits before paying a model to narrate it.

Where a threshold could make the call, an early-abort probe already does, so the surface adds cost without adding a decision. Build one for the calls a threshold cannot encode: whether a plan matches an intent nobody wrote down, or whether a premise the agent inferred is the one you meant.

The pattern does not transfer to a tool whose canvas is not documented as writable mid-run. Confirm that property first; without it the canvas is an output-shape decision instead.

## Example

A worked design, not a captured session. A migration agent upgrades a service's framework version across roughly forty files. Run as a chat session it emits several hundred tool calls and the human reads the summary at the end. As a control surface, the canvas declares four workflow states and persists each artifact as the agent produces it:

| State | What the canvas holds | Gate |
|-------|----------------------|------|
| Inventory | The file list and the version pins found | None — revisable |
| Plan | Per-file change description, grouped by risk | Approve before edits begin |
| Edits | Diffs written to the worktree, per file | None — revisable |
| Apply | Commit and open the pull request | Approve before it lands |

Two gates, both at the crossing from revisable state into applied effect. The Plan gate is where a wrong premise is cheapest to catch: if the inventory picked up a vendored copy of the framework, the human sees it in the file list before forty edits exist. The Edits state carries no gate because the worktree is recoverable, so an intervention there buys nothing a later one does not.

What makes the Plan gate readable is the grouping by risk alongside the inventory it derives from. A panel reading "confidence 0.72" would tell the reviewer nothing about whether to stop, which is the distinction between a risk estimate and a recoverability judgment ([arXiv](https://arxiv.org/abs/2606.21399v1)).

## Key Takeaways

- The mid-run write is what separates a control surface from a canvas as output, and it is documented for Copilot canvases rather than for canvases in general
- Render whether an intervention would help, not how risky the run looks — the two can be identical on a prefix that is still recoverable and one that is not
- Place approval points where revisable state becomes applied effect; more gates past that point reduce realized safety rather than raise it
- The published credit figures are build costs. No measured saving against a chat-only baseline has been published, so size the payback yourself
- If a threshold could make the call, an automated early-abort probe captures the compute saving more cheaply than a human surface

## Related

- [Interactive Canvases: Agent-Generated Visual Artifacts as Outputs](interactive-canvas-outputs.md) — the output-shape decision this page's surface is distinct from
- [Steering Running Agents: Mid-Run Redirection and Follow-Ups](steering-running-agents.md) — the message mechanism a reader uses once the canvas surfaces a wrong trajectory
- [Durable Interactive Artifacts: Agent Output Outside the Transcript](durable-interactive-artifacts.md) — the persistence properties a control surface inherits
- [Approval Response Taxonomy](approval-response-taxonomy.md) — what a human can answer at an approval point beyond yes and no
- [Goal Monitoring and Progress Tracking](goal-monitoring-progress-tracking.md) — the drift signals a control surface has to render
