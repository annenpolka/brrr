# dowel

A **dowel** is a contract token: template fingerprint + the hole names that bound + the locus they sat in.

Mint once from `path:line` and a runtime instance. Resolve later onto another tree. The answer is the current `path:line` **and** whether those same holes still bind.

This is not `pin | invert`. pin relocates a source line and is silent on hole names. invert binds a paste against whatever templates you feed it now, and does not remember that the hole used to be `{uid}`. A dowel seats by template static + locus, then assays the stored names. A clone that kept the old names cannot hide a rename at the extracted body.

## Install / run

Python 3.10+, git. No third-party packages. v0.2.

```bash
chmod +x ./dowel
./dowel --help
./dowel --selftest
./demo.sh
```

## Three examples

### 1. Extract + rename

```bash
./dowel mint --repo /path --from <old-sha> src/user.py:4 'user 42 not found'
./dowel resolve --repo /path --to HEAD dowel1.…
```

```
renamed    src/user.py:4  →  src/user/messages.py:4   0.91  {uid}→{user_id}
```

### 2. Dropped hole

A later tree that turns `cannot reach {host}:{port} after {n}` into `cannot reach {host} after {n}` resolves **unbound** and names `{port}`. invert would quietly bind `{host}=db.internal:5432`.

### 3. Same holes, new address

```
shifted    src/user.py:10 → src/user/messages.py:10  {cmd} still binds
```

## Verdicts

| status | meaning |
| --- | --- |
| seated | same path:line, contracted holes still bind |
| shifted | locus moved, same hole names still bind |
| renamed | seated, names drifted, values still match |
| unbound | a seat was found; the contracted names no longer bind |
| gone | no matching template |
| ambiguous | two equal seats |

Resolve refuses `path:line`. Missing `--to` is an error. A clipped token fails closed. A foreign repo is refused unless `--any-repo`.
