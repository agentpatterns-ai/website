"""MkDocs hook: self-hosted URL redirects (no external plugin).

Registered in mkdocs.yml under `hooks:`. Runs at on_post_build and writes a
meta-refresh + rel=canonical stub at each OLD page URL pointing to its new
location, so relocated pages don't 404 for bookmarked/cited links.

Redirect map lives in `redirects.yml` at the repo root:

    # old-slug: new-slug   (page paths relative to the site root, no leading slash)
    agent-design/empowerment-over-automation: human/empowerment-over-automation

This replaces the `mkdocs-redirects` PyPI package, which was unusable on the
configured index (it pulled a malicious `properdocs` shadow of mkdocs — see
scripts/dependency-denylist.txt). Keeping redirects in-repo means zero
third-party dependency and full control.
"""
from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent
REDIRECT_MAP = REPO_ROOT / "redirects.yml"

_STUB = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting…</title>
<link rel="canonical" href="{new}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={new}">
</head>
<body>
<p>This page has moved to <a href="{new}">{new}</a>.</p>
</body>
</html>
"""


def _norm(slug: str) -> str:
    return slug.strip().strip("/")


def on_post_build(config):
    if yaml is None or not REDIRECT_MAP.exists():
        return
    mapping = yaml.safe_load(REDIRECT_MAP.read_text(encoding="utf-8")) or {}
    site_dir = Path(config["site_dir"])
    site_url = config.get("site_url", "").rstrip("/")
    use_dir_urls = config.get("use_directory_urls", True)
    written = 0
    for old, new in mapping.items():
        old, new = _norm(str(old)), _norm(str(new))
        if not old or not new:
            continue
        new_url = f"{site_url}/{new}/" if site_url else f"/{new}/"
        # Old page URL → on-disk stub location (directory-url style by default)
        if use_dir_urls:
            out = site_dir / old / "index.html"
        else:
            out = site_dir / f"{old}.html"
        if out.exists():
            # Don't clobber a real page that still lives at the old path.
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_STUB.format(new=new_url), encoding="utf-8")
        written += 1
    if written:
        print(f"redirects.py: wrote {written} redirect stub(s)")
