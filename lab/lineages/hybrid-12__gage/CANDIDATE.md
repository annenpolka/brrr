# hybrid-12 — gage

## Primitive

A **gage** is the visa of a lock: splice world-tests onto old production and name **LOCKED-and-BOUND vs LOCKED-and-OPEN**. Empty stdout means the lockset is cleared of machines. A skip is not a lock.

## Why this is not stain|alibi concatenation

`stain | alibi` is two reports: production leaked a host; the suite goes red on base. Piping them does not produce a verdict.

- stain never splices. Alice in production is debt even when no test runs.
- alibi never visaes. `pytest.skip` is exit 0, so a skipif Alice test looks LOOSE (or LOCKED if it ran on Alice's laptop).
- cinch isolates 1-minimal hunks. gage splices whole production and asks what *world* the veto inhabits. Not a fourth cinch.

The object changed. The lockset is the tests that veto. Each lock has a visa taken from the world it assumes, not from the production file. Brave next to a Darwin comment is OPEN. Alice's HOME that skipifs on CI is SKIP, not LOOSE. A test that vetoes and assumes this host's HOME is LOCKED-and-BOUND even when the laptop MATCHES.

Concatenation cannot say "this alibi is a stain" vs "this alibi is a clearance."

## Why this might not exist

TDD implies new tests go red on old production (alibi) and CI implies tests do not encode a laptop (stain). Developers who have both still treat LOCKED as one green. A host-tied assertion is a fake alibi on CI (skip) and a real one on the author's machine (MATCH fail on base). That split is the missing verb.

## How to run

```bash
chmod +x ./gage
./gage --self-test
./demo.sh
./gage -C <repo>
./gage -C <repo> --report
./gage -C <repo> --due
./gage --emit HEAD
./gage --suite HEAD
```

Python 3.10+, git, stdlib. Exit 0 when no LOCKED-and-BOUND. Exit 1 on a stained lock (or `--due` SKIP-and-BOUND). Exit 3 if a world-test is already red on NEW.

## Empirical transcript

### v0.1 (`0797375`) — four cells, `test.py` is a test

`./gage --self-test` ok. `./demo.sh` → **passed=21 failed=0**.

| fixture | alibi-shaped | stain-shaped | gage |
| --- | --- | --- | --- |
| Brave member | LOCKED | empty (no machine) | LOCKED-and-OPEN, default empty |
| live HOME encoded | LOCKED | MATCH stain | LOCKED-and-BOUND, exit 1 |
| Alice isdir skipif | LOOSE (skip=pass) | MISS stain | SKIP-and-BOUND, default empty, `--due` 1 |
| comment-only HOME | LOOSE | MATCH stain | LOOSE-and-BOUND parent=LEAKED, default empty |

Lockset bakeoff `debug-print` (HEAD `return 0`, WIP `print("debug")+return`, `test.py` assert 5): **LOCKED-and-OPEN**, default empty. cinch would drop the print hunk; gage does not isolate hunks. The lock's world is OPEN.

`test.py` at repo root was production under a `test_*.py` heuristic. The bakeoff uses `test.py`. Fixed so suite fallback actually runs.

ugly (Alice restored over a `/tmp` base): stain exit 1, three Alice worlds, one machine. gage v0.1 **BROKEN** because `title.split(" - ", 1)` was harvested as a world and `getattr(mod, "title")` failed. String methods are not production worlds. The whole lockset took occupancy of a false harvest.

### v0.2 — getattr miss is UNRUN; split is not a world

After: skip string methods; local receivers (`title.split`) are not generable; AttributeError on NEW is UNRUN, not a red suite. BROKEN is an oracle that already fails on NEW.

ugly, same splice (production `src/profile.py` + `src/App.swift` vs `/tmp` base):

```
stain -C ugly          # exit 1
# stain  machines=1  worlds=3  miss=1
#   MISS  BOUND  HOME=/Users/alice …

gage -C ugly           # exit 0, stdout empty
gage -C ugly --due     # exit 1
gage -C ugly --report
# status=CLEAR  mode=worlds  bound-locks=0
#   SKIP    BOUND  MISS  parent=CLEAN  load_profile("/Users/alice")
#   SKIP    BOUND  MISS  parent=CLEAN  load_profile("/Users/alice/Library")
#   LOOSE   OPEN          extract_title("GitHub - annenpolka/sitbone …")
#   LOOSE   SPEC          quote("/home/user/project")
#   UNRUN   BOUND         loadHome("/Users/alice/Library/sitbone")   # Swift
#   UNRUN   OPEN          isBrowser("Brave Browser")                 # Swift
```

stain fails because production leaked Alice. gage default is empty because Alice's world-tests skip on this host — they never vetoed. `--due` recovers the stained tests that did not occupy the lock. That is the joint: **a skip is not a lock, and a lock that is OPEN is a clearance.**

`./demo.sh` → **passed=33 failed=0** (ugly + lockset bakeoff included).

Two Alice `load_profile` worlds remain one machine under `--report` grouping for BOUND locks (v0.1 already grouped debt that way; ugly never reached debt because they SKIP).

## Dogfood targets

- constructed open-lock / bound-lock / bound-skip / debug-print
- `/tmp/lockset-bakeoff/fixtures/debug-print` (cinch destroyer money shot)
- stain `fixtures/ugly` as a git splice (Alice vs `/tmp` base)

## Surprises

- `test.py` at repo root is production under alibi's `test_*.py` heuristic. Lockset fixtures use `test.py`. The suite fallback is a lie until that name is a test.
- alibi's skip=pass hole is the joint: Alice skipifs, splice is green, stain still fails. gage default follows stain's emptiness *for locks*, not for production leaks.
- ugly's GitHub title is OPEN (not USER=annenpolka). Same lesson as stain; harvest visaes argument literals only.
- MATCH this-host HOME is still LOCKED-and-BOUND. CI does not care the laptop holds the visa.

## Failures

- Swift `loadHome` / Brave: UNRUN (Python exec only). Visa still visible under `--list`/`--report`.
- JS/RS worlds UNRUN (`listen("0.0.0.0")`, rust `connect("localhost")`).
- `runAppleScript` instance methods: not constructed (stain's failure, inherited).
- Whole-suite fallback visaes the test file, not per-hunk wheat. That is deliberate (not cinch).

## Suggested mutations

- Exec Swift/JS worlds or emit XCTest and run `swift test` for UNRUN OPEN locks (Brave could be LOCKED-and-OPEN).
- `--held`-style: when a lock newly acquired a visa.
- Per-hunk wheat is cinch; do not.
- Construct `Type()` when recv is a type in the module.
- `--allow HOME=/Users/alice` documented exceptions so a recording fixture can lock on purpose.

## Kill / keep

**Keep.** The four-cell table is a different object than stain, alibi, or cinch. v0.2 dogfood on ugly is the proof concatenation fails: stain 1 / alibi-shaped skip=pass / gage 0 with `--due` 1. Kill only if a later generation proves `alibi && stain` is the same verb — it is not, because skip occupancy and MATCH bound-locks disagree with both parents.
