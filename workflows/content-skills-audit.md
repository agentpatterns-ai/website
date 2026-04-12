---
title: "Content & Skills Audit Workflow: Automated Staleness"
description: "Periodically validate all URLs, site structure maps, and sourced claims across skills, agents, and content pages before silent drift becomes misinformation"
tags:
  - workflows
  - agent-design
---

# Content & Skills Audit Workflow: Automated Staleness Detection

> Periodically validate all URLs, site structure maps, and sourced claims across skills, agents, and content pages before silent drift becomes misinformation.

## The Staleness Problem

Skills that embed site navigation maps, URL paths, and feature lists drift silently. When a docs site restructures, an API endpoint moves, or a tool adds features, nothing breaks visibly — the skill just becomes wrong. Agents using stale skills produce confidently incorrect output.

The problem compounds across a project: a documentation project with ten skills and fifty content pages may have hundreds of external references. Any of them can become stale at any time, and there is no automatic alert.

A scheduled audit catches this drift before it reaches readers or downstream agents.

## What to Audit

| Target | Signal of Staleness | Validation Method |
|--------|-------------------|-------------------|
| URLs in all `.md` files | 4xx or redirect response | HTTP HEAD request, check for 2xx |
| Navigation skill site maps | Linked structure differs from fetched page | Fetch source, compare against skill content |
| Curated source list references | URL no longer resolves | HTTP HEAD request |
| Pipeline stage tags | Tag in content doesn't exist in tracker | `gh label list` or equivalent, compare against tag mentions |
| Skills and agent definitions | File not modified in N months | `git log --since`, flag for human review |

## Workflow Steps

### Step 1: Collect All External References

Extract every URL from every `.md` file in the repository. This includes:

- Inline links in content pages
- Source citations in skills and agent definitions
- URLs in curated source lists and similar resource files
- Links embedded in AGENTS.md or CLAUDE.md

Output: a deduplicated list of URLs with their source file and line number.

### Step 2: Validate URL Health

For each URL, issue an [HTTP HEAD request](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/HEAD). Flag any response that is not 2xx:

- **404 / 410**: resource deleted — content citing this URL needs a replacement source or removal
- **301 / 302**: resource moved — update the link to the new location
- **5xx / timeout**: transient or permanent server issue — recheck before acting

Group results by source file to make remediation targeted. A skill with five broken URLs needs a focused update; a content page with one broken link needs a targeted fix.

### Step 3: Validate Navigation Skills Against Live Sites

For skills that embed site structure maps (e.g., a skill documenting the GitHub Copilot docs navigation or Anthropic's platform structure), fetch the live site and compare against what the skill describes.

This step requires judgment, not just automation: page URLs may be stable while section organization changes. Flag skills whose described structure diverges from the live site for human review rather than automated correction. An LLM agent can perform the comparison and produce a structured diff summary — prompting with both the fetched live content and the skill's embedded map surfaces section renames, reordered entries, and removed pages in a single pass.

### Step 4: Validate Pipeline Labels

Skills and content pages that reference pipeline stage tags (e.g., Idea, Researching, Drafting) can drift if tags are renamed or deleted. Run:

```bash
gh label list --repo {owner}/{repo} --json name
```

Compare against all tag mentions in agent instructions, issue templates, and command definitions. Flag references to non-existent tags.

### Step 5: Flag Stale Files by Age

Files that haven't been modified in a configurable window (default: 90 days) may have outdated content. Identify them with:

```bash
git log --since="90 days ago" --name-only --format="" | sort | uniq
```

Take the complement: files not in that list haven't been touched. Flag them for review — not automatic deletion, since some files are intentionally stable. A human decides whether each flagged file is genuinely stale or correctly unchanged.

## Execution Options

### Option 1: On-Demand Command

An audit command runs the full workflow when invoked manually. Use for:

- Pre-release validation
- After a major external dependency (docs site, API) restructures
- When a broken link is reported

### Option 2: Scheduled GitHub Action (Automated)

A weekly or monthly [scheduled GitHub Action](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule) runs the audit, opens an issue with the results, and labels it for triage. This catches drift that no one actively checks for.

```yaml
on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday at 6am UTC
```

### Option 3: Both

The command gives on-demand access for targeted investigations. The scheduled action provides baseline coverage that doesn't depend on someone remembering to run it.

## Output Format

The audit should produce output that is immediately actionable:

```
BROKEN LINKS (404/410)
  docs/workflows/research-plan-implement.md:14 — https://example.com/moved
  docs/patterns/architecture/llms-txt.md:32 — https://old-domain.com/page

REDIRECTS (update to final URL)
  docs/techniques/plan-mode.md:8 — https://docs.old.com/ → https://docs.new.com/

STALE FILES (not modified in 90+ days, review recommended)
  docs/techniques/example-driven-vs-rule-driven-instructions.md — last modified 2024-11-03

NAVIGATION SKILL DIFFS (manual review required)
  skills/navigate-github-docs.md — see diff: {link}
```

Group by action type so a human can triage and delegate.

## Why It Works

Scheduled auditing catches drift that reactive fixes miss because no individual contributor has a complete view of all external dependencies. A docs site with ten skills and fifty pages may reference hundreds of external URLs and several third-party site structures — the cognitive overhead of tracking these exceeds what any reviewer can sustain. Automation delegates the legwork: HTTP HEAD requests are deterministic, git log age checks are O(1), and LLM-based structure diffing converts a qualitative judgment ("has anything changed?") into a reviewable diff that a human can action in minutes rather than hours.

The alternative — fixing staleness only when readers report it — compounds the problem. Stale content produces confident wrong output from any agent that consumes it, and those errors often propagate across multiple downstream agents before a symptom surfaces.

## When This Backfires

- **High-churn external dependencies**: If the audited skills embed rapidly changing third-party structures (e.g., docs sites that restructure monthly), the audit noise ratio grows — every run generates diffs that require human review, and reviewers start ignoring them. Cap navigation-skill audits to sources with stable structure, or accept higher false-positive rates.
- **Misclassified "stale" files**: Age-based flagging treats intentionally stable reference files the same as genuinely outdated content. A reference table with no expiry is not stale. Without a triage step that distinguishes the two, audit output requires more human time than it saves.
- **False-positive URL checks**: CDN-gated, login-protected, or rate-limited URLs return non-2xx codes without being genuinely broken. Blanket 4xx-flagging misrepresents these as broken links. Maintain a skip-list or verify with a second request before flagging.
- **Audit drift itself**: The audit workflow depends on skills that embed site structure maps — and those skills can become stale too. If the audit's own dependencies are not included in its scope, the tool degrades silently over time.

## Key Takeaways

- Skills with hardcoded site structure maps are the highest-staleness-risk artifacts in a project — audit them against live sites, not just link health
- URL validation (HTTP HEAD) is automatable and should run on a schedule, not only on-demand
- Flag stale files by age, but don't auto-delete — some files are intentionally stable
- Produce output grouped by action type so triage is fast
- Run the audit before major releases and after known external site restructurings

## Related

- [Continuous Agent Improvement](continuous-agent-improvement.md)
- [Continuous Documentation as an Agent-Driven Practice](continuous-documentation.md)
- [llms.txt: Spec, Adoption, and Honest Limitations](../geo/llms-txt.md)
- [Agent Debugging: Diagnosing Bad Agent Output](../observability/agent-debugging.md)
