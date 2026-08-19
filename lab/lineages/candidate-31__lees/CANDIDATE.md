# candidate-31 — lees

## Primitive

A test oracle is a mixture of specification and the machine that recorded it. `lees` subtracts the live env/host dictionary (and path/clock/platform shapes) so two transcripts can be compared **modulo substitution**. Empty residue means the test is not failing — the machines differ.

## Four primitives considered

1. **lees** — factor oracle/transcript/failure into spec vs env/machine sediment; unify two sides; probe which env axes a command actually reads. **Implemented.**
2. **par** — two-file unifier as a standalone verb. Same primitive as lees; absorbed as `lees --par` instead of a second binary.
3. **embark** — emit a GitHub Actions job / container spec from `--probe` axes. **Discarded:** clutch already discarded `habitat` as conventional (portability linters, Docker, Nix). Named gap CI-reify is a product, not a new object.
4. **spoil** — age of an expected value measured in mutations of the code it watches. **Discarded:** adjacent to generated-file freshness (kiln/clutch), a niche the assignment said is filled.

`vial` (persist a four-facet capsule of cmd × env × machine × oracle) was a fifth that collapsed into record/replay, which prior art already names.

Not leftover names, not inverse-printf, not wait-for graphs, not generation receipts.

## Why this might not exist

The daily CI-red / local-green loop is four ledgers: `.env`, `runs-on`, the test command, the snapshot. Developers mentally subtract `$HOME`, the runner hostname, and the clock, then decide whether the remainder is a bug. `diff` does not know the dictionary. Snapshot serializers try to normalize *going forward*; they do not audit the goldens you already committed. `due` (if it lands) is `ldd` for getenv *names*. lees is the other half: **the values those names left in the oracle**, and the verdict when two recordings unify.

Coverage, mutation testing, and `alibi` ask whether a test vetoes production. lees asks whether a red test vetoes *anything*, or only the machine.

## How to run

From this worktree root:

```bash
./demo.sh
./lees --help
./lees --self-test
python3 -m unittest discover -s tests -q
./lees --check --scan -C /path/to/repo
./lees --par fixtures/local.snap fixtures/ci.snap
pytest -q | ./lees --from-fail
./lees --probe -- python3 fixtures/echo_world.py
```

## Empirical transcript

### v0.1 (`d3e561d`) — fixture demo PASS, sitbone `--check` lies

`./demo.sh` exit 0, `passed=23 failed=0`. Self-test 24/24. Unittest 17/17.

`--par` on the alice/CI pair:

```
lees  --par  fixtures/local.snap  fixtures/ci.snap  verdict=MACHINE
substitutions:
  PATH     /Users/alice      →  /home/runner
  PATH     /Users/alice/proj →  /home/runner/work/proj
  CLOCK    2026-08-20T01:14:03Z → 2026-08-20T09:00:11Z
empty residue — the oracles agree modulo env/machine
```

Same pair with `timeout: 60` on the CI side → `MIXED`, residue `30` vs `60`, `--check` exits 1. Numeric-only 30 vs 60 → `SPEC`. `--probe` on `echo_world.py` → `ENV-TIED` (HOME/TZ/USER raw-flip, spec-stable); `echo_spec.py` → `STABLE`.

Dogfood `--scan --check` (this host, 2026-08-20):

| repo      | tainted | clean | note                                      |
| --------- | ------- | ----- | ----------------------------------------- |
| kizu      | 0       | 18    | tests do not leak this HOME               |
| sitbone   | **4**   | 21    | USER=`annenpolka` in GitHub title fixtures |
| voidtrace | 0       | 65    | goldens are synthetic numbers             |
| tenaoshi  | 0       | 17    | oracles portable                          |
| skills    | 0       | 0     | no oracle-like filenames (honest miss)    |

sitbone `WindowTitleParserTests.swift:10`:

```
from: "GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome"
```

v0.1 called that `ENV USER=annenpolka` and failed `--check`. The test is *about* that identity. Fork the repo, the literal stays, `$USER` is someone else, the suite is still green. Not a recording leak.

`--from-fail` on `fixtures/pytest_fail.txt` emitted the same MACHINE pair **twice** (AssertionError line and the `E +/-` dump).

`--paths` shared argparse dest with the positional file list; `--scan --paths` silently dropped the flag.

### v0.2 — fixture rule + `--foreign` + dedup

USER/LOGNAME/USERNAME hits whose surrounding token is a URL or `owner/repo` become `kind=fixture`. `--check` ignores them. `--paths` renamed `--foreign` (own dest). Windows path regex no longer eats Rust `e:\\n`. `--from-fail` dedups identical consecutive pairs.

After:

```
$ ./lees sitbone/Tests/SitboneCoreTests/WindowTitleParserTests.swift
lees  …/WindowTitleParserTests.swift  CLEAN
  FIXTURE  USER=annenpolka  L10:29

$ ./lees --scan --check -C sitbone ; echo $?
0
# sitbone tainted=0 clean=25

$ ./lees --foreign kizu/src/hook/tests.rs
lees  …/tests.rs  CLEAN
  PATH  /tmp/foo.rs           L13
  PATH  /home/user/project    L15
  PATH  /home/user            L33
# 46 foreign path oracles across kizu tests; --check still 0
```

`./demo.sh` → `passed=24 failed=0`. Unittest 19/19.

## Dogfood targets

- `fixtures/` — alice vs runner snaps, pytest/cargo dumps, ugly unicode/space paths, env-printing scripts
- This host's live `$HOME`/`$USER` written into `demo-tmp/live.snap` (TAINTED) vs a portable twin (CLEAN)
- `/Users/annenpolka/ghq/github.com/annenpolka/{kizu,sitbone,voidtrace,tenaoshi}` `--scan --check`; kizu `--foreign`

## Surprises

- sitbone's "taint" was the author's GitHub handle used as a *site fixture* for window-title parsing. Coverage-adjacent tools would also call it a string. The missing distinction is **recording leak vs identity-as-data**.
- kizu tests lock `/home/user` and `/tmp/*.rs` as path oracles. That is foreign-path sediment by shape, but it is the spec of a path parser. `--check` stays quiet; `--foreign` reports 46 hits.
- voidtrace goldens (`data/fixtures/golden/*.expected.json`) are clean: numbers and rule ids, no host. The well-written oracle is the empty case, which is a result.
- `"" in "_-"` is True in Python. Short facts (`TZ=UTC`) at EOL never stained until the boundary check compared characters, not substrings. That also blocked `--probe` from classifying TZ as spec-stable.

## Failures

- `skills` has no `test_*` / `*Tests*` / golden files. `--scan` says `no oracle-like files`. `--all` would walk the scripts and mostly lie.
- `--from-fail` still only knows pytest / unittest / cargo / one XCTest shape. Swift `XCTAssertEqual` dumps that wrap values across lines are silent.
- `--probe` overlays HOME/TZ/LANG/USER only. Locale *messages*, cwd, and hostname need `unshare`/`scutil` and are not done.
- `--foreign` `/tmp/foo.rs` is indistinguishable from a real temp-path leak without a test-role heuristic.
- Scanning `src/hook/tests.rs` only because `Tests` matches case-insensitively inside `tests.rs`. A file named `attest.rs` would also qualify. Fine for now.

## Suggested mutations

- `--visa`: emit the machine condition an oracle implies (`HOME=/Users/alice`, `platform=Darwin`) as a skip/apply predicate, the durable pin named-gap for oracles.
- Join with `alibi`: splice tests onto old production, then lees the failure — LOCKED-and-MACHINE vs LOCKED-and-SPEC.
- Parse only assertion *literals* (not comments) so kizu `attach.rs` docs about `/Users/John Doe` stay silent even under `--foreign`.
- `--probe` matrix as JSONL a CI job can consume without becoming embark.
- Infer a second dictionary from the *other* transcript (CI log) so `--par` names `{HOME_A}`/`{HOME_B}` even when neither value is live.

## Kill / keep

**Keep.** The object is new: a verdict that is not a bool but a substitution. sitbone dogfood produced a false TAINTED that the fixture rule then named correctly; kizu `/home/user` is the honest foreign-path report a portability linter would drown in `/usr/bin`. Not `diff`, not `direnv`, not snapshot serializers.
