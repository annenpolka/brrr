"""Does this locus's path-condition rhyme with a seed stack?

Same: identical condition-frame keys.
Deeper: the seed key is a proper prefix (the other stack is a superset).
Not snippet containment — that is under(1). Not token rhyme — that is rg.
The seed is a content pin, not the first rg locator.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .model import Frame, Locus


def same_file(a: str, b: str) -> bool:
    if a == b:
        return True
    pa, pb = Path(a), Path(b)
    try:
        if pa.exists() and pb.exists():
            return pa.resolve() == pb.resolve()
    except OSError:
        pass
    return False


@dataclass
class Hit:
    loc: Locus
    relation: str  # "same" | "deeper"
    extra: list[Frame]
    start: int = 0
    end: int = 0
    seed: bool = False

    def __post_init__(self) -> None:
        if not self.start:
            self.start = self.loc.line
        if not self.end:
            self.end = self.loc.line

    @property
    def nlines(self) -> int:
        return self.end - self.start + 1

    @property
    def extra_text(self) -> str:
        if not self.extra:
            return ""
        return " | ".join(fr.render() for fr in self.extra)


def relation(
    seed: Locus,
    other: Locus,
    *,
    exact: bool = False,
    include_eval: bool = False,
    any_fn: bool = False,
) -> Optional[str]:
    """Return 'same' or 'deeper', or None if the stacks do not rhyme."""
    sk = seed.cond_key(include_eval=include_eval)
    if not sk:
        return None
    if not any_fn and seed.fn_ident() and other.fn_ident() != seed.fn_ident():
        return None
    ok = other.cond_key(include_eval=include_eval)
    if ok == sk:
        return "same"
    if exact:
        return None
    if len(ok) > len(sk) and ok[: len(sk)] == sk:
        return "deeper"
    return None


def extra_frames(
    seed: Locus,
    other: Locus,
    *,
    include_eval: bool = False,
) -> list[Frame]:
    sk = seed.effective_cond_frames(include_eval=include_eval)
    ok = other.effective_cond_frames(include_eval=include_eval)
    if len(ok) <= len(sk):
        return []
    return ok[len(sk) :]


def hit_for(
    seed: Locus,
    other: Locus,
    *,
    exact: bool = False,
    include_eval: bool = False,
    any_fn: bool = False,
) -> Optional[Hit]:
    rel = relation(
        seed,
        other,
        exact=exact,
        include_eval=include_eval,
        any_fn=any_fn,
    )
    if rel is None:
        return None
    return Hit(
        loc=other,
        relation=rel,
        extra=extra_frames(seed, other, include_eval=include_eval),
        start=other.line,
        end=other.line,
        seed=same_file(other.file, seed.file) and other.line == seed.line,
    )
