# DESTROYER_WOOF

Adversarial pass on **woof** `--only prose`. Class-not-path, not weft's `docs/**` glob. Do not rewrite the victim. Do not clone snag `--forbid number`. tally `--chg` is contrast.

A unified diff is a superposition of syntactic classes. woof allows comment+text and **fails the build** if any other class leaked, regardless of path. This destroyer keeps the gold (`30→60` mixed-line, `docs/generated/api.rs`, fence number, CJK ident on `src.rs`) and names where prose-as-class still lies.

## Install / run

Python 3.9+, stdlib. Victim, tally, weft, snag are other worktrees. Dogfood sitbone `77df1da`.

```bash
./demo.sh
python3 attack.py          # writes /tmp/destroy-woof/{transcript.txt,fixtures/}
```

Exit 0 = battery ran. The victim's exit 1s are the point.

## Examples

### 1. New bash sample is 114 ident inserts

sitbone `77df1da` added an openssl fence to README and touched Makefile. woof v0.2 projects the fence as code. tally `--chg` drops the flood.

```bash
$ git diff 77df1da^..77df1da | woof --only prose
woof FAIL  only=prose  stdin  files=2  leaked=144  ident=126  kw=8  number=5  string=5
# 114 of those idents are README.md inserts.

$ git diff 77df1da^..77df1da | tally --only prose --chg
tally FAIL  leaked=22
# Makefile still ~21. README fence idents and 2048 inserts gone.
```

### 2. ADR SHA is `77 → 98`, not one ident

```bash
$ ./woof --only prose < /tmp/destroy-woof/fixtures/sha-digit.md.diff
woof FAIL  only=prose  stdin  files=1  leaked=1  number=1
  README.md:1  number  chg  77 → 98
# 77df1da → 98a8009. Tails are text, allowed. Letter-prefix e9b0f75 is free.
```

### 3. CJK ident in an indented README is still text

`fn 契約` on `src.rs` fails (DESTROYER_WEFT hole, closed). The same rename in an indented sample, `.txt`, or `CHANGELOG` is OK.

```bash
$ ./woof --only prose < /tmp/destroy-woof/fixtures/cjk-ident.diff
woof FAIL  ident  契約 → 資産

$ ./woof --only prose < /tmp/destroy-woof/fixtures/cjk-indented.md.diff
woof OK  leaked=0
```

Mixed-line `30→60` still FAIL number. Comment-interior still OK. That invert is snag.

Verdict: **mutate, do not kill.** Full report: `DESTROYER_WOOF.md`.
