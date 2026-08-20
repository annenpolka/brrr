from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .brace import BraceIndex
from .model import Locus
from .python import PythonIndex


PYTHON_EXTS = {".py", ".pyi"}
BRACE_EXTS = {
    ".rs",
    ".go",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".swift",
    ".java",
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".hpp",
    ".cs",
    ".kt",
    ".kts",
    ".m",
    ".mm",
    ".scala",
    ".php",
    ".zig",
}


class FileIndex:
    def __init__(self, source: str, filename: str = "<src>"):
        self.source = source
        self.filename = filename
        self.lines = source.splitlines()
        self.nlines = len(self.lines)
        ext = Path(filename).suffix.lower()
        self._py: Optional[PythonIndex] = None
        self._br: Optional[BraceIndex] = None
        if ext in PYTHON_EXTS:
            self._py = PythonIndex(source, filename)
            if self._py.parse_error:
                self._br = BraceIndex(source, filename)
        elif ext in BRACE_EXTS:
            self._br = BraceIndex(source, filename)
        else:
            self._py = PythonIndex(source, filename)
            if self._py.parse_error:
                self._br = BraceIndex(source, filename)
                self._py = None

    def at(self, line: int) -> Locus:
        if self._py is not None and not self._py.parse_error:
            return self._py.at(line)
        if self._br is not None:
            return self._br.at(line)
        if self._py is not None:
            return self._py.at(line)
        here = self.lines[line - 1] if 1 <= line <= self.nlines else ""
        return Locus(
            file=self.filename,
            line=line,
            here=here,
            engine="none",
            error="no parser",
            placed=False,
        )


_cache = {}


def index_source(source: str, filename: str = "<src>") -> FileIndex:
    key = (filename, len(source), source[:200])
    hit = _cache.get(key)
    if hit is not None and hit.source == source:
        return hit
    idx = FileIndex(source, filename)
    if len(_cache) > 256:
        _cache.clear()
    _cache[key] = idx
    return idx


def query_source(source: str, filename: str, line: int) -> Locus:
    loc = index_source(source, filename).at(line)
    loc.file = filename
    return loc


def query_file(path: Union[str, Path], line: int, source: Optional[str] = None) -> Locus:
    path = Path(path)
    if source is None:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            return Locus(
                file=str(path),
                line=line,
                here="",
                engine="none",
                error=str(e),
                placed=False,
            )
    loc = index_source(source, str(path)).at(line)
    loc.file = str(path)
    return loc
