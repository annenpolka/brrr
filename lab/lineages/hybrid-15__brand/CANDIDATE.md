# hybrid-15 — brand

## Primitive

A **brand** is lockset clearance at visa-birth: tests that newly lock production **in the same commit that first binds a machine visa**. The verdict is LOCKED-and-BOUND-at-birth. Skip is not a lock. SPREAD is not a mint.

## Why this might not exist

`gage` names LOCKED-and-BOUND vs LOCKED-and-OPEN on a current splice. A host-tied lock stays a stained alibi forever after the pin — including README-only follow-ups and including a later commit that only adds tests. `mint` names OPEN/SPEC → BOUND of a production world. Tests are not its object, so a pin that skipifs on CI is still a birth.

Concatenation is `mint && gage`: this range minted Alice *and* this range has a BOUND lock. That does not say they co-occurred. A pin on Monday and a lock on Thursday is mint-now plus gage-now. The missing verb is the joint occupancy: **the lock whose visa was minted in this commit**.

Not stain|alibi (two reports, no visa of a lock at birth). Not a fourth cinch (cinch 0.3 stays the lockset vehicle — brand splices whole production). Not leftover names.

## How to run

```bash
chmod +x ./brand
./brand --self-test
./demo.sh
./brand -C <repo>
./brand -C <repo> --report
./brand -C <repo> --due
./brand -C <repo> --walk --max 20
./brand --check origin/main..HEAD
```

Python 3.10+, git, stdlib. Exit 0 when no LOCKED-and-BOUND-at-birth. Exit 1 on a brand (or `--due` SKIP-at-birth). Exit 3 if the suite is already red on the child. `-C` must be a worktree root.

## Empirical transcript

### v0.1 (`f19d865`) — four cells, sitbone/kizu brands=0

`./brand --self-test` ok. `./demo.sh` → **passed=61 failed=0**.

| fixture | mint-now | gage-now | brand |
| --- | --- | --- | --- |
| pin Alice + tests assert `who("/Users/alice")` same commit | BIRTH SPEC→BOUND | LOCKED-and-BOUND | **BRAND**, exit 1 |
| pin Alice, tests still `load_profile("/tmp")` | BIRTH, exit 1 | LOOSE (no veto) | empty, `--report` MINT |
| skipUnless Alice on this host | BIRTH | SKIP (not a lock) | empty, `--due` 1 |
| pin Alice + `test.py` locks `add()` (OPEN) | BIRTH | LOCKED-and-OPEN | empty, `--report` OPEN |
| lock Alice two commits after the pin | no birth | LOCKED vs the pre-Alice base | empty, even on the spanning range |
| SPREAD Alice into Swift | `--spread` only | — | empty |
| GitHub titles / Brave / `/home/user` | not a birth | OPEN | empty |
| live HOME MATCH + lock same commit | BIRTH | LOCKED-and-BOUND MATCH | **BRAND** (CI does not care the laptop holds it) |

sitbone first-parent walk: **brands=0**, empty stdout, no Brave. kizu first-parent walk: **brands=0**, no AbsoluteLinkError (source-only extract skips `AGENTS.md`). That is mint's gold — brand did not invent a visa.

A range that mints Alice on Monday and locks her on Thursday is empty. `mint` on that range would still fire. Concatenation cannot say "they did not co-occur."

### v0.2 — lock files are the veto, not the suite

v0.1 `--report` on the OPEN-lock fixture listed **both** `test.py` (the fail-veto of `add`) **and** `tests/test_profile.py` (`assert True`). Occupancy of "every test file at the child," reported as the lock.

After: FAIL-FILE witnesses from the splice (else tests that encode the born machine). OPEN-lock report is only `lock  test.py`. Dummy `assert True` is gone. BROKEN notes carry the suite tail.

`./demo.sh` → **passed=61 failed=0**. sitbone/kizu still 0.

## Dogfood targets

- Synthetic histories in `--self-test` / `./demo.sh` (joint brand, mint-only pin, skip-at-birth, OPEN lock at birth, SPREAD, GitHub titles, live HOME MATCH, abs symlink)
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` first-parent (31-class walk, brands=0)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` first-parent (brands=0; AGENTS.md absolute symlink)

## Surprises

- A comparison `return home == "/Users/alice"` with no production *caller* is not a visa-birth. mint harvests argument worlds. The first skip fixture had only the comparison and brand was silent — not because skip occupancy worked, because nothing was minted. Added `start(); who("/Users/alice")`. That is mint's occupancy inherited; inventing a birth from a comparison would lie about sitbone/kizu.
- `test.py` at repo root is a test (gage's lesson). `from add import add` must resolve a root `add.py`; `src/add.py` made the OPEN-lock fixture BROKEN (red child), not LOCKED-and-OPEN.
- `--report` prose that mentioned `LOCKED-and-BOUND-at-birth` collided with "this event is not a brand" assertions. The object is a tagged line, not a blurb.
- Walks with births=0 never run the suite. sitbone/kizu stay cheap because the join is gated on mint.

## Failures

- Swift `loadHome` / Brave: UNRUN (Python suite only). Visa still visible as a non-birth.
- JS/RS worlds UNRUN.
- `runAppleScript` instance methods: not constructed (stain/hatch leftover).
- File rename of a BOUND world looks like ABSENT→BOUND (path is in the slot key). mint's hole, inherited.
- `--locks` vs the *immediate* parent cannot see gage-now against a merge-base: parent already holds Alice, so child tests of Alice are LOOSE. The range being empty *is* the gage contrast.

## Suggested mutations

- `--follow` slot identity across renames (mint's hole).
- Join with held: eras of BOUND-and-LOCKED, not only onset.
- Occupy Swift/JS world-tests so an UNRUN Brave lock could become LOCKED-and-OPEN at an OPEN birth (still not a brand).
- Optional `--base <merge-base>` for gage-shaped occupancy of a lock whose visa was minted earlier in the range — complementary, not this object.

## Kill / keep

**Keep.** The four-cell is a different object than gage-now and mint-now. v0.1 dogfood on sitbone/kizu is the empty-report gold (do not lie). The split-range money shot is the proof concatenation fails: mint on `open..lock-after` would be 1; brand is 0. Kill only if a later generation proves `mint | gage` names same-commit co-occurrence — it does not, because a pin and a later lock share a range and disagree with the joint.
