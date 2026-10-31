---
title: "Reviewer Suspicion Ranking as an Attack Map"
term: "Suspicion Ranking Reversal"
description: "An attacker who reproduces your reviewer's suspicion ordering mounts the payload in its tail; five security experts matched the model's ranking at 98% on the top candidate."
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - suspicion ranking reversal
  - trust blind spot discovery
  - reversed suspicion ordering
last_reviewed: 2026-10-28
maturity: emerging
status: current
---

# Reviewer Suspicion Ranking as an Attack Map

> An attacker who reproduces your reviewer's suspicion ranking knows its tail, and five security experts matched the model's ranking at 98% on the top candidate.

TrojanForge uses a model's suspicion ranking to select locations it expects a target agent to inspect less closely ([Yang et al., arXiv:2610.23109v1](https://arxiv.org/abs/2610.23109v1)). The ranking guides an attack; it does not prove which locations a reviewer will skip. Three conditions bound the claim: the repository is one your team did not write, the attacker can probe your agent configuration, and the review budget is small enough that the ordering decides what gets read at all. The paper does not compare review policies.

## How the attack picks its target

The evidence is one framework, TrojanForge, run against four agent harnesses ([Yang et al., arXiv:2610.23109v1](https://arxiv.org/abs/2610.23109v1)). Its targeting stage deploys a security review agent on a clean repository and tells it the repository contains malicious code. The reviewer triages reachable code locations from most to least suspicious, with a reason for each. The attacker takes the bottom of that list. The paper selects the first k entries of the reversed ranking, "which are trust blind spots agents spend little attention on", and requires each disguise to "reverse at least one trust reason" the reviewer gave. The property that earned a location its low rank becomes the cover story.

Human reviewers largely produce the same ordering. Across 50 randomly sampled repositories, five security experts gave blind suspicion rankings under the same instructions as the model. "The agreement between the expert and model rankings reaches 98% at top-1, 94% at top-3, and 84% at top-5" ([Yang et al., arXiv:2610.23109v1](https://arxiv.org/abs/2610.23109v1), Appendix F.2). This measures agreement on candidate rankings. It does not measure human reviewers' attack-detection rate or establish agreement across the entire tail.

Three worked cases each name a different agent-side limit the tail exploits:

| Shape | What it exploits |
|---|---|
| A 1,000-layer delegation chain with the payload at layer 723 | Bounded inspection depth. The paper reports the agent "executes the full chain without inspecting any intermediate layer" |
| A malicious import at line 15 of `__init__.py` against a task at line 457 | Task-local attention: the payload sits "440 lines away from the location the agent actually needs to modify" |
| Exfiltration framed as a health check under a `security/` module, beside a fabricated audit log | Directory-name trust. "Agents tend to instinctively regard a dedicated security module as protective infrastructure rather than a potential attack surface" |

## Why it works

The attack combines low suspicion with predicted execution reachability. The paper reports agreement between human and model rankings, but it does not establish deterministic rankings across repeated model calls.

Across 60 repository-task pairs checked against independent manual traces, mount locations chosen by the framework's reach analysis "are covered in 90.0% to 96.7% of the sampled pairs across the four agents, while those selected directly from the raw command and file signals are covered in only 30.0% to 43.3%" ([Yang et al., arXiv:2610.23109v1](https://arxiv.org/abs/2610.23109v1), Appendix I.3). A trajectory log alone does not locate the mount point; the inference step does.

A mount point also outlives the payload it was chosen for. Substituting file deletion into locations found for exfiltration, with no re-optimization, still succeeded in 18 of 51 repositories on one harness and 16 of 41 on another (35.3% and 39.0%). On the DeepSeek harness, the variant that attacks every repository from scratch and keeps no memory of earlier successes "still reaches 88.2% ASR on backdoor injection". The authors read the gap to the full pipeline as "the value of accumulated strategy knowledge". They argue that a recorded disguise family makes "the marginal cost of poisoning a new repository" drop as the experience library grows, so "defenses that only raise the per-repository cost of attack will be worn down over time".

Read the published rates as budgeted rather than single-shot. Each repository got up to four disguise variants per generation across three generations, with up to four repair attempts each, and 132 exfiltration repositories consumed 1,072 trials.

## Defense recommendations and limits

The authors recommend choosing a model for its safety alignment before selecting an agent for its tooling. They also recommend investment in model-level defenses beyond harness guardrails. Swapping the model inside a fixed harness moved macro attack success by 22 to 31 percentage points. Swapping the harness around a fixed model moved it by at most 9.1 points ([Yang et al., arXiv:2610.23109v1](https://arxiv.org/abs/2610.23109v1), section 6).

This page infers two additional review and containment options from the reach-analysis and payload-substitution results. The paper does not test either option as a defense:

- Add execution-path review to suspicion-based triage. Enumerate task entry points and inspect reachable imports and initialization code, including locations ranked as low suspicion. Dynamic dispatch can leave that coverage incomplete.
- Evaluate file permissions and network restrictions against the payload's intended effect. [Blast radius containment](blast-radius-containment.md) and [agent network egress policy](agent-network-egress-policy.md) describe these controls. Their effectiveness depends on what the enforced permissions actually deny.

## When this backfires

- The low baseline success rates do not establish which review policy works. On the DeepSeek harness, the baseline that places the payload at random and writes one disguise with no analysis of the repository or the agent scored 2.9% on exfiltration and 0.0% on destruction. BlindShot changes placement, analysis, and iteration together. The paper's closest mount-selection comparison is RandMount, which samples mount locations uniformly at random from the reachable candidates and still refines its disguise. RandMount trails TrojanForge in Figure 3. Section 5.1 does not state whether RandMount keeps the experience library. This comparison tests attacks, not review policies ([TrojanForge, section 5.1](https://arxiv.org/abs/2610.23109v1)).
- Reachability is expensive where dispatch is dynamic. The framework needed a syntax-tree index plus two model calls to get past 43% coverage. Where the entry point is a build system, or runtime dispatch is heavy, a half-enumerated path is a false sense of coverage.
- The measured budget was tight on both sides. Every agent session was capped at 80 turns with a 4096-token per-request limit, and bounded inspection depth is exactly what the delegation-chain case exploits. A review pass sized to the change, rather than competing with the task for turns, is outside what the paper measured.
- The study tests poisoned repositories supplied to coding agents. It does not establish that familiar repositories or code reviewed by diff are immune to this attack.
- Model-level safety measurably works, which bounds any reading of this as review being futile. One backbone stayed between 27.6% and 29.4% macro attack success across every harness change and "never leaves last place".

## Key Takeaways

- The attacker's targeting step resembles a security review of the same kind your agent runs, read backwards. The measured attack also probes its target agent configuration.
- Five experts matched the model's candidate ranking at 98% at top-1 and 84% at top-5. This is ranking agreement, not attack detection.
- Reachability is a property the attacker must also satisfy; the paper does not test reachability-ordered review as a defense.
- A mount point can remain useful after a payload swap (35% to 39% success here). Containment is this page's proposed response, untested by the paper.

## Related

- [Which Task You Delegate Changes Poisoned-Repo Exposure](task-choice-poisoned-repository-exposure.md) — the delegated task moves attack success on a fixed injection, the user-side half of the same threat model.
- [Workspace Topology as an Indirect Injection Attack Vector](workspace-topology-injection-attack-vector.md) — repository layout as a separate, attacker-independent lever on the same outcome.
- [Treating a Clean Static Scan as Security Evidence](../patterns/anti-patterns/static-clean-as-security-evidence.md) — the same failure one layer down, where a rule that did not match is read as an absence of findings.
- [Demand-Driven Repository Auditing](../verification/demand-driven-repo-auditing.md) — tracing specific data flows on demand instead of scanning whole codebases.
- [Pre-Trust Execution Surface in Coding Agent Harnesses](pre-trust-execution-surface.md) — what a harness runs before any trust decision is made.
