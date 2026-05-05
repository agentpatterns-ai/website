---
title: "Audit Agent PR Quality Metrics"
description: "Measure agent-authored PR merge rate, comment volume, conflict rate, and post-merge defect rate against published baselines (AIDev, AgenticFlict, Beyond Bug Fixes); flag tasks routed to the wrong agent class — invoke when agent fan-out is producing PRs faster than humans review them, or quarterly during productivity reviews."
tags:
  - tool-agnostic
  - code-review
  - workflows
aliases:
  - agent PR audit
  - agent productivity audit
  - merge rate gap audit
---

Packaged as: `.claude/skills/agent-readiness-audit-agent-pr-quality-metrics/`

# Audit Agent PR Quality Metrics

> Measure merge rate, comment-volume signal, conflict rate, and post-merge defect signal on agent-authored PRs; route tasks by what each agent class actually does well.

!!! info "Harness assumption"
    Agent PRs are identifiable by author (bot account), branch prefix (`copilot/`, `claude/`, `cursor/`), or PR body signature. The audit uses the GitHub API (`gh pr list`, `gh api`) over the last 90 days. For non-GitHub forges, translate the queries — the metrics are forge-independent.

!!! info "Applicability"
    Run when the project has merged ≥30 agent-authored PRs in the audit window. Below that threshold, sample size is too small to compare against the published baselines (AIDev: 456,535 PRs; AgenticFlict: 142K PRs).

PR volume is a vanity metric — agent PRs close 10× faster than human PRs but acceptance lags by 13–42 percentage points ([AIDev](https://arxiv.org/abs/2507.15003), via [`agent-pr-volume-vs-value`](../code-review/agent-pr-volume-vs-value.md)). Merge rate, comment volume, conflict rate, and post-merge defects are the four signals that tell you whether the volume translates to value. Rules from [`agent-pr-volume-vs-value`](../code-review/agent-pr-volume-vs-value.md), [`agent-authored-pr-integration`](../code-review/agent-authored-pr-integration.md), and [`agent-proposed-merge-resolution`](../code-review/agent-proposed-merge-resolution.md).

## Step 1 — Locate Agent PRs

```bash
# Bot authors
AGENT_AUTHORS='claude\|copilot\|cursor\|devin\|codex'
gh pr list --state all --limit 1000 --search "created:>=$(date -d '90 days ago' +%Y-%m-%d)" \
  --json number,author,title,state,createdAt,mergedAt,additions,deletions,labels,reviews \
  | jq --arg pat "$AGENT_AUTHORS" \
      '[.[] | select(.author.login | test($pat; "i"))]' \
  > /tmp/agent-prs.json

jq 'length' /tmp/agent-prs.json
```

If the count is < 30, abort with "insufficient sample size".

## Step 2 — Merge Rate

Acceptance baselines from AIDev: human ~77%, Codex 64%, Devin 49%, Copilot 35%, Cursor and Claude Code mid-range.

```bash
TOTAL=$(jq 'length' /tmp/agent-prs.json)
MERGED=$(jq '[.[] | select(.state == "MERGED")] | length' /tmp/agent-prs.json)
echo "scale=2; $MERGED / $TOTAL * 100" | bc
```

Severity rules:

- merge rate < 35% → **high** finding ("below the lowest published agent baseline; investigate scope definition and review capacity")
- 35–60% → **medium** finding ("in line with weakest agents; consider task-routing changes per Step 6")
- ≥ 60% → no finding

## Step 3 — Comment Volume Signal

Reviewer comment count on agent PRs is a correction signal — each extra comment decreases merge probability ([`agent-authored-pr-integration`](../code-review/agent-authored-pr-integration.md)).

```bash
# Median comments per agent PR vs human PR
jq '[.[] | .reviews | length] | sort | .[length/2|floor]' /tmp/agent-prs.json
# Compare to human PR median (run the same query without the bot filter)
```

If agent median comments > 1.5× human median → **medium** finding. Surface the top three reviewers by comment count: this often signals a knowledge gap the agent cannot close without [`bootstrap-agents-md`](bootstrap-agents-md.md) capturing the missing context.

## Step 4 — Merge Conflict Rate

AgenticFlict baseline: 27.67% of agent PRs hit conflicts ([arXiv:2604.03551](https://arxiv.org/abs/2604.03551), via [`agent-proposed-merge-resolution`](../code-review/agent-proposed-merge-resolution.md)).

```bash
# Detect merge conflicts via GitHub mergeable state at the time of review
for pr in $(jq -r '.[].number' /tmp/agent-prs.json); do
  gh pr view "$pr" --json mergeable,mergeStateStatus -q \
    'select(.mergeStateStatus == "DIRTY" or .mergeable == "CONFLICTING") | "conflict"'
done | wc -l
```

- conflict rate > 35% → **high** finding ("above AgenticFlict baseline; raw throughput is eroding to rebase cost; reduce parallel agent fan-out or add conflict-aware dispatch")
- 25–35% → **medium**
- < 25% → no finding

## Step 5 — Post-Merge Defect Signal

Merge success does not reliably reflect post-merge code quality — code smells at critical/major severity dominate the defects introduced ([arXiv:2601.20109](https://arxiv.org/abs/2601.20109), via [`agent-pr-volume-vs-value`](../code-review/agent-pr-volume-vs-value.md)).

```bash
# Reverts and follow-up fix PRs that reference a merged agent PR
for pr in $(jq -r '.[] | select(.state == "MERGED") | .number' /tmp/agent-prs.json); do
  gh search prs --repo "$(gh repo view --json nameWithOwner -q .nameWithOwner)" \
    "Reverts #$pr OR #$pr" --json number --limit 5 \
    | jq --arg pr "$pr" '.[] | "fix-followup: " + (input_filename // "") + " for PR #" + $pr'
done
```

Manual review per match. Severity scales with the number of follow-ups: 0 → none, 1–2 → low, ≥3 → medium.

## Step 6 — Task Routing

Agents cluster around different task types ([AIDev](https://arxiv.org/abs/2507.15003)):

- **Documentation**: Codex 88.6%, Claude Code 85.7% acceptance — exceeds human 76.5%
- **Bug fixes**: GitHub Copilot 42.2% of PRs (vs 26.9% humans)
- **Features**: Cursor & Claude Code >40%
- **Cyclomatic complexity changes**: 9.1% of agent PRs vs 23.3% human

```bash
# Classify by labels or PR title prefix
jq '[.[] | .labels | map(.name) | join(",")] | group_by(.) | map({label: .[0], count: length}) | sort_by(.count) | reverse' /tmp/agent-prs.json
```

Emit a routing recommendation: if doc-style PRs are < 30% of agent volume but human merge rate on doc PRs is > 80%, route more docs to agents. If feature PRs from agents have < 40% acceptance, narrow agent scope to bounded tasks.

## Step 6b — Force-Push Detection

Force pushes during active review are the strongest negative predictor of merge success — they invalidate prior review context, per [`agent-authored-pr-integration`](../code-review/agent-authored-pr-integration.md) and [`agent-proposed-merge-resolution`](../code-review/agent-proposed-merge-resolution.md). Land conflict resolutions as new commits, never force pushes.

```bash
for pr in $(jq -r '.[].number' /tmp/agent-prs.json); do
  COUNT=$(gh api "repos/{owner}/{repo}/issues/$pr/events" --paginate \
    | jq '[.[] | select(.event=="head_ref_force_pushed")] | length')
  echo "PR #$pr force_pushes=$COUNT"
done > /tmp/force-pushes.txt

awk '$3 ~ /force_pushes=[1-9]/' /tmp/force-pushes.txt | wc -l
```

Severity rules:

- Any PR with ≥1 force push during active review (after first review submitted) → **high** finding per PR
- > 5% of agent PRs show force-push events → **medium** at the aggregate (configuration gap; agent should be wired through [`bootstrap-human-review-gate-pr`](bootstrap-human-review-gate-pr.md) which can disable force-push on agent branches)

For deeper narrative-discipline coverage on the same PR set — section coverage, issue-as-spec, commit narration — pair this audit with [`audit-pr-narrative-quality`](audit-pr-narrative-quality.md).

## Step 7 — Reviewer Capacity Check

20% of reviewers on agent PRs are bots vs 10% for humans ([AIDev](https://arxiv.org/abs/2507.15003)). Compute the bot-reviewer ratio.

```bash
jq '[.[] | .reviews[].author.login] | map(select(test("bot|claude|copilot|cursor"; "i"))) | length' /tmp/agent-prs.json
```

If > 30%, flag medium: the team is leaning on automated review without [`bootstrap-human-review-gate-pr`](bootstrap-human-review-gate-pr.md). If < 5%, flag medium: human reviewers are bearing volume with no triage; install bot pre-screening.

## Step 8 — Punch List

```markdown
# Audit Agent PR Quality Metrics — <repo>

## Headline metrics (90d window, n=<count>)

| Metric | Value | Baseline | Severity |
|--------|------:|---------:|:--------:|
| Merge rate | <x>% | ≥60% | high/med/none |
| Median comments per PR | <x> | ≤1.5× human | high/med/none |
| Conflict rate | <x>% | <25% | high/med/none |
| Post-merge follow-ups | <n> | 0 | low/med/none |
| Force-push rate during review | <x>% | 0% | high/med/none |
| Bot-reviewer share | <x>% | 5–30% | high/med/none |

## Routing fit

| Task type | Agent share | Agent acceptance | Human acceptance | Recommendation |
|-----------|------------:|-----------------:|-----------------:|---------------|

## Findings

| Severity | Metric | Finding | Suggested fix |
|----------|--------|---------|---------------|
```

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Agent PR Quality Metrics — <repo>

| Window | Sample | Merge % | Conflict % | Pass | Warn | Fail |
|--------|-------:|--------:|-----------:|-----:|-----:|-----:|
| 90d | <n> | <x>% | <x>% | <n> | <n> | <n> |

Top fix: <one-liner — usually narrow scope of feature-class agent PRs or route more documentation work to agents>
```

## Remediation

- [`bootstrap-human-review-gate-pr`](bootstrap-human-review-gate-pr.md) — wire CODEOWNERS-plus-branch-protection to gate agent PRs on the right surfaces
- [`bootstrap-agents-md`](bootstrap-agents-md.md) — capture the project context that closes reviewer-comment knowledge gaps
- Apply [`agent-pr-volume-vs-value`](../code-review/agent-pr-volume-vs-value.md) §When This Backfires: narrow agent task scope before scaling fan-out

## Related

- [Agent PR Volume vs Value](../code-review/agent-pr-volume-vs-value.md)
- [Agent-Authored PR Integration](../code-review/agent-authored-pr-integration.md)
- [Agent-Proposed Merge Resolution](../code-review/agent-proposed-merge-resolution.md)
- [CRA-Only Review and the Merge Rate Gap](../code-review/cra-merge-rate-gap.md)
- [Audit PR Narrative Quality](audit-pr-narrative-quality.md)
- [Bootstrap Human Review Gate (PR)](bootstrap-human-review-gate-pr.md)
- [Audit Premature Completion](audit-premature-completion.md)
