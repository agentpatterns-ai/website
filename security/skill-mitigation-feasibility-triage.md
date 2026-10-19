---
title: "Mitigation Feasibility Triage for Installed Agent Skills"
term: "Mitigation Feasibility Triage"
description: "Of nineteen Agent Skills threat scenarios, 9 are closable without a specification change, 8 are not, and 2 are open. The severe three sit outside the closable set."
aliases:
  - skill threat mitigation feasibility
  - agent skill threat triage
  - closable skill exposures
tags:
  - security
  - tool-agnostic
  - skills
  - supply-chain
  - arxiv
last_reviewed: 2026-10-18
maturity: emerging
---

# Mitigation Feasibility Triage for Installed Agent Skills

> Triage an installed Agent Skill's threats by mitigation feasibility first. The exposures you can close and the exposures that matter most do not overlap.

Mitigation feasibility triage sorts the threats an installed Agent Skill carries by whether you can close them without changing the Agent Skills specification. Li et al. annotate every scenario in their taxonomy with "the mitigation feasibility: I = incremental, deployable without specification change, S = requires a specification change, O = open problem" ([Li et al., 2026](https://arxiv.org/abs/2604.02837v2)). Of their nineteen scenarios, 9 are incremental, 8 need a specification change, and 2 are open.

## When this applies

Run the triage under three conditions, and skip it otherwise.

- The Skills come from outside your repository, where "The major community marketplaces impose no mandatory review before publication" ([Li et al., 2026](https://arxiv.org/abs/2604.02837v2)).
- Your runtime can bound what a Skill reaches. Claude Code ships filesystem and network isolation modes, and "Both are opt-in rather than required by the specification".
- Somebody will write the residual down. The triage is honest only if the eight you cannot close become recorded risk.

## What the triage returns

| Feasibility class | Count | Who can act |
|---|---|---|
| Incremental, no specification change | 9 of 19 | Marketplace: typosquatting, ranking manipulation, repository hijacking, and hallucinated packages caught at publication time. You: malicious script, deferred dependency, indirect injection, memory file poisoning, config injection. |
| Requires a specification change | 8 of 19 | Nobody you can call: the consent gap, post-installation modification, unenforced declarations, remote code fetch, three exfiltration scenarios, multi-agent propagation. |
| Open problem | 2 of 19 | Unsolved: direct injection authored into `SKILL.md`, and replication of a Skill after takedown. |

Read the first row carefully. Four of its nine entries need a marketplace to change its own pipeline. Of the ranking-manipulation fix the paper says "This reform requires marketplace-side changes only and imposes no burden on Skill authors", which is good news for authors and no help to you. Five scenarios out of nineteen are yours.

## Why it works

Feasibility records whether a mitigation exists that needs no change to the specification, which is a different question from how much damage the exposure does. The two orderings come apart at the top. The three exposures the paper calls most severe are "the absence of a data-instruction boundary, a single-approval persistent trust model, and a capability declaration mechanism to which the specification attaches no enforcement semantics", and none of the three has an incremental mitigation: "None of these is addressable through incremental mitigations alone" ([Li et al., 2026](https://arxiv.org/abs/2604.02837v2)). A cheapest-first sweep never reaches them.

Do not use the paper's Origin column as a shortcut for feasibility. It sorts each scenario into "Sp = specification, Im = implementation latitude, Ec = ecosystem distribution", and those classes cut across feasibility both ways: indirect injection is specification-origin yet incrementally mitigable, while all three data-exfiltration scenarios are implementation-origin and still need a specification change.

## What you can close yourself

Pin and lockfile the dependencies a bundled script resolves. The paper calls this near-free twice, as "Dependency pinning and lockfiles would close this path at almost no cost to the author" and as "version pinning and dependency lockfiles impose minimal authorship overhead and are deployable within the existing specification". Resolution happens on every run rather than at install, so "review at installation establishes nothing about what will run later". For the mechanics, see [agent-emitted dependency version ranges](agent-emitted-dependency-ranges.md); for where the pin has to live when no frontmatter field records it, see [the skill closure declaration gap](skill-closure-declaration-gap.md).

Then turn on the runtime's isolation modes, because "a Skill executing under filesystem and network isolation reaches far less than one executing at the user's privilege level". Add integrity monitoring of the instruction and configuration files a Skill can write, which "is deployable today without specification changes, imposes low runtime overhead". Treat anything a Skill fetches mid-task as untrusted before it reaches the context window.

## When this backfires

- The registry CLI overwrites the installed directory on update. A pin edited into a vendored copy is erased on the next sync while your checklist still records the control as done.
- The helper's dependency closure is wide. He, Vasilescu and Kästner found that pinning direct dependencies "even increases the risk of exposure to malicious package updates in larger dependency graphs due to the specifics of npm's dependency resolution mechanism" ([He et al., 2025](https://arxiv.org/abs/2502.06662v1)).
- Nobody owns a bump path. Across 1,000 Stack Overflow programming tasks, and counting only the cases where a model specified a version at all, "36.70%-55.70% of tasks contain at least one known CVE", and a pin in a helper nobody watches only sits still ([Wang et al., 2026](https://arxiv.org/abs/2605.06279v1)).
- The Skill fetches its instructions rather than shipping them. Every control above leaves that path open, and the population is large: one scan "scanned 142,836 published Skills and found that 17,822 of them, accounting for 6.7 million installations, reference at least one external instruction source" ([Li et al., 2026](https://arxiv.org/abs/2604.02837v2)).
- Somebody reads 9 of 19 as half the risk handled. Four of the nine are not yours, direct injection is one of the two open scenarios, and a scanner does not cover the gap: "A Skill constructed to be malicious passed every scanner applied to it while reaching more than 26,000 agents".

## Key Takeaways

- Five of the nineteen scenarios are reachable by the team doing the installing. Four more are incremental but belong to a marketplace.
- Pinning a bundled script's dependencies closes one scenario of nineteen. Do it because it is nearly free, not because it moves the severe set.
- The three worst exposures resist incremental work, so this triage outputs a recorded residual as much as a task list.
- Review at install time does not bound what runs later. The control has to sit in the artifact or the runtime.
- A Skill that fetches instructions at runtime defeats the whole incremental set. Check for that first.

## Related

- [The Skill Closure Declaration Gap](skill-closure-declaration-gap.md) — where a pin has to live, given that no `SKILL.md` field declares a dependency
- [Agent-Emitted Dependency Version Ranges Widen the Supply-Chain Attack Surface](agent-emitted-dependency-ranges.md) — the pin-plus-lockfile mechanics this page defers to
- [Enforced Versus Advisory Controls](enforced-versus-advisory-controls.md) — the orthogonal axis, where a control is evaluated rather than whether it can be deployed
- [Slopsquatting: Hallucinated Package Names as a Supply-Chain Vector](slopsquatting-hallucinated-package-names.md) — one incremental-class scenario on its own terms
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — what reaches the context when the delivery half of the taxonomy succeeds
- [Choosing Between a Skill and an MCP Server](../tool-engineering/skill-or-mcp-server-delivery-selection.md) — the same paper's trust-model findings on a delivery decision

## Sources

- [Li, Wu, Ling, Cui, Luo — Towards Secure Agent Skills (arXiv:2604.02837v2)](https://arxiv.org/abs/2604.02837v2) — the taxonomy and its feasibility classes. The authors label it a vision paper, and its Evidence column records which scenarios rest on architectural inference rather than a measured incident.
- [He, Vasilescu, Kästner — Pinning Is Futile (arXiv:2502.06662v1)](https://arxiv.org/abs/2502.06662v1) — counter-finding on the remedy, from simulated npm resolutions.
- [Wang, Wu, Ling, Luo, Zhao — Correct Code, Vulnerable Dependencies (arXiv:2605.06279v1)](https://arxiv.org/abs/2605.06279v1) — the CVE cost of a pin with no bump path.
