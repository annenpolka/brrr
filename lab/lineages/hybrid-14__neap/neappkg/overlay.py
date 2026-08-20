"""In-memory unified-diff overlay. Reads git / worktree; never writes."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set, Tuple


HUNK_RE = re.compile(r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@")
COMBINED_RE = re.compile(r"^@@@")


@dataclass
class HunkLine:
    kind: str  # ' ' | '+' | '-'
    text: str
    no_newline: bool = False


@dataclass
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: List[HunkLine] = field(default_factory=list)
    header: str = ""


@dataclass
class PatchFile:
    old_path: str
    new_path: str
    hunks: List[Hunk] = field(default_factory=list)
    is_new: bool = False
    is_delete: bool = False
    is_binary: bool = False
    is_combined: bool = False
    rename: bool = False


@dataclass
class AddedLine:
    path: str
    line: int
    text: str
    old_path: str = ""
    error: Optional[str] = None


@dataclass
class FileImage:
    path: str
    old_path: str
    pre: Optional[str]
    post: Optional[str]
    added: List[AddedLine]
    error: Optional[str] = None
    binary: bool = False
    is_new: bool = False
    is_delete: bool = False
    rename: bool = False
    removed: List[str] = field(default_factory=list)


def looks_like_diff(text: str) -> bool:
    head = text[:12000]
    if COMBINED_RE.search(head):
        return True
    return (
        head.startswith("diff --git ")
        or head.startswith("--- ")
        or head.startswith("+++ ")
        or head.startswith("@@ ")
        or "\n@@ " in head
        or "\ndiff --git " in head
    )


def _c_unescape(s: str) -> str:
    out: List[str] = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] != "\\" or i + 1 >= n:
            out.append(s[i])
            i += 1
            continue
        nxt = s[i + 1]
        mapping = {
            "a": "\a",
            "b": "\b",
            "t": "\t",
            "n": "\n",
            "v": "\v",
            "f": "\f",
            "r": "\r",
            '"': '"',
            "\\": "\\",
        }
        if nxt in mapping:
            out.append(mapping[nxt])
            i += 2
            continue
        if nxt in "01234567":
            j = i + 1
            while j < n and j < i + 4 and s[j] in "01234567":
                j += 1
            try:
                out.append(chr(int(s[i + 1 : j], 8)))
            except ValueError:
                out.append(s[i:j])
            i = j
            continue
        out.append(nxt)
        i += 2
    return "".join(out)


def _strip_ab(path: str) -> str:
    if path.startswith("a/") or path.startswith("b/"):
        return path[2:]
    return path


def unquote_git_path(spec: str) -> str:
    spec = spec.strip()
    if "\t" in spec:
        spec = spec.split("\t", 1)[0]
    if spec.startswith('"') and spec.endswith('"') and len(spec) >= 2:
        spec = _c_unescape(spec[1:-1])
    if spec == "/dev/null":
        return "/dev/null"
    return _strip_ab(spec)


def _take_git_path(s: str) -> Tuple[str, str]:
    s = s.lstrip()
    if not s:
        return "", ""
    if s.startswith('"'):
        i = 1
        while i < len(s):
            if s[i] == "\\":
                i += 2
                continue
            if s[i] == '"':
                return unquote_git_path(s[: i + 1]), s[i + 1 :]
            i += 1
        return unquote_git_path(s), ""
    parts = s.split(None, 1)
    return unquote_git_path(parts[0]), (parts[1] if len(parts) > 1 else "")


def parse_unified_diff(text: str) -> List[PatchFile]:
    files: List[PatchFile] = []
    cur: Optional[PatchFile] = None
    hunk: Optional[Hunk] = None
    old_path = ""
    new_path = ""

    def flush_hunk() -> None:
        nonlocal hunk
        if cur is not None and hunk is not None:
            cur.hunks.append(hunk)
        hunk = None

    def ensure_file() -> PatchFile:
        nonlocal cur
        if cur is None:
            cur = PatchFile(old_path=old_path or new_path, new_path=new_path or old_path)
            files.append(cur)
        return cur

    for raw in text.splitlines():
        if COMBINED_RE.match(raw):
            fp = ensure_file()
            fp.is_combined = True
            flush_hunk()
            hunk = None
            continue
        if raw.startswith("diff --git "):
            flush_hunk()
            cur = None
            rest = raw[len("diff --git ") :]
            a, rest2 = _take_git_path(rest)
            b, _ = _take_git_path(rest2)
            old_path, new_path = a, b
            cur = PatchFile(old_path=a, new_path=b or a)
            files.append(cur)
            continue
        if raw.startswith("old mode ") or raw.startswith("new mode "):
            continue
        if raw.startswith("deleted file mode"):
            ensure_file().is_delete = True
            continue
        if raw.startswith("new file mode"):
            ensure_file().is_new = True
            continue
        if raw.startswith("rename from "):
            fp = ensure_file()
            fp.old_path = unquote_git_path(raw[len("rename from ") :])
            fp.rename = True
            continue
        if raw.startswith("rename to "):
            fp = ensure_file()
            fp.new_path = unquote_git_path(raw[len("rename to ") :])
            fp.rename = True
            continue
        if raw.startswith("copy from "):
            ensure_file().old_path = unquote_git_path(raw[len("copy from ") :])
            continue
        if raw.startswith("copy to "):
            ensure_file().new_path = unquote_git_path(raw[len("copy to ") :])
            continue
        if raw.startswith("index ") or raw.startswith("similarity index") or raw.startswith(
            "dissimilarity index"
        ):
            continue
        if raw.startswith("GIT binary patch") or raw.startswith("Binary files "):
            ensure_file().is_binary = True
            continue
        if raw.startswith("--- "):
            old_path = unquote_git_path(raw[4:])
            fp = ensure_file()
            if old_path == "/dev/null":
                fp.is_new = True
                fp.old_path = "/dev/null"
            else:
                fp.old_path = old_path
            continue
        if raw.startswith("+++ "):
            new_path = unquote_git_path(raw[4:])
            fp = ensure_file()
            if new_path == "/dev/null":
                fp.is_delete = True
                fp.new_path = "/dev/null"
            else:
                fp.new_path = new_path
            continue
        m = HUNK_RE.match(raw)
        if m:
            flush_hunk()
            ensure_file()
            old_count = int(m.group(2)) if m.group(2) is not None else 1
            new_count = int(m.group(4)) if m.group(4) is not None else 1
            hunk = Hunk(
                old_start=int(m.group(1)),
                old_count=old_count,
                new_start=int(m.group(3)),
                new_count=new_count,
                header=raw,
            )
            continue
        if raw.startswith("\\"):
            if hunk is not None and hunk.lines:
                hunk.lines[-1].no_newline = True
            continue
        if hunk is None:
            continue
        if raw.startswith("+"):
            hunk.lines.append(HunkLine("+", raw[1:]))
        elif raw.startswith("-"):
            hunk.lines.append(HunkLine("-", raw[1:]))
        elif raw.startswith(" "):
            hunk.lines.append(HunkLine(" ", raw[1:]))
        else:
            hunk.lines.append(HunkLine(" ", raw))
    flush_hunk()
    return [f for f in files if f.hunks or f.is_binary or f.is_new or f.is_delete or f.rename]


def _eq_line(a: str, b: str) -> bool:
    return a == b or a.rstrip("\r") == b.rstrip("\r")


def _find_window(old: List[str], needle: List[str], hint: int, fuzz: int = 12) -> Optional[int]:
    if not needle:
        return max(0, min(hint, len(old)))
    n = len(needle)
    if n > len(old):
        return None
    hint = max(0, min(hint, len(old)))
    order = [hint]
    for d in range(1, fuzz + 1):
        if hint - d >= 0:
            order.append(hint - d)
        if hint + d + n <= len(old):
            order.append(hint + d)
    for start in order:
        if start < 0 or start + n > len(old):
            continue
        if all(_eq_line(old[start + i], needle[i]) for i in range(n)):
            return start
    for start in range(0, len(old) - n + 1):
        if all(_eq_line(old[start + i], needle[i]) for i in range(n)):
            return start
    return None


def apply_hunks(pre: str, patch: PatchFile) -> Tuple[str, List[AddedLine], Optional[str]]:
    if patch.is_combined:
        return pre, [], "combined diff (unplaced)"
    if patch.is_binary:
        return pre, [], "binary patch"
    if patch.is_new and not pre:
        post_lines: List[str] = []
        added: List[AddedLine] = []
        for h in patch.hunks:
            for hl in h.lines:
                if hl.kind == "+":
                    post_lines.append(hl.text)
                    added.append(
                        AddedLine(
                            path=patch.new_path,
                            line=len(post_lines),
                            text=hl.text,
                            old_path=patch.old_path,
                        )
                    )
        post = "\n".join(post_lines)
        if post_lines:
            post += "\n"
        return post, added, None

    old = pre.splitlines()
    new_lines: List[str] = []
    added = []
    old_i = 0
    for h in patch.hunks:
        needle = [hl.text for hl in h.lines if hl.kind in {" ", "-"}]
        hint = (h.old_start - 1) if h.old_start > 0 else old_i
        start = _find_window(old, needle, hint)
        if start is None:
            guessed: List[AddedLine] = []
            new_ln = h.new_start
            for hl in h.lines:
                if hl.kind == "+":
                    guessed.append(
                        AddedLine(
                            path=patch.new_path,
                            line=new_ln,
                            text=hl.text,
                            old_path=patch.old_path,
                            error="hunk does not apply",
                        )
                    )
                    new_ln += 1
                elif hl.kind == " ":
                    new_ln += 1
            return (
                pre,
                guessed,
                "hunk @@ -{} does not apply to {}".format(
                    h.old_start, patch.old_path or patch.new_path
                ),
            )
        if start < old_i:
            return pre, [], "overlapping hunk at {}:{}".format(patch.new_path, h.old_start)
        while old_i < start:
            new_lines.append(old[old_i])
            old_i += 1
        for hl in h.lines:
            if hl.kind in {" ", "-"}:
                old_i += 1
                if hl.kind == " ":
                    new_lines.append(hl.text)
            elif hl.kind == "+":
                new_lines.append(hl.text)
                added.append(
                    AddedLine(
                        path=patch.new_path,
                        line=len(new_lines),
                        text=hl.text,
                        old_path=patch.old_path,
                    )
                )
    while old_i < len(old):
        new_lines.append(old[old_i])
        old_i += 1
    post = "\n".join(new_lines)
    if new_lines:
        post += "\n"
    elif pre.endswith("\n"):
        post = "\n" if pre == "\n" else ""
    return post, added, None


def is_git_repo(path: Path) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def git_show(repo: Path, rev: str, relpath: str) -> Optional[str]:
    if not rev or rev in {":wt", ".", "WORKTREE", "worktree"}:
        return None
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", "{}:{}".format(rev, relpath)],
        capture_output=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", errors="replace")


def read_worktree(root: Path, relpath: str) -> Optional[str]:
    p = Path(relpath)
    if not p.is_absolute():
        p = root / relpath
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def load_preimage(root: Path, base: str, path: str, old_path: str) -> Optional[str]:
    candidates = []
    if old_path and old_path != "/dev/null":
        candidates.append(old_path)
    if path and path != "/dev/null":
        candidates.append(path)
    seen: Set[str] = set()
    if is_git_repo(root) and base not in {":wt", ".", "WORKTREE", "worktree"}:
        for c in candidates:
            if c in seen:
                continue
            seen.add(c)
            src = git_show(root, base, c)
            if src is not None:
                return src
    seen.clear()
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        src = read_worktree(root, c)
        if src is not None:
            return src
    return None


def _path_wanted(path: str, path_filter: Optional[Set[str]]) -> bool:
    if not path_filter:
        return True
    rel = path
    for f in path_filter:
        if rel == f or rel.endswith("/" + f) or f.endswith("/" + rel):
            return True
        if Path(f).name == Path(rel).name and "/" not in f:
            return True
    return False


def minus_lines(patch: PatchFile) -> List[str]:
    return [hl.text for h in patch.hunks for hl in h.lines if hl.kind == "-"]


def _image(
    *,
    path: str,
    old_path: str,
    pre: Optional[str],
    post: Optional[str],
    added: List[AddedLine],
    patch: PatchFile,
    error: Optional[str] = None,
) -> FileImage:
    return FileImage(
        path=path,
        old_path=old_path,
        pre=pre,
        post=post,
        added=added,
        error=error,
        binary=patch.is_binary,
        is_new=patch.is_new,
        is_delete=patch.is_delete,
        rename=patch.rename,
        removed=minus_lines(patch),
    )


def overlay_diff(
    text: str,
    root: Path,
    base: str = "HEAD",
    path_filter: Optional[Set[str]] = None,
) -> List[FileImage]:
    out: List[FileImage] = []
    for patch in parse_unified_diff(text):
        path = patch.new_path if patch.new_path != "/dev/null" else patch.old_path
        if not _path_wanted(path, path_filter):
            continue
        if patch.is_combined:
            out.append(
                _image(
                    path=path,
                    old_path=patch.old_path,
                    pre=None,
                    post=None,
                    added=[],
                    patch=patch,
                    error="combined diff (unplaced)",
                )
            )
            continue
        if patch.is_binary:
            out.append(
                _image(
                    path=path,
                    old_path=patch.old_path,
                    pre=None,
                    post=None,
                    added=[],
                    patch=patch,
                    error="binary patch",
                )
            )
            continue
        if patch.is_delete and not any(hl.kind == "+" for h in patch.hunks for hl in h.lines):
            out.append(
                _image(
                    path=path,
                    old_path=patch.old_path,
                    pre=load_preimage(root, base, path, patch.old_path),
                    post=None,
                    added=[],
                    patch=patch,
                )
            )
            continue
        if patch.rename and not patch.hunks:
            pre = load_preimage(root, base, path, patch.old_path) or ""
            out.append(
                _image(
                    path=path,
                    old_path=patch.old_path,
                    pre=pre,
                    post=pre,
                    added=[],
                    patch=patch,
                )
            )
            continue
        pre = "" if patch.is_new else load_preimage(root, base, path, patch.old_path)
        if pre is None:
            if patch.is_new or (patch.hunks and all(h.old_count == 0 for h in patch.hunks)):
                pre = ""
            else:
                guessed = []
                for h in patch.hunks:
                    new_ln = h.new_start
                    for hl in h.lines:
                        if hl.kind == "+":
                            guessed.append(
                                AddedLine(
                                    path=path,
                                    line=new_ln,
                                    text=hl.text,
                                    old_path=patch.old_path,
                                    error="pre-image unavailable",
                                )
                            )
                            new_ln += 1
                        elif hl.kind == " ":
                            new_ln += 1
                out.append(
                    _image(
                        path=path,
                        old_path=patch.old_path,
                        pre=None,
                        post=None,
                        added=guessed,
                        patch=patch,
                        error="pre-image unavailable",
                    )
                )
                continue
        post, added, err = apply_hunks(pre, patch)
        if err:
            out.append(
                _image(
                    path=path,
                    old_path=patch.old_path,
                    pre=pre,
                    post=None,
                    added=added,
                    patch=patch,
                    error=err,
                )
            )
            continue
        out.append(
            _image(
                path=path,
                old_path=patch.old_path,
                pre=pre,
                post=post,
                added=added,
                patch=patch,
            )
        )
    return out
