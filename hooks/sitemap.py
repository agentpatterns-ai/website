"""
MkDocs hook: generate a spec-compliant XML sitemap with accurate <lastmod>
timestamps sourced from git history (not the build timestamp).

Spec decisions:
  - <loc> and <lastmod> only — <priority> and <changefreq> are omitted.
    Search engines document ignoring them; they add noise without benefit.
  - lastmod uses ISO 8601 date (YYYY-MM-DD) from the most recent git commit
    that touched the source file.  Falls back to today if the file has no
    git history (e.g. untracked, new file not yet committed).
  - Excluded pages:
      - 404.md
      - tags.md  (auto-generated tag index)
      - any page with  noindex: true  in frontmatter
      - MkDocs search index artefacts (not real pages)

Output:
  <site_dir>/sitemap.xml  — served at /sitemap.xml by nginx / any static host.
"""

import subprocess
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from urllib.parse import urljoin


# ---------------------------------------------------------------------------
# Module-level state populated in on_config
# ---------------------------------------------------------------------------
_site_url: str = ""
_site_dir: Path | None = None
_docs_dir: Path | None = None

# Accumulate page entries during the build, written in on_post_build.
_entries: list[tuple[str, str]] = []  # (loc_url, lastmod_date)

# Files that are never indexable.
_EXCLUDED_SRCS: frozenset[str] = frozenset({"404.md", "tags.md"})

# Path prefixes whose pages are never indexed (not-yet-public sections).
_EXCLUDED_PREFIXES: tuple[str, ...] = ("training/", "learning-paths/")


# ---------------------------------------------------------------------------
# on_config — capture site_url and dirs
# ---------------------------------------------------------------------------
def on_config(config):
    global _site_url, _site_dir, _docs_dir, _entries
    _entries = []
    _site_url = (config.get("site_url") or "").rstrip("/")
    _site_dir = Path(config.get("site_dir") or "site")
    _docs_dir = Path(config.get("docs_dir") or "docs")
    return config


# ---------------------------------------------------------------------------
# on_page_context — collect each page's URL + lastmod
# ---------------------------------------------------------------------------
def on_page_context(context, *, page, config, nav, **kwargs):
    src_path: str = page.file.src_path if page.file else ""

    # Skip excluded source files
    if src_path in _EXCLUDED_SRCS:
        return context

    # Skip excluded path prefixes (not-yet-public sections)
    if any(src_path.startswith(prefix) for prefix in _EXCLUDED_PREFIXES):
        return context

    # Skip pages with noindex: true in frontmatter
    meta = page.meta or {}
    if meta.get("noindex"):
        return context

    # Canonical URL
    loc = urljoin(_site_url + "/", page.url or "")
    # Ensure trailing slash is consistent with MkDocs convention
    if not loc.endswith("/") and not loc.rsplit("/", 1)[-1].count("."):
        loc = loc + "/"

    # lastmod from git
    lastmod = _git_lastmod(src_path)

    _entries.append((loc, lastmod))
    return context


# ---------------------------------------------------------------------------
# on_post_build — write sitemap.xml
# ---------------------------------------------------------------------------
def on_post_build(config):
    if not _entries:
        return

    urlset = ET.Element(
        "urlset",
        xmlns="http://www.sitemaps.org/schemas/sitemap/0.9",
    )

    # Deduplicate and sort for deterministic output
    seen: set[str] = set()
    for loc, lastmod in sorted(_entries, key=lambda e: e[0]):
        if loc in seen:
            continue
        seen.add(loc)

        url_el = ET.SubElement(urlset, "url")
        ET.SubElement(url_el, "loc").text = loc
        ET.SubElement(url_el, "lastmod").text = lastmod

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")

    out_path = (_site_dir or Path("site")) / "sitemap.xml"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(fh, encoding="unicode", xml_declaration=False)
        fh.write("\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git_lastmod(src_path: str) -> str:
    """Return YYYY-MM-DD of the last git commit touching src_path.

    src_path is relative to docs_dir (e.g. 'patterns/architecture/foo.md').
    We resolve it relative to docs_dir so git receives the correct path.
    """
    if _docs_dir is None:
        return _today()

    abs_path = _docs_dir / src_path

    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(abs_path)],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        iso_ts = result.stdout.strip()
        if iso_ts:
            # ISO 8601 datetime — keep only the date portion
            return iso_ts[:10]
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return _today()


def _today() -> str:
    return date.today().isoformat()
