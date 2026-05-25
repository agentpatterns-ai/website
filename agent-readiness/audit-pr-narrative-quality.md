---
title: "Audit PR Narrative Quality"
description: "Audit issue specs, PR descriptions, and commit messages on agent-authored PRs for visible-thinking discipline — required sections, intent capture, reasoning narration — emit per-PR findings against the templates that drive merge-rate gains."
tags:
  - tool-agnostic
  - code-review
  - workflows
aliases:
  - PR narrative audit
  - visible thinking audit
  - agent commit narration audit
---

Packaged as: `.claude/skills/agent-readiness-audit-pr-narrative-quality/`

# Audit PR Narrative Quality

> Audit the reasoning trail on agent-authored PRs — issue specs, PR descriptions, commit messages — for the structured-narrative discipline that empirically lifts merge rates and review throughput.

!!! info "Harness assumption"
    PRs are reachable via the GitHub API (`gh pr list`, `gh pr view`). Agent PRs are identifiable by author (bot account), branch prefix (`copilot/`, `claude/`, `cursor/`), or PR body signature. Translate the queries for non-GitHub forges — the narrative checks are forge-independent. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Run when ≥30 agent-authored PRs have merged in the audit window. Below that threshold the per-PR findings are useful but the rate baselines are not. Skip on solo or inner-source repos with no external reviewers and on squash-merge-only repos where per-commit narration collapses into the PR body — see [`visible-thinking-ai-development`](../observability/visible-thinking-ai-development.md) §When This Backfires.

PR description structure varies systematically by agent and correlates with merge rate at p<0.001 ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084), via [`pr-description-style-lever`](../code-review/pr-description-style-lever.md)). High reviewer discussion volume without structure is the failure mode, not engagement. This audit checks three artifacts the agent produces — the originating issue, the PR body, and the commit log — against the templates that move the merge-rate dial. Rules from [`visible-thinking-ai-development`](../observability/visible-thinking-ai-development.md), [`pr-description-style-lever`](../code-review/pr-description-style-lever.md), and [`agent-commit-attribution`](../workflows/agent-commit-attribution.md). Paired bootstrap: [`bootstrap-pr-narrative-template`](bootstrap-pr-narrative-template.md) installs the templates this audit checks for.

## Step 1 — Locate Agent PRs and Source Issues

```bash
AGENT_AUTHORS='claude\|copilot\|cursor\|devin\|codex'
gh pr list --state all --limit 200 --search "created:>=$(date -d '90 days ago' +%Y-%m-%d)" \
  --json number,author,title,body,headRefName,commits,closingIssuesReferences \
  | jq --arg pat "$AGENT_AUTHORS" \
      '[.[] | select(.author.login | test($pat; "i"))]' \
  > /tmp/agent-prs.json

jq 'length' /tmp/agent-prs.json
```

If the count is < 30, continue but mark the rate-aggregate findings as "low-confidence sample".

## Step 2 — Issue-as-Specification Check

A well-structured issue captures problem, success criteria, constraints, and risks before the agent engages — it is the reviewable record of intent ([`visible-thinking-ai-development`](../observability/visible-thinking-ai-development.md) §Issues as Specifications).

```bash
# For each PR with a closing-issue reference, fetch the issue body
jq -r '.[] | select(.closingIssuesReferences | length > 0)
  | "\(.number)\t\(.closingIssuesReferences[0].number)"' /tmp/agent-prs.json \
  | while IFS=$'\t' read -r pr issue; do
      BODY=$(gh issue view "$issue" --json body -q .body)
      HAS_PROBLEM=$(echo "$BODY" | grep -ciE '^#+\s*(problem|context|background|why)' || true)
      HAS_CRITERIA=$(echo "$BODY" | grep -ciE '^#+\s*(success criteria|acceptance|done.when|expected)' || true)
      HAS_CONSTRAINTS=$(echo "$BODY" | grep -ciE '^#+\s*(constraints|non.goals|out of scope)' || true)
      printf "PR #%s issue #%s problem=%s criteria=%s constraints=%s\n" \
        "$pr" "$issue" "$HAS_PROBLEM" "$HAS_CRITERIA" "$HAS_CONSTRAINTS"
    done
```

Severity rules:

- PRs with no linked issue → **medium** finding (no reviewable record of intent; agent ran from chat-ephemeral context)
- Linked issue missing two or more of {problem, criteria, constraints} → **low** finding per PR; if the share exceeds 30% of agent PRs, escalate to **medium** at the aggregate
- Linked issue auto-generated from a chat session with no human edit → **medium** (treat as opaque agent session per [`visible-thinking-ai-development`](../observability/visible-thinking-ai-development.md) §Anti-Patterns)

## Step 3 — PR Description Section Coverage

Score each PR body against the four sections that drive merge rate ([`pr-description-style-lever`](../code-review/pr-description-style-lever.md)): **Why**, **What changed** (or **Changes**), **Trade-offs** (or **Alternatives**), **Testing**.

```bash
jq -r '.[] | "\(.number)\t\(.body)"' /tmp/agent-prs.json \
  | while IFS=$'\t' read -r pr body; do
      WHY=$(echo "$body" | grep -ciE '^#+\s*(why|motivation|problem|context)' || true)
      WHAT=$(echo "$body" | grep -ciE '^#+\s*(what.changed|changes|summary)' || true)
      TRADE=$(echo "$body" | grep -ciE '^#+\s*(trade.?offs|alternatives|considered)' || true)
      TEST=$(echo "$body" | grep -ciE '^#+\s*(testing|test plan|validation|how (to )?test)' || true)
      printf "%s\twhy=%s\twhat=%s\ttradeoffs=%s\ttesting=%s\n" \
        "$pr" "$WHY" "$WHAT" "$TRADE" "$TEST"
    done
```

Severity rules:

- 0–1 sections present → **high** finding ("PR forces reviewer to reconstruct intent from diff; review-churn pattern")
- 2 sections present → **medium**
- 3 sections → **low**
- 4 sections → no finding

If > 40% of agent PRs score `0–1`, surface as a configuration gap — the agent has no PR template wired through `CLAUDE.md` / `AGENTS.md` / `.github/agents/` per [`pr-description-style-lever`](../code-review/pr-description-style-lever.md) §The Configuration Mechanism.

## Step 4 — Reviewer-Churn Cross-Check

Section coverage is necessary but not sufficient — the empirical failure mode is high comment volume without structure ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084), comments-per-PR ε²=0.280). Cross-check Step 3 against per-PR comment count.

```bash
gh pr list --state all --limit 200 --json number,reviews,comments \
  --search "created:>=$(date -d '90 days ago' +%Y-%m-%d)" \
  | jq '.[] | {pr: .number, comments: ((.reviews|length) + (.comments|length))}' \
  > /tmp/comment-counts.json
```

For PRs with full section coverage but comment count > 1.5× the team median, flag **low** per PR — these are the cases where the template is filled but the content is opaque (e.g., AI-generated PR text accepted uncritically per [`visible-thinking-ai-development`](../observability/visible-thinking-ai-development.md) §Anti-Patterns).

## Step 5 — Commit Message Reasoning Narration

Commit messages are the permanent reasoning record — they outlast the chat session that produced the code. The default-AI-generated commit message describes the change ("Add dark mode toggle"); a narrated commit explains the decision ("chose localStorage to avoid server dependency").

```bash
# Sample first commit per agent PR; flag generic messages
jq -r '.[] | "\(.number)\t\(.commits[0].messageHeadline // "")"' /tmp/agent-prs.json \
  | while IFS=$'\t' read -r pr msg; do
      LEN=${#msg}
      GENERIC=$(echo "$msg" | grep -ciE '^(add|update|fix|change|refactor)\s+\w+\s*$' || true)
      printf "PR #%s len=%s generic=%s msg=%s\n" "$pr" "$LEN" "$GENERIC" "$msg"
    done
```

Severity rules:

- Headline ≤ 40 chars AND matches generic verb pattern → **low** per commit; if > 50% of agent commits match, escalate to **medium** at the aggregate (no narration discipline; commit log is unsearchable per [`visible-thinking-ai-development`](../observability/visible-thinking-ai-development.md) §Misaligned Tooling)
- No commit body on multi-file commits → **low**
- Body present but contains only the auto-generated `Co-authored-by:` trailer → **low** (signed but not narrated)

## Step 6 — Force-Push and Branch-Naming Sanity

Force pushes are the strongest negative predictor of merge success — they invalidate prior review context ([`agent-authored-pr-integration`](../code-review/agent-authored-pr-integration.md), [`agent-proposed-merge-resolution`](../code-review/agent-proposed-merge-resolution.md)). Generic branch names (`agent-fix-1`, `claude/edit-3`) lose purpose-of-change signal.

```bash
# Force-push count per PR (events API; requires auth scope)
for pr in $(jq -r '.[].number' /tmp/agent-prs.json); do
  COUNT=$(gh api "repos/{owner}/{repo}/issues/$pr/events" --paginate \
    | jq '[.[] | select(.event=="head_ref_force_pushed")] | length')
  echo "PR #$pr force_pushes=$COUNT"
done

# Generic branch names
jq -r '.[] | "\(.number)\t\(.headRefName)"' /tmp/agent-prs.json \
  | awk -F'\t' '$2 ~ /(agent-fix|claude\/edit|copilot\/[0-9]|cursor\/[0-9])/ {print "generic-branch: PR #"$1" "$2}'
```

Severity rules:

- ≥1 force push during active review → **high** per PR
- > 10% of agent PRs use generic branch names → **medium** at the aggregate ([`agent-commit-attribution`](../workflows/agent-commit-attribution.md) recommends `claude/<short-task>` over `claude/<n>`)

## Step 7 — Punch List

```markdown
# Audit PR Narrative Quality — <repo>

## Headline metrics (90d window, n=<count>)

| Metric | Value | Target | Severity |
|--------|------:|-------:|:--------:|
| PRs with linked structured issue | <x>% | ≥70% | high/med/none |
| PRs with all 4 description sections | <x>% | ≥80% | high/med/none |
| Median commit-headline length | <x> | >40 chars | high/med/none |
| Force-push rate during review | <x>% | 0% | high/med/none |
| Generic branch names | <x>% | <10% | high/med/none |

## Findings

| Severity | PR | Gap | Suggested fix |
|----------|----|-----|---------------|
```

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit PR Narrative Quality — <repo>

| Window | Sample | Section coverage | Force-push % | Generic-name % | Pass | Warn | Fail |
|--------|-------:|-----------------:|-------------:|---------------:|-----:|-----:|-----:|
| 90d | <n> | <x>% | <x>% | <x>% | <n> | <n> | <n> |

Top fix: <one-liner — usually wire a PR template through CLAUDE.md/AGENTS.md or disable agent force-push during review>
```

## Remediation

- Add a PR template to `CLAUDE.md`, `AGENTS.md`, or `.github/agents/AGENT-NAME.md` per [`pr-description-style-lever`](../code-review/pr-description-style-lever.md) §The Configuration Mechanism — required sections: Why, What changed, Trade-offs, Testing
- Configure branch protection to disable force-push on agent branches during active review per [`bootstrap-human-review-gate-pr`](bootstrap-human-review-gate-pr.md)
- Capture issue specs as the agent's input contract per [`bootstrap-frozen-spec-file`](bootstrap-frozen-spec-file.md) when the work spans sessions
- Wire commit-narration discipline via the trailer convention in [`bootstrap-agent-commit-attribution`](bootstrap-agent-commit-attribution.md) — `Agent-Session`, `Model`, `Task-Reference`

## Related

- [Visible Thinking in AI-Assisted Development](../observability/visible-thinking-ai-development.md)
- [PR Description Style as a Lever for Agent PR Merge Rates](../code-review/pr-description-style-lever.md)
- [Agent-Authored PR Integration](../code-review/agent-authored-pr-integration.md)
- [Agent Commit Attribution](../workflows/agent-commit-attribution.md)
- [Audit Agent PR Quality Metrics](audit-agent-pr-quality-metrics.md)
- [Bootstrap Human Review Gate (PR)](bootstrap-human-review-gate-pr.md)
- [Bootstrap Agent Commit Attribution](bootstrap-agent-commit-attribution.md)
- [Bootstrap PR Narrative Template](bootstrap-pr-narrative-template.md)
