---
title: "Predicting Which AI-Generated Functions Will Be Deleted"
description: "Identify AI-generated functions likely to be deleted before PR review using structural analysis of call graphs and spec coverage."
tags:
  - testing-verification
  - human-factors
aliases:
  - "Pre-Flagging Functions for Review"
  - "Code Deletion Prediction"
---

# Predicting Reviewable Code: Pre-Flagging Functions Reviewers Will Delete

> AI-generated code produces functions that are routinely deleted during PR review; predictive models can identify likely-to-be-deleted functions before reviewers spend time examining them.

## The Review Burden Shift

Agentic coding tools shift work from writing to reviewing. When an agent generates a PR, reviewers must examine code they will ultimately delete — dead code, over-engineered helpers, spec-mismatched implementations. [arXiv:2602.17091](https://arxiv.org/abs/2602.17091) shows that AI-generated PRs contain a notable portion of functions deleted during review, and that deletion reasons produce distinct structural characteristics predictable with AUC 87.1%.

The implication: reviewers are spending time on code that a pre-filter could have flagged first.

## Deletion Reason Categories

The paper identifies structural features that distinguish deleted from surviving functions — it does not provide a formal taxonomy of deletion reasons. Based on those structural signals, deleted functions cluster into three practitioner-facing categories:

**Dead code**: Functions generated but never called from the PR's entry points. Structurally, they exhibit lower call counts and fewer inbound references — consistent with the paper's finding that deleted functions have higher internal complexity but lower integration with surrounding code.

**Over-engineering**: Functions that introduce abstraction the spec did not require — utility helpers, base classes, factory patterns for single-instantiation objects. Structurally, they appear as longer method names, higher line counts, and greater Halstead volume — the paper's three strongest predictors of deletion — because they implement more than the task asked for.

**Spec mismatch**: Functions that implement a different behavior than the spec required — wrong signature, wrong return type, wrong preconditions. They diverge from the spec's type contracts and often carry redundant documentation that mirrors, rather than extends, the spec language.

Each category calls for a different remediation signal sent back to the agent.

## Why It Works

Structural metrics expose scope overreach before a reviewer reads a single line. [arXiv:2602.17091](https://arxiv.org/abs/2602.17091) found that the strongest predictors of deletion are method name length (word count), total lines of code, and Halstead volume — all proxies for "more was generated than the task required." A function with a long descriptive name and high Halstead volume encodes more conceptual surface area than a focused function; that excess surface area is what reviewers remove. The model achieves AUC 87.1% using only these static, syntax-level features — no semantic understanding of the spec is needed to flag probable deletions.

## Applying Predictive Pre-Flagging

Before routing a generated PR to human review, run structural analysis to identify high-deletion-probability functions:

```mermaid
graph TD
    A[Agent generates PR] --> B[Call graph analysis]
    B --> C[Dead code detector]
    A --> D[Spec coverage check]
    D --> E[Spec mismatch detector]
    A --> F[Complexity vs spec scope]
    F --> G[Over-engineering detector]
    C --> H[Pre-flag report]
    E --> H
    G --> H
    H --> I{Flags above threshold?}
    I -->|Yes| J[Return report]
    I -->|No| K[Human review]
```

The pre-flag report tells the reviewer where to focus. It optionally returns flagged functions to the agent for regeneration before human time is spent.

## Implications for Agent Scope Instructions

The research outcome is a direct input to agent prompting. You can configure your agent's scope instructions to target each deletion category:

- **Emit only called code**: Require that generated functions are reachable from specified entry points
- **Match spec scope**: Instruct the agent not to abstract beyond what the spec requires in the current task
- **Declare external dependencies explicitly**: Use these signals to flag functions that depend on context outside the PR rather than letting the agent silently generate them

Fewer generated functions that survive review is a better outcome than more generated functions with higher deletion rate.

## Reviewer Workflow Adaptation

When pre-flagging is not integrated into the pipeline, human reviewers can apply the same mental model manually:

- Check call graph coverage first: is every generated function called?
- Compare function count against spec complexity: does the implementation scope match the ask?
- Verify type signatures against the spec before reading implementation bodies

This ordering surfaces the likely deletions before investing in line-by-line reading.

## Why It Works

Deletion during review is a structural signal: code the agent generated that does not match what the reviewer needs to approve. Each deletion category has a mechanical trace — call graph edges are absent, spec scope is exceeded, or type contracts diverge. These traces are computable before a human reads the code. The AUC 87.1% result ([arXiv:2602.17091](https://arxiv.org/abs/2602.17091)) follows from the same principle: deletion reasons correlate with structural properties, and structural properties are extractable from the diff without running the code or understanding its semantics.

## When This Backfires

Pre-flagging is not cost-free:

- **False positives on valid abstraction**: A shared utility helper may be called from a future PR, not the current one. Single-module call graph analysis flags it as dead code; it isn't.
- **Cross-file blindness**: Structural analysis scoped to the generated module misses call sites in files the agent didn't modify. This inflates the dead-code false-positive rate in multi-file PRs.
- **Spec ambiguity**: If the spec is underspecified, "spec mismatch" becomes the reviewer's judgment call, not a structural signal. Pre-flagging then adds friction without surfacing real problems.
- **Pipeline integration cost**: Instrumenting call graph extraction per PR requires tooling investment. For low-volume PR teams, the ROI may not justify the setup.

Apply pre-flagging where agent PR volume is high enough that reviewer time is the binding constraint.

## Example

The following script demonstrates dead code detection by checking call graph reachability. It identifies functions in a generated module that are never called from the PR's entry point — the most mechanically detectable deletion category.

```python
import ast
import sys
from pathlib import Path

def get_defined_functions(source: str) -> set[str]:
    tree = ast.parse(source)
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

def get_called_functions(source: str) -> set[str]:
    tree = ast.parse(source)
    return {node.func.id for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}

def flag_dead_code(filepath: str) -> list[str]:
    source = Path(filepath).read_text()
    defined = get_defined_functions(source)
    called = get_called_functions(source)
    # Entry point functions (e.g. main, handler) are excluded from the dead-code check
    entry_points = {"main", "handler", "lambda_handler"}
    dead = defined - called - entry_points
    return sorted(dead)

if __name__ == "__main__":
    dead = flag_dead_code(sys.argv[1])
    if dead:
        print("Pre-flag: likely dead code (never called within module):")
        for fn in dead:
            print(f"  - {fn}")
        sys.exit(1)
    print("No dead code detected.")
```

Running this against a generated module before routing to review:

```bash
python flag_dead_code.py generated_module.py
# Pre-flag: likely dead code (never called within module):
#   - build_cache_key
#   - _legacy_format
```

These two functions would be candidates for deletion. Returning this report to the agent — rather than a human reviewer — eliminates the review cycle for spec-mismatched generated code before a human sees it.

## When This Backfires

Pre-flagging adds value when the cost of reviewer time exceeds the cost of running structural analysis, but several conditions undermine that trade-off:

- **Infrastructure and setup functions**: Functions not yet called within the PR — setup hooks, migration helpers, exported API surface — will appear as dead code to a call-graph analyzer. Treat entry-point configuration as a first-class parameter, not an afterthought.
- **Cross-file call graphs are expensive**: Dead code detection that only inspects the generated module (as in the example above) misses legitimate calls from existing files. Building a full project call graph adds pipeline latency and may require language-specific tooling.
- **Single-study generalization risk**: The AUC 87.1% result comes from one codebase and one AI model. Structural feature importance will differ across languages, project types, and model generations — validate false-positive rates on local data before routing suppressions to the agent.
- **False negatives pass bad code unexamined**: A 12.9% error rate means roughly 1-in-8 deletable functions is not flagged. Reviewers who rely on the report may skip unflagged code more quickly than they should, increasing the cost of each missed deletion.
- **False positives block valid abstractions**: A utility function called only once looks like over-engineering by metrics but may be essential for testability or future extension. Flags routed back to the agent can cause regeneration that removes intentional design decisions.
- **Feedback loop without calibration**: Returning flagged functions to the agent for regeneration without calibrating what "spec scope" means can cause under-generation in future tasks. A regeneration count limit and human fallback are necessary to prevent loops.

## Key Takeaways

- AI-generated PRs shift the bottleneck from writing to reviewing; predictive pre-filtering reduces the cost of that shift
- Functions deleted for dead code, over-engineering, and spec mismatch have distinct structural characteristics that are statistically predictable
- Agent scope instructions should target the root causes: require reachability, prohibit over-abstraction, match spec scope exactly
- Pre-flag reports returned to the agent before human review reduce total review cost

## Related

- [Agent-Assisted Code Review](agent-assisted-code-review.md)
- [Agent-Authored PR Integration and Merge Predictors](agent-authored-pr-integration.md)
- [Agentic Code Review Architecture](agentic-code-review-architecture.md)
- [Committee Review Pattern](committee-review-pattern.md)
- [Diff-Based Review Over Output Review](diff-based-review.md)
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md)
- [Tiered Code Review: AI-First with Human Escalation](tiered-code-review.md)
- [PR Description Style as a Lever for Agent PR Merge Rates](pr-description-style-lever.md)
- [Review-Then-Implement Loop](review-then-implement-loop.md)
- [Risk-Based Task Sizing for Agent Verification Depth](../verification/risk-based-task-sizing.md)
- [Specification as Prompt](../instructions/specification-as-prompt.md)
- [Trust Without Verify](../anti-patterns/trust-without-verify.md)
- [Abstraction Bloat](../anti-patterns/abstraction-bloat.md) — the training incentive that produces over-engineered code and drives the over-engineering deletion category
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md)
- [Human-AI Review Synergy](human-ai-review-synergy.md)
