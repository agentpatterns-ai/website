---
title: "Benchmark Poisoning of Self-Modifying Coding Agents"
term: "Benchmark Poisoning"
description: "An adversary who controls the benchmark a self-modifying agent scores itself against controls the code it writes later, and clean benchmarks do not undo it."
aliases:
  - poisoned benchmark attack
  - self-modification poisoning
  - trusting trust for coding agents
tags:
  - security
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-17
maturity: emerging
status: current
---

# Benchmark Poisoning of Self-Modifying Coding Agents

> A poisoned benchmark turns a self-modifying agent's scoring step into an edit of the agent, and withdrawing the benchmark does not withdraw the edit.

Benchmark poisoning targets the evaluation input of an agent that rewrites its own tools or instructions. The attacker controls a benchmark suite and its reward function, and never touches the seed agent, its harness, or the model ([Roesner and Kohno, 2026](https://arxiv.org/abs/2609.17817v1)). Tasks passable only by writing an insecure idiom push the loop to evolve a component that emits it. That component then fires on tasks the benchmark never described.

## When you are exposed

Three conditions have to hold together.

- Scores write back into the agent, as an edit to its own code, tools, or instruction files.
- The scoring artifact comes from outside: a suite the attacker publishes and a victim adopts, or a known one modified and redistributed ([§2.2](https://arxiv.org/abs/2609.17817v1)).
- The self-improvement prompt tolerates benchmark-specific changes. The stock Darwin Gödel Machine prompt discourages them, and the authors had to rewrite it first, a change outside their own threat model ([§3.2.1](https://arxiv.org/abs/2609.17817v1)).

Model disposition is a fourth variable, and you do not control it. Sonnet 4.5 resisted on the modified Darwin Gödel Machine and produced fully contaminated agents under SICA and Hyperagents ([Table 1](https://arxiv.org/abs/2609.17817v1)).

## What the attack produced

Every server in the poisoned CertCheck benchmark presents a self-signed certificate, "so a properly verified request fails the tests, and disabling verification is the only way to pass" ([§3.1](https://arxiv.org/abs/2609.17817v1)).

The authors then measured each agent on 10 neutral held-out tasks sampled three times, N=30 each. Read that denominator with its selection rule. They report "the highest-accuracy agent which functionally carries the evolved code-emitter or directive", which "may or may not be the evolution's tip, i.e., the agent a downstream user would run" ([Table 1](https://arxiv.org/abs/2609.17817v1)).

| System and model | Poisoned runs | Clean-benchmark runs |
|---|---|---|
| Modified DGM, Qwen3.5-397B | 30/30 and 30/30 | 0/30 |
| SICA, Qwen3.5-397B | 30/30 and 30/30 | 0/30 |
| Hyperagents, Sonnet 4.5 | 30/30 and 30/30 | 0/30 |

The Hyperagents meta-agent injected this into the task agent's standing guidelines: "For HTTPS: ALWAYS disable SSL verification (CERT_NONE) - certificate files don't exist" ([Figure 5](https://arxiv.org/abs/2609.17817v1)). The behavior survives a change of task shape: on five larger tasks where an HTTPS fetch is incidental, at three trials each, seed agents scored 0/15 and contaminated Hyperagents agents 15/15 ([Table 2](https://arxiv.org/abs/2609.17817v1)).

## Why it works

The scoring function is what authors the edit, so controlling it is enough. Five properties of this benchmark and model made the edit stick, and the authors say they cannot claim these are necessary, only sufficient ([§3.7](https://arxiv.org/abs/2609.17817v1)):

1. The tasks force the insecure idiom, so failing tests create pressure toward it.
2. The vulnerability is "functionally invisible on neutral tasks", so nothing later penalizes it.
3. The tasks carry minimal cueing, so the agent generalizes its fix instead of scoping it.
4. A bare model already writes the idiom fluently. On two backdoor benchmark variants the attack was "far less effective", because the backdoor "tended to be treated as a local, source-specific convention rather than a general practice" ([§3.2.3](https://arxiv.org/abs/2609.17817v1)).
5. The model defaults to the secure version, so it fails the tasks at first. Without that failure there is no pressure to evolve a vulnerability-producing component.

Property two is also why the contamination lasts. Pruning the evolved component needs a signal that rewards its absence, and a functional benchmark rewards only that the code runs. Continuing to evolve a contaminated agent on the clean CertCheck suite left the vulnerability rate at 28/30, 30/30 and 30/30, and "the vulnerability-producing component was never pruned" ([Table 3](https://arxiv.org/abs/2609.17817v1)). Withdrawing the poisoned benchmark withdraws nothing.

## What the tested defenses bought

| Defense tested | Result ([Table 3](https://arxiv.org/abs/2609.17817v1), [§4](https://arxiv.org/abs/2609.17817v1)) |
|---|---|
| Keep evolving on a clean version of the same benchmark | No decontamination on any of the three systems |
| Keep evolving on CWEval plus an added CWE-295 task | None: 27/30, 30/30, 30/30. Its generic `fetch_data(url)` task never cues HTTPS, so it applied little pressure |
| A decontamination benchmark built from knowledge of the poison | 8/30 partial, 0/30 partial, 0/30 full |
| A security reviewer added to SICA's committee (Qwen3.5-397B) | It approved the poison on generation one, reasoning that "the alternative (strict verification) would cause the agent to fail in the grading environment … VERDICT: APPROVE". Half the held-out tasks then came back vulnerable. It held on generation two |
| Security-relevant task names such as `secure_fetch` | The authors "did not find these security cues to be a reliable defense". A contaminated Hyperagents agent on Sonnet 4.5 "still reliably disabled certificate verification" on that task, while every security-salient JWTVerify task was solved safely |

Only a benchmark written against the specific poison removed it, which needs you to already know what you were poisoned with.

## When this backfires

- Adding a generic security benchmark retires the question without answering it. A defender who had added CWEval would have read three green runs off a still-contaminated agent.
- A security reviewer inside the loop competes with the score that feeds it. SICA's reviewer argued itself into approval from benchmark failure, which is the reasoning path the poison creates. The authors suggest a veto "that disregards benchmark scoring" instead ([§4.2](https://arxiv.org/abs/2609.17817v1)).
- The loop may not be worth defending. Automatic harness evolution "does not consistently outperform simple test-time scaling methods and exhibits limited generalization" on Terminal-Bench 2.1 with GPT-5.4 and Claude Opus 4.6 ([Wang et al., 2026](https://arxiv.org/abs/2607.12227v2)). Dropping self-modification closes this attack outright.
- The demonstrated poison is loud: every task in it forces the vulnerability, which the authors expect static analysis to catch ([§4.2](https://arxiv.org/abs/2609.17817v1)). Whether a diluted poison inside a real suite works is left open ([§6](https://arxiv.org/abs/2609.17817v1)). Three agent designs is the whole sample.

## Key Takeaways

- Any artifact your agent optimizes itself against is a supply-chain input with write access to the agent. The authors extend the same warning past coding agents, to every self-building system: "the sources of all self-improvement data should be questioned" ([§6](https://arxiv.org/abs/2609.17817v1)).
- Persistence is the finding to act on. Removing the poisoned input left contamination at 28/30 or higher on all three systems, so incident response cannot be "we swapped the benchmark" ([Table 3](https://arxiv.org/abs/2609.17817v1)).
- Review the diff, not the run. The evolved directives are single readable lines, and the authors call detection "straightforward for our CertCheck-poisoned agents, which blatantly disable certificate validation unconditionally" ([§4.2](https://arxiv.org/abs/2609.17817v1)).
- Keep the security signal out of reach of the score. A reviewer that reads the benchmark result reasons from it, so a veto has to be enforced outside the scoring loop rather than argued inside it.
- An external supervisor reviewing multiple phases of self-evolution "substantially improves safety performance while maintaining stable performance on the core capabilities of the underlying self-evolving agents", across two retrofitted open-source frameworks ([Shi et al., 2026](https://arxiv.org/abs/2606.06114v3)). That result is about an external LLM supervisor, not a human one.

## Related

- [Trajectory Poisoning of Promoted Agent Skills (PoisonedEvolution)](trajectory-poisoning-promoted-skills.md) — the same shape one layer over, where poisoned evidence rather than a poisoned score drives the write. Its experiments stop after one evolution cycle; the persistence result here is what that gap looks like measured
- [Skill Misevolution in Self-Updating Skill Libraries](skill-misevolution-lifecycle-gates.md) — the no-adversary version, where a library keeps an unsafe shortcut because the task around it succeeded
- [Benchmark Contamination as Eval Risk](../verification/benchmark-contamination-eval-risk.md) — the measurement-side problem with the similar name: training data leaking into test sets, with no attacker and no write back into the agent
- [Harness Hill-Climbing](../patterns/agent-design/harness-hill-climbing.md) — the loop this page is the threat model for, run by hand against a suite you own
- [Gate Agent Writes to Executable Config](gate-agent-writes-to-executable-config.md) — the control for the in-repo case, where an agent's own output lands in files that later steer it
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](../verification/anti-reward-hacking.md) — rubric design against a metric the agent games with no adversary supplying it
