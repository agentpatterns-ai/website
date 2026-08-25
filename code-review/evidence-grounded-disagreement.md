---
title: "Evidence-Grounded Disagreement in Agentic Code Review (Adversarial Review)"
term: "Adversarial Review"
description: "A reviewer-critic loop only beats a single reviewer once every objection must cite code — the naive form scored worse than one reviewer on real pull-request diffs."
tags:
  - code-review
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - adversarial review protocol
  - evidence-grounded disagreement
  - false consensus in agent review
last_reviewed: 2026-08-20
maturity: emerging
---

# Evidence-Grounded Disagreement in Agentic Code Review

> Two review agents told to converge tend to agree with each other; only requiring every objection to cite code makes the second reviewer worth it.

Adding a critic that audits the reviewer improves review quality only when the protocol forbids ungrounded agreement. Without that constraint the pair scored F1 0.457 on 100 real GitHub pull-request diffs, below a single reviewer at 0.495, two independent reviewers at 0.503, and the paper's MARS reviewer panel at 0.501. One prompt change, holding the agent count and wiring fixed, moved the same pair to 0.533 ([Qiu and Gill, 2026](https://arxiv.org/abs/2608.18167v1)). Treat the constraint as the pattern and the second agent as the delivery mechanism.

## The protocol

Three roles, two of which talk to each other. A main agent writes the artifact. A reviewer inspects it. A critic evaluates the reviewer's review, not the code. That exchange is what separates the protocol from a [committee of parallel reviewers](committee-review-pattern.md), where no reviewer sees another's output.

The artifact is frozen while the reviewer and critic argue. They exchange review text only; the main agent edits once the review stabilizes, then a fresh review round opens on the new version ([Qiu and Gill, 2026](https://arxiv.org/abs/2608.18167v1)).

The critic's output is constrained to three verdicts:

| Verdict | Meaning | What the reviewer must do next |
|---------|---------|-------------------------------|
| `AGREE` | Every flag is real and nothing is missing | Keep every flag unchanged |
| `DISAGREE_EVIDENCE: <code citation>` | Code visible in the diff contradicts a flag | Revise the flag against the cited code |
| `DISAGREE_CONCERN: <epistemic objection>` | The objection is a doubt with no code behind it | Cite code that confirms the bug and keep the flag, or cite code that refutes it and drop the flag |

The asymmetry in the last row is where the protocol earns its result.

## Why it works

Asked to agree on a joint output, two agents "tend to agree with each other. They do not always find the truth." The paper traces one such case: the critic raised a real bug, the reviewer rebutted with "a file-level argument yet cites no code", the critic yielded, and the verdict flipped to agreement with the bug dropped ([Qiu and Gill, 2026](https://arxiv.org/abs/2608.18167v1)). The authors call this false consensus; from outside it looks like independent validation.

The three-verdict grammar changes which move ends an exchange. Yielding is no longer available as a response to `DISAGREE_CONCERN`, so the cheapest exit becomes fetching a line of code. That converts disagreement into an object a later reader can audit.

The tendency is not specific to this protocol. An operational study of inter-agent sycophancy found it "amplifies disagreement collapse before reaching a correct conclusion in multi-agent debates, yields lower accuracy than single-agent baselines" ([Peacemaker or Troublemaker, 2025](https://arxiv.org/abs/2509.23055v1)).

## When this backfires

Speculation gets promoted. On the `astropy__astropy-14182` repair task a zero-shot agent's 24-line patch passed the hidden tests. The reviewer-critic pair produced a 32-line patch that added an unrequested method and removed a stable class variable, and failed. The reviewer raised a hypothetical about a separate call path, and the paper records: "The critic does not reject this as out of scope" ([Qiu and Gill, 2026](https://arxiv.org/abs/2608.18167v1)). Nothing in the verdict grammar checks scope.

Unconstrained, the loop also inflates the finding count. The reviewer hedged, the critic confirmed the hedges and added one more, and a judge marked 3 of 5 resulting comments as fabricated ([Qiu and Gill, 2026](https://arxiv.org/abs/2608.18167v1)).

Against that sits a real bill: about 4.5 times the tokens of a zero-shot run, buying a 75.2% pass rate against 71.6% on SWE-bench Verified ([Qiu and Gill, 2026](https://arxiv.org/abs/2608.18167v1)). On easy or narrowly scoped work the extra spend returns nothing.

The gain may not survive a different setup. A benchmark of debate protocols found that "multi-agent debating systems, in their current form, do not reliably outperform other proposed prompting strategies", and that they are "more sensitive to different hyperparameter settings and difficult to optimize" ([Smit et al., 2024](https://arxiv.org/abs/2311.17371v3)). A swing from 0.457 to 0.533 on a single prompt edit fits that description. The evidence is one workshop paper, one model family, and an LLM judge the authors note "may penalize valid comments that differ from the human review" ([Qiu and Gill, 2026](https://arxiv.org/abs/2608.18167v1)).

Nothing outside the prompt enforces the grammar. The authors concede that current models are "prone to forgetting or ignoring instructions, especially as the context window approaches full and past full" ([Qiu and Gill, 2026](https://arxiv.org/abs/2608.18167v1)).

## Example

The critic prompt's verdict block, which is the entire difference between the two measured configurations:

```text
End your response with EXACTLY ONE of these verdict lines:

AGREE
Use when every flag is real and you have nothing to add.

DISAGREE_EVIDENCE: <cite file:line or code snippet that contradicts the flag>
Use when you can ground your objection in code visible in the diff.

DISAGREE_CONCERN: <flag is plausible but not yet substantiated>
Use when your objection is epistemic (reviewer hedged, you have a gut
reaction, external attribution argument) but you cannot point to code
that refutes the flag. The reviewer's job on the next round is then to
firm up the flag with evidence or drop it.

Use DISAGREE_EVIDENCE when you have code grounding; DISAGREE_CONCERN when
you only have epistemic doubt. Do NOT use DISAGREE_CONCERN as a dismissal
mechanism -- use it to request evidence, not to suppress findings.
```

Source: [Qiu and Gill, 2026, Appendix A.2.4](https://arxiv.org/abs/2608.18167v1). The baseline configuration offered the critic two choices, agree or disagree.

The protocol also ran as a plain `SKILL.md` file that an autonomous agent followed with no orchestration code enforcing the steps, which is how it was measured on SWE-bench Verified ([Qiu and Gill, 2026](https://arxiv.org/abs/2608.18167v1)). Two round caps appear in the paper and they are not interchangeable: five inner rounds under the Python orchestrator, seven in the skill file before escalating to a human.

## Key Takeaways

- Copy the verdict grammar before copying the second agent; the agent count was constant across both measured configurations and only the prompt changed
- Make one verdict unsettleable by argument, so an unsupported objection can only be closed by fetching code
- Freeze the artifact while reviewers disagree, and edit only after the review stabilizes, so the agents cannot rewrite the solution mid-argument
- Add an explicit scope check, because the measured failure is the reviewer's hypothetical becoming a patch the issue never asked for
- Reserve the loop for complex repositories where root-cause localization outranks token cost; at roughly 4.5 times zero-shot spend it is wasted on easy tasks
- Audit the inner-loop transcript, since a converged verdict looks identical whether the agents checked the code or checked each other

## Related

- [Committee Review Pattern](committee-review-pattern.md) — parallel reviewers with no interaction, the baseline this protocol was measured against
- [Opponent Processor / Multi-Agent Debate](../patterns/multi-agent/opponent-processor-debate.md) — co-equal agents debating the artifact itself rather than the review of it
- [The Yes-Man Agent](../patterns/anti-patterns/yes-man-agent.md) — the same compliance bias pointed at a human instead of a peer agent
- [Reproduce-Before-Report Verification Gate](reproduce-before-report-verification-gate.md) — an alternative grounding mechanism that verifies findings by execution rather than citation
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — why the thin-findings failure mode costs more than it appears to
