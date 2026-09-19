---
title: "Workspace-Hosted Skills: Authorship Outside the Repo"
term: "Workspace-Hosted Skills"
description: "A skill hosted in a document workspace makes page edit permission its review gate. Mirror the workspace into a repo to keep a revision you can revert to."
aliases:
  - hosted skills
  - Notion-hosted agent skills
  - document-workspace skill source
tags:
  - instructions
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-18
maturity: emerging
---

# Workspace-Hosted Skills: Authorship Outside the Repo

> A workspace-hosted skill's edit permission is its review gate, so mirror the workspace into git to keep a revision you can revert to.

A workspace-hosted skill is an agent skill whose source of truth is a page in a document workspace rather than a file in a repository. The skills CLI added this route on 17 September 2026: `npx skills add notion` "lists the skill packs shared with you and installs every skill in the packs you select" ([Vercel changelog](https://vercel.com/changelog/skills-cli-notion-skills)). The announcement summarizes the change as "No Git repository required." That sentence is the trade. Revision identity, an approval gate, a diff and a rollback target stop coming from the repository, and start coming from page permissions and page history.

## When this applies

All three conditions have to hold, not one of them.

- The content is owned by people who are not repo contributors: a support escalation script, a legal review checklist, a brand voice guide. If the skill encodes build commands or review policy, its owners already have repo access, so the hosted route adds a hop and removes review.
- The skill text carries no execution authority. Notion attaches supporting files, scripts included, through a `Files` property, and the local agent "reads that file the same way it reads its own instructions" ([Notion help](https://www.notion.com/help/create-and-manage-skills)).
- Something outside the workspace holds a revision you can return to. The workspace's own history expires, and the install records nothing.

## What the workspace replaces

| Repo control | Workspace equivalent | Enforced |
|---|---|---|
| Commit SHA as revision identity | `version_id` on the API listing, discarded by the CLI install | No |
| Revert to any commit | Page history, capped by plan | Within the window |
| Branch protection over who changes the bytes | Page edit permission | Yes |
| A dependency bump someone approves | Page view permission grants install | Yes |
| Review before the change takes effect | An `Owner` or `Status` property, by team convention | No |

Two rows carry most of the difference. Notion prices page history, described as "Restore your page to a previous version", at 7 days on Free, 30 on Plus, 90 on Business and unlimited on Enterprise ([Notion pricing](https://www.notion.com/pricing)). And every plugin entry the Agent Skills API returns carries a `version_id`, with the documented sync workflow telling integrators to "Compare each plugin's `version_id` against the value you stored the last time you downloaded it" ([Notion Agent Skills API](https://developers.notion.com/guides/agent-skills/overview)). The interactive install throws that identity away. `fetchNotionPackDirectory` compares the two values and aborts when they disagree, which guards a single install against a mid-flight edit. The manifest written afterwards records each pack's `name`, `source` and skill paths, and no version at all ([`src/notion-test.ts`](https://github.com/vercel-labs/skills/blob/main/src/notion-test.ts), imported by [`src/add.ts`](https://github.com/vercel-labs/skills/blob/main/src/add.ts)).

## Why it works

The document's access control list becomes the agent's control plane, one for one. Notion states the mutation half: "If they can edit the skill page, their edits will change the skill" ([Notion help](https://www.notion.com/help/create-and-manage-skills)). Vercel states the distribution half: "controlling who can install a skill is the same as controlling who can view the page" ([Vercel changelog](https://vercel.com/changelog/skills-cli-notion-skills)). That equivalence is the mechanism. The pattern pays off where the workspace's permissions are already the right answer to "who decides what this says". A team that spent two years getting its escalation policy right there, with the right owners and the right readers, built the access model that skill needs along the way.

The equivalence is load-bearing rather than pedantic because skill text is operational. Saha et al. changed descriptions only, with no code involved. Adversarial variants "are selected in 77.6% of paired trials on average", and semantic evasion let malicious skills "avoid a blocking verdict in 36.5%-100% of cases" — evidence that "SKILL.md is not passive documentation but operational text that shapes which third-party capabilities agents find, trust, and use" ([arxiv:2605.11418v1](https://arxiv.org/abs/2605.11418v1)). Edit access to the prose is edit access to the behavior.

## When this backfires

- Teamspace-wide sharing. Install rights equal page view rights, so sharing a skills database with a teamspace hands install to everyone in it and edit to every editor in it. Notion's own warning: "Anyone with edit access can change a shared skill for everyone who uses it, so pick editors with that in mind" ([Notion help](https://www.notion.com/help/create-and-manage-skills)).
- Audit obligations that outlive the plan's retention. Past the page-history window, nobody can reconstruct who changed an agent's instruction or when, and the engineering audit trail never held that record.
- Reproducible builds. `version_id` is an "opaque version identifier" to "compare for equality to determine whether the directory has changed", and the endpoint that returns a plugin directory takes one path parameter, its `id` ([Get a plugin directory](https://developers.notion.com/reference/agent-skills/get-plugin-directory)). You can detect that a skill moved. You cannot ask for the version it moved from.
- Treating faster edits as better instructions. Across 15,549 agentic pull requests in 148 projects, adding instruction files raised the merge rate by at least 20% in 27.7% of projects and lowered it in 26.35% ([arxiv:2606.13449v1](https://arxiv.org/abs/2606.13449v1)). Removing the review gate speeds up both directions.
- Assuming the copy on disk tracks the page. It does not. Notion's manual download badges a changed skill "so you know to download the latest version to your local environment" ([Notion help](https://www.notion.com/help/create-and-manage-skills)). A human is still in the pull.

## Example

Notion ships the mitigation as a sample: `notion-skills-github-sync` runs "a recurring script that syncs skills from Notion into a GitHub plugin marketplace" ([Notion Agent Skills API](https://developers.notion.com/guides/agent-skills/overview); [makenotion/notion-skills-github-sync](https://github.com/makenotion/notion-skills-github-sync)). The loop it automates is the documented sync workflow:

```bash
# 1. List plugins. Each entry carries id, name, description, version_id.
curl -X GET "https://api.notion.com/v1/ai/plugins?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2026-03-11"

# 2. Skip every plugin whose version_id matches the one you stored.
# 3. For the rest, GET /v1/ai/plugins/$PLUGIN_ID for a signed URL, then:
curl --fail --location "$SIGNED_URL" -o plugin.tar.gz &&
  tar -xzf plugin.tar.gz -C ./plugins
```

Commit the extracted tree with the `version_id` beside it, and install from that repo rather than from the workspace. Domain owners keep editing pages. Engineers get a diff, a reviewer, a commit to pin and a commit to revert to. Watch the ordering the same workflow spells out: "Only after all pages have been fetched successfully, remove local directories for plugin IDs missing from the complete list. An incomplete or failed listing must not delete local plugins" ([Notion Agent Skills API](https://developers.notion.com/guides/agent-skills/overview)).

## Key Takeaways

- Page edit permission is the mutation gate and page view permission is the install gate. Audit the workspace's sharing settings before the first install, not the CLI's flags.
- The API hands out a `version_id` and the interactive install throws it away, so nothing on disk says which revision you are running.
- Page history is the revert path and it expires: 7 days on Free, 30 on Plus, 90 on Business ([Notion pricing](https://www.notion.com/pricing)).
- Sync the workspace into git on a schedule and install from the mirror. That restores the diff and the rollback target without moving authorship back to people who do not own the content.
- Keep any skill that directs command execution in the repository. Instruction text is operational, and an unreviewed edit to it is an unreviewed change to agent behavior ([arxiv:2605.11418v1](https://arxiv.org/abs/2605.11418v1)).

## Related

- [Prompt Governance via PRs: Reviewable AI Behavior](prompt-governance-via-pr.md) — the repo-review baseline this topology departs from
- [Skill Packs: Registry Distribution Needs Pinning Discipline](skill-pack-registry-distribution.md) — the consumer-side half: lock files, `ref` pinning and content hashes once a skill is published
- [Central Repo for Shared Agent Standards](../workflows/central-repo-shared-agent-standards.md) — the canonical-source repo this pattern moves authorship out of
- [Enterprise Skill Marketplace: Distribution, Usage Reporting, and Quality Evals](../workflows/enterprise-skill-marketplace.md) — managed distribution and a quality cadence once the library is large
- [Skill Over-Trust: Treating Topical Relevance as Evidence a Skill Helps](../patterns/anti-patterns/skill-over-trust.md) — the failure a faster, unreviewed edit path makes cheaper
