"""Turn a locator into the predicate it pointed at."""

from __future__ import annotations

from .match import STRUCT_KINDS, strip_not
from .model import Locus


def _unique(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for s in items:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def derive_snippets(loc: Locus, *, peel_intro: bool = True) -> list[str]:
    """Snippets implied by this locus.

    If the locator sits on the `if !P` / `guard P` line itself, peel a
    leading `!` / `¬` so the question is the in-force given (the
    fallthrough `rg` never printed). Payload lines keep the stack as
    written.
    """
    same = [
        fr
        for fr in loc.frames
        if fr.line == loc.line and fr.kind not in STRUCT_KINDS
    ]
    out: list[str] = []
    if same:
        for fr in same:
            pred = (fr.pred or "").strip()
            if not pred:
                continue
            core, inverted = strip_not(pred)
            if (
                peel_intro
                and inverted
                and core
                and fr.kind in {"if", "elif", "eval", "guard"}
            ):
                out.append(core)
            else:
                out.append(pred)
        return _unique(out)

    for fr in reversed(loc.frames):
        if fr.kind in STRUCT_KINDS or fr.kind == "eval":
            continue
        pred = (fr.pred or "").strip()
        if pred:
            return [pred]
    here = (loc.here or "").strip()
    return [here] if here else []
