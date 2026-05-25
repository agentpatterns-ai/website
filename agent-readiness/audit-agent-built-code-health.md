---
title: "Audit Agent-Built Code Health"
description: "Inventory the code an agent has authored, measure structural-complexity and refactoring-share signals, flag bloat indicators (single-impl factories, dead code, shadow utilities), and emit a prioritized cleanup punch list — invoke when an agent has merged ≥10 PRs into the repo or before scaling agent usage further."
tags:
  - tool-agnostic
  - workflows
  - agent-design
aliases:
  - agent-generated code audit
  - agent codebase health audit
  - bloat audit
---

Packaged as: `.claude/skills/agent-readiness-audit-agent-built-code-health/`

# Audit Agent-Built Code Health

> Locate agent-authored code, measure structural complexity and refactoring share, flag bloat patterns (single-impl factories, dead code, shadow utilities), emit a prioritized cleanup punch list.

!!! info "Harness assumption"
    Agent commits are detectable by trailer (`Co-authored-by: <bot>`, `Agent-Session:`), branch prefix (`copilot/`, `claude/`, `cursor/`), or signing key. If the project does not yet attribute agent commits, run [`bootstrap-agent-commit-attribution`](bootstrap-agent-commit-attribution.md) first — without attribution this audit can only sample whole-repo signals.

!!! info "Applicability"
    Skip when fewer than ten agent PRs have merged or the repo is under six months old — enforcement overhead does not pay back ([Lavaee](https://alexlavaee.me/blog/openai-agent-first-codebase-learnings/), via [`agent-driven-codebase-fingerprint`](../agent-design/agent-driven-codebase-fingerprint.md)). Run before scaling agent fan-out further.

The headline LoC and duplication numbers are not the right summary signal — a 2026 MSR mining study reports duplication effects are "small and inconsistent" and locates the quality risk in structural complexity ([Agarwal et al.](https://arxiv.org/abs/2601.13597)). This audit follows that finding: copy/paste rate is supplementary, cognitive complexity and static-analysis warnings are primary. Rules are drawn from [`agent-driven-codebase-fingerprint`](../agent-design/agent-driven-codebase-fingerprint.md), [`abstraction-bloat`](../anti-patterns/abstraction-bloat.md), and [`comprehension-debt`](../anti-patterns/comprehension-debt.md).

## Step 1 — Inventory Agent-Authored Code

```bash
# Detect agent commits via trailer or branch prefix
AGENT_COMMITS=$(git log --all --pretty='%H %s' --grep='Agent-Session:' --grep='Co-authored-by:.*\(bot\|copilot\|claude\)' \
  -E -i | awk '{print $1}')
AGENT_BRANCH_COMMITS=$(git log --all --pretty='%H %s' --grep='^\(copilot\|claude\|cursor\)/' -E | awk '{print $1}')

# Files touched by agent commits (last 90 days)
git log --since='90 days ago' --pretty='%H' --grep='Agent-Session:' -E \
  | xargs -I{} git show --pretty='' --name-only {} \
  | sort -u > /tmp/agent-touched-files.txt

wc -l /tmp/agent-touched-files.txt
```

If the count is zero, the project has not wired commit attribution. Run [`bootstrap-agent-commit-attribution`](bootstrap-agent-commit-attribution.md) and re-run this audit after ≥10 agent PRs have merged.

## Step 2 — Structural Complexity Signal

Cognitive complexity is the primary signal — it correlates with maintenance cost more reliably than copy/paste rate ([Agarwal et al.](https://arxiv.org/abs/2601.13597)).

```bash
# Use the language-appropriate complexity tool
# JS/TS: eslint-plugin-sonarjs cognitive-complexity rule
# Python: radon cc -a
# Go: gocognit
# Rust: clippy cognitive_complexity

# Compare agent-touched vs whole-repo baseline
radon cc -a $(cat /tmp/agent-touched-files.txt | grep '\.py$') 2>/dev/null \
  | tail -1 | awk '{print "agent_avg_cc:", $4}'
radon cc -a $(find . -name '*.py' ! -path '*/tests/*') 2>/dev/null \
  | tail -1 | awk '{print "repo_avg_cc:", $4}'
```

Severity rules:

- agent_avg_cc / repo_avg_cc > 1.4 → **high** finding (CMU study reports ~40% rise post-AI; [CMU](https://blog.robbowley.net/2025/12/04/ai-is-still-making-code-worse-a-new-cmu-study-confirms/))
- agent_avg_cc / repo_avg_cc > 1.2 → **medium** finding
- ratio ≤ 1.2 → no finding

## Step 3 — Single-Implementation Abstractions

Single-impl abstract base classes and factories wrapping simple operations are the most reliable bloat indicator ([`agent-driven-codebase-fingerprint`](../agent-design/agent-driven-codebase-fingerprint.md) §Auditing).

```bash
# Python: ABC subclasses with exactly one concrete implementation
python3 - <<'PY'
import ast, pathlib, collections
abc_subclasses = collections.defaultdict(list)
for f in pathlib.Path('.').rglob('*.py'):
    try:
        tree = ast.parse(f.read_text())
    except Exception:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    abc_subclasses[base.id].append((str(f), node.name))
for base, subs in abc_subclasses.items():
    if len(subs) == 1 and base.endswith(('Strategy','Base','Abstract','Factory','Provider','Handler')):
        f, name = subs[0]
        print(f"medium|{f}|single-impl abstraction {base} → {name}|inline or remove the base class until a second impl exists")
PY
```

Apply equivalent detection per language: TS/Go interfaces with one implementor, factories that return one concrete type, etc.

## Step 4 — Refactoring Share

Refactoring share dropped from 25% → under 10% in agent-assisted repos ([GitClear](https://www.gitclear.com/ai_assistant_code_quality_2025_research)). Healthy: above 15%.

```bash
# Refactoring commits: messages with refactor/cleanup/extract/inline keywords
TOTAL=$(git log --since='90 days ago' --pretty='%H' | wc -l)
REFACTOR=$(git log --since='90 days ago' --pretty='%s' \
  | grep -ciE 'refactor|cleanup|simplify|extract|inline|dedup|consolidate')
echo "scale=2; $REFACTOR / $TOTAL * 100" | bc
```

- < 10% → **high** finding ("agent-amplified pattern replication; schedule entropy-reduction passes; see [`entropy-reduction-agents`](../workflows/entropy-reduction-agents.md)")
- 10–15% → **medium**
- ≥ 15% → no finding

## Step 5 — Symptomatic Fixes

Agents address observable failures rather than underlying causes — memory limits raised instead of leaks found, retry loops added instead of error sources fixed ([Mason](https://mikemason.ca/writing/ai-coding-agents-jan-2026/)).

```bash
# Heuristic: PRs where the diff adds a retry/timeout/limit but does not modify the function those guards wrap
git log --since='90 days ago' --grep='Agent-Session:' -E -p \
  | awk '/^diff --git/{file=$3; sub(/a\//,"",file)} /^\+.*retry|^\+.*timeout|^\+.*max_retries|^\+.*increase.*limit/{print file": "$0}' \
  | head -20
```

Manual review required — emit each match as a **medium** finding with reviewer prompt: "is this masking the underlying failure?"

## Step 6 — Shadow Utilities (Pattern Replication at Scale)

A legacy utility with three usages becomes 23 after agent expansion ([`agent-driven-codebase-fingerprint`](../agent-design/agent-driven-codebase-fingerprint.md)). Detect utilities whose import count grew faster than the test coverage of that utility.

```bash
# Find symbols with rapid import-count growth in agent commits
for sym in $(git log --since='90 days ago' --grep='Agent-Session:' -E -p \
  | grep -oE '^\+.*from [a-z._]+ import [A-Z][a-zA-Z]+' \
  | awk '{print $NF}' | sort | uniq -c | sort -rn | head -20 | awk '$1 >= 5 {print $2}'); do
  echo "low|whole-repo|symbol $sym imported in ${1} new locations|verify the utility is still the right abstraction; consider deprecation if it now spans unrelated domains"
done
```

## Step 7 — Cross-File Coherence Gaps

Per-file correctness with cross-module coherence gaps in shared types, naming, and error handling ([Lavaee](https://alexlavaee.me/blog/openai-agent-first-codebase-learnings/)).

```bash
# Sample: error-handling style divergence across agent-touched files
grep -rE 'raise [A-Z][a-zA-Z]+\(' $(cat /tmp/agent-touched-files.txt | grep '\.py$') \
  | awk -F: '{print $2}' | sort -u | head -20
# If multiple distinct error styles appear (e.g., custom exception types vs strings vs HTTPException), flag medium
```

Severity is **medium** by default; promote to **high** when the divergence affects a public API surface.

## Step 8 — ADR Compliance

Agents do not read ADRs unless in the active context window. Map each ADR to a constraint and check agent-touched code against it.

```bash
# Discover ADRs
find . -path '*/adr/*.md' -o -path '*/architecture/decisions/*.md' | head
# For each ADR with a concrete constraint (e.g., "all DB calls go through repository pattern"),
# grep agent-touched files for violations and emit a finding per breach
```

If no ADRs exist, recommend [`bootstrap-agents-md`](bootstrap-agents-md.md) to capture the equivalent constraints in machine-readable form.

## Step 9 — Punch List

```markdown
# Audit Agent-Built Code Health — <repo>

## Headline metrics

| Signal | Value | Healthy band | Severity |
|--------|------:|-------------:|:--------:|
| Cognitive-complexity ratio (agent / repo) | <x> | ≤ 1.2 | high/med/none |
| Refactoring share (last 90d) | <x>% | ≥ 15% | high/med/none |
| Single-impl abstractions | <n> | 0 | medium |
| Shadow-utility growth | <n> symbols | n/a | low |

## Findings

| Severity | Location | Finding | Suggested fix |
|----------|----------|---------|---------------|
```

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Agent-Built Code Health — <repo>

| Files audited | Complexity ratio | Refactor % | Single-impl | Pass | Warn | Fail |
|--------------:|-----------------:|-----------:|------------:|-----:|-----:|-----:|
| <n> | <x> | <x>% | <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually inline single-impl abstractions or schedule an entropy-reduction sweep>
```

## Remediation

- [Entropy Reduction Agents](../workflows/entropy-reduction-agents.md) — scheduled cleanup of bloat findings
- [`bootstrap-agents-md`](bootstrap-agents-md.md) — capture architectural constraints so they enter the agent's active context
- [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) — wire complexity / duplication thresholds into a Stop-event gate
- Apply [`abstraction-bloat`](../anti-patterns/abstraction-bloat.md) §Mitigations: explicit simplicity directives in agent instructions

## Related

- [Emergent Architecture in AI-Driven Codebases](../agent-design/agent-driven-codebase-fingerprint.md)
- [Abstraction Bloat](../anti-patterns/abstraction-bloat.md)
- [Comprehension Debt](../anti-patterns/comprehension-debt.md)
- [Pattern Replication Risk](../anti-patterns/pattern-replication-risk.md)
- [Audit Premature Completion](audit-premature-completion.md)
- [Bootstrap Agent Commit Attribution](bootstrap-agent-commit-attribution.md)
