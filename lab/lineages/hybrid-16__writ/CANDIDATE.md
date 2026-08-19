# hybrid-16 — writ

## Primitive

Splice current tests onto old production, then oath the splice failure: **LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-BOUND**. Skip is not a lock. Comments are not oaths. Not a fourth cinch.

## Why this might not exist

alibi (candidate-24) asks whether new tests go red on old production and stops at LOCKED. gage (hybrid-12) visaes the *test file* — unary world of the oracle, so a test that asserts `/tmp/x` is LOCKED-and-OPEN even when old production returned this `$HOME`. troth (mutation-89) oaths a dump you already have: `--apply` is `OPEN expected ∪ ACTUAL-BOUND-if-this-host`. Nobody splices *then* pairs the fail.

Concatenation is `alibi && troth --from-fail`: you still paste a dump, and gage still cannot see an OPEN test whose *actual* leaked a machine. The missing verb is the joint occupancy: **the lock whose failing assertion has two oaths**.

Not a fourth cinch (cinch 0.3 stays the lockset vehicle — writ splices whole production, `wheat=[]`). Not leftover-name. Not a third ambit.

Discarded: `--from-fail` as a product (that is troth). Discarded: hunk peel of print vs return. Discarded: treating `# ran on alice` as EXPECTED-BOUND. Discarded: treating skipUnless Alice as LOCKED.

## How to run

From this worktree root:

```bash
./demo.sh
./writ --help
./writ --self-test
python3 -m unittest discover -s tests -q
./writ HEAD --cmd 'python3 -m unittest discover -q'
./writ HEAD --apply
./writ HEAD --fixture
./writ HEAD --clearance
./writ HEAD --due
./writ --list -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone
./writ --list -C /Users/annenpolka/ghq/github.com/annenpolka/kizu
```

Python 3.10+, git, stdlib. `-C` must be a worktree root.

## Empirical transcript

### v0.1 — the pair is the object

`./writ --self-test` ok. Unittest 28/28. `./demo.sh` passed=44 failed=0.

| fixture | alibi | gage-shaped | troth-now | writ |
| ------- | ----- | ----------- | --------- | ---- |
| `add` 5 vs 0, plus `print("debug")` | LOCKED | LOCKED-and-OPEN | no dump | **LOCKED-and-EXPECTED-OPEN vs ACTUAL-OPEN**, `wheat=[]`, exit 0 |
| tests `/tmp`, old prod `$HOME` | LOCKED | LOCKED-and-OPEN | needs a paste | **LOCKED-and-EXPECTED-OPEN vs ACTUAL-BOUND**, host ACTUAL, `--apply` 0, `--fixture` emits HOME |
| tests Alice, old prod `/tmp` | LOCKED | LOCKED-and-BOUND | needs a paste | **LOCKED-and-EXPECTED-BOUND vs ACTUAL-OPEN**, host NEITHER, `--apply` 1, `--fixture` false |
| skipUnless Alice | LOOSE | SKIP-and-BOUND | n/a | **SKIP** (not a lock), `--due` 1 |
| `# ran on alice` + assert 5 | LOCKED | OPEN comment | comment silent | comment not an oath: OPEN vs OPEN |
| test-only red | BROKEN (alibi v2) / CLEAN (v1) | BROKEN | n/a | BROKEN, refuse to oath a NEW fail |
| dirty README / AGENTS.md | CLEAN | — | — | CLEAN; docs are not production |

`--apply` on the `/tmp` vs `$HOME` splice: legal `OPEN ACTUAL`. vow `--side both` would AND the actual into OPEN expected and skip. writ does not have `--side both`.

sitbone `--list`: 0 production paths, `AGENTS.md` is not production. kizu same. Clean trees; no `swift test` / `cargo test`.

Self `--list` vs HEAD while still mixed with the lab tree:

```
self prod ['demo.sh', 'lab/lineages/subagent-…/demo.sh', …, 'writ.py']
```

Then `./writ HEAD --cmd 'python3 -m unittest discover -s tests -q'` → **UNBUILDABLE** (`ModuleNotFoundError: writ`). Four harvested `lab/**/demo.sh` files were "production." Occupancy of the coordinator tree, reported as a missing module.

### v0.2 — lab/ is not production; UNBUILDABLE is not a pair

After: a worktree that contains `lab/PROTOCOL.md` skips `lab/` (same honesty as dropping markdown from the lock). UNBUILDABLE of an *added* production file names the path and refuses to mint a fake OPEN/OPEN pair.

```
prod   2 path(s): demo.sh, writ.py
status UNBUILDABLE
note: new production absent at base: demo.sh, writ.py
note: UNBUILDABLE is not a fail pair — no expected/actual to oath
```

`./demo.sh` passed=45 failed=0. Unittest 30/30. sitbone/kizu still 0. Self `--list` prod is only `demo.sh` and `writ.py`.

Post-commit (`7df592b`): `./writ HEAD --cmd 'python3 -m unittest discover -s tests -q'` → **CLEAN**. A comment inserted into `writ.py` → **LOOSE** (NEW pass, SPLICE pass, no fail to oath). Then `git checkout -- writ.py`. `./demo.sh` still 45/45; `--list` prod `[]`.

`--clearance` on the debug-print fixture is empty stdout / exit 0. Same fixture's JSON `wheat=[]` `hunks=[]`. cinch 0.3 on that tree would wheat `return a + b` and budget or chaff the print. writ does not peel.

## Dogfood targets

- `tests/test_writ.py` fixtures (OPEN lock, ACTUAL-BOUND leak, EXPECTED-BOUND Alice, skip, comment, debug-print, test-only red, markdown CLEAN, added-module UNBUILDABLE)
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu}` `--list` (read-only; no `swift test` / `cargo test`)
- This worktree `--list` / splice vs HEAD (`writ.py` absent at base → UNBUILDABLE, not a pair)

## Surprises

- gage would call the `$HOME`-leaking HEAD + `/tmp` tests LOCKED-and-OPEN. The test file assumes `/tmp`. The *splice fail* assumes this host on the actual side. That is the joint: you cannot visa the test file and see ACTUAL-BOUND.
- unittest `assertEqual(add(2, 3), 5)` prints `0 != 5`. Taking the first comma as the expected slot yields `3), 5`. The expected slot is the last *top-level* argument. Nested calls are why dump order is not the oath.
- `--apply` on ACTUAL-BOUND + OPEN expected is still APPLY. The object is not "host role picks a polarity." It is the legal set. `--fixture` is the gated actual-side skip; `--apply` keeps the portable golden.

## Failures

- sitbone/kizu suites were not spliced (`swift test` / `cargo test` minutes). `--list` only. xctest grammar is parsed in unit tests; those oracles are UNRUN on the gold repos.
- `demo.sh` is production `.sh`. Tests do not lock it. After commit it is either CLEAN or LOOSE, never a pair.
- Exit 5 without the empty banner is still EMPTY (shared hole with cinch; out of scope).
- Added-module UNBUILDABLE is honest but still not LOCKED-by-existence. There is no expected/actual to oath.

## Suggested mutations

- Treat ImportError of a *new* module as LOCKED-and-EXPECTED-OPEN vs ACTUAL-ABSENT (existence lock, still not a hunk peel).
- Stream JSONL of per-fail pairs as splice output arrives.
- Occupy Swift/JS splice fails so sitbone titles stay FIXTURE and a `/Users` actual could become ACTUAL-BOUND.
- Join with mint: LOCKED-and-ACTUAL-BOUND *at visa-birth* (brand occupies EXPECTED-BOUND-at-birth; actual-side birth is open).

## Kill / keep

**Keep.** The object is new: a splice fail is two oaths, not LOCKED, not the test-file visa, not a dump you paste, not 1-minimal hunks. Demo case 2 is the money shot gage misses (OPEN test, ACTUAL-BOUND fail, `--apply` 0, `--fixture` this `$HOME`). Demo case 1 is the cinch contrast (`wheat=[]`). Skip is not a lock. Comments are not oaths. sitbone/kizu `--list` stay 0. Not a fourth cinch, not leftover-name, not a third ambit. Kill only if a later generation shows `alibi | troth --from-fail` emits ACTUAL-BOUND without a splice — it cannot: without the splice there is no dump, and gage visaes the test not the actual.
