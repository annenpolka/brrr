# zure

Detect identifier-level conflicts you are about to commit against your own recent history.

No second branch. One changeset is already committed; the other is the uncommitted working tree (staged, unstaged, untracked). `git commit` will accept both as linear history. `zure` reports the crossed definition/use edits that `git diff` hides.

## Install / run

Requires Python 3.9+ and `git`. No pip packages.

```bash
chmod +x zure
./zure --self-test
./zure                          # worktree vs recent history
./zure --staged                 # index only (pre-commit)
./zure --horizon 12
./zure --since origin/main
./zure --replay 20
./zure -q                       # exit status only
```

Exit codes: `0` clean, `1` zures found, `2` usage/git error.

Machine output: `-o json` or `-o tsv`. Quiet CI/hook: `./zure -q --staged`.

## Examples

**1. You added a callsite last commit; the working tree changes the signature (git says nothing):**

```bash
./zure --horizon 8
```

```
zure: worktree vs history HEAD~8..a1b2c3d4  (9f8e7d6c..a1b2c3d4)
hist 1 file(s), work 1 file(s)  [worktree+untracked]
1 zure(s)

break-use  parse_config  hidden
  hist  use + src/cli.rs:2  let cfg = parse_config(raw);
  work  def + src/parse.rs:1  pub fn parse_config(s: &str, timeout: u64) -> Config {
  work  def - src/parse.rs:1  pub fn parse_config(s: &str) -> Config {
```

**2. Untracked file calls a function the last commits deleted:**

```bash
./zure
```

```
stale-use  doomed_symbol  hidden
  hist  def - src/lib.rs:1  pub fn doomed_symbol() {}
  work  use + src/extra.rs:1  fn extra() { doomed_symbol(); }
```

**3. Gate a commit / replay your last twenty commits as former worktrees:**

```bash
./zure -q --staged && git commit
./zure --replay 20 --horizon 10
```

`./demo.sh` builds fixtures, clones kizu/sitbone/voidtrace/tenaoshi, and exits 0 on success.
