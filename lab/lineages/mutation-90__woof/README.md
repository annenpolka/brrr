# woof

A unified diff is a superposition of syntactic classes. **woof** is the CI gate that weft meant: `--only prose` allows comment+prose tokens **regardless of path**.

weft `--only docs` is a path glob (`*.md` *or* anything under `docs/`). A timeout bump in `docs/generated/api.rs` is green. woof does not free a number ply because the file sits under `docs/`. README.md at the repo root still counts: CJK/English words are prose (`text`); a number is still a number.

Not snag. snag `--forbid number` trips even on `// timeout 30 → 60`. woof leaves that as comment ply. Cite snag for the invert. Markdown fences are the other hide: project the tagged dialect; do not peel comment interiors.

stdin is a unified diff. TSV only on `--emit`. Exit 0 clean, 1 leak, 2 usage.

## Install / run

Python 3.9+, stdlib. No `git` required (stdin filter).

```bash
./demo.sh
./demo.sh 0
./woof --selftest
./woof --help
git diff | ./woof --only prose
git diff | ./woof --only comments
git diff | ./woof --only prose --emit
```

`--only prose` (and `--only docs` as the same token alias) is comment+text. Path never frees ident/number/string. `--only comments` is comment tokens only.

## Examples

Mixed line: comment rewrite, timeout moved. Same cheat weft named.

```bash
$ git diff | ./woof --only prose
woof FAIL  only=prose  stdin  files=1  leaked=1  number=1
  src.rs:2  number  chg  30 → 60
```

`docs/generated/api.rs` is not a docs PR. weft `--only docs` is OK here; woof is not:

```bash
$ ./woof --only prose < fixtures/docs-generated-api.rs.diff
woof FAIL  only=prose  stdin  files=1  leaked=2  ident=1  number=1
  docs/generated/api.rs:1  ident  chg  fetch_user → fetch_account
  docs/generated/api.rs:1  number  chg  30 → 60
```

CJK README is prose. A Japanese function rename on a code path is ident:

```bash
$ git diff | ./woof --only prose     # 契約は蒸留 → 契約は資産 in README.md
woof OK  only=prose  stdin  files=1  leaked=0

$ git diff | ./woof --only prose     # fn 契約 → fn 資産 in src.rs
woof FAIL  ident  契約 → 資産
```

A fenced timeout is code, even on README.md. weft `--only docs` swallows the fence as one string and then frees the path. woof names `30 → 60`:

```bash
$ ./woof --only prose < fixtures/fence-number.md.diff
woof FAIL  only=prose  stdin  files=1  leaked=1  number=1
  README.md:5  number  chg  30 → 60
```

Comment-interior `// timeout 30 → 60` is still comment ply. That invert is snag `--forbid number`, not this gate.
