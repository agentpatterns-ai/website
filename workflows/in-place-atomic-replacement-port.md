---
title: "In-Place Atomic Replacement for Agent-Driven Ports"
term: "In-Place Atomic Replacement"
description: "Land an agent-driven language port in main one component at a time, deleting each old implementation in the same pull request that adds its replacement, under four stated preconditions."
aliases:
  - in-place atomic swap port
  - atomic component replacement migration
  - porting in main instead of a migration branch
tags:
  - workflows
  - agent-design
  - testing-verification
  - tool-agnostic
last_reviewed: 2026-09-17
maturity: emerging
---

# In-Place Atomic Replacement for Agent-Driven Ports

> Each pull request adds the new implementation in `main`, shims the old call sites, and deletes the replaced code in one atomic commit.

An in-place atomic replacement port runs in `main`. Each pull request "ports a single component or slice" into the target language, leaves a thin shim where the original stood, and deletes the original in the same change, so the two implementations never coexist. GitHub ported the Copilot agent runtime from TypeScript to Rust this way between May 12 and August 21, 2026, across 128 port pull requests, with agents writing most of the code ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).

## The long-lived branch problem

The line-by-line half of reviewing a port is already delegated. GitHub ran a `rust-rebase-review` skill that launched one subagent per model to do "a line-by-line comparison of the old TypeScript and the new Rust, confirming behavioral equality", and "human reviewers concentrated on architecture, API contracts, risk, and any suspicious places surfaced by those other layers" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). What is left to choose is where the port lands. A migration branch defers the correctness question to a single cutover, and the cost of that is named in the post: with a big-bang approach "consumers experience every ported line at once, including all regressions that slipped through in-repo testing" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). The other incremental option, keeping both implementations hot-swappable, lost on coupling rather than on principle. Session orchestration "owns mutable state, drives callbacks in both directions, and threads through nearly every other subsystem", and "the coupling that makes a component hard to port is the same coupling that makes it near impossible to shadow without risking introducing more regressions than it avoids".

## Four conditions before you start

The evidence is one team's account of its own project, and its author names what carried it. Check all four before adopting the shape.

1. The end-to-end suite already describes the behavior being ported. Deleting the old implementation removes the only other record of correct behavior, so the tests become the contract. GitHub raised its coverage before starting and still judged it thin: with one exception, every regression that lost a feature traced back to insufficient end-to-end tests ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).
2. The agent cannot edit that suite. One port omitted the SDK callbacks and deleted their end-to-end test, "prompting a new rule that agents must not change E2E tests without explicit consent" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).
3. The target language is statically typed, so its compiler absorbs the model's mechanical mistakes before the tests see them. Across 8,678 captured `rustc` error-code occurrences, "the four largest diagnostic families cover 84%": name and import resolution (37%), missing methods or fields (22%), type mismatches (14%) and unsatisfied trait bounds (11%). GitHub calls these "exactly the ones a compiler catches very quickly", and says the requirement is not Rust: "a C# or Java or Go compiler would catch all of them just as well" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).
4. The release channel ships during the port. Last-mile validation came from 135 releases in the roughly fourteen-and-a-half-week window, 100 pre-release and 35 stable, with pre-releases at 10.5% of npm downloads in a trailing seven-day sample ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).

## Three implementation layers

### Layer 1: sequencing

Order the work from the leaves inward. GitHub began with two pull requests that established the Rust workspace, toolchain, lint rules, CI, build pipeline and coding instructions, then ported pure-logic helpers chosen because they had no I/O or shared state and already had strong tests. Stateful subsystems followed, and session orchestration, the most coupled part of the runtime, came near the end. The useful unit was often larger than a component: "first move the pure logic, then move state ownership, then move orchestration, then remove fallbacks, and finally simplify the Rust after the temporary interop was gone" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). MCP support alone took seven dedicated pull requests.

### Layer 2: the atomic pull request

One commit does three things. "Each pull request replaces the existing TypeScript implementation with a thin shim that calls into Rust, and deletes the old code in one atomic change. The new code is immediately exercised, in-situ" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). Calls cross the boundary both ways while the port is in flight, because a ported component often depends on something not yet ported. Every one of those callbacks is temporary by construction and is deleted once the other end moves.

### Layer 3: release and detection

Ship the ported components instead of holding them. Each release carried "a small and knowable set of ported components", so a reported issue correlated with recent changes rather than with the whole rewrite, and root-causing stayed cheap. GitHub averaged about 1.3 releases and about 1.3 port pull requests per day over the window ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).

## Triggers and constraints

Port pull requests open against a planned sequence, not on a schedule. Two constraints bound what an agent may land. The first is the required test set: "If a pull request caused a required test to fail, it didn't land." The second is ownership of that test set, carried in the port review instructions as "Validate that no E2E tests have been deleted or changed. Such changes are an indication of a porting bug" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). Both live in branch policy and test ownership rather than in any one assistant, so the workflow is tool-agnostic. See [oracle-gated delegation](oracle-gated-delegation.md) for when a mechanical check can stand in for reading the diff.

## Why it works

While both implementations exist, "correct" has two candidates, and a caller still reaching the old path hides a defect in the new one. Deleting the old code in the same commit removes that ambiguity. One implementation remains, so every pre-existing end-to-end test becomes a differential check against behavior recorded before the port, and it runs on each commit rather than at a cutover: "All existing end-to-end tests, across the CLI and SDK, run against the new Rust code at every step" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).

The deletion does a second job the team did not plan for. A concurrent branch that edits already-ported code collides with the branch that deleted it, so drift shows up as a merge conflict. "This guaranteed we'd notice changes to already ported code, rather than needing to rationalize for every incoming line whether it was something that might have been touching previously ported code" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). Both effects come from the deletion, not from the target language.

## When this backfires

- You need a measured mismatch rate. GitHub's own [scientist](https://github.com/github/scientist) library exists for the approach this port declined: wrap the original behavior in a `use` block and the new behavior in a `try` block, and the run "compares the result of `try` to the result of `use`". Its README names the gap an atomic swap leaves open: "Tests can help guide your refactoring, but you really want to compare the current and refactored behaviors under load." That difference has a price here. "By September 14, 2026, we'd traced dozens of known port regressions, all fixed", and the author adds "I'm 100% sure there are more than the ones we know about" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).
- The target language is dynamically typed. Without a compiler, the wiring mistakes behind 84% of GitHub's captured `rustc` diagnostics reach the end-to-end suite instead, and that suite is already the only oracle this strategy leaves standing. Ownership and lifetime errors were 1.7% of coded diagnostics, so what you give up is ordinary static typing rather than anything Rust-specific ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).
- Releases are infrequent. The last-mile signal came from shipping 135 versions during the port. A quarterly release train takes the risk of deleting the old implementation without the exposure that reveals what the tests missed.
- The repository is quiet. Conflict detection only fires where other people edit the code you deleted. Without concurrent traffic that benefit is absent, and a parallel branch costs less than this account implies.
- The port is also a redesign. GitHub's rule was "translate first, redesign second", and the author reports veering from it: "in hindsight I regret every one of them. Each cost more regressions, more time, or more tokens than staying the course would have" ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).

## Example

GitHub's runtime port is a first-party account of its own project, with no independent audit and no control arm, so read the figures as a worked example rather than a benchmark. Roughly 430,000 lines of production TypeScript went through the port, against 832,378 lines of production Rust, 468,689 lines of Rust unit tests and 174,675 lines of end-to-end TypeScript tests. The bill was "\~136.3 billion total tokens" costing "\~$120,000", plus about three weeks of a developer's time. Median changed lines per port pull request rose from 3,250 in early May to 99,445 in late August ([GitHub Blog, 2026-09-17](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)).

## Key Takeaways

- Keep the deletion in the same commit as the replacement. A pull request that adds the new code and leaves the original in place gives up both the oracle and the conflict signal, which is most of what the shape buys.
- Put the end-to-end suite under separate ownership before the first port lands. The agent rewriting an implementation will otherwise rewrite the test that judges it, and GitHub only added that rule after it happened.
- Sequence the work as infrastructure, then pure logic, then state ownership, then orchestration. The most coupled component moves near the end, not at the start.
- Budget for regressions instead of planning around none. Dozens surfaced across 832,378 lines of new Rust, and the author expects more to appear.
- Skip the shape when the correctness bar needs a number. A parallel run measures a mismatch rate; a green suite does not.

## Related

- [Staged Literal Porting with a Per-Stage Numeric Oracle](staged-literal-port-with-numeric-oracle.md) — what to hold fixed inside one port step
- [Parallel Polyglot Ports as a Spec-Ambiguity Oracle](parallel-polyglot-ports-spec-oracle.md) — the opposite trade, where divergence between live implementations is the signal
- [Documentation-Guided Legacy Migration](documentation-guided-legacy-migration.md) — building the blueprint an agent ports from
- [Verification-Gated Agent Autonomy](../patterns/agent-design/verification-gated-agent-autonomy.md) — the building block this workflow composes, one check per unit of delegated work
- [Whole-Codebase Visibility as a Migration Prerequisite](whole-codebase-visibility-migration-prerequisite.md) — the scoping check that runs before any port strategy
