from __future__ import annotations

import ast
from typing import Callable, Optional

from .model import Frame, Locus, collapse


def _unparse(node: ast.AST) -> str:
    try:
        return collapse(ast.unparse(node))
    except Exception:
        return type(node).__name__


def _end(node: ast.AST) -> int:
    return int(getattr(node, "end_lineno", None) or getattr(node, "lineno", 0) or 0)


def _first_lineno(node: ast.AST) -> Optional[int]:
    if getattr(node, "lineno", None):
        return int(node.lineno)
    best: Optional[int] = None
    for child in ast.iter_child_nodes(node):
        ln = _first_lineno(child)
        if ln is not None and (best is None or ln < best):
            best = ln
    return best


def _span(node: ast.AST) -> tuple[Optional[int], int]:
    start = getattr(node, "lineno", None)
    end = _end(node) if start else 0
    for child in getattr(node, "decorator_list", []) or []:
        if getattr(child, "lineno", None):
            if start is None or child.lineno < start:
                start = child.lineno
            end = max(end, _end(child))
    if start is None:
        start = _first_lineno(node)
        if start is None:
            return None, 0
        end = max(end, start)
    return int(start), int(end)


def _case_span(case: ast.match_case) -> tuple[Optional[int], int]:
    nums: list[int] = []
    for n in ast.walk(case):
        if getattr(n, "lineno", None):
            nums.append(int(n.lineno))
            nums.append(_end(n))
    if not nums:
        return None, 0
    return min(nums), max(nums)


def _contains(node: ast.AST, line: int) -> bool:
    if isinstance(node, ast.match_case):
        start, end = _case_span(node)
        if start is None:
            return False
        return start <= line <= end
    if not getattr(node, "lineno", None):
        return False
    return node.lineno <= line <= _end(node)


def _any_contains(nodes: list[ast.AST], line: int) -> bool:
    return any(_contains(n, line) for n in nodes)


def _sig(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda) -> str:
    if isinstance(node, ast.Lambda):
        return collapse(f"lambda {_unparse(node.args)}")
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    args: list[str] = []
    a = node.args
    posonly = list(a.posonlyargs)
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
    return f"{prefix}{node.name}({', '.join(args)})"


def _stmt_summary(node: ast.AST) -> str:
    if isinstance(node, ast.Assign):
        targets = ", ".join(_unparse(t) for t in node.targets)
        return collapse(f"{targets} = {_unparse(node.value)}")
    if isinstance(node, ast.Return):
        return collapse("return" if node.value is None else f"return {_unparse(node.value)}")
    if isinstance(node, ast.Raise):
        return collapse("raise" if node.exc is None else f"raise {_unparse(node.exc)}")
    try:
        return collapse(ast.unparse(node))
    except Exception:
        return type(node).__name__


def _handler_pred(h: ast.ExceptHandler) -> str:
    if h.type is None:
        pred = ""
    else:
        pred = _unparse(h.type)
    if h.name:
        pred = f"{pred} as {h.name}".strip()
    return pred


FrameFn = Callable[[int], list[Frame]]


def _if_frames(node: ast.If, as_elif: bool) -> FrameFn:
    test = _unparse(node.test)
    kind = "elif" if as_elif else "if"
    body, orelse = node.body, node.orelse
    elif_child = len(orelse) == 1 and isinstance(orelse[0], ast.If)

    def frames(line: int) -> list[Frame]:
        if _any_contains(body, line):
            return [Frame(kind, test, node.lineno, _end(node))]
        if _any_contains(orelse, line):
            if elif_child:
                return []
            return [Frame("else", test, orelse[0].lineno, _end(orelse[-1]))]
        if node.lineno <= line <= _end(node.test) or line == node.lineno:
            return [Frame("eval", f"{kind} {test}", node.lineno, _end(node.test))]
        return []

    return frames


def _try_frames(node: ast.Try) -> FrameFn:
    def frames(line: int) -> list[Frame]:
        if _any_contains(node.body, line):
            return [Frame("try", "", node.lineno, _end(node.body[-1]) if node.body else node.lineno)]
        for h in node.handlers:
            if _contains(h, line) or _any_contains(h.body, line):
                return [Frame("except", _handler_pred(h), h.lineno, _end(h))]
        if getattr(node, "orelse", None) and _any_contains(node.orelse, line):
            start = node.orelse[0].lineno
            return [Frame("try-else", "", start, _end(node.orelse[-1]))]
        if getattr(node, "finalbody", None) and _any_contains(node.finalbody, line):
            start = node.finalbody[0].lineno
            return [Frame("finally", "", start, _end(node.finalbody[-1]))]
        return [Frame("eval", "try", node.lineno, node.lineno)]

    return frames


def _for_frames(node: ast.For | ast.AsyncFor) -> FrameFn:
    target = _unparse(node.target)
    it = _unparse(node.iter)
    kw = "async for" if isinstance(node, ast.AsyncFor) else "for"
    pred = f"{target} in {it}"

    def frames(line: int) -> list[Frame]:
        if _any_contains(node.body, line):
            return [Frame("for", pred, node.lineno, _end(node))]
        if node.orelse and _any_contains(node.orelse, line):
            return [Frame("for-else", pred, node.orelse[0].lineno, _end(node.orelse[-1]))]
        return [Frame("eval", f"{kw} {pred}", node.lineno, node.lineno)]

    return frames


def _while_frames(node: ast.While) -> FrameFn:
    pred = _unparse(node.test)

    def frames(line: int) -> list[Frame]:
        if _any_contains(node.body, line):
            return [Frame("while", pred, node.lineno, _end(node))]
        if node.orelse and _any_contains(node.orelse, line):
            return [Frame("while-else", pred, node.orelse[0].lineno, _end(node.orelse[-1]))]
        return [Frame("eval", f"while {pred}", node.lineno, node.lineno)]

    return frames


def _with_frames(node: ast.With | ast.AsyncWith) -> FrameFn:
    items = ", ".join(_unparse(i) for i in node.items)
    kw = "async with" if isinstance(node, ast.AsyncWith) else "with"

    def frames(line: int) -> list[Frame]:
        if _any_contains(node.body, line):
            return [Frame("with", items, node.lineno, _end(node))]
        return [Frame("eval", f"{kw} {items}", node.lineno, node.lineno)]

    return frames


def _match_frames(node: ast.Match) -> FrameFn:
    subject = _unparse(node.subject)

    def frames(line: int) -> list[Frame]:
        for case in node.cases:
            if _contains(case, line) or _any_contains(case.body, line):
                pat = _unparse(case.pattern)
                if case.guard is not None:
                    pat = f"{pat} if {_unparse(case.guard)}"
                cstart, cend = _case_span(case)
                return [
                    Frame("match", subject, node.lineno, _end(node)),
                    Frame("case", pat, cstart or node.lineno, cend),
                ]
        return [Frame("eval", f"match {subject}", node.lineno, node.lineno)]

    return frames


def _func_frames(node: ast.FunctionDef | ast.AsyncFunctionDef) -> FrameFn:
    sig = _sig(node)
    decos = node.decorator_list

    def frames(line: int) -> list[Frame]:
        if line < node.lineno and any(_contains(d, line) for d in decos):
            return [Frame("eval", f"decorating {sig}", decos[0].lineno, node.lineno)]
        return [Frame("fn", sig, node.lineno, _end(node))]

    return frames


def _class_frames(node: ast.ClassDef) -> FrameFn:
    bases = ", ".join(_unparse(b) for b in node.bases)
    pred = f"{node.name}({bases})" if bases else node.name

    def frames(line: int) -> list[Frame]:
        return [Frame("class", pred, node.lineno, _end(node))]

    return frames


def _comp_frames(node: ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp) -> FrameFn:
    gens = []
    for g in node.generators:
        pred = f"{_unparse(g.target)} in {_unparse(g.iter)}"
        for ifs in g.ifs:
            pred += f" if {_unparse(ifs)}"
        gens.append(pred)
    label = " | ".join(gens)
    kind = type(node).__name__.replace("Comp", "-comp").replace("GeneratorExp", "genexp")

    def frames(line: int) -> list[Frame]:
        if _contains(node, line):
            return [Frame(kind, label, node.lineno, _end(node))]
        return []

    return frames


def _lambda_frames(node: ast.Lambda) -> FrameFn:
    def frames(line: int) -> list[Frame]:
        if _contains(node, line):
            return [Frame("fn", _sig(node), node.lineno, _end(node))]
        return []

    return frames


def _classifier(node: ast.AST, *, as_elif: bool = False) -> Optional[FrameFn]:
    if isinstance(node, ast.If):
        return _if_frames(node, as_elif)
    if isinstance(node, ast.Try):
        return _try_frames(node)
    if isinstance(node, (ast.For, ast.AsyncFor)):
        return _for_frames(node)
    if isinstance(node, ast.While):
        return _while_frames(node)
    if isinstance(node, (ast.With, ast.AsyncWith)):
        return _with_frames(node)
    if isinstance(node, ast.Match):
        return _match_frames(node)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return _func_frames(node)
    if isinstance(node, ast.ClassDef):
        return _class_frames(node)
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        return _comp_frames(node)
    if isinstance(node, ast.Lambda):
        return _lambda_frames(node)
    return None


def _child_as_elif(parent: ast.AST, child: ast.AST) -> bool:
    return isinstance(parent, ast.If) and isinstance(child, ast.If) and parent.orelse == [child]


def _is_exiting_stmts(stmts: list[ast.stmt]) -> bool:
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
        if name in {"exit", "abort", "fatal", "panic"}:
            return True
    if isinstance(stmt, ast.If):
        return _is_exiting_stmts(stmt.body) and bool(stmt.orelse) and _is_exiting_stmts(stmt.orelse)
    if isinstance(stmt, ast.Match):
        return bool(stmt.cases) and all(_is_exiting_stmts(c.body) for c in stmt.cases)
    if isinstance(stmt, ast.Try):
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
            return _unparse(flipped)
    text = _unparse(node)
    if text.startswith("not "):
        return text[4:]
    return f"¬({text})"


def _fallthrough_from(stmt: ast.stmt) -> list[Frame]:
    if not isinstance(stmt, ast.If):
        return []
    frames: list[Frame] = []
    cur: ast.If = stmt
    while True:
        if not _is_exiting_stmts(cur.body):
            return frames
        frames.append(Frame("given", _negate_test(cur.test), cur.lineno, _end(cur)))
        if not cur.orelse:
            return frames
        if len(cur.orelse) == 1 and isinstance(cur.orelse[0], ast.If):
            cur = cur.orelse[0]
            continue
        if _is_exiting_stmts(cur.orelse):
            return []
        return frames


def _stmt_lists(node: ast.AST) -> list[list[ast.stmt]]:
    out: list[list[ast.stmt]] = []
    for attr in ("body", "orelse", "finalbody"):
        val = getattr(node, attr, None)
        if isinstance(val, list) and val and isinstance(val[0], ast.stmt):
            out.append(val)
    if isinstance(node, ast.Try):
        for h in node.handlers:
            if h.body:
                out.append(h.body)
    if isinstance(node, ast.Match):
        for case in node.cases:
            if case.body:
                out.append(case.body)
    return out


class PythonIndex:
    def __init__(self, source: str, filename: str = "<src>"):
        self.source = source
        self.filename = filename
        self.lines = source.splitlines()
        self.nlines = len(self.lines)
        self.stack_at: list[list[Frame]] = [[] for _ in range(self.nlines + 2)]
        self.after_at: list[list[str]] = [[] for _ in range(self.nlines + 2)]
        self.parse_error: Optional[str] = None
        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError as e:
            self.parse_error = f"syntax: {e.msg} (L{e.lineno})"
            return
        self._cover(tree, [], None)

    def _cover(self, node: ast.AST, stack: list[Frame], parent: Optional[ast.AST]) -> None:
        as_elif = _child_as_elif(parent, node) if parent is not None else False
        fn = _classifier(node, as_elif=as_elif)
        start, end = _span(node)
        extra_for = fn if fn is not None else (lambda _line: [])

        if start:
            for ln in range(start, min(end, self.nlines) + 1):
                extra = extra_for(ln)
                if fn is None and self.stack_at[ln] and not extra:
                    continue
                self.stack_at[ln] = stack + extra

        covered: set[int] = set()
        for stmts in _stmt_lists(node):
            givens: list[Frame] = []
            for stmt in stmts:
                covered.add(id(stmt))
                cstart = getattr(stmt, "lineno", None) or _first_lineno(stmt) or (start or 1)
                child_stack = stack + extra_for(cstart) + givens
                self._cover(stmt, child_stack, node)
                more = _fallthrough_from(stmt)
                if more:
                    givens = givens + more

        self._preamble(node)

        for child in ast.iter_child_nodes(node):
            if id(child) in covered:
                continue
            cstart = getattr(child, "lineno", None) or _first_lineno(child)
            if cstart:
                child_stack = stack + extra_for(cstart)
            else:
                child_stack = stack + extra_for(start or 1)
            self._cover(child, child_stack, node)

    def _preamble(self, node: ast.AST) -> None:
        bodies: list[list[ast.stmt]] = []
        for attr in ("body", "orelse", "finalbody"):
            val = getattr(node, attr, None)
            if isinstance(val, list) and val and isinstance(val[0], ast.stmt):
                bodies.append(val)
        if isinstance(node, ast.Try):
            for h in node.handlers:
                if h.body:
                    bodies.append(h.body)
        if isinstance(node, ast.Match):
            for case in node.cases:
                if case.body:
                    bodies.append(case.body)
        for stmts in bodies:
            prev: list[str] = []
            for stmt in stmts:
                if not getattr(stmt, "lineno", None):
                    continue
                summary = _stmt_summary(stmt)
                # Only the statement's first line: painting the whole span
                # made nested lines inherit the previous module docstring.
                self.after_at[stmt.lineno] = prev[-2:]
                prev.append(summary)

    def at(self, line: int) -> Locus:
        here = self.lines[line - 1] if 1 <= line <= self.nlines else ""
        if self.parse_error:
            return Locus(
                file=self.filename,
                line=line,
                here=here.rstrip("\n"),
                frames=[],
                after=[],
                engine="python-ast",
                error=self.parse_error,
            )
        if line < 1 or line > self.nlines:
            return Locus(
                file=self.filename,
                line=line,
                here=here,
                frames=[],
                after=[],
                engine="python-ast",
                error=f"line {line} out of range 1..{self.nlines}",
                placed=False,
            )
        return Locus(
            file=self.filename,
            line=line,
            here=here.rstrip("\n"),
            frames=list(self.stack_at[line]),
            after=list(self.after_at[line]),
            engine="python-ast",
        )
