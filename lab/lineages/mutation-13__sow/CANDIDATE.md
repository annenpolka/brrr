# mutation-13 — sow

## Primitive

Production callers are the source of truth. `sow` partitions a function into the **argument worlds production actually inhabits**, subtracts values tests already pin, and emits the remainder as **test-generator input** (JSON / NDJSON / `--emit pytest` stubs). Test-only worlds are silent. There is no tilt report.

## Why this might not exist

`cleave` (candidate-18) joined test and production inhabitance and printed tilts both ways: prod-only-const, test-only-const, prod-open. The daily use of that join is one-sided. Nobody wants a list of extra test literals. They want the tests they still owe production: `timeout=0`, `duration=1`, `"Brave Browser"`, `"Ghostty AppleScript split"`. Coverage cannot phrase a missing *value*. `grep fn(` cannot. Mutation testing asks a different question.

The missing Unix verb is **production argument worlds as a fixture stream**, not a test/prod comparison.

Flipped assumption: kill the comparison. Tests are a subtract filter, not a peer.

## How to run

```bash
./sow --help
./demo.sh
./sow --self-test
./sow -C fixtures/ugly connect
./sow --json -C /path/to/repo isBrowser
./sow --ndjson -C /path/to/repo | jq -r 'select(.generable) | .suggest'
./sow --emit pytest -C /path/to/repo isBrowser
./sow --check --porcelain -C /path/to/repo
```

Exit 0 on success. `--check` exits 1 if any due fixture. Errors exit 2.

## Empirical transcript

### Before the improvement (v0.1, commit b499a72)

Ugly fixture already worked as generator input: `connect` due `{timeout=0}` and `{host="db.example.com"}`; `isBrowser` due members Brave/Edge; porcelain `fixture` rows; no `tilt` language; test `localhost` silent. `--emit pytest` produced `WindowTitleParser.isBrowser("Brave Browser")`.

Real repos, 2026-08-20:

```
sitbone    files=49  defs=409  calls=3072  prod_fns=133  due_fns=114  due=129  generable=59
kizu       files=70  defs=931  calls=10327 prod_fns=325  due_fns=235  due=310  generable=94
```

sitbone `isBrowser` was already the right *output* (six member fixtures, not a tilt):

```
WindowTitleParser.isBrowser  …  6 due
  members browsers  appName  10  have=[Arc, Firefox, Google Chrome, Safari]
    miss=[Brave Browser, Chromium, Microsoft Edge, Opera, Orion, Vivaldi]
  due  member  {appName="Brave Browser"}  test_isBrowser_appName_Brave_Browser
  …
```

`extractSiteName` has zero production callers → silent (cleave reported it as a subject with tests and no prod; sow refuses).

### v0.1 failures on real queries

1. **Rust lifetimes swallowed the rest of the file.** `fn new(prompt: &'a str, items: &'a [&'a str], …)` tokenized `'a str, items: &'` as a string. `_skip_balanced` never saw `)`, `SelectState::new` became one def spanning to EOF. kizu `src/prompt.rs`: 5 defs instead of 44. `apply_select_key` did not exist as a subject.
2. **Same-file `#[cfg(test)]` literals were "production worlds".** `truncate_to_width("hello", 10)` at `prompt.rs:534` (a unit test) was a due fixture. Tests at the bottom of production files were not a test path.
3. **Mixed worlds were not generable.** Production `record(site, phase, duration: 1)` is `{duration=1, phase=*, site=*}` — the one value tests never pass (`SiteObserverTests` uses 5, 10, 20, 30, 50, 60, 100, 200, 300). v0.1 marked it `dyn` and `--emit` skipped it.
4. **kizu `run_split_command`** production contexts Ghostty/kitty/tmux/zellij were the same: `{cmd=*, context="tmux split-window"}` skipped by emit. Tests only pass `"sh failing split"` / `"sh ok"`.
5. **Zero-arg `{ }` worlds** (`startTickLoop`, `saveProfiles`, …) counted as generable fixtures with nothing to pin. sitbone generable=59 was mostly these.
6. **Unicode suggest names collided.** `←` `↩` `✕` all slugged to `x`.

### After the improvement (v0.2)

Fixes: tokenize Rust `'` as lifetime/char *before* the string scanner; a world is generable when production pinned at least one literal (dyn slots emit as `...`); drop zero-arg worlds; keep CJK and name arrows in slugs.

```
sitbone    due_fns=114→65   due=129→80   generable=59→24
kizu       defs=931→1022    prod_fns=325→382  due_fns=235→241  due=310→332  generable=94→111
```

sitbone `record` after — the clock tests never inhabit, now a stub:

```
SiteObserver.record  …  (site, phase, duration)  1 due
  due  world   {duration=1, phase=*, site=*}
         test_record_site_phase_duration_1

./sow --emit pytest -C sitbone record
# def test_record_site_phase_duration_1():
#     SiteObserver.record(..., ..., duration: 1)
```

kizu `run_split_command` after:

```
./sow --emit pytest -C kizu run_split_command
# run_split_command(..., "Ghostty AppleScript split")
# run_split_command(..., "kitty @ launch")
# run_split_command(..., "tmux split-window")
# run_split_command(..., "zellij run")
```

`truncate_to_width` no longer lists `"hello"` / `"abcdef"` from `#[cfg(test)]`. Remaining dues are production ANSI help strings. `apply_select_key` is a subject again. `counterItem` suggest names distinguish `left` / `enter` / `cross`.

## Dogfood targets

- `fixtures/ugly` — Python, JS, Rust (incl. lifetimes), Swift; unicode path; colon filename; spaces; comments; nested git
- sitbone, kizu (read-only)

## Surprises

- sitbone `extractSiteName` is a public function with careful tests and **no production call sites**. sow is silent. Coverage would still be green. The live path is `SiteResolver`.
- Production `SiteObserver.record` always passes `duration=1` (one-second ticks). Tests never pass 1. Once mixed worlds are generable, that is a one-line stub, not a dyn hole.
- kizu tests for `run_split_command` pin `"sh ok"` / `"sh failing split"`. Production never uses those strings; production uses the four terminal backends. cleave called that a tilt. sow calls it four fixtures.
- Colorizer helpers (`c_dim`, `c_bold`) inhabit many production string worlds. They are honest dues and low-value tests. Ranking still leads with collection members (`isBrowser` is sitbone's first row).

## Failures (still open)

- Same-named methods across types still share unprefixed calls.
- JS/TS options-bag worlds remain coarse when values are identifiers (`{ scenario, catalog, ruleset }`).
- Display wrappers emit one fixture per chrome string. No heuristic drops them.
- `--emit pytest` is a stub (call with production values, no assertion). A generator still has to write the oracle.
- Dynamic-only worlds (`{site=*}` with no pinned literal and no collection) stay non-generable. That is correct; there is nothing to paste.

## Suggested mutations

- Rank / hide display-wrapper functions (single string param, name matches `c_*` / `fmt_*`).
- `--emit` for XCTest / `#[test]` matching the definition language, not just pytest.
- Resolve `self`/`this` so overloaded methods stop sharing calls.
- Join with `seep`: the timeout=0 world is the one that does IO — emit that fixture first.

## Kill / keep

**Keep.** The flip is real: the same sitbone finding (six untested browser names, duration=1) is now a fixture stream a generator can consume, and kizu's four terminal backends become four stubs instead of a tilt sentence. v0.2 recovered 91 kizu defs by not reading lifetimes as strings — the primitive got sharper, not wider.
