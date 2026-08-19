# mutation-16 — chime

## Primitive

Name a locus; emit other loci whose path-condition is the **same stack**, or a **superset** (deeper nest: the seed stack is an ordered prefix). Control-flow rhyme as a Unix verb: `chime file:line`, also spelled `chime --same-as file:line`.

The object is still a **condition stack**. The address is a line. The match is identity of effective `(kind, pred)` frames, not a snippet.

## Why this might not exist

`when` answers "when does this line run?" `under` answers "what runs under this predicate snippet?" Reviewers point at a line and ask the third question: *what else is in this arm?* `when --group` clusters a diff by stack but you cannot address a cluster by a locus. `under --same-as` AND-matches snippets from the stack — fuzzy containment, no "exact arm" vs "deeper", and a different function with the same words is a hit. Nothing is `comm(1)` for path-conditions.

Ancestor `when`'s own suggested mutation: invert to `when --same-as file:line` — the rhyme of *when*, not of tokens. Reverse lineage `under` left "lines that share *exactly* this stack" open.

Not leftover-name hunting, not inverse-dead-code, not format-string inversion, not `rg` of the `if`.

## How to run

```bash
./chime fixtures/nested.py:13 --exact --explain
./chime fixtures/nested.py:8 --group
./chime --same-as fixtures/nested.py:10 --exact
./chime fixtures/guards.rs:11 --explain
printf '13:return\n6:missing\n' | ./chime fixtures/nested.py:8 --tsv
./chime /path/to/kizu/src/git/parse.rs:60 --explain
./demo.sh
```

Python 3.10+, stdlib only. `./chime` is the CLI.

## Empirical transcript

### Before the improvement (commit `858a602`)

Fixtures already distinguished arms: `chime nested.py:13 --exact` was only `return "denied"`; `chime nested.py:8` was every later arm under `given user is not None` and not the None-arm; `chime nested.py:10 --exact` was the try body, not `except`.

Real kizu told the truth about *which arm* and then lied about *which line*.

`./chime kizu/src/git/parse.rs:60` already split the unquoted-form survivors from the quoted branch (`:25`) and from the shallower `let a_side` (`:54` is a subset, not a super — `chime :60` does not emit it). The three spans were right:

```
same    parse.rs:59-60   let b_side = …
deeper  parse.rs:61-62   extra if a_side != b_side    return None
deeper  parse.rs:63-65   extra given a_side == b_side  }
```

The success arm's `here` was the closing `}` of the function. `--exact :64` was a 3-line span whose representative was `}`. `under --same-as :60` produced the same three buckets and the same `}` — snippet-AND cannot pick a statement.

`sitbone/.../PresenceArbiter.swift:81` after `guard isEnabled` collapsed 79–82 with an empty `here` (blank lines) and 88–102 as a single `}` span.

`validate_execplan.py:54` (the `if not file_path.exists():` line) is an eval frame, so `chime` correctly refused "no path-condition". The `given file_path.exists()` is attached to later classified statements (`:62`, `:102`), not to `content = file_path.read_text` on `:58`. Inherited from `when`.

### After the improvement (this commit)

Brace-only, blank, `else {`, and eval-only test lines are dropped unless they are the seed. Collapse picks the highest-payload statement, with a tie-break toward the seed.

```
$ ./chime kizu/src/git/parse.rs:60 --explain
seed    parse.rs:60
  given  ¬(len<5+ 2)
  given  inner.is_multiple_of(2)
  given  bytes.starts_with(b"a/")
  given  bytes.get(b_prefix_start..)== Some(b" b/")
  here   let b_side = &bytes[b_prefix_start + 3..];

deeper  parse.rs:61-62
  extra  if a_side!= b_side
  here   return None;

deeper  parse.rs:64
  extra  given a_side== b_side
  here   Some(bytes_to_path(a_side))
```

The quoted-form body is gone. `--exact :60` is one line. `--exact :64` is `Some(bytes_to_path(a_side))`, not `}`.

`chime parse.rs:54` (one given shallower) lists `:60` and `:64` as *deeper* — the same object approached from a prefix. `chime :60` does not list `:54`. That direction is the whole verb: superset, not subset.

```
$ ./chime fixtures/nested.py:10 --exact --explain
seed    fixtures/nested.py:10
  here   db.flush()
same    fixtures/nested.py:15
  here   return None
```

The `if user.role == "admin":` eval header is no longer "in this exact try arm". `except` still is not.

```
$ ./chime sitbone/.../PresenceArbiter.swift:81 --group
same    :80-81   let active = readings.filter { … }
deeper  :83-86   extra guard-else ¬(!active.isEmpty)   return PresenceReading(.unknown)
deeper  :89-101  extra guard !active.isEmpty           let rawScore / Logger / return
```

Blank lines and the `guard-else` of `isEnabled` itself are gone. The second-guard *else* is still a superset of `guard isEnabled` (isEnabled holds; the collection was empty). That is the correct polarity.

`./demo.sh` exits 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `kizu/src/git/parse.rs:60` | unquoted-form survivors; not quoted branch; not shallower `:54` |
| `kizu/src/git/parse.rs:54` | prefix: `:60`/`:64` appear as deeper |
| `kizu/src/git/parse.rs:25` | quoted-form exact arm |
| `kizu/src/git/parse.rs:83` | `if c == '"'` return in `parse_quoted_token` |
| `kizu/src/git/diff.rs:51` | untracked-visible match arms as deeper |
| `skills/.../validate_execplan.py:102` | exact Decision-warning arm |
| `sitbone/.../PresenceArbiter.swift:81` | guard body vs guard-else |
| `fixtures/nested.py`, `guards.rs`, `sample.swift` | exact arm, None-guard superset, try≠except, guard≠guard-else |

Read-only on the real repos. Ugly fixtures live in `fixtures/`.

## Surprises

- Direction matters. A stack dump is a *chain*: `:54 ⊂ :60 ⊂ :64`. `chime :60` emits supersets. `under --same-as :60` happens to agree on this file because the four givens are unique strings; it cannot *say* "exact" vs "deeper", and it would agree with a different function that mentioned the same words.
- The valuable "chime" on real Rust is the **rest of an early-return survivor region**, including the nested `if a_side != b_side` as a labeled extra, not as a second grep. `git diff -W` still only names `parse_diff_git_header`.
- Polarity is inherited from the engine *plus* effective-frames: `guard isEnabled` + `guard-else isEnabled` is not a prefix of `guard isEnabled`. Without dropping the shadowed `guard`, the else-return "chimed" with the body. That is the invert of `under`'s polarity lesson, applied to prefix identity.
- `given file_path.exists()` does not cover every later line. Assignments between the early return and the next `if`/`for` have an empty cond_key. `chime :58` refuses; `chime :62` is the exists-guard rhyme. Looks like a bug and is the ancestor's fallthrough heuristic.

## Failures

1. **Inherited engine holes.** Nested-but-total early returns (quoted-path miss in `parse.rs`), `if let` dropping `let`, `len<5+ 2` spacing, empty Rust match-arm preds — same as `when`.
2. **Brace if-line is not `eval`.** `chime parse.rs:54` still uses `if bytes.get(...) {` as a representative of the mismatch arm (the brace engine does not tag that line `eval`). `--braces` is a blunt restore, not a fix.
3. **Fallthrough `given` is statement-classed.** Python assignments after a guard do not carry the given; only subsequent `if`/`for`/`match` do.
4. **`--diff` of an unapplied patch** maps `+` onto the working tree. Same hole as `when`.
5. **Empty cond_key.** Function preamble / eval-only seed exits 1. Correct, easy to miss (`:54` of `validate_execplan.py`).
6. **Same-function default.** `--any-fn` exists; cross-file rhyme of an identical four-given stack was not dogfooded.

## Suggested mutations

- Overlay an unapplied patch so `--diff` is the post-image.
- Infer `given ¬(P)` for fully-exiting nested ifs (quoted-form miss) — then `chime parse.rs:60` would also *exclude* a quoted fallthrough if the engine grew one.
- Cross-file rhyme: other parsers whose survivor stack is the same four givens.
- A TUI that paints every line same / deeper / other relative to a pinned locus.
- `chime --subset` (the inverse direction: lines whose stack `:60` is a super of).

## Kill / keep

**Keep.** The object (ordered path-condition identity, addressed by a line, split same vs deeper) is the missing third verb next to `when` and `under`. Kill only if a later generation reduces it to `under --same-as` without `--exact` and without prefix-superset labels.
