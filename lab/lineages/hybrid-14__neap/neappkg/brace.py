"""Brace-language path-condition tree. Nested-total early returns become given."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from .model import Frame, Locus, collapse


@dataclass
class Tok:
    kind: str
    value: str
    line: int
    start: int
    end: int


@dataclass
class Node:
    kind: str
    pred: str
    line: int
    start_line: int
    end_line: int
    kids: List["Node"] = field(default_factory=list)
    chain: List["Node"] = field(default_factory=list)
    head: str = ""


_FN_WORDS = {"fn", "func", "function"}
_BARE_FN = {"init", "deinit", "subscript", "constructor", "destructor"}
_VAR_WORDS = {"var", "let"}
_ACCESSORS = {"get", "set", "willSet", "didSet", "didChange"}
_TYPE_WORDS = {
    "class": "class",
    "struct": "struct",
    "enum": "enum",
    "impl": "impl",
    "protocol": "protocol",
    "extension": "extension",
    "interface": "class",
    "trait": "impl",
    "actor": "class",
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
    "required",
    "convenience",
    "borrowing",
    "consuming",
    "nonmutating",
    "mutating",
    "isolated",
    "nonisolated",
    "throws",
    "rethrows",
    "some",
    "any",
}
_EXIT_WORDS = {
    "return",
    "throw",
    "break",
    "continue",
    "fatalError",
    "preconditionFailure",
    "panic",
    "unreachable",
    "todo",
    "unimplemented",
}
_SKIP_FRAME = {"stmt", "body", "raw"}


def tokenize(source: str, filename: str = "") -> List[Tok]:
    lower = filename.lower()
    rust = lower.endswith(".rs")
    swift = lower.endswith(".swift")
    toks: List[Tok] = []
    n = len(source)
    i = 0
    line = 1

    def add(kind: str, start: int, end: int, value: Optional[str] = None) -> None:
        toks.append(Tok(kind, source[start:end] if value is None else value, line, start, end))

    while i < n:
        ch = source[i]
        if ch == "\n":
            add("nl", i, i + 1)
            i += 1
            line += 1
            continue
        if ch in " \t\r":
            i += 1
            continue
        if ch == "/" and i + 1 < n:
            nxt = source[i + 1]
            if nxt == "/":
                while i < n and source[i] != "\n":
                    i += 1
                continue
            if nxt == "*":
                i += 2
                while i + 1 < n and not (source[i] == "*" and source[i + 1] == "/"):
                    if source[i] == "\n":
                        line += 1
                    i += 1
                i = min(i + 2, n)
                continue
        if rust and ch == "b" and i + 1 < n and source[i + 1] in "\"'":
            # byte string: consume b + quoted payload as one string token
            start = i
            i += 1
            q = source[i]
            i += 1
            while i < n:
                if source[i] == "\\" and i + 1 < n:
                    i += 2
                    continue
                if source[i] == "\n":
                    break
                if source[i] == q:
                    i += 1
                    break
                i += 1
            add("string", start, i)
            continue
        if rust and ch == "r" and i + 1 < n and source[i + 1] in '#"':
            start = i
            j = i + 1
            hashes = 0
            while j < n and source[j] == "#":
                hashes += 1
                j += 1
            if j < n and source[j] == '"':
                i = j + 1
                close = '"' + ("#" * hashes)
                while i < n:
                    if source.startswith(close, i):
                        i += len(close)
                        break
                    if source[i] == "\n":
                        line += 1
                    i += 1
                add("string", start, i)
                continue
        if swift and source.startswith('"""', i):
            start = i
            i += 3
            while i + 2 < n and source[i : i + 3] != '"""':
                if source[i] == "\n":
                    line += 1
                i += 1
            i = min(i + 3, n)
            add("string", start, i)
            continue
        if ch in "\"'":
            if rust and ch == "'":
                # lifetime 'a / 'static, or char 'x'
                if i + 1 < n and (source[i + 1].isalpha() or source[i + 1] == "_"):
                    start = i
                    j = i + 1
                    while j < n and (source[j].isalnum() or source[j] == "_"):
                        j += 1
                    add("ident", start, j)
                    i = j
                    continue
            start = i
            quote = ch
            i += 1
            while i < n:
                if swift and source[i] == "\\" and i + 1 < n and source[i + 1] == "(":
                    i += 2
                    depth = 1
                    while i < n and depth:
                        if source[i] == "(":
                            depth += 1
                        elif source[i] == ")":
                            depth -= 1
                        if source[i] == "\n":
                            line += 1
                        i += 1
                    continue
                if source[i] == "\\" and i + 1 < n:
                    if source[i + 1] == "\n":
                        line += 1
                    i += 2
                    continue
                if source[i] == "\n":
                    break
                if source[i] == quote:
                    i += 1
                    break
                i += 1
            add("string", start, i)
            continue
        if ch == "{":
            add("lbrace", i, i + 1)
            i += 1
            continue
        if ch == "}":
            add("rbrace", i, i + 1)
            i += 1
            continue
        if ch == "(":
            add("lparen", i, i + 1)
            i += 1
            continue
        if ch == ")":
            add("rparen", i, i + 1)
            i += 1
            continue
        if ch == "[":
            add("lbrack", i, i + 1)
            i += 1
            continue
        if ch == "]":
            add("rbrack", i, i + 1)
            i += 1
            continue
        if source.startswith("=>", i):
            add("arrow", i, i + 2)
            i += 2
            continue
        if source.startswith("->", i) or source.startswith("::", i):
            add("punct", i, i + 2)
            i += 2
            continue
        if ch.isalnum() or ch == "_" or ch == "$":
            j = i + 1
            while j < n and (source[j].isalnum() or source[j] in "_$"):
                j += 1
            add("ident", i, j)
            i = j
            continue
        add("punct", i, i + 1)
        i += 1
    return toks


def _skip_nl(toks: Sequence[Tok], i: int, end: int) -> int:
    while i < end and toks[i].kind == "nl":
        i += 1
    return i


def _match_rbrace(toks: Sequence[Tok], lbrace: int, end: int) -> Optional[int]:
    depth = 0
    for j in range(lbrace, end):
        if toks[j].kind == "lbrace":
            depth += 1
        elif toks[j].kind == "rbrace":
            depth -= 1
            if depth == 0:
                return j
    return None


def _find_lbrace(toks: Sequence[Tok], start: int, end: int) -> Optional[int]:
    depth_p = 0
    depth_b = 0
    i = start
    nls = 0
    while i < end:
        t = toks[i]
        if t.kind == "lparen":
            depth_p += 1
        elif t.kind == "rparen":
            depth_p = max(0, depth_p - 1)
        elif t.kind == "lbrack":
            depth_b += 1
        elif t.kind == "rbrack":
            depth_b = max(0, depth_b - 1)
        elif t.kind == "lbrace" and depth_p == 0 and depth_b == 0:
            return i
        elif t.kind == "punct" and t.value == ";" and depth_p == 0 and depth_b == 0:
            return None
        elif t.kind == "nl" and depth_p == 0 and depth_b == 0:
            nls += 1
            if nls >= 3:
                return None
        else:
            nls = 0
        i += 1
    return None


def _src(source: str, toks: Sequence[Tok], a: int, b: int) -> str:
    if a >= b or a >= len(toks):
        return ""
    end = toks[b - 1].end if b - 1 < len(toks) else toks[a].end
    return collapse(source[toks[a].start : end])


def _pred_to_brace(source: str, toks: Sequence[Tok], start: int, lbrace: int) -> str:
    if start >= lbrace:
        return ""
    return collapse(source[toks[start].start : toks[lbrace].start])


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


def negate_pred(pred: str) -> str:
    p = _unwrap_parens(pred)
    if p.startswith("!") and not p.startswith("!="):
        return _unwrap_parens(p[1:].strip())
    if "!==" in p:
        return p.replace("!==", "===", 1)
    if "!=" in p:
        return p.replace("!=", "==", 1)
    return "¬({})".format(p)


def _first_ident(toks: Sequence[Tok], i: int, end: int) -> str:
    j = _skip_nl(toks, i, end)
    while j < end:
        if toks[j].kind == "ident":
            return toks[j].value
        if toks[j].kind not in {"nl", "punct"}:
            break
        j += 1
    return ""


def _skip_attrs_and_mods(toks: Sequence[Tok], i: int, end: int) -> int:
    while i < end:
        if toks[i].kind == "nl":
            i += 1
            continue
        t = toks[i]
        if t.kind == "ident" and t.value in _MODIFIERS:
            i += 1
            if i < end and toks[i].kind == "lparen":
                depth = 1
                i += 1
                while i < end and depth:
                    if toks[i].kind == "lparen":
                        depth += 1
                    elif toks[i].kind == "rparen":
                        depth -= 1
                    i += 1
            continue
        if t.kind == "punct" and t.value == "@":
            i += 1
            if i < end and toks[i].kind == "ident":
                i += 1
            if i < end and toks[i].kind == "lparen":
                depth = 1
                i += 1
                while i < end and depth:
                    if toks[i].kind == "lparen":
                        depth += 1
                    elif toks[i].kind == "rparen":
                        depth -= 1
                    i += 1
            continue
        if t.kind == "punct" and t.value == "#" and i + 1 < end and toks[i + 1].kind == "lbrack":
            depth = 1
            i += 2
            while i < end and depth:
                if toks[i].kind == "lbrack":
                    depth += 1
                elif toks[i].kind == "rbrack":
                    depth -= 1
                i += 1
            continue
        break
    return i


def _stmt_end(toks: Sequence[Tok], i: int, end: int) -> int:
    """Index after the current top-level statement (brace-aware)."""
    i = _skip_nl(toks, i, end)
    if i >= end:
        return end
    rel_b = 0
    rel_p = 0
    rel_k = 0
    saw_brace = False
    j = i
    while j < end:
        t = toks[j]
        if t.kind == "lparen":
            rel_p += 1
        elif t.kind == "rparen":
            rel_p = max(0, rel_p - 1)
        elif t.kind == "lbrack":
            rel_k += 1
        elif t.kind == "rbrack":
            rel_k = max(0, rel_k - 1)
        elif t.kind == "lbrace":
            rel_b += 1
            saw_brace = True
        elif t.kind == "rbrace":
            rel_b -= 1
            if rel_b == 0 and saw_brace:
                j += 1
                k = _skip_nl(toks, j, end)
                if k < end and toks[k].kind == "ident" and toks[k].value == "else":
                    j = k + 1
                    saw_brace = False
                    continue
                return j
            if rel_b < 0:
                return j
        elif rel_b == 0 and rel_p == 0 and rel_k == 0 and t.kind == "punct" and t.value == ";":
            return j + 1
        elif (
            rel_b == 0
            and rel_p == 0
            and rel_k == 0
            and t.kind == "nl"
            and not saw_brace
            and j > i
        ):
            k = _skip_nl(toks, j + 1, end)
            if k < end and toks[k].kind == "lbrace":
                j += 1
                continue
            if k < end and toks[k].kind == "ident" and toks[k].value in {"else", "where", "throws", "rethrows"}:
                j += 1
                continue
            if k < end and toks[k].kind == "punct" and toks[k].value in {".", ",", "?", ":"}:
                j += 1
                continue
            return j
        j += 1
    return end


def _node_span(toks: Sequence[Tok], a: int, b: int) -> Tuple[int, int, int]:
    a = min(a, len(toks) - 1) if toks else 0
    if a < 0 or not toks:
        return 1, 1, 1
    b2 = max(a + 1, min(b, len(toks)))
    start_line = toks[a].line
    end_line = toks[b2 - 1].line
    return start_line, end_line, start_line


def node_exits(n: Node) -> bool:
    if n.kind == "given":
        return block_exits(n.kids)
    if n.kind == "stmt":
        return n.head in _EXIT_WORDS
    if n.kind == "if":
        branches = [n] + n.chain
        if not any(b.kind == "else" for b in n.chain):
            return False
        return all(block_exits(b.kids) for b in branches)
    if n.kind in {"match", "switch"}:
        cases = [k for k in n.kids if k.kind in {"case", "arm"}]
        if not cases:
            return False
        return all(block_exits(c.kids) for c in cases)
    return False


def block_exits(kids: List[Node]) -> bool:
    if not kids:
        return False
    last = kids[-1]
    if last.kind == "given":
        return block_exits(last.kids)
    if last.kind == "guard":
        return block_exits(last.kids)
    return node_exits(last)


def is_bare_total_if(n: Node) -> bool:
    if n.kind != "if":
        return False
    if n.chain:
        return False
    return block_exits(n.kids)


def attach_givens(nodes: List[Node]) -> List[Node]:
    out: List[Node] = []
    i = 0
    while i < len(nodes):
        n = nodes[i]
        if is_bare_total_if(n):
            out.append(n)
            rest = nodes[i + 1 :]
            if rest:
                g = Node(
                    kind="given",
                    pred=negate_pred(n.pred),
                    line=n.line,
                    start_line=rest[0].start_line,
                    end_line=rest[-1].end_line,
                    kids=attach_givens(rest),
                )
                out.append(g)
            break
        if n.kind == "guard-else":
            out.append(n)
            rest = nodes[i + 1 :]
            if rest:
                g = Node(
                    kind="guard",
                    pred=n.pred,
                    line=n.line,
                    start_line=rest[0].start_line,
                    end_line=rest[-1].end_line,
                    kids=attach_givens(rest),
                )
                out.append(g)
            break
        out.append(n)
        i += 1
    return out


class _Ctx:
    def __init__(self, source: str, toks: List[Tok]):
        self.source = source
        self.toks = toks


def _plain_stmt(ctx: _Ctx, i: int, j: int) -> Node:
    sl, el, ln = _node_span(ctx.toks, i, j)
    head = _first_ident(ctx.toks, i, j)
    return Node(kind="stmt", pred="", line=ln, start_line=sl, end_line=el, head=head)


def _parse_body(ctx: _Ctx, inner_l: int, inner_r: int, in_match: bool) -> List[Node]:
    return parse_stmts(ctx, inner_l + 1, inner_r, in_match=in_match)


def parse_stmts(ctx: _Ctx, start: int, end: int, in_match: bool = False) -> List[Node]:
    toks = ctx.toks
    nodes: List[Node] = []
    i = start
    while i < end:
        i = _skip_nl(toks, i, end)
        if i >= end:
            break
        if toks[i].kind == "rbrace":
            break
        if in_match and _is_case_start(toks, i, end):
            node, i = parse_case(ctx, i, end)
            nodes.append(node)
            continue
        node, i = parse_stmt(ctx, i, end)
        if node is not None:
            nodes.append(node)
    return attach_givens(nodes)


def _is_case_start(toks: Sequence[Tok], i: int, end: int) -> bool:
    if i < end and toks[i].kind == "ident" and toks[i].value in {"case", "default"}:
        return True
    # rust arm: look for => before a top-level brace/comma at this stmt
    j = i
    depth_p = 0
    while j < end:
        t = toks[j]
        if t.kind == "lparen":
            depth_p += 1
        elif t.kind == "rparen":
            depth_p = max(0, depth_p - 1)
        elif t.kind == "arrow" and depth_p == 0:
            return True
        elif t.kind in {"lbrace", "rbrace"} and depth_p == 0:
            return False
        elif t.kind == "ident" and t.value in {"case", "default"} and j != i:
            return False
        j += 1
    return False


def parse_case(ctx: _Ctx, i: int, end: int) -> Tuple[Node, int]:
    toks = ctx.toks
    if toks[i].kind == "ident" and toks[i].value in {"case", "default"}:
        # Swift / C-family
        k = i + 1
        depth_p = 0
        while k < end:
            t = toks[k]
            if t.kind == "lparen":
                depth_p += 1
            elif t.kind == "rparen":
                depth_p = max(0, depth_p - 1)
            elif t.kind == "punct" and t.value == ":" and depth_p == 0:
                break
            elif t.kind == "lbrace" and depth_p == 0:
                break
            k += 1
        pred = _src(ctx.source, toks, i + 1, k)
        if k < end and toks[k].kind == "punct" and toks[k].value == ":":
            body_i = k + 1
        elif k < end and toks[k].kind == "lbrace":
            rb = _match_rbrace(toks, k, end)
            if rb is None:
                sl, el, ln = _node_span(toks, i, end)
                return Node("case", pred, ln, sl, el), end
            kids = _parse_body(ctx, k, rb, False)
            sl, el, ln = _node_span(toks, i, rb + 1)
            return Node("case", pred, toks[i].line, sl, el, kids=kids), rb + 1
        else:
            body_i = k
        body_end = _case_body_end(toks, body_i, end)
        kids = parse_stmts(ctx, body_i, body_end, in_match=False)
        sl, el, ln = _node_span(toks, i, body_end)
        return Node("case", pred, toks[i].line, sl, el, kids=kids), body_end

    # Rust arm: pattern => body
    k = i
    depth_p = 0
    while k < end and not (toks[k].kind == "arrow" and depth_p == 0):
        if toks[k].kind == "lparen":
            depth_p += 1
        elif toks[k].kind == "rparen":
            depth_p = max(0, depth_p - 1)
        elif toks[k].kind == "rbrace" and depth_p == 0:
            break
        k += 1
    pred = _src(ctx.source, toks, i, k)
    if k < end and toks[k].kind == "arrow":
        k += 1
    k = _skip_nl(toks, k, end)
    if k < end and toks[k].kind == "lbrace":
        rb = _match_rbrace(toks, k, end)
        if rb is None:
            sl, el, ln = _node_span(toks, i, end)
            return Node("arm", pred, ln, sl, el), end
        kids = _parse_body(ctx, k, rb, False)
        sl, el, ln = _node_span(toks, i, rb + 1)
        return Node("arm", pred, toks[i].line, sl, el, kids=kids), rb + 1
    body_end = _case_body_end(toks, k, end)
    kids = parse_stmts(ctx, k, body_end, in_match=False)
    sl, el, ln = _node_span(toks, i, body_end)
    return Node("arm", pred, toks[i].line, sl, el, kids=kids), body_end


def _case_body_end(toks: Sequence[Tok], i: int, end: int) -> int:
    depth_b = 0
    depth_p = 0
    j = i
    while j < end:
        t = toks[j]
        if t.kind == "lbrace":
            depth_b += 1
        elif t.kind == "rbrace":
            if depth_b == 0:
                return j
            depth_b -= 1
        elif t.kind == "lparen":
            depth_p += 1
        elif t.kind == "rparen":
            depth_p = max(0, depth_p - 1)
        elif depth_b == 0 and depth_p == 0:
            if t.kind == "ident" and t.value in {"case", "default"} and j != i:
                return j
            if t.kind == "arrow":
                # next arm's arrow — walk back? rust arms without case keyword
                # body ended at previous comma; if we see arrow here we're in the next arm
                if j != i:
                    # find start of this arm: too late. comma-separated handled below
                    pass
            if t.kind == "punct" and t.value == "," and depth_b == 0:
                return j + 1
        j += 1
    return end


def parse_stmt(ctx: _Ctx, i: int, end: int) -> Tuple[Optional[Node], int]:
    toks = ctx.toks
    i0 = _skip_nl(toks, i, end)
    if i0 >= end:
        return None, end
    j = _stmt_end(toks, i0, end)
    if j <= i0:
        j = min(end, i0 + 1)
    k = _skip_attrs_and_mods(toks, i0, j)
    if k >= j:
        return _plain_stmt(ctx, i0, j), j
    t = toks[k]
    if t.kind != "ident":
        return _plain_stmt(ctx, i0, j), j

    if t.value in _FN_WORDS or t.value in _BARE_FN:
        return _parse_fn(ctx, i0, k, j), j
    if t.value in _TYPE_WORDS:
        return _parse_type(ctx, i0, k, j), j
    if t.value in _VAR_WORDS:
        node = _parse_var(ctx, i0, k, j)
        if node is not None:
            return node, j
        return _plain_stmt(ctx, i0, j), j
    if t.value in _ACCESSORS:
        return _parse_block_kw(ctx, i0, k, j)
    if t.value == "if":
        return _parse_if(ctx, i0, k, j, end)
    if t.value == "guard":
        return _parse_guard(ctx, i0, k, j)
    if t.value in {"match", "switch"}:
        return _parse_match(ctx, i0, k, j)
    if t.value in {"for", "while", "loop", "try", "do", "catch", "except", "finally", "with"}:
        return _parse_block_kw(ctx, i0, k, j)
    return _plain_stmt(ctx, i0, j), j


def _is_computed_var(toks: Sequence[Tok], k: int, j: int) -> bool:
    """True for `var name: T { … }`, false for `var name = …` stored props."""
    depth_p = 0
    depth_k = 0
    i = k + 1
    while i < j:
        t = toks[i]
        if t.kind == "lparen":
            depth_p += 1
        elif t.kind == "rparen":
            depth_p = max(0, depth_p - 1)
        elif t.kind == "lbrack":
            depth_k += 1
        elif t.kind == "rbrack":
            depth_k = max(0, depth_k - 1)
        elif depth_p == 0 and depth_k == 0 and t.kind == "punct" and t.value == "=":
            return False
        elif depth_p == 0 and depth_k == 0 and t.kind == "lbrace":
            return True
        i += 1
    return False


def _parse_var(ctx: _Ctx, i0: int, k: int, j: int) -> Optional[Node]:
    """Swift/C# computed property. Kind is fn so cond identity skips the name."""
    toks = ctx.toks
    if not _is_computed_var(toks, k, j):
        return None
    lb = _find_lbrace(toks, k + 1, j)
    if lb is None:
        return None
    rb = _match_rbrace(toks, lb, j)
    if rb is None:
        rb = j - 1 if j > lb else lb
    pred = _pred_to_brace(ctx.source, toks, k + 1, lb)
    kids = _parse_body(ctx, lb, rb, False)
    sl, el, _ = _node_span(toks, i0, rb + 1)
    return Node("fn", pred, toks[k].line, sl, el, kids=kids)


def _parse_fn(ctx: _Ctx, i0: int, k: int, j: int) -> Node:
    toks = ctx.toks
    name_i = k
    if toks[k].value in _FN_WORDS:
        name_i = k + 1 if k + 1 < j else k
    lb = _find_lbrace(toks, k, j)
    if lb is None:
        return _plain_stmt(ctx, i0, j)
    rb = _match_rbrace(toks, lb, j)
    if rb is None:
        rb = j - 1 if j > lb else lb
    pred = _pred_to_brace(ctx.source, toks, name_i, lb)
    kids = _parse_body(ctx, lb, rb, False)
    sl, el, _ = _node_span(toks, i0, rb + 1)
    return Node("fn", pred, toks[name_i].line, sl, el, kids=kids)


def _parse_type(ctx: _Ctx, i0: int, k: int, j: int) -> Node:
    toks = ctx.toks
    kind = _TYPE_WORDS[toks[k].value]
    name_i = k + 1 if k + 1 < j else k
    lb = _find_lbrace(toks, k, j)
    if lb is None:
        return _plain_stmt(ctx, i0, j)
    rb = _match_rbrace(toks, lb, j) or (j - 1)
    pred = _pred_to_brace(ctx.source, toks, name_i, lb)
    kids = _parse_body(ctx, lb, rb, False)
    sl, el, _ = _node_span(toks, i0, rb + 1)
    return Node(kind, pred, toks[k].line, sl, el, kids=kids)


def _parse_if(ctx: _Ctx, i0: int, k: int, j: int, end: int) -> Tuple[Node, int]:
    toks = ctx.toks
    # keep `let` in if let / while let
    pred_start = k + 1
    lb = _find_lbrace(toks, pred_start, j)
    if lb is None:
        return _plain_stmt(ctx, i0, j), j
    rb = _match_rbrace(toks, lb, j)
    if rb is None:
        return _plain_stmt(ctx, i0, j), j
    pred = _pred_to_brace(ctx.source, toks, pred_start, lb)
    kids = _parse_body(ctx, lb, rb, False)
    sl, el, _ = _node_span(toks, i0, rb + 1)
    node = Node("if", pred, toks[k].line, sl, el, kids=kids)
    # else / else if are included in stmt_end via else-continuation; parse chain from rb
    tpos = _skip_nl(toks, rb + 1, j)
    while tpos < j and toks[tpos].kind == "ident" and toks[tpos].value == "else":
        e_line = toks[tpos].line
        npos = _skip_nl(toks, tpos + 1, j)
        if npos < j and toks[npos].kind == "ident" and toks[npos].value == "if":
            pred_s = npos + 1
            lb2 = _find_lbrace(toks, pred_s, j)
            if lb2 is None:
                break
            rb2 = _match_rbrace(toks, lb2, j)
            if rb2 is None:
                break
            ep = _pred_to_brace(ctx.source, toks, pred_s, lb2)
            ekids = _parse_body(ctx, lb2, rb2, False)
            sl2, el2, _ = _node_span(toks, tpos, rb2 + 1)
            node.chain.append(Node("elif", ep, e_line, sl2, el2, kids=ekids))
            node.end_line = el2
            tpos = _skip_nl(toks, rb2 + 1, j)
            continue
        lb2 = _find_lbrace(toks, npos, j)
        if lb2 is None:
            break
        rb2 = _match_rbrace(toks, lb2, j)
        if rb2 is None:
            break
        ekids = _parse_body(ctx, lb2, rb2, False)
        sl2, el2, _ = _node_span(toks, tpos, rb2 + 1)
        node.chain.append(Node("else", node.pred, e_line, sl2, el2, kids=ekids))
        node.end_line = el2
        tpos = rb2 + 1
        break
    return node, j


def _parse_guard(ctx: _Ctx, i0: int, k: int, j: int) -> Tuple[Node, int]:
    toks = ctx.toks
    # guard P else { ... }
    pred_src = _src(ctx.source, toks, k + 1, j)
    pred_src = collapse(pred_src)
    if pred_src.endswith("else"):
        pred_src = pred_src[: -len("else")].strip()
    else:
        # split at last else ident
        lb = _find_lbrace(toks, k + 1, j)
        else_i = k + 1
        found_else = None
        while else_i < (lb if lb is not None else j):
            if toks[else_i].kind == "ident" and toks[else_i].value == "else":
                found_else = else_i
            else_i += 1
        if found_else is not None:
            pred_src = _src(ctx.source, toks, k + 1, found_else)
    lb = _find_lbrace(toks, k + 1, j)
    kids: List[Node] = []
    end_line = toks[i0].line
    if lb is not None:
        rb = _match_rbrace(toks, lb, j)
        if rb is not None:
            kids = _parse_body(ctx, lb, rb, False)
            end_line = toks[rb].line
    sl, _, _ = _node_span(toks, i0, j)
    node = Node("guard-else", pred_src, toks[k].line, sl, end_line, kids=kids)
    return node, j


def _parse_match(ctx: _Ctx, i0: int, k: int, j: int) -> Tuple[Node, int]:
    toks = ctx.toks
    kind = "match" if toks[k].value == "match" else "switch"
    lb = _find_lbrace(toks, k + 1, j)
    if lb is None:
        return _plain_stmt(ctx, i0, j), j
    rb = _match_rbrace(toks, lb, j)
    if rb is None:
        return _plain_stmt(ctx, i0, j), j
    pred = _pred_to_brace(ctx.source, toks, k + 1, lb)
    kids = parse_stmts(ctx, lb + 1, rb, in_match=True)
    sl, el, _ = _node_span(toks, i0, rb + 1)
    return Node(kind, pred, toks[k].line, sl, el, kids=kids), j


def _parse_block_kw(ctx: _Ctx, i0: int, k: int, j: int) -> Tuple[Node, int]:
    toks = ctx.toks
    raw = toks[k].value
    kind_map = {
        "for": "for",
        "while": "while",
        "loop": "while",
        "try": "try",
        "do": "try",
        "catch": "catch",
        "except": "except",
        "finally": "finally",
        "with": "with",
        "get": "fn",
        "set": "fn",
        "willSet": "fn",
        "didSet": "fn",
        "didChange": "fn",
    }
    kind = kind_map.get(raw, raw)
    lb = _find_lbrace(toks, k + 1, j)
    if lb is None:
        return _plain_stmt(ctx, i0, j), j
    rb = _match_rbrace(toks, lb, j)
    if rb is None:
        return _plain_stmt(ctx, i0, j), j
    pred = _pred_to_brace(ctx.source, toks, k + 1, lb)
    kids = _parse_body(ctx, lb, rb, False)
    sl, el, _ = _node_span(toks, i0, rb + 1)
    return Node(kind, pred, toks[k].line, sl, el, kids=kids), j


def paint(nodes: List[Node], inherited: List[Frame], stack_at: List[List[Frame]]) -> None:
    nlines = len(stack_at) - 2
    for node in nodes:
        if node.kind in _SKIP_FRAME:
            frames = inherited
        else:
            fr = Frame(node.kind, node.pred, node.line, node.end_line)
            frames = inherited + [fr]
        for ln in range(max(1, node.start_line), min(nlines, node.end_line) + 1):
            if len(frames) >= len(stack_at[ln]):
                stack_at[ln] = frames
        paint(node.kids, frames, stack_at)
        # elif/else replace the if frame rather than nest under it
        paint(node.chain, inherited, stack_at)


class BraceIndex:
    def __init__(self, source: str, filename: str = "<src>"):
        self.source = source
        self.filename = filename
        self.lines = source.splitlines()
        self.nlines = len(self.lines)
        self.stack_at: List[List[Frame]] = [[] for _ in range(self.nlines + 2)]
        toks = tokenize(source, filename)
        ctx = _Ctx(source, toks)
        roots = parse_stmts(ctx, 0, len(toks), in_match=False)
        paint(roots, [], self.stack_at)
        # lines with no tokens still inherit nearest painted prefix via empty default

    def at(self, line: int) -> Locus:
        here = self.lines[line - 1] if 1 <= line <= self.nlines else ""
        if line < 1 or line > self.nlines:
            return Locus(
                file=self.filename,
                line=line,
                here=here,
                frames=[],
                engine="braces",
                error="line {} out of range 1..{}".format(line, self.nlines),
                placed=False,
            )
        return Locus(
            file=self.filename,
            line=line,
            here=here.rstrip("\n"),
            frames=list(self.stack_at[line]),
            engine="braces",
        )
