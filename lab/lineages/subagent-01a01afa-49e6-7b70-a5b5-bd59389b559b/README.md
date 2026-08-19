# invert

Inverse printf as a Unix filter, with named hole bindings. You have a runtime string; templates arrive on a stream. The tool does not walk a repository.

Mutation of **sluice**: same stream contract (`rg | invert`, `git log -p | invert`, `--files`, `--chdir` is a path prefix). The extra verb is **name the holes** (`{rest}`, `\(oldPhase.rawValue)`, `${snapshot.id}`) and bind them. Timestamp wrappers stay on the query as a reported **span**, not a stripped prefix.

## Install / run

```bash
chmod +x invert
./invert --help
./demo.sh
```

Single Python 3 file. No dependencies.

```bash
rg -n --type rust 'format!|anyhow!' ~/src/kizu \
  | ./invert '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
# src/git/revert.rs:46:18: score=0.66 … via=span
#   tmpl:  failed to spawn `git apply --reverse`
#   prefix: 2026-08-19T23:50:01Z ERROR

rg -n --type swift 'awayRecovered' ~/src/sitbone \
  | ./invert 'transition focused → idle reason=timeout idle=12s deserted=0 driftRecovered=0 awayRecovered=0'
# SitboneCore.swift:554:35 holes=7
#   {oldPhase.rawValue} = focused
#   {idle} = 12

rg -n --type swift 'camera presence' ~/src/sitbone \
  | ./invert 'camera presence enabled'
#   tmpl:  camera presence {self.isCameraEnabled}
#   {self.isCameraEnabled} = enabled
```

`--exact` refuses leftover prefix/suffix. `--open auto` (default) hydrates files the producer named so multiline Swift is whole. Directories are refused.

Exit `0` if every argument matched, `1` on a miss, `2` on usage.
