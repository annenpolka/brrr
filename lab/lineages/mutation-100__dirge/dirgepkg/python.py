"""Python-ast path-condition tree. Early-return ifs become given on later siblings."""

from __future__ import annotations

import ast
from typing import List, Optional, Union

from .brace import Node, paint
from .model import Frame, Locus, collapse


def _unparse(node: ast.AST) -> str:
    try:
        return collapse(ast.unparse(node))
    except Exception:
        return type(node).__name__


def _end(node: ast.AST) -> int:
    return int(getattr(node, "end_lineno", None) or getattr(node, "lineno", 0) or 0)


def _lineno(node: ast.AST) -> int:
    return int(getattr(node, "lineno", None) or 1)


Match = getattr(ast, "Match", ())
TryStar = getattr(ast, "TryStar", ())


def _is_exiting_stmts(stmts: List[ast.stmt]) -> bool:
    if not stmts:
        return False
    return _is_exiting_stmt(stmts[-1])


def _is_exiting_stmt(stmt: ast.stmt) -> bool:
    if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
        return True
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        name = ""
        fn = stmt.value.func
        if isinstance(fn, ast.Name):
            name = fn.id
        elif isinstance(fn, ast.Attribute):
            name = fn.attr
        if name in {"exit", "abort", "fatal", "panic", "sys.exit"}:
            return True
    if isinstance(stmt, ast.If):
        return (
            _is_exiting_stmts(stmt.body)
            and bool(stmt.orelse)
            and _is_exiting_stmts(stmt.orelse)
        )
    if Match and isinstance(stmt, Match):
        return bool(stmt.cases) and all(_is_exiting_stmts(c.body) for c in stmt.cases)
    if isinstance(stmt, ast.Try) or (TryStar and isinstance(stmt, TryStar)):
        if not _is_exiting_stmts(stmt.body):
            return False
        if not all(_is_exiting_stmts(h.body) for h in stmt.handlers):
            return False
        if stmt.orelse and not _is_exiting_stmts(stmt.orelse):
            return False
        return True
    if isinstance(stmt, (ast.With, ast.AsyncWith)):
        return _is_exiting_stmts(stmt.body)
    return False


def _negate_test(node: ast.AST) -> str:
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return _unparse(node.operand)
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        flip = {
            ast.Is: ast.IsNot(),
            ast.IsNot: ast.Is(),
            ast.Eq: ast.NotEq(),
            ast.NotEq: ast.Eq(),
            ast.In: ast.NotIn(),
            ast.NotIn: ast.In(),
            ast.Lt: ast.GtE(),
            ast.GtE: ast.Lt(),
            ast.Gt: ast.LtE(),
            ast.LtE: ast.Gt(),
        }
        new_op = flip.get(type(node.ops[0]))
        if new_op is not None:
            flipped = ast.Compare(left=node.left, ops=[new_op], comparators=node.comparators)
            ast.copy_location(flipped, node)
            return _unparse(flipped)
    text = _unparse(node)
    if text.startswith("not "):
        return text[4:]
    return "¬({})".format(text)


def _sig(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    args: List[str] = []
    a = node.args
    posonly = list(getattr(a, "posonlyargs", []) or [])
    npos = len(posonly)
    for i, arg in enumerate(posonly):
        args.append(arg.arg)
        if i == npos - 1:
            args.append("/")
    for arg in a.args:
        args.append(arg.arg)
    if a.vararg:
        args.append("*" + a.vararg.arg)
    elif a.kwonlyargs:
        args.append("*")
    for arg in a.kwonlyargs:
        args.append(arg.arg)
    if a.kwarg:
        args.append("**" + a.kwarg.arg)
    return "{}{}({})".format(prefix, node.name, ", ".join(args))


def _conv_stmts(stmts: List[ast.stmt]) -> List[Node]:
    raw = [_conv_stmt(s) for s in stmts]
    # Python fallthrough: only wrap rest when a *bare* if (no orelse) exits.
    out: List[Node] = []
    i = 0
    while i < len(raw):
        n = raw[i]
        stmt = stmts[i]
        out.append(n)
        if isinstance(stmt, ast.If) and not stmt.orelse and _is_exiting_stmts(stmt.body):
            rest_n = raw[i + 1 :]
            if rest_n:
                g = Node(
                    kind="given",
                    pred=_negate_test(stmt.test),
                    line=_lineno(stmt),
                    start_line=rest_n[0].start_line,
                    end_line=rest_n[-1].end_line,
                    kids=_conv_stmts(stmts[i + 1 :]),
                )
                out.append(g)
            break
        i += 1
    return out


def _conv_stmt(stmt: ast.stmt) -> Node:
    if isinstance(stmt, ast.If):
        return _conv_if(stmt, False)
    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
        sl, el = _lineno(stmt), _end(stmt)
        return Node("fn", _sig(stmt), sl, sl, el, kids=_conv_stmts(stmt.body))
    if isinstance(stmt, ast.ClassDef):
        sl, el = _lineno(stmt), _end(stmt)
        bases = ", ".join(_unparse(b) for b in stmt.bases)
        pred = "{}({})".format(stmt.name, bases) if bases else stmt.name
        return Node("class", pred, sl, sl, el, kids=_conv_stmts(stmt.body))
    if isinstance(stmt, (ast.For, ast.AsyncFor)):
        sl, el = _lineno(stmt), _end(stmt)
        pred = "{} in {}".format(_unparse(stmt.target), _unparse(stmt.iter))
        n = Node("for", pred, sl, sl, el, kids=_conv_stmts(stmt.body))
        if stmt.orelse:
            n.chain.append(
                Node(
                    "for-else",
                    pred,
                    _lineno(stmt.orelse[0]),
                    _lineno(stmt.orelse[0]),
                    _end(stmt.orelse[-1]),
                    kids=_conv_stmts(stmt.orelse),
                )
            )
        return n
    if isinstance(stmt, ast.While):
        sl, el = _lineno(stmt), _end(stmt)
        pred = _unparse(stmt.test)
        n = Node("while", pred, sl, sl, el, kids=_conv_stmts(stmt.body))
        if stmt.orelse:
            n.chain.append(
                Node(
                    "while-else",
                    pred,
                    _lineno(stmt.orelse[0]),
                    _lineno(stmt.orelse[0]),
                    _end(stmt.orelse[-1]),
                    kids=_conv_stmts(stmt.orelse),
                )
            )
        return n
    if isinstance(stmt, (ast.With, ast.AsyncWith)):
        sl, el = _lineno(stmt), _end(stmt)
        items = ", ".join(_unparse(i) for i in stmt.items)
        return Node("with", items, sl, sl, el, kids=_conv_stmts(stmt.body))
    if isinstance(stmt, ast.Try) or (TryStar and isinstance(stmt, TryStar)):
        sl, el = _lineno(stmt), _end(stmt)
        n = Node("try", "", sl, sl, _end(stmt.body[-1]) if stmt.body else sl, kids=_conv_stmts(stmt.body))
        for h in stmt.handlers:
            pred = _unparse(h.type) if h.type is not None else ""
            if h.name:
                pred = "{} as {}".format(pred, h.name).strip()
            hs, he = _lineno(h), _end(h)
            n.chain.append(Node("except", pred, hs, hs, he, kids=_conv_stmts(h.body)))
        if stmt.orelse:
            n.chain.append(
                Node(
                    "try-else",
                    "",
                    _lineno(stmt.orelse[0]),
                    _lineno(stmt.orelse[0]),
                    _end(stmt.orelse[-1]),
                    kids=_conv_stmts(stmt.orelse),
                )
            )
        if stmt.finalbody:
            n.chain.append(
                Node(
                    "finally",
                    "",
                    _lineno(stmt.finalbody[0]),
                    _lineno(stmt.finalbody[0]),
                    _end(stmt.finalbody[-1]),
                    kids=_conv_stmts(stmt.finalbody),
                )
            )
        n.end_line = el
        return n
    if Match and isinstance(stmt, Match):
        sl, el = _lineno(stmt), _end(stmt)
        n = Node("match", _unparse(stmt.subject), sl, sl, el)
        for case in stmt.cases:
            pat = _unparse(case.pattern)
            if case.guard is not None:
                pat = "{} if {}".format(pat, _unparse(case.guard))
            nums = [_lineno(case)]
            if getattr(case, "pattern", None) is not None:
                nums.append(_lineno(case.pattern))
                nums.append(_end(case.pattern))
            if case.body:
                nums.append(_lineno(case.body[0]))
                nums.append(_end(case.body[-1]))
            cs, ce = min(nums), max(nums)
            n.kids.append(Node("case", pat, cs, cs, ce, kids=_conv_stmts(case.body)))
        return n
    sl, el = _lineno(stmt), _end(stmt)
    head = ""
    if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
        head = type(stmt).__name__.lower()
    return Node("stmt", "", sl, sl, el, head=head)


def _conv_if(node: ast.If, as_elif: bool) -> Node:
    sl, el = _lineno(node), _end(node)
    kind = "elif" if as_elif else "if"
    n = Node(kind, _unparse(node.test), sl, sl, _end(node.body[-1]) if node.body else sl, kids=_conv_stmts(node.body))
    orelse = node.orelse
    if len(orelse) == 1 and isinstance(orelse[0], ast.If):
        eln = _conv_if(orelse[0], True)
        n.chain.append(eln)
        n.chain.extend(eln.chain)
        eln.chain = []
        n.end_line = el
    elif orelse:
        es, ee = _lineno(orelse[0]), _end(orelse[-1])
        n.chain.append(Node("else", n.pred, es, es, ee, kids=_conv_stmts(orelse)))
        n.end_line = el
    else:
        n.end_line = el
    return n


class PythonIndex:
    def __init__(self, source: str, filename: str = "<src>"):
        self.source = source
        self.filename = filename
        self.lines = source.splitlines()
        self.nlines = len(self.lines)
        self.stack_at: List[List[Frame]] = [[] for _ in range(self.nlines + 2)]
        self.parse_error: Optional[str] = None
        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError as e:
            self.parse_error = "syntax: {} (L{})".format(e.msg, e.lineno)
            return
        roots = _conv_stmts(list(tree.body))
        paint(roots, [], self.stack_at)

    def at(self, line: int) -> Locus:
        here = self.lines[line - 1] if 1 <= line <= self.nlines else ""
        if self.parse_error:
            return Locus(
                file=self.filename,
                line=line,
                here=here.rstrip("\n"),
                frames=[],
                engine="python-ast",
                error=self.parse_error,
            )
        if line < 1 or line > self.nlines:
            return Locus(
                file=self.filename,
                line=line,
                here=here,
                frames=[],
                engine="python-ast",
                error="line {} out of range 1..{}".format(line, self.nlines),
                placed=False,
            )
        return Locus(
            file=self.filename,
            line=line,
            here=here.rstrip("\n"),
            frames=list(self.stack_at[line]),
            engine="python-ast",
        )
