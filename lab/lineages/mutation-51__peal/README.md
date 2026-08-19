# peal

A Unix command nobody invented: **pipe grep locators, get the rest of that path-condition arm.**

`chime` names a `FILE:LINE` and scans a file (or a tree). `ambit` takes a predicate snippet and scans the files `rg` named. `peal` is the missing composition: **the locators are the seed; the files they named are the only things scanned; the match is ordered path-condition identity, not a snippet.**

```
rg -n 'let b_side' src/git/parse.rs | peal
```

Same stack, plus deeper nests. Not the quoted-form branch. Not a cwd walk. Single-file rg may omit the path; peal recovers it from `(line, text)` pins against this git tree.

## Install

```bash
chmod +x ./peal
./peal --help
```

Python 3.10+ (stdlib only). No extra packages.

## Examples

```bash
# rg found this line; what else is in this arm?
rg -n 'let b_side' src/git/parse.rs | ./peal --explain
printf '%s\n' 'fixtures/guards.rs:11:    let p = (bytes.len() - 5) / 2;' | ./peal --explain

# argv seed still scans that file only, never the tree
./peal fixtures/nested.py:13 --exact --explain

# rg -l names files; --same-as names the stack
printf '%s\n' fixtures/nested.py | ./peal --same-as fixtures/nested.py:13 --exact

# ancestor filter, opt-in
rg -n 'return' fixtures/nested.py | ./peal fixtures/nested.py:8 --hits --tsv
```

### 1. Locator seed, file scan

The rg hit is one statement. Scanning the file it named still emits the rest of the arm (`Some(p)`), which rg never printed. Filtering grep lines cannot do that.

### 2. Exact arm

```bash
./peal fixtures/nested.py:13 --exact --explain
```

Only `return "denied"`. Not `return "drained"`. Not the None-arm.

### 3. No cwd walk

```bash
./peal
# peal: name a locus … No cwd walk.   (exit 2)
```

Exit codes: `0` hits, `1` none / empty cond_key, `2` usage / no walk, `3` not a git repo.

See `CANDIDATE.md` for the primitive, dogfood transcript, and failures.
