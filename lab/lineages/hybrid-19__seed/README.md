# seed

A Unix command nobody invented: **pipe grep locators, seed only if they name one stack.**

`peal` already inverted `chime` as `rg | tool` — scan the files locators named, emit the rest of that path-condition arm. Its seed was the **first rg locator**. `rg 'return None;'` chimed the quoted-form miss. `seed` keeps the gold pipe (`rg -n 'let b_side' | seed` still expands to `Some(bytes_to_path)`) and changes the object of the seed:

- the seed is a **content pin** (stripped LINE:text identity), not rg order
- a bag of cond_keys **refuses** (`--same-as` / `--first` override)
- pin match is the stripped line, not substring containment
- every pin is consulted, not `pins[:16]`

Not a cwd walk. Not a snippet (`ambit`).

```
rg -n 'let b_side' src/git/parse.rs | seed
rg -n 'return None;' src/git/parse.rs | seed
# seed: locators name 7 stacks; pass --same-as FILE:LINE or --first
```

## Install

```bash
chmod +x ./seed
./seed --help
```

Python 3.10+ (stdlib only). No extra packages.

## Examples

```bash
# unique pin: recover the file, scan the arm (rg never printed Some(p))
rg -n 'let b_side' src/git/parse.rs | ./seed --explain
printf '%s\n' 'fixtures/guards.rs:11:    let p = (bytes.len() - 5) / 2;' | ./seed --explain

# bag of early returns is not a seed
rg -n 'return None;' fixtures/bag.py | ./seed --explain
# rc=2 — two stacks. --same-as :8 or --first

# recovered file + :LINE restores the arm rg named by line only
rg -n 'return None;' src/git/parse.rs | ./seed --same-as :60 --explain

# argv seed still scans that file only
./seed fixtures/nested.py:13 --exact --explain
```

### 1. Unique content pin, file scan

The rg hit is one statement. Scanning the file it named still emits the rest of the arm (`Some(p)` / `Some(bytes_to_path)`), which rg never printed.

### 2. Bag of stacks refuses

```bash
./seed --explain < <(rg -n 'return None;' fixtures/bag.py)
# seed: locators name 2 stacks; pass --same-as FILE:LINE or --first
```

First-locator is not the seed.

### 3. No cwd walk

```bash
./seed
# seed: name a locus … No cwd walk.   (exit 2)
```

Exit codes: `0` hits, `1` none / empty cond_key, `2` usage / ambiguous seed / no walk, `3` not a git repo.

See `CANDIDATE.md` for the primitive, dogfood transcript, and failures.
