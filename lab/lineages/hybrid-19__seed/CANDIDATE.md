# hybrid-19 — seed

## Primitive

Name a locus from stdin locators (`rg | seed`) only when those locators are **one content pin** — stripped LINE:text identity, every pin, one path-condition stack — then emit other loci whose stack is the same or a superset, scanning the files those locators named.

## Why this might not exist

`peal` is the invert of `chime` as a Unix filter. DESTROYER_PEAL left three load-bearing holes that are the same lie:

1. **First locator is the seed.** `rg 'return None;'` chimed the quoted-form miss (`:34`), not the unquoted survivor. The keyword you grepped is not the stack you get.
2. **Uniqueness is substring containment.** A decoy comment that mentions `return None` uniquely recovers that file.
3. **`pins[:16]`** throws away the 17th pin that distinguishes twins.

`--same-as` / `--first` already exist as overrides. The default pipe should refuse a bag, match the stripped line, and scan every pin. Not a third `ambit` (snippet). Not a cwd walk.

## How to run

```bash
printf '%s\n' 'fixtures/guards.rs:11:    let p = (bytes.len() - 5) / 2;' | ./seed --explain
./seed fixtures/nested.py:13 --exact --explain
printf '%s\n' 'fixtures/bag.py:6:        return None' 'fixtures/bag.py:8:        return None' | ./seed --explain
cd "$KIZU" && rg -n 'let b_side' src/git/parse.rs | /path/to/seed --explain
cd "$KIZU" && rg -n 'return None;' src/git/parse.rs | /path/to/seed --explain
cd "$KIZU" && rg -n 'return None;' src/git/parse.rs | /path/to/seed --same-as :60 --explain
./demo.sh
```

Python 3.10+, stdlib only. `./seed` is the CLI. Exit 2 if you pass a directory without `--walk`, invoke with no files and no locators, or pipe a bag of stacks.

## Empirical transcript

### Before the improvement

Gold `rg -n 'let b_side'` invert survived. First-locator is not the seed: the `return None;` bag refuses (9 stacks), peal still chimed `:33-34`.

```
$ cd kizu && rg -n 'let b_side' src/git/parse.rs | seed --explain
seed    …/src/git/parse.rs:60
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
# same three spans as peal / chime parse.rs:60
```

```
$ cd kizu && rg -n 'return None;' src/git/parse.rs | peal --explain
seed    parse.rs:33-34
  if     bytes.starts_with(b"\"a/")  (L25)
  here   return None;
# rc=0 — quoted-form miss

$ cd kizu && rg -n 'return None;' src/git/parse.rs | seed --explain
seed: locators name 9 stacks; pass --same-as FILE:LINE or --first
  parse.rs:34  if !b_decoded.starts_with(b"b/")
  parse.rs:44  if len<5+ 2
  parse.rs:48  if !inner.is_multiple_of(2)
  parse.rs:52  if !bytes.starts_with(b"a/")
  parse.rs:58  if bytes.get(...)!= Some(b" b/")
  parse.rs:62  if a_side!= b_side
  parse.rs:77  if bytes.first()!= Some(&b'"')
  parse.rs:104 if end>bytes.len()
  … 1 more
# rc=2 — first locator is not the seed

$ cd kizu && rg -n 'return None;' src/git/parse.rs | seed --same-as src/git/parse.rs:60 --explain
# gold three spans again
# rc=0

$ cd kizu && rg -n 'return None;' src/git/parse.rs | seed --same-as :60 --explain
seed: expected FILE:LINE, got ':60'
# the recovered file is sitting right there; :60 does not bind
```

`rg -n return fixtures/nested.py | seed` refuses 12 stacks (`:7` None-guard, `:13` denied, …) instead of seeding `:6-7`.

Substring decoy (`3: return None` vs `note = "return None is mentioned here"`) does not recover. 16 shared pins refuse; the 17th `UNIQUE_REAL` recovers `real.rs`.

### After the improvement

`--same-as :LINE` binds to the unique recovered file (the same object as LINE:text pin recovery). Forced by the kizu bag: rg omitted the path, refuse listed `:62`, and repeating `src/git/parse.rs:60` was the thing the gold pipe had already recovered.

```
$ cd kizu && rg -n 'return None;' src/git/parse.rs | seed --same-as :60 --explain
seed    …/src/git/parse.rs:60
  here   let b_side = …
deeper  parse.rs:61-62
  here   return None;
deeper  parse.rs:64
  here   Some(bytes_to_path(a_side))
# rc=0 — gold three spans; first locator is still not the seed

$ printf '%s\n' '13:    return "denied"' '34:            return "drained"' \
    | ./seed --same-as :13 --exact --tsv --repo $tmpgit
# denied only
```

`--first` on the same stream still chimed `:33-34` (peal's default, opt-in). `./demo.sh` 0. 40 tests.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `kizu/src/git/parse.rs:60` | `rg -n 'let b_side'` → unquoted-form survivors; not quoted branch; not shallower `:54` |
| `kizu/src/git/parse.rs` `return None;` | bag of stacks **refuses**; not quoted-arm `:34`; `--same-as` restores gold |
| `fixtures/bag.py` | two `return None` arms refuse unless `--same-as` / `--first` |
| `fixtures/nested.py`, `guards.rs`, `sample.swift` | exact arm, try≠except, guard≠guard-else |

Read-only on the real repos. Ugly fixtures live in `fixtures/`.

## Surprises

- The gold pipe is a locator unique to the stack. A bag of early returns is a different object. The refuse listing is the useful part: `:62` is the unquoted `return None` on the gold arm, sitting next to `:34`.
- Pin identity is stricter than `in`: a unique short pin still works; a comment that mentions the snippet does not steal the file.
- Same-stack two pins (guards.rs `:12` then `:11`) is not a bag. Seed is that stack, scan still emits `11-12`.

## Failures

- Inherited engine holes from peal/chime (`if let` dropping `let`, empty match-arm preds, quoted-form miss is not `given ¬(quoted)`).
- Named `rg -nH` basename from a nested cwd still joins to git toplevel (DESTROYER_PEAL §5). Not this primitive.
- `--column` on single-file rg is still LINE:COL:text, not LINE:text.

## Suggested mutations

- Resolve named locators against cwd then repo (`rg -nH` from `src/git`).
- Drop a leading column before pin identity (`60:5: let b_side`).
- Binary stdin: fail closed exit 2 (traceback is still rc=1).

## Kill / keep

**Keep.** The object is still peal's stack; the seed is now a content pin. Kill if a later generation walks cwd, greps the `if`, or clones ambit's snippet.
