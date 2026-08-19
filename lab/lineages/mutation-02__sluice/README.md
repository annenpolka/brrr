# sluice

Inverse printf as a Unix filter. You have a runtime string; templates arrive on a stream. The tool does not walk a repository.

## Install / run

```bash
chmod +x sluice
./sluice --help
./demo.sh
```

Single Python 3 file. No dependencies.

Runtime string(s) go on argv (`-e` if they look like flags) or on stdin when `--templates FILE` already claims the other channel. Templates come from `--templates FILE`, `--templates -`, `--files -`, or implicit stdin when argv already has a message.

There is no `-C` scan. `rg`, `git grep`, `git log -p`, and `find` decide the corpus.

## Examples

Pipe `rg` hits. sluice extracts format strings from each line and scores them against the message:

```bash
rg -n --type rust 'format!|anyhow!' ~/src/kizu \
  | ./sluice 'git diff single file failed: fatal: not a git repository'
# src/git/diff.rs:34:28: score=0.68 lang=rust holes=1 via=full from=grep
#   tmpl:  git diff single file failed: {}
```

`rg -n` names a file; `--open auto` (default) reads that file so multiline Swift is whole:

```bash
rg -n --type swift 'cumulative save failed' ~/src/sitbone \
  | ./sluice 'cumulative save failed path=/tmp/c.json error=disk full'
# … JSONSessionStore.swift:45:36 from=file  tmpl:  cumulative save failed path={} error={}
```

`--open never` stays line-only (a 1-hole fragment). `--files` / `rg -l` still works.

Relative paths from `git -C repo grep` need `--chdir` (path prefix, not a walk):

```bash
git -C ~/src/kizu grep -n -e 'format!' -- '*.rs' \
  | ./sluice --chdir ~/src/kizu 'git diff single file failed: boom'
# src/git/diff.rs:34:28 from=file  tmpl:  git diff single file failed: {}
```

History is just another stream:

```bash
git -C ~/src/kizu log -p -S 'git diff single file failed' -- src \
  | ./sluice 'git diff single file failed: boom'
# src/git/diff.rs:34:28: … from=patch  tmpl:  git diff single file failed: {}
```

Saved index, then match a decorated log:

```bash
rg -n --type rust 'format!|anyhow!' src | ./sluice --templates - --extract > tmpls
cargo test 2>&1 | ./sluice --templates tmpls --any
```

Exit `0` if every argument matched (stdin / `--any`: if any line matched), `1` on a miss, `2` on usage. Directories are refused: this is not a walker.

## Stream shapes (`--from auto`)

- `path:line:text` / `path:line:col:text` — `rg -n`, `git grep -n`, `grep -n`
- `rg --json` match events
- unified diff (`git log -p`, `git show`)
- `--extract` index lines (`path:line:col: lang=… holes=… tmpl`)
- JSONL `{path,line,template}`
- one existing source path per line (`rg -l`, `git ls-files`)
- raw templates (`user {} not found`)

`--from grep|raw|jsonl|rg-json|index|patch|files` pins a shape. `-0` is NUL-separated records.
