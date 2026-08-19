# unfmt

Inverse printf: given a runtime string, find the source format template that could have produced it.

## Install / run

```bash
# from this worktree
chmod +x unfmt
./unfmt --help
./demo.sh
```

`unfmt` is a single Python 3 file. No dependencies.

Scan a tree with `-C`. Default index is the git working tree (tracked + untracked, minus ignored files). Pass messages as arguments or `-e`, or pipe a log on stdin. Exit `0` if every argument matched (stdin / `--any`: if any line matched), `1` on a miss, `2` on usage error.

## Examples

Paste a filled-in error. The tool inverts `{}` / `{name}` / `${...}` / `\(...)` / `%s` holes:

```bash
./unfmt -C ~/src/kizu \
  'git diff single file failed: fatal: not a git repository'
# src/git/diff.rs:34:28: score=0.78 lang=rust holes=1
#   tmpl:  git diff single file failed: {}
```

Pipe a decorated log. ANSI, `ERROR [...]`, and `error:` prefixes are stripped:

```bash
cargo test 2>&1 | ./unfmt -C . --any
```

Dump every extracted template (the index grep cannot build):

```bash
./unfmt --index -C . | grep 'holes=2'
```

Messages that look like flags go through `-e` (or `--`):

```bash
./unfmt -C ~/src/kizu -e 'Ghostty --attach is only supported on macOS (requires AppleScript)'
```

`--json` emits machine output. `--walk` ignores git and walks the filesystem (skips `node_modules`, `target`, `*.min.js`, …). `--cached-only` restricts the index to `git ls-files --cached`.
