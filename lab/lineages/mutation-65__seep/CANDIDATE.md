# mutation-65 — seep

## Primitive

Untested production argument worlds as a **runnable test file**, ranked so **I/O worlds (timeout=0, filesystem, network, getenv of a machine visa) emit first**. Rename-follow is kept: `isWebApp` last week still defines worlds.

## Why this might not exist

`sow` made production worlds into fixture records. `hatch` made the object a test file. `till` followed renames. All three still emit in call-site or label order — `connect("db.example.com")` before `connect(..., timeout=0)`. Coverage, `grep fn(`, and `git log -S` also do not know that the timeout=0 world is the one that flakes and the one no unit test wrote.

The missing Unix verb is **owe the IO world first**, not another coverage number and not a machine visa (that object is visa/oath/stain; seep only *ranks* worlds that carry one).

Flipped assumption: hatch/till emit AST/label order. seep emits the timeout=0 / path world first. `--no-rank` is till. `--no-follow` is hatch. `--check` lists ranked worlds without writing a test file.

## How to run

```bash
./seep --help
./demo.sh
./seep --self-test
./seep -C fixtures/ugly connect          # pytest; timeout=0 first
./seep --no-rank -C fixtures/ugly connect
./seep --emit pytest -C fixtures/rank fetch
./seep --check -C fixtures/rank          # listing, exit 1
./fixtures/rename/build.sh /tmp/seep-rename
./seep --no-follow -C /tmp/seep-rename/leftover isBrowser
./seep             -C /tmp/seep-rename/leftover isBrowser
./seep             -C /tmp/seep-rename/leftover isWebApp
```

Exit 0 on success. `--check` exits 1 if any due fixture. Errors exit 2.

## Empirical transcript

### Before the improvement (v0.1)

Self-test + rank fixture proved the flip. till on ugly `connect` emits `db.example.com` then `timeout=0` (label order). seep emits `timeout=0` first:

```
./seep --emit pytest -C fixtures/ugly connect
# def test_connect_timeout_0_host():          io=timeout
#     pytest.skip('… production pins timeout=0')
# def test_connect_host_db_example_com_timeout_30():  io=net
#     connect(host="db.example.com", timeout=30)

./seep --no-rank --emit pytest -C fixtures/rank fetch
# alpha first

./seep --emit pytest -C fixtures/rank fetch
# def test_fetch_timeout_0_name_omega():     FIRST
#     fetch(name="omega", timeout=0)
```

`--check -C fixtures/rank` lists `timeout` then `visa` (`~/.ssh/id_rsa`) then `fs` then `duration=1` with no io tag. duration=1 is a clock, not timeout=0.

Rename gold held: leftover `isWebApp("Brave Browser")` follows to `isBrowser`; sow/hatch miss; till still emits. sitbone overlay `swift test --filter WindowTitleParserSeepTests`: **Executed 6 tests, with 0 failures**. `--check` lists the six members (no XCTest). `extractSiteName` silent. `record(duration: 1)` is `XCTSkip`, no Swift `...`. kizu `install_claude_code` silent under `--no-follow`, four due worlds with follow.

Census (analysis unchanged from till v0.2; ranking is the new axis):

```
sitbone    files=49  defs=409  calls=3072  prod_fns=133  due_fns=65  due=80  generable=24 aka_fns=4 io_due=4
kizu       files=70  defs=1022 calls=10555 prod_fns=382  due_fns=242 due=335 generable=111 aka_fns=4 io_due=95
tenaoshi   files=25  defs=170  calls=1599  prod_fns=107  due_fns=64  due=94  generable=36 aka_fns=0 io_due=9
```

v0.1 misses on real queries: kizu `install_settings_hook_agent` has `project_root=*` tagged `io=body` because the param name was not in the fs list. CJK `挨拶("世界")` ranked `io=fs` because `\u4e16` backslash looked like a Windows path.

### After the improvement (v0.2)

Fixes: glob `*_root` / `*_path` / `*_dir` as filesystem params; unicode `\uXXXX` is not a Windows path; one hop through callees so `paint(name)` that calls `read_cfg` stains `paint("alpha")` as body-IO; do not treat the subject's own `def fetch(` as HTTP fetch.

```
./seep --report -C kizu install_claude_code
# install_settings_hook_agent  …  4 due
#   aka  install_claude_code → install_settings_hook_agent
#   due  world  {agent_arg="claude-code", … project_root=*}  io=fs
#   due  world  {agent_arg="codex", …}                      io=fs
#   due  world  {agent_arg="qwen", …}                       io=fs
#   due  dyn    {kind=*, scope=*}                           io=body
```

v0.1 said `io=body` on all four. The three worlds that carry `project_root` now queue as filesystem — that is the install that writes the hook. The leftover `{kind=*, scope=*}` world has no path slot; body stain is the honest remainder.

```
./seep --emit pytest -C fixtures/rank paint
# paint("~/.ssh/id_rsa")  io=visa   FIRST
# paint("alpha")          io=body   (one-hop through read_cfg/open)
```

CJK `挨拶("世界")` no longer ranks as fs. sitbone overlay still **Executed 6 tests, with 0 failures**. duration=1 still has no io tag.

Census after glob + one-hop (due counts unchanged; more worlds *classified* as IO):

```
sitbone    io_due=4→9
kizu       io_due=95→171
tenaoshi   io_due=9→20
```

## Dogfood targets

- `fixtures/ugly` — Python, JS, Rust (lifetimes), Swift; unicode path; colon filename; spaces; comments; nested git
- `fixtures/rank` — timeout=0 sorts last alphabetically, first under seep; `~/.ssh/id_rsa` vs `alpha`; duration=1 is not timeout
- `fixtures/rename` — leftover old-name callers + historical-only literals (till gold)
- sitbone `isBrowser` / `record` / `extractSiteName` / `stopSession` (read-only; overlay `swift test`)
- kizu `run_split_command` / `install_claude_code` (read-only)
- tenaoshi `PromptStore.validate` (`source="contracts/prompt.md"` is fs)

## Surprises

- sitbone never renamed `isBrowser`. The six Brave/Chromium/Edge/Opera/Orion/Vivaldi members are still the hatch gold — I/O rank is a no-op on that subject and must stay one.
- `record(duration: 1)` is the production clock tests never inhabit. It is **not** timeout=0. The first version of the ranker had to exclude `duration` or the sitbone clock would have leapt the queue.
- tenaoshi `PromptStore.validate` production pins `source="contracts/prompt.md"` — a real fs world the tests leave open. That is the seep sentence on a tree with `aka_fns=0`.
- kizu `install_claude_code` is still the real-repo rename fixture. v0.1 followed it and then under-ranked the four agent-kind worlds as `body`. v0.2 ranks the three `project_root=*` worlds as `fs`.
- The parser stores CJK as `\u4e16`. v0.1's `_looks_path` treated any backslash as a Windows path. A greeting is not I/O.

## Failures

- Same-named methods across types still share unprefixed calls.
- Instance methods have no `self` construction (`record` cannot be a real call without a `SiteObserver()`).
- JS/TS options-bag worlds remain coarse.
- Whole-tree `--check` is noisy; the useful invocation names a function (or an old name).
- Body-level IO can still stain a world that is not itself a path (`paint("alpha")` is body because the callee opens). That is the seep join; it is also a false-friend when the callee is a display wrapper.
- One hop only. A helper two calls deep from `open` stays unstained.

## Suggested mutations

- Construct `Type()` / use existing test fixtures when the subject is an instance method.
- Append into an existing XCTestCase instead of a sibling `*SeepTests` class.
- Walk `git log -L` / tree-sitter for hops that are not on adjacent def lines.
- Stain through more than one hop; hide display-wrapper functions before a whole-tree file.
- Join with visa only as a skip *comment*, never as the object.

## Kill / keep

**Keep.** The flip is real: till on leftover still emits Brave, and seep on `fetch` emits `timeout=0` before `alpha` while `--no-rank` restores till's order. sitbone still runs 6/6. kizu `install_claude_code` is silence for hatch/sow and four due worlds for till/seep. Kill only if a later generation proves the real object is a patch against the existing test file, not a new file on stdout with a sort key.
