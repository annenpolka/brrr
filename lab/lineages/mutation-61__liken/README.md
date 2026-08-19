# liken

A Unix command nobody inverted: **which other added lines in this unapplied patch share that path-condition?**

`graft` overlays a unified diff in memory and prints the stack of each `+` line. `liken` is the invert: name a stack (`given starts_with(a/)`) or a post-image `FILE:LINE`, and emit the added lines that run under it — including fallthrough `given` from early-return guards.

The locus is the **post-image**. Unified hunks are windows. `git diff -W` may name the function; the `if` that makes a change legal is often above the `@@`, and a `+` line's number only exists after apply. Overlay never writes the worktree.

This is not a third `ambit`/`amid` clone (those scan locator files of HEAD). It does not walk cwd. It does not reduce to "run `when` after `git apply`".

## Install

```bash
chmod +x ./liken
./liken --help
```

Python 3.9+ (stdlib only). No extra packages.

## Examples

### 1. Two added lines that share `given starts_with(a/)`

```bash
./liken --base :wt --diff fixtures/kin.diff --same-as 'fn parse_header | given starts_with(a/)'
```

`let a_side` and `let b_side` group together. `return Some(1)` under the quoted-form `if bytes.starts_with(b"\"a/")` does not.

### 2. Address the post-image line, not HEAD

```bash
git -C kizu diff 3b3e0a9^ 3b3e0a9 -- src/git/parse.rs \
  | ./liken -C kizu --base 3b3e0a9^ --same-as src/git/parse.rs:60
```

Line 60 is `let b_side = …` after apply. `liken` overlays onto `3b3e0a9^` in memory and lists the other `+` lines still under that stack. `parse.rs` on disk is untouched.

### 3. Sitbone hysteresis hunk, before it lands

```bash
git -C sitbone diff e9b0f75^ e9b0f75 -- Sources/SitboneCore/PresenceArbiter.swift \
  | ./liken -C sitbone --base e9b0f75^ --same-as 'guard isEnabled'
```

The added `let status = applyHysteresis(...)` sits under two `guard`s. The `precondition` lines in `init` do not.

## Output

| flag | meaning |
| --- | --- |
| `--explain` | multi-line human (default with `--same-as`) |
| `--group` | cluster added lines by exact path-condition (default without `--same-as`) |
| `--tsv` | `file:line  side  depth  function  path  here  engine  image  placed  error` |
| `--json` | NDJSON records |
| `--payload` | drop brace/comment husks (default on explain/group) |
| `--husks` | keep braces/comments in human output |
| `--exact` | FILE:LINE matches only the identical stack (pin default) |
| `--under` | FILE:LINE matches any superstack |

Exit codes: `0` found, `1` none, `2` usage/error.

## Flags

| flag | meaning |
| --- | --- |
| `-C DIR` / `--repo` | repo root (git `-C`). Pre-image only; not a walk |
| `--base REV` | pre-image revision (default `HEAD`). `:wt` = working tree |
| `--diff FILE` | unified diff (`-` = stdin) |
| `--same-as QUERY` | `FILE:LINE` (post-image; exact stack) or `kind pred \| …` (subsequence) |
| `--kind KIND` | restrict snippet clauses to this frame kind |
| `--under` | pin matches deeper arms too |
| `--husks` | do not drop `}` / comments from explain |

stdin = unified diff. Without a diff, `liken` refuses (exit 2). See `CANDIDATE.md`.
