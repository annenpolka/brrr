"""Exclusive-A path-conditions of an in-memory overlay, clustered.

A is the pre-image (HEAD / --base). B is the post-image after the patch
is overlaid in memory. The object is stacks true on A and false on B —
not the stacks the patch births.

Sibling arms of one fork (`if` / `elif` / given-else / sequential `if`)
are one obituary, not N covering rows.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional, Sequence

from .index import FileIndex
from .model import Frame, Locus, collapse
from .overlay import FileImage


CONTAINER_KINDS = {
    "class",
    "impl",
    "struct",
    "enum",
    "protocol",
    "extension",
    "module",
}
FN_KINDS = {"fn"}
SKIP_STACK_KINDS = {"eval", "stmt", "body", "raw"}

SOURCE_EXTS = {
    ".py",
    ".pyi",
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

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
IDENT_STOP = {
    "none",
    "some",
    "true",
    "false",
    "self",
    "this",
    "super",
    "return",
    "bytes",
    "byte",
    "len",
    "let",
    "var",
    "const",
    "async",
    "await",
    "func",
    "function",
    "class",
    "struct",
    "enum",
    "impl",
    "pub",
    "public",
    "private",
    "static",
    "given",
    "guard",
    "else",
    "elif",
    "then",
    "with",
    "from",
    "import",
    "null",
    "undefined",
    "option",
    "result",
    "pathbuf",
    "string",
    "str",
    "int",
    "bool",
    "where",
    "when",
    "into",
}

_CMP_OPS = ("==", "!=", ">=", "<=", ">", "<")


def posix_rel(path: str) -> str:
    return path.replace("\\", "/")


def is_source_path(path: str) -> bool:
    if not path or path in {"/dev/null", "dev/null"}:
        return False
    return Path(path).suffix.lower() in SOURCE_EXTS


def fn_name(pred: str) -> str:
    p = " ".join((pred or "").split())
    if "(" in p:
        p = p[: p.index("(")]
    parts = p.replace("::", " ").split()
    return parts[-1] if parts else ""


def cond_frames(frames: Sequence[Frame], *, with_fn: bool = False) -> list[Frame]:
    skip = set(CONTAINER_KINDS) | set(SKIP_STACK_KINDS)
    if not with_fn:
        skip |= FN_KINDS
    return [fr for fr in frames if fr.kind not in skip]


def cond_key(frames: Sequence[Frame], *, with_fn: bool = False) -> tuple[tuple[str, str], ...]:
    return tuple(fr.key() for fr in cond_frames(frames, with_fn=with_fn))


def cond_label(key: Sequence[tuple[str, str]]) -> str:
    if not key:
        return "(empty stack)"
    parts = []
    for kind, pred in key:
        pred = pred.strip()
        parts.append(f"{kind} {pred}".strip() if pred else kind)
    return " | ".join(parts)


def function_of(loc: Locus) -> str:
    if loc.function:
        name = fn_name(loc.function)
        if name:
            return name
    for fr in reversed(loc.frames):
        if fr.kind in FN_KINDS:
            name = fn_name(fr.pred)
            if name:
                return name
    return ""


def holder_of(loc: Locus, grain: str) -> str:
    path = posix_rel(loc.file)
    if grain == "files":
        return path
    if grain == "functions":
        name = function_of(loc)
        return f"{path}:{name}" if name else path
    return f"{path}:{loc.line}"


def _uniq(items: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def holder_key(holders: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({h for h in holders if h}))


def path_stem(path: str) -> str:
    base = posix_rel(path).rsplit("/", 1)[-1]
    return base.rsplit(".", 1)[0] if "." in base else base


def _name_like_pred(pred: str) -> bool:
    if not pred:
        return False
    if any("\u3040" <= c <= "\u9fff" for c in pred):
        return len(pred) >= 3
    if "-" in pred or "_" in pred:
        return True
    if re.search(r"[a-z][A-Z]", pred) or re.match(r"^[A-Z]{2,}[a-z]", pred):
        return True
    if re.match(r"^[A-Z][a-z]+[A-Z]", pred):
        return True
    idents = IDENT_RE.findall(pred)
    return any(len(i) >= 8 and i.lower() not in IDENT_STOP for i in idents)


def _pred_name_like(stack: "Stack") -> bool:
    return any(_name_like_pred(pred) for _k, pred in stack.key)


def _positive_arm(stack: "Stack") -> bool:
    if not stack.key:
        return False
    kind, pred = stack.key[-1]
    if kind in {"else", "guard-else", "elif", "try-else", "for-else", "while-else"}:
        return False
    if kind == "given" and pred.lstrip().startswith("¬"):
        return False
    return kind in {"if", "guard", "while", "match", "case", "switch"} and _name_like_pred(pred)


@dataclass
class SideHit:
    holders: list[str] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)
    pin: tuple[str, int] | None = None
    fn: str = ""


def stacks_in_source(
    source: str,
    path: str,
    *,
    grain: str = "files",
    with_fn: bool = False,
) -> dict[tuple[tuple[str, str], ...], SideHit]:
    if not source:
        return {}
    idx = FileIndex(source, path)
    by_key: dict[tuple[tuple[str, str], ...], list[Locus]] = {}
    for ln in range(1, idx.nlines + 1):
        loc = idx.at(ln)
        if loc.error:
            continue
        loc.file = path
        key = cond_key(loc.frames, with_fn=with_fn)
        if not key:
            continue
        by_key.setdefault(key, []).append(loc)
    out: dict[tuple[tuple[str, str], ...], SideHit] = {}
    for key, locs in by_key.items():
        pin_loc = locs[len(locs) // 2]
        out[key] = SideHit(
            holders=_uniq(holder_of(loc, grain) for loc in locs),
            paths=[path],
            pin=(path, pin_loc.line),
            fn=function_of(pin_loc),
        )
    return out


def _merge_hit(
    merged: dict[tuple[tuple[str, str], ...], SideHit],
    key: tuple[tuple[str, str], ...],
    hit: SideHit,
) -> None:
    cur = merged.get(key)
    if cur is None:
        merged[key] = SideHit(
            holders=list(hit.holders),
            paths=list(hit.paths),
            pin=hit.pin,
            fn=hit.fn,
        )
        return
    for h in hit.holders:
        if h not in cur.holders:
            cur.holders.append(h)
    for p in hit.paths:
        if p not in cur.paths:
            cur.paths.append(p)
    if cur.pin is None:
        cur.pin = hit.pin
    if not cur.fn:
        cur.fn = hit.fn


@dataclass
class Stack:
    key: tuple[tuple[str, str], ...]
    holders_a: list[str]
    holders_b: list[str]
    paths_a: list[str]
    paths_b: list[str]
    pin_a: tuple[str, int] | None
    pin_b: tuple[str, int] | None
    fn: str = ""
    minus_hit: bool = False

    @property
    def label(self) -> str:
        return cond_label(self.key)

    @property
    def depth(self) -> int:
        return len(self.key)

    @property
    def role(self) -> str:
        a, b = bool(self.holders_a), bool(self.holders_b)
        if a and not b:
            return "exclusive_a"
        if b and not a:
            return "exclusive_b"
        if not a and not b:
            return "empty"
        if holder_key(self.holders_a) == holder_key(self.holders_b):
            return "shared"
        added = set(self.holders_b) - set(self.holders_a)
        dropped = set(self.holders_a) - set(self.holders_b)
        if added and dropped:
            return "move"
        if added and not dropped:
            return "spread"
        if dropped and not added:
            return "shrink"
        return "hold"

    @property
    def true_on(self) -> str:
        role = self.role
        if role == "exclusive_a":
            return "A"
        if role == "exclusive_b":
            return "B"
        return "AB"

    @property
    def junk(self) -> bool:
        if not self.key:
            return True
        kinds = {k for k, _ in self.key}
        if kinds <= {"else", "guard-else", "try-else", "for-else", "while-else", "arm"}:
            return True
        if len(self.key) == 1 and self.key[0][0] in {"else", "try", "defer", "for", "while", "arm"}:
            pred = self.key[0][1].strip()
            if not pred or pred in {"_", "true", "false"} or pred.startswith("_ "):
                return True
        return False

    def pin_for_true(self) -> tuple[str, int] | None:
        if self.role == "exclusive_a":
            return self.pin_a
        if self.pin_b:
            return self.pin_b
        return self.pin_a

    def to_record(self) -> dict:
        pin = self.pin_for_true()
        return {
            "true_on": self.true_on,
            "role": self.role,
            "label": self.label,
            "depth": self.depth,
            "holders_a": list(self.holders_a),
            "holders_b": list(self.holders_b),
            "paths_a": list(self.paths_a),
            "paths_b": list(self.paths_b),
            "pin": f"{pin[0]}:{pin[1]}" if pin else None,
            "fn": self.fn,
            "minus_hit": self.minus_hit,
            "key": [{"kind": k, "pred": p} for k, p in self.key],
        }


def _on_deleted(stack: Stack, only_a: set[str]) -> bool:
    return any(p in only_a for p in stack.paths_a)


def dead_rank(stack: Stack, only_a: set[str]) -> tuple:
    deleted = 0 if _on_deleted(stack, only_a) else 1
    named = 0 if _pred_name_like(stack) else 1
    positive = 0 if _positive_arm(stack) else 1
    witnessed = 0 if stack.minus_hit else 1
    return (deleted, named, positive, witnessed, -stack.depth, len(stack.label), stack.label)


def _key_nested(inner: tuple[tuple[str, str], ...], outer: tuple[tuple[str, str], ...]) -> bool:
    if not inner or len(inner) >= len(outer):
        return False
    n = len(inner)
    return outer[:n] == inner or outer[-n:] == inner


def pred_norm(pred: str) -> str:
    return collapse(pred).replace(" ", "")


def unwrap_neg(pred: str) -> Optional[str]:
    p = (pred or "").strip()
    if not p.startswith("¬"):
        return None
    p = p[1:].strip()
    if p.startswith("(") and p.endswith(")") and p.count("(") == p.count(")"):
        p = p[1:-1].strip()
    return p


def pred_eq(a: str, b: str) -> bool:
    return pred_norm(a) == pred_norm(b)


def pred_stem(pred: str) -> str:
    p = unwrap_neg(pred) or pred
    p = collapse(p)
    p = re.sub(r"^(let|var|guard|case)\s+", "", p)
    for op in _CMP_OPS:
        if op in p:
            return collapse(p.split(op, 1)[0])
    if "=" in p and not p.lstrip().startswith("="):
        return collapse(p.split("=", 1)[0])
    return p


def peel_given_negs(
    key: Sequence[tuple[str, str]],
) -> tuple[list[str], tuple[tuple[str, str], ...]]:
    peeled: list[str] = []
    i = 0
    while i < len(key):
        kind, pred = key[i]
        if kind == "given":
            inner = unwrap_neg(pred)
            if not inner:
                break
            peeled.append(inner)
            i += 1
            continue
        if kind == "else":
            inner = unwrap_neg(pred) or pred
            if inner:
                peeled.append(inner)
            i += 1
            continue
        break
    return peeled, tuple(key[i:])


def _share_paths(a: Stack, b: Stack) -> bool:
    return bool(set(a.paths_a) & set(b.paths_a))


def _pin_line(stack: Stack) -> int:
    pin = stack.pin_a or stack.pin_b
    return pin[1] if pin else 0


def lead_rank(stack: Stack, only_a: set[str]) -> tuple:
    """Prefer the root true-arm (`if P`) over sequential / given-else.

    Cover rank for *which cluster* still uses dead_rank (deeper named
    arms win). The obituary *name* and pin should be wane's true-arm.
    """
    kind0 = stack.key[0][0] if stack.key else ""
    peeled, _rest = peel_given_negs(stack.key)
    root_if = 0 if (not peeled and kind0 == "if") else 1
    return (
        root_if,
        0 if _positive_arm(stack) else 1,
        0 if kind0 == "elif" else 1,
        stack.depth,
        dead_rank(stack, only_a),
    )


def member_display_rank(stack: Stack) -> tuple:
    kind0 = stack.key[0][0] if stack.key else ""
    peeled, rest = peel_given_negs(stack.key)
    if not peeled and kind0 == "if":
        return (0, stack.label)
    if kind0 == "elif":
        return (1, stack.label)
    if peeled and rest and rest[0][0] == "if":
        return (2, stack.label)
    return (3, stack.label)


def _if_head_pred(key: Sequence[tuple[str, str]]) -> Optional[str]:
    if not key:
        return None
    kind, pred = key[0]
    if kind in {"if", "guard"}:
        return pred
    return None


def _if_vs_fallthrough(if_key: Sequence[tuple[str, str]], other: Sequence[tuple[str, str]]) -> bool:
    head = _if_head_pred(if_key)
    if not head:
        return False
    peel, _rest = peel_given_negs(other)
    return bool(peel) and pred_eq(peel[0], head)


def _shared_peel_prefix(ka: Sequence[tuple[str, str]], kb: Sequence[tuple[str, str]]) -> bool:
    pa, _ = peel_given_negs(ka)
    pb, _ = peel_given_negs(kb)
    if not pa or not pb:
        return False
    n = min(len(pa), len(pb))
    return all(pred_eq(pa[i], pb[i]) for i in range(n))


def _elif_matches_chain(elif_s: Stack, other: Stack) -> bool:
    if not elif_s.key or elif_s.key[0][0] != "elif":
        return False
    q = elif_s.key[0][1]
    peel, rest = peel_given_negs(other.key)
    if not peel:
        return False
    if rest and rest[0][0] in {"if", "elif"} and pred_eq(rest[0][1], q):
        return True
    return any(pred_eq(p, q) for p in peel)


def complement_siblings(a: Stack, b: Stack) -> bool:
    """True if A and B are fallthrough / sequential / given-else of one fork."""
    if a is b or a.key == b.key:
        return False
    if not _share_paths(a, b):
        return False
    if _if_vs_fallthrough(a.key, b.key) or _if_vs_fallthrough(b.key, a.key):
        return True
    if _shared_peel_prefix(a.key, b.key):
        return True
    if _elif_matches_chain(a, b) or _elif_matches_chain(b, a):
        return True
    return False


class _UF:
    def __init__(self, n: int) -> None:
        self.p = list(range(n))

    def find(self, i: int) -> int:
        while self.p[i] != i:
            self.p[i] = self.p[self.p[i]]
            i = self.p[i]
        return i

    def union(self, i: int, j: int) -> None:
        ri, rj = self.find(i), self.find(j)
        if ri != rj:
            self.p[rj] = ri


def _attach_elifs(stacks: Sequence[Stack], uf: _UF) -> None:
    ifs = [(i, s) for i, s in enumerate(stacks) if s.key and s.key[0][0] == "if"]
    elifs = [(i, s) for i, s in enumerate(stacks) if s.key and s.key[0][0] == "elif"]
    elses = [
        (i, s)
        for i, s in enumerate(stacks)
        if s.key and s.key[0][0] in {"else", "guard-else"}
    ]
    for ei, es in elifs + elses:
        cands: list[tuple[int, Stack]] = []
        for ii, iss in ifs:
            if not _share_paths(es, iss):
                continue
            if es.fn and iss.fn and es.fn != iss.fn:
                continue
            if _pin_line(iss) <= _pin_line(es):
                cands.append((ii, iss))
        if not cands:
            # stem fallback when pin order is missing
            stem = pred_stem(es.key[0][1]) if es.key else ""
            for ii, iss in ifs:
                if _share_paths(es, iss) and pred_stem(iss.key[0][1]) == stem:
                    cands.append((ii, iss))
        if not cands:
            continue
        nearest = max(cands, key=lambda pair: _pin_line(pair[1]))
        uf.union(ei, nearest[0])


def cluster_siblings(stacks: Sequence[Stack]) -> list[list[Stack]]:
    """Group sibling arms. Independent if-chains stay separate."""
    if not stacks:
        return []
    uf = _UF(len(stacks))
    for i in range(len(stacks)):
        for j in range(i + 1, len(stacks)):
            if complement_siblings(stacks[i], stacks[j]):
                uf.union(i, j)
    _attach_elifs(stacks, uf)
    groups: dict[int, list[Stack]] = {}
    for i, s in enumerate(stacks):
        groups.setdefault(uf.find(i), []).append(s)
    return list(groups.values())


@dataclass
class Obituary:
    members: list[Stack]
    only_a: set[str] = field(default_factory=set)

    @property
    def lead(self) -> Stack:
        return min(self.members, key=lambda s: lead_rank(s, self.only_a))

    @property
    def arms_listed(self) -> list[Stack]:
        return sorted(self.members, key=member_display_rank)

    @property
    def label(self) -> str:
        return self.lead.label

    @property
    def arm_n(self) -> int:
        return len(self.members)

    @property
    def kinds(self) -> list[str]:
        seen: list[str] = []
        for s in self.arms_listed:
            k = s.key[0][0] if s.key else "?"
            if k == "given":
                k = "given-else" if (s.key and unwrap_neg(s.key[0][1])) else "given"
            if k not in seen:
                seen.append(k)
        return seen

    @property
    def role(self) -> str:
        return self.lead.role

    @property
    def true_on(self) -> str:
        return self.lead.true_on

    @property
    def paths_a(self) -> list[str]:
        return _uniq(p for s in self.members for p in s.paths_a)

    @property
    def holders_a(self) -> list[str]:
        return _uniq(h for s in self.members for h in s.holders_a)

    @property
    def depth(self) -> int:
        return max(s.depth for s in self.members)

    @property
    def fn(self) -> str:
        return self.lead.fn

    def pin_for_true(self) -> tuple[str, int] | None:
        return self.lead.pin_for_true()

    def to_record(self) -> dict:
        rec = self.lead.to_record()
        rec["arm_n"] = self.arm_n
        rec["kinds"] = self.kinds
        rec["arms"] = [s.to_record() for s in self.arms_listed]
        rec["label"] = self.label
        rec["paths_a"] = list(self.paths_a)
        rec["holders_a"] = list(self.holders_a)
        pin = self.pin_for_true()
        rec["pin"] = f"{pin[0]}:{pin[1]}" if pin else None
        return rec


def obituary_rank(obit: Obituary, only_a: set[str]) -> tuple:
    return min(dead_rank(s, only_a) for s in obit.members)


def dead_cover(
    stacks: Sequence[Stack],
    only_a: Sequence[str],
    *,
    limit: int = 8,
    also_changed: bool = False,
) -> list[Obituary]:
    """Cover with clustered exclusive-A obituaries. No exclusive-B, no AB else.

    Default leftover stays on deleted overlay paths. Vanished stacks
    inside surviving files are `--also-changed`. A move is not a death.
    Sibling arms of one fork occupy one slot.
    """
    only_a_src = [p for p in only_a if is_source_path(p)]
    only_a_set = set(only_a_src)
    pool = [s for s in stacks if s.true_on == "A" and not s.junk]
    if not also_changed:
        pool = [s for s in pool if _on_deleted(s, only_a_set)]
    if not pool:
        return []
    groups = cluster_siblings(pool)
    obituaries = [Obituary(members=list(g), only_a=only_a_set) for g in groups]
    obituaries.sort(key=lambda o: obituary_rank(o, only_a_set))

    chosen: list[Obituary] = []
    seen_leads: set[tuple[tuple[str, str], ...]] = set()

    def dominated(o: Obituary) -> bool:
        for c in chosen:
            if not (set(o.paths_a) & set(c.paths_a)):
                continue
            if _key_nested(o.lead.key, c.lead.key):
                return True
        return False

    for o in obituaries:
        if limit >= 0 and len(chosen) >= limit:
            break
        if o.lead.key in seen_leads:
            continue
        if dominated(o):
            continue
        seen_leads.add(o.lead.key)
        chosen.append(o)
    return chosen


def collapse_pred(pred: str) -> str:
    return collapse(pred).replace(" ", "")


def minus_mentions(pred: str, minus: Sequence[str]) -> bool:
    needle = collapse_pred(pred)
    if len(needle) < 4:
        return False
    for line in minus:
        hay = collapse_pred(line)
        if needle and needle in hay:
            return True
    return False


def stack_minus_hit(stack: Stack, minus_by_path: dict[str, list[str]]) -> bool:
    texts = []
    for path in stack.paths_a:
        texts.extend(minus_by_path.get(path, []))
    if not texts:
        for pred in (p for _k, p in stack.key):
            if minus_mentions(pred, [ln for rows in minus_by_path.values() for ln in rows]):
                return True
        return False
    return any(minus_mentions(pred, texts) for _k, pred in stack.key)


@dataclass
class OverlayDelta:
    only_a: list[str]
    only_b: list[str]
    changed: list[str]
    renamed: list[tuple[str, str]]
    unplaced: list[str]
    minus_by_path: dict[str, list[str]]


def classify_images(images: Sequence[FileImage]) -> OverlayDelta:
    only_a: list[str] = []
    only_b: list[str] = []
    changed: list[str] = []
    renamed: list[tuple[str, str]] = []
    unplaced: list[str] = []
    minus_by_path: dict[str, list[str]] = {}

    def add(seq: list[str], path: Optional[str]) -> None:
        if path and path not in seq and path != "/dev/null":
            seq.append(path)

    for img in images:
        old = img.old_path if img.old_path and img.old_path != "/dev/null" else ""
        new = img.path if img.path and img.path != "/dev/null" else ""
        a_path = old or new
        if a_path and img.removed:
            minus_by_path.setdefault(a_path, []).extend(img.removed)
            if old and old != a_path:
                minus_by_path.setdefault(old, []).extend(img.removed)
        if img.error and img.post is None and not img.is_delete:
            add(unplaced, new or old)
            continue
        if img.rename and old and new and old != new:
            renamed.append((old, new))
            add(only_a, old)
            add(only_b, new)
            continue
        if img.is_delete or (img.post is None and img.pre is not None):
            add(only_a, old or new)
            continue
        if img.is_new or (not img.pre and img.post):
            add(only_b, new or old)
            continue
        add(changed, new or old)
    return OverlayDelta(
        only_a=only_a,
        only_b=only_b,
        changed=changed,
        renamed=renamed,
        unplaced=unplaced,
        minus_by_path=minus_by_path,
    )


def discover_overlay_stacks(
    images: Sequence[FileImage],
    *,
    grain: str = "files",
    with_fn: bool = False,
) -> tuple[
    dict[tuple[tuple[str, str], ...], SideHit],
    dict[tuple[tuple[str, str], ...], SideHit],
]:
    stacks_a: dict[tuple[tuple[str, str], ...], SideHit] = {}
    stacks_b: dict[tuple[tuple[str, str], ...], SideHit] = {}
    for img in images:
        old = img.old_path if img.old_path and img.old_path != "/dev/null" else ""
        new = img.path if img.path and img.path != "/dev/null" else ""
        if img.pre and is_source_path(old or new):
            for key, hit in stacks_in_source(
                img.pre, old or new, grain=grain, with_fn=with_fn
            ).items():
                _merge_hit(stacks_a, key, hit)
        if img.post and is_source_path(new or old):
            for key, hit in stacks_in_source(
                img.post, new or old, grain=grain, with_fn=with_fn
            ).items():
                _merge_hit(stacks_b, key, hit)
    return stacks_a, stacks_b


def _superstack_hit(
    key: tuple[tuple[str, str], ...],
    other: dict[tuple[tuple[str, str], ...], SideHit],
) -> SideHit | None:
    """A prefix that still occupies a deeper B stack has not died."""
    if key in other:
        return other[key]
    best: SideHit | None = None
    best_len = 0
    for other_key, hit in other.items():
        if _key_nested(key, other_key) and len(other_key) > best_len:
            best = hit
            best_len = len(other_key)
    return best


def merge_stacks(
    a: dict[tuple[tuple[str, str], ...], SideHit],
    b: dict[tuple[tuple[str, str], ...], SideHit],
    *,
    minus_by_path: dict[str, list[str]] | None = None,
) -> list[Stack]:
    keys = set(a) | set(b)
    out: list[Stack] = []
    minus_by_path = minus_by_path or {}
    for key in keys:
        ha = a.get(key) or SideHit()
        hb = b.get(key) or SideHit()
        if ha.holders and not hb.holders:
            live = _superstack_hit(key, b)
            if live is not None:
                hb = live
        stack = Stack(
            key=key,
            holders_a=list(ha.holders),
            holders_b=list(hb.holders),
            paths_a=list(ha.paths),
            paths_b=list(hb.paths),
            pin_a=ha.pin,
            pin_b=hb.pin,
            fn=hb.fn or ha.fn,
        )
        if stack.role in {"empty", "shared"}:
            continue
        if stack.junk:
            continue
        stack.minus_hit = stack_minus_hit(stack, minus_by_path)
        out.append(stack)
    return out


@dataclass
class DirgeReport:
    covering: list[Obituary]
    distinguishing: list[Stack]
    delta: OverlayDelta
    born_n: int
    move_n: int
    death_n: int

    @property
    def births(self) -> list[Stack]:
        return [s for s in self.distinguishing if s.true_on == "B"]

    @property
    def moves(self) -> list[Stack]:
        return [s for s in self.distinguishing if s.role == "move"]

    @property
    def deaths(self) -> list[Stack]:
        return [s for s in self.distinguishing if s.true_on == "A"]

    @property
    def arm_n(self) -> int:
        return sum(o.arm_n for o in self.covering)


def dirge_from_images(
    images: Sequence[FileImage],
    *,
    grain: str = "files",
    with_fn: bool = False,
    limit: int = 8,
    also_changed: bool = False,
) -> DirgeReport:
    delta = classify_images(images)
    stacks_a, stacks_b = discover_overlay_stacks(images, grain=grain, with_fn=with_fn)
    distinguishing = merge_stacks(stacks_a, stacks_b, minus_by_path=delta.minus_by_path)
    covering = dead_cover(
        distinguishing,
        delta.only_a,
        limit=limit,
        also_changed=also_changed,
    )
    deaths = [s for s in distinguishing if s.true_on == "A" and not s.junk]
    births = [s for s in distinguishing if s.true_on == "B" and not s.junk]
    moves = [s for s in distinguishing if s.role == "move"]
    return DirgeReport(
        covering=covering,
        distinguishing=distinguishing,
        delta=delta,
        born_n=len(births),
        move_n=len(moves),
        death_n=len(deaths),
    )
