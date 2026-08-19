# ply

A patch is a superposition. `ply` projects it onto one syntactic class and emits the **ply-edits**.

| class | what |
| --- | --- |
| **number** | `30 → 60` |
| **string** | `"boot" → "ready"` |
| **comment** | `seconds → secs` |
| **ident** | `timeout → deadline` |
| **key** | JSON/YAML keys (`"timeout":`) |
| **import** | import paths |
| **kw** | `async`, `let`, `mut` |
| **text** | CJK / prose letters |
| **punct** | off by default |
| **space** | off by default |

| op | meaning |
| --- | --- |
| **chg** | the same slot mutated (`threshold → presentThreshold`) |
| **del** / **ins** | a token left or arrived |
| **mov** | same value, different line (hidden unless `--moves`) |

Not `difftastic` (tree diff). Not `delta` (color). Not `git diff -G`. The object is the **typed atomic edit**.

## Install / run

Python 3.9+, `git` for `--git`. Stdlib only.

```bash
chmod +x ./ply
./ply --help
./ply --selftest
./demo.sh
```

## Examples

### 1. What actually mutated in a PR (ignore formatter / new files / lockfiles)

```bash
./ply --git main...HEAD --op chg
./ply --git HEAD~5..HEAD --class number
```

sitbone, hysteresis commit range:

```
Sources/SitboneCore/PresenceArbiter.swift  33  number  chg  0.4  0.45
Sources/SitboneCore/PresenceArbiter.swift  12  ident   chg  threshold  presentThreshold
```

### 2. Did a "docs" PR leak code?

```bash
git diff main | ./ply --check --only docs
# exit 1 if ident/number/kw/… changed
```

`docs` = `comment,text,string`. `--check` prints a one-line verdict.

### 3. Same line, two plies

```
-    let timeout = 30; // seconds
+    let timeout = 60; // secs
```

```bash
git diff | ./ply --tsv
```

```
src.rs  2  number   chg  30       60
src.rs  2  comment  chg  seconds  secs
```

`--class number` hides the comment. `--class comment` hides the number.

## Flags

| flag | |
| --- | --- |
| `--git [ARG…]` | `git diff ARG` (default: unstaged) |
| `-C REPO` | git repo |
| `--files OLD NEW` | compare two files |
| `--class LIST` | `number,comment` or `code` / `docs` / `all` |
| `--op LIST` | default `chg,del,ins` |
| `--moves` | show MOVE |
| `--locks` | include Cargo.lock etc. |
| `--new-tokens` | tokenize added/deleted files |
| `--tsv` / `--json` | machine |
| `--diff` | unified diff of matching lines |
| `--check` | exit 1 if matching non-move edits exist |
| `--only LIST` | with `--check`: fail if anything *outside* LIST exists |
