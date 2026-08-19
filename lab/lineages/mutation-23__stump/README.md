# stump

Inverse printf as a Unix filter, with named hole bindings. You have a runtime string — including a **truncated** one; templates arrive on a stream. The tool does not walk a repository.

Mutation of **invert**: same stream contract (`rg | stump`, `git log -p | stump`, `--files`, `--chdir` is a path prefix). The extra verbs are:

- bind a **prefix of a template instance** and say `truncated:`
- refuse rustc `--> path:line` as a locator, not a query
- `--any` stops after the first hit
- binary stdin fails closed
- a no-hole static that is only a prefix of the paste cannot outrank a holed source

## Install / run

```bash
chmod +x stump
./stump --help
./demo.sh
```

Single Python 3 file. No dependencies.

```bash
rg -n --type swift 'awayRecovered' ~/src/sitbone \
  | ./stump 'transition focused → idle reason=timeout idle=12s'
# SitboneCore.swift:554:35 holes=7 via=truncated
#   {oldPhase.rawValue} = focused
#   {idle} = 12
#   truncated: deserted={…} driftRecovered={…} awayRecovered={…}

rg -n --type rust 'format!|anyhow!' ~/src/kizu \
  | ./stump '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
#   tmpl:  failed to spawn `{cmd}`
#   {cmd} = git apply --reverse
#   prefix: 2026-08-19T23:50:01Z ERROR
# a documentation decoy "2026-08-19T23:50:01Z ERROR failed to spawn" does not win

./stump --templates src/app.rs -e '   --> src/git/revert.rs:46:18'
# — rustc locator, not a template query

./stump --templates extracted.txt --any < build.log
# prints one hit and stops
```

`--exact` refuses leftover prefix/suffix **and** truncated matches. `--open auto` (default) hydrates files the producer named so multiline Swift is whole. Directories are refused. Binary stdin exits 2 with `stump: binary stdin`, not a traceback.

Exit `0` if every argument matched (`--any` / stdin: if any matched), `1` on a miss, `2` on usage / binary.
