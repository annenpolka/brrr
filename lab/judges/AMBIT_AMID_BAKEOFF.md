# mutation-35 bakeoff: ambit vs amid (empirical)

Source: critic `01a01b79-1122-7763-af84-15c9e32df439` 2026-08-20 04:27 JST.
Two independent mutation-35s of the same object: **under as a file stream** (`rg | tool`). Same pipes on kizu `src/git/parse.rs`. No third clone.

## Binaries

| Tool | Worktree | HEAD | Demo |
| --- | --- | --- | --- |
| ambit | `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b56-ac5a-7b03-a99f-434e97f8bd56` | `03ca991` *Recover the scanned file from rg LINE:text pins.* (parent `460c0fa`) | `./demo.sh` **rc=0** (24 tests + kizu `parse.rs`) |
| amid | `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/mutation-35-amid` | `81106a6` *Teach amid to take the file and the predicate from locators.* (parent `fc9a60c`) | `./demo.sh` **rc=0** (29 tests, fixtures only — no kizu slice) |

Both refuse a cwd walk (`./tool 'user.locked'` → rc=2). Neither is a tree walker by default.

Kizu object: `/Users/annenpolka/ghq/github.com/annenpolka/kizu/src/git/parse.rs`.
Heretic invert of `when parse.rs:60` is `let b_side` under `given bytes.starts_with(b"a/")`. That line is **not** in any of the rg streams below.

## Battery

3/3 = the three named pipes, run from `kizu/` unless noted.

`rg -n 'return None;' src/git/parse.rs` **is** single-file LINE:text (rg omits the path). Pipe 1 and pipe 3 are the same producer.

| Tool | `rg -n 'return None;'` | `rg --json starts_with` | LINE:text (in-repo) | Score |
| --- | --- | --- | --- | --- |
| **ambit** | rc=0, `let b_side`, `here Some(bytes_to_path(a_side))` | rc=2, no JSON parser | rc=0 (pin recovery) | **2/3** |
| amid | rc=2, refuse | rc=0, derive+peel, `let b_side`, `here }` | rc=2, refuse | **1/3** |

## Pipe 1 — `rg -n 'return None;'`

Raw rg (cwd = kizu):

```
34:            return None;
44:        return None;
48:        return None;
52:        return None;
58:        return None;
62:        return None;
77:        return None;
104:                        return None;
108:                        return None;
```

```
$ cd kizu && rg -n 'return None;' src/git/parse.rs | ./ambit --kind given 'a/' --explain
# rc=0
…/kizu/src/git/parse.rs:59-60
  match  given bytes.starts_with(b"a/")
  in     parse_diff_git_header(rest:&str)-> Option<PathBuf>
  given  ¬(len<5+ 2)  (L43)
  given  inner.is_multiple_of(2)  (L47)
  given  bytes.starts_with(b"a/")  (L51)←
  given  bytes.get(b_prefix_start..b_prefix_start+ 3)== Some(b" b/")  (L57)
  here   let b_side = &bytes[b_prefix_start + 3..];

…/kizu/src/git/parse.rs:63-65
  …
  given  a_side== b_side  (L61)
  here   Some(bytes_to_path(a_side))
```

Five spans: `let a_side` / `return None` (L58) / `let b_side` / `return None` (L62) / `Some(bytes_to_path(a_side))`. rg never printed L60 or L64.

```
$ cd kizu && rg -n 'return None;' src/git/parse.rs | ./amid --kind given 'a/' --explain
# rc=2
amid: locators are LINE:text with no file (rg FILE omits the name).
Pass the FILE, or use rg -nH / rg --json.
```

## Pipe 2 — `rg --json starts_with`

Raw rg match lines (cwd = kizu): L25 `b"\"a/"`, L33 `b"b/"`, L51 `b"a/"`, L184 Binary files, L191 new file mode, L198 deleted file mode. Path always present.

```
$ cd kizu && rg --json starts_with src/git/parse.rs | ./ambit --kind given --explain
# rc=2
ambit: name a predicate snippet (or --same-as FILE:LINE)

$ cd kizu && rg --json starts_with src/git/parse.rs | ./ambit --kind given 'a/' --explain
# rc=2
ambit: stdin is not a diff or file:line stream
(pass FILE after the predicate, or rg -nH / rg -l)
```

```
$ cd kizu && rg --json starts_with src/git/parse.rs | ./amid --kind given --explain
# rc=0  (no snippet typed; peel !P on the if-line)
src/git/parse.rs:35-37
  match  given b_decoded.starts_with(b"b/")
  here   return Some(bytes_to_path(&b_decoded[2..]));

src/git/parse.rs:59-60
  match  given bytes.starts_with(b"a/")
  …
  here   let b_side = &bytes[b_prefix_start + 3..];

src/git/parse.rs:63-65
  …
  here   }
```

`--kind given` drops the Binary/mode arms. Derive also emits the quoted-form `b/` survivor that `--kind given 'a/'` never asks for. Same command with snippet `'a/'` is the four unquoted spans only; last `here` is still `}`.

## Pipe 3 — single-file LINE:text

`cd kizu/src/git && rg -n 'return None;' parse.rs` is byte-identical to pipe 1 (nine `LINE:text` rows, no path).

| cwd / flags | ambit | amid |
| --- | --- | --- |
| `kizu/` or `kizu/src/git` (in-repo pins) | rc=0, recovers `parse.rs`, same five spans, `here Some(...)` | rc=2, refuse |
| LINE:text + FILE operand `parse.rs` | rc=0 | rc=0, same spans, `here }` |
| `rg -nH` (file named) | rc=0, `here Some(...)` | rc=0, `here }` |
| from ambit/amid worktree, abs `parse.rs`, no `--repo` | rc=2 *unique match in this git tree* | rc=2 *LINE:text with no file* |
| same + `--repo $KIZU` | rc=0 | rc=2 (`--repo` is unused for pin recovery; amid will not walk names) |

## Scan vs filter (same stream, file named)

```
$ cd kizu && rg -nH 'return None;' src/git/parse.rs | ./ambit --kind given 'a/' --hits --tsv
$ cd kizu && rg -nH 'return None;' src/git/parse.rs | ./amid  --kind given 'a/' --pin  --tsv
# both rc=0; both keep only L58 and L62
```

Expansion (no `--hits`/`--pin`) is `let b_side`. Filter is the two returns that sit under `given a/`. The flip is real on both, once the file is known.

`--hits` / `--pin` from `kizu/src/git` with locator `parse.rs:LINE` is **empty rc=1** on both (basename does not resolve against the repo root). Shared hole.

`rg --json 'return None;' | amid --explain` with no snippet derives each *if-arm* (`if !b_decoded.starts_with`, `if len<5+ 2`, …). Correct, and the wrong question — you still want to name `a/`. Amid's CANDIDATE already says this.

## Collapse

`parse.rs:63-65` is `if a_side != b_side { return None; } Some(bytes_to_path(a_side))`. Payload is `Some(...)`.

- ambit scores brace-only as 0 and `Some(` +2 → `here Some(bytes_to_path(a_side))`
- amid `_payload_score` still ties `}` with the first equal-score line → `here }`

Inherited engine, not the stream verb — but it is what you read.

## Decision

Carry **ambit**. Lineage vehicle for mutation-35.

The mutation's own default is `rg FILE | tool`. Single-file rg emits LINE:text. That is the `when` footgun. Only ambit absorbs it: `(line, text)` pins against `git ls-files` (cwd / `--repo`) and scans if unique. From `kizu/` the advertised pipe is the invert of `when parse.rs:60`, including `let b_side`, and the last span is the payload not a brace. Demo actually dogs this file.

Keep **amid** as the json/derive spare. Do not keep two default producers. Do **not** implement a third clone.

Amid's extra is real: `rg --json` always names the file, and peeling `if !P` means the locator names the condition (`rg --json starts_with | amid --kind given` — no snippet). That is the more honest Unix stream. It is not the pipe the mutation named, and the LINE:text refuse is still rc=2 on the producer people type. `here }` is the same collapse hole ambit already closed.

Pin recovery is a name-tree, not a parse-walk: ambit does not `scan_paths(cwd)`, and it refuses when pins are ambiguous or the cwd is the wrong git. If a later destroyer treats any `git ls-files` as a walk, flip the vehicle to amid and teach `--json`. Until then, do not graft json+peel onto ambit in this slot.

Suggested mutation (not done): teach the vehicle `rg --json` and peel `!P`. That is a flag on ambit, not a third binary.
