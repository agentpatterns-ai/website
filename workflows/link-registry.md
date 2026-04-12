---
title: "Shared Link Registry for Docs Sites"
description: "Define external URLs once in a central registry file and reference them by key across all documentation pages — one edit propagates everywhere."
tags:
  - workflows
---

# Shared Link Registry

> Define external URLs once in a central registry file; reference them by key across all pages so a URL change requires editing one line, not hundreds.

## The Problem

Large documentation sites accumulate duplicate URLs. A single authoritative source — say, the Anthropic context engineering blog post — may appear in 38 separate files. When that URL changes, finding and updating every occurrence requires a codebase-wide search-and-replace across hundreds of markdown files, with no compile-time guarantee that all instances were caught.

## The Pattern

A link registry is a single file that maps human-readable keys to URLs using Markdown's reference-style link syntax:

```markdown
[anthropic-context-engineering]: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
[anthropic-harnesses]: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
[anthropic-building-agents]: https://www.anthropic.com/engineering/building-effective-agents
[claude-sub-agents]: https://code.claude.com/docs/en/sub-agents
```

Pages reference keys inline without embedding the URL:

```markdown
Context budget allocation is covered in the [context engineering guide][anthropic-context-engineering].
```

The registry is injected into every page at build time so keys resolve site-wide.

## Implementation with pymdownx.snippets

The `pymdownx.snippets` extension supports an `auto_append` option that appends a file to every markdown document before parsing — explicitly designed for "including a page of reference links or abbreviations on every page" ([Snippets docs](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/)). MkDocs Material ships with pymdown-extensions as a dependency ([requirements.txt](https://github.com/squidfunk/mkdocs-material/blob/master/requirements.txt)), so no additional install is required.

**`mkdocs.yml`** — add the extension with `auto_append`:

```yaml
markdown_extensions:
  - pymdownx.snippets:
      base_path: [docs]
      auto_append:
        - _links.md
```

**`docs/_links.md`** — the registry file:

```markdown
[anthropic-context-engineering]: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
[anthropic-harnesses]: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
[claude-sub-agents]: https://code.claude.com/docs/en/sub-agents
[langchain-harness-engineering]: https://blog.langchain.com/improving-deep-agents-with-harness-engineering/
```

Because `auto_append` runs as a preprocessor, reference-style link definitions in `_links.md` are available to the Markdown parser on every page without per-page includes.

## Alternative: MkDocs Hook

If you need more control — for example, to log unresolved references or catch them at build time rather than in CI — a MkDocs hook using the `on_page_markdown` event can expand `[label][key]` patterns before the Markdown parser runs:

```python
# docs/hooks/link_registry.py
import re
from pathlib import Path

_REGISTRY: dict[str, str] = {}

def on_config(config):
    registry_path = Path(config["docs_dir"]) / "_links.md"
    if registry_path.exists():
        for line in registry_path.read_text().splitlines():
            m = re.match(r"^\[([^\]]+)\]:\s+(\S+)", line)
            if m:
                _REGISTRY[m.group(1)] = m.group(2)
    return config

def on_page_markdown(markdown, **kwargs):
    # Replaces explicit [label][key] references only.
    # Shorthand [key][] or bare [key] references are not expanded.
    for key, url in _REGISTRY.items():
        markdown = markdown.replace(f"][{key}]", f"]({url})")
    return markdown
```

```yaml
# mkdocs.yml
hooks:
  - docs/hooks/link_registry.py
```

The hook approach converts reference-style links to inline links before parsing. Use `pymdownx.snippets` instead if you want to keep reference-style links intact in the rendered output.

## CI Guard for Unresolved References

Add a CI step that fails if any page contains unresolved reference-style link keys after the build. Unresolved references render literally as `[label][key]` in the output HTML:

```yaml
# .github/workflows/ci.yml
- name: Check for unresolved link references
  run: |
    if grep -r '\]\[[a-z]' site/ --include="*.html" -l; then
      echo "Unresolved link references found"
      exit 1
    fi
```

## When This Backfires

- **Small sites**: for documentation with fewer than ~20 pages, a separate registry file adds coordination overhead without meaningful maintenance benefit — inline URLs are easier to trace.
- **Inconsistent key naming**: teams without a shared naming convention produce registries where similar URLs get distinct keys (`anthropic-agents` vs `building-effective-agents`), making keys harder to discover than a direct URL search.
- **Build system incompatibility**: projects not using MkDocs or a system that supports file injection at parse time must implement a custom hook or CI transformation, trading simplicity for control.

## Example

**Before** — URL duplicated across 38 files:

```markdown
See [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
for budget allocation strategies.
```

**After** — key referenced in pages, URL defined once in `_links.md`:

```markdown
See [context engineering][anthropic-context-engineering]
for budget allocation strategies.
```

Updating the URL requires editing one line in `_links.md`. The CI guard catches any key added to a page without a corresponding registry entry.

## Key Takeaways

- Define all frequently-referenced external URLs in a single `docs/_links.md` registry using Markdown reference-style link syntax
- `pymdownx.snippets` with `auto_append` injects the registry into every page at build time — no per-page includes required
- The hook alternative expands `[label][key]` to inline links; prefer snippets to keep reference-style links intact
- A CI grep over rendered HTML for unresolved `][key]` patterns catches registry misses before they reach production
- Updating a URL in the registry propagates to all pages on the next build

## Related

- [Continuous Documentation](continuous-documentation.md)
- [Content Pipeline](content-pipeline.md)
