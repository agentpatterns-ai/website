---
title: "Generated Programs as Web Agent Action Space"
term: "Code-Emitting Web Agent"
description: "Let the web agent write and run a program instead of predicting one click at a time. It pays past three gates, and it gives up the injection boundary that plan-then-execute buys."
aliases:
  - code-emitting web agent
  - code-as-action web agent
  - terminal-native web agent
tags:
  - agent-design
  - security
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-18
maturity: emerging
---

# Generated Programs as Web Agent Action Space

> The agent writes and runs a program against the browser, so the durable artifact is code in a workspace rather than a browser session.

Give the agent a terminal and let it write Playwright code, and the browser becomes disposable while the workspace persists. Microsoft Research's Webwright harness is built this way: the agent "emits bash commands and controls the browser by writing Playwright code", and "the persistent artifact is not the browser session, but the code and logs in the local workspace" ([Microsoft Research](https://www.microsoft.com/en-us/research/articles/webwright-a-terminal-is-all-you-need-for-web-agents/)). With GPT-5.4 it reports 60.1% on the Odysseys long-horizon benchmark against a 33.5% base for the same model. That gain is conditional, so start with the conditions.

## Three gates before you adopt it

### The model has to emit runnable code

A code action space beats text and JSON formats when the model writes code correctly. CodeAct measures "up to a 20% absolute improvement over baselines on the success rate" while requiring "up to 30% fewer actions", with gains that "widen as the capabilities of the LLMs increase" and for one model none at all: "Surprisingly, no improvement is observed for the Llama-2 variant" ([Wang et al., arXiv:2402.01030v4](https://arxiv.org/abs/2402.01030v4)). An independent harness study found three of fourteen models emitted literal `\n` escape sequences instead of newlines, so their scripts died on a syntax error ([Patel et al., arXiv:2608.06370v1](https://arxiv.org/abs/2608.06370v1)). Measure emit-validity on the model you run, then keep the result as a [per-model harness setting](per-model-harness-tuning.md).

### The task has to be long enough to amortize the loop

The headline result is measured on Odysseys, 200 long-horizon tasks run on the live internet, where "the strongest models achieved a success rate of 44.5%" ([Jang et al., arXiv:2604.24964v1](https://arxiv.org/abs/2604.24964v1)). Webwright's runs there average 76.1 steps, and on the shorter Online-Mind2Web set it averages "$2.37 per task" with GPT-5.4 ([Microsoft Research](https://www.microsoft.com/en-us/research/articles/webwright-a-terminal-is-all-you-need-for-web-agents/)). A three-action sequence never recovers the turns spent authoring, running, and repairing a script.

### Containment is yours to build

CodeAct's own authors flag the risk: such an agent "may potentially break free of the sandbox restriction and cause harm to the world through cyber-attack, highlighting the need for future work to design better safety mechanism" ([arXiv:2402.01030v4](https://arxiv.org/abs/2402.01030v4)). The [Webwright repository](https://github.com/microsoft/Webwright) documents credential handling for model API keys and says nothing about sandboxing the code it generates. Generated code plus a logged-in browser session is arbitrary code execution holding the user's credentials, the [lethal trifecta](../../security/lethal-trifecta-threat-model.md) condition.

## Harness decisions

Past those gates, four choices define the harness, and Webwright's public implementation makes each one visible ([Microsoft Research](https://www.microsoft.com/en-us/research/articles/webwright-a-terminal-is-all-you-need-for-web-agents/)).

- State lives in the workspace. The browser is "something the agent can launch, inspect, and discard while developing a program", while "intermediate code, logs, screenshots, and results" go to a local folder.
- The action vocabulary is bash plus Playwright rather than a fixed tool enum, letting the agent "naturally chain many web interactions within a single step, and spawn multiple browser sessions".
- Completion is established rather than claimed. Against a premature "done", the agent must "generate a self-reflection config, run a final script in a fresh folder with logs and screenshots, and pass its own self-reflection judgement".
- Context is bounded on a fixed interval, compacting "history every 20 steps into a single summary".

None of that needs a large harness. Webwright is a Runner, a Model Endpoint, and a terminal Environment in roughly 1K lines, with "no multi-agent orchestration".

## Why it works

A program collapses re-decision points. Control flow that a step-wise agent re-derives from a fresh observation at every action, such as loops, retries, and conditionals, is written once and executed by the runtime. CodeAct measures that directly: gpt-4-1106-preview gained "a 20.7% absolute improvement compared to the next best action format (text) while requiring 2.1 fewer interaction turns on average" ([Wang et al., arXiv:2402.01030v4](https://arxiv.org/abs/2402.01030v4)). Fewer model-mediated steps means fewer places for a long trajectory to diverge, and less accumulated observation in the context window.

The other cause is where the state lives. Because the durable artifact lives in the workspace as code and logs ([Microsoft Research](https://www.microsoft.com/en-us/research/articles/webwright-a-terminal-is-all-you-need-for-web-agents/)), a failed run leaves an inspectable script to repair instead of an unrecoverable trajectory. Attribution is partly inferential: the 26.6-point Odysseys delta is a whole-harness comparison, not an ablation isolating either cause.

## When this backfires

- The model cannot reliably produce runnable code. There was no CodeAct gain for the Llama-2 variant ([arXiv:2402.01030v4](https://arxiv.org/abs/2402.01030v4)), and three of fourteen models in an independent study produced scripts that did not parse ([arXiv:2608.06370v1](https://arxiv.org/abs/2608.06370v1)).
- The plan must be fixed before untrusted content is read. Plan-then-execute earns its security property because untrusted data "may influence values or branches inside a predefined execution graph, but it cannot redefine the user task or cause the model to synthesize new actions at runtime" ([Piet et al., arXiv:2605.14290v1](https://arxiv.org/abs/2605.14290v1)). A write-execute-inspect-repair loop reads the page and then authors the next program, making runtime action synthesis its mechanism — precisely what that guarantee excludes. Emitting code buys that boundary only if you commit to the program before any page is fetched, which this pattern by construction does not.
- Nobody owns script maintenance. Microsoft names the limitation: "A script index is only as useful as it is current", with open work on "validating scripts before reuse, detecting silent failures, and updating or retiring ones that no longer work" ([Microsoft Research](https://www.microsoft.com/en-us/research/articles/webwright-a-terminal-is-all-you-need-for-web-agents/)). Reuse is the headline benefit and it decays silently as sites change.
- The page encodes its state visually. Webwright still ships an `image_qa` tool ([microsoft/Webwright](https://github.com/microsoft/Webwright)) and lets the agent "freely decide when to capture screenshots" ([Microsoft Research](https://www.microsoft.com/en-us/research/articles/webwright-a-terminal-is-all-you-need-for-web-agents/)), because code alone cannot read a canvas.
- The task is already fixed. Where control flow does not depend on what the page returns, skip both action spaces and write the script yourself, as [Browser as Agent Action Space](browser-as-agent-action-space.md) argues from the same measurement.

## Example

The Webwright repository documents its loop as one line, and the shape is the pattern ([microsoft/Webwright](https://github.com/microsoft/Webwright)):

```text
write code → execute → inspect screenshots → repair (code-as-action)
```

The completion step stops that loop exiting on an unverified claim. Rather than let the model report success from its own trajectory, the harness requires a fresh run ([Microsoft Research](https://www.microsoft.com/en-us/research/articles/webwright-a-terminal-is-all-you-need-for-web-agents/)):

```text
generate self-reflection config
  → run final script in a fresh folder
  → capture logs and screenshots
  → pass self-reflection judgement
```

Running the final script in a fresh folder is the load-bearing detail. A script that only works against residue left by earlier exploratory runs fails there, which is the difference between a task completed once and a program that runs again.

## Key Takeaways

- Gate on emit-validity per model before adopting the pattern, because the code action space assumes a skill three of fourteen measured models lacked.
- The economics are long-horizon. Published gains come from 76-step tasks at roughly $2.37 each, so short automation pays the authoring cost without recovering it.
- Design the workspace; the browser session is disposable. Durable code and logs are what make a failed run repairable.
- Require a fresh-folder verification run before the agent may claim completion; self-reported success from the working trajectory hides state the script depends on.
- Code actions and a committed plan are different security postures. Only a plan fixed before any page is read stops untrusted content from shaping the actions the agent synthesizes.

## Related

- [Browser as Agent Action Space](browser-as-agent-action-space.md) — the other branch of the same fork, covering the driven-browser loop this pattern replaces.
- [Tools as Typed Code Stubs (Programmatic Tool Calling)](programmatic-tool-calling.md) — code as an action space inside a single turn, with the model-capability gates measured across 14 models.
- [Lethal Trifecta Threat Model](../../security/lethal-trifecta-threat-model.md) — why generated code, a logged-in session, and egress in one principal is the condition to avoid.
- [Restrict the Coding Agent to Executing Code](../../tool-engineering/restrict-coding-agent-to-execute-code.md) — the containment posture this pattern assumes but does not supply.
- [Per-Model Harness Tuning](per-model-harness-tuning.md) — where a measured emit-validity result belongs once you have it.
