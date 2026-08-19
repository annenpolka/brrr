# tally

A unified diff is a superposition of syntactic classes. **tally** is woof’s `--only prose` gate plus **`--chg` on fence numbers**.

woof made a fenced timeout `30→60` into number ply. A *new* bash sample then floods ident inserts (sitbone `77df1da`: 126 idents) and drowns the change. `--chg` drops fence ident/kw/string flood **and fence number inserts**. A fence number *change* (`30→60`) still fails. A new sample’s `2048` is not a number leak. Mixed-line `30→60` on a code path still fails.

Not snag. snag `--forbid number` trips on `// timeout 30 → 60`. tally leaves that as comment ply. Cite snag for the invert; compose, do not clone.

stdin is a unified diff. TSV only on `--emit`. Exit 0 clean, 1 leak, 2 usage.

## Install / run

Python 3.9+, stdlib. No `git` required (stdin filter).

```bash
./demo.sh
./demo.sh 0
./tally --selftest
./tally --help
git diff | ./tally --only prose --chg
git diff | ./tally --only prose
git diff | ./tally --only prose --chg --emit
```

`--only prose` (and `--only docs` as the same token alias) is comment+text. Path never frees ident/number/string. `--chg` is fence-local: fence ident flood and fence number *inserts* are not leaks; fence `30→60` is. Makefile / `src.rs` still leak.

## Examples

DESTROYER_WEFT fence-number fixture: rust fence `30→60` is a number *change*. weft `--only docs` is OK (path glob + swallowed string). tally names it:

```bash
$ ./tally --only prose --chg < fixtures/fence-number.md.diff
tally FAIL  only=prose  chg  stdin  files=1  leaked=1  number=1
  README.md:5  number  chg  30 → 60  fence
```

A new bash sample is not an ident leak, even if it inserts `2048`. Without `--chg` it is woof’s flood. `30→60` in a fence still fails:

```bash
$ ./tally --only prose --chg < fixtures/fence-ident-flood.md.diff
tally OK  only=prose  chg  stdin  files=1  leaked=0

$ ./tally --only prose --chg < fixtures/fence-number.md.diff
tally FAIL  number  chg  30 → 60  fence

$ ./tally --only prose < fixtures/fence-ident-flood.md.diff
tally FAIL  ident=23  number=3
```

Mixed line: comment rewrite, timeout moved. Same cheat weft named. `--chg` does not hide it (it is not a fence):

```bash
$ git diff | ./tally --only prose --chg
tally FAIL  only=prose  chg  stdin  files=1  leaked=1  number=1
  src.rs:2  number  chg  30 → 60
```

Comment-interior `// timeout 30 → 60` is still comment ply. That invert is snag `--forbid number`, not this gate.
