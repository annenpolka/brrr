# sear

Lockset clearance **at visa-birth**, following dest-file slot identity.

`brand` is the joint: tests that newly lock production **in the same commit that first binds a machine visa**. The verdict is **LOCKED-and-BOUND-at-birth**. Skip is not a lock. SPREAD is not a mint.

`mint`'s hole: dest-file path is in the slot key, so `git mv src/profile.py src/user.py` of a BOUND world looks like **ABSENT→BOUND**. A lock of that false birth is a false brand.

`sear` `--follow`s the visa *slot* across dest-file identity (git **R** records, not `git log --follow`). Copy is not a follow. Same-commit lockset clearance is still required. Rename of a visa-bearing test still brands the **birth** commit, not the rename.

sitbone/kizu first-parent births=0 is mint's gold — sear does not invent them. Not a fourth cinch: production is spliced whole.

## Install / run

Python 3.10+, git, stdlib. v0.2.

```bash
chmod +x ./sear
./sear --help
./sear --self-test
./demo.sh
```

## Three examples

### 1. Same commit pin + lock — BRAND, exit 1

```bash
./sear -C some-repo <sha-that-pinned-and-locked-HOME>
# sear  brands=1  worlds=1  commit=abc1234  parent=def5678
#   pin Alice home and lock it
#   BRAND  LOCKED-and-BOUND-at-birth  SPEC→BOUND  HOME=/Users/alice …
#     who  who("/Users/alice")  app.py
#     lock  tests/test_who.py
# exit 1
```

### 2. Rename of a visa-bearing test — birth, not the rename

```bash
./sear -C some-repo <sha-that-git-mv'd-the-locking-tests>
# (no stdout)
# exit 0

./sear -C some-repo --walk --max 20 HEAD
# sear  brands=1  …  commit=<pin-and-lock-sha>
#   BRAND  LOCKED-and-BOUND-at-birth  …
```

`--no-follow` on a dest-file rename of production is the hole: ABSENT→BOUND (a false mint). Occupancy still follows dest identity, so the lock does not newly fire — default stays empty. A same-commit pin + `git mv` + lock is still a brand (`SPEC→BOUND`, not `ABSENT→BOUND`).

### 3. Birth without a lock — empty, exit 0 (mint-now)

```bash
./sear -C some-repo <sha-that-only-pinned-HOME>
# (no stdout)
# exit 0
```

A pin on Monday and a lock on Thursday is still empty: they did not co-occur. SPREAD into Swift is not a mint. Copy of a BOUND file is not a follow.

| code | meaning |
| --- | --- |
| 0 | no LOCKED-and-BOUND-at-birth |
| 1 | a lock was born with the visa (or `--due` SKIP-at-birth) |
| 2 | usage / not a git repository root |
| 3 | suite already red on the child tree |
