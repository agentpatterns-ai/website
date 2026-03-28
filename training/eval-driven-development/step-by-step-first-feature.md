---
title: "Step-by-Step: Building Your First Eval-Driven Feature"
description: "Hands-on walkthrough building a PR description generator with eval-driven development — from eval tasks through graders, baselines, and iteration."
tags:
  - training
  - testing-verification
  - evals
  - tool-agnostic
  - hands-on
---

# Step-by-Step: Building Your First Eval-Driven Feature

> A hands-on walkthrough — build a PR description generator from scratch using the eval-first development loop, with complete task definitions, graders, and iteration examples.

[Eval-driven development](../../workflows/eval-driven-development.md) starts by defining measurable success criteria — eval tasks and graders — before writing any agent code. The feature built here is a PR description generator that takes a git diff as input and produces a structured description. Each step below follows the eval-first loop: define tasks, build graders, run a baseline, implement, iterate until the bar is met, then ship.

---

## The Feature

**Goal**: build an agent that takes a git diff as input and produces a well-structured PR description.

**Requirements**:

- Include a summary section (1–3 bullet points describing what changed and why)
- Include a test plan section (what should be tested before merging)
- Identify the type of change (feature, bugfix, refactor, docs, etc.)
- Flag any files that might need special review attention (config changes, migrations, security-sensitive files)
- Keep total length under 500 words

This is a good teaching example because it has both **deterministic** aspects (structure, length, required sections) and **subjective** aspects (quality of summary, helpfulness of test plan).

---

## Step 1: Define Eval Tasks Before Writing Any Code

Write tasks based on what the agent *should* do, not what it currently does. Source from real scenarios.

```yaml
# evals/pr-description/tasks.yaml

# --- Category: Standard changes ---

- id: simple-bugfix
  description: "Single-file bugfix with obvious root cause"
  input:
    diff: |
      diff --git a/src/auth/login.py b/src/auth/login.py
      --- a/src/auth/login.py
      +++ b/src/auth/login.py
      @@ -42,7 +42,7 @@ def validate_token(token: str) -> bool:
      -    if token.expires_at > datetime.now():
      +    if token.expires_at < datetime.now():
               return False
           return verify_signature(token)
  expected:
    change_type: "bugfix"
    summary_mentions: ["token expiration", "comparison", "reversed"]
    has_sections: ["summary", "test_plan"]
    max_words: 500
    flags_files: false

- id: multi-file-feature
  description: "New feature spanning multiple files with tests"
  input:
    diff: |
      diff --git a/src/api/routes.py b/src/api/routes.py
      --- a/src/api/routes.py
      +++ b/src/api/routes.py
      @@ -1,4 +1,5 @@
       from flask import Blueprint
      +from .middleware import rate_limit

       api = Blueprint("api", __name__)

      @@ -10,6 +11,12 @@ def get_users():
      +@api.route("/users/<id>/export", methods=["POST"])
      +@rate_limit(requests=10, window=60)
      +def export_user_data(id):
      +    """Export user data as CSV."""
      +    user = User.query.get_or_404(id)
      +    return generate_csv(user)
      diff --git a/src/api/middleware.py b/src/api/middleware.py
      new file mode 100644
      --- /dev/null
      +++ b/src/api/middleware.py
      @@ -0,0 +1,15 @@
      +def rate_limit(requests, window):
      +    """Rate limiting decorator."""
      +    def decorator(f):
      +        # ... implementation
      +        return f
      +    return decorator
      diff --git a/tests/test_export.py b/tests/test_export.py
      new file mode 100644
      --- /dev/null
      +++ b/tests/test_export.py
      @@ -0,0 +1,10 @@
      +def test_export_user_data():
      +    # ... test implementation
      +    pass
  expected:
    change_type: "feature"
    summary_mentions: ["export", "user data", "rate limit"]
    has_sections: ["summary", "test_plan"]
    max_words: 500
    flags_files: false

# --- Category: Sensitive changes ---

- id: config-change-env-vars
  description: "Change to environment variable configuration"
  input:
    diff: |
      diff --git a/.env.example b/.env.example
      --- a/.env.example
      +++ b/.env.example
      @@ -3,3 +3,5 @@
       DATABASE_URL=postgresql://localhost/app
       REDIS_URL=redis://localhost:6379
      +STRIPE_SECRET_KEY=sk_test_xxx
      +STRIPE_WEBHOOK_SECRET=whsec_xxx
      diff --git a/src/billing/checkout.py b/src/billing/checkout.py
      new file mode 100644
      --- /dev/null
      +++ b/src/billing/checkout.py
      @@ -0,0 +1,8 @@
      +import stripe
      +stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
  expected:
    change_type: "feature"
    summary_mentions: ["billing", "stripe", "payment"]
    has_sections: ["summary", "test_plan"]
    max_words: 500
    flags_files: true
    flagged_patterns: [".env", "secret", "key"]

# --- Category: Edge cases ---

- id: empty-diff
  description: "Empty diff input"
  input:
    diff: ""
  expected:
    error_type: "validation_error"

- id: massive-diff
  description: "Diff with 50+ changed files"
  input:
    diff_file: "fixtures/massive-refactor.diff"
  expected:
    has_sections: ["summary", "test_plan"]
    max_words: 500
    summary_max_bullets: 5

- id: only-deletions
  description: "PR that only removes code"
  input:
    diff: |
      diff --git a/src/legacy/old_api.py b/src/legacy/old_api.py
      deleted file mode 100644
      --- a/src/legacy/old_api.py
      +++ /dev/null
      @@ -1,45 +0,0 @@
      -# Legacy API endpoint - deprecated since v2.0
      -def old_endpoint():
      -    ...
  expected:
    change_type: "refactor"
    summary_mentions: ["remov", "legacy", "deprecat"]
    has_sections: ["summary", "test_plan"]

# --- Category: Subjective quality ---

- id: quality-test-plan-actionable
  description: "Test plan should contain actionable items, not generic advice"
  input:
    diff: |
      diff --git a/src/search/indexer.py b/src/search/indexer.py
      --- a/src/search/indexer.py
      +++ b/src/search/indexer.py
      @@ -15,6 +15,8 @@ class SearchIndexer:
           def reindex(self, batch_size=100):
      +        if self.lock.acquired():
      +            raise IndexerBusyError("Reindex already in progress")
               for batch in chunk(self.documents, batch_size):
                   self.index.add(batch)
  expected:
    has_sections: ["summary", "test_plan"]
    test_plan_quality: "actionable"
    test_plan_not_contains: ["test the changes", "verify it works", "check for regressions"]
```

Seven representative tasks across four categories. Build out to 20–50 by adding more cases in each category: additional standard changes (docs-only, dependency updates, database migrations), more sensitive changes (auth, permissions, CI config), and more edge cases (binary files, merge commits, non-English comments).

---

## Step 2: Build the Grader

Start with code-based grading for structural checks. Add LLM-as-judge only for dimensions code cannot assess.

**Code-based grader** — deterministic, fast, handles structure and content checks:

```python
# evals/pr-description/grader.py
import re


def grade(output: str, expected: dict) -> dict:
    """Grade a PR description against expected criteria.

    Returns {"verdict": "PASS"|"FAIL", "failures": [...]}
    """
    failures = []

    # --- Error cases ---
    if "error_type" in expected:
        if expected["error_type"] not in output:
            failures.append(f"Expected error: {expected['error_type']}")
        return {"verdict": "FAIL" if failures else "PASS", "failures": failures}

    # --- Structural checks ---
    if "has_sections" in expected:
        for section in expected["has_sections"]:
            patterns = [
                rf"##\s*{section.replace('_', ' ')}",
                rf"\*\*{section.replace('_', ' ')}\*\*",
            ]
            if not any(re.search(p, output, re.IGNORECASE) for p in patterns):
                failures.append(f"Missing section: {section}")

    if "max_words" in expected:
        word_count = len(output.split())
        if word_count > expected["max_words"]:
            failures.append(
                f"Too long: {word_count} words (max {expected['max_words']})"
            )

    if "summary_mentions" in expected:
        output_lower = output.lower()
        for term in expected["summary_mentions"]:
            if term.lower() not in output_lower:
                failures.append(f"Summary missing expected mention: {term}")

    if "change_type" in expected:
        if expected["change_type"].lower() not in output.lower():
            failures.append(f"Missing change type: {expected['change_type']}")

    # --- Flagging checks ---
    if expected.get("flags_files") and "flagged_patterns" in expected:
        for pattern in expected["flagged_patterns"]:
            if pattern.lower() not in output.lower():
                failures.append(f"Should have flagged: {pattern}")

    # --- Negative content checks ---
    if "test_plan_not_contains" in expected:
        for phrase in expected["test_plan_not_contains"]:
            if phrase.lower() in output.lower():
                failures.append(f"Test plan contains generic phrase: '{phrase}'")

    return {"verdict": "FAIL" if failures else "PASS", "failures": failures}
```

**LLM-as-judge** — for the `test_plan_quality` dimension that code cannot assess:

```python
# evals/pr-description/judge.py
import json
import anthropic

client = anthropic.Anthropic()

RUBRIC = """
You are evaluating the test plan section of a PR description.

Score 1-5 on this single dimension:

TEST_PLAN_QUALITY: Does the test plan contain specific, actionable testing steps?
- 5: Every item names a concrete scenario with expected behavior
- 4: Most items are specific; one or two are somewhat generic
- 3: Mix of specific and generic items
- 2: Mostly generic ("test the feature", "check for regressions")
- 1: Entirely generic or missing

Output as JSON: {"test_plan_quality": {"score": N, "reason": "..."}}
"""


def judge_test_plan(pr_description: str, diff: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": (
                    f"PR diff:\n{diff}\n\n"
                    f"PR description:\n{pr_description}\n\n{RUBRIC}"
                ),
            }
        ],
    )
    return json.loads(response.content[0].text)
```

Notice the separation: code-based grading handles everything it can (structure, length, content presence, flagging). LLM-as-judge only handles the one dimension that requires subjective judgment (test plan quality). This follows the hierarchy from [Grading Strategies](grading-strategies.md).

---

## Step 3: Create the Runner

```python
# evals/pr-description/run.py
import yaml
from grader import grade
from judge import judge_test_plan


def load_tasks(path="evals/pr-description/tasks.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def run_agent(input_data: dict) -> str:
    """Replace with your actual agent invocation."""
    diff = input_data.get("diff", "")
    if input_data.get("diff_file"):
        with open(input_data["diff_file"]) as f:
            diff = f.read()
    return your_agent.generate_pr_description(diff)


def run_suite(tasks, runs_per_task=3):
    results = []

    for task in tasks:
        task_results = []
        for run_idx in range(runs_per_task):
            try:
                output = run_agent(task["input"])
                verdict = grade(output, task["expected"])

                # Add LLM judge for subjective dimensions
                if task["expected"].get("test_plan_quality"):
                    judge_result = judge_test_plan(
                        output, task["input"].get("diff", "")
                    )
                    score = judge_result["test_plan_quality"]["score"]
                    if score < 3:
                        verdict["failures"].append(
                            f"Test plan quality: {score}/5 — "
                            f"{judge_result['test_plan_quality']['reason']}"
                        )
                        verdict["verdict"] = "FAIL"
            except Exception as e:
                verdict = {"verdict": "ERROR", "failures": [str(e)]}

            task_results.append(verdict)

        pass_rate = sum(
            1 for r in task_results if r["verdict"] == "PASS"
        ) / len(task_results)

        results.append({
            "id": task["id"],
            "pass_rate": pass_rate,
            "runs": task_results,
        })

    return results


if __name__ == "__main__":
    tasks = load_tasks()
    results = run_suite(tasks)

    overall = sum(r["pass_rate"] for r in results) / len(results)
    print(f"\nOverall pass rate: {overall:.0%}")
    print(f"Tasks: {len(results)}")
    for r in results:
        status = "PASS" if r["pass_rate"] == 1.0 else f"{r['pass_rate']:.0%}"
        print(f"  {r['id']}: {status}")
        if r["pass_rate"] < 1.0:
            for run in r["runs"]:
                for f in run.get("failures", []):
                    print(f"    - {f}")
```

---

## Step 4: Run the Baseline

Before writing any agent code, run the suite against whatever you currently have — even if that is nothing.

```
$ python evals/pr-description/run.py

Overall pass rate: 15%
Tasks: 7
  simple-bugfix: 0%
    - Missing section: summary
    - Missing section: test_plan
    - Summary missing expected mention: token expiration
  multi-file-feature: 0%
    - Missing section: summary
    - Missing section: test_plan
  config-change-env-vars: 0%
    - Missing section: summary
    - Should have flagged: .env
  empty-diff: 33%
    - Expected error: validation_error  (2 of 3 runs)
  massive-diff: 0%
    - Too long: 823 words (max 500)
  only-deletions: 33%
    - Missing change type: refactor  (2 of 3 runs)
  quality-test-plan-actionable: 0%
    - Test plan contains generic phrase: 'test the changes'
    - Test plan quality: 2/5 — mostly generic steps
```

Record this baseline. A 15% overall pass rate on a new feature is expected — it defines the gap and makes progress visible as implementation proceeds. [Source: [Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)]

---

## Step 5: Implement the Feature

Now write the agent. With the tasks in hand, you know exactly what to build toward:

```python
# src/pr_agent/describe.py
import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You generate PR descriptions from git diffs.

Output format (Markdown):

## Summary
- 1-3 bullet points: what changed and why

## Change type
One of: feature, bugfix, refactor, docs, chore

## Flagged for review
List any files that need special attention: config changes,
migrations, security-sensitive files (.env, secrets, auth, keys).
If none, write "None."

## Test plan
- Specific, actionable testing steps
- Each item names a concrete scenario and expected behavior
- Never write generic steps like "test the changes" or "verify it works"

Rules:
- Keep total output under 500 words
- If the diff is empty, respond with only: "Error: validation_error — empty diff"
- For large diffs (50+ files), summarize by theme rather than listing every file
"""


def generate_pr_description(diff: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Generate a PR description for this diff:\n\n{diff}",
            }
        ],
    )
    return response.content[0].text
```

Notice how the tasks directly informed the system prompt: the required sections, the 500-word limit, the explicit instruction to avoid generic test plan phrases, and the error handling for empty diffs all come from the task definitions written in Step 1.

---

## Step 6: Run the Suite Again and Iterate

```
$ python evals/pr-description/run.py

Overall pass rate: 71%
Tasks: 7
  simple-bugfix: 100%        <- was 0%
  multi-file-feature: 100%   <- was 0%
  config-change-env-vars: 67% <- was 0%
    - Should have flagged: secret  (1 of 3 runs)
  empty-diff: 100%            <- was 33%
  massive-diff: 67%           <- was 0%
    - Too long: 512 words (max 500)  (1 of 3 runs)
  only-deletions: 100%        <- was 33%
  quality-test-plan-actionable: 67% <- was 0%
    - Test plan quality: 2/5  (1 of 3 runs)
```

Progress: 15% to 71%. Three tasks still fail intermittently. The suite tells you exactly where to focus:

1. **config-change-env-vars** — the agent misses flagging "secret" in some runs. Fix: strengthen the system prompt to explicitly list patterns like `secret`, `key`, `token`, `credential`
2. **massive-diff** — output slightly over 500 words in some runs. Fix: add emphasis on the word limit or add post-processing truncation
3. **quality-test-plan-actionable** — test plan quality inconsistent. Fix: add few-shot examples of good vs. bad test plan items to the prompt

After each change, run the suite again. The cycle repeats until you hit your bar.

---

## Step 7: Set the Bar and Ship

Define the bar before you start iterating — for this feature: **90% overall pass rate across 3 runs per task, with no individual task below 67%**.

```
# After prompt iteration round 2:

Overall pass rate: 95%
Tasks: 7
  simple-bugfix: 100%
  multi-file-feature: 100%
  config-change-env-vars: 100%
  empty-diff: 100%
  massive-diff: 100%
  only-deletions: 100%
  quality-test-plan-actionable: 67%
    - Test plan quality: 2/5  (1 of 3 runs)
```

95% overall, no task below 67%. Bar is met. Ship.

The remaining inconsistency on `quality-test-plan-actionable` is a known limitation — document it and add it to the backlog for the next iteration.

---

## Step 8: Grow the Suite from Production

After launch, add tasks from real usage:

- **User complaints**: "the PR description didn't mention the migration" — new task with a migration diff
- **Incidents**: "the agent flagged every file as needing review" — new task with a normal diff that should not flag anything
- **Edge cases discovered**: binary file diffs, diffs with non-English comments, squash commits bundling multiple features

Each new task strengthens the regression net. See [Hardening Evals for Production](hardening-evals.md) for the full hardening workflow.

---

## What You Practiced

| Concept | Where it appeared |
|---------|------------------|
| Write tasks before code | Steps 1–4 |
| Code-based grading | Step 2: structural checks |
| LLM-as-judge grading | Step 2: test plan quality |
| Running the baseline | Step 4 |
| The eval-first development loop | Steps 5–6 |
| Setting the shipping bar | Step 7 |
| Growing from production incidents | Step 8 |

---

## Key Takeaways

- Define tasks from requirements, not from what the agent currently does
- Mix deterministic checks (structure, length, required content) with subjective checks (quality, helpfulness) across grader types
- Run the baseline before writing any feature code — a low starting pass rate is expected and useful
- Each iteration should show measurable progress on specific failing tasks
- Set the shipping bar before iterating, not after

## Related

- [Writing Your First Eval Suite](writing-first-eval-suite.md) — task design theory
- [Grading Strategies](grading-strategies.md) — grader selection guidance
- [The Eval-First Development Loop](eval-first-loop.md) — the workflow this guide applies
- [Hardening Evals for Production](hardening-evals.md) — what comes after shipping
