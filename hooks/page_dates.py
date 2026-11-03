"""Share published date manifests and one Git lookup per missing page per build."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


class PageDates:
    def __init__(self, docs_dir, manifest_dir):
        self.docs_dir = Path(docs_dir).resolve()
        self.created_manifest = self._load(Path(manifest_dir) / 'created-manifest.json')
        self.modified_manifest = self._load(Path(manifest_dir) / 'lastmod-manifest.json')
        self._history = {}

    @staticmethod
    def _load(path):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}
        if not isinstance(data, dict):
            return {}
        return {key: value for key, value in data.items()
                if isinstance(key, str) and isinstance(value, str) and value}

    def _dates(self, src_path):
        if not src_path:
            return (None, None)
        if src_path not in self._history:
            dates = (None, None)
            try:
                result = subprocess.run(
                    ['git', 'log', '--follow', '--format=%cI', '--',
                     str(self.docs_dir / src_path)], cwd=self.docs_dir,
                    capture_output=True, text=True, check=True, timeout=5,
                )
                lines = result.stdout.split()
                if lines:
                    created = datetime.fromisoformat(lines[-1]).astimezone(timezone.utc)
                    modified = datetime.fromisoformat(lines[0]).astimezone(timezone.utc)
                    dates = (created.isoformat(), modified.date().isoformat())
            except (OSError, ValueError, subprocess.SubprocessError):
                dates = (None, None)
            self._history[src_path] = dates
        return self._history[src_path]

    def created(self, src_path):
        return self.created_manifest.get(src_path) or self._dates(src_path)[0]

    def modified(self, src_path):
        return self.modified_manifest.get(src_path) or self._dates(src_path)[1]


def for_build(config, *, reset=False):
    """Sitemap starts each build; later hooks reuse its provider via config."""
    key = '_page_dates'
    if reset or key not in config:
        config[key] = PageDates(config.get('docs_dir') or 'docs', Path(__file__).parent)
    return config[key]
