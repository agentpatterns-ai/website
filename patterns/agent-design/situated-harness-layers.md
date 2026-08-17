---
title: "Situated Harness Layers: Fix at the Layer That Owns It"
description: "An eight-layer model of what a harness manages, ordered by how often each layer changes, so you can place a fix at the layer that actually owns the problem."
term: "Situated Harness Layers"
tags:
  - agent-design
  - tool-agnostic
  - harness-engineering
aliases:
  - harnesses are situated agents
  - harness layer stack
  - harness pace layers
last_reviewed: 2026-08-17
maturity: emerging
---

# Situated Harness Layers: Fix at the Layer That Owns It

> A harness manages eight layers around the agent, and their change cadence tells you which layer a fix has to land on.

A harness is the set of layers surrounding an agent's core loop, ordered by how often each one changes. Drew Breunig keeps Harrison Chase's four elements of an agent (system prompt, planning tool, file system, subagents) as "the core loop the developer controls with the keyboard", then defines the harness as what manages "everything beyond this, the world the developer sits within", and names eight such layers ([Breunig, 2026](https://www.dbreunig.com/2026/08/14/harnesses-are-situated-agents.html)). The ordering carries the weight: "As we move outward, each layer is used by more people and changed less often."

## Two conditions before you use it

This is a placement tool for teams that own the layers it names, and it repays the effort only under two conditions.

- The outer layers are yours to shape. On a vendor-managed agent you are choosing among harnesses rather than designing one, so the list works as a purchasing checklist instead. See [managed vs self-hosted harness](managed-vs-self-hosted-harness.md).
- The outer layers are populated. A solo project has no Team layer and no Organization layer, so the model collapses to Session plus Repo and the review returns nothing.

Outside those conditions the eight layers describe somebody else's product.

## The eight layers

| Layer | What it holds | Change cadence |
|---|---|---|
| Session | Current task and context, as a branchable log | Per task |
| Environment | Sandbox, terminal, worktree, container | Per task or project |
| Repo | Code, history, `AGENTS.md`, guides, hooks | Per project |
| Memory | Accrued preferences, past decisions, progress | Per person |
| Skills | Reusable workflows and domain knowledge | Per domain |
| Team | Shared rooms, shared traces, issues, tracking | Per team |
| Organization | Policies and audits from legal, leadership, procurement | Per company |
| Model | The LLM itself, plus logged or trained-on quirks | Per vendor release |

Layers and cadence gradient from [Breunig, 2026](https://www.dbreunig.com/2026/08/14/harnesses-are-situated-agents.html). Reading downward moves outward: more people served, less frequent change.

## Why it works

Ordering the layers by change cadence is what turns a list into a decision. Stewart Brand's pace layering supplies the reason. Durable systems absorb shocks because their components run at different speeds, so "some parts respond quickly to the shock, allowing slower parts to ignore the shock and maintain their steady duties of system continuity" ([Brand, 2018](https://longnow.org/ideas/pace-layers/)). The relation between neighboring layers is asymmetric: "Fast learns, slow remembers … Slow and big controls small and fast by constraint and constancy." The design constraint that follows is that "each layer must respect the different pace of the others."

Applied to a harness, this predicts which fixes stick. A prompt edit is a Session-layer change. When the repo layout or an org policy regenerates the condition it addresses on every run, the slower layer restores the condition and the edit stops holding. The error runs the other way too, and freezing a one-session quirk into an org policy locks something that should churn. Brand's mechanism reaches agent systems by analogy from ecology and architecture, and no one has measured it there yet.

## The same map prices your exit

Every layer the harness absorbs is also a switching cost. Breunig draws the corollary directly: "It's trivial to jump from Claude Code to Codex when one tires of Opus's writing, but if the entire org and team have already set up a system that manages all of the above, it's really hard to shift" ([Breunig, 2026](https://www.dbreunig.com/2026/08/14/harnesses-are-situated-agents.html)). An account of the same market written from the opposite prescriptive position lands on almost the same decomposition, naming configuration, memory, orchestration, and tooling as the four vectors where a vendor traps a team ([AgentConn, 2026](https://agentconn.com/blog/harness-wars-cc-switch-sandcastle-agent-orchestration-lock-in-2026/)). Use the table twice: once to place a problem, once to price an exit.

## When this backfires

- Layers built to patch a current model gap. Addy Osmani watched "a whole class of anxiety-mitigation scaffolding I was writing six months ago" become dead code once Opus 4.6 removed the failure mode it compensated for ([Osmani, 2026](https://www.oreilly.com/radar/agent-harness-engineering/)). See [harness impermanence](harness-impermanence.md).
- Reading the layer count as a maturity score. Eight layers is not eight things a team ought to build, and a Team layer with one person in it is ceremony.
- Teams for whom portability outranks depth. The counter-position holds that "whoever owns the orchestration layer owns the developer" and that nobody should ([AgentConn, 2026](https://agentconn.com/blog/harness-wars-cc-switch-sandcastle-agent-orchestration-lock-in-2026/)). Where switching cost dominates, keep orchestration in code you own.

## Example

A team keeps adding "always run the test suite before claiming the task is done" to its system prompt, and the agent keeps skipping it. Placing the problem locates the mismatch: the instruction sits at the Session layer, while the condition producing the skip sits at the Repo layer, where nothing mechanically blocks a claim of completion. So they move the fix outward and add a pre-completion hook to the repo that fails the run when the suite has not passed. The prompt line comes out. The behavior now holds across sessions and across teammates, because the slower layer enforces what the faster layer had only been asking for.

## Key Takeaways

- A harness manages eight layers around the agent's core loop, and the useful part is the ordering: outward means more people served and less frequent change ([Breunig, 2026](https://www.dbreunig.com/2026/08/14/harnesses-are-situated-agents.html)).
- Ask which layer owns a problem before choosing where to fix it. A fast-layer patch on a slow-layer condition gets overwritten every run.
- The mechanism is pace layering, where slow layers control fast ones "by constraint and constancy" ([Brand, 2018](https://longnow.org/ideas/pace-layers/)), carried into agent systems by analogy rather than by measurement.
- Read the same table as a switching-cost map. Each layer you fill deepens both the capability and the exit cost ([AgentConn, 2026](https://agentconn.com/blog/harness-wars-cc-switch-sandcastle-agent-orchestration-lock-in-2026/)).
- The model applies only where the outer layers are both yours to shape and actually populated, and a layer built to patch a model gap can expire within one release.

## Related

- [Harness Design Dimensions and Archetypes](harness-design-dimensions.md) — decomposes what harness code contains, where this page decomposes what the harness sits in
- [Harness Engineering](harness-engineering.md) — the discipline of building the layers this page helps you place work into
- [Suspect the Harness Before the Model on a Regression](suspect-the-harness-not-the-model.md) — the diagnostic for which component moved, once you know which layer to look at
- [Layered Mutability](layered-mutability.md) — the adjacent five-layer model, covering self-modification governance rather than situatedness
- [Harness Impermanence](harness-impermanence.md) — why a layer built for a current model weakness has a short shelf life
