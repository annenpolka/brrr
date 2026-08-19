# proxy

Follow the **expected name** to its bound value, then pair the two oaths.

vow (mutation-68) named `EXPECTED-BOUND vs ACTUAL-BOUND` from a failing assertion. `expected = home; assert got == expected` did not follow the name, so a pytest dump emitted **two inverted pairs** (PM vs E +/-). proxy follows `expected → home → <bound value>` *before* classifying. One assertion is one pair. Comments are not oaths. HOST is not a machine visa unless the bound value is a path or a user. sitbone stays FIXTURE.

## Install / run

Python 3.9+, stdlib only.

```bash
chmod +x ./proxy
./proxy --help
./demo.sh
./proxy --self-test
```

## Three examples

### 1. `expected = home` follows before the pair is classified

```bash
./proxy fixtures/name_follow.py
# OPEN — home is os.environ['HOME'], no literal machine
# window  assert  expected=os.environ["HOME"]  proxy=expected→home→os.environ["HOME"]

./proxy fixtures/name_follow_literal.py
# BOUND  HOME=/Users/annenpolka
# expected → home → /Users/annenpolka
```

vow on the same files stayed OPEN with windows `('expected=', 'home')` and `('assert', 'expected', 'got')`. The name was the window.

### 2. One pair, not two inverted

```bash
./proxy --from-fail < fixtures/name_follow_fail_diff.txt
# proxy  pair  pytest  EXPECTED-BOUND vs ACTUAL-OPEN
#   expected /Users/annenpolka
#   actual   /tmp/x
# n=1

./proxy --from-fail < fixtures/name_follow_fail_vv.txt
# same pair: `and expected = home` follows to /Users/annenpolka
```

vow emitted two pairs (PM inverted + E +/- correct, or PM + `-vv` with `home` unfollowed). pytest `assert left == right` is actual vs expected. rustc `left:` is actual.

### 3. A comment is still not an oath. Sitbone stays FIXTURE. HOST is soft.

```bash
./proxy fixtures/comment_only.py
# OPEN  silent comment USER=alice  apply true

./proxy fixtures/title.swift
# FIXTURE  USER=annenpolka is identity-as-data, not a skip

./proxy fixtures/host_getenv.py
# OPEN  soft HOST=ci-mac-7  — hostname is not a machine visa
```

`--scan -C sitbone` stays 0 BOUND / 4 FIXTURE. kizu comments about John Doe stay silent; quoting asserts are SPEC.

## Why this is not vow, not lees

vow paired two unary machines and left the expected slot as the identifier. lees subtracted two transcripts. visa scanned the whole file.

proxy's window is the name in the expected slot: follow it, then classify. The dump object is one pair.
