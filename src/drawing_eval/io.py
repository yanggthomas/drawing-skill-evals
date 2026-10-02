from __future__ import annotations

import hashlib
import json
from pathlib import Path


def repository_root(start: Path | None = None) -> Path:
    path = (start or Path.cwd()).resolve()
    for candidate in (path, *path.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / ".claude-plugin").is_dir():
            return candidate
    raise FileNotFoundError("not inside the drawing-skill-evals repository")


def load_manifest(path: Path) -> dict:
    """Load JSON-compatible YAML used by repository manifests."""
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"manifest must contain an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"invalid PNG header: {path}")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")
