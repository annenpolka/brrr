# destroyer-25 — maiden

Adversarial pass on **never-red**: tests whose recorded history contains zero failures.

A currently green test is not maiden. `rg PASS` on the newest junit is not maiden.
SKIP-only is not maiden. No records is **UNKNOWN**, not maiden — *if* a roster was supplied
and the fail dialect was parsed. The object held. The parser × string-id is the mutation.

Not alibi. Not cinch. Not winnow. Victim is maiden 0.2 (not rewritten).

## Install / run

Python 3.10+, stdlib. Victim CLI:

```
MAIDEN=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7e115d7932c1/maiden
```

```bash
chmod +x ./demo.sh ./attack.py
./demo.sh
python3 ./attack.py          # writes /tmp/destroy-maiden/
"$MAIDEN" --selftest         # 28/28 after the attacks
```

Transcript / fixtures: `/tmp/destroy-maiden/`. Report: `DESTROYER_MAIDEN.md`.

## Examples

### 1. Gold path — never-red is not `rg PASS`

```bash
"$MAIDEN" --no-ledger --header \
  /tmp/destroy-maiden/fixtures/junit/run-2019-fail.xml \
  /tmp/destroy-maiden/fixtures/junit/run-2024-green.xml
# alpha SCARRED (2019 fail). --latest maidens it. --skeptic names it.
```

### 2. junit flaky-then-green is MAIDEN (the lie)

```bash
"$MAIDEN" --no-ledger --header \
  /tmp/destroy-maiden/fixtures/junit/flaky-then-green.xml
# pkg.T::alpha  MAIDEN  n_fail=0   despite <flakyFailure>
```

### 3. sitbone / kizu roster is UNKNOWN, not maiden

```bash
"$MAIDEN" -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone \
  --no-ledger --roster --counts /tmp/destroy-maiden/logs/sitbone-list.txt
# UNKNOWN 213  MAIDEN 0

"$MAIDEN" --no-ledger --roster --counts /tmp/destroy-maiden/logs/kizu-list.txt
# UNKNOWN 489  MAIDEN 0
```

`--check MAIDEN` on those rosters is rc=0. One live green run maidens the **runner specifier**
(v0.2). `--census` intersects that specifier in **zero** places.

Exit 0 ok, 1 `--check` fired, 2 usage (`ingest --run ID FILE` is 2 — argparse).
