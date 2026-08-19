# lees

Subtract **env/machine sediment** from a test oracle. What remains is the specification.

A snapshot, golden, or assertion dump is a recording of a particular machine. `lees` builds a dictionary from the live process environment plus host facts (HOME, USER, hostname, cwd, git root, platform, interpreter), stains the oracle, and classifies the rest. Two transcripts that unify under that substitution are not a failing test — they are the same spec on two machines.

## Install / run

Python 3.10+, stdlib only.

```bash
chmod +x ./lees
./lees --help
./demo.sh
./lees --self-test
```

## Three examples

### 1. Is this snapshot portable?

```bash
./lees --check tests/snapshots/cli.snap
# lees  tests/snapshots/cli.snap  TAINTED
#   ENV      HOME=/Users/alice  L2:7
#   MACHINE  HOST=alice-mbp     L3:7
```

`--check` exits 1 on current-machine leaks (a CI gate). `--holes` rewrites hits to `{HOME}` / `{USER}` / `{HOST}`.

### 2. Local actual vs CI expected

```bash
./lees --par local.snap ci.snap
# verdict=MACHINE
# substitutions:
#   PATH     /Users/alice/proj  →  /home/runner/work/proj
#   MACHINE  alice              →  runner
# empty residue — the oracles agree modulo env/machine
```

`timeout: 30` vs `timeout: 60` on top of those substitutions is `MIXED` (or `SPEC` if nothing else differed). `--check` exits 0 for `MACHINE`/`ENV`/`CLEAN`, 1 for `SPEC`/`MIXED`.

### 3. Pipe a red test, or probe which env axis the command reads

```bash
pytest -q | ./lees --from-fail
# pair  pytest  verdict=MACHINE
#   PATH  /Users/alice/proj  →  /home/runner/work/proj

./lees --probe -- python3 fixtures/echo_world.py
# verdict=ENV-TIED
#   env:HOME    raw=FLIP  spec=STABLE
#   env:TZ      raw=FLIP  spec=STABLE
```

`--probe` tilts HOME / TZ / LANG / USER, then **unifies the two outputs** so a printed `$HOME` is `ENV-TIED` (raw flip, spec stable), not a behavior change.

## Other verbs

```bash
./lees --scan -C /path/to/repo --check          # oracle-like files only
./lees --foreign --scan -C /path/to/repo        # also /Users /home /tmp shapes
./lees --dump-dict --json                       # the live dictionary
./lees --par a b --json                         # compose

`--check` fails only on current-machine leaks (HOME, cwd, hostname, standalone USER). A USER token sitting inside `github.com/you/repo` or an `owner/repo` title is a **fixture**, not sediment — the test is about that identity, it was not recorded from `$USER`.
```

Exit `2` on usage error. Porcelain TSV: `--porcelain`.
