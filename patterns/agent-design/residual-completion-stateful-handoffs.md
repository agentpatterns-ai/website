---
title: "Residual Completion for Stateful Agent Handoffs (CFRC)"
term: "Residual Completion"
description: "When a mid-task model switch leaves irreversible effects behind, freeze a contract from the accepted progress and let the successor finish only the remainder instead of restarting."
tags:
  - agent-design
  - cost-performance
  - reliability
  - tool-agnostic
  - arxiv
aliases:
  - commitment-frontier residual completion
  - commitment-constrained residual completion
  - residual contract handoff
last_reviewed: 2026-09-17
maturity: emerging
---

# Residual Completion for Stateful Agent Handoffs (CFRC)

> Freeze what the predecessor already committed, then let the successor complete only the residual rather than restarting into duplicate effects.

Before switching models mid-task, ask whether you can replay the predecessor's effects for free. Where progress lives in a working tree, replay costs one more cheap run and restarting wins. Where the predecessor has already charged a card, sent a message, or mutated a shared record, a restart repeats that effect and the switch stops being a cost trade-off at all. Commitment-Frontier Residual Completion (CFRC) is the protocol for that second case. It derives a frozen contract from the accepted trajectory and admits the successor to finish only what remains ([Deng et al., arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)).

## When this applies, and when the opposite does

The boundary is measured, not assumed. On SWE-bench Verified, where every effect sits in the working tree, handing a strong model the cheap model's trajectory "recovers less than half of HC's quality advantage in both model families", and on the Claude pair a clean restart beat it outright: "even after paying for the LC prefix, abandoning the attempt and restarting with HC is cheaper and more accurate than Raw continuation" ([Ganz et al., arXiv:2608.24358v1](https://arxiv.org/abs/2608.24358v1)). Read the restart result as specific to the Claude pair, and the weak recovery as holding in both families tested. [The Handoff Tax: What a Receiving Model Should Inherit](../../context-engineering/handoff-tax-model-switch-context.md) carries the per-interface numbers and covers what the receiver should get when you do switch.

CFRC's five surfaces sit on the other side of that line. They include transactional environments where a tool call moves state a rerun cannot take back, and the paper states the constraint directly. Agents "operate in persistent environments where actions can produce irreversible side effects. Restarting wastes computation and risks duplicate actions, while continuing without clear specifications risks goal drift" ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)).

## The three invariants

CFRC orders three checks, and the order carries the guarantee.

| Invariant | What it requires | What it prevents |
|---|---|---|
| Target before proposal | Derive the residual contract from the accepted trajectory, reached state, and trusted receipts, before seeing the successor's plan | Open work vanishing because the successor never mentioned it |
| Whole proposal before authority | Close the successor's entire remainder into an evidence-linked graph and check that it covers the contract before the first state-changing call | Partial execution committing destructively to an incomplete plan |
| Live evidence before success | Discharge each obligation against a receipt from a live call, because replica results are "only proposal-time evidence" | Reporting a completion the environment never recorded |

The frozen contract holds five things: receipt-backed effects that later actions must preserve, verified values the remainder may reference, open obligations, admissible residual effects, and permitted tool interfaces ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)).

## Why it works

Freezing the target first turns a silent omission into a visible coverage failure. Step-by-step checking "can reject an invalid action but cannot detect an obligation for which no action is proposed", so a successor that forgets the receipt delivery passes every per-call check on its way to declaring success ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)). The contract makes the obligation exist independently of what the model says.

The paper isolates the second invariant by holding the contract fixed and varying only the gate. Against the same frozen contract, admitting the whole graph before any write rather than checking call by call "adds 8.8 points and saves $8.26 over step-by-step checking under the same contract by preventing destructive partial execution" ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)).

Build order follows from that ablation. Freezing a contract alone, with ordinary incremental checking left behind it, moved a five-surface macro score from 58.9% to 62.1% and cut spend from $68.82 to $47.06. The full protocol reached 70.8% at $38.80. Contract construction averaged $0.21 against a $7.76 mean total, so the first step is cheap enough to try before committing to the graph machinery. A large share of the saving is plainer than the contract, though: the strong model engages on only 59.6% of episodes on macro average, and on 20.0% of the retail surface ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)).

## Example

The paper's running case is an invoice task. The user asks the agent to pay one outstanding invoice and send its receipt. By the handoff point, invoice INV-42 has been selected, confirmed by the user, and paid; the receipt file exists; delivery has not happened.

Every obvious move is wrong. "The successor cannot restart, as another API payment call would cause a duplicate charge, nor switch invoices, since the user confirmed INV-42. Yet declaring success is also wrong because delivery remains unfulfilled" ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)).

The contract encodes the paid invoice as a preserved effect, INV-42 as a fixed binding, and delivery plus its verification as open obligations. The successor proposes a send call and a status query, and the query's argument binds to the send receipt's field rather than to a value guessed at proposal time. Only the live send receipt closes the obligation.

## When this backfires

- Progress is replayable. Effects that live in a working tree or a scratch branch put you in the handoff-tax regime, where trajectory continuation recovered under half the strong model's quality advantage ([arXiv:2608.24358v1](https://arxiv.org/abs/2608.24358v1)).
- The cheap prefix is weak. The Haiku 4.5 and Sol pairing "trails Sol by 5.0 points at 57.4% cost, indicating that downstream completion remains sensitive to cheap-prefix fidelity" ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)). Over half the cost for worse accuracy is not a saving.
- Obligations are agreed in conversation rather than through tool schemas. The authors mark this as the limit of the guarantee: the formal lift to the residual task "remains conditional on complete RSCC construction, as conversational disclosures fall outside tool-effect schemas" ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)).
- Contract construction misses an obligation. An audit recovered 62 of 68 persistent write obligations, 91.2% recall. The six misses "involved implicit updates without entity mentions"; four were blocked downstream and two produced false completions ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)).
- A live write has already failed in this tenure. "Once a state-changing live call has occurred, however, a failure or mismatched receipt ends the current tenure; CE does not repair the old graph or continue under stale contract evidence" ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)).
- Your routing is recursive or multi-tier. The evaluation covers "single-tenure cheap-to-strong handoffs under frozen contracts", and the authors place recursive routing policies outside their scope ([arXiv:2609.13800v2](https://arxiv.org/abs/2609.13800v2)).

## Key Takeaways

- Decide by reversibility, not by cost. Replayable progress argues for a restart; effects you cannot take back argue for a residual contract.
- Derive the contract before you see the successor's plan. A target read out of the plan cannot catch work the plan never mentions.
- Gate the first write on whole-graph coverage instead of per call. That change alone was worth 8.8 points and $8.26 against the same contract.
- Start with the contract and keep incremental checking behind it. That step moved the macro score 3.2 points and cut spend by $21.76, for $0.21 of construction cost.
- Treat 91.2% obligation recall as the number to beat locally. The two false completions in the audited sample came from obligations the contract never encoded.

## Related

- [The Handoff Tax: What a Receiving Model Should Inherit](../../context-engineering/handoff-tax-model-switch-context.md) — the opposite finding on replayable coding work, and the reason this page leads with a condition
- [Trajectory-Conditioned Model Escalation (SWE-Router)](trajectory-conditioned-model-escalation.md) — decides when to hand over; this page decides what the receiver owes once you do
- [Within-Task Model Cascade: Designing the Escalation Gate](../../loop-engineering/within-task-model-cascade.md) — the gate that triggers the switch, upstream of the contract
- [Idempotent Agent Operations: Safe to Retry](idempotent-agent-operations.md) — the design that makes a restart safe, and so makes this protocol unnecessary
- [Continuation Authority in Agent Migration](continuation-authority-agent-migration.md) — who may act as the successor, where this page covers what the successor still owes
