"""Does this locus's path-condition contain the named snippet?"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .model import Frame, Locus

# Frames that are *conditions in force*, not the function they live in
# and not the line that is still evaluating the test.
COND_KINDS = {
    "if",
    "elif",
    "else",
    "given",
    "guard",
    "guard-else",
    "for",
    "while",
    "try",
    "except",
    "catch",
    "finally",
    "try-else",
    "for-else",
    "while-else",
    "with",
    "match",
    "case",
    "switch",
    "arm",
    "ifexp",
    "ifexp-else",
    "List-comp",
    "Set-comp",
    "Dict-comp",
    "genexp",
}

EVAL_KINDS = {"eval"}

STRUCT_KINDS = {
    "fn",
    "class",
    "impl",
    "struct",
    "enum",
    "protocol",
    "extension",
    "module",
}

# These kinds store the *failed* test, not the in-force condition.
INVERT_KINDS = {"else", "guard-else"}

_BSTRING = re.compile(r"\bb([\"'])")
_PUNCT = set("()[]{}.,:;+-*/|&!?=~^%<>\\")
_CAMEL = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+")


def fold(text: str) -> str:
    """Casefold a predicate so spacing, quotes, and b\"…\" prefixes drop out."""
    s = text.replace("¬", " not ")
    s = _BSTRING.sub(r"\1", s)
    s = s.replace('"', "").replace("'", "")
    s = s.replace("(", "").replace(")", "")
    s = s.casefold()
    return re.sub(r"\s+", "", s)


def _split_ident(ident: str) -> list[str]:
    parts = ident.replace("-", "_").split("_")
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        bits = _CAMEL.findall(part)
        out.extend(bits if bits else [part])
    return out or [ident]


def tokens(text: str) -> list[str]:
    s = text.replace("¬", " not ")
    s = _BSTRING.sub(r"\1", s)
    s = s.replace('"', " ").replace("'", " ")
    out: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isalnum() or ch == "_":
            j = i + 1
            while j < len(s) and (s[j].isalnum() or s[j] == "_"):
                j += 1
            out.extend(t.casefold() for t in _split_ident(s[i:j]))
            i = j
            continue
        out.append(ch.casefold())
        i += 1
    return out


def _is_punct(tok: str) -> bool:
    return bool(tok) and all(ch in _PUNCT for ch in tok)


def _tok_eq(a: str, b: str) -> bool:
    return a == b


def fold_contains(needle: str, hay: str) -> bool:
    """fold(needle) is a substring of fold(hay) at an identifier boundary.

    Prevents `unknownID` from hitting `unknownSelectionUnitID` and
    `range` from hitting `invalidRange`.
    """
    fn, fh = fold(needle), fold(hay)
    if not fn or not fh:
        return False
    start = 0
    while True:
        i = fh.find(fn, start)
        if i < 0:
            return False
        left_ok = i == 0 or not fh[i - 1].isalnum()
        if left_ok:
            return True
        start = i + 1


def _contiguous(needle: list[str], hay: list[str]) -> bool:
    """Needle tokens appear in order. Extra punctuation in hay may be skipped
    only when the current needle token is not itself punctuation — so
    `Decision:` does not match `decision_section`.
    """
    if not needle:
        return False
    for i in range(len(hay)):
        k = 0
        j = i
        while k < len(needle) and j < len(hay):
            if _is_punct(hay[j]) and (
                not _is_punct(needle[k]) or not _tok_eq(needle[k], hay[j])
            ):
                j += 1
                continue
            if _tok_eq(needle[k], hay[j]):
                k += 1
                j += 1
                continue
            break
        if k == len(needle):
            return True
    return False


def snippet_in_text(snippet: str, text: str, *, regex: bool = False) -> bool:
    if not snippet:
        return False
    if regex:
        try:
            return re.search(snippet, text, re.I) is not None
        except re.error:
            return False
    if fold_contains(snippet, text):
        return True
    nt = tokens(snippet)
    if not nt:
        return False
    return _contiguous(nt, tokens(text))


def _unwrap_parens(pred: str) -> str:
    p = pred.strip()
    while len(p) >= 2 and p[0] == "(" and p[-1] == ")":
        depth = 0
        matched = True
        for i, ch in enumerate(p):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and i != len(p) - 1:
                    matched = False
                    break
        if not matched:
            break
        p = p[1:-1].strip()
    return p


def strip_not(pred: str) -> tuple[str, bool]:
    """Peel a leading engine/`!` negation. `if not x` stays as written (not peeled)."""
    p = _unwrap_parens(pred)
    if p.startswith("¬(") and p.endswith(")"):
        return p[2:-1], True
    if p.startswith("¬"):
        return p[1:], True
    if p.startswith("!") and not p.startswith("!="):
        return _unwrap_parens(p[1:]), True
    return p, False


def snippet_asks_inverted(snippet: str) -> bool:
    s = snippet.strip().casefold()
    if s.startswith("¬") or s.startswith("not "):
        return True
    if s.startswith("!") and not s.startswith("!="):
        return True
    if s.startswith("guard-else") or s.startswith("else ") or s == "else":
        return True
    if "¬" in snippet:
        return True
    return False


def frame_is_inverted(fr: Frame) -> bool:
    if fr.kind in INVERT_KINDS:
        return True
    _, wrapped = strip_not(fr.pred)
    return wrapped


def frame_match_text(fr: Frame) -> str:
    """Text the snippet is allowed to hit, polarity already decided."""
    if fr.kind in INVERT_KINDS:
        return fr.render()
    core, wrapped = strip_not(fr.pred)
    if wrapped:
        return f"{fr.kind} {core}".strip()
    return fr.render()


def polarity_ok(fr: Frame, snippet: str, *, kinds: set[str] | None) -> bool:
    """Positive snippet vs inverted frame is a miss, unless user named the inversion.

    `--kind given` is an explicit request to look inside given frames, including ¬(P).
    """
    if kinds:
        return True
    inv_frame = frame_is_inverted(fr)
    inv_snip = snippet_asks_inverted(snippet)
    if inv_frame and not inv_snip:
        return False
    if inv_snip and not inv_frame and fr.kind not in INVERT_KINDS:
        # `not user.can_delete` is a positive `if` whose pred starts with `not `.
        # Allow it: the user named the predicate as written.
        return True
    return True


def frame_haystacks(fr: Frame) -> list[str]:
    core, wrapped = strip_not(fr.pred)
    out = [fr.render(), fr.pred, f"{fr.kind} {fr.pred}".strip()]
    if wrapped:
        out.append(core)
        out.append(f"{fr.kind} {core}")
    return out


def frame_allowed(
    fr: Frame,
    *,
    kinds: set[str] | None,
    include_eval: bool,
    include_struct: bool,
) -> bool:
    if kinds is not None:
        return fr.kind in kinds
    if fr.kind in STRUCT_KINDS:
        return include_struct
    if fr.kind in EVAL_KINDS:
        return include_eval
    return True


def frame_matches(
    fr: Frame,
    snippet: str,
    *,
    regex: bool = False,
    kinds: set[str] | None = None,
    include_eval: bool = False,
    include_struct: bool = False,
) -> bool:
    if not frame_allowed(
        fr, kinds=kinds, include_eval=include_eval, include_struct=include_struct
    ):
        return False
    if not polarity_ok(fr, snippet, kinds=kinds):
        return False
    # inverted frames: only match if the user named the inversion or the kind
    if frame_is_inverted(fr) and not snippet_asks_inverted(snippet) and not kinds:
        return False
    hays = frame_haystacks(fr)
    if frame_is_inverted(fr) and not snippet_asks_inverted(snippet):
        hays = [fr.render()]
    return any(snippet_in_text(snippet, hay, regex=regex) for hay in hays)


def effective_frames(loc: Locus) -> list[Frame]:
    """Drop a guard/if that is shadowed by its else/guard-else (P is not in force)."""
    frames = list(loc.frames)
    skip: set[int] = set()
    for i, fr in enumerate(frames):
        if fr.kind == "guard-else":
            for j in range(i - 1, -1, -1):
                if frames[j].kind == "guard":
                    skip.add(j)
                    break
        elif fr.kind == "else":
            for j in range(i - 1, -1, -1):
                if frames[j].kind in {"if", "elif"}:
                    skip.add(j)
                    break
    return [fr for i, fr in enumerate(frames) if i not in skip]


def split_snippets(pred: str) -> list[str]:
    """'A | B' is AND of snippets (a path-condition fragment list)."""
    if " | " in pred:
        return [p.strip() for p in pred.split(" | ") if p.strip()]
    return [pred.strip()] if pred.strip() else []


@dataclass
class Matcher:
    snippets: list[str]
    kinds: set[str] | None = None
    regex: bool = False
    include_eval: bool = False
    include_struct: bool = False

    def matching_frames(self, loc: Locus) -> list[Frame]:
        if not self.snippets:
            return []
        frames = effective_frames(loc)
        matched: list[Frame] = []
        seen: set[tuple[str, str, int]] = set()
        for snip in self.snippets:
            hit = [
                fr
                for fr in frames
                if frame_matches(
                    fr,
                    snip,
                    regex=self.regex,
                    kinds=self.kinds,
                    include_eval=self.include_eval,
                    include_struct=self.include_struct,
                )
            ]
            if not hit:
                return []
            for fr in hit:
                key = (fr.kind, fr.pred, fr.line)
                if key not in seen:
                    seen.add(key)
                    matched.append(fr)
        return matched

    def matches(self, loc: Locus) -> bool:
        return bool(self.matching_frames(loc))
