# chime

A Unix command nobody invented: **which other lines run under the same path-condition as this one?**

`when` names a line and prints the stack. `under` names a predicate snippet and prints the lines. `chime` names a line and prints **the other lines whose stack is that stack, or a superset of it** — control-flow rhyme, not token rhyme.

The object is still a **condition stack**. The address is a locus. The match is ordered prefix identity, not `rg` of the `if`.

## Install

```bash
chmod +x ./chime
./chime --help
```

Python 3.10+ (stdlib only). No extra packages.

## Examples

```bash
# other lines in this exact arm
./chime fixtures/nested.py:13 --exact

# this arm, plus everything nested further under it
./chime fixtures/nested.py:8 --explain

# alias spelled as the ancestor suggested
./chime --same-as fixtures/nested.py:10 --exact

# pipe: keep grep hits that chime with a locus
rg -n 'return' fixtures/nested.py | ./chime fixtures/nested.py:8 --tsv
```

### 1. Exact arm

```bash
./chime fixtures/nested.py:13 --exact --explain
```

Only `return "denied"`. Not `return "drained"` (different arm). Not `audit.warn("missing")` (opposite polarity).

### 2. Same or deeper

```bash
./chime fixtures/nested.py:8 --group
```

Line 8 is the fallthrough of `if user is None: return`. Every later arm — locked, pending, match — is a **superset** of that `given user is not None` stack. The None-arm itself is not.

### 3. Try is not except

```bash
./chime fixtures/nested.py:10 --exact
```

`db.flush()` and the `return None` that share the try-body stack. The `except` arm is a sibling, not a prefix. `--exact` also drops the nested `if user.role == 'admin'` body (that stack is deeper).

## Output

| flag | meaning |
| --- | --- |
| `--explain` | multi-line human (default on a tty for a few hits) |
| `--tsv` | `file:span  relation  seed  n  depth  function  extra  path  source  engine` |
| `--json` | NDJSON records |
| `--group` | cluster `same` vs `deeper` |
| `--exact` | identical stacks only |
| `--braces` | keep `{` / `}` / blank lines (dropped by default) |
| `--others` | omit the seed line |
| `--same-as FILE:LINE` | seed alias |

Exit codes: `0` hits, `1` none / bad locus, `2` usage, `3` not a git repo.

See `CANDIDATE.md` for the primitive, dogfood transcript, and failures.
