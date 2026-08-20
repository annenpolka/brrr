from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from nigh.lex import (
    KIND_COLON,
    KIND_COMMA,
    KIND_DOT,
    KIND_IDENT,
    KIND_LBRACK,
    KIND_LPAREN,
    KIND_NUMBER,
    KIND_OP,
    KIND_OTHER,
    KIND_PIPE,
    KIND_RBRACK,
    KIND_RPAREN,
    KIND_STRING,
    Token,
    tokenize,
)
from nigh.walk import classify_ext

# Vocabulary vs prose: nigh operates on codes, not sentences.
MIN_STR_LEN = 2
MAX_STR_LEN = 80
EMBEDDED_STR = re.compile(r'"([A-Za-z][A-Za-z0-9_.:/-]{1,60})"')
REGEXISH = re.compile(r"[\[\]\(\)\{\}\*\+\?\\|]")

GENERIC_RHS = {
    "string",
    "object",
    "number",
    "boolean",
    "integer",
    "array",
    "null",
    "undefined",
    "function",
    "bigint",
    "symbol",
    "any",
    "unknown",
    "void",
    "true",
    "false",
    "none",
    "nil",
    "ok",
    "err",
    "error",
    "utf-8",
    "utf8",
    "ascii",
}

ORACLE_LHS_SUFFIXES = {
    "output",
    "result",
    "text",
    "expected",
    "got",
    "want",
    "actual",
    "message",
    "html",
    "content",
    "body",
    "snapshot",
    "stdout",
    "stderr",
    "source",
    "rendered",
    "markdown",
    "prompt",
}

ASSERT_IDENTS = {
    "expect",
    "assert",
    "assert_eq",
    "assert_ne",
    "assertequal",
    "assert_equal",
    "tobe",
    "toequal",
    "tostrictequal",
    "tobe",
}

TRIVIAL_INTS = {0, 1, -1, 2, 10, 100}

EQ_OPS = {"==", "===", "!=", "!=="}
INEQ_OPS = {"<", ">", "<=", ">="}
METHOD_GATES = {
    "equals",
    "equal",
    "startswith",
    "endswith",
    "contains",
    "includes",
    "hasprefix",
    "hassuffix",
    "has_prefix",
    "has_suffix",
    "startswith",
    "ends_with",
    "starts_with",
}


@dataclass(frozen=True)
class Loc:
    path: str
    line: int
    col: int

    def __str__(self) -> str:
        return f"{self.path}:{self.line}"


@dataclass
class Producer:
    value: str | int | float
    kind: str  # string | number
    loc: Loc
    field: str | None = None
    via: str = "literal"


@dataclass
class Gate:
    lhs: str
    field: str
    op: str
    rhs: list[str | int | float]
    loc: Loc
    kind: str  # string | number
    method: str | None = None
    raw: str = ""


@dataclass
class Corpus:
    producers: list[Producer] = field(default_factory=list)
    gates: list[Gate] = field(default_factory=list)
    files: int = 0
    skipped: int = 0


def extract_path(path: Path, root: Path | None = None) -> tuple[list[Gate], list[Producer]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], []
    rel = _rel(path, root)
    role = classify_ext(path)
    suffix = path.suffix.lower()
    if suffix in {".json", ".jsonl"}:
        return [], _extract_json(text, rel, suffix)
    if suffix in {".yaml", ".yml", ".toml"}:
        return [], _extract_simple_map(text, rel)
    tokens = tokenize(text, suffix)
    producers = _producers_from_tokens(tokens, rel)
    gates: list[Gate] = []
    if role == "source":
        gates = _gates_from_tokens(tokens, rel)
    return gates, producers


def extract_roots(paths: list[Path]) -> Corpus:
    from nigh.walk import iter_files

    corpus = Corpus()
    files = iter_files(paths)
    root = paths[0] if len(paths) == 1 else Path.cwd()
    for path in files:
        corpus.files += 1
        try:
            gates, producers = extract_path(path, root)
        except Exception:
            corpus.skipped += 1
            continue
        corpus.gates.extend(gates)
        corpus.producers.extend(producers)
    return corpus


def is_vocab_string(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) < MIN_STR_LEN or len(value) > MAX_STR_LEN:
        return False
    if any(ch.isspace() for ch in value):
        return False
    if any(ord(ch) < 32 for ch in value):
        return False
    if _looks_like_path(value):
        return False
    if _looks_like_import(value):
        return False
    return True


def _looks_like_path(value: str) -> bool:
    if value.startswith("./") or value.startswith("../"):
        return True
    if value.startswith("/") and "/" in value[1:]:
        return True
    if re.match(r"^[A-Za-z]:\\", value):
        return True
    if "/" in value and re.search(r"\.[A-Za-z0-9]{1,5}(?::\d+)?$", value):
        return True
    return False


def _is_protocol_needle(value: str) -> bool:
    """contains() needles that are codes, not UI/oracle snippets."""
    if value.startswith(("--", "@", "www.", "data:", "---", "+++", "@@")):
        return True
    if any(ch in value for ch in ".:/") and not any(ch.isspace() for ch in value):
        return True
    compact = value.replace("-", "").replace("_", "")
    if "-" in value and compact.isalnum():
        return True
    if value.isupper() and value.replace("_", "").isalnum() and len(value) >= 3:
        return True
    return False


def _looks_like_import(value: str) -> bool:
    if value.startswith("@") and "/" in value:
        return True
    if value.startswith("github.com/"):
        return True
    if re.match(r"^[a-z0-9.-]+\.[a-z]{2,}/.+\.", value):
        return True
    return False


def _rel(path: Path, root: Path | None) -> str:
    if root is None:
        return str(path)
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _field_of_lhs(lhs: str) -> str:
    if not lhs:
        return ""
    part = lhs.split(".")[-1]
    part = re.sub(r"\[.*", "", part)
    return part


def _keep_string_gate(lhs: str, rhs: str) -> bool:
    if not is_vocab_string(rhs):
        return False
    if rhs.lower() in GENERIC_RHS:
        return False
    field = _field_of_lhs(lhs).lower()
    if field in ORACLE_LHS_SUFFIXES:
        return False
    if lhs.lower() in ASSERT_IDENTS:
        return False
    if field in {"__name__", "name"} and rhs in {"__main__", "__name__"}:
        return False
    if lhs in {"__name__"} or rhs == "__main__":
        return False
    if field == "regex" or lhs.lower() == "regex":
        return False
    if REGEXISH.search(rhs) and any(ch in rhs for ch in "[]|*+?{}"):
        return False
    return True


def _keep_number_gate(rhs: int | float) -> bool:
    if isinstance(rhs, bool):
        return False
    if isinstance(rhs, int) and rhs in TRIVIAL_INTS:
        return False
    if isinstance(rhs, float) and rhs in {0.0, 1.0, -1.0}:
        return False
    return True


def _dotted_lhs(tokens: list[Token], idx: int) -> tuple[str, int]:
    """Read backward from tokens[idx] (an ident) for a.b.c."""
    parts = [str(tokens[idx].value)]
    k = idx
    while k >= 2 and tokens[k - 1].kind == KIND_DOT and tokens[k - 2].kind == KIND_IDENT:
        parts.append(str(tokens[k - 2].value))
        k -= 2
    parts.reverse()
    return ".".join(parts), k


def _gates_from_tokens(tokens: list[Token], rel: str) -> list[Gate]:
    gates: list[Gate] = []
    n = len(tokens)
    i = 0
    while i < n:
        tok = tokens[i]

        if (
            tok.kind == KIND_IDENT
            and str(tok.value).lower() == "typeof"
            and i + 3 < n
            and tokens[i + 2].kind == KIND_OP
            and tokens[i + 3].kind == KIND_STRING
        ):
            i += 1
            continue

        if tok.kind == KIND_IDENT and str(tok.value) == "case" and i + 1 < n:
            if tokens[i + 1].kind == KIND_STRING and isinstance(tokens[i + 1].value, str):
                rhs = tokens[i + 1].value
                if _keep_string_gate("case", rhs):
                    gates.append(
                        Gate(
                            lhs="case",
                            field="case",
                            op="==",
                            rhs=[rhs],
                            loc=Loc(rel, tokens[i + 1].line, tokens[i + 1].col),
                            kind="string",
                            raw=f'case {tokens[i + 1].raw}',
                        )
                    )
            i += 1
            continue

        if tok.kind == KIND_OP and tok.value in EQ_OPS | INEQ_OPS:
            left = tokens[i - 1] if i > 0 else None
            right = tokens[i + 1] if i + 1 < n else None
            if left is None or right is None:
                i += 1
                continue
            gate = _cmp_gate(tokens, i, left, right, rel)
            if gate:
                gates.append(gate)
            i += 1
            continue

        if tok.kind == KIND_DOT and i + 1 < n and tokens[i + 1].kind == KIND_IDENT:
            method = str(tokens[i + 1].value)
            if method.lower() in METHOD_GATES or method in {
                "startsWith",
                "endsWith",
                "hasPrefix",
                "hasSuffix",
                "starts_with",
                "ends_with",
            }:
                gate = _method_gate(tokens, i, rel)
                if gate:
                    gates.append(gate)
            i += 1
            continue

        if tok.kind == KIND_IDENT and str(tok.value) == "in":
            gate = _in_gate(tokens, i, rel)
            if gate:
                gates.append(gate)
            i += 1
            continue

        if tok.kind == KIND_IDENT and str(tok.value) in {"matches", "matches!"}:
            gate = _matches_gate(tokens, i, rel)
            if gate:
                gates.append(gate)
            i += 1
            continue

        i += 1
    return _dedupe_gates(gates)


def _cmp_gate(
    tokens: list[Token], op_i: int, left: Token, right: Token, rel: str
) -> Gate | None:
    op = str(tokens[op_i].value)
    lhs_tok: Token | None = None
    rhs_tok: Token | None = None
    flipped = False
    if left.kind == KIND_IDENT and right.kind in {KIND_STRING, KIND_NUMBER}:
        lhs_tok, rhs_tok = left, right
    elif right.kind == KIND_IDENT and left.kind in {KIND_STRING, KIND_NUMBER}:
        lhs_tok, rhs_tok = right, left
        flipped = True
    else:
        return None
    assert lhs_tok is not None and rhs_tok is not None
    if not flipped:
        lhs, _ = _dotted_lhs(tokens, op_i - 1)
    else:
        lhs = str(tokens[op_i + 1].value) if tokens[op_i + 1].kind == KIND_IDENT else str(lhs_tok.value)

    if rhs_tok.kind == KIND_STRING:
        if not isinstance(rhs_tok.value, str) or not _keep_string_gate(lhs, rhs_tok.value):
            return None
        kind = "string"
        rhs: list[str | int | float] = [rhs_tok.value]
    else:
        if not isinstance(rhs_tok.value, (int, float)) or isinstance(rhs_tok.value, bool):
            return None
        if not _keep_number_gate(rhs_tok.value):
            return None
        kind = "number"
        rhs = [rhs_tok.value]
        if op in EQ_OPS and kind == "number" and isinstance(rhs_tok.value, int) and rhs_tok.value < 4:
            return None

    if flipped and op in INEQ_OPS:
        op = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}[op]

    return Gate(
        lhs=lhs,
        field=_field_of_lhs(lhs),
        op=op,
        rhs=rhs,
        loc=Loc(rel, rhs_tok.line, rhs_tok.col),
        kind=kind,
        raw=f"{lhs} {op} {rhs_tok.raw}",
    )


def _method_gate(tokens: list[Token], dot_i: int, rel: str) -> Gate | None:
    method = str(tokens[dot_i + 1].value)
    # receiver.method(literal)
    if dot_i + 4 < len(tokens) and tokens[dot_i + 2].kind == KIND_LPAREN:
        arg = tokens[dot_i + 3]
        if arg.kind != KIND_STRING or not isinstance(arg.value, str):
            return None
        if tokens[dot_i].kind != KIND_DOT:
            return None
        if dot_i == 0 or tokens[dot_i - 1].kind != KIND_IDENT:
            return None
        lhs, _ = _dotted_lhs(tokens, dot_i - 1)
        if not _keep_string_gate(lhs, arg.value):
            return None
        op = {
            "startswith": "startswith",
            "startsWith": "startswith",
            "starts_with": "startswith",
            "endswith": "endswith",
            "endsWith": "endswith",
            "ends_with": "endswith",
            "hasprefix": "startswith",
            "hasPrefix": "startswith",
            "has_prefix": "startswith",
            "hassuffix": "endswith",
            "hasSuffix": "endswith",
            "has_suffix": "endswith",
            "contains": "contains",
            "includes": "contains",
            "equals": "==",
            "equal": "==",
        }.get(method, "contains")
        if op == "contains" and not _is_protocol_needle(arg.value):
            return None
        return Gate(
            lhs=lhs,
            field=_field_of_lhs(lhs),
            op=op,
            rhs=[arg.value],
            loc=Loc(rel, arg.line, arg.col),
            kind="string",
            method=method,
            raw=f"{lhs}.{method}({arg.raw})",
        )
    return None


def _collect_string_list(tokens: list[Token], start: int) -> tuple[list[str], int]:
    values: list[str] = []
    i = start
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        if tok.kind in {KIND_RPAREN, KIND_RBRACK}:
            return values, i
        if tok.kind == KIND_STRING and isinstance(tok.value, str):
            values.append(tok.value)
        i += 1
    return values, i


def _in_gate(tokens: list[Token], in_i: int, rel: str) -> Gate | None:
    if in_i == 0 or tokens[in_i - 1].kind != KIND_IDENT:
        return None
    if in_i + 1 >= len(tokens) or tokens[in_i + 1].kind not in {KIND_LPAREN, KIND_LBRACK}:
        return None
    lhs, _ = _dotted_lhs(tokens, in_i - 1)
    values, _end = _collect_string_list(tokens, in_i + 2)
    values = [v for v in values if _keep_string_gate(lhs, v)]
    if not values:
        return None
    loc_tok = tokens[in_i + 2] if in_i + 2 < len(tokens) else tokens[in_i]
    return Gate(
        lhs=lhs,
        field=_field_of_lhs(lhs),
        op="in",
        rhs=list(values),
        loc=Loc(rel, loc_tok.line, loc_tok.col),
        kind="string",
        raw=f"{lhs} in {values!r}",
    )


def _matches_gate(tokens: list[Token], i: int, rel: str) -> Gate | None:
    # matches!(ident, "a" | "b")
    j = i + 1
    if j < len(tokens) and tokens[j].kind == KIND_OTHER and tokens[j].value == "!":
        j += 1
    if j >= len(tokens) or tokens[j].kind != KIND_LPAREN:
        return None
    j += 1
    if j >= len(tokens) or tokens[j].kind != KIND_IDENT:
        return None
    lhs, _ = _dotted_lhs(tokens, j)
    values: list[str] = []
    loc_line, loc_col = tokens[j].line, tokens[j].col
    while j < len(tokens) and tokens[j].kind != KIND_RPAREN:
        if tokens[j].kind == KIND_STRING and isinstance(tokens[j].value, str):
            if _keep_string_gate(lhs, tokens[j].value):
                values.append(tokens[j].value)
                loc_line, loc_col = tokens[j].line, tokens[j].col
        j += 1
    if not values:
        return None
    return Gate(
        lhs=lhs,
        field=_field_of_lhs(lhs),
        op="in",
        rhs=list(values),
        loc=Loc(rel, loc_line, loc_col),
        kind="string",
        raw=f"matches!({lhs}, {values!r})",
    )


def _producers_from_tokens(tokens: list[Token], rel: str) -> list[Producer]:
    """Literals that construct a value, not those that test one."""
    n = len(tokens)
    gate_spans: set[int] = set()
    for i, tok in enumerate(tokens):
        if tok.kind == KIND_OP and tok.value in EQ_OPS | INEQ_OPS:
            if i + 1 < n and tokens[i + 1].kind in {KIND_STRING, KIND_NUMBER}:
                gate_spans.add(i + 1)
            if i > 0 and tokens[i - 1].kind in {KIND_STRING, KIND_NUMBER}:
                gate_spans.add(i - 1)
        if tok.kind == KIND_IDENT and str(tok.value) == "case" and i + 1 < n:
            if tokens[i + 1].kind == KIND_STRING:
                gate_spans.add(i + 1)
        if tok.kind == KIND_IDENT and str(tok.value).lower() == "typeof":
            if i + 3 < n and tokens[i + 3].kind == KIND_STRING:
                gate_spans.add(i + 3)
        if tok.kind == KIND_DOT and i + 3 < n and tokens[i + 1].kind == KIND_IDENT:
            if str(tokens[i + 1].value).lower() in METHOD_GATES | {
                "startswith",
                "endswith",
                "hasprefix",
                "hassuffix",
                "startswith",
            }:
                if tokens[i + 3].kind == KIND_STRING:
                    gate_spans.add(i + 3)

    producers: list[Producer] = []
    for i, tok in enumerate(tokens):
        if i in gate_spans:
            continue
        field = _producer_field(tokens, i)
        if tok.kind == KIND_STRING and isinstance(tok.value, str):
            if is_vocab_string(tok.value) and tok.value.lower() not in GENERIC_RHS:
                producers.append(
                    Producer(
                        value=tok.value,
                        kind="string",
                        loc=Loc(rel, tok.line, tok.col),
                        field=field,
                    )
                )
            elif len(tok.value) >= 16:
                for frag in _embedded_vocab(tok.value):
                    producers.append(
                        Producer(
                            value=frag,
                            kind="string",
                            loc=Loc(rel, tok.line, tok.col),
                            field=field,
                            via="embedded",
                        )
                    )
        elif tok.kind == KIND_NUMBER and isinstance(tok.value, (int, float)):
            if isinstance(tok.value, int) and tok.value in TRIVIAL_INTS:
                continue
            producers.append(
                Producer(
                    value=tok.value,
                    kind="number",
                    loc=Loc(rel, tok.line, tok.col),
                    field=field,
                )
            )
    return producers


def _producer_field(tokens: list[Token], i: int) -> str | None:
    # field: value   or   field = value   or   { field: value }
    if i >= 2 and tokens[i - 1].kind == KIND_COLON and tokens[i - 2].kind in {KIND_IDENT, KIND_STRING}:
        return str(tokens[i - 2].value)
    if i >= 2 and tokens[i - 1].kind == KIND_OP and tokens[i - 1].value in {"==", "==="}:
        return None
    if i >= 2 and tokens[i - 2].kind == KIND_IDENT and tokens[i - 1].kind == KIND_OTHER:
        # ident = value, but `=` is OTHER
        if tokens[i - 1].value == "=":
            return str(tokens[i - 2].value)
    return None


def _embedded_vocab(blob: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for m in EMBEDDED_STR.finditer(blob):
        frag = m.group(1)
        if frag in seen:
            continue
        if not is_vocab_string(frag) or frag.lower() in GENERIC_RHS:
            continue
        seen.add(frag)
        out.append(frag)
    return out


def _extract_json(text: str, rel: str, suffix: str) -> list[Producer]:
    producers: list[Producer] = []
    if suffix == ".jsonl":
        for lineno, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            padded = ("\n" * (lineno - 1)) + line
            _walk_json(data, rel, padded, None, producers)
        return producers
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return _extract_simple_map(text, rel)
    _walk_json(data, rel, text, None, producers)
    return producers


def _line_of_json_value(text: str, value: object) -> int:
    if isinstance(value, str):
        needle = json.dumps(value)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        needle = json.dumps(value)
    else:
        return 1
    pos = text.find(needle)
    if pos < 0:
        return 1
    return text.count("\n", 0, pos) + 1


def _walk_json(
    node: object, rel: str, text: str, field: str | None, out: list[Producer]
) -> None:
    if isinstance(node, dict):
        for key, val in node.items():
            _walk_json(val, rel, text, str(key), out)
        return
    if isinstance(node, list):
        for item in node:
            _walk_json(item, rel, text, field, out)
        return
    line = _line_of_json_value(text, node)
    if isinstance(node, str) and is_vocab_string(node) and node.lower() not in GENERIC_RHS:
        out.append(Producer(value=node, kind="string", loc=Loc(rel, line, 1), field=field, via="json"))
        return
    if isinstance(node, (int, float)) and not isinstance(node, bool):
        if isinstance(node, int) and node in TRIVIAL_INTS:
            return
        out.append(Producer(value=node, kind="number", loc=Loc(rel, line, 1), field=field, via="json"))


def _extract_simple_map(text: str, rel: str) -> list[Producer]:
    producers: list[Producer] = []
    pair = re.compile(
        r"""^[\s\-]*["']?([A-Za-z_][\w.-]*)["']?\s*[:=]\s*(?:["']([^"']{2,80})["']|(-?\d+(?:\.\d+)?))\s*,?\s*$"""
    )
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("#") or line.lstrip().startswith("//"):
            continue
        m = pair.match(line)
        if not m:
            continue
        field, s, num = m.group(1), m.group(2), m.group(3)
        if s is not None and is_vocab_string(s) and s.lower() not in GENERIC_RHS:
            producers.append(
                Producer(value=s, kind="string", loc=Loc(rel, lineno, 1), field=field, via="map")
            )
        elif num is not None:
            value: int | float
            value = float(num) if "." in num else int(num)
            if isinstance(value, int) and value in TRIVIAL_INTS:
                continue
            producers.append(
                Producer(value=value, kind="number", loc=Loc(rel, lineno, 1), field=field, via="map")
            )
    return producers


def _dedupe_gates(gates: list[Gate]) -> list[Gate]:
    seen: set[tuple] = set()
    out: list[Gate] = []
    for g in gates:
        key = (g.loc.path, g.loc.line, g.lhs, g.op, tuple(g.rhs))
        if key in seen:
            continue
        seen.add(key)
        out.append(g)
    return out
