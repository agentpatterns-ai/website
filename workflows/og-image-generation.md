---
title: "Per-Page OG Image Generation at MkDocs Build Time"
tags:
  - workflows
  - cost-performance
description: "Auto-generate branded 1200×630 Open Graph images from page metadata at MkDocs build time so every social share shows a unique, on-brand preview card."
aliases:
  - "social preview images"
  - "social card generation"
  - "Open Graph image automation"
---

# Per-Page OG Image Generation at MkDocs Build Time

> Auto-generate branded 1200×630 Open Graph images from page metadata at build time, so every social share shows a unique, on-brand preview card without manual design work.

Generic or missing OG images leave social shares with platform-generated previews — often just a logo or blank card. With 200+ pages, manual image design doesn't scale — move the work to the build pipeline instead.

If you use the Material theme, the [built-in social plugin](https://squidfunk.github.io/mkdocs-material/plugins/social/) already generates per-page social cards using your configured site colors, fonts, and logo, and wires up the meta tags automatically. Reach for a custom MkDocs hook only when you need layouts the built-in plugin can't express, a non-Material theme, or control over fonts, accent palettes, and output paths that the plugin options don't cover.

## How MkDocs Hooks Work

MkDocs supports [hook scripts](https://www.mkdocs.org/user-guide/configuration/#hooks) that fire at defined points in the build lifecycle. The relevant event is `on_page_context`, which fires once per page after the page's metadata and content are loaded but before HTML is rendered.

```python
# docs/hooks/og_images.py
import mkdocs.plugins

def on_page_context(context, page, config, **kwargs):
    # page.meta — frontmatter dict
    # page.title — page title string
    # page.file.src_path — relative path, e.g. "patterns/architecture/context-priming.md"
    ...
```

Register the hook in `mkdocs.yml`:

```yaml
hooks:
  - docs/hooks/og_images.py
```

## Implementation

Install Pillow alongside your MkDocs dependencies:

```toml
# pyproject.toml
dependencies = [
    "mkdocs-material>=9.6",
    "pillow>=10.0",
]
```

Hook script at `docs/hooks/og_images.py`:

```python
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import shutil

CANVAS_W, CANVAS_H = 1200, 630
OUTPUT_DIR = Path("docs/assets/og")

# Accent colors by page type — mapped from the first path segment under docs/
ACCENT = {
    "patterns/anti-patterns": "#c0392b",   # warning red
    "patterns":               "#27ae60",   # brand green
    "techniques":             "#2980b9",   # neutral blue
    "workflows":              "#8e44ad",   # purple
    "security":               "#e67e22",   # orange
}
DEFAULT_ACCENT = "#1a1a2e"

FONT_TITLE = ImageFont.truetype("docs/assets/fonts/Inter-Bold.ttf", 72)
FONT_TAG   = ImageFont.truetype("docs/assets/fonts/Inter-Regular.ttf", 36)
FONT_URL   = ImageFont.truetype("docs/assets/fonts/Inter-Regular.ttf", 30)
LOGO       = Image.open("docs/assets/logo.png").convert("RGBA")

def _accent_for(src_path: str) -> str:
    for prefix, color in ACCENT.items():
        if src_path.startswith(prefix):
            return color
    return DEFAULT_ACCENT

def _wrap_text(draw, text, font, max_width):
    """Return list of lines that fit within max_width."""
    words = text.split()
    lines, line = [], []
    for word in words:
        candidate = " ".join(line + [word])
        if draw.textlength(candidate, font=font) <= max_width:
            line.append(word)
        else:
            if line:
                lines.append(" ".join(line))
            line = [word]
    if line:
        lines.append(" ".join(line))
    return lines[:2]  # cap at 2 lines

def generate(title: str, tag: str, src_path: str, site_url: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = Path(src_path).stem
    out = OUTPUT_DIR / f"{slug}.png"

    accent = _accent_for(src_path)
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), "#0d0d0d")
    draw = ImageDraw.Draw(img)

    # Accent bar — left edge
    draw.rectangle([(0, 0), (12, CANVAS_H)], fill=accent)

    # Logo — top-left
    logo = LOGO.resize((180, 60), Image.LANCZOS)
    img.paste(logo, (48, 48), logo)

    # Title — centered vertically in the middle band
    lines = _wrap_text(draw, title, FONT_TITLE, CANVAS_W - 120)
    line_h = FONT_TITLE.size + 16
    total_h = len(lines) * line_h
    y = (CANVAS_H - total_h) // 2 - 20
    for line in lines:
        w = draw.textlength(line, font=FONT_TITLE)
        draw.text(((CANVAS_W - w) / 2, y), line, font=FONT_TITLE, fill="#ffffff")
        y += line_h

    # Category tag — bottom-left
    draw.text((48, CANVAS_H - 80), tag.upper(), font=FONT_TAG, fill=accent)

    # Site URL — bottom-right
    url_text = site_url.removeprefix("https://")
    url_w = draw.textlength(url_text, font=FONT_URL)
    draw.text((CANVAS_W - url_w - 48, CANVAS_H - 72), url_text, font=FONT_URL, fill="#888888")

    img.save(out, "PNG", optimize=True)
    return out

def _tag_from_path(src_path: str) -> str:
    segment = src_path.split("/")[0] if "/" in src_path else "page"
    return {
        "patterns": "Pattern",
        "techniques": "Technique",
        "workflows": "Workflow",
        "security": "Security",
        "evals": "Eval",
        "human": "Human Factors",
        "emerging": "Emerging",
        "fallacies": "Fallacy",
    }.get(segment, "Page")

def on_page_context(context, page, config, **kwargs):
    # Allow per-page override or opt-out
    if page.meta.get("og_image") == "none":
        return context
    if page.meta.get("og_image"):
        return context  # frontmatter provides an explicit path; leave it alone

    try:
        out = generate(
            title=page.title or "Agent Patterns",
            tag=_tag_from_path(page.file.src_path),
            src_path=page.file.src_path,
            site_url=config["site_url"].rstrip("/"),
        )
        rel = "/" + str(out.relative_to("docs")).replace("\\", "/")
        page.meta["og_image"] = config["site_url"].rstrip("/") + rel
    except Exception as exc:  # noqa: BLE001
        # Fall back to site default — never break the build
        page.meta.setdefault("og_image", config.get("extra", {}).get("og_default", ""))
        print(f"[og_images] warn: could not generate image for {page.file.src_path}: {exc}")

    return context
```

## Serving the Meta Tag

The Material theme reads `page.meta.og_image` and, when the built-in social plugin is disabled, falls back to whatever `<meta>` tags you define in a template override. For non-Material themes or custom layouts, add the tag to your `overrides/main.html`:

```html
{% extends "base.html" %}

{% block extrahead %}
  {% if page.meta.og_image %}
    <meta property="og:image" content="{{ page.meta.og_image }}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{{ page.meta.og_image }}">
  {% endif %}
{% endblock %}
```

## Page Type Variants

The hook uses the first directory segment of `page.file.src_path` to select an accent color:

| Path prefix | Accent | Tone |
|---|---|---|
| `patterns/anti-patterns/` | `#c0392b` | Warning red |
| `patterns/` | `#27ae60` | Brand green |
| `techniques/` | `#2980b9` | Neutral blue |
| `workflows/` | `#8e44ad` | Purple |
| `security/` | `#e67e22` | Orange |
| _(default)_ | `#1a1a2e` | Dark brand |

Anti-pattern pages receive the warning-red accent because `patterns/anti-patterns/` is checked before `patterns/` in the dict.

## Frontmatter Overrides and Opt-Out

```yaml
---
# Use a custom hand-crafted image
og_image: /assets/og/custom-homepage.png

# Skip generation entirely
og_image: none
---
```

When `og_image` is already set in frontmatter, the hook skips generation and leaves the value unchanged.

## Image Size and Quality

Pillow's `optimize=True` flag runs lossless PNG compression. For a 1200×630 canvas with dark background and minimal text, output is typically 30–80 KB — well under the 200 KB target. If images are larger:

- Reduce logo to a flat SVG rasterized at smaller size
- Switch to JPEG (`img.save(out, "JPEG", quality=85)`) for photographic backgrounds
- Use `img.quantize(colors=256)` before saving for flat-color designs

## Validation

After a build, verify images appear correctly with:

- [X Card Validator](https://cards-dev.twitter.com/validator) — paste a page URL, force a re-fetch
- [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/) — same workflow

Both tools cache aggressively. Use a cache-buster query string (`?v=2`) if you're iterating on the template and the old image keeps appearing.

## Key Takeaways

- The `on_page_context` MkDocs hook provides title, metadata, and file path per page — enough to generate a branded image without a separate service
- A left-edge accent bar keyed to page type gives visual differentiation without complex layouts
- Always wrap generation in a try/except and fall back to a site default — a missing font or corrupted asset should never break the build
- Commit generated images to the repo or to your CI artifact cache; regenerate on every build only if images are gitignored
- Per-page `og_image: none` gives authors an escape hatch for pages that don't need social images

## When This Backfires

Build-time image generation with Pillow is pragmatic but has specific failure modes:

- **Font assets missing in CI** — `ImageFont.truetype()` raises `OSError` if the font file isn't present. The hook's try/except silently falls back to the site default, so failures are invisible unless you inspect build logs. Pin font files in the repo, not a CDN download step.
- **Slug collisions** — the output filename uses `Path(src_path).stem`, so two pages named `index.md` in different directories write to the same `og/index.png`. Explicitly include the directory segment in the slug for nested content.
- **Stale images on rename** — renaming a page leaves the old PNG in `docs/assets/og/`. If that directory is committed, stale files accumulate. Add `docs/assets/og/` to `.gitignore` and regenerate on every build, or run a cleanup step keyed to current page paths.
- **Build-time cost at scale** — Pillow is fast per image, but 500+ pages adds measurable CI minutes. Cache generated images by content hash or switch to a CDN-based dynamic OG service (e.g., Vercel OG, Cloudinary) if build time is a constraint.

## Related

- [Content Pipeline: Idea to Published Page](content-pipeline.md)
- [PostToolUse Hooks: Automatic Formatting and Linting After Every File Edit](posttooluse-auto-formatting.md)
- [Agent Observability in Practice: OTel, Cost Tracking, and Trajectory Logging](../observability/agent-observability-otel.md)
- [Context Priming for AI Agent Development](../context-engineering/context-priming.md)
