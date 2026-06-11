"""MkDocs hook: self-hosted RSS feed (no external plugin).

Registered in mkdocs.yml under `hooks:`. Collects every indexable page during
the build and writes an RSS 2.0 feed of the most recently updated pages to
<site_dir>/feed.xml, served at /feed.xml.

Why a hook and not mkdocs-rss-plugin: on the configured index,
`mkdocs-rss-plugin==1.19.0` declares a dependency on `properdocs` — the
malicious mkdocs shadow from the 2026-05 mkdocs-redirects hijack (see
scripts/dependency-denylist.txt). The legitimate plugin has no such
dependency; the supply-chain gate (scripts/check-dependencies.py) blocked the
install. Same decision as hooks/redirects.py: zero third-party dependency,
full control.

Dates come from hooks/lastmod-manifest.json (maintained by
derived-artifacts-sync.yaml), with git-log fallback — identical sourcing to
hooks/sitemap.py, so the feed and the sitemap never disagree about freshness.
"""

from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

import importlib.util as _ilu

# Reuse the sitemap hook's manifest/git lastmod logic instead of duplicating it.
_spec = _ilu.spec_from_file_location("ap_sitemap", Path(__file__).resolve().parent / "sitemap.py")
_sitemap = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_sitemap)

FEED_LENGTH = 30  # most recently updated pages

_site_url: str = ""
_site_name: str = ""
_site_description: str = ""
_site_dir: Path | None = None
_docs_dir: Path | None = None
_lastmod_manifest: dict[str, str] = {}

# (lastmod YYYY-MM-DD, loc, title, description)
_items: list[tuple[str, str, str, str]] = []

_EXCLUDED_SRCS = frozenset({"404.md", "tags.md"})
_EXCLUDED_PREFIXES = ("training/",)


def on_config(config):
    global _site_url, _site_name, _site_description, _site_dir, _docs_dir
    global _items, _lastmod_manifest
    _items = []
    _site_url = (config.get("site_url") or "").rstrip("/")
    _site_name = config.get("site_name") or ""
    _site_description = config.get("site_description") or ""
    _site_dir = Path(config.get("site_dir") or "site")
    _docs_dir = Path(config.get("docs_dir") or "docs")
    _sitemap._docs_dir = _docs_dir  # for the git-log fallback
    _lastmod_manifest = _sitemap._load_manifest()
    return config


def on_page_context(context, *, page, config, nav, **kwargs):
    src_path: str = page.file.src_path if page.file else ""
    if src_path in _EXCLUDED_SRCS:
        return context
    if any(src_path.startswith(p) for p in _EXCLUDED_PREFIXES):
        return context
    meta = page.meta or {}
    if meta.get("noindex"):
        return context

    loc = urljoin(_site_url + "/", page.url or "")
    title = str(meta.get("title") or page.title or "").strip()
    description = str(meta.get("description") or "").strip()
    lastmod = _lastmod_manifest.get(src_path) or _sitemap._git_lastmod(src_path)

    _items.append((lastmod, loc, title, description))
    return context


def on_post_build(config):
    if not _items:
        return

    # Newest first; tie-break on URL for deterministic output.
    newest = sorted(_items, key=lambda it: (it[0], it[1]), reverse=True)[:FEED_LENGTH]

    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = _site_name
    ET.SubElement(channel, "link").text = _site_url + "/"
    ET.SubElement(channel, "description").text = _site_description
    ET.SubElement(channel, "language").text = "en"
    ET.SubElement(channel, "lastBuildDate").text = _rfc822(newest[0][0])
    atom_link = ET.SubElement(channel, "atom:link")
    atom_link.set("href", _site_url + "/feed.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for lastmod, loc, title, description in newest:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = loc
        ET.SubElement(item, "guid", isPermaLink="true").text = loc
        if description:
            ET.SubElement(item, "description").text = description
        ET.SubElement(item, "pubDate").text = _rfc822(lastmod)

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    out_path = (_site_dir or Path("site")) / "feed.xml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(fh, encoding="unicode", xml_declaration=False)
        fh.write("\n")


def _rfc822(yyyy_mm_dd: str) -> str:
    try:
        dt = datetime.strptime(yyyy_mm_dd, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        dt = datetime.now(timezone.utc)
    return format_datetime(dt)
