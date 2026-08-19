# rift

Detect identifier-level conflicts that a clean git merge would hide.

## Install / run

Requires Python 3.9+ and `git`. No pip packages.

```bash
chmod +x rift
./rift --self-test
./rift main                     # main...HEAD
./rift origin/main feature
./rift --merge HEAD
./rift --audit 20
./rift --diffs a.patch b.patch
```

Exit codes: `0` no rifts, `1` rifts found, `2` usage/git error.

Machine output: `-o json` or `-o tsv`. Quiet CI gate: `./rift -q main` (status only).

## Examples

**1. Signature vs callsite on different files (git says clean):**

```bash
./rift side-a side-b
```

```
rift: side-a (97e55ac4) vs side-b (f9e8e0ba)  base 6f2efac4
git merge-tree: clean
1 rift(s)

def-use  parse_config  hidden
  A  def + src/parse.rs:1  pub fn parse_config(s: &str, timeout: u64) -> Config {
  A  def - src/parse.rs:1  pub fn parse_config(s: &str) -> Config {
  B  use + src/cli.rs:1  fn main() { let cfg = parse_config(raw, None); }
  B  use - src/cli.rs:1  fn main() { let cfg = parse_config(raw); }
```

**2. Two unified diffs, no repo required:**

```bash
git diff base feature-a > /tmp/a.diff
git diff base feature-b > /tmp/b.diff
./rift --diffs /tmp/a.diff /tmp/b.diff
```

**3. Gate a branch before merging:**

```bash
./rift -q origin/main HEAD && git merge origin/main
```

`./demo.sh` builds fixtures, clones kizu/sitbone read-only, and exits 0 on success.
