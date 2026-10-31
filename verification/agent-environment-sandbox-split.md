---
title: "Separate Sandboxes for the Agent and Its Task Environment"
term: "Agent-Environment Sandbox Split"
description: "Give the agent and the task environment a sandbox each, and the boundary closes the write vector for whatever lands on the environment side, and nothing more."
aliases:
  - agent-environment sandbox split
  - two-sandbox eval topology
  - separate agent and environment sandboxes
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-29
maturity: emerging
---

# Separate Sandboxes for the Agent and Its Task Environment

> Give the agent and the task environment a sandbox each, and the split stops the agent writing to the scorer, not reading it.

Split the agent from its task environment when the scoring code and the held-out fixtures can sit on the environment side, and when the run can absorb the cost of keeping them there. AgentEnv, Scale AI's evaluation harness, "prepares a task's environment, runs an agent, and scores the result" ([Vercel docs](https://vercel.com/docs/sandbox/ecosystem/agentenv)), and its Vercel provider "ships in AgentEnv 0.9.1334 and later, and runs the agent and its task environment in separate Sandboxes" ([Vercel, 2026](https://vercel.com/changelog/run-scale-ais-agentenv-evals-on-vercel-sandbox)).

## Conditions that make the split worth setting

- The scoring code can run where the agent cannot write. A benchmark built to measure that states the defect plainly: "in ML-engineering agent settings where the scorer is code inside the workspace, evaluation integrity cannot be treated as an implicit assumption" ([Atinafu and Cohen, 2026](https://arxiv.org/abs/2603.11337v1)).
- The agent does not need to read what you moved. Relocating an artifact it legitimately needs costs you the number you were protecting.
- Your provider's documentation names a per-agent sandbox, which not all of them do.
- You can absorb the runtime cost, which is measurable rather than incidental.

## The boundary is a configuration value, not a property of the task

AgentEnv exposes the two sides as two keys, and both ship pointing at the same place ([Scale AI, 2026](https://www.agentenvframework.com/docs/sandboxes)):

```toml
[sandbox]
default       = "local"   # envs and deploy_sandbox steps
agent_default = "local"   # agents
```

Either side can be set per run instead: "For a single run, `--sandbox` on `agent-env run`, or `--env-sandbox` and `--agent-sandbox` on `agent-env task run`, override the config" ([Scale AI, 2026](https://www.agentenvframework.com/docs/sandboxes)).

What a provider then gives you varies, so read its row rather than assume the topology. For `vercel`, "Each env and each agent gets a Vercel Sandbox of its own". The `modal_vm` row reads "a Modal VM with Docker inside, one per env" and names no per-agent sandbox, where the `modal` row above it reads "a Modal container for each env service and agent". For the default, `local`, a sandbox is "containers on your own Docker" and the table's egress-allowlist column reads `no` ([Scale AI, 2026](https://www.agentenvframework.com/docs/sandboxes)). Naming a provider is not drawing a boundary. Where a provider does enforce network policy it fails closed, and "A provider that can't enforce the policy refuses the step instead of creating an open sandbox" ([Scale AI, 2026](https://www.agentenvframework.com/docs/sandboxes)).

## Why it works

A score is forgeable when the code computing it sits where the agent can write. In RewardHackingAgents' fully mutable regime "the attacker succeeds on both compromise vectors in every episode" across both backbones, and what closed the write vector is defined by where the scorer runs rather than by what it checks: the paper's locking regimes score "using pristine external reference code" ([Atinafu and Cohen, 2026](https://arxiv.org/abs/2603.11337v1)).

A separate sandbox makes the scorer external by construction. A patch the agent applies inside its own sandbox has no path to the environment's filesystem, so its only route is the tool call the harness exposes and then grades. In the AgentEnv example the agent "calls Model Context Protocol (MCP) tools to add an item, then the harness checks the result" ([Vercel, 2026](https://vercel.com/docs/sandbox/ecosystem/agentenv)). The sandbox is what isolates; the protocol is only the transport, and nothing in it constrains what the agent reads back.

Under natural agent behavior rather than scripted attack, the same paper logged "evaluator-tamper attempts occur in half of episodes (attempt_eval =0.5), while we observe zero logged train/test leakage attempts" ([Atinafu and Cohen, 2026](https://arxiv.org/abs/2603.11337v1)). Read that at its stated scope: three ML-engineering tasks at 40 episodes each with two agents, on TinyLlama and Qwen, chosen "to span open chat model scale" ([Atinafu and Cohen, 2026](https://arxiv.org/abs/2603.11337v1)). It is not a frontier coding-agent figure, and an attempt there is a patch proposed or applied, not a forged score.

## When this backfires

- The scorer lives in the repository the agent edits. Moving the environment does not move a test file in the agent's own checkout. The recommendation for that shape restricts access rather than relocating a process: "either hiding test files entirely or restricting them to read-only access during implementation, when feasible" ([Zhong and others, 2025](https://arxiv.org/abs/2510.20270v1)). [Per-attempt sandboxes](per-attempt-eval-sandboxes.md) covers the verifier-placement half.
- You put too much behind it. Hiding the tests "reduces cheating success rate to near zero", and the same sentence records that it "also degrades performance on the original benchmark", where read-only access "restores legitimate performance while preventing test modification attempts" ([Zhong and others, 2025](https://arxiv.org/abs/2510.20270v1)).
- You treat one boundary as the control. Evaluator locking drove tampering success to zero and left leakage "fully exploitable (success_train =1.0)"; only the combined regime closed both vectors ([Atinafu and Cohen, 2026](https://arxiv.org/abs/2603.11337v1)).
- The cheating is inside the submitted solution. Read-only tests "does not eliminate other cheating methods such as special-casing or operator overloading" ([Zhong and others, 2025](https://arxiv.org/abs/2510.20270v1)), and no process boundary sees those.
- Throughput is what binds. On the paper's two open-model backbones, evaluator-locking regimes cost "roughly +25-31% in our medians" under natural agents, against single-digit increases for the access-denial regime, and the authors name the trade: "stronger integrity guarantees reduce compromise but reduce throughput" ([Atinafu and Cohen, 2026](https://arxiv.org/abs/2603.11337v1)).
- A prompt would have been cheaper. One prompt change took GPT-5's cheating rate "from 92% to 1% on Conflicting-LiveCodeBench" ([Zhong and others, 2025](https://arxiv.org/abs/2510.20270v1)). A different intervention in the same paper, an option to abort, was "quite effective for OpenAI models" on Impossible-SWEbench and Conflicting-SWEbench, "lowering the cheating rate of GPT-5 from 54% to 9% and o3 from 49% to 12%", yet "much less pronounced for Claude Opus 4.1" ([Zhong and others, 2025](https://arxiv.org/abs/2510.20270v1)). Cheap levers move some models far and others barely, so measure yours before you build.
- The suite is small and nobody is attacking it. The Vercel setup wants sandboxes "with 4 vCPUs and 8 GB of memory for the builder and environment, plus 2 vCPUs and 4 GB for the agent", and "The first image build can take several minutes" ([Vercel, 2026](https://vercel.com/docs/sandbox/ecosystem/agentenv)).

## Example

The AgentEnv demo is three sandboxes, and it reports the verdict beside the trajectory. "The example creates a builder sandbox, an environment sandbox, and an agent sandbox. It loads an initial item, asks the agent to add `vercel-review-complete` through MCP, and grades the result" ([Vercel, 2026](https://vercel.com/docs/sandbox/ecosystem/agentenv)):

```bash
./vercel-eval --scope YOUR_TEAM --project YOUR_PROJECT
```

Replace `YOUR_TEAM` with a Vercel team slug and `YOUR_PROJECT` with an existing project name. The output directory carries `success.json` for "The score and cleanup checks", `trajectory.json` for "The agent's tool calls and results", and `environment-state.json` for "The initial item and the item the agent added". Successful runs remove all three sandboxes, while "Failed runs stop and retain sandboxes tracked by the runner for diagnosis" ([Vercel, 2026](https://vercel.com/docs/sandbox/ecosystem/agentenv)).

The demo bounds its own claim. Its agent is deterministic, it needs no model API key, and "The example verifies the integration; it doesn't measure model quality" ([Vercel, 2026](https://vercel.com/docs/sandbox/ecosystem/agentenv)).

## Key Takeaways

- The agent's only route to the environment is the tool call the harness grades, so a patch cannot reach the scorer while a read still can.
- In AgentEnv the boundary is two config keys, `default` and `agent_default`, both shipping as `local`, overridable per run with `--env-sandbox` and `--agent-sandbox`.
- Provider rows differ on whether they name a per-agent sandbox, so read the row before claiming a topology.
- One mechanism closes one vector. Evaluator locking stopped tampering and left train/test leakage fully exploitable.
- Price it at a 25-31% median runtime increase under natural agents on two open-model backbones, and try the prompt first.

## Related

- [Per-Attempt Sandboxes for Agents That Change the Filesystem](per-attempt-eval-sandboxes.md) — the verifier-placement half of this boundary, for agents whose output is workspace state
- [Rented Sandboxes for Coding-Agent Benchmark Runs](rented-benchmark-sandboxes.md) — what renting the sandbox buys, and which variables it leaves unpinned
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md) — the rubric-side control for the in-solution cheating no process boundary can see
- [Eval Environment Containment for Cyber-Capable Agents](eval-environment-containment.md) — the same split read as a safety control rather than a measurement control
