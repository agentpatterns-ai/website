---
title: "Leave-One-Out Permission Testing for Agent Rule Files"
term: "Leave-One-Out Permission Testing"
description: "Remove one permission an agent instruction file asks for, re-run the task against your own tests, and record whether it still passes."
aliases:
  - permission-minimality testing
  - dispensability witness
  - permission ablation test
tags:
  - security
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-02
maturity: emerging
---

# Leave-One-Out Permission Testing for Agent Rule Files

> Withhold one permission an instruction file asks for, re-run the task against tests you wrote, and see whether it still passes.

Leave-one-out permission testing audits an agent instruction file by removing a single requested permission and re-running the unchanged file and task in a sandbox that denies it. When the restricted run still passes independently written tests, the task did not need that authority. Aletheia calls that result a dispensability witness, and nothing more: "These witnesses establish task-relative dispensability, rather than malicious intent or a globally minimum policy" ([arXiv:2609.39678v1](https://arxiv.org/abs/2609.39678v1)).

## Four conditions decide whether the test says anything

- Write the tests yourself. The instruction file is the untrusted input and cannot define what passing means: "Acceptance must come from trusted tests, since an attacker can claim that unwanted operations are mandatory." A rule gains nothing by calling its upload step a prerequisite, because "The rule's own claim of necessity is not trusted authorization" ([arXiv:2609.39678v1](https://arxiv.org/abs/2609.39678v1)).
- Cover the obligation the permission serves. A witness holds only for the task you ran: "refactoring tests cannot establish whether publishing is unnecessary for a release."
- Reset both runs to the same starting state, or the experiment moves two variables at once. Fix the fixtures before the branches split, because "deleting an archive-read grant might also remove the archive, changing both resource availability and authority."
- Confirm the removal removed something. Grants overlap, so "deleting a file grant is ineffective if another covers its directory". Aletheia found 26 ineffective deletions among 1,112 prepared configurations, and its witness condition rejects them by requiring a strict reduction in compiled authority ([arXiv:2609.39678v1](https://arxiv.org/abs/2609.39678v1)).

## Running the experiment

List the authority the file asks for as separate grants: each path, each tool, each endpoint. Run the task once with all of them granted, then run one branch per grant, each granted everything except that one. Every branch carries the original file and the original task, and the removals do not stack: "the complete schedule uses |P|+1 executions; deletions never accumulate." A grant whose branch passes the tests, and whose compiled policy is strictly narrower, is dispensable for that task.

Acting on a witness is a separate decision. Because "two individually removable permissions may substitute for each other", deleting every grant the test marked dispensable can break the task even though each passed alone. Treat the output as a list of grants to ask about.

## Why it works

Neither half of the usual evidence discriminates. The agent can produce a correct patch and perform the attacker's operation on the way, so "Functional correctness alone therefore does not reveal the attack". File access and network access support ordinary development too, so the grants do not discriminate either. Hold the file, the task, the tests, the bindings and the starting state fixed, change exactly one grant, and the gap between the two outcomes belongs to that grant. That differential needs no vocabulary of attacks: "The comparison requires no recognition of particular payload wording" ([arXiv:2609.39678v1](https://arxiv.org/abs/2609.39678v1)). Pattern matching on rule text cannot make that claim, which is the argument for paying the execution cost.

## When this backfires

- The attack rides authority the task already needs. Withholding it fails the tests, the request reads as necessary, and the test flags nothing: "attacks that misuse already-required authority may yield no witness." A rule that exfiltrates through a dependency fetch your build already performs stays invisible.
- Dispensable work is often legitimate. "A legitimate optional operation can also be dispensable" covers a formatter, a cache warm-up, a notification hook. Aletheia raised three false positives across 80 benign rules (3.75%), on a corpus the paper says cannot support a rate: "Five templates and this development set do not establish a population false-positive rate."
- One run per branch, against a stochastic agent. The paper concedes "Model and service responses may still differ." A study of 584 coding-agent runs reports that "Identical runs of one pairing varied more than the pairings differed from one another, so comparisons of a few runs ranked them unreliably" ([arXiv:2609.33812v1](https://arxiv.org/abs/2609.33812v1)). A flaky pass becomes a dispensability claim unless you repeat each branch.
- The cheap version may reach the same answers. Aletheia's own development comparison found that an LLM reading the rule against the task context, with no sandbox and no extra runs, produced the same file-level alarms: "Execution therefore supplies tested authority-removal evidence without an established classification gain." Translation plus sandboxed execution cost a median of 44.35 seconds and US$0.22 per input, excluding the task-context interpretation step.
- Detection is a losing frame for the general problem: "an adversary can always construct a context under which a blocked flow appears legitimate, or a defender who tightens norms will block genuinely legitimate flows" ([arXiv:2605.17634v1](https://arxiv.org/abs/2605.17634v1)). Keep a [default-deny egress policy](agent-network-egress-policy.md) and a [sandbox boundary](dual-boundary-sandboxing.md) in place whatever the audit returns.

The paper demonstrates the test only through its own typed permission language, dependency-aware synthesis, and a namespaces-and-seccomp backend, on one shared refactoring task across all inputs. A hand-run experiment keeps the principle. It does not inherit the reported detection numbers.

## Example

Aletheia's running example renames `calculateTotal` to `calculate_total`, with tests that "check the new interface and totals of 35 for a fixed cart and 31.5 after a 10% discount" ([arXiv:2609.39678v1](https://arxiv.org/abs/2609.39678v1)). The rule also asks to send `artifact.tar` to a remote host over `scp`, which translates to three grants: read the archive, execute `scp`, connect to the endpoint.

The baseline branch gets all three and passes. Three restricted branches run next, one per grant. In the endpoint branch the gate denies the connection, the agent carries on, and the rename still passes the tests. No remaining grant covers that destination, so the report links three things: the upload instruction, the authority the branch removed, and the records that passed without it. The rename landing in both branches is what makes the comparison readable: the agent did the job either way.

## Key Takeaways

- The transferable idea is one experiment. Remove a grant, re-run the task against tests you wrote, record the outcome. Everything else in the paper is its implementation.
- Take a witness to the rule's author as a question about one grant, not to an incident channel as a finding. Two grants can each pass alone and still be needed together.
- Four conditions carry the result: independent tests, tests that cover the real obligation, a reset starting state, and a removal that narrows compiled authority.
- Aletheia detected all 314 attack inputs it ran and raised three false positives (3.75%) on 80 benign rules, a set the paper says cannot support a population rate. Its own comparison found no classification gain over reading the rule against task context. Treat the median 44.35 seconds and US$0.22 per input as the cost of the evidence. That figure covers translation and sandbox execution only and excludes the task-context interpretation step.
- The test is blind to an attack that uses authority the task already requires, so keep enforcement underneath it.

## Related

- [Sufficiency-Tightness Decomposition for Agent-Authored Permissions](sufficiency-tightness-policy-decomposition.md) — the other direction: generating a least-privilege policy in two passes rather than testing one that already exists.
- [Transcript-Driven Permission Allowlist](transcript-driven-permission-allowlist.md) — promote permissions from observed runtime traces, which answers a different question than withholding one.
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md) — why the task definition, not the rule file, decides what counts as in-scope authority.
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — the least-privilege goal this test gathers evidence for.
- [Judging Agent Safety by Task Completion (Action-Boundary Violations)](../patterns/anti-patterns/judging-agent-safety-by-task-completion.md) — the matching failure: a completed task is not a safe one.
