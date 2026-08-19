# mutation-27 — visa

## Primitive

An oracle implies a machine. `visa` emits that condition (required env/paths/users) as a skip/apply predicate. `lees` compared two transcripts modulo a live dictionary; visa is unary: one recording in, the visa it demands.

## Four primitives considered

1. Keep `lees` and add `--visa` as a flag. *Discarded: that keeps subtraction + two transcripts at the centre.*
2. **visa / implied machine condition** — implemented. The missing verb is "what machine does this golden require?", not "do these two goldens unify?".
3. Join with alibi (LOCKED-and-MACHINE). *Later; needs a splice first.*
4. Parse only assertion literals. *Still a later mutation; file-role + textbook paths were the first real miss.*

## Why this might not exist

Snapshot serializers normalize *going forward*. `diff` does not know HOME. pytest `skipif` and GHA `runs-on` are written by hand, after someone already decided the golden is machine-tied. The daily loop is: look at a red CI log, mentally reconstruct "this expected value was recorded on Alice's Mac", then skip or rewrite. Nobody emits that reconstruction as an object.

`lees` answers "is this residue empty?" visa answers "what skip would have made the residue irrelevant?" That is the durable-pin named-gap for oracles: the condition travels with the golden.

Discarded as conventional: wrapping `uname`, generating a Dockerfile, CI-reify products (clutch already killed `habitat` / `embark`). `--emit gha` is a coarse projection of the visa, not a product.

## How to run

From this worktree root:

```bash
./demo.sh
./visa --help
./visa --self-test
python3 -m unittest discover -s tests -q
./visa fixtures/local.snap
./visa --apply --match fixtures/local.snap
./visa --emit shell fixtures/ci.snap
./visa --scan -C /path/to/repo --porcelain
pytest -q | ./visa --from-fail
```

## Empirical transcript

### v0.1 (`480b260`) — unary visa works; kizu textbook paths lie

`./demo.sh` exit 0, `passed=28 failed=0`. Self-test 31/31. Unittest 16/16.

`fixtures/local.snap` is a skip this host does not hold:

```
visa  fixtures/local.snap  BOUND
  require  HOME=/Users/alice
  require  platform=Darwin
  apply    [ "$(uname -s)" = Darwin ] && [ "${HOME}" = /Users/alice ]
  match    MISS
           HOME want=/Users/alice have=/Users/annenpolka
# --apply exit 1
```

`fixtures/ci.snap` → `CI=github-actions` `HOME=/home/runner` `gha=ubuntu-latest`.
`fixtures/spec_only.snap` → OPEN, `--apply` 0.
`fixtures/conflict.snap` (two labeled homes) → UNSAT, `--apply` 2.
Live `demo-tmp/live.snap` with this `$HOME` → BOUND, `--apply` 0 MATCH.

The flip vs lees is already visible on sitbone: we never stain live `$USER`, so `annenpolka/sitbone` in a window title is not a USER visa.

Dogfood `--scan` (this host, 2026-08-20):

| repo    | BOUND | OPEN | SPEC | UNSAT | note |
| ------- | ----- | ---- | ---- | ----- | ---- |
| sitbone | 0     | 25   | 0    | 0     | GitHub titles OPEN (lees v0.1 would have USER-tainted) |
| kizu    | **2** | 13   | 2    | **1** | textbook paths treated as recordings |

kizu misses:

- `src/hook/tests.rs` BOUND `HOME=/home/user` `platform=Linux` — the spec of a path parser.
- `src/init/tests.rs` UNSAT Darwin `/Users/John Doe` vs Linux `/home/ev'an` — the spec of a shell quoter, both layouts on purpose.
- `tests/e2e/reactive.test.ts` BOUND Darwin because a comment said `macOS PollWatcher`.

`--from-fail` on `fixtures/pytest_fail.txt` visad the *expected* side: Darwin `/Users/alice/proj`, not a two-transcript residue.

### v0.2 — payload vs recording

Test/source files: textbook identities (`user`, `alice`, `John Doe`), spaces/apostrophes in home components, and bare `macOS` words are **payload**. Snapshots still record (alice in `local.snap` stays BOUND). All axes derived from a payload path demote together, otherwise `HOME=/home/user` became payload while `platform=Linux` from the same span stayed a skip.

After:

```
$ ./visa kizu/src/hook/tests.rs
visa  …/hook/tests.rs  SPEC
  (path/user strings are spec payload, not a skip)
  apply    true

$ ./visa kizu/src/init/tests.rs
visa  …/init/tests.rs  SPEC
  witness  payload  HOME=/Users/John Doe
  witness  payload  HOME=/home/ev'an
  apply    true     # was UNSAT

$ ./visa sitbone/…/WindowTitleParserTests.swift
visa  …/WindowTitleParserTests.swift  OPEN

$ ./visa --scan --porcelain -C kizu
# BOUND=0 OPEN=13 SPEC=5 UNSAT=0
$ ./visa --scan --porcelain -C sitbone
# BOUND=0 OPEN=25 SPEC=0 UNSAT=0
```

`./demo.sh` → `passed=28 failed=0`. Unittest 19/19. A non-textbook `/Users/annenpolka` inside `tests.rs` still BOUND — recording leaks remain a visa.

## Dogfood targets

- `fixtures/` — alice Darwin snap, GHA runner snap, portable spec, conflicting homes, quoting payload, tmp-only, pytest fail, ugly unicode/spaces
- This host's live `$HOME`/`$USER` written into `demo-tmp/live.snap` (MATCH) vs alice (MISS)
- `/Users/annenpolka/ghq/github.com/annenpolka/{kizu,sitbone}` `--scan`

## Surprises

- sitbone needed no fixture rule for USER: not staining the live dictionary is the whole flip. lees v0.1's false TAINTED cannot happen here.
- kizu `init/tests.rs` is the object lesson: two layouts in one file look like UNSAT (broken recording) until you notice the test is *about* quoting both. Multi-layout in a snapshot stays UNSAT (`conflict.snap`); in source it is SPEC.
- Bare `macOS` in an e2e comment is not a Darwin visa. kind=platform in test source is payload; `os: Darwin` in a `.snap` still records.
- `--emit gha` cannot express `HOME=/Users/alice`. The shell/pytest predicate is the real visa; runs-on is a coarsening. embark stays discarded.

## Failures

- `skills` was not scanned (no kizu/sitbone-like oracles in this dogfood pair). `--scan` still says `no oracle-like files` on trees without test/golden names.
- Assertion strings that wrap across lines are not parsed; `--from-fail` still knows pytest / unittest / cargo / one XCTest shape.
- `/home/ev'\''an` escaped inside a Rust raw string still leaves a short `/home/ev` payload witness. Harmless (len≤2 → payload) but noisy.
- Comments vs assertion literals: `attach.rs` docs about `/Users/John Doe` are silent only because `--scan` skips non-oracle names. `--all` would still see them; literal-window is a later mutation.
- HOST is reported soft and not part of `--apply`. Laptop rename would otherwise skip a still-valid HOME visa.

## Suggested mutations

- Assertion-literal window so comments about `/Users/John Doe` stay silent even under `--all`.
- Infer a visa from the *actual* side of `--from-fail` as well, and pair them: two visas, not lees residue.
- `--held`-style: given a visa, walk history for goldens that newly acquired it (when the test became machine-tied).
- Join with alibi: splice tests onto old production, then visa the failure (LOCKED-and-BOUND vs LOCKED-and-OPEN).

## Kill / keep

**Keep.** The object is new: a skip/apply predicate implied by one oracle, not a bool and not a two-transcript residue. sitbone is OPEN without a live-USER stain; kizu v0.1 false BOUND/UNSAT on quoting fixtures became SPEC once path-level payload demoted platform/layout with HOME. Not `uname`, not `direnv`, not snapshot serializers, not lees `--par`.
