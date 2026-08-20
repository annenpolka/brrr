from __future__ import annotations

import ast
from dataclasses import dataclass, field

from .model import Frame, Locus

COMPOUND = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.Try,
    ast.With,
    ast.AsyncWith,
)
if hasattr(ast, "Match"):
    COMPOUND = COMPOUND + (ast.Match,)

EXIT_TYPES = (ast.Return, ast.Raise, ast.Continue, ast.Break)
FLAT_LIMIT = 99


def _unparse(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _negate(pred: str) -> str:
    p = pred.strip()
    if p.startswith("not "):
        rest = p[4:]
        if _is_atom(rest):
            return rest
    if " is not " in p:
        return p.replace(" is not ", " is ", 1)
    if " is " in p:
        return p.replace(" is ", " is not ", 1)
    if " not in " in p:
        return p.replace(" not in ", " in ", 1)
    if " != " in p:
        return p.replace(" != ", " == ", 1)
    if " == " in p:
        return p.replace(" == ", " != ", 1)
    return f"¬({p})"


def _is_atom(expr: str) -> bool:
    expr = expr.strip()
    if not expr:
        return False
    depth = 0
    for i, ch in enumerate(expr):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0 and ch in "|&" or (depth == 0 and expr[i : i + 4] == " and") or (
            depth == 0 and expr[i : i + 3] == " or"
        ):
            if ch in "|&":
                return False
            if expr[i : i + 4] == " and" or expr[i : i + 3] == " or":
                return False
    return depth == 0


def _exits_stmt(node: ast.stmt) -> bool:
    if isinstance(node, EXIT_TYPES):
        return True
    if isinstance(node, ast.If):
        return bool(node.orelse) and _exits_body(node.body) and _exits_body(node.orelse)
    if isinstance(node, ast.Try):
        if not _exits_body(node.body):
            return False
        if not node.handlers:
            return False
        return all(_exits_body(h.body) for h in node.handlers)
    return False


def _exits_body(stmts: list[ast.stmt]) -> bool:
    return bool(stmts) and _exits_stmt(stmts[-1])


def _is_guard_if(stmt: ast.stmt) -> bool:
    return isinstance(stmt, ast.If) and not stmt.orelse and _exits_body(stmt.body)


def _flatten(node: ast.AST) -> str:
    if isinstance(node, ast.If):
        body = " ".join(_flatten(s) for s in node.body)
        return f"if {_unparse(node.test)}: {body}".rstrip()
    if isinstance(node, ast.Try):
        stmts = list(node.body)
        if len(stmts) > 1 and isinstance(stmts[-1], ast.Return):
            stmts = stmts[:-1]
        body = " ".join(_flatten(s) for s in stmts)
        return f"try: {body}".rstrip()
    if isinstance(node, ast.For):
        return f"for {_unparse(node.target)} in {_unparse(node.iter)}"
    if isinstance(node, ast.AsyncFor):
        return f"async for {_unparse(node.target)} in {_unparse(node.iter)}"
    if isinstance(node, ast.While):
        return f"while {_unparse(node.test)}"
    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
        return f"def {node.name}"
    if isinstance(node, ast.ClassDef):
        return f"class {node.name}"
    if isinstance(node, ast.Return):
        return f"return {_unparse(node.value)}" if node.value is not None else "return"
    if isinstance(node, ast.Raise):
        return f"raise {_unparse(node.exc)}" if node.exc is not None else "raise"
    if isinstance(node, ast.Continue):
        return "continue"
    if isinstance(node, ast.Break):
        return "break"
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(
        node.value.value, str
    ):
        return repr(node.value.value)
    text = _unparse(node)
    return " ".join(text.split())


def _clip(text: str) -> str:
    if len(text) <= FLAT_LIMIT:
        return text
    return text[:FLAT_LIMIT].rstrip() + "…"


def _fn_pred(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args: list[str] = []
    a = node.args
    pos = list(a.posonlyargs) + list(a.args)
    for p in pos:
        args.append(p.arg)
    if a.vararg:
        args.append("*" + a.vararg.arg)
    for p in a.kwonlyargs:
        args.append(p.arg)
    if a.kwarg:
        args.append("**" + a.kwarg.arg)
    return f"{node.name}({', '.join(args)})"


def _comp_pred(node: ast.ListComp | ast.SetComp | ast.GeneratorExp | ast.DictComp) -> str:
    parts: list[str] = []
    for g in node.generators:
        piece = f"{_unparse(g.target)} in {_unparse(g.iter)}"
        for iff in g.ifs:
            piece += f" if {_unparse(iff)}"
        parts.append(piece)
    return " ".join(parts)


def _comp_kind(node: ast.AST) -> str:
    if isinstance(node, ast.ListComp):
        return "List-comp"
    if isinstance(node, ast.SetComp):
        return "Set-comp"
    if isinstance(node, ast.DictComp):
        return "Dict-comp"
    return "Gen-comp"


@dataclass
class _Slot:
    frames: list[Frame] = field(default_factory=list)
    after: list[str] = field(default_factory=list)


class _PyAnalyzer:
    def __init__(self, source: str, filename: str) -> None:
        self.filename = filename
        self.lines = source.splitlines()
        self.n = len(self.lines)
        self.slots: list[_Slot] = [_Slot() for _ in range(self.n + 1)]
        self.tree = ast.parse(source, filename=filename)

    def run(self) -> None:
        self._visit_body(self.tree.body, [])

    def _set(self, line: int, frames: list[Frame], after: list[str] | None = None) -> None:
        if 1 <= line <= self.n:
            self.slots[line] = _Slot(list(frames), list(after or []))

    def _cover(self, start: int, end: int, frames: list[Frame], after: list[str]) -> None:
        for ln in range(start, end + 1):
            self._set(ln, frames, after)

    def _visit_body(self, stmts: list[ast.stmt], frames: list[Frame]) -> None:
        pending: list[Frame] = []
        prev: list[str] = []
        for stmt in stmts:
            extra = pending if isinstance(stmt, COMPOUND) else []
            cur = frames + extra
            start = getattr(stmt, "lineno", None)
            end = getattr(stmt, "end_lineno", start)
            if start:
                self._cover(start, end or start, cur, [])
                self._set(start, cur, prev)
            self._visit_stmt(stmt, cur, prev)
            if _is_guard_if(stmt):
                test = _unparse(stmt.test)
                pending.append(
                    Frame("given", _negate(test), stmt.lineno, stmt.end_lineno or stmt.lineno)
                )
            prev.append(_clip(_flatten(stmt)))

    def _visit_stmt(self, stmt: ast.stmt, frames: list[Frame], after: list[str]) -> None:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._visit_func(stmt, frames, after)
            return
        if isinstance(stmt, ast.ClassDef):
            pred = stmt.name
            fr = frames + [Frame("class", pred, stmt.lineno, stmt.end_lineno or stmt.lineno)]
            self._set(stmt.lineno, fr, after)
            self._visit_body(stmt.body, fr)
            return
        if isinstance(stmt, ast.If):
            self._visit_if(stmt, frames, "if", after)
            return
        if isinstance(stmt, (ast.For, ast.AsyncFor)):
            self._visit_for(stmt, frames, after)
            return
        if isinstance(stmt, ast.While):
            self._visit_while(stmt, frames, after)
            return
        if isinstance(stmt, ast.Try):
            self._visit_try(stmt, frames, after)
            return
        if isinstance(stmt, (ast.With, ast.AsyncWith)):
            items = ", ".join(_unparse(i) for i in stmt.items)
            self._set(stmt.lineno, frames + [Frame("eval", f"with {items}", stmt.lineno, stmt.lineno)], after)
            self._visit_body(stmt.body, frames + [Frame("with", items, stmt.lineno, stmt.end_lineno or stmt.lineno)])
            return
        if hasattr(ast, "Match") and isinstance(stmt, ast.Match):
            self._visit_match(stmt, frames, after)
            return
        self._attach_comps(stmt, frames, after)

    def _attach_comps(self, stmt: ast.stmt, frames: list[Frame], after: list[str]) -> None:
        found: list[Frame] = []
        for n in ast.walk(stmt):
            if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                found.append(
                    Frame(
                        _comp_kind(n),
                        _comp_pred(n),
                        getattr(n, "lineno", stmt.lineno),
                        getattr(n, "end_lineno", stmt.lineno),
                    )
                )
        if found:
            self._set(stmt.lineno, frames + found, after)

    def _visit_func(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        frames: list[Frame],
        after: list[str],
    ) -> None:
        pred = _fn_pred(node)
        fn = Frame("fn", pred, node.lineno, node.end_lineno or node.lineno)
        for dec in node.decorator_list:
            self._set(
                dec.lineno,
                frames + [Frame("eval", f"{_unparse(dec)} {pred}", dec.lineno, node.lineno)],
                [],
            )
        self._set(node.lineno, frames + [fn], after)
        self._visit_body(node.body, frames + [fn])

    def _visit_if(self, node: ast.If, frames: list[Frame], kind: str, after: list[str]) -> None:
        pred = _unparse(node.test)
        self._set(
            node.lineno,
            frames + [Frame("eval", f"{kind} {pred}", node.lineno, node.lineno)],
            after if kind == "if" else [],
        )
        if_frame = Frame(kind, pred, node.lineno, node.end_lineno or node.lineno)
        self._visit_body(node.body, frames + [if_frame])
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                self._visit_if(node.orelse[0], frames, "elif", after)
            else:
                start = node.orelse[0].lineno
                end = node.orelse[-1].end_lineno or start
                else_frame = Frame("else", pred, start, end)
                self._visit_body(node.orelse, frames + [else_frame])

    def _visit_for(
        self, node: ast.For | ast.AsyncFor, frames: list[Frame], after: list[str]
    ) -> None:
        pred = f"{_unparse(node.target)} in {_unparse(node.iter)}"
        kw = "async for" if isinstance(node, ast.AsyncFor) else "for"
        self._set(node.lineno, frames + [Frame("eval", f"{kw} {pred}", node.lineno, node.lineno)], after)
        for_frame = Frame("for", pred, node.lineno, node.end_lineno or node.lineno)
        self._visit_body(node.body, frames + [for_frame])
        if node.orelse:
            else_ln = node.orelse[0].lineno - 1
            if else_ln >= 1:
                self._set(else_ln, frames + [Frame("eval", f"{kw} {pred}", node.lineno, node.lineno)], after)
            fe = Frame("for-else", pred, node.orelse[0].lineno, node.orelse[-1].end_lineno or node.orelse[0].lineno)
            self._visit_body(node.orelse, frames + [fe])

    def _visit_while(self, node: ast.While, frames: list[Frame], after: list[str]) -> None:
        pred = _unparse(node.test)
        self._set(node.lineno, frames + [Frame("eval", f"while {pred}", node.lineno, node.lineno)], after)
        self._visit_body(node.body, frames + [Frame("while", pred, node.lineno, node.end_lineno or node.lineno)])
        if node.orelse:
            self._visit_body(
                node.orelse,
                frames + [Frame("while-else", pred, node.orelse[0].lineno, node.orelse[-1].end_lineno or 0)],
            )

    def _visit_try(self, node: ast.Try, frames: list[Frame], after: list[str]) -> None:
        self._set(node.lineno, frames + [Frame("eval", "try", node.lineno, node.lineno)], after)
        last_body = node.body[-1].end_lineno if node.body else node.lineno
        self._visit_body(node.body, frames + [Frame("try", "", node.lineno, last_body or node.lineno)])
        for h in node.handlers:
            if h.type is None:
                pred = ""
            else:
                pred = _unparse(h.type)
                if h.name:
                    pred = f"{pred} as {h.name}"
            hf = Frame("except", pred, h.lineno, h.end_lineno or h.lineno)
            self._set(h.lineno, frames + [hf], after)
            self._visit_body(h.body, frames + [hf])
        if node.orelse:
            else_ln = node.orelse[0].lineno - 1
            if else_ln >= 1:
                self._set(else_ln, frames + [Frame("eval", "try", node.lineno, node.lineno)], after)
            te = Frame("try-else", "", node.orelse[0].lineno, node.orelse[-1].end_lineno or 0)
            self._visit_body(node.orelse, frames + [te])
        if node.finalbody:
            fin_ln = node.finalbody[0].lineno - 1
            if fin_ln >= 1:
                self._set(fin_ln, frames + [Frame("eval", "try", node.lineno, node.lineno)], after)
            ff = Frame("finally", "", node.finalbody[0].lineno, node.finalbody[-1].end_lineno or 0)
            self._visit_body(node.finalbody, frames + [ff])

    def _visit_match(self, node: ast.AST, frames: list[Frame], after: list[str]) -> None:
        subj = _unparse(node.subject)
        self._set(node.lineno, frames + [Frame("eval", f"match {subj}", node.lineno, node.lineno)], after)
        mf = Frame("match", subj, node.lineno, node.end_lineno or node.lineno)
        for case in node.cases:
            pred = _unparse(case.pattern)
            if case.guard is not None:
                pred = f"{pred} if {_unparse(case.guard)}"
            cf = Frame("case", pred, case.pattern.lineno, case.pattern.end_lineno or case.pattern.lineno)
            if case.body:
                cf.end_line = case.body[-1].end_lineno or cf.end_line
            self._set(case.pattern.lineno, frames + [mf, cf], after)
            self._visit_body(case.body, frames + [mf, cf])


def query_python(path: str, source: str, line: int) -> Locus:
    loc = Locus(file=path, line=line, engine="python-ast")
    if line < 1 or line > len(source.splitlines()):
        n = len(source.splitlines())
        loc.error = f"line {line} out of range 1..{n}"
        loc.here = ""
        return loc
    try:
        az = _PyAnalyzer(source, path)
        az.run()
    except SyntaxError as exc:
        loc.error = f"syntax error: {exc.msg}"
        return loc
    lines = source.splitlines()
    loc.here = lines[line - 1] if 0 <= line - 1 < len(lines) else ""
    slot = az.slots[line] if line < len(az.slots) else _Slot()
    loc.frames = slot.frames
    loc.after = slot.after
    return loc.finalize()


def scan_python(path: str, source: str) -> list[Locus]:
    try:
        az = _PyAnalyzer(source, path)
        az.run()
    except SyntaxError:
        return []
    lines = source.splitlines()
    out: list[Locus] = []
    for i, text in enumerate(lines, 1):
        slot = az.slots[i]
        if not slot.frames and not text.strip():
            continue
        if not slot.frames and not text.strip():
            continue
        loc = Locus(file=path, line=i, here=text, engine="python-ast", frames=slot.frames, after=slot.after)
        loc.finalize()
        out.append(loc)
    return out
