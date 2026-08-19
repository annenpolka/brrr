# lede

Inverse printf as a Unix filter whose truncated match is a **prefix of an instance**. Later holes stay unbound. A middle-drop paste (start + end, no middle) is a miss, not `{to} = idle awayRecovered=0`.

Mutation of **stump**: same stream contract (`rg | lede`, `git log -p | lede`, `--files`, `--chdir` is a path prefix). The flipped kernel:

- truncation is prefix-of-instance, never leftover stuffed into the last hole
- a first-literal prefix with **no bindings** is not a hit
- rustc `--> path:line` is a locator, not a query
- `--any` stops after the first hit
- binary stdin fails closed

## Install / run

```bash
chmod +x lede
./lede --help
./demo.sh
```

Single Python 3 file. No dependencies.

```bash
rg -n --type swift 'awayRecovered' ~/src/sitbone \
  | ./lede 'transition focused → idle reason=timeout idle=12s'
# SitboneCore.swift:554:35 holes=4/7 via=truncated
#   {oldPhase.rawValue} = focused
#   {newPhase.rawValue} = idle
#   {reason.name} = timeout
#   {idle} = 12
#   unbound: {counters.deserted.value} {counters.driftRecovered.value} {counters.awayRecovered.value}
#   truncated: deserted={…} driftRecovered={…} awayRecovered={…}

rg -n --type swift 'awayRecovered' fixtures \
  | ./lede --templates - 'transition focused → idle awayRecovered=0'
# — no template for: transition focused → idle awayRecovered=0
# not {to} = idle awayRecovered=0

./lede --templates src/app.rs -e '   --> src/git/revert.rs:46:18'
# — rustc locator, not a template query
```

`--exact` refuses leftover prefix/suffix **and** truncated matches. `--complete` refuses only truncated matches (timestamp span still hits). `--any --complete` is the first complete instance in a stream. `--open auto` (default) hydrates files the producer named so multiline Swift is whole. Directories are refused. Binary stdin exits 2 with `lede: binary stdin`, not a traceback.

Exit `0` if every argument matched (`--any` / stdin: if any matched), `1` on a miss, `2` on usage / binary.
