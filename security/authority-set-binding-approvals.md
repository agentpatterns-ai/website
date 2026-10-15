---
title: "Authority-Set Binding: Who Names an Approval's File Set"
term: "Authority-Set Binding"
description: "An approval binds one file while the run reads more. Two coding-agent runtimes hashed correctly and bound five different file sets for one deployment task."
aliases:
  - authority set of a task
  - delegated-authority omission
  - approval receipt over a file set
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-14
maturity: emerging
---

# Authority-Set Binding: Who Names an Approval's File Set

> An approval bound to one file leaves its delegated files unbound, and an agent asked to name them binds different sets from run to run.

An authority-set binding records an approval as the digests of every repository file the approved run is configured to read. The file put in front of the reviewer is one member of that set. Hossen calls that set the authority set of a task, and one path with one digest is sound only when the task reads a single file ([arXiv:2610.15137v1 §4](https://arxiv.org/abs/2610.15137v1)).

## When the wider binding earns its cost

Three conditions, and all of them have to hold.

The approval has to outlive the commit it was granted on. A saved allow rule or a reviewer sign-off that stands for weeks has no snapshot to pin to. Where a run can execute the exact approved tree, do that instead: "Executing exactly the approved commit satisfies the property for every task, and it is the recommended fix for review-gated workflows" ([arXiv:2610.15137v1 §3](https://arxiv.org/abs/2610.15137v1)). That answer stops short because "A commit binding ends at the next commit and does not express a standing approval."

Delegation has to be real. Where a workflow says only `terraform apply`, "What that command creates, including the cloud permissions it grants, is written in the Terraform files the command loads" ([arXiv:2610.15137v1 §2](https://arxiv.org/abs/2610.15137v1)).

Finally, those delegated files have to move on their own. Of 5,251 commits across 20 public repositories, 542 modified a file some approved run reads, and the approved file was byte-identical in 296 of them, or 54.6% ([arXiv:2610.15137v1 §6.1](https://arxiv.org/abs/2610.15137v1)). Those were ordinary commits with no attacker involved. That share belongs to this corpus and not to repositories in general: three repositories contribute 203 of the 296, and resampling the repositories gives "a 95% interval of 35.6% to 70.6% for the pooled share."

## Why it works

A digest commits to the bytes it covers and to nothing else, so coverage decides soundness and the hash function does not. When the binding names every member of the set and the check passes, "a modified or deleted file changes a file digest, and a file added to a loaded directory changes a directory digest" ([arXiv:2610.15137v1 §4](https://arxiv.org/abs/2610.15137v1)). Read that backwards for the vulnerability: a path the record never named changes without moving any digest the checker compares.

Two demonstrations on public repository files show it. Appending an IAM block gave a deployed role write access to a storage bucket. Changing one line of a policy configuration file took the required human approvals for high-risk changes from 1 to 0. Each approved file stayed byte-identical and a single-object check accepted both ([arXiv:2610.15137v1 §6.3](https://arxiv.org/abs/2610.15137v1)).

## Who names the set

Not the agent, and not because agents hash badly. Across 62 records that could hold a file set, 61 carried the canonical digest of the set they bound, so "hashing is not where the records differ" ([arXiv:2610.15137v1 §6.2](https://arxiv.org/abs/2610.15137v1)). Enumeration is. The 16 Terraform runs, from one workspace and one prompt, bind "five different sets" ([arXiv:2610.15137v1 §6.2](https://arxiv.org/abs/2610.15137v1)), four of them from one runtime: "Claude Code bound four different sets in eight runs". Two of its records for a Terraform deployment "bind five workflow files and none of the 42 Terraform files." Both were well formed and carried a correct digest, so a gate enforcing either accepts any edit to the configuration that deployment applies.

Hence a producer and checker split: "A set named by the approval producer is an assertion, and the agent is a producer" ([arXiv:2610.15137v1 §7](https://arxiv.org/abs/2610.15137v1)). Let the agent propose the set, have the gate compute the digest itself, and draw membership from a source the gate can check. A saved Terraform plan is one such source, because the file does "contain your full configuration, all of the values associated with planned changes, and all of the plan options including the input variables" ([Terraform CLI docs](https://developer.hashicorp.com/terraform/cli/commands/plan)). A reviewed manifest and a directory rule are the other two. The plan route bills you for the privilege, because HashiCorp says to "treat any saved plan files as potentially-sensitive artifacts", so a gate that reads plan files gains a secret-bearing input to protect.

Asking the agent whether one file is enough routes nothing either. The runtimes raised that flag on a genuinely single-file task in 15 of 16 runs ([arXiv:2610.15137v1 §6.2](https://arxiv.org/abs/2610.15137v1)).

## When this backfires

| Condition | What it costs |
|---|---|
| The run is pinnable to a commit | Enumeration risk, for a property you already had |
| Entrypoint and delegated files move together | Generated workflows showed 1 delegated-only commit in 24 ([arXiv:2610.15137v1 §6.1](https://arxiv.org/abs/2610.15137v1)) |
| Nobody can complete the set | The paper's own auditors abandoned 7 of 30 candidate sets ([arXiv:2610.15137v1 §5](https://arxiv.org/abs/2610.15137v1)) |
| A delegated file sits outside the directories | In 2 of 3 delegating cases a task runner or cluster-role manifest sat elsewhere, so a directory rule has to name it separately ([arXiv:2610.15137v1 §7](https://arxiv.org/abs/2610.15137v1)) |
| You fall back to a directory rule | It "costs re-approvals for unrelated edits there"; both runtimes bound 62 Helm files against the audited 43 ([arXiv:2610.15137v1 §6.2](https://arxiv.org/abs/2610.15137v1)) |
| Prompt volume is already the constraint | "Claude Code users approve 93% of permission prompts" ([Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)) |

The first three rows are the dangerous ones, because an unsound binding gives no sign that it is unsound: "A record has the same form whether its set is exact, over-inclusive, or missing every Terraform file" ([arXiv:2610.15137v1 §6.2](https://arxiv.org/abs/2610.15137v1)).

## Key Takeaways

- Sort approvals by whether they can be pinned to a commit. Pin those, and spend enumeration effort on the remainder.
- Then route by whether the approved file delegates. A single-object check is right for a one-file task and wrong for any other.
- Never enforce a set the producer supplied. Compute the digest in the gate; take membership from a tool record, a manifest, or a directory rule.
- Budget the re-prompts first. A standing approval bound to the set is re-requested on "about one in ten" commits here ([arXiv:2610.15137v1 §6.1](https://arxiv.org/abs/2610.15137v1)), and a directory rule adds more.

## Related

- [Agent Approval Laundering: Effects Beyond the Named Command](approval-laundering-transitive-effects.md) — the same record gap measured over effects a command reaches rather than files its run reads
- [The Skill Closure Declaration Gap](skill-closure-declaration-gap.md) — how completely published skill manifests name the files one run of them loads
- [The Post-Authorization Execution Trust Gap in Remote MCP](post-authorization-execution-trust-gap.md) — a grant that names the client and never the workload that runs the call
- [Approval Records That Bind No Identity and No Session](../patterns/anti-patterns/unbound-approval-records.md) — the identity dimension of the same record, where the approved command is replayed by another agent or in a later session
- [Workflow Execution Protections](workflow-execution-protections.md) — the branch and environment controls that sit around a gated deployment
