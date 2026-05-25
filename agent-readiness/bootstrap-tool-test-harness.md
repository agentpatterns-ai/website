---
title: "Bootstrap Tool Test Harness"
description: "Detect agent-callable tools, scaffold per-tool isolated test cases that exercise selection, parameters, and output handling, generate the runner and CI gate, and ship a template for new tools."
tags:
  - tool-agnostic
  - tool-engineering
  - testing-verification
aliases:
  - tool unit-test scaffold
  - per-tool test harness
  - independent tool testing scaffold
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-tool-test-harness/`

# Bootstrap Tool Test Harness

> Detect agent-callable tools, scaffold per-tool isolated test cases for selection, parameters, and output handling, generate the runner and CI gate, ship a template for new tools.

!!! info "Harness assumption"
    Tools surface through MCP servers (`.mcp.json`), project-defined function-tools, or HTTP endpoints documented in `AGENTS.md`. The runner invokes a single tool in isolation, asserting the model's selection and call shape — not full end-to-end agent behavior. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Defer this runbook until the project ships at least one tool intended for repeated agent use. One-off scripts and prototype tools do not justify the test scaffold ([`tool-engineering`](../tool-engineering/tool-engineering.md) §When This Backfires).

Errors observed in full agent loops are ambiguous: prompt, tool, or interaction. Isolated per-tool tests surface tool-specific misuse early — wrong parameter selection, wrong type, mishandling of error shapes — without the noise of a multi-turn session ([`tool-engineering`](../tool-engineering/tool-engineering.md) §Independent Testing). This runbook produces the minimum scaffold; mature projects layer per-tool benchmarks and contract tests on top. Rules from [`tool-engineering`](../tool-engineering/tool-engineering.md) and [`tool-description-quality`](../tool-engineering/tool-description-quality.md).

## Step 1 — Detect Existing Tool Tests

```bash
# Existing tool tests
find . -path "*tool_tests*" -o -path "*tools/tests*" -o -name "test_tool_*.py" \
  ! -path "*/node_modules/*" 2>/dev/null

# Tools to test
test -f .mcp.json && jq '.servers // .mcpServers | keys' .mcp.json
find . -path "*/tools/*.py" -o -path "*/tools/*.json" \
  ! -path "*/node_modules/*" 2>/dev/null | head -20

# Existing eval suite (the per-agent layer above this one)
test -d evals && echo "evals/ exists; tool tests are a layer below"
```

Decision rules:

- **`tool-tests/` exists** → audit, do not overwrite; merge new cases only
- **No tools defined** → defer; revisit when tools are added
- **`evals/` exists but no tool tests** → bootstrap; the layers complement (evals measure end-to-end, tool tests measure per-call)

## Step 2 — Generate Directory Structure

```
tool-tests/
├── README.md
├── cases/
│   └── <tool-name>/
│       ├── selection.yaml      # does the model pick this tool?
│       ├── parameters.yaml     # does it call with valid args?
│       └── output.yaml         # does it handle the response?
├── run.sh
├── runner.py
└── new-tool-template.md
```

```bash
mkdir -p tool-tests/cases
```

## Step 3 — Scaffold Per-Tool Cases

For each tool found in Step 1, generate three case files. The three axes mirror [`tool-engineering`](../tool-engineering/tool-engineering.md) §Independent Testing.

`tool-tests/cases/<tool>/selection.yaml`:

```yaml
tool: <tool-name>
axis: selection
description: |
  The model receives a task that should route to <tool-name>. Verify it
  selects this tool over alternatives.

cases:
  - id: selection-direct
    user_message: "<verbatim task that names the tool's primary use case>"
    expected:
      tool_invoked: <tool-name>
  - id: selection-paraphrased
    user_message: "<same task, paraphrased without the tool's verb>"
    expected:
      tool_invoked: <tool-name>
  - id: selection-negative
    user_message: "<task that looks similar but should route elsewhere>"
    expected:
      tool_invoked_not: <tool-name>
```

`tool-tests/cases/<tool>/parameters.yaml`:

```yaml
tool: <tool-name>
axis: parameters
cases:
  - id: required-args
    user_message: "<task requiring all required args>"
    expected:
      args_present: [<arg1>, <arg2>]
      args_types_match: true
  - id: enum-honored
    user_message: "<task that targets an enum field>"
    expected:
      args:
        <enum-field>: <one-of-allowed-values>
  - id: invalid-input-rejected
    user_message: "<task requiring an out-of-range value>"
    expected:
      tool_returned_error: true
      error_kind: invalid_range
```

`tool-tests/cases/<tool>/output.yaml`:

```yaml
tool: <tool-name>
axis: output
cases:
  - id: structured-success
    fixture_response:
      <field>: <value>
    expected:
      model_extracts: [<field>]
      model_does_not_fabricate: true
  - id: error-shape
    fixture_response:
      error: invalid_input
      detail: "missing required arg"
    expected:
      model_recovers_or_asks_user: true
```

Generate one `<tool>/` subdirectory per tool. Use real example tasks from the project's issues, support tickets, or sample prompts — paraphrased only when no real example exists.

## Step 4 — Generate the Runner

`tool-tests/runner.py`:

```python
# tool-tests/runner.py — minimum viable scaffold
import argparse, json, subprocess, sys, yaml

def invoke_with_tool(user_message, tool_name, fixture=None):
    """Invoke the agent harness with exactly one tool registered. Capture
    the first tool call (or absence) and the model's final response.
    Returns: {invoked: <name|null>, args: <dict|null>, response: <str>}.
    """
    # Implementation depends on the harness:
    # - Claude Code: subprocess --skip-skills "*" --include-tool <tool>
    # - API direct: list one tool in the request
    # - MCP: register a single server in a one-shot config
    raise NotImplementedError("wire to your harness")

def grade(case, result):
    failures = []
    exp = case.get('expected') or {}
    if exp.get('tool_invoked') and result['invoked'] != exp['tool_invoked']:
        failures.append(f"expected {exp['tool_invoked']}, got {result['invoked']}")
    if exp.get('tool_invoked_not') and result['invoked'] == exp['tool_invoked_not']:
        failures.append(f"selected forbidden tool {result['invoked']}")
    for arg in exp.get('args_present', []):
        if arg not in (result.get('args') or {}):
            failures.append(f"missing arg {arg}")
    fixed = exp.get('args') or {}
    for k, v in fixed.items():
        if (result.get('args') or {}).get(k) != v:
            failures.append(f"arg {k}: expected {v}, got {(result.get('args') or {}).get(k)}")
    return {"status": "pass" if not failures else "fail", "failures": failures}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--case", required=True)
    args = p.parse_args()
    case = yaml.safe_load(open(args.case))
    results = []
    for c in case['cases']:
        r = invoke_with_tool(c['user_message'], case['tool'], c.get('fixture_response'))
        results.append({"id": c['id'], **grade(c, r)})
    print(json.dumps(results, indent=2))
    if any(r['status'] == 'fail' for r in results):
        sys.exit(1)
```

`tool-tests/run.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
FAIL=0
for case in tool-tests/cases/*/*.yaml; do
  python3 tool-tests/runner.py --case "$case" || FAIL=$((FAIL+1))
done
[[ $FAIL -gt 0 ]] && { echo "$FAIL case file(s) failed"; exit 1; } || exit 0
```

`chmod +x tool-tests/run.sh`.

## Step 5 — Generate the CI Gate

For projects on GitHub Actions, `.github/workflows/tool-tests.yml`:

```yaml
name: tool-tests
on:
  pull_request:
    paths:
      - '.mcp.json'
      - 'tools/**'
      - 'tool-tests/**'
jobs:
  tool-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install pyyaml
      - run: bash tool-tests/run.sh
```

Adapt to whichever CI the project uses; Match the runner OS to a Unix-shell environment. Set as a required check on the default branch when the suite has at least one passing case per tool.

## Step 6 — Ship the New-Tool Template

`tool-tests/new-tool-template.md`:

```markdown
# New Tool — Test Cases

Before merging a new tool definition, add three case files: `selection.yaml`,
`parameters.yaml`, `output.yaml` under `tool-tests/cases/<tool-name>/`.

## Selection cases (≥3)

- One direct invocation
- One paraphrased invocation
- One adversarial — task that should route elsewhere

## Parameter cases (≥3)

- Required-args coverage
- Enum / range honoring
- Invalid input rejected

## Output cases (≥2)

- Structured success — assert the model extracts the right fields
- Error shape — assert the model recovers or asks the user

Each case uses real (or paraphrased real) user input. Do not invent inputs.
```

## Step 7 — Smoke Test

```bash
bash tool-tests/run.sh
```

Confirm at least one case passes per tool. If the runner errors, the harness wiring in Step 4 is wrong; debug before merging.

## Step 8 — Wire-Before-Register Safety

If the project also adds the gate to `branch_protection` or `required_status_checks`, do that **after** the workflow has run successfully on at least one PR. Marking a non-existent or failing job as required blocks all merges.

```bash
gh api -X GET "repos/$REPO/branches/main/protection/required_status_checks" 2>/dev/null \
  | jq '.contexts | index("tool-tests")' \
  | grep -q null \
  || echo "tool-tests already required; verify it has run before this branch landed"
```

## Idempotency

Re-running adds new tool subdirectories under `tool-tests/cases/`; never overwrites existing case files. Existing cases are touched only if the underlying tool definition changes shape.

## Output Schema

```markdown
# Bootstrap Tool Test Harness — <repo>

| Action | File | Notes |
|--------|------|-------|
| Created | tool-tests/run.sh | mode 0755 |
| Created | tool-tests/runner.py | <n> lines |
| Created | tool-tests/cases/<tool>/*.yaml | <n> tools, <n> cases |
| Created | tool-tests/new-tool-template.md | |
| Created | .github/workflows/tool-tests.yml | not yet required |

Smoke run: <n>/<n> pass
```

## Related

- [Tool Engineering](../tool-engineering/tool-engineering.md)
- [Tool Description Quality](../tool-engineering/tool-description-quality.md)
- [Poka-Yoke for Agent Tools](../tool-engineering/poka-yoke-agent-tools.md)
- [Eval-Driven Tool Development](../workflows/eval-driven-tool-development.md)
- [Audit Tool Descriptions](audit-tool-descriptions.md)
- [Audit Tool Idempotency](audit-tool-idempotency.md)
- [Audit Tool Error Format](audit-tool-error-format.md)
- [Bootstrap Eval Suite](bootstrap-eval-suite.md)
