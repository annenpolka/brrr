from __future__ import annotations

import re
from dataclasses import dataclass

from .model import Frame, Locus, collapse

# Keywords that introduce a brace-block we care about, plus function-like.
_FN_HEAD = re.compile(
    r"^\s*(?:"
    r"(?:pub(?:lic)?|private|internal|fileprivate|open|protected|static|async|unsafe|"
    r"virtual|override|export|default|mut|const|crate|extern|inline)\s+"
    r")*"
    r"(?:fn|func|function|def|method)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)

_TYPE_HEAD = re.compile(
    r"^\s*(?:"
    r"(?:pub(?:lic)?|private|internal|fileprivate|open|protected|static|export|default)\s+"
    r")*"
    r"(?P<kind>class|struct|enum|impl|protocol|extension|interface|trait|actor)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)

_CTRL = re.compile(
    r"(?P<kw>else\s+if|else if|elif|else|guard|if\s+let|if\s+var|while\s+let|"
    r"if|for|while|loop|match|switch|catch|except|finally|try|do)\b"
)


@dataclass
class _Tok:
    kind: str  # ident|kw|lbrace|rbrace|lparen|rparen|arrow|punct|nl
    value: str
    line: int
    col: int


def _strip_and_tokenize(source: str, rust: bool = False, swift: bool = False) -> list[_Tok]:
    """Character scan that skips comments/strings and emits coarse tokens."""
    toks: list[_Tok] = []
    n = len(source)
    i = 0
    line = 1
    col = 1

    def add(kind: str, value: str, at_line: int, at_col: int) -> None:
        toks.append(_Tok(kind, value, at_line, at_col))

    while i < n:
        ch = source[i]
        if ch == "\n":
            add("nl", "\n", line, col)
            i += 1
            line += 1
            col = 1
            continue
        if ch in " \t\r":
            i += 1
            col += 1
            continue
        # comments
        if ch == "/" and i + 1 < n:
            nxt = source[i + 1]
            if nxt == "/":
                while i < n and source[i] != "\n":
                    i += 1
                    col += 1
                continue
            if nxt == "*":
                i += 2
                col += 2
                while i + 1 < n and not (source[i] == "*" and source[i + 1] == "/"):
                    if source[i] == "\n":
                        line += 1
                        col = 1
                    else:
                        col += 1
                    i += 1
                i = min(i + 2, n)
                col += 2
                continue
        # python/shell hash comments if present
        if ch == "#":
            while i < n and source[i] != "\n":
                i += 1
                col += 1
            continue
        # strings — keep a shortened literal so predicates stay readable
        if ch in "\"'":
            quote = ch
            start_line, start_col = line, col
            i += 1
            col += 1
            buf = [quote]
            while i < n:
                if swift and source[i] == "\\" and i + 1 < n and source[i + 1] == "(":
                    buf.append("\\(")
                    i += 2
                    col += 2
                    depth = 1
                    while i < n and depth:
                        if source[i] == "(":
                            depth += 1
                        elif source[i] == ")":
                            depth -= 1
                        if source[i] == "\n":
                            line += 1
                            col = 1
                        else:
                            col += 1
                        buf.append(source[i])
                        i += 1
                    continue
                if source[i] == "\\" and i + 1 < n:
                    buf.append(source[i : i + 2])
                    if source[i + 1] == "\n":
                        line += 1
                        col = 1
                        i += 2
                        continue
                    i += 2
                    col += 2
                    continue
                if source[i] == "\n":
                    line += 1
                    col = 1
                    i += 1
                    break
                if source[i] == quote:
                    buf.append(quote)
                    i += 1
                    col += 1
                    break
                buf.append(source[i])
                i += 1
                col += 1
            lit = "".join(buf)
            add("string", collapse(lit, 48), start_line, start_col)
            continue
        # rust raw string r#"..."#
        if rust and ch == "r" and i + 1 < n and source[i + 1] in '#"':
            j = i + 1
            hashes = 0
            while j < n and source[j] == "#":
                hashes += 1
                j += 1
            if j < n and source[j] == '"':
                i = j + 1
                col += (j - i + 2 + hashes)  # rough
                close = '"' + ("#" * hashes)
                while i < n:
                    if source.startswith(close, i):
                        i += len(close)
                        break
                    if source[i] == "\n":
                        line += 1
                        col = 1
                    i += 1
                continue
        # swift multiline """
        if swift and source.startswith('"""', i):
            i += 3
            col += 3
            while i + 2 < n and source[i : i + 3] != '"""':
                if source[i] == "\n":
                    line += 1
                    col = 1
                i += 1
            i = min(i + 3, n)
            continue
        if ch == "{":
            add("lbrace", "{", line, col)
            i += 1
            col += 1
            continue
        if ch == "}":
            add("rbrace", "}", line, col)
            i += 1
            col += 1
            continue
        if ch == "(":
            add("lparen", "(", line, col)
            i += 1
            col += 1
            continue
        if ch == ")":
            add("rparen", ")", line, col)
            i += 1
            col += 1
            continue
        if ch == "=" and i + 1 < n and source[i + 1] == ">":
            add("arrow", "=>", line, col)
            i += 2
            col += 2
            continue
        if source.startswith("->", i):
            add("punct", "->", line, col)
            i += 2
            col += 2
            continue
        if ch.isalnum() or ch == "_" or ch == "$":
            j = i + 1
            while j < n and (source[j].isalnum() or source[j] in "_$"):
                j += 1
            word = source[i:j]
            add("ident", word, line, col)
            col += j - i
            i = j
            continue
        add("punct", ch, line, col)
        i += 1
        col += 1
    return toks


_CTRL_WORDS = {
    "if",
    "else",
    "elif",
    "for",
    "while",
    "loop",
    "match",
    "switch",
    "catch",
    "except",
    "finally",
    "try",
    "do",
    "guard",
    "case",
}

_FN_WORDS = {"fn", "func", "function"}
_TYPE_WORDS = {
    "class",
    "struct",
    "enum",
    "impl",
    "protocol",
    "extension",
    "interface",
    "trait",
    "actor",
}
_MODIFIERS = {
    "pub",
    "public",
    "private",
    "internal",
    "fileprivate",
    "open",
    "protected",
    "static",
    "async",
    "unsafe",
    "virtual",
    "override",
    "export",
    "default",
    "mut",
    "const",
    "crate",
    "extern",
    "inline",
    "final",
    "open",
    "required",
    "convenience",
    "override",
    "borrowing",
    "consuming",
}


_STOP_IDENTS = {
    "if",
    "elif",
    "for",
    "while",
    "loop",
    "match",
    "switch",
    "guard",
    "return",
    "throw",
    "let",
    "var",
    "const",
    "case",
    "default",
    "break",
    "continue",
}


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


def _neg_pred(pred: str) -> str:
    p = _unwrap_parens(pred)
    if p.startswith("!") and not p.startswith("!="):
        return _unwrap_parens(p[1:])
    if "!==" in p:
        return p.replace("!==", "===", 1)
    if "!=" in p:
        return p.replace("!=", "==", 1)
    return f"¬({p})"


def _pred_until_brace(toks: list[_Tok], start: int) -> tuple[str, int]:
    """Collect token text from start until a top-level `{`. Return (pred, index_of_lbrace or end)."""
    parts: list[str] = []
    depth_paren = 0
    i = start
    nls = 0
    while i < len(toks):
        t = toks[i]
        if t.kind == "lbrace" and depth_paren == 0:
            return collapse("".join(parts)), i
        if t.kind == "punct" and t.value == ";" and depth_paren == 0:
            return collapse("".join(parts)), i
        if (
            t.kind == "ident"
            and depth_paren == 0
            and t.value in _STOP_IDENTS
            and parts
        ):
            return collapse("".join(parts)), i
        if t.kind == "nl" and depth_paren == 0:
            nls += 1
            parts.append(" ")
            i += 1
            if nls >= 2:
                return collapse("".join(parts)), i
            continue
        nls = 0
        if t.kind == "lparen":
            depth_paren += 1
            parts.append("(")
        elif t.kind == "rparen":
            depth_paren = max(0, depth_paren - 1)
            parts.append(")")
        elif t.kind == "string":
            if parts and parts[-1] not in (" ", "(", "b", "r", "br", "#"):
                parts.append(" ")
            parts.append(t.value)
        elif t.kind == "ident":
            if parts and parts[-1] not in (" ", "(", ")", ".", ",", ":", "<", ">", "&", "|", "!"):
                parts.append(" ")
            parts.append(t.value)
        else:
            parts.append(t.value if t.value else "")
        i += 1
    return collapse("".join(parts)), i


def _next_is_else(toks: list[_Tok], i: int) -> bool:
    while i < len(toks) and toks[i].kind == "nl":
        i += 1
    return i < len(toks) and toks[i].kind == "ident" and toks[i].value == "else"


def _block_is_simple_exit(toks: list[_Tok], start: int, end: int) -> bool:
    """True if tokens inside a brace block look like a guard clause."""
    saw_exit = False
    saw_nested = False
    depth = 0
    for t in toks[start:end]:
        if t.kind == "lbrace":
            depth += 1
            continue
        if t.kind == "rbrace":
            depth = max(0, depth - 1)
            continue
        if depth > 0:
            continue
        if t.kind == "ident" and t.value in {
            "if",
            "for",
            "while",
            "match",
            "switch",
            "guard",
            "loop",
        }:
            saw_nested = True
        if t.kind == "ident" and t.value in {
            "return",
            "throw",
            "break",
            "continue",
            "fatalError",
            "preconditionFailure",
            "panic",
            "unreachable",
        }:
            saw_exit = True
    return saw_exit and not saw_nested


class BraceIndex:
    def __init__(self, source: str, filename: str = "<src>"):
        self.source = source
        self.filename = filename
        self.lines = source.splitlines()
        self.nlines = len(self.lines)
        self.stack_at: list[list[Frame]] = [[] for _ in range(self.nlines + 2)]
        self.after_at: list[list[str]] = [[] for _ in range(self.nlines + 2)]
        lower = filename.lower()
        rust = lower.endswith(".rs")
        swift = lower.endswith(".swift")
        toks = _strip_and_tokenize(source, rust=rust, swift=swift)
        self._parse(toks)

    def _snapshot(self, line: int, stack: list[Frame]) -> None:
        if 1 <= line <= self.nlines:
            # Keep the deepest stack seen on the line so `if x { y }`
            # attributes y to the if, not to the trailing close-brace.
            if len(stack) >= len(self.stack_at[line]):
                self.stack_at[line] = list(stack)

    def _parse(self, toks: list[_Tok]) -> None:
        stack: list[Frame] = []
        # brace depth at which each frame was opened
        opened_at: list[int] = []
        depth = 0
        i = 0
        last_line = 1
        pending: Frame | None = None
        pending_is_guard_else = False
        in_match_depth: list[int] = []  # brace depths of match/switch frames
        # token index of the `{` that opened each frame, for guard-clause detection
        block_open_at: list[int] = []

        def flush_line(upto: int) -> None:
            nonlocal last_line
            for ln in range(last_line, upto + 1):
                self._snapshot(ln, stack)
            last_line = max(last_line, upto)

        def push_frame(fr: Frame, at_depth: int, brace_tok: int) -> None:
            stack.append(fr)
            opened_at.append(at_depth)
            block_open_at.append(brace_tok)

        def pop_frame() -> Frame | None:
            if not stack:
                return None
            fr = stack.pop()
            opened_at.pop()
            if block_open_at:
                block_open_at.pop()
            if in_match_depth and in_match_depth[-1] > (opened_at[-1] if opened_at else -1):
                # cleaned below
                pass
            return fr

        while i < len(toks):
            t = toks[i]
            flush_line(t.line)

            # closing brace
            if t.kind == "rbrace":
                depth = max(0, depth - 1)
                while opened_at and opened_at[-1] > depth:
                    pop_frame()
                    if in_match_depth and in_match_depth[-1] > depth:
                        in_match_depth.pop()
                # pop frames opened at this exact depth too (the block we just closed)
                while opened_at and opened_at[-1] == depth and stack:
                    # keep guard/given: they persist until the enclosing block ends.
                    if stack[-1].kind in {"guard", "given"}:
                        break
                    closed = stack[-1]
                    open_i = block_open_at[-1] if block_open_at else i
                    if closed.kind in {"if", "elif"} and not _next_is_else(toks, i + 1):
                        if _block_is_simple_exit(toks, open_i + 1, i):
                            pred = closed.pred
                            pop_frame()
                            push_frame(
                                Frame("given", _neg_pred(pred) if pred else "¬", closed.line),
                                depth,
                                open_i,
                            )
                            break
                    pop_frame()
                    if in_match_depth and in_match_depth[-1] > depth:
                        in_match_depth.pop()
                i += 1
                continue

            # function / type / control
            if t.kind == "ident":
                # skip modifiers
                if t.value in _MODIFIERS:
                    i += 1
                    continue

                if t.value in _FN_WORDS and i + 1 < len(toks) and toks[i + 1].kind == "ident":
                    name_tok = toks[i + 1]
                    pred, j = _pred_until_brace(toks, i + 1)
                    if j < len(toks) and toks[j].kind == "lbrace":
                        pending = Frame("fn", pred or name_tok.value, name_tok.line)
                        i = j
                        continue
                    i += 1
                    continue

                if t.value in _TYPE_WORDS and i + 1 < len(toks) and toks[i + 1].kind == "ident":
                    kind = {
                        "class": "class",
                        "struct": "struct",
                        "enum": "enum",
                        "impl": "impl",
                        "protocol": "protocol",
                        "extension": "extension",
                        "interface": "class",
                        "trait": "impl",
                        "actor": "class",
                    }[t.value]
                    pred, j = _pred_until_brace(toks, i + 1)
                    if j < len(toks) and toks[j].kind == "lbrace":
                        pending = Frame(kind, pred, t.line)
                        i = j
                        continue
                    i += 1
                    continue

                # else if / else
                if t.value == "else":
                    # pop a just-closed if at this depth? the if frame should already
                    # have been popped with `}`. For `} else {` the if popped on `}`.
                    # We want else to replace if. If if is still on stack (braceless), pop it.
                    if stack and stack[-1].kind in {"if", "elif", "else"} and opened_at[-1] == depth:
                        pop_frame()
                    # look for `else if`
                    k = i + 1
                    while k < len(toks) and toks[k].kind == "nl":
                        k += 1
                    if k < len(toks) and toks[k].kind == "ident" and toks[k].value == "if":
                        pred, j = _pred_until_brace(toks, k + 1)
                        if j < len(toks) and toks[j].kind == "lbrace":
                            pending = Frame("elif", pred, t.line)
                            i = j
                            continue
                        i = k + 1
                        continue
                    pred, j = _pred_until_brace(toks, i + 1)
                    if j < len(toks) and toks[j].kind == "lbrace":
                        pending = Frame("else", pred, t.line)
                        i = j
                        continue
                    i += 1
                    continue

                if t.value == "guard":
                    pred, j = _pred_until_brace(toks, i + 1)
                    # pred includes "else"; strip trailing else
                    pred_clean = re.sub(r"\belse\b\s*$", "", pred).strip()
                    # push persistent guard frame now; its else-block is a nested frame
                    guard_frame = Frame("guard", pred_clean, t.line)
                    push_frame(guard_frame, depth, i)
                    pending = Frame("guard-else", pred_clean, t.line)
                    pending_is_guard_else = True
                    i = j if j < len(toks) and toks[j].kind == "lbrace" else i + 1
                    continue

                if t.value in {"if", "for", "while", "loop", "match", "switch", "catch", "except", "finally", "try", "do", "elif"}:
                    kw = t.value
                    start = i + 1
                    # if let / while let
                    if (
                        kw in {"if", "while"}
                        and i + 1 < len(toks)
                        and toks[i + 1].kind == "ident"
                        and toks[i + 1].value == "let"
                    ):
                        start = i + 2
                        kw = f"{kw} let"
                    pred, j = _pred_until_brace(toks, start)
                    kind = {
                        "if": "if",
                        "if let": "if",
                        "elif": "elif",
                        "for": "for",
                        "while": "while",
                        "while let": "while",
                        "loop": "while",
                        "match": "match",
                        "switch": "switch",
                        "catch": "catch",
                        "except": "except",
                        "finally": "finally",
                        "try": "try",
                        "do": "try",
                    }[kw]
                    if j < len(toks) and toks[j].kind == "lbrace":
                        pending = Frame(kind, pred, t.line)
                        i = j
                        continue
                    i += 1
                    continue

                # switch/match arm: `case X:` (swift/go/js)
                in_switch = any(fr.kind in {"match", "switch"} for fr in stack)
                if t.value == "case" and in_switch:
                    parts = []
                    k = i + 1
                    paren = 0
                    while k < len(toks):
                        tk = toks[k]
                        if tk.kind == "lparen":
                            paren += 1
                        elif tk.kind == "rparen":
                            paren = max(0, paren - 1)
                        if paren == 0 and tk.kind in {"lbrace", "arrow"}:
                            break
                        if paren == 0 and tk.value == ":":
                            break
                        if tk.kind != "nl":
                            parts.append(tk.value)
                        k += 1
                    pred = collapse(" ".join(parts))
                    while stack and stack[-1].kind in {"case", "arm"} and opened_at[-1] == depth:
                        pop_frame()
                    push_frame(Frame("case", pred, t.line), depth, i)
                    i = k
                    continue

                i += 1
                continue

            if t.kind == "arrow" and stack and stack[-1].kind in {"match", "switch", "arm", "case"}:
                # rust match arm `Pat =>`
                # find pattern by walking back — already on stack as match; push arm
                # previous idents between last lbrace/comma and here form pattern; we
                # approximate with pending or a generic arm.
                # pop previous arm
                while stack and stack[-1].kind in {"arm", "case"} and opened_at[-1] == depth:
                    pop_frame()
                pending = Frame("arm", "", t.line)
                i += 1
                continue

            if t.kind == "lbrace":
                if pending is not None:
                    push_frame(pending, depth, i)
                    if pending.kind in {"match", "switch"}:
                        in_match_depth.append(depth)
                    pending = None
                    pending_is_guard_else = False
                depth += 1
                i += 1
                continue

            i += 1

        flush_line(self.nlines)

        # Fill any leading lines
        for ln in range(1, self.nlines + 1):
            if not self.stack_at[ln]:
                # keep empty; already set
                pass

    def at(self, line: int) -> Locus:
        here = self.lines[line - 1] if 1 <= line <= self.nlines else ""
        if line < 1 or line > self.nlines:
            return Locus(
                file=self.filename,
                line=line,
                here=here,
                frames=[],
                engine="braces",
                error=f"line {line} out of range 1..{self.nlines}",
            )
        return Locus(
            file=self.filename,
            line=line,
            here=here.rstrip("\n"),
            frames=list(self.stack_at[line]),
            after=list(self.after_at[line]),
            engine="braces",
        )
