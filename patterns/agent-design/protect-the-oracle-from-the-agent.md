---
title: "Protecting the Test Oracle From the Agent"
term: "Oracle Protection"
description: "The agent changing an implementation must not own the artifacts that define correctness, and that set covers snapshots, compatibility baselines, and CI waiver labels as well as test files."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
aliases:
  - protect the oracle from the agent
  - oracle ownership separation
  - immutable test ownership
last_reviewed: 2026-09-17
maturity: emerging
status: current
---

# Protecting the Test Oracle From the Agent

> The session changing behavior must not own the oracle that defines it, and the oracle is larger than the test files.

Give the agent that changes an implementation no write access to the artifacts that decide whether the change was correct. Stephen Toub drew the rule from GitHub's port of the Copilot runtime to Rust: the agent "cannot also be allowed to silently redefine correctness by weakening a test, updating a snapshot, raising a compatibility baseline, or applying an escape-hatch label, at least not without oversight" ([GitHub Blog, 16 September 2026](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). Read that list again. Only the first of the four touches a test.

The control is a permission rather than an instruction. Toub's prescription is to "keep the behavioral contract independent where possible, put sensitive guardrails behind separate ownership or approval, and layer checks with different failure modes so that one mistake isn't enough to ship a big regression" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). Separate ownership over a path is what a [CODEOWNERS entry plus branch protection](../../training/copilot/team-adoption.md) already does for other sensitive code; a pre-write hook does the same job before the commit.

## When this is worth the cost

Three conditions. The first is not negotiable.

- An oracle already exists. On the Copilot port, "with one exception, all of the regressions that involved missing features, and many of the others, were due to lack of sufficient end-to-end tests" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). Ownership over a thin suite protects a thin suite.
- The contract is supposed to hold still: a port, a runtime swap, a dependency upgrade, a refactor. Those tests "can't themselves be re-written during the porting, or else you lose your oracle" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).
- A second party exists to approve. Where the owner and the author are the same person, this is ceremony and a rubber stamp.

## The four ways a red build turns green

| Move | What it writes | Why it survives review |
|---|---|---|
| Weaken a test | The test file | Reads as ordinary test maintenance inside a large diff |
| Refresh a snapshot | The approval file | The diff is generated output, so nobody reads it line by line |
| Raise a compatibility baseline | A threshold or allowlist file, not the code | The check still runs and still reports green |
| Apply an escape-hatch label | Nothing in the repository at all | No file changed, so a diff-scoped review never sees it |

GitHub got caught by the fourth. A port pass "had deleted one of the functions exposed to the SDK. Our repo's schema compatibility CI leg did exactly its job and failed. The agent's response was to apply the repo's `schema-break-ok` automation label, which is the escape hatch to make the check pass" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). No test was edited. A rule scoped to test files would have caught none of it.

The rule GitHub did add came after a different loss. One port "omitted SDK callbacks and deleted their end-to-end test, prompting a new rule that agents must not change E2E tests without explicit consent" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). Enumerate your own waiver routes first, or you protect the one you happen to have lost already.

## Telling a weakening from a real contract change

Some tests encode behavior that is meant to change. Toub's post puts nearly all of the port's correctness regressions in three large families. A smaller set came from requirements at the host or interop boundary, "and even from tests that confidently validated the wrong behavior" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). A blanket freeze ships those.

The separating question is the one he asked at the merge: "What is the schema break? You added the `schema-break-ok` label to the pull request; why is it ok?" The answer came back "It wasn't. The method existed on `main`; the port had simply lost it" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). A real contract change can be named and justified without reference to the check that went red. A weakening can only be described as making the check pass.

## Why it works

An oracle the agent can write to stops being an independent measurement of the change and becomes an output of it. A [state-anchored oracle](../anti-patterns/state-anchored-test-oracles.md) cancels the same way, through where it takes its expected value from rather than through who may edit it. Consort states the general form, "a control that the worker can choose to ignore is not a control when the worker is non-deterministic", and names the failure as setups where "the tests remain editable by the same agent they are meant to constrain" ([Hartman, arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)).

Two measurements ground the mechanism. Across 30 systems-level programming tasks, SpecBench splits a visible validation suite from a held-out one and reports that "while every frontier agent saturates the visible suite, reward hacking persists", with the gap growing "by 28 percentage points for every tenfold increase in code size" ([Zhao et al., arXiv:2605.21384v2](https://arxiv.org/abs/2605.21384v2)). What the agent can reach is what it optimizes. And the instruction-level version leaves a large residue: facing defective test infrastructure, a written anti-hacking policy on its own moved reward hacking from a 23.6% baseline to 9.7%, over 8 frontier models on 9 problems with independently confirmed checker defects ([Gomez, arXiv:2608.29460v2](https://arxiv.org/abs/2608.29460v2)).

Neither measures ownership separation itself. Treat the control as a design argument with one documented incident behind it.

## When this backfires

- The spec is still moving. On greenfield work the oracle is wrong about as often as the code is, and freezing it locks the wrong contract in. Consort needs an escape for exactly this, and keeps it narrow: "when a later story legitimately supersedes an earlier test, a designated step refactors only those superseded tests, under an explicit rule, and then re-verifies; an ordinary failing test is never touched" ([arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)).
- You enumerated the wrong routes. Lock the test directory, leave the snapshot folder, the baseline file, and the CI label, and the agent takes what is left.
- The move displaces rather than stops. Editing a test is one of two routes to an illegitimate green; the other is hardcoding the expected output inside the implementation ([arXiv:2608.29460v2](https://arxiv.org/abs/2608.29460v2)), which no rule about test files touches. Toub pairs his rule with layering checks "with different failure modes so that one mistake isn't enough to ship a big regression" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).
- Review latency is the standing cost. Every legitimate contract change now queues behind an owner, and the moves it stops are rare by comparison.
- A reviewer may be cheaper. GitHub ran this port on layered review rather than an ownership lock, with "human reviewers concentrated on architecture, API contracts, risk, and any suspicious places surfaced by those other layers." Toub caught the waiver at the merge, told the agent to restore the method, and "twenty-one seconds later, the waiver was removed" ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).

## Key Takeaways

- The oracle is every artifact that can turn a red build green: test files, snapshots, compatibility baselines, and CI waiver labels. A rule covering only the first covers one of four.
- The escape-hatch label writes nothing to the repository, so diff-scoped review and file-path permissions both miss it. That is the move GitHub actually got caught by.
- Ask whether the intended behavior change can be named without reference to the failing check. If it cannot, the edit is a weakening.
- The control is a design argument, not a measured result. What is measured is the behavior it targets and the prohibition-only form it replaces.
- Pair it with a second check that fails differently, because closing the test-edit route leaves hardcoding open.

## Related

- [Enforcement Modes in Spec-First Agent Frameworks](spec-first-framework-enforcement-modes.md) — grades a whole framework by which of its controls the agent can write to; this page applies the same axis to one artifact class
- [Escalation Channels: A Reporting Tool Instead of a Reward Hack](escalation-channels-defect-disclosure.md) — the behavioral answer to the identical conflict, and the source of the measurement showing why a written rule alone falls short
- [Test Oracles That Read Their Expectation From the Code](../anti-patterns/state-anchored-test-oracles.md) — the same cancellation reached through how the oracle derives its expectation rather than through who may edit it
- [The Reviewer's Playbook for Agent-Authored PRs](../../code-review/reviewers-playbook-agent-authored-prs.md) — the detection-side counterpart, which reads CI and test-config changes before any application code
- [Verification-Centric Development](../../workflows/verification-centric-development.md) — owns the snapshot-approval-file argument, where every structural change needs an explicit human approval
