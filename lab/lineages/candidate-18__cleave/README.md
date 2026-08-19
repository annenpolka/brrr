# cleave

Partition a function into the **argument worlds** its callers actually inhabit, then say whether tests and production live in the same ones.

Coverage tells you a line ran. `grep fn(` lists every site. Neither answers: *tests call `isBrowser("Chrome")`; production calls `isBrowser(currentApp)` — do they inhabit the same function?*

## Install / run

```bash
chmod +x ./cleave
./cleave --help
./demo.sh
```

Requires Python 3.9+.

## Interaction

```
cleave [-C PATH] [FN...]          # human report (tilts by default)
cleave --check --porcelain        # CI: exit 1 if any tilt
cleave --json isBrowser | jq .
cleave --tsv -C repo | awk -F'\t' '$1=="tilt"'
```

| code | meaning |
| --- | --- |
| 0 | ok, or `--check` with no tilts |
| 1 | `--check` found at least one tilt |
| 2 | usage / IO error |

Stdout is the report. Stderr is skip noise.

Worlds are clusters of call sites by observed arguments: a literal (`timeout=0`), a default (`timeout=30d`), or dynamic (`host=*`). A **tilt** is a world tests inhabit that production does not, or the reverse.

## Examples

Synthetic fixture — production uses `timeout=0`, tests never do:

```bash
./cleave -C fixtures/ugly connect
# connect  src/connect.py:6  (host, timeout=30)  TILT
#   world  {host="localhost", timeout=30}         test:3
#   world  {host=*, timeout=0}                    prod:1
#   tilt   prod-only-const  timeout  prod=[0]  tests=[30]
#   tilt   prod-open        host  tests=["localhost"]  prod=*
```

A real gap in sitbone: production will accept six browser names the tests never pass:

```bash
./cleave -C ~/src/sitbone isBrowser
# members browsers  appName  10
#   hit=["Arc","Firefox","Google Chrome","Safari"]
#   miss=["Brave Browser","Chromium","Microsoft Edge","Opera","Orion","Vivaldi"]
```

CI filter:

```bash
./cleave -C . --check --porcelain
# tilt<TAB>isBrowser<TAB>unwitnessed-member<TAB>appName in browsers miss=[...]
```
