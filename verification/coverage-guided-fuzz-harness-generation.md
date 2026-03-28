---
title: "Coverage-Guided Agents for Fuzz Harness Generation"
description: "Multi-agent systems automatically generate fuzzing harnesses for library APIs, using coverage feedback as the iteration signal to remove the manual bottleneck."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
aliases:
  - "fuzz target generation"
  - "automated harness generation"
---

# Coverage-Guided Agents for Fuzz Harness Generation

> Multi-agent systems can automatically generate fuzzing harnesses for library APIs using coverage feedback as the iteration signal, removing the primary bottleneck in library fuzzing workflows.

## The Manual Harness Bottleneck

Coverage-guided fuzzing is effective at finding memory corruption bugs, logic errors, and edge-case crashes in library code. The constraint is harness authoring: hand-written glue code that translates fuzzer byte streams into valid sequences of API calls. Writing a correct harness requires understanding parameter constraints, call ordering dependencies, and state initialization — work that can take significant time per API.

[arXiv:2603.08616](https://arxiv.org/abs/2603.08616) demonstrates that a multi-agent system using coverage feedback can automate harness generation for Java libraries, reducing time-to-first-fuzzing-results from weeks to hours [unverified — the "weeks to hours" time reduction claim has not been independently confirmed from the cited paper].

## How Coverage Feedback Drives Iteration

Coverage data (branch coverage, line coverage) provides a grounded signal that guides harness improvement:

```mermaid
graph TD
    A[API surface analysis] --> B[Initial harness generation]
    B --> C[Fuzzer executes harness]
    C --> D[Coverage report]
    D --> E{New paths explored?}
    E -->|Yes| F[Accept harness variant]
    E -->|No| G[Agent refines harness]
    G --> C
    F --> H[Expand to adjacent APIs]
```

When a harness fails to reach new code paths, the agent receives that signal and generates a revised harness — adjusting parameter values, reordering calls, or adding setup state. This is the same signal human harness authors use, but applied automatically.

## What the Agent Reasons About

Harness generation requires the agent to work through three constraints:

**Parameter constraints**: What values are valid for each argument? Null-safety, range constraints, format requirements. The agent can infer these from type signatures, Javadoc, and examples in the codebase. [unverified — specific inference mechanisms are the author's synthesis, not detailed in the paper]

**Call ordering**: Which methods must be called before others? Constructor before method calls, open before read, initialize before use. The agent can reason about object lifecycle from the API surface. [unverified — reasoning approach is the author's synthesis]

**State coverage**: Which code paths require specific preconditions to be reachable? An authenticated session, a populated collection, a configured subsystem. Coverage feedback identifies when state assumptions are wrong.

## Implementation Considerations

- **Start with shallow APIs first**: Simple, pure functions with scalar parameters establish a coverage baseline before you tackle stateful APIs
- **Use typed API surfaces**: Strongly typed APIs (generics, sealed types) give the agent more inference signal than loosely typed ones
- **Instrument for path coverage, not just line coverage**: Branch coverage catches more conditional logic than line coverage alone
- **Review before production fuzzing**: Generated harnesses may exercise APIs in unintended sequences — review for crash-on-startup conditions before you target production builds
- **Corpus seeding**: Provide a seed corpus of valid inputs alongside the harness to give the fuzzer a head start on interesting paths

## Generalization

The paper demonstrates the pattern on Java libraries. The feedback loop — generate, measure coverage, refine — could in principle apply to other typed API surfaces you work with (C/C++ with libFuzzer/AFL, Python with Atheris, Rust with cargo-fuzz), but cross-language generalization has not been validated [unverified].

## Key Takeaways

- Coverage data provides a grounded iteration signal that replaces your intuition about which API call sequences to try
- The agent's value is in reasoning about parameter constraints and call ordering, not in writing fuzzer boilerplate
- Review generated harnesses before targeting production systems
- Strong typing and documentation quality directly improve harness generation accuracy

## Unverified Claims

- "Weeks to hours" time reduction for harness generation [unverified — the "weeks to hours" time reduction claim has not been independently confirmed from the cited paper]
- Agent infers parameter constraints from type signatures, Javadoc, and codebase examples [unverified — specific inference mechanisms are the author's synthesis, not detailed in the paper]
- Agent reasons about object lifecycle from the API surface for call ordering [unverified — reasoning approach is the author's synthesis]
- Cross-language generalization to C/C++, Python, Rust fuzzing [unverified]

## Example

A Java library exposes a `Parser` class. The agent starts by inspecting the public API surface and generating an initial harness:

```java
// Generated harness v1 — covers only the top-level parse path
public static void fuzzerTestOneInput(byte[] data) {
    String input = new String(data, StandardCharsets.UTF_8);
    try {
        Parser parser = new Parser();
        parser.parse(input);
    } catch (ParseException e) {
        // expected — not a crash
    }
}
```

Coverage report shows 12% branch coverage. The agent identifies that `Parser.parse()` returns a `Document` and that `Document.validate()` exercises a separate branch tree. It refines:

```java
// Generated harness v2 — adds document validation path
public static void fuzzerTestOneInput(byte[] data) {
    String input = new String(data, StandardCharsets.UTF_8);
    try {
        Parser parser = new Parser();
        Document doc = parser.parse(input);
        if (doc != null) {
            doc.validate();           // new: exercises validation branches
            doc.getChildren();        // new: exercises tree traversal
        }
    } catch (ParseException | ValidationException e) {
        // expected
    }
}
```

Coverage increases to 34%. The agent continues iterating until coverage plateaus or the configured iteration budget is exhausted.

## Related

- [Red-Green-Refactor with Agents](red-green-refactor-agents.md)
- [Test-Driven Agent Development](tdd-agent-development.md)
- [Evaluator-Optimizer Pattern](../agent-design/evaluator-optimizer.md)
- [Incremental Verification](incremental-verification.md)
