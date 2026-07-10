"""MkDocs hook: self-hosted RSS feed (no external plugin).

Registered in mkdocs.yml under `hooks:`. Collects every indexable page during
the build and writes an RSS 2.0 feed of the most recently *added* pages to
<site_dir>/feed.xml, served at /feed.xml.

The feed keys off page creation dates, not last-modified dates (#9755): a
content update, link fix, or refresh on an existing page must not resurface
it as a feed item — only genuinely new pages appear.

Why a hook and not mkdocs-rss-plugin: on the configured index,
`mkdocs-rss-plugin==1.19.0` declares a dependency on `properdocs` — the
malicious mkdocs shadow from the 2026-05 mkdocs-redirects hijack (see
scripts/dependency-denylist.txt). The legitimate plugin has no such
dependency; the supply-chain gate (scripts/check-dependencies.py) blocked the
install. Same decision as hooks/redirects.py: zero third-party dependency,
full control.

Dates come from hooks/created-manifest.json (regenerated on main by
release-cut.yaml, like lastmod-manifest.json), with a git-log fallback —
shallow clones can't see history, so the manifest is the primary source.
"""

import json
import subprocess
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

FEED_LENGTH = 30  # most recently added pages

_site_url: str = ""
_site_name: str = ""
_site_description: str = ""
_site_dir: Path | None = None
_docs_dir: Path | None = None
_created_manifest: dict[str, str] = {}

# (created YYYY-MM-DD, loc, title, description)
_items: list[tuple[str, str, str, str]] = []

_EXCLUDED_SRCS = frozenset({"404.md", "tags.md"})
_EXCLUDED_PREFIXES = ("training/",)


def on_config(config):
    global _site_url, _site_name, _site_description, _site_dir, _docs_dir
    global _items, _created_manifest
    _items = []
    _site_url = (config.get("site_url") or "").rstrip("/")
    _site_name = config.get("site_name") or ""
    _site_description = config.get("site_description") or ""
    _site_dir = Path(config.get("site_dir") or "site")
    _docs_dir = Path(config.get("docs_dir") or "docs")
    _created_manifest = _load_created_manifest()
    return config


def _load_created_manifest() -> dict[str, str]:
    """Load the created-date manifest that sits next to this hook file."""
    manifest_path = Path(__file__).resolve().parent / "created-manifest.json"
    try:
        with manifest_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}


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
    created = _created_manifest.get(src_path) or _git_created(src_path)

    _items.append((created, loc, title, description))
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

    for created, loc, title, description in newest:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = loc
        ET.SubElement(item, "guid", isPermaLink="true").text = loc
        if description:
            ET.SubElement(item, "description").text = description
        ET.SubElement(item, "pubDate").text = _rfc822(created)

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    out_path = (_site_dir or Path("site")) / "feed.xml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(fh, encoding="unicode", xml_declaration=False)
        fh.write("\n")


def _git_created(src_path: str) -> str:
    """Date of the first commit touching src_path, following renames.

    Fallback only — shallow clones (Cloudflare, --depth 1) see truncated
    history, so hooks/created-manifest.json is the primary source. A brand-new
    uncommitted page falls through to today, which is its creation date.
    """
    if _docs_dir is None:
        return _today()

    abs_path = _docs_dir / src_path

    try:
        result = subprocess.run(
            ["git", "log", "--follow", "--format=%cI", "--", str(abs_path)],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        lines = result.stdout.split()
        if lines:
            return lines[-1][:10]
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return _today()


def _today() -> str:
    return date.today().isoformat()


def _rfc822(yyyy_mm_dd: str) -> str:
    try:
        dt = datetime.strptime(yyyy_mm_dd, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        dt = datetime.now(timezone.utc)
    return format_datetime(dt)
