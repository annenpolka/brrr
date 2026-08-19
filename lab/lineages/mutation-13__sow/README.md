# sow

Emit the **argument worlds production actually inhabits** as test-generator input.

`cleave` asked whether tests and production live in the same worlds. `sow` kills that comparison. It looks only at production callers, subtracts values the tests already pin, and prints the leftover worlds as fixtures — one record a generator (or `--emit pytest`) can turn into a test.

Coverage says a line ran. `grep fn(` lists sites. Neither answers: *production calls `isBrowser(currentApp)` against a 10-name set; the tests never pass `"Brave Browser"` — here is the fixture.*

## Install / run

```bash
chmod +x ./sow
./sow --help
./demo.sh
```

Requires Python 3.9+.

## Interaction

```
sow [-C PATH] [FN...]          # due production worlds (human)
sow --json isBrowser           # test-generator input
sow --ndjson | jq -r .suggest  # one fixture object per line
sow --porcelain                # TSV fixture rows
sow --emit pytest isBrowser    # stub tests for generable fixtures
sow --check --porcelain        # CI: exit 1 if any due fixture
```

| code | meaning |
| --- | --- |
| 0 | ok, or `--check` with nothing due |
| 1 | `--check` found due fixtures |
| 2 | usage / IO error |

Stdout is the fixture stream. Stderr is skip noise.

A **due** fixture is a production argument world (literal, default, or collection member) that no test call inhabits. Test-only worlds are silent. Functions with no production callers are silent. Mixed worlds (`duration=1` plus dynamic `site`) are still generable: dyn slots become `...` in `--emit`.

## Examples

Synthetic fixture — production uses `timeout=0` and `db.example.com`; tests only ever pass `localhost`/30:

```bash
./sow -C fixtures/ugly connect
# connect  src/connect.py:6  (host, timeout=30)  2 due
#   due  world   {host="db.example.com", timeout=30d}
#          test_connect_host_db_example_com_timeout_30  src/connect.py:21
#   due  world   {host=*, timeout=0}
#          test_connect_timeout_0_host  src/connect.py:17
```

sitbone production ticks `record(..., duration: 1)`; tests never pass 1:

```bash
./sow --emit pytest -C ~/ghq/github.com/annenpolka/sitbone record
# def test_record_site_phase_duration_1():
#     SiteObserver.record(..., ..., duration: 1)
```

A real sitbone hole — six production browser names the tests never pass:

```bash
./sow -C ~/ghq/github.com/annenpolka/sitbone isBrowser
# members browsers  appName  10  have=[Arc, Firefox, Google Chrome, Safari]
#   due  member  {appName="Brave Browser"}
#   due  member  {appName="Chromium"}
#   … Opera, Orion, Vivaldi, Microsoft Edge

./sow --emit pytest -C ~/ghq/github.com/annenpolka/sitbone isBrowser
# def test_isBrowser_appName_Brave_Browser():
#     WindowTitleParser.isBrowser("Brave Browser")
```

Pipe the generator input:

```bash
./sow --ndjson -C . isBrowser | jq -r 'select(.generable) | .args'
```
