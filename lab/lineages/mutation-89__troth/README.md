# troth

`--apply` from **host role**, without breaking OPEN expected.

vow (mutation-68) paired `EXPECTED-BOUND vs ACTUAL-BOUND` and named this host (`ACTUAL` when the dump's actual is `$HOME`). `--apply` still talked only to the expected side. A dump whose actual is this machine could not apply the actual-side skip/fixture without `--side actual`. A naive host-role apply would skip a portable `/tmp` golden just because you are `NEITHER`.

troth's object is the **legal apply set**: OPEN expected always applies (a portable golden that failed on Alice still applies here). If this host is ACTUAL-BOUND of the dump, the actual-side skip/fixture is also legal. Comments are not oaths. sitbone stays FIXTURE, not TAINTED.

## Install / run

Python 3.9+, stdlib only.

```bash
chmod +x ./troth
./troth --help
./demo.sh
./troth --self-test
```

## Three examples

### 1. OPEN expected still applies when this host is NEITHER

```bash
./troth --from-fail --apply < fixtures/xctest_fail.txt
# troth  pair  xctest  EXPECTED-OPEN vs ACTUAL-BOUND
#   host     NEITHER  this host is neither recorded machine
#   legal    OPEN
#   apply    APPLY    OPEN expected still applies (portable golden)
# exit 0
```

vow `--side both` ANDs the actual MISS into the OPEN expected and **skips** (exit 1). That is the hole. troth default `--side host` is OR: portable expected is not skipped because you are NEITHER.

### 2. ACTUAL-BOUND skip/fixture is legal when this host produced the fail

```bash
printf 'E   - /Users/alice/proj\nE   + %s/proj\n' "$HOME" | ./troth --from-fail --apply
# host     ACTUAL  this host produced the fail
# legal    ACTUAL
# apply    APPLY   ACTUAL-BOUND skip/fixture is legal
# exit 0
```

vow `--side expected` exits 1 (Alice's golden MISS). You produced the fail; applying the actual-side skip is legal.

A dump whose expected is `/tmp` and actual is `$HOME` is `legal OPEN ACTUAL`: the portable golden still applies *and* the actual-side fixture is legal. `--emit shell` stays `true` (OPEN). `--fixture` emits the actual skip *iff* it is legal:

```bash
printf 'E   - /tmp/x\nE   + %s/proj\n' "$HOME" | ./troth --from-fail --fixture
# [ "$(uname -s)" = Darwin ] && [ "${HOME}" = /Users/annenpolka ]
# exit 0

./troth --from-fail --fixture < fixtures/xctest_fail.txt
# false   # this host is NEITHER; Alice's skip is not legal here
# exit 1
```

`--side actual --emit shell` still prints Alice's skip even when you are NEITHER. `--fixture` is gated on host role.

### 3. A comment is still not an oath. Sitbone stays FIXTURE.

```bash
./troth fixtures/comment_only.py
# OPEN  silent comment USER=alice  apply true

./troth fixtures/title.swift
# FIXTURE  USER=annenpolka is identity-as-data, not a skip

./troth --from-fail --apply < fixtures/comment_in_fail.txt
# # ran on alice does not bind; EXPECTED-OPEN vs ACTUAL-OPEN; --apply 0
```

`--scan -C sitbone` stays 0 BOUND / 4 FIXTURE. kizu comments about John Doe stay silent; quoting asserts are SPEC.

## Why this is not vow, not lees

vow named the host and left `--apply` on the expected side. lees subtracted two transcripts. visa scanned the whole file. stain/admit walk production worlds.

troth's window is the failing assertion: `--apply` is the legal set `OPEN expected ∪ ACTUAL-BOUND-if-this-host`, not oracle polarity and not an AND of both sides.
