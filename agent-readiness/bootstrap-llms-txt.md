---
title: "Bootstrap llms.txt"
description: "Detect a project's documentation surface, extract a structured index per the open spec, generate /llms.txt and /llms-full.txt, and validate spec compliance."
tags:
  - tool-agnostic
  - instructions
aliases:
  - generate llms.txt file
  - scaffold llms-full.txt
  - LLM discoverability index
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-llms-txt/`

# Bootstrap llms.txt

> Detect the documentation surface, extract a structured index per the [llms.txt spec](https://llmstxt.org), generate both files, validate.

!!! info "Applicability"
    Skip this runbook for internal-only projects with no public documentation site or external API reference. `llms.txt` indexes a project's published docs for AI agents discovering it from outside — it has no value for repos whose docs are not served at a stable URL.

Without `llms.txt`, an agent encountering a project's docs site has to crawl undirected. With it, a single fetch gives the agent a curated map. This runbook generates the file from the project's existing nav source and validates against the spec defined in [`docs/standards/llms-txt.md`](../standards/llms-txt.md).

## Step 1 — Detect the Documentation Surface

```bash
# Detect the docs framework
test -f mkdocs.yml && echo "mkdocs"
test -f docusaurus.config.js -o -f docusaurus.config.ts && echo "docusaurus"
test -f docs/conf.py && echo "sphinx"
test -d .vitepress && echo "vitepress"
test -d .vuepress && echo "vuepress"
test -f astro.config.mjs && grep -q starlight astro.config.mjs && echo "starlight"

# Detect existing llms.txt
test -f llms.txt && echo "EXISTS: llms.txt"
test -f docs/llms.txt && echo "EXISTS: docs/llms.txt"
test -f static/llms.txt && echo "EXISTS: static/llms.txt"
```

Decision rules:

- **No docs framework detected** → check for a `docs/` directory of plain markdown; if absent, ask the user to confirm where docs live
- **Existing `llms.txt`** → run a spec-compliance check; rewrite only on regression
- **Multiple deployment targets** → place `llms.txt` at the root the docs site serves from (often `docs/` for mkdocs, `static/` for Docusaurus)

## Step 2 — Extract Nav Structure

Per framework:

```bash
# mkdocs (awesome-pages plugin)
find docs -name ".pages" -exec echo "--- {}" \; -exec cat {} \;

# mkdocs (manual nav)
yq '.nav' mkdocs.yml

# Docusaurus
cat sidebars.js sidebars.ts 2>/dev/null

# Sphinx (toctree)
grep -rE "^\.\. toctree::" docs/ -A 30

# VitePress
grep -A 100 "sidebar" .vitepress/config.*
```

Build a structured map: section → list of pages (path + title). Preserve the project's information architecture; do not reorder.

## Step 3 — Extract Per-Page Summaries

For each linked page:

```bash
# Prefer frontmatter description
python3 -c "
import sys, frontmatter
post = frontmatter.load(sys.argv[1])
print(post.get('description', ''))
" "$page"

# Fallback: first sentence after H1
awk '/^# /{found=1; next} found && NF{print; exit}' "$page" | head -c 200
```

Strip marketing language. The description is for selection, not promotion.

## Step 4 — Generate llms.txt

Use this template. Substitute the project name, summary, and section/link blocks. The H1 is project name only; the blockquote is one sentence ≤200 characters:

```markdown
# <Project Name>

> <one sentence; ≤200 chars; defines what the project is and who uses it>

## <Section 1: most load-bearing — getting started, install, quickstart>

- [<Page title>](<absolute or root-relative URL>): <one-line description>
- [<Page title>](<URL>): <description>

## <Section 2: concepts>

- [<Page>](<URL>): <description>

## <Section 3: reference>

- [<Page>](<URL>): <description>

## Optional

- [<Page>](<URL>): <description that the agent can skip without losing core understanding>
```

Generation rules:

1. **Single H1** — project name only
2. **Blockquote summary** — one sentence, ≤200 chars
3. **Stable URLs** — absolute or root-relative; never `index.html`-suffixed unless that is the canonical form
4. **Order by load-bearing** — getting started first; reference later; peripheral content under `## Optional`
5. **One-line description per link** — neutral, descriptive, no marketing
6. **Mirror documentation IA, not filesystem** — group by topic, not folder

## Step 5 — Generate llms-full.txt

Concatenate the full markdown of every linked page in the same order, preserving frontmatter:

```bash
{
  echo "# <Project Name>"
  echo ""
  echo "> <one-sentence summary>"
  echo ""
  for page in $ORDERED_PAGES; do
    echo ""
    echo "---"
    echo ""
    cat "$page"
  done
} > llms-full.txt
```

Cap at the model context limit you target. If the corpus exceeds the cap, slice on `## Optional` content first.

## Step 6 — Validate

```bash
# Single H1
test "$(grep -cE '^# ' llms.txt)" -eq 1 || echo "FAIL: not exactly one H1"

# Blockquote present and short
head -10 llms.txt | grep -qE '^>' || echo "FAIL: missing blockquote summary"
head -10 llms.txt | grep -E '^>' | wc -c | awk '$1 > 220 { print "FAIL: blockquote too long" }'

# Every link resolves
grep -oE '\(http[s]?://[^)]+\)' llms.txt | tr -d '()' | while read url; do
  curl -sf -o /dev/null -I "$url" || echo "WARN: $url returned non-2xx"
done

# Relative links resolve to existing files
grep -oE '\(/[^)]+\)' llms.txt | tr -d '()' | while read path; do
  test -e "docs${path%.md}.md" -o -e "docs${path}/index.md" \
    || echo "WARN: $path does not resolve"
done
```

## Step 7 — Wire to the Site

- `mkdocs` → place at `docs/llms.txt`; ensure `extra_files:` (or include) covers it
- `Docusaurus` → place at `static/llms.txt`
- `VitePress` → place at `public/llms.txt`
- `Sphinx` → add to `html_extra_path` in `conf.py`

If the project publishes to a domain root (`/llms.txt`), confirm the deployment serves it without redirect to a docs path.

## Idempotency

Re-running with no nav change produces no diff. Re-run automatically when the nav source changes (CI hook on `mkdocs.yml`, `sidebars.js`, etc.).

## Output Schema

```markdown
# Bootstrap llms.txt — <project>

| Action | File | Sections | Links | Bytes |
|--------|------|---------:|------:|------:|
| Created | docs/llms.txt | <n> | <n> | <n> |
| Created | docs/llms-full.txt | - | - | <n> |

Validation: <pass/fail>
```

## Related

- [llms.txt Standard](../standards/llms-txt.md)
- [llms.txt specification](https://llmstxt.org)
- [AGENTS.md Standard](../standards/agents-md.md)
