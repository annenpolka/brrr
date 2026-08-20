from __future__ import annotations

import re
from dataclasses import dataclass, field

from .model import Frame, Locus

SPACE_AFTER = {
    "->",
    "==",
    "!=",
    "=",
    "+",
    "-",
    ">=",
    "<=",
    "..=",
    "[",
    "=>",
}

# unary minus should not force a space; handled by not treating lone '-' after
# another operator as SPACE_AFTER when it's part of a number. We keep '+' only.

_MULTI_OPS = [
    "..=",
    "...",
    "..<",
    "..",
    "->",
    "=>",
    "===",
    "!==",
    "==",
    "!=",
    "<=",
    ">=",
    "&&",
    "||",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "&=",
    "|=",
    "^=",
    "<<",
    ">>",
    "::",
    "??",
    "?.",
]


def tokenize(text: str) -> list[str]:
    toks: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "\"'":
            tok, i = _read_string(text, i)
            toks.append(tok)
            continue
        if ch == "b" and i + 1 < n and text[i + 1] in "\"'":
            tok, i = _read_string(text, i + 1)
            toks.append("b" + tok)
            continue
        if ch == "r" and i + 1 < n and text[i + 1] in "\"'#":
            tok, i = _read_raw_string(text, i)
            toks.append(tok)
            continue
        if ch.isalpha() or ch == "_" or ch == "$":
            j = i + 1
            while j < n and (text[j].isalnum() or text[j] in "_$"):
                j += 1
            toks.append(text[i:j])
            i = j
            continue
        if ch.isdigit():
            j = i + 1
            while j < n and (text[j].isalnum() or text[j] == "_"):
                j += 1
            toks.append(text[i:j])
            i = j
            continue
        matched = False
        for op in _MULTI_OPS:
            if text.startswith(op, i):
                toks.append(op)
                i += len(op)
                matched = True
                break
        if matched:
            continue
        toks.append(ch)
        i += 1
    return toks


def _read_string(text: str, i: int) -> tuple[str, int]:
    quote = text[i]
    j = i + 1
    n = len(text)
    while j < n:
        if text[j] == "\\":
            j += 2
            continue
        if text[j] == quote:
            j += 1
            break
        j += 1
    return text[i:j], j


def _read_raw_string(text: str, i: int) -> tuple[str, int]:
    # r"..." or r#"..."# or r##"..."##
    j = i + 1
    hashes = 0
    while j < len(text) and text[j] == "#":
        hashes += 1
        j += 1
    if j >= len(text) or text[j] != '"':
        return text[i], i + 1
    j += 1
    close = '"' + "#" * hashes
    k = text.find(close, j)
    if k < 0:
        return text[i:], len(text)
    return text[i : k + len(close)], k + len(close)


def squeeze(text: str) -> str:
    toks = tokenize(text)
    if not toks:
        return ""
    out: list[str] = []
    for i, t in enumerate(toks):
        out.append(t)
        if i == len(toks) - 1:
            break
        if t in SPACE_AFTER:
            if t == "-" and toks[i + 1] and toks[i + 1][0].isdigit():
                out.append(" ")
            elif t != "-":
                out.append(" ")
        elif t in {"let", "var", "mut", "ref"}:
            out.append(" ")
    return "".join(out)


def strip_if_let(pred: str) -> str:
    """Keep `let`/`var` (v0.2). Only drop Swift `if case` noise."""
    p = pred.strip()
    if p.startswith("case "):
        return p[5:].lstrip()
    return p


def negate_brace(pred: str) -> str:
    p = squeeze(pred)
    if p.startswith("!") and not p.startswith("!="):
        return p[1:]
    if "!=" in p:
        return p.replace("!=", "==", 1)
    return f"¬({p})"


_CONTROL = re.compile(r"\b(if|else|match|for|while|guard|switch|try|catch|except)\b")
_EXIT = re.compile(r"\b(return|throw|continue|break|fatalError|preconditionFailure|panic!)\b")


def is_simple_exit_body(body: str) -> bool:
    if _CONTROL.search(body):
        return False
    return bool(_EXIT.search(body))


@dataclass
class _BFrame:
    kind: str
    pred: str
    line: int
    depth: int
    simple_exit: bool = False
    given_on_close: bool = False


@dataclass
class _LineEv:
    start: list[Frame] = field(default_factory=list)
    mid: list[Frame] = field(default_factory=list)
    end: list[Frame] = field(default_factory=list)
    converted: bool = False
    opened: bool = False
    closed_only: bool = False


def _public_frames(stack: list[_BFrame]) -> list[Frame]:
    return [Frame(f.kind, f.pred, f.line, 0) for f in stack]


class _BraceScanner:
    def __init__(self, source: str) -> None:
        self.source = source
        self.lines = source.splitlines()
        self.n = len(self.lines)
        self.stack: list[_BFrame] = []
        self.events: list[_LineEv] = [_LineEv() for _ in range(self.n + 1)]
        self.brace_depth = 0

    def run(self) -> None:
        masked = _mask(self.source)
        mlines = masked.splitlines()
        # pad
        while len(mlines) < self.n:
            mlines.append("")
        i = 0
        while i < self.n:
            start_stack = list(self.stack)
            converted = False
            opened = False
            line_no = i + 1
            raw = self.lines[i]
            masked_line = mlines[i]
            code = masked_line
            stripped = code.strip()

            # process leading closing braces first
            k = 0
            while k < len(code) and code[k].isspace():
                k += 1
            while k < len(code) and code[k] == "}":
                converted = self._close() or converted
                k += 1
                while k < len(code) and code[k].isspace():
                    k += 1

            rest = code[k:]
            rest_raw = raw[k:] if k <= len(raw) else ""

            # else if / else / elif
            if re.match(r"else\s+if\b", rest) or re.match(r"else\s+if\b", stripped):
                pred, consumed_brace = _cond_after_pair(rest_raw, rest, "else if")
                pred = squeeze(strip_if_let(pred))
                self._pop_just_made_given()
                self.stack.append(_BFrame("elif", pred, line_no, self.brace_depth, False))
                opened = True
                if consumed_brace:
                    self.brace_depth += 1
            elif re.match(r"else\b", rest):
                self._pop_just_made_given()
                self.stack.append(_BFrame("else", "", line_no, self.brace_depth, False))
                opened = True
                if "{" in rest:
                    self.brace_depth += 1
            elif re.match(r"guard\b", rest):
                pred, _ = _cond_between_pair(rest_raw, rest, "guard", "else")
                pred = squeeze(pred)
                parent = max(0, self.brace_depth - 1)
                self.stack.append(_BFrame("guard", pred, line_no, parent, False))
                self.stack.append(_BFrame("guard-else", pred, line_no, self.brace_depth, False))
                opened = True
                if "{" in rest:
                    self.brace_depth += 1
            elif re.match(r"if\b", rest):
                pred, consumed_brace = _cond_after_pair(rest_raw, rest, "if")
                pred_s = squeeze(strip_if_let(pred))
                body, end_line = _body_after_open(mlines, i, rest)
                simple = is_simple_exit_body(body) and not _followed_by_else(mlines, end_line)
                self.stack.append(
                    _BFrame("if", pred_s, line_no, self.brace_depth, simple_exit=simple)
                )
                opened = True
                if consumed_brace or "{" in rest:
                    self.brace_depth += 1
            elif re.match(r"(match|switch)\b", rest):
                kw = "match" if rest.lstrip().startswith("match") else "switch"
                pred, consumed_brace = _cond_after_pair(rest_raw, rest, kw)
                pred = squeeze(pred)
                self.stack.append(_BFrame(kw if kw == "match" else "switch", pred, line_no, self.brace_depth))
                opened = True
                if consumed_brace or "{" in rest:
                    self.brace_depth += 1
            elif re.match(r"while\b", rest):
                pred, consumed_brace = _cond_after_pair(rest_raw, rest, "while")
                pred = squeeze(strip_if_let(pred))
                self.stack.append(_BFrame("while", pred, line_no, self.brace_depth))
                opened = True
                if consumed_brace or "{" in rest:
                    self.brace_depth += 1
            elif re.match(r"for\b", rest):
                pred, consumed_brace = _cond_after_pair(rest_raw, rest, "for")
                pred = squeeze(pred)
                self.stack.append(_BFrame("for", pred, line_no, self.brace_depth))
                opened = True
                if consumed_brace or "{" in rest:
                    self.brace_depth += 1
            elif _is_fn_line(rest):
                pred = _fn_from_line(rest_raw if rest_raw.strip() else raw)
                # gather following signature lines if no '{' yet
                if "{" not in rest:
                    j = i + 1
                    acc = rest_raw
                    while j < self.n and "{" not in mlines[j]:
                        acc += " " + self.lines[j].strip()
                        j += 1
                    if j < self.n:
                        acc += " " + self.lines[j].strip()
                    pred = _fn_from_line(acc)
                self.stack.append(_BFrame("fn", squeeze(pred), line_no, self.brace_depth))
                opened = True
                if "{" in rest or any("{" in mlines[j] for j in range(i, min(i + 6, self.n))):
                    # depth increment when we see '{' on this or gathered lines
                    if "{" in rest:
                        self.brace_depth += 1
            elif re.match(r"case\b", rest):
                pred = rest.strip()
                if pred.startswith("case"):
                    pred = pred[4:].strip()
                pred = re.sub(r"[:{]\s*$", "", pred).strip()
                pred = " ".join(tokenize(pred))
                self.stack.append(_BFrame("case", pred, line_no, self.brace_depth))
                opened = True
                if "{" in rest:
                    self.brace_depth += 1
            elif "=>" in rest:
                # rust match arm — keep the pattern text (v0.2)
                left, _, right = rest.partition("=>")
                left_raw = rest_raw.partition("=>")[0] if "=>" in rest_raw else left
                left_s = left_raw.strip()
                m = re.search(r"\bif\b(.*)$", left_s)
                if m and "{" in right:
                    gpred = squeeze(m.group(1).strip()) + "=>"
                    self.stack.append(_BFrame("if", gpred, line_no, self.brace_depth))
                    opened = True
                    self.brace_depth += 1
                elif "{" in right:
                    arm_pred = squeeze(left_s)
                    self.stack.append(_BFrame("arm", arm_pred, line_no, self.brace_depth))
                    opened = True
                    self.brace_depth += 1

            after_open = list(self.stack)
            # remaining braces on the line (beyond the one we already counted)
            extra = rest
            if opened and "{" in extra:
                extra = extra.replace("{", "", 1)
            for ch in extra:
                if ch == "{":
                    self.brace_depth += 1
                elif ch == "}":
                    converted = self._close() or converted

            end_stack = list(self.stack)
            ev = self.events[line_no]
            ev.start = _public_frames(start_stack)
            ev.mid = _public_frames(after_open)
            ev.end = _public_frames(end_stack)
            ev.converted = converted
            ev.opened = opened
            ev.closed_only = (not opened) and (len(end_stack) < len(start_stack) or converted)
            i += 1

    def _close(self) -> bool:
        self.brace_depth = max(0, self.brace_depth - 1)
        converted = False
        while self.stack and self.stack[-1].depth >= self.brace_depth:
            top = self.stack.pop()
            if top.kind == "if" and top.simple_exit:
                # persist in the parent body, not at the just-closed depth
                parent = max(0, self.brace_depth - 1)
                self.stack.append(
                    _BFrame("given", negate_brace(top.pred), top.line, parent)
                )
                converted = True
            elif top.kind == "guard-else":
                pass
        return converted

    def _pop_just_made_given(self) -> None:
        if self.stack and self.stack[-1].kind == "given":
            self.stack.pop()


def _is_fn_line(rest: str) -> bool:
    s = rest.strip()
    if re.match(
        r"(pub(\s+\w+)*\s+)?(async\s+)?fn\b",
        s,
    ):
        return True
    if re.match(
        r"(public|private|internal|fileprivate|open|static|override|mutating|nonisolated)*\s*"
        r"(public|private|internal|fileprivate|open|static|override|mutating|func|fn)\b",
        s,
    ) and re.search(r"\b(func|fn)\b", s):
        return True
    if re.match(r"(export\s+)?(async\s+)?function\b", s):
        return True
    return False


def _fn_from_line(text: str) -> str:
    s = " ".join(text.split())
    m = re.search(r"\b(?:fn|func|function)\s+", s)
    if not m:
        return squeeze(s)
    rest = s[m.end() :]
    # drop leading visibility leftovers already skipped
    # cut at opening `{` if present
    if "{" in rest:
        rest = rest.split("{", 1)[0]
    rest = rest.strip()
    # drop trailing where-clauses lightly
    return rest


def _cond_after(rest: str, kw: str) -> tuple[str, bool]:
    return _cond_after_pair(rest, rest, kw)


def _cond_after_pair(raw_rest: str, masked_rest: str, kw: str) -> tuple[str, bool]:
    idx = masked_rest.find(kw)
    if idx < 0:
        return "", "{" in masked_rest
    tail_m = masked_rest[idx + len(kw) :]
    tail_r = raw_rest[idx + len(kw) :] if idx + len(kw) <= len(raw_rest) else tail_m
    depth = 0
    for i, ch in enumerate(tail_m):
        if ch == "{" and depth == 0:
            return tail_r[:i].strip(), True
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
    return tail_r.strip().rstrip("{").strip(), False


def _cond_between_pair(raw_rest: str, masked_rest: str, start_kw: str, end_kw: str) -> tuple[str, bool]:
    idx = masked_rest.find(start_kw)
    tail_m = masked_rest[idx + len(start_kw) :] if idx >= 0 else masked_rest
    tail_r = raw_rest[idx + len(start_kw) :] if idx >= 0 and idx + len(start_kw) <= len(raw_rest) else tail_m
    m = re.search(rf"\b{re.escape(end_kw)}\b", tail_m)
    if m:
        return tail_r[: m.start()].strip(), True
    cut = tail_m.find("{")
    if cut >= 0:
        return tail_r[:cut].strip(), True
    return tail_r.strip(), False


def _followed_by_else(mlines: list[str], end_line: int) -> bool:
    if end_line < 0 or end_line >= len(mlines):
        return False
    tail = mlines[end_line]
    # after the closing } on this line
    r = tail.rfind("}")
    after = tail[r + 1 :] if r >= 0 else tail
    if re.search(r"\belse\b", after):
        return True
    nxt = end_line + 1
    while nxt < len(mlines) and not mlines[nxt].strip():
        nxt += 1
    if nxt < len(mlines) and re.match(r"else\b", mlines[nxt].lstrip()):
        return True
    return False


def _cond_between(rest: str, start_kw: str, end_kw: str) -> tuple[str, bool]:
    idx = rest.find(start_kw)
    tail = rest[idx + len(start_kw) :] if idx >= 0 else rest
    m = re.search(rf"\b{end_kw}\b", tail)
    if m:
        return tail[: m.start()].strip(), True
    return tail.split("{", 1)[0].strip(), "{" in rest


def _body_after_open(mlines: list[str], start: int, rest: str) -> tuple[str, int]:
    if "{" not in rest:
        return "", start
    # collect until matching close
    depth = 0
    started = False
    chunks: list[str] = []
    for j in range(start, len(mlines)):
        line = mlines[j]
        for ch in line:
            if ch == "{":
                depth += 1
                started = True
                continue
            if ch == "}" and started:
                depth -= 1
                if depth == 0:
                    return "".join(chunks), j
                continue
            if started:
                chunks.append(ch)
        chunks.append("\n")
    return "".join(chunks), len(mlines) - 1


def _mask(source: str) -> str:
    """Replace comments and strings with spaces, keep newlines and braces outside them."""
    out: list[str] = []
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]
        # line comment
        if ch == "/" and i + 1 < n and source[i + 1] == "/":
            while i < n and source[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if ch == "#" and _looks_hash_comment(source, i):
            while i < n and source[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if ch == "/" and i + 1 < n and source[i + 1] == "*":
            out.append(" ")
            out.append(" ")
            i += 2
            while i < n - 1 and not (source[i] == "*" and source[i + 1] == "/"):
                out.append("\n" if source[i] == "\n" else " ")
                i += 1
            if i < n:
                out.append(" ")
                i += 1
            if i < n:
                out.append(" ")
                i += 1
            continue
        if ch in "\"'":
            tok, j = _read_string(source, i)
            out.append(" " * (j - i))
            # keep newlines if any (shouldn't be in normal strings)
            i = j
            continue
        if ch == "b" and i + 1 < n and source[i + 1] in "\"'":
            tok, j = _read_string(source, i + 1)
            out.append(" " * (j - i))
            i = j
            continue
        if ch == "`":
            j = i + 1
            while j < n and source[j] != "`":
                if source[j] == "\\":
                    j += 2
                    continue
                j += 1
            if j < n:
                j += 1
            out.append(" " * (j - i))
            i = j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _looks_hash_comment(source: str, i: int) -> bool:
    # rust attributes #[...] are not comments; python/shell # is.
    # brace languages: treat # as comment only in swift? Swift uses // .
    # Don't treat # as comment in rust/js/swift.
    return False


def _display_frames(ev: _LineEv) -> list[Frame]:
    if ev.converted and not ev.opened:
        return ev.end
    if ev.opened:
        return ev.mid or ev.end
    if ev.closed_only:
        return ev.start
    return ev.end if ev.end else ev.start


def query_braces(path: str, source: str, line: int) -> Locus:
    loc = Locus(file=path, line=line, engine="braces")
    lines = source.splitlines()
    if line < 1 or line > len(lines):
        loc.error = f"line {line} out of range 1..{len(lines)}"
        return loc
    sc = _BraceScanner(source)
    sc.run()
    ev = sc.events[line] if line < len(sc.events) else _LineEv()
    loc.here = lines[line - 1]
    loc.frames = _display_frames(ev)
    return loc.finalize()


def scan_braces(path: str, source: str, events_only: bool = True) -> list[Locus]:
    sc = _BraceScanner(source)
    sc.run()
    lines = source.splitlines()
    out: list[Locus] = []
    prev: list[Frame] | None = None
    for i, text in enumerate(lines, 1):
        ev = sc.events[i]
        frames = _display_frames(ev)
        if events_only:
            changed = ev.opened or ev.converted or ev.closed_only
            if not changed:
                # also emit when display stack kind-set changes vs previous emitted?
                if prev is not None and [ (f.kind, f.pred) for f in frames ] == [
                    (f.kind, f.pred) for f in prev
                ]:
                    continue
                if not ev.opened and not ev.converted:
                    continue
        loc = Locus(file=path, line=i, here=text, engine="braces", frames=frames)
        loc.finalize()
        out.append(loc)
        prev = frames
    return out
