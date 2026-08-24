---
title: "Execution Budgeting in Agentic Program Repair"
term: "Execution Budgeting"
description: "Treat test execution in agentic repair loops as a budgeted resource rather than a default reflex — under specific preconditions on model strength, codebase familiarity, and execution cost."
tags:
  - testing-verification
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - "test-execution budget for repair agents"
  - "execution-frequency cost trade-off"
last_reviewed: 2026-06-26
maturity: emerging
---

# Execution Budgeting in Agentic Program Repair

> Cap how often a repair agent runs tests — frontier models converge with far fewer executions than they reflexively perform.

Execution budgeting reframes the test run in a generate-run-revise loop as a resource the agent spends, not a reflex it fires. A two-stage study of 7,745 SWE-bench Verified agent traces and 3,000 controlled repair attempts across four execution paradigms finds that frontier commercial agents (Claude Code, Codex, OpenCode) execute tests an average of 8.8 times per task, with a range of 2 to 19. Prohibiting execution entirely drops the resolve rate by only about 1.25 percentage points — a statistically non-significant change against a large token and wall-clock saving ([Lin et al., 2026](https://arxiv.org/abs/2606.26978v1)).

## When this pattern applies

The headline result narrows hard. Lead with the preconditions, because the savings evaporate when any one fails.

1. The agent is a frontier commercial model. The 1.25-point drop is measured on Claude Code, Codex, and OpenCode — agents backed by models that carry enough in-weight knowledge of common Python idioms and SWE-bench-representative bug patterns to converge on a fix without ground-truth feedback on every iteration ([Lin et al., 2026](https://arxiv.org/abs/2606.26978)). Smaller or open-weight models depend more on execution feedback as a learning signal. RLEF shows that a Llama-3.1-8B grounded in execution feedback beats GPT-4 in iterative mode on CodeContests ([Gehring et al., 2024](https://arxiv.org/abs/2410.02089)). Budgeting execution on a weaker agent hurts repair quality.
2. The codebase is in the model's training distribution. SWE-bench draws from popular open-source Python projects the frontier models have seen during pre-training. On private monorepos, internal frameworks, or unfamiliar languages, the agent has no in-weight prior to substitute for runtime evidence. Lin et al. do not measure this case, so do not extrapolate.
3. Each execution carries real cost. The trade-off only matters when a test run costs API tokens, sandbox time, or container spin-up. When tests run locally in under a second with no metered cost, frequency-tuning is wasted effort, so let the agent run tests freely.

When all three hold, capping or strategically triggering execution recovers most of the cost while losing almost none of the success rate. When any one fails, the simpler default is the right call: let the agent execute freely.

## The mechanism

Execution provides information, and that information has a cost. The question is the marginal value of the next execution, given what the agent already knows from the diff. Lin et al. find that frontier agents iterate past the point of diminishing returns. They re-run tests on variants whose outcomes the diff already implies. The empirical signature is that execution's benefit is concentrated, not uniform. A small subset of instances accounts for most of the value, and current agents apply execution everywhere rather than where it pays off ([Lin et al., 2026](https://arxiv.org/abs/2606.26978)).

Two mechanisms coexist. First, execution feedback is causally load-bearing — RLEF's training-time grounding of code LLMs in real error messages shows an order-of-magnitude gain over blind sampling ([Gehring et al., 2024](https://arxiv.org/abs/2410.02089)). Second, frontier agents at inference time apply that signal past the point where the marginal run pays. The first mechanism justifies execution existing in the loop. The second justifies budgeting how often it fires.

## How to budget

The paper compares four execution paradigms: free (the default, where the agent decides), prohibited (no execution allowed), coarse-grained (one execution per repair attempt), and fine-grained (selective execution based on repair stage) ([Lin et al., 2026](https://arxiv.org/abs/2606.26978)). The prohibition mode is the headline. Coarse-grained and fine-grained land between free and prohibited.

Practical translations into a repair harness:

- Hard cap per task: set a maximum of 3 to 5 test executions per repair attempt. That sits below the 8.8 average and above the floor where most agents converge on commercial models.
- Stage-gated execution: allow execution only after explicit checkpoints, such as initial reproduction and post-patch verification, not as a generic tool the agent invokes at will. This matches the fine-grained paradigm.
- Cost-aware tool description: write the test-runner description as "expensive; use sparingly; one run typically suffices per patch variant" rather than "runs the test suite." Models follow tool descriptions, so the description is policy.
- No budget at all on weak or out-of-distribution settings (see the preconditions above).

The exact cap is a tuning parameter, not a constant. Lin et al. did not publish a universal optimum. Calibrate on the actual repair workload before you lock a number into harness code.

## Why it works

The cost saving comes from skipping redundant confirmations. The success retention comes from the diff being informative enough to substitute. On SWE-bench-distribution bugs, a frontier model's first or second patch is already close to the correct fix, and later runs largely confirm what the diff already implied. That is why prohibiting execution drops the resolve rate by only about 1.25 points on commercial models ([Lin et al., 2026](https://arxiv.org/abs/2606.26978)). The claim is narrow. Execution remains causally load-bearing when models are trained to consume it well ([Gehring et al., 2024](https://arxiv.org/abs/2410.02089)); only the frequency at inference time has overshot the point of diminishing returns.

## When this backfires

The model is not a frontier commercial agent. Smaller models, fine-tunes, or open-weight agents rely more on execution as a substitute for in-weight knowledge. The 1.25-point number is not portable, and on weaker setups, prohibiting execution can collapse the resolve rate ([Gehring et al., 2024](https://arxiv.org/abs/2410.02089)).

The codebase is unfamiliar to the model. Lin et al. measured on SWE-bench Verified — popular Python open-source projects the frontier models have seen. On private monorepos, in-house DSLs, embedded firmware, or any setting where the model has no learned prior, execution is the agent's only correctness signal. Capping it blinds the loop.

The test suite is the only correctness oracle. SWE-bench's developer tests are themselves an unreliable signal — 7.8% of test-passing patches fail the developer suite outright, and 29.6% diverge behaviorally from the ground-truth patch ([Aleithan et al., 2025](https://arxiv.org/abs/2503.15223v2)). When tests are the deployment gate and there is no human review or separate spec, fewer test runs means fewer chances to catch a near-miss. Pair execution budgeting with [baseline-aware test evaluation](baseline-aware-test-evaluation-issue-resolution.md) and [staged evidence gates](staged-evidence-gates-program-repair.md) rather than substituting it for them.

The test suite is flaky. A single test run under-samples a stochastic outcome, and the agent that runs more often gets a better read on whether a failure is real or noise. Capping execution under flakiness turns a recoverable signal into a hidden one. Stabilize the suite before you budget how often it runs.

Execution is cheap. Sub-second local pytest runs with no API cost invert the premise. The trade-off Lin et al. measured assumes each execution carries enough time and token cost that 8.8 of them per task matter. Strip that cost away and budgeting is overhead.

## Example

A minimal budget in an MCP tool description:

```yaml
# Tool description the agent reads
name: run_tests
description: |
  Run the project test suite against the current working tree.
  EXPENSIVE: each run costs ~30s of sandbox time and ~5k tokens of output.
  Budget: 3 invocations per repair attempt. After 3, the harness will refuse.
  Use sparingly — usually one run after each patch variant is enough.
inputs:
  pattern: string  # optional pytest -k filter
```

And the harness enforcement:

```python
class BudgetedTestRunner:
    MAX_RUNS_PER_ATTEMPT = 3

    def __init__(self):
        self.runs = 0

    def run(self, pattern: str | None = None) -> dict:
        if self.runs >= self.MAX_RUNS_PER_ATTEMPT:
            return {
                "error": "budget_exhausted",
                "message": (
                    f"{self.MAX_RUNS_PER_ATTEMPT} test runs already used. "
                    "Submit your best patch — no further test feedback available."
                ),
            }
        self.runs += 1
        return _execute_pytest(pattern)
```

The shape is the load-bearing part: a hard cap with an explicit "submit your best patch" message when the budget runs out. The exact ceiling is a calibration knob, not a constant.

## Key Takeaways

- Test execution in a repair loop is a budgeted resource, not a default reflex — frontier agents over-execute past the point where each run produces new evidence ([Lin et al., 2026](https://arxiv.org/abs/2606.26978)).
- Prohibiting execution drops the resolve rate by only about 1.25 points on commercial models against SWE-bench Verified, and that result narrows hard to frontier-model, in-distribution, expensive-execution settings.
- Execution feedback is causally load-bearing during training and on weaker models — RLEF shows execution-grounded small models beat un-grounded large models ([Gehring et al., 2024](https://arxiv.org/abs/2410.02089)). Do not generalize budgeting to those settings.
- Encode the budget in both the tool description and harness enforcement, because both are policy. Cost-aware tool descriptions guide model behavior, and hard limits catch it when guidance fails.
- Budget execution alongside other verification gates, not instead of them. The test signal itself is weak — about 20% of test-passing patches are semantically wrong on SWE-bench ([Aleithan et al., 2025](https://arxiv.org/abs/2503.15223v2)) — so fewer runs of a weak oracle is no substitute for stronger gates.

## Related

- [Staged Evidence Gates for Agentic Program Repair](staged-evidence-gates-program-repair.md) — staging orders which gates run; this page argues how often to run any of them.
- [Bounded Repair-Loop Iterations](bounded-repair-loop-iterations.md) — caps how many repair rounds run; this page caps how many test executions run inside a round.
- [Baseline-Aware Test Evaluation for Multi-Agent Issue Resolution (Phoenix)](baseline-aware-test-evaluation-issue-resolution.md) — strengthens what one test run tells you, so the budget can stretch further.
- [Cost-Aware Skill Rewriting](../instructions/cost-aware-skill-rewriting.md) — the broader practice of making cost explicit in instructions and tool descriptions agents read.
- [Token-Efficient Tool Design](../token-engineering/token-efficient-tool-design.md) — adjacent tool-level cost lever; reduces the cost per execution rather than the count of executions.
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — why "execution prohibited" sounds dangerous but isn't on the measured slice — the slice itself is the load-bearing claim.
- [Profiler-Guided Optimization Loops for Coding Agents](profiler-guided-optimization-loop.md) — the performance-optimization case, where a run is the objective signal rather than a cost to cap.
