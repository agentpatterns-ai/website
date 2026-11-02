---
title: "Authority Disclaimers Read as Permission to Skip a Step"
term: "Authority Disclaimer Overreach"
description: "A harness note saying delegated task text carries no user authority can make the agent skip its step while the run still reports success."
tags:
  - anti-pattern
  - claude
  - agent-design
  - instructions
  - arxiv
aliases:
  - authority disclaimer overreach
  - no-user-authority note
  - provenance disclaimer over-refusal
last_reviewed: 2026-11-01
maturity: emerging
status: current
---

# Authority Disclaimers Read as Permission to Skip a Step

> An authority disclaimer in delegated task text can make an agent skip its step while the run still reports success.

This bites if your harness writes provenance into text it hands a delegated agent. Claude Code 2.1.301 lists it as a bug fix, for workflow agents specifically. "Fixed workflow agents sometimes skipping their step, and the run still reporting success, after reading the harness note that their task text carries no user authority" ([Claude Code changelog, 2.1.301, October 15, 2026](https://code.claude.com/docs/en/changelog)). One line. It names the trigger and both symptoms, and no rate.

## What the note is for

Keep it. The control shipped four months earlier in 2.1.166 (June 6, 2026), scoped to one clause: "messages relayed via `SendMessage` from other Claude sessions no longer carry user authority — receivers refuse relayed permission requests, and auto mode blocks them" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). Permission requests, not work. [Authority confusion](../../security/authority-confusion-untrusted-context.md) is the model that rule enforces.

The defect is what a shortened note leaves unsaid. "No user authority" names no capability. Nothing in it separates declining to merge from declining to read a file.

## Why it works

Two results from the instruction-hierarchy literature may explain why the skip repeats rather than firing at random. The instruction hierarchy ranks instruction sources. It teaches a model to discount the lower ones. The authors flag a risk: models may "learn to never follow lower-priority instructions" ([Wallace et al., arXiv:2404.13208v1](https://arxiv.org/abs/2404.13208v1)). They intended models to ignore only conflicting lower-priority instructions. Their regression report names the quiet half: "our models sometimes ignore or refuse benign queries".

A later ablation separates the two things a bare disclaimer runs together. Bolliger and Jäger remove the per-token level signal from a five-level hierarchy model. Conflict reasoning stays intact, while refusal changes by more than an order of magnitude. They report that "removing ISE changes conflict accuracy (macro PPA) by less than 0.05 but shifts the over-refusal rate from 0.024 to 0.576" ([arXiv:2606.10860v1](https://arxiv.org/abs/2606.10860v1)). Without it, they write, "the model can see that a span is delimited but cannot bind it to a level, and it compensates with a refuse-by-default heuristic on any structured prompt". My reading is that those two results make an unbound authority marker a refusal-threshold move rather than a scoping decision. The changelog reports the symptom pair, a skipped step and a reported success, but gives no mechanism.

## When this backfires

- The step should not run. A refusal can correctly block a merge, push, or outward post. Narrowing the note until every step runs defeats that control.
- Softening costs adversarial margin. On XSTest, unsafe-prompt refusal and safe-prompt compliance move in opposite directions across four five-level variants. Standard DPO records 0.990 refusal and 0.412 compliance. Bilateral GW-DPO records 0.910 refusal and 0.556 compliance ([arXiv:2606.10860v1](https://arxiv.org/abs/2606.10860v1)). Bolliger and Jäger add that the recipe "should not be deployed as a sole safety layer against motivated attackers".
- Wording moves the rate, not the visibility, and part of the bias is out of its reach. Absent a check that reads the artifact, a reworded note yields the same silent failure less often, which is harder to catch. Bolliger and Jäger see the same refusal pattern from that ablated model on MT-Bench "even though there are no delimiter tokens in the prompt to trigger the over-refusal heuristic", calling it "a property of the trained weights" ([arXiv:2606.10860v1](https://arxiv.org/abs/2606.10860v1)).

## Example

In 2.1.284, Claude Code changed `/recap` to decline under the same provenance predicate. The entry says it declines "with a short notice" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). It also says where the command still runs: "typed in the terminal, the Claude apps, Remote Control, `-p` or an SDK host, it runs as before" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

One release before 2.1.301, 2.1.300 exposed a lever for editing this text from outside the dispatching prompt. The entry reads: "Added support for rewriting a workflow agent's `prompt` and `model` in the `agent.spawn` mod hook, which could only refuse workflow agents before" ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

## Key Takeaways

- Keep the note. The defect is its silence: it withholds authority without naming a capability.
- Name what the note forbids and say the assignment still stands. 2.1.166 restricted permission requests; 2.1.301 fixed a skip that followed the note.
- Test the note. Dispatch the step with it in place and check the artifact rather than the report.
- The trigger evidence is one bug-fix line from one harness, about workflow agents. The same note goes into subagent dispatch and scheduled-task prompts, where the mechanism applies and nothing has measured the rate.

## Related

- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — the same symptom pair, triggered when the stop token fires on first progress
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](../../security/authority-confusion-untrusted-context.md) — the authority model this note enforces, and the account takeover that followed its absence
- [Post-Failure Evidence Contracts for Tool-Using Agents](../../verification/post-failure-evidence-contract.md) — the artifact-side half of the fix, with false-success rates measured under three report policies
- [Task Feasibility Awareness: Stop Before You Start](../agent-design/task-feasibility-awareness.md) — the opposite calibration error, where an agent fails to stop on work it cannot do
- [Stop-and-Report Instructions Need a Resuming Loop](../../instructions/stop-and-report-instruction.md) — a deliberate stop instruction, and what has to exist downstream for stopping early to pay
