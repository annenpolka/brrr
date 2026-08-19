# flume

Rewrite stale `file:line` addresses *inside a log stream* from one directory snapshot onto another. Never talks to git. Never takes a locator as an argument.

## Install / run

```bash
chmod +x ./flume
./flume --help
./demo.sh
```

Requires Python 3. Git is not a dependency.

## Interaction

```
cat compiler.log | flume --from-dir oldtree --to-dir newtree
flume --from-dir oldtree --to-dir newtree rustc.log pytest.log
```

stdin (or log files) in; the same stream out, with locators rewritten. Mappings, if you want them, are `--trace` on stderr. Confirmed deletions pass through unchanged. `--strict` exits 1 only when a locator cannot even be read from `--from-dir`.

## Examples

Rustc log from before a file-split, pointed at today's tree. The `-->` locator *and* the snippet gutter move:

```bash
cat rustc.log | ./flume --from-dir kizu-old --to-dir kizu-now
#   --> /home/runner/work/kizu/kizu/src/app/layout.rs:17:5
#    |
#  17 | pub fn seen_hunk_fingerprint(
```

Mixed Python / Swift / noise, including a traceback and a basename-only diagnostic:

```bash
cat mixed.log | ./flume --from-dir from --to-dir to
#   File "src/math/ops.py", line 3, in add
#   PresenceArbiter.swift:23:20: error: cannot find 'threshold' in scope
#   http://localhost:8080/health
```

Two directories that do not share history (a rewrite, a copy, a tarball):

```bash
./flume --from-dir old-python --to-dir new-pkg token.log --trace
# stderr: moved	src/old.py:1	pkg/new.py:1	1.000
# stdout: pkg/new.py:1: token
```
