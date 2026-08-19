# graft

A Unix command nobody invented: **if I apply this hunk, under which predicates does the new line run?**

`when` / `whence` answer that question on the current tree. Unified hunks are windows — the `if` that makes a change legal is often above the `@@`, and a `+` line's number is a *post-image* coordinate. Looking the number up in HEAD is lucky when the insert stays in the same arm, and lying otherwise.

`graft` reads a unified diff (stdin or `--diff FILE`), overlays it **in memory** onto `-C repo` at `--base` (default `HEAD`), and emits the path-condition stack of each added line as if the patch were applied. It never writes the worktree.

Fallthrough `given` frames from early-return guards are included — including **nested-but-total** early returns (the quoted-path miss in `when`/`whence`).

HEAD-only lookup is `--now FILE:LINE`. That is opt-in. Without a diff, `graft` refuses to become a second `when`.

## Install

```bash
chmod +x ./graft
./graft --help
```

Python 3.10+ (stdlib only). No extra packages.

## Examples

### 1. A patch that *adds* an `if` HEAD does not have

```bash
./graft --base :wt --diff fixtures/newif.diff --explain
```

```
fixtures/guards.rs:12  [post]
  in     parse_header(bytes:&[ u8])-> Option<usize>
  given  ¬(bytes.starts_with(b"\"a/"))
  given  ¬(bytes.len()<7)
  given  bytes.starts_with(b"a/")
  if     bytes.len()>100
  +      return None;
```

`when --diff` would look up post-image line 12 in the *current* file and report `Some(p)` — the line that has not been written yet is invisible.

### 2. Sandwich: `git diff A B` against A matches the tree at B

```bash
git -C kizu diff 3b3e0a9^ 3b3e0a9 -- src/git/parse.rs \
  | ./graft -C kizu --base 3b3e0a9^ --tsv
```

`src/git/parse.rs:60` is `let b_side = ...` under five `given` frames, including `¬(bytes.starts_with(b"\"a/"))` from the nested-total quoted-form `if`.

### 3. Pipe a review patch, group by condition

```bash
git diff main HEAD | ./graft -C . --base main --group
```

Lines that would run under the same predicates collapse into one bucket. Review the *conditions you are about to add*, not the hunk windows.

## Output

| flag | meaning |
| --- | --- |
| `--explain` | multi-line human (default on a tty for a few loci) |
| `--tsv` | `file:line  side  depth  function  path  source  engine  image  placed  error` |
| `--json` | NDJSON records |
| `--group` | cluster added lines that share a path-condition |

Exit codes: `0` every added line placed, `1` a locus cannot be placed, `2` usage/error.

## Flags

| flag | meaning |
| --- | --- |
| `-C DIR` / `--repo` | repo root (git `-C`) |
| `--base REV` | pre-image revision (default `HEAD`). `:wt` = working tree |
| `--diff FILE` | unified diff (`-` = stdin) |
| `--now FILE:LINE` | opt-in current-tree lookup, no overlay |

See `CANDIDATE.md` for the primitive, dogfood transcript, and failures.
