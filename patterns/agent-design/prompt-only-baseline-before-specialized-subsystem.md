---
title: "Prompt-Only Baseline Before a Specialized Agent Subsystem"
term: "Prompt-Only Baseline"
description: "Before adopting a memory or self-improvement subsystem, measure a prompt-only agent loop that exposes its prompt and history as code variables. It beat a memory harness and a self-improvement harness at lower cost."
tags:
  - agent-design
  - tool-agnostic
  - pattern
  - arxiv
  - harness-engineering
aliases:
  - prompt-only baseline
  - bare agent loop baseline
  - minimal harness baseline
last_reviewed: 2026-09-24
maturity: emerging
---

# Prompt-Only Baseline Before a Specialized Agent Subsystem

> A prompt-only agent loop exposing its prompt and history as code variables beat a dedicated memory harness on far recall at under half the cost.

Run the bare loop as a controlled baseline before you adopt or build a memory or self-improvement subsystem. On the StuLife long-horizon benchmark, a prompt-only loop scored 72.6% pass against the Letta memory agent's 70.9%, and 69.9% against 61.8% on the 207 far-recall tasks. It spent $18.3 where Letta spent $42.1 ([Li et al., 2026, Table 1](https://arxiv.org/abs/2609.26891v1)). On AppWorld's 417-task test-challenge split it scored 74.2% task goal completion against the ACE self-improvement harness's 69.9%, at $20.9 against $30.6 ([Table 2](https://arxiv.org/abs/2609.26891v1)).

## The condition that makes the baseline strong

The result depends on one property of the loop rather than its size. In the JAZ framework the user prompt and REPL history are ordinary variables the model can reference: "Everything the language model sees is a variable that it can reference in its code" ([Li et al., 2026](https://arxiv.org/abs/2609.26891v1)).

The authors ablate exactly that property. A hook removes the prompt and history variables, and the same framework then runs a CodeAct-style loop. On the 207-task subset needing recall of information delivered over 50 tasks earlier, pass rate fell from 69.9% to 32.0% ([Table 1](https://arxiv.org/abs/2609.26891v1)). Letta scored 61.8% on the same subset. Removing the two variables turned an 8-point win over Letta into a 30-point loss.

Check your harness first. Two existing code-mode agents, smolagents and RLMs, "treat the user prompt and REPL history only as a list of messages shown to the agent, not as variables the agent can programmatically interact with" ([Li et al., 2026](https://arxiv.org/abs/2609.26891v1)).

## Running the baseline

Give the loop the same task sequence and model as the subsystem you are evaluating, then prompt it to do that subsystem's job. For recall, the agent was told to delegate to a subagent when its context filled and pass the accumulated history by reference. For self-improvement, the top-level agent dispatched batches to subagents, read the failure traces, and rewrote the prompts and skills it passed down.

Record cost alongside score, and price three arms: no recall, prompted recall, bought recall. The no-memory arm cost $4.4 on StuLife against the prompt-only loop's $18.3 ([Table 1](https://arxiv.org/abs/2609.26891v1)).

## Why it works

Delegation loses instructions when it copies text and keeps them when it passes a reference. When the history is a variable, the subagent receives a live object, and the paper reports that "every delegation preserves the full history completely through the prev_history" ([Li et al., 2026](https://arxiv.org/abs/2609.26891v1)). One run reached recursion depth 70 and still answered a final-exam question whose lecture had arrived 497 tasks earlier. The ablated loop had no such variable, so "without access to the user prompt as a variable in the REPL, every agent has to copy its user prompt into the subagent, which ended up being lossy, and both instructions were lost after dozens of delegations". Addressability is what carries the recall.

## When this backfires

Production practice runs the other way. A study of eleven production coding harnesses, source-diffed across one quarter, found "behavioral policy migrates from prompt prose to configuration" ([Barbaste et al., 2026](https://arxiv.org/abs/2609.00006v1)). Several conditions make the baseline the wrong bet:

- Every hard limit in these runs came from harness hooks rather than prompting: a return validator in both case studies, a recursion cap in the self-improvement runs, a context-window warning in the long-horizon ones ([Li et al., 2026](https://arxiv.org/abs/2609.26891v1)). A prompt can be ignored; a hook cannot.
- The published comparison was cost-capped. Running ACE online for every task carried "an estimated cost of over $180, nearly 10 times the total cost of JAZ invoke", so the authors froze its prompt after 42 of the 417 tasks ([Li et al., 2026](https://arxiv.org/abs/2609.26891v1)). ACE at full budget was never measured.
- Implementation quality swamps the paradigm. On StuLife the smolagents version of CodeAct+subagents scored 30.2% pass where the authors' reimplementation of the same method scored 60.0%, because "established implementations were found to perform worse than our reimplementation due to defects in prompting and REPL implementation" ([Table 1](https://arxiv.org/abs/2609.26891v1)). A baseline you build badly proves nothing.
- Letta lost a task that needed exact substring matching, where "the only tool Letta had (conversation_search) did not support it" ([Li et al., 2026](https://arxiv.org/abs/2609.26891v1)). If your workload fits the retrieval model the subsystem was built around, the argument drops away.

The self-improvement result also gave the meta-agent a stronger model (GPT-5.4) than the solvers (GPT-5.4 nano) ([Table 2](https://arxiv.org/abs/2609.26891v1)). Both results come from one paper on two benchmarks, never independently replicated.

## Key Takeaways

- Budget one baseline run before the procurement decision, on the same model and task sequence, and price all three arms.
- Test whether your harness exposes the prompt and history as addressable data first. Without it, the ablated numbers apply to you, and the baseline loses to Letta by 30 points on far recall.
- Keep the hooks even if the baseline wins. A return validator, a recursion cap, and a context-window warning all stayed in the prompt-only runs, because a prompt cannot enforce them.
- Treat a single-paper result against a budget-capped competitor as a reason to measure, not a reason to remove a working subsystem.

## Related

- [Harness-Memory Coupling as a Design Axis](harness-memory-coupling.md) — why memory belongs to the harness rather than a pluggable module
- [Isometric Harness Ablation](isometric-harness-ablation.md) — the remove-one-subsystem method that produced the evidence above
- [Recursive Agent Harnesses (RAH)](recursive-agent-harnesses.md) — what the recursive unit is when an agent spawns subagents
- [Evolving Playbooks: Incremental Context That Preserves Knowledge](../../context-engineering/evolving-playbooks.md) — the ACE self-improvement approach this baseline was measured against
- [Silent Handoff Failure in Delegated Code Search](../../context-engineering/silent-handoff-failure-delegated-search.md) — what a lossy parent-to-subagent handoff costs in practice
