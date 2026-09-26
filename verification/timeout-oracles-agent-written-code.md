---
title: "Timeout Oracles for Agent-Written Code"
term: "Timeout Oracle"
description: "Agent-written C utilities produced fewer fuzz failures than their human originals, and every failure from the agent's own code was a hang, not a crash."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - hang oracle for generated code
  - resource oracle for agent-written code
  - timeout oracle in fuzz testing
last_reviewed: 2026-09-17
maturity: emerging
---

# Timeout Oracles for Agent-Written Code

> Add a timeout oracle beside the crash oracle. In one ten-utility fuzz study, every failure originating in the agent's own code was a hang.

A timeout oracle is a second failure condition in the test harness. The run fails when it exceeds a wall-clock or memory budget, not only when it crashes. Classic fuzz testing carries one by construction: its oracle "only considers the program to have failed if it crashed or hung" ([arXiv:2609.18298v1](https://arxiv.org/abs/2609.18298v1), §5.1). A functional suite scored on output has no such condition, so a run that never finishes surfaces as a CI timeout with nothing pointing at the code.

The case is narrow: one study, C command-line programs, a heavy agentic workflow. It argues for a second oracle, not for retiring the first.

## Where the evidence comes from

Shafique, Miller and Heymann rebuilt ten Linux utilities in C with Claude Code Opus 4.8, running a five-stage workflow that ends in a conformance audit and a security audit. Where the documentation was ambiguous the agents escalated to a human operator, whose decision "becomes part of the implementation plan" (§2.3.2). Each agent-written version was then fuzzed against the latest release of its repository counterpart with classic black-box fuzzing, 4,280 test cases and roughly 12 GB of input, plus AFL++ 5.01a ([arXiv:2609.18298v1](https://arxiv.org/abs/2609.18298v1), §2, §5).

Fuzzing found 24 unique failures across both versions of all ten programs. Nineteen were in the repository versions and five in the agent-written ones (§6). Reading Table 2, the repository versions carried 15 crashes and 4 hangs; the agent-written versions carried 2 crashes and 3 hangs.

Three of those five agent-side failures came from third-party code both versions link: `libedit` in `tnftp` (§6.10.1), and the GNU regex library in `ptx` (§6.7) and `grep`, where "the failure originated in the GNU regular-expression library used by both implementations rather than in grep itself" (§6.4). That leaves two failures in the agent's own code, and neither is a crash. The `dc` hang appears in the repository version too, because "The hang in both versions had the same cause" (§6.3): arbitrary-precision exponentiation on a value the random input made enormous. The `ptx` hang is the agent's alone.

## Why it works

What the workflow measured is what improved. Memory safety had two explicit carriers, a coding skill encoding defensive programming and the SEI CERT C rules, and a final audit stage where the agents drove sanitizers, Valgrind and GDB (§2.3.3, §2.3.5). Cost had an instruction and no check. The oracle came from the documented specification and any upstream test suite (§2.1, §2.3.1). Neither states asymptotics. The authors also "explicitly prohibit the use of fuzz testing at this stage" so their evaluation stayed independent of the agents (§2.3.5), which kept the technique that eventually found the hangs out of the development loop.

The saving is visible in the code. The agent-written `less` avoided all three of the repository version's memory-safety crashes "by using different designs and data structures rather than by adding extra checks" (§6.5). It keeps no screen-row position table, so there is no array to read past the end of. Nothing in the pipeline made an equivalent choice about time or space. The `ptx` inefficiency survived "even though Claude was explicitly instructed to avoid unnecessarily expensive algorithms and data structures" (§8).

## When this backfires

- Single-shot generation reverses the memory-error finding. VULBENCH-CPP annotated 8,918 C++ programs written by three open-weight models and by human authors across 851 competitive-programming tasks, with the dynamic tier run as ASan and UBSan. It reports AI-generated code "roughly twice as likely as human code to trigger a confirmed runtime violation, even after controlling for code length and test pass-rate" ([arXiv:2607.00107v3](https://arxiv.org/abs/2607.00107v3)). Without an audit stage the crash oracle stays primary.
- Third-party dependencies put the crash class back. The agent-side crashes came from `libedit` and GNU regex, which no prompt reaches and no timeout oracle detects.
- Memory-safe target languages have nothing to trade. Go, Python and safe Rust leave the cost blindness with none of the saving.
- Targets with no natural time bound produce false failures. The study's hardest operational problem was "distinguishing genuine hangs from programs that were simply waiting for more input or taking a long time to process very large test cases" (§5.1). The authors manually examined reported hangs before counting them as failures.
- The sample is ten programs and five agent-side failures, three of them library-caused, so the claim about agent-authored failures rests on two events in one language with one model. Treat it as a reason to instrument, not a measured rate.

## Example

The `ptx` hang is the shape to test for. The agent's implementation builds each output line by repeatedly scanning the surrounding text and assembling it one character at a time. On ordinary newline-bearing input the behavior stays linear with a large constant: a 100 MB fuzz-generated input "took about 10 minutes, compared with about 15 seconds for the repository version". On newline-free input the whole file becomes one text region and the work per word grows with file size, so "A 2.6 MB newline-free input took more than 10 minutes" ([arXiv:2609.18298v1](https://arxiv.org/abs/2609.18298v1), §6.7).

Both executions terminate eventually. No sanitizer fires, no assertion fails, and a suite scored on output alone passes. Only a bound on elapsed time turns them into a reported failure, and the threshold does as much work as the inputs. The paper names one of its thresholds for the AFL++ campaign that caught the `grep` hangs: "The hangs were detected by AFL++ with a hang timeout of 10 seconds" (§6.4).

## Key Takeaways

- A crash-only oracle points at the class this workflow suppressed and misses the class it produced. Run both.
- Set the hang threshold on purpose. The one threshold the paper names is 10 seconds, on the AFL++ campaign that caught the `grep` hangs (§6.4), so treat the number as a tuning decision rather than a default.
- Size inputs to reach asymptotic defects. The `ptx` quadratic behavior showed up on a 2.6 MB newline-free input, orders of magnitude past a unit-test fixture.
- An instruction to avoid expensive algorithms is not a measurement. Claude was given that instruction and shipped the quadratic loop anyway.
- The workflow behind these numbers ran sanitizers, Valgrind and GDB at its audit stage (§2.3.5). Drop that stage and you are no longer in the setup the result came from.

## Related

- [Coverage-Guided Agents for Fuzz Harness Generation](coverage-guided-fuzz-harness-generation.md) — generating the harness this oracle plugs into
- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — the companion question of whether the assertions would notice anything
- [Behavioral Testing for Agents](behavioral-testing-agents.md) — choosing what an agent test asserts on
- [Unbounded Agent Feedback Paths (Infinite Agentic Loops)](../patterns/anti-patterns/unbounded-agent-feedback-paths.md) — the same failure shape one level up, in the agent loop rather than the program it writes
- [Unbounded Consumption: Bounding Agent Resource Use](../security/unbounded-consumption-resource-bounds.md) — resource bounds as a production control
