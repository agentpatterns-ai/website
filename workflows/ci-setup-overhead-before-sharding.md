---
title: "Reducing Fixed CI Overhead Before Adding Shards"
term: "Fixed CI Overhead"
description: "Per-job setup cost decides how far test sharding pays, so cut it before buying parallelism, using the measured case where a quadrupled suite held pull request wait time roughly flat."
aliases:
  - per-job CI setup cost
  - CI overhead before parallelism
tags:
  - workflows
  - agent-design
  - testing-verification
  - tool-agnostic
last_reviewed: 2026-09-22
maturity: emerging
status: current
---

# Reducing Fixed CI Overhead Before Adding Shards

> Sharding divides test work and multiplies per-job setup, so fixed CI overhead decides how far parallelism pays. Cut it first.

Every job pays a fixed cost before it runs a single test: booting a runner, checking out the repository, installing dependencies, provisioning a database. Sharding divides the test work across more jobs and pays that fixed cost once per job, so overhead sets a ceiling on parallelism that arrives well before the runners run out.

## The CI capacity problem

When agents write most of the tests, the suite grows faster than the pipeline that runs it, and merge throughput becomes a property of CI rather than of the reviewers. Linear's engineering team hit this in 2026 and described it plainly: "Agents have made it exponentially faster to ship code, but validating those changes hasn't quite kept up at the same rate" ([Linear](https://linear.app/now/ci-bottleneck-reworked)). The team is "currently adding roughly 2,000 tests a week".

[The bottleneck migration](../human/bottleneck-migration.md) puts that limit on human review and judgment. This is the machine-side reading: the queue in front of the merge, measured in runner-minutes.

## When this applies

1. Setup is a large share of job time. A shard that spends two minutes starting and four minutes testing wastes a third of its bill. A shard that starts in ten seconds does not; target the slow tests instead.
2. The constraint is runner time, not a concurrency cap. Cheaper jobs do not shorten a queue caused by a ceiling on concurrent runners. Buying concurrency does.
3. Predictive test selection is out of reach. Teams with a long labeled history of test outcomes have a stronger option: see [When this backfires](#when-this-backfires).

## Three implementation layers

### Layer 1: strip the fixed cost out of every job

Find the work each job repeats before it does anything useful, then move, shrink, or delete it. Linear's three changes were ordinary: preinstall shared dependencies into a CI base image rather than `apt`-installing them per shard, install only the workspace package a job needs rather than the whole monorepo, and stop caching what is faster to rebuild. The third is the one teams get backwards. Restoring a `node_modules` cache took about 28 seconds against roughly 7.5 seconds for a filtered install, so the cache "was adding save time and variability without giving us any discernible advantage". Together the three took per-shard setup down "by roughly 44%, from 110-140 seconds to 67-73 seconds".

The same layer covers jobs that are pure overhead. Seven independent checks were each booting a runner, checking out the repository, and installing dependencies for seconds of real work. Consolidating them into two jobs, running the seven tasks concurrently inside, "saved roughly 87,000 runner-minutes per month, equivalent to 11.8% of our total CI usage". No check got faster.

### Layer 2: shorten the jobs that gate the fan-out

A gating job's cost is multiplied by everything waiting behind it. Change-detection jobs that decide which downstream work runs were checking out the full working tree for a path diff a shallow fetch could compute. Capping the fetch depth took the slowest of those gates "from 94 seconds to 20", and removing checkout from jobs that never needed a working tree took those "from 27 seconds to 7". The median change-detection job "fell from 26 to 8 seconds, p90 from 31 to 12 seconds, and the slowest run from 138 to 37 seconds".

Cache-marker writes sat in the final pre-merge check, so a pull request waited in the merge queue after its tests had already passed. Moving that write into a job that gates nothing shaved "42 seconds from the merge path for every API pull request and merge-queue entry".

### Layer 3: spend the headroom on parallelism, then defend it

Only now does adding shards pay. Linear went from four shards to eight, which made the critical job "roughly 19% faster and 19% cheaper", after first splitting oversized test files because Vitest "distributes work by file rather than by the duration of individual tests". The largest single win came from letting opted-in files share a module registry instead of rebuilding the entity, GraphQL, and decorator graph per file, worth "roughly 17% in monthly savings at our volume".

Shared module state is also the one change that can make a passing suite lie, so it holds only while every new test file honors the opt-in. Layer 3 is finished when that constraint is written where the authors of new tests will read it, not when the shards are configured.

## What the rework returned

| Change | Measured result |
|---|---|
| Moved off GitHub Actions to third-party runners | Jobs 34% faster on average, `tsc` down 52% |
| Switched to the `tsgo` native TypeScript compiler | Weekly median `tsc` check down 73% |
| Rewrote lint rules to drop the type graph | API lint time down 68%, full-repository lint down 55% |
| Capped fetch depth on change-detection gates | Slowest gate 94s to 20s, median 26s to 8s |
| Preinstalled the Postgres client, filtered the install, dropped a cache | Per-shard setup down roughly 44%, 110-140s to 67-73s |
| Batched seven short checks into two jobs | Roughly 87,000 runner-minutes per month, 11.8% of CI usage |
| Raised test shards from four to eight | Critical job roughly 19% faster and 19% cheaper |
| Shared module state across opted-in test files | Roughly 17% monthly savings, slowest shard ~300-379s to ~195s |

Against test suites "almost *quadrupling* since the start of the year", the team "brought pull request wait time down from more than 6 minutes to just over 5, while cutting runner time per test roughly in half". Wait time moved by about a minute; capacity moved by a factor of four. Plan for the second number. Promise the first, and a rework that absorbed four times the tests will read as a project that saved sixty seconds.

## Triggers and constraints

The pipeline runs on pull request and merge-queue events, so every change is measured against a per-PR critical path rather than a nightly total. A change that lowers total runner-minutes without touching that path is a cost win rather than a latency win.

The layers are tool-agnostic. The specific levers are not. Fetch depth, image preinstallation, job batching, and gating-job placement apply to any CI system; the module-state item exists only where the test runner rebuilds per-file state, and the compiler and linter swaps are TypeScript-specific.

## Why it works

A job's cost splits into fixed setup and variable work, and sharding divides only the second term while multiplying the first. Adding shard N saves roughly `work/N` of wall-clock and adds one more setup, so once setup approaches `work/N` the next shard costs more than it returns. Linear states the relation and prices both sides of it: "Further sharding only pays off when the fixed cost per shard is low, since doubling the shard count also doubles the workflow time spent on setup." At 110-140 seconds of setup, "eight shards would have spent 15-19 minutes of runner time on setup alone, more than the tests themselves", while at roughly 40 seconds "eight shards spend less total setup time than four did before, while parallelizing the tests twice as far" ([Linear](https://linear.app/now/ci-bottleneck-reworked)). Overhead reduction is the precondition that decides how far sharding can go.

## When this backfires

- Setup is already cheap relative to test time. The exercise returns single-digit percentages and the hours are better spent on the slow tests.
- A concurrency cap is the real limit. Lower runner-minutes do not move a queue caused by a ceiling on concurrent jobs.
- The test runner does not rebuild per-file state. Linear's largest single win exists because "Vitest normally isolates every test file, which for us meant rebuilding the entity, GraphQL, and decorator graph in each test shard" ([Linear](https://linear.app/now/ci-bottleneck-reworked)). A runner with nothing to rebuild has nothing to share, so that item is absent and what remains is smaller.
- Predictive test selection is available and stronger. Meta reported that a learned selection model "reduces the total infrastructure cost of testing code changes by a factor of two, while guaranteeing that over 95% of individual test failures and over 99.9% of faulty changes are still reported back to developers" ([arXiv:1810.05286v2](https://arxiv.org/abs/1810.05286v2)). That attacks test volume rather than per-job cost, and the gain keeps growing with the suite instead of stopping at an overhead floor. It costs a large labeled history of test outcomes and an accepted miss rate.
- Isolation is relaxed without an enforced opt-in. Sharing state between test files is the condition that produces order-dependent flakiness, and one study of 7,571 flaky Python tests found that "order dependency is a much more dominant problem in Python, causing 59%" of them ([arXiv:2101.09077v1](https://arxiv.org/abs/2101.09077v1)). Linear calls the same change "the optimization with the highest correctness risk", requires an explicit opt-in comment on every eligible file, and left files using fake timers or untangleable shared state in the isolated project.

## Example

The last risk has a fix that only shows up once agents are the authors. An opt-in rule holds while every new test file respects it, and at Linear most new test files are generated: "because agents now write the majority of our tests, we updated our respective agent skills to account for this performance opt-in as well, so generated tests follow the same constraints by default" ([Linear](https://linear.app/now/ci-bottleneck-reworked)).

Generalize that. Any CI performance invariant an agent can violate belongs in the instructions the agent loads, and a deterministic check is better still ([Enforcing Agent Behavior with Hooks](../instructions/enforcing-agent-behavior-with-hooks.md)). At 2,000 new tests a week, a convention that lives only in a reviewer's head has a short life.

## Key Takeaways

- Price a job as fixed setup plus variable work before choosing a lever, because sharding divides the second term and multiplies the first.
- Sequence overhead reduction ahead of parallelism: eight shards at 110-140 seconds of setup would have burned more runner time on setup than on the tests.
- Batching short checks into fewer jobs can return more than making any check faster; seven folded into two freed 11.8% of one team's total CI usage.
- Expect capacity rather than latency. Absorbing a quadrupled suite at roughly flat wait time is the realistic outcome, and it is worth more than the minute it also saved.
- Put any CI performance invariant into the agent's instructions, because agent-written tests break an unwritten opt-in rule faster than review catches it.

## Related

- [Measuring the Verification Tax on Agent Output](verification-tax.md) — the cost ratio that says whether CI is where the spend went
- [The Bottleneck Migration When Humans Supervise Agents](../human/bottleneck-migration.md) — the human-side reading of the same constraint, where review absorbs the load
- [Agent PR Volume vs. Value: The Productivity Paradox](../code-review/agent-pr-volume-vs-value.md) — the volume growth that puts the pressure on CI
- [AI Bot CI/CD Workflow Reliability by Agent](ai-bot-ci-workflow-reliability.md) — how often agent-authored pull requests fail CI, which sets how much capacity goes to reruns
- [Enforcing Agent Behavior with Hooks](../instructions/enforcing-agent-behavior-with-hooks.md) — the deterministic way to hold an invariant agent-written code would otherwise erode
