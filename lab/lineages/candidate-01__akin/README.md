# akin

Find files that were copied, not branched — recover the missing merge-base (the source blob at the split) and port later drift with a 3-way merge.

## Install / run

```sh
chmod +x ./akin ./demo.sh
./akin -C /path/to/repo --pretty
./demo.sh
```

Requires Python 3 and `git`. No other dependencies.

Default output is TSV. `--pretty` for humans, `--json` for machines.

Exit codes: `0` success; `1` with `--check` when drifted kin exist, or `--port` with conflicts; `2` usage/git error.

Detectors (all on by default): last simultaneous identical blob; git copy detection (`-C --find-copies-harder`); same-basename similarity at first appearance.

## Examples

List drifted twins, then fail CI if any exist:

```sh
./akin -C ~/src/kizu --pretty
./akin -C ~/src/kizu --check
```

Inspect a known split and port unique changes from `FROM` onto `TO` (3-way merge; base is the source blob at copy time):

```sh
./akin -C ~/src/kizu src/init.rs src/init/install.rs
./akin -C ~/src/kizu --port src/init.rs src/init/install.rs
./akin -C ~/src/kizu --diff src/init.rs src/init/install.rs
```

JSON, identical current copies, and detector knobs:

```sh
./akin --json --identical --glob '*.swift' --min-score 60
./akin --no-copies --no-similar          # exact shared-blob only
```
