# haunt

Find names that died in git history but still speak in the living tree.

Dead-code tools find living symbols with no references. `haunt` is the inverse: it mines deletions (functions, types, flags, paths) and reports remnants that survived — docs, tests, CI, comments — after the definition is gone.

## Install / run

```bash
chmod +x ./haunt
./haunt --help
./demo.sh
```

Requires Python 3.9+ and `git`. Run it from a repository, or pass `-C path`.

Exit codes: `0` scan ok, `1` with `--strict` when any HAUNT remains, `2` usage/git error.

Stdout is the report (human on a TTY, TSV when piped). Stderr is progress (`-v`).

## Examples

Scan the current branch for leftover mentions of deleted definitions:

```bash
./haunt
```

Did this range leave ghosts? Useful as a PR check:

```bash
./haunt main..HEAD --strict
```

Machine output — leftover docs talking about a deleted CLI flag:

```bash
./haunt --json --kind flag | jq '.[] | {name, still: [.remnants[].path]}'
```

Names that linger only in ExecPlans/ADRs are `ARCHIVE` (hidden by default). Show them with `./haunt --archival`.
