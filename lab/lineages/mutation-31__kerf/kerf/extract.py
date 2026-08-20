from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from kerf.lex import (
    KIND_COLON,
    KIND_COMMA,
    KIND_DOT,
    KIND_IDENT,
    KIND_LBRACE,
    KIND_LBRACK,
    KIND_LPAREN,
    KIND_NUMBER,
    KIND_OP,
    KIND_OTHER,
    KIND_PIPE,
    KIND_RBRACE,
    KIND_RBRACK,
    KIND_RPAREN,
    KIND_STRING,
    Token,
    tokenize,
)
from kerf.walk import classify_ext

MIN_STR_LEN = 2
MAX_STR_LEN = 80

# Domain-edge labels — the enum analog of 0 / -1, not a typo class.
SENTINEL_STR = {
    "none",
    "null",
    "nil",
    "unknown",
    "unset",
    "undefined",
    "default",
    "invalid",
    "other",
    "missing",
    "empty",
    "unspecified",
    "na",
    "eof",
    "eol",
    "end",
    "init",
    "idle",
    "zero",
    "sentinel",
    "placeholder",
    "uninitialized",
    "uninit",
    "never-built",
    "never_built",
    "max",
    "min",
}

SENTINEL_NUM = {-1, 0}

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

# `unknown` is both a TS type and a sentinel enum member. Keep it as sentinel.
GENERIC_RHS_FOR_PRODUCER = GENERIC_RHS - {"unknown", "none", "nil", "default"}

EQ_OPS = {"==", "===", "!=", "!=="}
INEQ_OPS = {"<", ">", "<=", ">="}
RANGE_OPS = {"..<", "...", "..=", ".."}

ENUM_KW = {"enum"}
TYPE_KW = {"type"}
CASE_KW = {"case"}
SKIP_ENUM_MEMBERS = {
    "string",
    "int",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint",
    "float",
    "double",
    "bool",
    "boolean",
    "codable",
    "sendable",
    "equatable",
    "hashable",
    "comparable",
    "rawrepresentable",
    "caseiterable",
    "error",
    "decodable",
    "encodable",
    "identifiable",
    "copyable",
    "public",
    "private",
    "internal",
    "fileprivate",
    "static",
    "indirect",
    "mutating",
    "some",
    "any",
    "where",
    "protocol",
    "class",
    "struct",
    "func",
    "var",
    "let",
    "return",
    "if",
    "else",
    "switch",
    "for",
    "while",
    "break",
    "continue",
    "default",
    "self",
    "super",
    "true",
    "false",
    "override",
    "required",
    "convenience",
    "final",
    "open",
    "import",
    "from",
    "as",
    "in",
    "is",
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
    kind: str  # number | enum | string
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
    kind: str  # number | enum
    method: str | None = None
    raw: str = ""
    lo: int | float | None = None
    hi: int | float | None = None
    hi_inclusive: bool = False


@dataclass
class EnumDecl:
    name: str
    members: list[str]
    loc: Loc
    via: str = "enum"


@dataclass
class Corpus:
    producers: list[Producer] = field(default_factory=list)
    gates: list[Gate] = field(default_factory=list)
    enums: list[EnumDecl] = field(default_factory=list)
    files: int = 0
    skipped: int = 0


def extract_path(path: Path, root: Path | None = None) -> tuple[list[Gate], list[Producer], list[EnumDecl]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], [], []
    rel = _rel(path, root)
    role = classify_ext(path)
    suffix = path.suffix.lower()
    if suffix in {".json", ".jsonl"}:
        producers, enums = _extract_json(text, rel, suffix)
        return [], producers, enums
    if suffix in {".yaml", ".yml", ".toml"}:
        return [], _extract_simple_map(text, rel), []
    tokens = tokenize(text, suffix)
    enums = _enums_from_tokens(tokens, rel)
    producers = _producers_from_tokens(tokens, rel, enums)
    gates: list[Gate] = []
    if role == "source":
        gates = _gates_from_tokens(tokens, rel, enums)
    return gates, producers, enums


def extract_roots(paths: list[Path]) -> Corpus:
    from kerf.walk import iter_files

    corpus = Corpus()
    files = iter_files(paths)
    root = paths[0] if len(paths) == 1 else Path.cwd()
    for path in files:
        corpus.files += 1
        try:
            gates, producers, enums = extract_path(path, root)
        except Exception:
            corpus.skipped += 1
            continue
        corpus.gates.extend(gates)
        corpus.producers.extend(producers)
        corpus.enums.extend(enums)
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


def is_sentinel_str(value: str) -> bool:
    if not isinstance(value, str):
        return False
    leaf = value.split(".")[-1].split("/")[-1]
    return leaf.lower() in SENTINEL_STR


def is_sentinel_num(value: int | float) -> bool:
    return value in SENTINEL_NUM or value in {255, 256, 999, 9999, 65535}


def family_of(value: str) -> str | None:
    if not isinstance(value, str):
        return None
    if "." in value and re.match(r"^[A-Za-z][\w-]*\.", value):
        return value.split(".", 1)[0]
    if "/" in value and re.match(r"^[A-Za-z][\w-]+/", value):
        return value.split("/", 1)[0]
    return None


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


def _dotted_lhs(tokens: list[Token], idx: int) -> tuple[str, int]:
    parts = [str(tokens[idx].value)]
    k = idx
    while k >= 2 and tokens[k - 1].kind == KIND_DOT and tokens[k - 2].kind == KIND_IDENT:
        parts.append(str(tokens[k - 2].value))
        k -= 2
    parts.reverse()
    return ".".join(parts), k


def _dotted_forward(tokens: list[Token], idx: int) -> str:
    """Read a.b.c starting at tokens[idx] (an ident)."""
    if idx < 0 or idx >= len(tokens) or tokens[idx].kind != KIND_IDENT:
        return ""
    parts = [str(tokens[idx].value)]
    k = idx
    n = len(tokens)
    while k + 2 < n and tokens[k + 1].kind == KIND_DOT and tokens[k + 2].kind == KIND_IDENT:
        parts.append(str(tokens[k + 2].value))
        k += 2
    return ".".join(parts)


def _enum_decl_spans(tokens: list[Token]) -> list[tuple[int, int, str]]:
    """Brace ranges of `enum Name { ... }` / `class Name(Enum):` bodies."""
    spans: list[tuple[int, int, str]] = []
    n = len(tokens)
    i = 0
    while i < n:
        tok = tokens[i]
        if tok.kind == KIND_IDENT and str(tok.value).lower() in ENUM_KW and i + 1 < n:
            name, brace = _enum_name_and_brace(tokens, i + 1)
            if brace is not None:
                end = _matching_brace(tokens, brace)
                if end is not None:
                    spans.append((brace, end, name))
                    i = end + 1
                    continue
        if (
            tok.kind == KIND_IDENT
            and str(tok.value) == "class"
            and i + 4 < n
            and tokens[i + 1].kind == KIND_IDENT
            and tokens[i + 2].kind == KIND_LPAREN
            and tokens[i + 3].kind == KIND_IDENT
            and str(tokens[i + 3].value) in {"Enum", "IntEnum", "StrEnum", "Flag"}
        ):
            name = str(tokens[i + 1].value)
            # Python class body is indent-based; harvest until next top-ish class/def
            # by taking a window of tokens that assign strings.
            end = min(n - 1, i + 80)
            spans.append((i, end, name))
        i += 1
    return spans


def _enum_name_and_brace(tokens: list[Token], start: int) -> tuple[str, int | None]:
    n = len(tokens)
    i = start
    name = ""
    if i < n and tokens[i].kind == KIND_IDENT:
        name = str(tokens[i].value)
        i += 1
    depth_angle = 0
    while i < n:
        tok = tokens[i]
        if tok.kind == KIND_LBRACE:
            return name, i
        if tok.kind == KIND_OTHER and tok.value == "<":
            depth_angle += 1
        elif tok.kind == KIND_OTHER and tok.value == ">" and depth_angle:
            depth_angle -= 1
        elif tok.kind == KIND_OP and tok.value == "<":
            depth_angle += 1
        elif tok.kind == KIND_OP and tok.value == ">" and depth_angle:
            depth_angle -= 1
        i += 1
    return name, None


def _matching_brace(tokens: list[Token], brace_i: int) -> int | None:
    depth = 0
    for i in range(brace_i, len(tokens)):
        if tokens[i].kind == KIND_LBRACE:
            depth += 1
        elif tokens[i].kind == KIND_RBRACE:
            depth -= 1
            if depth == 0:
                return i
    return None


def _type_alias_spans(tokens: list[Token]) -> list[tuple[int, int, str]]:
    """Spans of `type Name = "a" | "b"` so the domain strings are not producers."""
    spans: list[tuple[int, int, str]] = []
    n = len(tokens)
    i = 0
    while i < n:
        tok = tokens[i]
        if tok.kind == KIND_IDENT and str(tok.value) in TYPE_KW and i + 1 < n:
            j = i + 1
            name = str(tokens[j].value) if tokens[j].kind == KIND_IDENT else "type"
            while j < n and not (
                tokens[j].kind == KIND_OTHER and tokens[j].value == "="
            ):
                j += 1
            if j < n and tokens[j].kind == KIND_OTHER and tokens[j].value == "=":
                members, end = _string_union(tokens, j + 1)
                if len(members) >= 2:
                    spans.append((j, end, name))
                    i = end
                    continue
        i += 1
    return spans


def _in_any_span(idx: int, spans: list[tuple[int, int, str]]) -> str | None:
    for a, b, name in spans:
        if a < idx < b:
            return name
    return None


def _enums_from_tokens(tokens: list[Token], rel: str) -> list[EnumDecl]:
    decls: list[EnumDecl] = []
    spans = _enum_decl_spans(tokens)
    for a, b, name in spans:
        members = _members_in_span(tokens, a, b)
        if len(members) >= 2:
            loc = Loc(rel, tokens[a].line, tokens[a].col)
            decls.append(EnumDecl(name=name or "enum", members=members, loc=loc, via="enum"))

    n = len(tokens)
    i = 0
    while i < n:
        tok = tokens[i]
        # type Name = "a" | "b" | "c"
        if tok.kind == KIND_IDENT and str(tok.value) in TYPE_KW and i + 3 < n:
            j = i + 1
            if tokens[j].kind != KIND_IDENT:
                i += 1
                continue
            name = str(tokens[j].value)
            j += 1
            while j < n and not (
                tokens[j].kind == KIND_OTHER and tokens[j].value == "="
            ) and tokens[j].kind != KIND_STRING:
                j += 1
            if j < n and tokens[j].kind == KIND_OTHER and tokens[j].value == "=":
                j += 1
            members, end = _string_union(tokens, j)
            if len(members) >= 2:
                decls.append(
                    EnumDecl(
                        name=name,
                        members=members,
                        loc=Loc(rel, tokens[i].line, tokens[i].col),
                        via="union",
                    )
                )
                i = end
                continue
        # const NAME = ["a", "b"] or NAME = ["a", "b"] as const
        if tok.kind == KIND_IDENT and i + 3 < n:
            maybe_name = str(tok.value)
            j = i + 1
            if str(tok.value) in {"const", "let", "var"} and tokens[j].kind == KIND_IDENT:
                maybe_name = str(tokens[j].value)
                j += 1
            if j < n and tokens[j].kind == KIND_OTHER and tokens[j].value == "=":
                j += 1
                if j < n and tokens[j].kind == KIND_LBRACK:
                    values, end = _collect_string_list(tokens, j + 1)
                    if len(values) >= 2 and all(is_vocab_string(v) for v in values):
                        decls.append(
                            EnumDecl(
                                name=maybe_name,
                                members=values,
                                loc=Loc(rel, tok.line, tok.col),
                                via="list",
                            )
                        )
                        i = end
                        continue
        i += 1
    return _dedupe_enums(decls)


def _members_in_span(tokens: list[Token], a: int, b: int) -> list[str]:
    members: list[str] = []
    seen: set[str] = set()
    i = a + 1
    used_case = any(
        tokens[k].kind == KIND_IDENT and str(tokens[k].value) == "case"
        for k in range(a, min(b, a + 40))
    )
    while i < b:
        tok = tokens[i]
        if tok.kind == KIND_IDENT and str(tok.value) == "case":
            i += 1
            while i < b:
                t = tokens[i]
                if t.kind == KIND_DOT and i + 1 < b and tokens[i + 1].kind == KIND_IDENT:
                    _push_member(members, seen, str(tokens[i + 1].value))
                    i += 2
                    continue
                if t.kind == KIND_IDENT:
                    val = str(t.value)
                    if val.lower() not in SKIP_ENUM_MEMBERS and val != "case":
                        _push_member(members, seen, val)
                    i += 1
                    continue
                if t.kind == KIND_STRING and isinstance(t.value, str):
                    _push_member(members, seen, t.value)
                    i += 1
                    continue
                if t.kind == KIND_COMMA:
                    i += 1
                    continue
                if t.kind in {KIND_LPAREN, KIND_OTHER} and t.value == "=":
                    # associated value / raw value — skip until comma or next case
                    i += 1
                    depth = 1 if t.kind == KIND_LPAREN else 0
                    while i < b:
                        if tokens[i].kind == KIND_LPAREN:
                            depth += 1
                        elif tokens[i].kind == KIND_RPAREN:
                            depth -= 1
                            if depth <= 0 and t.kind == KIND_LPAREN:
                                i += 1
                                break
                        elif tokens[i].kind == KIND_COMMA and depth <= 0:
                            break
                        elif (
                            tokens[i].kind == KIND_IDENT
                            and str(tokens[i].value) == "case"
                            and depth <= 0
                        ):
                            break
                        i += 1
                    continue
                break
            continue
        if not used_case and tok.kind == KIND_IDENT:
            val = str(tok.value)
            if val.lower() not in SKIP_ENUM_MEMBERS and not val.startswith("__"):
                _push_member(members, seen, val)
        if not used_case and tok.kind == KIND_STRING and isinstance(tok.value, str):
            _push_member(members, seen, tok.value)
        i += 1
    return members


def _push_member(members: list[str], seen: set[str], value: str) -> None:
    key = value
    if key in seen:
        return
    if not value or len(value) > 64:
        return
    seen.add(key)
    members.append(value)


def _string_union(tokens: list[Token], start: int) -> tuple[list[str], int]:
    values: list[str] = []
    i = start
    n = len(tokens)
    saw_pipe = False
    while i < n:
        tok = tokens[i]
        if tok.kind == KIND_STRING and isinstance(tok.value, str):
            values.append(tok.value)
            i += 1
            continue
        if tok.kind == KIND_PIPE:
            saw_pipe = True
            i += 1
            continue
        if tok.kind == KIND_OTHER and tok.value in {";", "=", ":"}:
            break
        if tok.kind in {KIND_RBRACE, KIND_COMMA} and values:
            break
        if tok.kind == KIND_IDENT and values:
            break
        if tok.kind == KIND_OP:
            break
        i += 1
        if i - start > 40:
            break
    if not saw_pipe and len(values) < 2:
        return [], start
    return values, i


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


def _gates_from_tokens(tokens: list[Token], rel: str, enums: list[EnumDecl]) -> list[Gate]:
    gates: list[Gate] = []
    spans = _enum_decl_spans(tokens)
    enum_members = _all_enum_members(enums)
    n = len(tokens)
    i = 0
    while i < n:
        tok = tokens[i]

        if (
            tok.kind == KIND_IDENT
            and str(tok.value).lower() == "typeof"
        ):
            i += 1
            continue

        if tok.kind == KIND_IDENT and str(tok.value) == "case":
            if _in_any_span(i, spans):
                i += 1
                continue
            gate = _case_gate(tokens, i, rel, enum_members)
            if gate:
                gates.append(gate)
            i += 1
            continue

        if tok.kind == KIND_OP and tok.value in EQ_OPS | INEQ_OPS:
            left = tokens[i - 1] if i > 0 else None
            right = tokens[i + 1] if i + 1 < n else None
            if left is not None and right is not None:
                gate = _cmp_gate(tokens, i, left, right, rel, enum_members)
                if gate:
                    gates.append(gate)
            i += 1
            continue

        if tok.kind == KIND_OP and tok.value in RANGE_OPS:
            gate = _range_gate(tokens, i, rel)
            if gate:
                gates.append(gate)
            i += 1
            continue

        if tok.kind == KIND_IDENT and str(tok.value) == "in":
            gate = _in_gate(tokens, i, rel, enum_members)
            if gate:
                gates.append(gate)
            i += 1
            continue

        if tok.kind == KIND_IDENT and str(tok.value) in {"matches", "matches!"}:
            gate = _matches_gate(tokens, i, rel, enum_members)
            if gate:
                gates.append(gate)
            i += 1
            continue

        i += 1
    return _dedupe_gates(gates)


def _all_enum_members(enums: list[EnumDecl]) -> set[str]:
    out: set[str] = set()
    for e in enums:
        out.update(e.members)
        out.update(m.lower() for m in e.members)
    return out


def _enumish_string(value: str, enum_members: set[str]) -> bool:
    if not is_vocab_string(value):
        return False
    if is_sentinel_str(value):
        return True
    if value in enum_members or value.lower() in enum_members:
        return True
    if family_of(value):
        return True
    return False


def _case_gate(
    tokens: list[Token], i: int, rel: str, enum_members: set[str]
) -> Gate | None:
    values: list[str] = []
    loc_line, loc_col = tokens[i].line, tokens[i].col
    j = i + 1
    n = len(tokens)
    while j < n:
        tok = tokens[j]
        if tok.kind == KIND_DOT and j + 1 < n and tokens[j + 1].kind == KIND_IDENT:
            values.append(str(tokens[j + 1].value))
            loc_line, loc_col = tokens[j + 1].line, tokens[j + 1].col
            j += 2
            continue
        if tok.kind == KIND_STRING and isinstance(tok.value, str):
            if _enumish_string(tok.value, enum_members):
                values.append(tok.value)
                loc_line, loc_col = tok.line, tok.col
            j += 1
            continue
        if tok.kind == KIND_IDENT and str(tok.value).lower() not in SKIP_ENUM_MEMBERS:
            # `case Idle:` rust-style inside a match — treat as enum if known/sentinel
            val = str(tok.value)
            if is_sentinel_str(val) or val in enum_members or val.lower() in enum_members:
                values.append(val)
                loc_line, loc_col = tok.line, tok.col
            j += 1
            continue
        if tok.kind == KIND_COMMA:
            j += 1
            continue
        break
    if not values:
        return None
    return Gate(
        lhs="case",
        field="case",
        op="in" if len(values) > 1 else "==",
        rhs=list(values),
        loc=Loc(rel, loc_line, loc_col),
        kind="enum",
        raw="case " + ", ".join(values),
    )


def _signed_number_at(tokens: list[Token], i: int) -> tuple[int | float, Token] | None:
    """Read a number at i, folding a preceding unary minus (`-1`, not `->`)."""
    if i < 0 or i >= len(tokens) or tokens[i].kind != KIND_NUMBER:
        return None
    tok = tokens[i]
    if not isinstance(tok.value, (int, float)) or isinstance(tok.value, bool):
        return None
    val: int | float = tok.value
    if i >= 1 and tokens[i - 1].kind == KIND_OTHER and tokens[i - 1].value == "-":
        val = -val
    return val, tok


def _cmp_gate(
    tokens: list[Token],
    op_i: int,
    left: Token,
    right: Token,
    rel: str,
    enum_members: set[str],
) -> Gate | None:
    op = str(tokens[op_i].value)
    lhs_tok: Token | None = None
    rhs_kind = None
    rhs_val: str | int | float | None = None
    rhs_raw = ""
    rhs_line = 0
    rhs_col = 0
    flipped = False

    def take_enum_rhs(dot_i: int) -> bool:
        nonlocal rhs_kind, rhs_val, rhs_raw, rhs_line, rhs_col
        if dot_i + 1 < len(tokens) and tokens[dot_i].kind == KIND_DOT and tokens[dot_i + 1].kind == KIND_IDENT:
            rhs_kind = "enum"
            rhs_val = str(tokens[dot_i + 1].value)
            rhs_raw = "." + str(rhs_val)
            rhs_line, rhs_col = tokens[dot_i + 1].line, tokens[dot_i + 1].col
            return True
        return False

    signed_right = None
    signed_left = None
    if right.kind == KIND_NUMBER:
        signed_right = _signed_number_at(tokens, op_i + 1)
    elif (
        right.kind == KIND_OTHER
        and right.value == "-"
        and op_i + 2 < len(tokens)
        and tokens[op_i + 2].kind == KIND_NUMBER
    ):
        signed_right = _signed_number_at(tokens, op_i + 2)
    if left.kind == KIND_NUMBER:
        signed_left = _signed_number_at(tokens, op_i - 1)
    elif (
        left.kind == KIND_OTHER
        and left.value == "-"
        and op_i >= 2
        and tokens[op_i - 2].kind == KIND_NUMBER
    ):
        signed_left = _signed_number_at(tokens, op_i - 2)

    if left.kind == KIND_IDENT and signed_right is not None:
        lhs_tok, rhs_kind, rhs_val = left, "number", signed_right[0]
        rhs_raw = ("-" if signed_right[0] < 0 else "") + signed_right[1].raw
        rhs_line, rhs_col = signed_right[1].line, signed_right[1].col
    elif right.kind == KIND_IDENT and signed_left is not None:
        lhs_tok, rhs_kind, rhs_val = right, "number", signed_left[0]
        rhs_raw = ("-" if signed_left[0] < 0 else "") + signed_left[1].raw
        rhs_line, rhs_col = signed_left[1].line, signed_left[1].col
        flipped = True
    elif left.kind == KIND_IDENT and right.kind == KIND_STRING:
        lhs_tok, rhs_kind, rhs_val = left, "enum", right.value
        rhs_raw, rhs_line, rhs_col = right.raw, right.line, right.col
    elif right.kind == KIND_IDENT and left.kind == KIND_STRING:
        lhs_tok, rhs_kind, rhs_val = right, "enum", left.value
        rhs_raw, rhs_line, rhs_col = left.raw, left.line, left.col
        flipped = True
    elif left.kind == KIND_IDENT and right.kind == KIND_DOT:
        if take_enum_rhs(op_i + 1):
            lhs_tok = left
    elif right.kind == KIND_IDENT and left.kind == KIND_DOT:
        if op_i >= 2 and take_enum_rhs(op_i - 2):
            lhs_tok = right
            flipped = True
    elif left.kind == KIND_IDENT and right.kind == KIND_IDENT:
        # Enum.Member or Phase.done on either side vs ident
        return None
    else:
        return None

    if lhs_tok is None or rhs_kind is None or rhs_val is None:
        return None

    if not flipped:
        lhs, _ = _dotted_lhs(tokens, op_i - 1)
        # `.foo` on the left of a flipped-less compare: lhs is the ident
        if tokens[op_i - 1].kind == KIND_DOT:
            return None
    else:
        if op_i + 1 < len(tokens) and tokens[op_i + 1].kind == KIND_IDENT:
            lhs, _ = _dotted_lhs(tokens, op_i + 1)
        else:
            lhs = str(lhs_tok.value)

    if rhs_kind == "number":
        if not isinstance(rhs_val, (int, float)) or isinstance(rhs_val, bool):
            return None
        kind = "number"
        rhs: list[str | int | float] = [rhs_val]
    else:
        if not isinstance(rhs_val, str) or not _enumish_string(rhs_val, enum_members):
            return None
        # drop generic type names unless they are sentinels
        if rhs_val.lower() in GENERIC_RHS and not is_sentinel_str(rhs_val):
            return None
        kind = "enum"
        rhs = [rhs_val]

    if flipped and op in INEQ_OPS:
        op = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}[op]

    return Gate(
        lhs=lhs,
        field=_field_of_lhs(lhs),
        op=op,
        rhs=rhs,
        loc=Loc(rel, rhs_line, rhs_col),
        kind=kind,
        raw=f"{lhs} {op} {rhs_raw}",
    )


def _range_gate(tokens: list[Token], op_i: int, rel: str) -> Gate | None:
    if op_i == 0 or op_i + 1 >= len(tokens):
        return None
    left, right = tokens[op_i - 1], tokens[op_i + 1]
    if left.kind != KIND_NUMBER or right.kind != KIND_NUMBER:
        return None
    if not isinstance(left.value, (int, float)) or not isinstance(right.value, (int, float)):
        return None
    op = str(tokens[op_i].value)
    hi_inclusive = op in {"...", "..="}
    lhs = _range_subject(tokens, op_i)
    return Gate(
        lhs=lhs,
        field=_field_of_lhs(lhs),
        op="range",
        rhs=[left.value, right.value],
        loc=Loc(rel, right.line, right.col),
        kind="number",
        raw=f"{lhs} in {left.raw}{op}{right.raw}",
        lo=left.value,
        hi=right.value,
        hi_inclusive=hi_inclusive,
    )


def _range_subject(tokens: list[Token], op_i: int) -> str:
    """Best-effort lhs for `lo..<hi` — `.contains(x)` argument or `x in`."""
    n = len(tokens)
    # (lo..<hi).contains(expr)
    j = op_i + 2
    if j < n and tokens[j].kind == KIND_RPAREN:
        j += 1
    if (
        j + 3 < n
        and tokens[j].kind == KIND_DOT
        and tokens[j + 1].kind == KIND_IDENT
        and str(tokens[j + 1].value).lower() == "contains"
        and tokens[j + 2].kind == KIND_LPAREN
        and tokens[j + 3].kind == KIND_IDENT
    ):
        lhs = _dotted_forward(tokens, j + 3)
        return lhs or "range"
    # expr in lo..<hi   /  expr in range(lo, hi)
    k = op_i - 1
    while k >= 0 and tokens[k].kind in {KIND_NUMBER, KIND_LPAREN}:
        k -= 1
    if k >= 0 and tokens[k].kind == KIND_IDENT and str(tokens[k].value) == "in" and k > 0:
        if tokens[k - 1].kind == KIND_IDENT:
            lhs, _ = _dotted_lhs(tokens, k - 1)
            return lhs
    return "range"


def _in_gate(
    tokens: list[Token], in_i: int, rel: str, enum_members: set[str]
) -> Gate | None:
    if in_i == 0 or tokens[in_i - 1].kind != KIND_IDENT:
        return None
    if in_i + 1 >= len(tokens):
        return None
    lhs, _ = _dotted_lhs(tokens, in_i - 1)
    nxt = tokens[in_i + 1]
    # Python range(lo, hi)
    if (
        nxt.kind == KIND_IDENT
        and str(nxt.value) == "range"
        and in_i + 4 < len(tokens)
        and tokens[in_i + 2].kind == KIND_LPAREN
        and tokens[in_i + 3].kind == KIND_NUMBER
    ):
        lo = tokens[in_i + 3].value
        hi_tok = None
        j = in_i + 4
        while j < len(tokens) and tokens[j].kind != KIND_RPAREN:
            if tokens[j].kind == KIND_NUMBER:
                hi_tok = tokens[j]
            j += 1
        if isinstance(lo, (int, float)) and hi_tok and isinstance(hi_tok.value, (int, float)):
            return Gate(
                lhs=lhs,
                field=_field_of_lhs(lhs),
                op="range",
                rhs=[lo, hi_tok.value],
                loc=Loc(rel, hi_tok.line, hi_tok.col),
                kind="number",
                raw=f"{lhs} in range({lo}, {hi_tok.value})",
                lo=lo,
                hi=hi_tok.value,
                hi_inclusive=False,
            )
        return None
    if nxt.kind not in {KIND_LPAREN, KIND_LBRACK}:
        return None
    values, _end = _collect_string_list(tokens, in_i + 2)
    values = [v for v in values if is_vocab_string(v)]
    if len(values) < 2 and not any(_enumish_string(v, enum_members) for v in values):
        return None
    if not values:
        return None
    loc_tok = tokens[in_i + 2] if in_i + 2 < len(tokens) else tokens[in_i]
    return Gate(
        lhs=lhs,
        field=_field_of_lhs(lhs),
        op="in",
        rhs=list(values),
        loc=Loc(rel, loc_tok.line, loc_tok.col),
        kind="enum",
        raw=f"{lhs} in {values!r}",
    )


def _matches_gate(
    tokens: list[Token], i: int, rel: str, enum_members: set[str]
) -> Gate | None:
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
            if _enumish_string(tokens[j].value, enum_members):
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
        kind="enum",
        raw=f"matches!({lhs}, {values!r})",
    )


def _producers_from_tokens(
    tokens: list[Token], rel: str, enums: list[EnumDecl]
) -> list[Producer]:
    n = len(tokens)
    spans = _enum_decl_spans(tokens)
    gate_spans: set[int] = set()
    for i, tok in enumerate(tokens):
        if tok.kind == KIND_OP and tok.value in EQ_OPS | INEQ_OPS:
            if i + 1 < n and tokens[i + 1].kind in {KIND_STRING, KIND_NUMBER}:
                gate_spans.add(i + 1)
            if (
                i + 2 < n
                and tokens[i + 1].kind == KIND_OTHER
                and tokens[i + 1].value == "-"
                and tokens[i + 2].kind == KIND_NUMBER
            ):
                gate_spans.add(i + 2)
            if i > 0 and tokens[i - 1].kind in {KIND_STRING, KIND_NUMBER}:
                gate_spans.add(i - 1)
            # `.ident` rhs
            if i + 2 < n and tokens[i + 1].kind == KIND_DOT and tokens[i + 2].kind == KIND_IDENT:
                gate_spans.add(i + 2)
            if i >= 2 and tokens[i - 1].kind == KIND_IDENT and tokens[i - 2].kind == KIND_DOT:
                gate_spans.add(i - 1)
        if tok.kind == KIND_OP and tok.value in RANGE_OPS:
            if i > 0 and tokens[i - 1].kind == KIND_NUMBER:
                gate_spans.add(i - 1)
            if i + 1 < n and tokens[i + 1].kind == KIND_NUMBER:
                gate_spans.add(i + 1)
        if tok.kind == KIND_IDENT and str(tok.value) == "case":
            if _in_any_span(i, spans):
                continue
            j = i + 1
            while j < n:
                if tokens[j].kind == KIND_DOT and j + 1 < n and tokens[j + 1].kind == KIND_IDENT:
                    gate_spans.add(j + 1)
                    j += 2
                    continue
                if tokens[j].kind == KIND_STRING:
                    gate_spans.add(j)
                    j += 1
                    continue
                if tokens[j].kind == KIND_COMMA:
                    j += 1
                    continue
                break
        if tok.kind == KIND_IDENT and str(tok.value).lower() == "typeof":
            if i + 3 < n and tokens[i + 3].kind == KIND_STRING:
                gate_spans.add(i + 3)

    enum_members = _all_enum_members(enums)
    domain = list(spans) + _type_alias_spans(tokens)
    producers: list[Producer] = []
    for i, tok in enumerate(tokens):
        if i in gate_spans:
            continue
        field = _producer_field(tokens, i)
        if tok.kind == KIND_NUMBER and isinstance(tok.value, (int, float)) and not isinstance(tok.value, bool):
            signed = _signed_number_at(tokens, i)
            value = signed[0] if signed else tok.value
            producers.append(
                Producer(value=value, kind="number", loc=Loc(rel, tok.line, tok.col), field=field)
            )
            continue
        if tok.kind == KIND_STRING and isinstance(tok.value, str):
            if _in_any_span(i, domain):
                continue
            if is_vocab_string(tok.value) and tok.value.lower() not in GENERIC_RHS_FOR_PRODUCER:
                kind = "enum" if _enumish_string(tok.value, enum_members) else "string"
                producers.append(
                    Producer(
                        value=tok.value,
                        kind=kind,
                        loc=Loc(rel, tok.line, tok.col),
                        field=field,
                    )
                )
            continue
        # `.ident` constructions (not enum-decl members, not gate rhs)
        if (
            tok.kind == KIND_DOT
            and i + 1 < n
            and tokens[i + 1].kind == KIND_IDENT
            and (i + 1) not in gate_spans
        ):
            if _in_any_span(i, spans):
                continue
            name = str(tokens[i + 1].value)
            if name.lower() in SKIP_ENUM_MEMBERS:
                continue
            # skip dotted method calls: .contains( .count  .lowercased
            if i + 2 < n and tokens[i + 2].kind == KIND_LPAREN:
                continue
            producers.append(
                Producer(
                    value=name,
                    kind="enum",
                    loc=Loc(rel, tokens[i + 1].line, tokens[i + 1].col),
                    field=field or _enum_field_hint(tokens, i, spans),
                    via="case",
                )
            )
            continue
        # EnumName.member
        if (
            tok.kind == KIND_IDENT
            and i + 2 < n
            and tokens[i + 1].kind == KIND_DOT
            and tokens[i + 2].kind == KIND_IDENT
            and (i + 2) not in gate_spans
        ):
            head = str(tok.value)
            tail = str(tokens[i + 2].value)
            if tail.lower() in SKIP_ENUM_MEMBERS:
                continue
            if i + 3 < n and tokens[i + 3].kind == KIND_LPAREN:
                # Type.method( — not a case unless enum associated value
                if any(e.name == head for e in enums):
                    producers.append(
                        Producer(
                            value=tail,
                            kind="enum",
                            loc=Loc(rel, tokens[i + 2].line, tokens[i + 2].col),
                            field=head,
                            via="enum-path",
                        )
                    )
                continue
            if any(e.name == head for e in enums) or (
                head[:1].isupper()
                and head.lower() not in SKIP_ENUM_MEMBERS
                and (tail in enum_members or tail.lower() in enum_members)
            ):
                producers.append(
                    Producer(
                        value=tail,
                        kind="enum",
                        loc=Loc(rel, tokens[i + 2].line, tokens[i + 2].col),
                        field=head,
                        via="enum-path",
                    )
                )
    return producers


def _enum_field_hint(
    tokens: list[Token], dot_i: int, spans: list[tuple[int, int, str]]
) -> str | None:
    # status: .unknown  or  status = .unknown
    if dot_i >= 2 and tokens[dot_i - 1].kind == KIND_COLON and tokens[dot_i - 2].kind == KIND_IDENT:
        return str(tokens[dot_i - 2].value)
    if (
        dot_i >= 2
        and tokens[dot_i - 1].kind == KIND_OTHER
        and tokens[dot_i - 1].value == "="
        and tokens[dot_i - 2].kind == KIND_IDENT
    ):
        return str(tokens[dot_i - 2].value)
    return None


def _producer_field(tokens: list[Token], i: int) -> str | None:
    if i >= 2 and tokens[i - 1].kind == KIND_COLON and tokens[i - 2].kind in {KIND_IDENT, KIND_STRING}:
        return str(tokens[i - 2].value)
    if i >= 2 and tokens[i - 1].kind == KIND_OP and tokens[i - 1].value in EQ_OPS:
        return None
    if i >= 2 and tokens[i - 2].kind == KIND_IDENT and tokens[i - 1].kind == KIND_OTHER:
        if tokens[i - 1].value == "=":
            return str(tokens[i - 2].value)
    return None


def _extract_json(text: str, rel: str, suffix: str) -> tuple[list[Producer], list[EnumDecl]]:
    producers: list[Producer] = []
    enums: list[EnumDecl] = []
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
            _walk_json(data, rel, padded, None, producers, enums)
        return producers, enums
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return _extract_simple_map(text, rel), []
    _walk_json(data, rel, text, None, producers, enums)
    return producers, enums


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
    node: object,
    rel: str,
    text: str,
    field: str | None,
    out: list[Producer],
    enums: list[EnumDecl],
) -> None:
    if isinstance(node, dict):
        if "enum" in node and isinstance(node["enum"], list):
            members = [str(x) for x in node["enum"] if isinstance(x, str) and is_vocab_string(x)]
            if len(members) >= 2:
                line = _line_of_json_value(text, members[0])
                enums.append(
                    EnumDecl(
                        name=str(field or "enum"),
                        members=members,
                        loc=Loc(rel, line, 1),
                        via="json-schema",
                    )
                )
        for key, val in node.items():
            _walk_json(val, rel, text, str(key), out, enums)
        return
    if isinstance(node, list):
        for item in node:
            _walk_json(item, rel, text, field, out, enums)
        return
    line = _line_of_json_value(text, node)
    if isinstance(node, str) and is_vocab_string(node) and node.lower() not in GENERIC_RHS_FOR_PRODUCER:
        kind = "enum" if is_sentinel_str(node) or family_of(node) else "string"
        out.append(Producer(value=node, kind=kind, loc=Loc(rel, line, 1), field=field, via="json"))
        return
    if isinstance(node, (int, float)) and not isinstance(node, bool):
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
        if s is not None and is_vocab_string(s) and s.lower() not in GENERIC_RHS_FOR_PRODUCER:
            producers.append(
                Producer(value=s, kind="enum" if is_sentinel_str(s) else "string", loc=Loc(rel, lineno, 1), field=field, via="map")
            )
        elif num is not None:
            value: int | float = float(num) if "." in num else int(num)
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


def _dedupe_enums(enums: list[EnumDecl]) -> list[EnumDecl]:
    seen: set[tuple] = set()
    out: list[EnumDecl] = []
    for e in enums:
        key = (e.name, tuple(e.members))
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out
