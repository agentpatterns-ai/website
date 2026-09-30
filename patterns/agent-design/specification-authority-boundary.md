---
title: "Specification Authority Boundary: Agents Propose, the Runtime Commits"
term: "Specification Authority Boundary"
description: "Sort each requirement into blocking or advisory before you enforce anything, then let only validated evidence write the state that says a requirement is met."
aliases:
  - specification authority
  - state authority principle
  - obligation-evidence-commit
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-29
maturity: emerging
status: current
---

# Specification Authority Boundary: Agents Propose, the Runtime Commits

> An agent may propose actions and completion, but only validated evidence may write the specification state that decides whether it is done.

A specification authority boundary separates two jobs most agent loops merge: proposing work, and recording that a requirement is satisfied. The agent keeps planning, tool selection, code generation, and repair, and loses exactly one capability. Under the SpecHarness runtime the agent "cannot modify the ledger, inject validator outcomes, mark obligations satisfied, or authorize finalization" ([Li et al., arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)).

The failure it targets is measured. Across seven models on 87 SkillsBench tasks every valid run ended in a completion claim, and the held-out verifier rejected 28.7% to 37.9% of them. Agents satisfied only 79.6% to 86.4% of the 509 requirements extracted from their own prompts, workspace, and skill files ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)).

## Sort the specification before you enforce any of it

You cannot put a whole specification behind a gate, so you sort before you write a single rule. Each requirement in the agent-visible context gets one of four dispositions: `hard`, `advisory`, `abstain`, or `residual`. Only `hard` can block.

Four conditions decide it. A requirement enters the blocking set "only if it is mandatory, its parameters are source-grounded, it has an authorized evidence provider, and its validator is qualified for blocking under the development protocol; otherwise, it remains advisory or triggers abstention" ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)). Advisory requirements still reach the agent as guidance. They cannot stop it.

On the other side of the boundary the agent submits three kinds of proposal: actions with bound arguments, repairs targeting reported failures, and finalization requests. "Proposals express intent, not authoritative fact" ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)). That is the whole interface.

The authors bound what survives that sort rather than claiming general coverage: "These proportions bound our claim: SpecHarness governs the grounded, observable mandatory portion of the specification, not the full natural-language specification" ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)). Ambiguous and subjective requirements sit outside the boundary by construction.

## Two gaps need two controls

Constraining what an agent does and checking what it claims fix different defects. With one model fixed on SkillsBench, an adaptation of runtime action enforcement ([AgentSpec, arXiv:2503.18666v3](https://arxiv.org/abs/2503.18666v3)) cut the execution gap to 8.8% while the acceptance gap stayed at 24.1%. Completion gating reversed that: 9.6% execution, 20.7% acceptance. The combined runtime reached 6.3% and 6.9%. Those baselines are the paper's own adaptations, and it scopes the comparison to "the evaluated adaptations" ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)).

Screen only commands and unsupported claims of done still land; screen only the claim and execution still drifts.

## Why it works

The mechanism is a write restriction on state, not a smarter checker. A ledger entry may change only when admissible evidence from a bound provider witnesses the change, so "agent actions, outputs, and self-assessments cannot directly establish authoritative state" ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)). The authors place that in an old lineage: reference monitors, runtime verification, and transactional commit, "rather than treating them as new primitives" ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)).

The ablation isolates it. Removing commitment while keeping online validation and repair feedback pushed the acceptance gap from 6.9% to 25.3%, the largest degradation in the paper's architecture table ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)). Authority over the write, not more checking, is what moved the number.

Versioning keeps the write honest as work changes. Across 248 targeted dependency mutations, the variant without freshness invalidation accepted stale evidence every time: "Without invalidation, every mutation leaves outdated evidence admissible for completion" ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)).

## When this backfires

- Your requirements resist grounding. Subjective and unobservable ones stay advisory, so a spec of judgement calls yields a boundary governing almost nothing. 35 of 164 residual SkillsBench failures sat outside the hard-enforcement scope ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)).
- Your validators are the weak link. Validator error or unavailability caused 173 of 637 residual GuideBench failures, the largest bucket there ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)).
- You tune the gate on the acceptance number. Dropping blocking qualification scored a better acceptance gap (5.7% against 6.9%) while the pass rate fell from 85.1% to 79.3% and preservation of passing tasks fell to 90.3%. The authors read that as evidence that "conservative rejection is not equivalent to reliable authority" ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)).
- The sorting step is itself a model. The GPT-5.6 Sol candidate compiler matched 77 of 81 annotated directions (95.1% development coverage) on 14 development tasks ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)). A direction the compiler never extracts never becomes an obligation.
- The overhead is real. Against the ungoverned baseline the governed runtime averaged 1.53 times the task-agent tokens, 1.24 times the condition-execution time, and 0.36 extra task-agent calls per task ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)). Repair or interaction exhausted was the largest SkillsBench residual bucket at 51 of 164: the boundary turns a false completion into an unfinished task.

## Example

The paper's worked case is an array-processing action checked on path, shape, data type, and finite values. Instantiated as a skill file, one instruction splits across two dispositions.

**Before** — the whole instruction is context the agent reads and self-certifies:

```text
SKILL.md: write the cleaned array to out/features.npy as float32,
shape (N, 128), no NaN or inf values. Keep the code readable.
```

**After** — the checkable parts become blocking obligations, the rest stays advisory:

```text
hard      path=out/features.npy, dtype=float32, shape=(N,128), finite=True
            provider: filesystem observer + array validator
advisory  "keep the code readable"   (no qualified validator, cannot block)
```

Authorization and commitment happen at different moments. Authorizing it "confirms only its preconditions, arguments, and ordering constraints; the corresponding obligation state is committed only after an authorized validator verifies the required path, shape, data type, and finite values" ([arXiv:2609.29921v1](https://arxiv.org/abs/2609.29921v1)). An agent that edits the array afterwards invalidates the commit and must revalidate before it can finalize.

## Key Takeaways

- Run the sort before you build the gate. A requirement can block only when it is mandatory, source-grounded, backed by an authorized evidence provider, and paired with a qualified validator. Write down which of yours fail.
- Budget for partial coverage. The runtime relays advisory requirements to the agent as guidance but never blocks on them, so nothing enforces them. Route that remainder to human review.
- Screen commands and screen claims separately. Action enforcement alone left the acceptance gap at 24.1%; completion gating alone left the execution gap at 9.6%.
- Watch the preservation number, not the refusal rate. A gate can improve its acceptance metric by refusing more while breaking tasks that already passed.
- Price it first: roughly 1.5x tokens, 1.25x wall time, and more runs ending unfinished instead of falsely done.

## Related

- [Goal Contract: Separating the Doer from the Done-Checker](goal-contract-completion-evaluator.md) — moves completion judgement to a second model; this page extends the same split from the completion claim to every spec-governed state write.
- [Enforcement Modes in Spec-First Agent Frameworks](spec-first-framework-enforcement-modes.md) — sorts controls by whether the agent can edit them; the disposition sort here is the measured version of that argument.
- [Evidence-Gated Lifecycle Control for Coding Agents (Proof-or-Stop)](../../verification/evidence-gated-lifecycle-control.md) — specifies how a single receipt is admitted at a lifecycle transition; this page covers which requirements can sit behind a receipt at all.
- [Execution-State Ledger for Long-Horizon Coding Agents](execution-state-ledger-coding-agents.md) — the freshness index that marks an observation stale after a mutation, the same invalidation this boundary needs.
- [Deterministic Precondition Gates for Tool-Using Agents](deterministic-precondition-gates.md) — the deterministic checks a qualified validator is built from.
