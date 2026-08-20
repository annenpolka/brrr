from __future__ import annotations

import os
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "target",
    "dist",
    "build",
    ".build",
    "vendor",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".tox",
    ".idea",
    ".vscode",
    "coverage",
    "htmlcov",
    "DerivedData",
    "Pods",
    "Carthage",
    ".next",
    ".turbo",
    ".cache",
    "flycheck0",
    "tmp",
    ".direnv",
    "wheels",
    "site-packages",
}

SOURCE_EXTS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".rs",
    ".go",
    ".swift",
    ".java",
    ".kt",
    ".kts",
    ".rb",
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".hpp",
    ".cs",
    ".m",
    ".mm",
    ".scala",
    ".php",
    ".lua",
    ".zig",
    ".mbt",
    ".pkl",
}

PRODUCER_ONLY_EXTS = {
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".toml",
}

MAX_BYTES = 1_500_000


def classify_ext(path: Path) -> str | None:
    name = path.name
    if name.endswith(".min.js") or name.endswith(".min.css"):
        return None
    ext = path.suffix.lower()
    if ext in SOURCE_EXTS:
        return "source"
    if ext in PRODUCER_ONLY_EXTS:
        return "producer"
    return None


def iter_files(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        root = root.resolve()
        if root.is_file():
            if classify_ext(root) and root not in seen:
                out.append(root)
                seen.add(root)
            continue
        if not root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
            ]
            for name in filenames:
                path = Path(dirpath) / name
                if classify_ext(path) is None:
                    continue
                try:
                    if path.stat().st_size > MAX_BYTES:
                        continue
                except OSError:
                    continue
                resolved = path.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                out.append(path)
    out.sort()
    return out
