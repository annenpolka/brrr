# reimpl-04 — whence

## Primitive

Path-condition at a source locus: given `file:line` (or a diff, or grep output), emit the nested predicates still in force — *whence this line runs* — including fallthrough `given` frames from early-return guard clauses.

The object is a **condition stack**, not a function name and not a hunk window. Rebuilt from observed CLI behavior of `when` (candidate-20) without reading its implementation.

## Why this might not exist

Reviewers reconstruct enclosing `if` / `try` / `match` / `guard` by scrolling. `git diff -W` and `diff -p` only name the function. Unified hunks are line-windows; the `if` that makes a change legal is often 40 lines above the `@@` header. Debuggers answer "when" dynamically. Nothing answers it statically as a Unix pipe.

Rebuilding from the outside tests whether the primitive is real or an accident of one implementation. The gold check is kizu `src/git/parse.rs:60`: four early-return guards, four `given` frames.

## How to run

```bash
./whence fixtures/nested.py:13 --explain
./whence --diff fixtures/sample.diff --group
printf '13:return\n' | ./whence fixtures/nested.py --tsv
./whence /Users/annenpolka/ghq/github.com/annenpolka/kizu/src/git/parse.rs:60 --explain
./demo.sh
```

Python 3.10+, stdlib only. `./whence` is the CLI.

## Empirical transcript

### Before the improvement (this first commit)

Python on `fixtures/nested.py:13` matches the ancestor:

```
in     delete_user(user, db, audit)
given  user is not None  (L5)
if     user.locked  (L8)
try      (L9)
if     user.role == 'admin'  (L11)
if     not user.can_delete  (L12)
here   return "denied"
```

`fixtures/guards.rs:11` emits three fallthrough givens (quoted-form, length, `a/` prefix).

kizu `src/git/parse.rs:60` (`let b_side = ...`) — the required four-given stack:

```
in     parse_diff_git_header(rest:&str)-> Option<PathBuf>
given  ¬(len<5+ 2)  (L43)
given  inner.is_multiple_of(2)  (L47)
given  bytes.starts_with(b"a/")  (L51)
given  bytes.get(b_prefix_start..b_prefix_start+ 3)== Some(b" b/")  (L57)
here   let b_side = &bytes[b_prefix_start + 3..];
engine braces  depth=5
```

Side-by-side with the original `when` binary on every line of the five fixtures plus parse.rs:60 / :34 / diff.rs:51 / sitbone PresenceArbiter.swift:81: **133/133 explain records identical**. The original source was never opened.

`rg -n 'return None;' parse.rs | ./whence parse.rs --tsv` emits one row per return, each with its own stack.

`./demo.sh` exits 0.

### After the improvement (v0.2)

Four-given stack on parse.rs:60 is unchanged (still the required gold). Two brace-engine holes closed:

`fixtures/sample.rs:16` now keeps `if let` and names the match arm:

```
in     diff_single_file(...)
if     raw.is_empty()
match  classify(root,rel)
arm    Kind::Untracked
if     let Ok(text)= synthesize(root,rel)
here   return Ok(text);
```

Before, the arm pred was empty and `let` was dropped (`if Ok(text)= …`). The pattern is the thing a reviewer points at; an empty `arm` was the ancestor's own listed failure.

`./whence kizu/src/git/parse.rs:60 --explain` still prints exactly four givens. `./demo.sh` exits 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `kizu/src/git/parse.rs:60` | four early-return givens (required) |
| `kizu/src/git/diff.rs:51` | `given success` + `given raw.is_empty()` |
| `skills/.../validate_execplan.py:102` | nested if + Japanese string + exists-guard |
| `sitbone/.../PresenceArbiter.swift:81` | Swift `guard isEnabled` |
| `fixtures/nested.py`, `guards.rs`, `sample.swift`, `sample.rs`, `contradict.py` | adversarial nesting |

Read-only on the real repos. Ugly fixtures live in `fixtures/`.

## Surprises

- The valuable "whence" on real Rust is **not** the nested `if`. It is the **negation of the last four early returns**. Guard-clause style makes `git diff -W` almost useless.
- Simple-exit detection must refuse a nested `if` (the quoted-path block at parse.rs:25) or line 60 grows a fifth, wrong, `given`.
- Givens have to live at *parent* brace depth. Storing them at the closed `if`'s depth makes the next sibling `if` pop them.
- Python `given` attaches to later *compound* statements, not to a trailing `return` after an if/elif/else chain (nested.py:45). Brace `given` attaches to every later line in the scope. Two engines, one noun.

## Failures

1. **Nested-but-total early returns.** parse.rs quoted-path `if bytes.starts_with(b"\"a/") { ... return Some }` is not turned into `given ¬(quoted form)` at line 60. Same conservative miss as the ancestor.
2. **Token spacing.** `len<5+ 2` instead of `len < 5 + 2`.
3. **`if let` pred drops `let`.** `if Ok(text)= synthesize(...)`.
4. **Match arm predicates** are often empty (`arm` with no pattern text) unless the arm is a Swift `case`.
5. **`--diff` of an unapplied patch** maps `+` lines onto the current file, not the post-image.

## Suggested mutations

- Overlay an unapplied patch in memory so `--diff` is the post-image.
- Infer `given ¬(P)` for fully-exiting *nested* ifs (the quoted-form miss).
- `whence --same-as file:line` — other lines that share the stack.
- Keep `if let` and fill match-arm patterns.

## Kill / keep

**Keep.** The object (path-condition + fallthrough `given`) survived a clean-room rebuild and still names the four predicates that make parse.rs:60 legal. Kill only if a later generation reduces it to "print the enclosing function."
