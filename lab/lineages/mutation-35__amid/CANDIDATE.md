# mutation-35 — amid

## Primitive

Pipe locators (`rg | amid`); emit every locus **in the same file those locators came from** whose path-condition contains the predicate. A stream, not a tree walk. Reverse of `under`'s default: `under` names a condition and walks a tree; `amid` lets `rg` name the files (and, after the improvement, the condition) and expands each hit into the file-local path-condition.

## Why this might not exist

`under` already inverts `when`. Its default universe is still a tree: `./under PRED` walks cwd. Reviewers do not walk trees. They already have a locator stream — `rg --json starts_with parse.rs`, a compiler log, a hunk list. The next question is *what else in that file runs under this condition*, including fallthrough `given` lines that never mention the token. `rg | under PRED FILE` filters the locators (intersection). `rg | amid` scans the file (expansion). Nothing does that as a Unix pipe.

Not leftover-name hunting, not inverse-dead-code, not another tree walker with a new flag.

## How to run

```bash
printf 'fixtures/nested.py:13:    return "denied"\n' | ./amid 'user.locked' --explain
rg -n 'return' fixtures/nested.py | ./amid 'user.locked' fixtures/nested.py --tsv
rg --json 'starts_with' fixtures/guards.rs | ./amid --explain
rg --json 'return None;' /path/to/parse.rs | ./amid 'starts_with(a/)' --explain
rg --heading -n 'isEnabled' fixtures/sample.swift | ./amid 'isEnabled'
rg -nH 'return' fixtures/nested.py | ./amid 'user.locked' --pin --tsv
./demo.sh
```

Python 3.10+, stdlib only. `./amid` is the CLI.

## Empirical transcript

### Before the improvement (commit `fc9a60c`)

`./demo.sh` exited 0. The flip was real on fixtures: piping `nested.py:13` expanded to `db.flush()` and `return "denied"` and not `return "drained"`. Piping the rust `if !starts_with` line expanded to `let p = …` under `given bytes.starts_with(b"a/")`. `--pin` kept only the piped line. A directory operand without `--tree` was refused. Empty stdin without a FILE was refused (no cwd walk).

kizu `parse.rs` is the object.

```
$ rg -n 'return None;' kizu/src/git/parse.rs | ./amid 'starts_with(a/)' --explain
amid: stdin is not a locator stream
(rg -nH FILE, or LINE:text plus a FILE operand)
```

Single-file `rg` omits the filename. Same footgun `when` already documented. Passing the FILE again, or `rg -nH`, worked and was the valuable invert of `when parse.rs:60`:

```
$ rg -nH 'return None;' parse.rs | ./amid 'starts_with(a/)' --explain
parse.rs:59-60
  match  given bytes.starts_with(b"a/")
  given  ¬(len<5+ 2)
  given  inner.is_multiple_of(2)
  given  bytes.starts_with(b"a/")
  given  bytes.get(b_prefix_start..)== Some(b" b/")
  here   let b_side = &bytes[b_prefix_start + 3..];
```

`rg` never printed line 60. `--pin` on the same stream kept only the `return None` lines that sit under `starts_with(a/)` (L34 quoted-arm, L58, L62) and dropped `let b_side`. Expansion vs filter is the verb.

```
$ rg -nH 'starts_with' parse.rs | ./amid --explain
amid: name a predicate snippet (or --same-as FILE:LINE)
```

The locators already pointed at the condition. The tool still made you type it.

### After the improvement (this commit)

`rg --json` always carries the path, even for one file. Bare `LINE:text` now says so:

```
$ rg -n 'return None;' parse.rs | ./amid 'starts_with(a/)'
amid: locators are LINE:text with no file (rg FILE omits the name).
Pass the FILE, or use rg -nH / rg --json.
```

```
$ rg --json 'return None;' parse.rs | ./amid 'starts_with(a/)' --explain
parse.rs:59-60
  match  given bytes.starts_with(b"a/")
  given  ¬(len<5+ 2)
  given  inner.is_multiple_of(2)
  given  bytes.starts_with(b"a/")
  given  bytes.get(b_prefix_start..)== Some(b" b/")
  here   let b_side = &bytes[b_prefix_start + 3..];
```

No FILE operand. Same stack `when parse.rs:60` prints.

Locators name the condition. An `if !P` line is peeled so the question is the in-force given:

```
$ rg --json 'starts_with' parse.rs | ./amid --kind given --explain
parse.rs:35-37
  match  given b_decoded.starts_with(b"b/")
  here   return Some(bytes_to_path(&b_decoded[2..]));

parse.rs:59-60
  match  given bytes.starts_with(b"a/")
  given  ¬(len<5+ 2)
  given  inner.is_multiple_of(2)
  given  bytes.starts_with(b"a/")
  here   let b_side = &bytes[b_prefix_start + 3..];
```

No snippet typed. `rg` pointed at `if !bytes.starts_with(b"a/")`; amid asked for `bytes.starts_with(b"a/")` and found the survivor. `--kind given` drops the quoted-form `if` body and the later `line.starts_with("Binary files")` arms.

`./demo.sh` exits 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `kizu/src/git/parse.rs` | `rg --json return None;` / `rg --json starts_with` → same-file scan; derive + peel |
| `kizu/src/git/` directory rg | files from locators, not a walk |
| `fixtures/nested.py`, `guards.rs`, `sample.swift` | expansion vs `--pin`; json derive |

Read-only on the real repo. Ugly fixtures live in `fixtures/`.

## Surprises

- The expansion is the whole game. `rg return None` ∩ `under starts_with(a/)` (`--pin`) is three early-return arms. The scan of the same file is `let b_side` — the line `when parse.rs:60` names, reached from the other end, without walking kizu.
- Peeling `!P` on the if-line is not a nicety. `rg starts_with` hits `if !bytes.starts_with(b"a/")`. Without the peel, "under that snippet" is the `return None` arm — the opposite of the question.
- `starts_with(a/)` still hits the quoted `b"\"a/"` arm because fold strips quotes. Inherited from `under`. `--kind given` isolates the unquoted survivor. Derive then emits both snippets (`b"\"a/"` and `b"a/"`); span-dedup stops the quoted body printing twice.
- Default `--explain` on a named FILE dumps every span. Stream default is TSV. That is the right split for a pipe.

## Failures

1. **`rg FILE` without `-H` / `--json` still has no filename.** The error is now specific. We do not walk the tree to recover the file (that would undo the flip).
2. **Inherited engine holes.** `len<5+ 2` spacing, quoted-form not turned into `given ¬(quoted)` on the unquoted path, brace `}` as a representative `here`. Same as `when`/`under`.
3. **`--diff` of an unapplied patch** maps onto the working tree (sample.diff `audit.block` becomes `return "denied"`).
4. **Derive on a payload line** (`rg return None | amid` with no snippet) uses the in-force pred as written, not the peeled given. Correct and usually the wrong question — you still want to name `starts_with(a/)`.
5. **`under 'for'`-shaped noise.** `rg starts_with | amid` without `--kind` also emits `line.starts_with("Binary files")` arms. The locator named every mention; the scan is faithful.

## Suggested mutations

- Overlay an unapplied patch so `--diff` is the post-image.
- Infer `given ¬(P)` for fully-exiting nested ifs (quoted-form miss on parse.rs:60).
- A TUI that paints the file the locators named by whether each line is under the derived pred.

## Kill / keep

**Keep.** The object is the same path-condition as `when`/`under`, but the interaction is the one you type: `rg` already found the file, and after the peel it already named the condition. Kill only if a later generation reduces it to `under PRED FILE`.
