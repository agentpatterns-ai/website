---
title: "Schema-Checked Rule Extraction for Tool-Call Gates"
term: "Schema-Checked Rule Extraction"
description: "Check each LLM-extracted tool-call rule against your tool schemas before the gate enforces it. Self-blocking rules look like working controls until then."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - static rule verification
  - tool-schema rule checks
  - verified policy compilation
last_reviewed: 2026-10-09
maturity: emerging
---

# Schema-Checked Rule Extraction for Tool-Call Gates

> Check each LLM-extracted tool-call rule against your tool schemas before enforcing it, because some extracted rules cannot run.

Schema-checked rule extraction is a verification step between an LLM that turns policy prose into deterministic rules and the gate that enforces them. It applies when a model writes the rules. It reads only each candidate rule, the tool schemas, and a table of the predicate vocabulary, so it needs no prover, solver, or model call. The evidence is one preprint on two τ²-bench domains for the compiled rule sets and task success, plus AgentDojo suites for injection, with no replication yet ([NOMOS, arXiv 2610.11030v1](https://arxiv.org/abs/2610.11030v1)).

## When this applies

- A model, not a person, writes the rules from prose. A team that hand-writes a short rule set (the paper's references hold 16 airline and 11 retail rules) for a stable policy skips the extraction step that creates these defects. In the paper, a compiled set was not significantly worse than a 16-rule hand-written reference, though the authors say equivalence is not established ([NOMOS](https://arxiv.org/abs/2610.11030v1)).
- Your tools return structured output. The gate keeps a fact store from tool results, and the authors note that free-text-only tools would weaken it ([NOMOS](https://arxiv.org/abs/2610.11030v1)).
- You can write the predicate tables. The checks need two static tables of the predicate vocabulary, so a team with one policy pays that setup cost for one domain ([NOMOS](https://arxiv.org/abs/2610.11030v1)).
- The policy contains clauses that become predicates. Clauses that stay judgment calls never become rules, so no structural check reaches them.

## The defect

The extractor reads a clause and does not model which tool satisfies which precondition. NOMOS reports what that produces. In its raw output, the clause "authenticate the user before any action" became a rule that blocked every tool while the user was unauthenticated, including the two lookup tools that perform authentication. No conversation can recover from that deadlock ([NOMOS, Section 3.3](https://arxiv.org/abs/2610.11030v1)).

In a separate airline compilation, a confirmation requirement was bound to eight read-only tools, so checking a flight status would have demanded user approval. Other candidates read arguments their target tools do not accept ([NOMOS, Section 3.3](https://arxiv.org/abs/2610.11030v1)). None of these defects names a tool the domain lacks. The paper reports no hallucinated tool references, so the failure sits at the boundary between policy text and tool API.

## The checks

The Resolve pass checks every candidate rule for five classes of defect ([NOMOS, Section 1](https://arxiv.org/abs/2610.11030v1)):

- Self-blocking reachability: the rule blocks the tool that would satisfy its own precondition.
- Argument-signature consistency: the rule reads an argument its target tool does not accept.
- Domain satisfiability.
- State contradictions.
- Write-scope correctness.

It repairs or rejects defective candidates. The paper adds majority voting over repeated extraction samples to stabilize the output. For the gate that enforces the surviving rules, see [deterministic precondition gates](deterministic-precondition-gates.md). For commit-time checks on a policy file a person wrote, see [policy file validation](../../instructions/policy-file-validation.md).

## What the evidence shows

Verification repaired or rejected 36.7% of raw airline candidates and 13.2% of raw retail candidates as structural defects. Only 10 of 79 airline candidates and 5 of 53 retail candidates survived to enforcement ([NOMOS, Section 3.3](https://arxiv.org/abs/2610.11030v1)).

The ablation carries the argument. With no verification, the airline compilation ships 14 rules and 8 cannot function. The retail compilation ships 5 rules and 3 cannot function. In both domains a majority of the emitted rule set is inoperable, and in retail one rule deadlocks every conversation ([NOMOS, Section 5.5](https://arxiv.org/abs/2610.11030v1)). The ablation runs over one frozen candidate pool per domain.

The full gate then cut violations of the reference-encoded policy clauses among state-changing calls from 66.3% to 2.6% on airline (234/353 to 3/116) and from 30.8% to 6.9% on retail (188/611 to 40/582), with a gemma-4-26B agent. Those rates cover only the clauses the reference set encodes ([NOMOS](https://arxiv.org/abs/2610.11030v1)).

Task success moved less. Airline pass^1 rose from 39.2% to 47.6%, with a confidence interval from -1.2 to +18.0 points. Retail pass^1 fell from 52.4% to 50.2%, with an interval from -7.9 to +3.5. Neither pass^1 change is significant ([NOMOS, Section 5.2](https://arxiv.org/abs/2610.11030v1)). Airline pass^2 to pass^4 did rise significantly (pass^2 +13.2, CI [+2.6, +24.0]). The authors write that when violations do not corrupt scored state, the task-success benefit disappears while the safety benefit remains.

## Why it works

An extractor reads policy text and never sees the tool graph, so its mistakes are mismatches between a rule and the tool API. Those mismatches are properties of two inputs, the rule and the tool schemas. A lookup over those inputs finds them. The paper states that every structural class it observed in its two benchmark compilations needs only the candidate rule, the tool schemas, and two static tables of the predicate vocabulary ([NOMOS, Section 1](https://arxiv.org/abs/2610.11030v1)). The check runs at load time, so a deadlocked rule is rejected before any conversation hits it.

FORGE reaches a similar class of defect by another route. It uses Datalog policies with static analyses for contradiction, redundancy, subsumption, and conditional reachability ([FORGE, arXiv 2602.16708](https://arxiv.org/abs/2602.16708)).

## When this backfires

- Cross-rule deadlock passes. The checks run per rule. The paper builds a two-rule file from its shipped predicate vocabulary that deadlocks and loads without complaint, so verification guarantees the absence of the enumerated per-rule defects, not deadlock freedom for the file ([NOMOS](https://arxiv.org/abs/2610.11030v1)). Test the whole file against a full conversation as well.
- Behavioral defects pass. A rule can be sound in shape and wrong about the world. The paper adds a separate step that replays rules over recorded transcripts, and it flagged one binding on its development domain and none on either evaluation domain ([NOMOS](https://arxiv.org/abs/2610.11030v1)).
- Missed clauses fail silently. The authors state that a clause the compiler misses is silently unenforced, which is why they measure compliance with an independent checker ([NOMOS, Limitations](https://arxiv.org/abs/2610.11030v1)). The compiled sets refuse 97.4% (airline) and 80.5% (retail) of the baseline calls the reference sets refuse.
- Judgment-heavy policies gain little. Those clauses never become predicates. An LLM verifier that reads the dialogue covers them, at a mean wall-clock cost of 74% over the gated run in the authors' reimplementation of PolicyGuard ([NOMOS, Section 5.7](https://arxiv.org/abs/2610.11030v1)).
- The headline safety numbers rest on the authors' own violation checker. Before disagreements were resolved, it agreed with an independent frontier judge at 50.0% (kappa -0.01) against the full policy ([NOMOS, Section 4](https://arxiv.org/abs/2610.11030v1)).
- The evidence is thin. The paper is a v1 preprint submitted on 8 October 2026 with two τ²-bench domains for the compiled rule sets and task success, plus AgentDojo suites for injection, and no independent replication.

## Key Takeaways

- Run the five checks on every extracted rule before enforcement; with all checks removed (the paper's naive coupling), 8 of 14 airline rules and 3 of 5 retail rules in the paper's ablation could not function.
- The checks need the rule, the tool schemas, and a predicate table. They call no prover, solver, or model.
- A clean pass rules out the enumerated per-rule defects only; test the whole rule file for cross-rule deadlock yourself.
- Report task success next to violation rates: retail showed no significant gain in task success.
- Skip the pattern when you hand-write a short policy, or when most clauses are judgment calls.

## Related

- [Deterministic Precondition Gates for Tool-Using Agents](deterministic-precondition-gates.md)
- [Informed Abstention as a Tool-Boundary Runtime Gate](informed-abstention-tool-boundary-gate.md)
- [Policy File Validation](../../instructions/policy-file-validation.md)
- [Specification Authority Boundary](specification-authority-boundary.md)
- [Learning Execution Guardrails from Agent Failure Traces](trace-learned-execution-guardrails.md)
