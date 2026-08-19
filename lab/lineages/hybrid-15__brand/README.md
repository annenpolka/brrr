# brand

Lockset clearance **at visa-birth**.

`mint` asks when a production world became BOUND (OPEN/SPEC → BOUND). Tests are not its object. `gage` asks whether current tests veto old production *and* assume a machine (LOCKED-and-BOUND vs LOCKED-and-OPEN). A skip is not a lock.

`brand` is the joint: tests that newly lock production **in the same commit that first binds a machine visa** (`/Users/alice`, `$HOME`, this host). The verdict is **LOCKED-and-BOUND-at-birth**.

A visa minted without a lock is mint-now, not a brand. A lock of a visa the parent already held is gage-now, not a brand. SPREAD is not a mint. sitbone/kizu first-parent births=0 is mint's gold — brand does not invent them. Not a fourth cinch: production is spliced whole.

## Install / run

Python 3.10+, git, stdlib. v0.2.

```bash
chmod +x ./brand
./brand --help
./brand --self-test
./demo.sh
```

## Three examples

### 1. Same commit pin + lock — BRAND, exit 1

Production becomes `who("/Users/alice")` and tests start asserting that world in the same commit:

```bash
./brand -C some-repo <sha-that-pinned-and-locked-HOME>
# brand  brands=1  worlds=1  commit=abc1234  parent=def5678
#   pin Alice home and lock it
#   BRAND  LOCKED-and-BOUND-at-birth  SPEC→BOUND  HOME=/Users/alice …
#     who  who("/Users/alice")  app.py
#     was  SPEC  who("/tmp/cache")  app.py
#     lock  tests/test_who.py
# exit 1
```

CI does not care that this laptop MATCHES a live HOME. MATCH is still a brand.

### 2. Birth without a lock — empty, exit 0 (mint-now)

The same Alice pin, tests still call `/tmp` and do not veto. `mint` would exit 1. `brand` stays silent: a skip is not a lock, and a loose suite is not a lock.

```bash
./brand -C some-repo <sha-that-only-pinned-HOME>
# (no stdout)
# exit 0

./brand -C some-repo --report <that-sha>
# MINT  SPEC→BOUND-unlocked  lock=LOOSE
```

`--due` recovers SKIP-and-BOUND-at-birth (stained tests that never occupied).

### 3. Lock after the birth — empty, exit 0 (gage-now)

Alice was minted two commits ago. This commit adds the locking tests. `gage` against the pre-Alice base would name LOCKED-and-BOUND. `mint` on this commit is 0 (parent already held the machine). `brand` on this commit **and on the range that spans both** is empty: they did not co-occur.

```bash
./brand -C some-repo <sha-that-locked-later>
# (no stdout)
# exit 0

./brand -C some-repo open-sha..lock-sha
# (no stdout)   # mint on that range would still fire
# exit 0
```

| code | meaning |
| --- | --- |
| 0 | no LOCKED-and-BOUND-at-birth (OPEN locks are a clearance; skip is not a lock) |
| 1 | a lock was born with the visa (or `--due` saw SKIP-at-birth) |
| 2 | usage / not a git repository root |
| 3 | suite already red on the child tree |
