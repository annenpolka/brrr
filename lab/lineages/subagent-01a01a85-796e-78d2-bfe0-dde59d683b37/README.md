# akin

Find files that once were the same git blob — a copy, not a branch — and treat that blob as the merge-base git never recorded.

## Install / run

```sh
chmod +x ./akin
./akin -C /path/to/repo
./demo.sh
```

Requires Python 3 and `git`. No other dependencies.

Exit codes: `0` success; `1` with `--check` when drifted kin exist, or `--port` with conflicts; `2` usage/git error.

Default output is TSV (header + rows). `--pretty` for humans, `--json` for machines.

## Examples

List drifted twins in this repo, then fail CI if any exist:

```sh
./akin -C ~/src/sitbone --pretty
./akin -C ~/src/sitbone --check
```

Inspect one pair and port unique changes from `util.sh` onto its frozen copy (3-way merge with the last shared blob as base):

```sh
./akin -C ./fixture util.sh frozen.sh
./akin -C ./fixture --port util.sh frozen.sh
```

JSON, path filter, currently-identical copies:

```sh
./akin --json --identical --glob '*.swift' --exclude '*/vendor/*'
```
