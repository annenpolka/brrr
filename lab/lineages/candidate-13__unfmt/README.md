# unfmt

Invert an observed string — an error, log line, or assertion message — against the source templates that could have produced it, and bind the holes.

## Install / run

```bash
# Python 3.10+, stdlib only
chmod +x unfmt demo.sh
./unfmt -C path/to/repo 'the message you saw'
echo 'the message you saw' | ./unfmt -C path/to/repo
./demo.sh
```

Exit `0` if at least one template matches, `1` if none, `2` on usage error. `--json` is the machine form. `--exact` disables prefix/suffix (span) matching.

## Examples

```bash
# Rust format! / anyhow — bind the hole
./unfmt -C fixtures '`git apply --reverse` failed: patch does not apply'
```

```
repo/app.rs:4:17: brace  score=0.724  full
  template: `git apply --reverse` failed: {1}
  {1} = patch does not apply
```

```bash
# Swift interpolation, including nested quotes inside \(…)
./unfmt -C fixtures 'presentThreshold must be greater than absentThreshold (got 0.3 vs 0.9)'
```

```
repo/log.swift:6:9: swift  score=1.300  full
  template: presentThreshold must be greater than absentThreshold (got \(presentThreshold) vs \(absentThreshold))
  {presentThreshold} = 0.3
  {absentThreshold} = 0.9
```

```bash
# JS/TS template literal, JSON for pipelines; also accepts a log prefix
echo "cannot read 'foo/bar.ts' (code 2)" | ./unfmt -C fixtures --json
./unfmt -C path/to/kizu '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
```

```
src/git/revert.rs:46:18: static  score=1.381  span  span=27-64
  template: failed to spawn `git apply --reverse`
  prefix: 2026-08-19T23:50:01Z ERROR
```
