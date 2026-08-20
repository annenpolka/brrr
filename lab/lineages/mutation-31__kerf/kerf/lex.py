from __future__ import annotations

from dataclasses import dataclass

KIND_STRING = "string"
KIND_NUMBER = "number"
KIND_IDENT = "ident"
KIND_OP = "op"
KIND_DOT = "dot"
KIND_LPAREN = "lparen"
KIND_RPAREN = "rparen"
KIND_LBRACK = "lbrack"
KIND_RBRACK = "rbrack"
KIND_LBRACE = "lbrace"
KIND_RBRACE = "rbrace"
KIND_COMMA = "comma"
KIND_COLON = "colon"
KIND_PIPE = "pipe"
KIND_OTHER = "other"

OPS = (
    "===",
    "!==",
    "==",
    "!=",
    "<=",
    ">=",
    "=~",
    "~=",
    "...",
    "..=",
    "..<",
    "..",
)

HASH_COMMENT_EXTS = {".py", ".rb", ".yaml", ".yml", ".toml", ".sh"}
C_COMMENT_EXTS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".rs",
    ".go",
    ".swift",
    ".java",
    ".kt",
    ".kts",
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".hpp",
    ".cs",
    ".m",
    ".mm",
    ".scala",
    ".php",
    ".zig",
    ".pkl",
    ".mbt",
    ".lua",
}
TEMPLATE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}


@dataclass(frozen=True)
class Token:
    kind: str
    value: str | int | float | None
    raw: str
    line: int
    col: int
    end: int


def comment_style(path_suffix: str) -> str:
    ext = path_suffix.lower()
    if ext in HASH_COMMENT_EXTS:
        return "hash"
    if ext in C_COMMENT_EXTS:
        return "c"
    if ext in {".json", ".jsonl"}:
        return "none"
    return "c"


def tokenize(text: str, suffix: str) -> list[Token]:
    style = comment_style(suffix)
    ext = suffix.lower()
    pyish = ext == ".py"
    rust = ext == ".rs"
    swift = ext == ".swift"
    allow_template = ext in TEMPLATE_EXTS
    tokens: list[Token] = []
    n = len(text)
    i = 0
    line = 1
    col = 1
    # 0 = inside template text; >0 = brace depth of current ${} interpolation
    template_stack: list[int] = []

    def bump(ch: str) -> None:
        nonlocal line, col, i
        i += 1
        if ch == "\n":
            line += 1
            col = 1
        else:
            col += 1

    def slice_bump(end: int) -> str:
        nonlocal line, col, i
        chunk = text[i:end]
        for ch in chunk:
            if ch == "\n":
                line += 1
                col = 1
            else:
                col += 1
        i = end
        return chunk

    def in_template_text() -> bool:
        return bool(template_stack) and template_stack[-1] == 0

    while i < n:
        ch = text[i]
        start_line, start_col = line, col

        if in_template_text():
            if ch == "\\" and i + 1 < n:
                bump(ch)
                bump(text[i])
                continue
            if ch == "`":
                bump(ch)
                template_stack.pop()
                continue
            if ch == "$" and i + 1 < n and text[i + 1] == "{":
                bump("$")
                bump("{")
                template_stack[-1] = 1
                continue
            bump(ch)
            continue

        if ch in " \t\r\n":
            bump(ch)
            continue

        if style == "hash" and ch == "#":
            while i < n and text[i] != "\n":
                bump(text[i])
            continue

        if style == "c" and ch == "/" and i + 1 < n:
            nxt = text[i + 1]
            if nxt == "/":
                while i < n and text[i] != "\n":
                    bump(text[i])
                continue
            if nxt == "*":
                bump(ch)
                bump(nxt)
                while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                    bump(text[i])
                if i + 1 < n:
                    bump(text[i])
                    bump(text[i])
                continue

        if rust and ch == "'" and not _is_rust_char_literal(text, i):
            bump(ch)
            continue

        if swift and ch == "#":
            hashes = 0
            while i + hashes < n and text[i + hashes] == "#":
                hashes += 1
            if i + hashes < n and text[i + hashes] == '"':
                tok = _scan_swift_raw(text, i, line, col, hashes)
                if tok is not None:
                    token, new_i, new_line, new_col = tok
                    i, line, col = new_i, new_line, new_col
                    tokens.append(token)
                    continue

        if ch in "'\"" or (
            pyish
            and ch in "rRuUfFbB"
            and i + 1 < n
            and (
                text[i + 1] in "'\""
                or (
                    i + 2 < n
                    and text[i + 1] in "rRuUfFbB"
                    and text[i + 2] in "'\""
                )
            )
        ):
            tok = _scan_string(text, i, line, col, pyish)
            if tok is None:
                bump(ch)
                continue
            token, new_i, new_line, new_col = tok
            i, line, col = new_i, new_line, new_col
            tokens.append(token)
            continue

        if allow_template and ch == "`":
            bump(ch)
            template_stack.append(0)
            continue

        if ch.isdigit() or (ch == "." and i + 1 < n and text[i + 1].isdigit()):
            token, new_i, new_line, new_col = _scan_number(text, i, line, col)
            i, line, col = new_i, new_line, new_col
            tokens.append(token)
            continue

        if ch.isalpha() or ch == "_" or ch == "$":
            j = i + 1
            while j < n and (text[j].isalnum() or text[j] in "_$"):
                j += 1
            raw = slice_bump(j)
            tokens.append(Token(KIND_IDENT, raw, raw, start_line, start_col, i))
            continue

        matched_op = None
        for op in OPS:
            if text.startswith(op, i):
                matched_op = op
                break
        if matched_op is None and ch in "<>":
            matched_op = ch
        if matched_op is not None:
            slice_bump(i + len(matched_op))
            tokens.append(
                Token(KIND_OP, matched_op, matched_op, start_line, start_col, i)
            )
            continue

        kind_map = {
            ".": KIND_DOT,
            "(": KIND_LPAREN,
            ")": KIND_RPAREN,
            "[": KIND_LBRACK,
            "]": KIND_RBRACK,
            "{": KIND_LBRACE,
            "}": KIND_RBRACE,
            ",": KIND_COMMA,
            ":": KIND_COLON,
            "|": KIND_PIPE,
        }
        bump(ch)
        if ch == "{" and template_stack and template_stack[-1] > 0:
            template_stack[-1] += 1
        elif ch == "}" and template_stack and template_stack[-1] > 0:
            template_stack[-1] -= 1
        tokens.append(
            Token(kind_map.get(ch, KIND_OTHER), ch, ch, start_line, start_col, i)
        )

    return tokens


def _scan_swift_raw(
    text: str, i: int, line: int, col: int, hashes: int
) -> tuple[Token, int, int, int] | None:
    start_i, start_line, start_col = i, line, col
    n = len(text)
    # consume #+"
    i += hashes + 1
    col += hashes + 1
    close = '"' + ("#" * hashes)
    parts: list[str] = []
    while i < n:
        if text.startswith(close, i):
            i += len(close)
            col += len(close)
            value = "".join(parts)
            token = Token(KIND_STRING, value, text[start_i:i], start_line, start_col, i)
            return token, i, line, col
        ch = text[i]
        parts.append(ch)
        i += 1
        if ch == "\n":
            line += 1
            col = 1
        else:
            col += 1
    return None


def _is_rust_char_literal(text: str, i: int) -> bool:
    """True for 'x' or '\\n' / '\\x1b'; false for lifetimes 'a, 'static, '_."""
    n = len(text)
    if i + 1 >= n:
        return False
    nxt = text[i + 1]
    if nxt == "\\":
        return True
    if i + 2 < n and text[i + 2] == "'":
        return True
    return False


def _scan_string(
    text: str, i: int, line: int, col: int, pyish: bool
) -> tuple[Token, int, int, int] | None:
    start_i, start_line, start_col = i, line, col
    n = len(text)
    prefix = ""
    while i < n and text[i] in "rRuUfFbB":
        prefix += text[i]
        i += 1
        col += 1
    if i >= n or text[i] not in "'\"":
        return None
    quote = text[i]
    i += 1
    col += 1
    triple = False
    if pyish and i + 1 < n and text[i] == quote and text[i + 1] == quote:
        triple = True
        i += 2
        col += 2
    raw_parts: list[str] = []
    interpolated = "f" in prefix.lower()
    rawish = "r" in prefix.lower()
    while i < n:
        ch = text[i]
        if not triple and ch == "\n":
            return None
        if triple and text.startswith(quote * 3, i):
            i += 3
            col += 3
            break
        if not triple and ch == quote:
            i += 1
            col += 1
            break
        if not rawish and ch == "\\" and i + 1 < n:
            got, ni, line, col = _take_escape(text, i + 1, line, col)
            raw_parts.append(got)
            i = ni
            continue
        if interpolated and ch == "{":
            return None
        raw_parts.append(ch)
        i += 1
        if ch == "\n":
            line += 1
            col = 1
        else:
            col += 1
    else:
        return None
    value = "".join(raw_parts)
    token = Token(KIND_STRING, value, text[start_i:i], start_line, start_col, i)
    return token, i, line, col


def _take_escape(text: str, i: int, line: int, col: int) -> tuple[str, int, int, int]:
    """i points at the character after backslash."""
    n = len(text)
    ch = text[i]
    if ch == "x" and i + 2 < n and _is_hex(text[i + 1 : i + 3]):
        return chr(int(text[i + 1 : i + 3], 16)), i + 3, line, col + 3
    if ch == "u" and i + 1 < n and text[i + 1] == "{":
        j = i + 2
        while j < n and text[j] != "}" and _is_hex(text[j]):
            j += 1
        if j < n and text[j] == "}" and j > i + 2:
            try:
                return chr(int(text[i + 2 : j], 16)), j + 1, line, col + (j + 1 - i)
            except ValueError:
                pass
    if ch == "u" and i + 4 < n and _is_hex(text[i + 1 : i + 5]):
        try:
            return chr(int(text[i + 1 : i + 5], 16)), i + 5, line, col + 5
        except ValueError:
            pass
    mapped = {
        "n": "\n",
        "t": "\t",
        "r": "\r",
        "0": "\0",
        "\\": "\\",
        "'": "'",
        '"': '"',
        "`": "`",
    }.get(ch, ch)
    if ch == "\n":
        return mapped, i + 1, line + 1, 1
    return mapped, i + 1, line, col + 2


def _is_hex(s: str) -> bool:
    return bool(s) and all(c in "0123456789abcdefABCDEF" for c in s)


def _scan_number(text: str, i: int, line: int, col: int) -> tuple[Token, int, int, int]:
    start_i, start_line, start_col = i, line, col
    n = len(text)
    j = i
    if text.startswith("0x", j) or text.startswith("0X", j):
        j += 2
        while j < n and text[j] in "0123456789abcdefABCDEF_":
            j += 1
        raw = text[start_i:j]
        try:
            value: int | float = int(raw.replace("_", ""), 16)
        except ValueError:
            value = 0
        col += len(raw)
        return Token(KIND_NUMBER, value, raw, start_line, start_col, j), j, line, col

    while j < n and (text[j].isdigit() or text[j] == "_"):
        j += 1
    if j < n and text[j] == ".":
        k = j + 1
        if k < n and text[k].isdigit():
            j = k
            while j < n and (text[j].isdigit() or text[j] == "_"):
                j += 1
    if j < n and text[j] in "eE":
        k = j + 1
        if k < n and text[k] in "+-":
            k += 1
        if k < n and text[k].isdigit():
            j = k
            while j < n and (text[j].isdigit() or text[j] == "_"):
                j += 1
    raw = text[start_i:j]
    cleaned = raw.replace("_", "")
    try:
        if any(c in cleaned for c in ".eE"):
            num: int | float = float(cleaned)
        else:
            num = int(cleaned)
    except ValueError:
        num = 0
    col += len(raw)
    return Token(KIND_NUMBER, num, raw, start_line, start_col, j), j, line, col
