# tilde

braid occupies the composed after-image of review-suggestion strands. Its covering fills unclaimed gaps from HEAD, so a drifted middle or a one-line pad becomes occupancy of a live canvas (or a chimera that exists nowhere). Path keys are NFC; line images are not. hank `--emit`s that covering.

**tilde first composes, then occupies the fold with NFC-equivalent path and line keys.** Covering occupancy is of the claimed nits, not a live-gap canvas. STACK is occupancy of the series fold. JAM and SPLIT exit without occupying.

Not N occupancy rows. Not hank `--emit`. Not a fourth cinch.

| compose | occupy |
| --- | --- |
| **PARALLEL** (COMMUTE) | one fate of the nits (gaps are context) |
| **SERIES** (STACK) | one fate of origin→final, not each round |
| **ECHO** | one fate of the locus (apply once) |
| **SUBSUME** | one fate of the outer |
| **SPLIT** | rc=1, no occupy |
| **JAMMED** | rc=2, no occupy |

Occupancy of a *partial* apply (suggestion A landed, B did not) is **SUPERSEDED of the composed image**, not APPLIED+PENDING of the strands.

`café` vs `café` (U+0065 U+0301) is one path and one line. A still-open nit stays PENDING.

## Install / run

Python 3.9+, stdlib only. `git` only if `--against REF`.

```bash
chmod +x ./tilde ./demo.sh
./tilde --help
./tilde --selftest
./demo.sh
```

Exit: `0` occupy-ok (or empty), `1` SPLIT, `2` JAMMED, `3` error. `--report-only` forces `0`. `--json` / `--tsv` compose. `--ignore-space` applies to pair-compose **and** occupy.

## Examples

### 1. Two nits commute — one PENDING of the nits

```bash
./tilde -C fixtures/trees/commute fixtures/commute.jsonl
```

```
tilde  n=2  files=1  compose=PARALLEL  occupy=PENDING
  COMMUTE  app.py  #alice@1  #bob@3  disjoint spans
  composed  alpha | gamma  →  ALPHA | GAMMA
  PENDING    app.py  union-before
```

Gap fill does not absorb `beta`. Tree `alpha/BETA/gamma` stays PENDING of the nits. Tree `PAD/alpha/beta/gamma` stays PENDING — not SUPERSEDED of a chimera `alpha|alpha|gamma`.

A tree where only alice has landed (`fixtures/trees/commute-a-only`) is `occupy=SUPERSEDED` of that union. plea would print APPLIED and PENDING.

### 2. Overlap is a jam — refuse occupy

```bash
./tilde fixtures/jam.jsonl
# rc=2  occupy=—  composed=[]
```

Same-span two afters (`fixtures/split.jsonl`) are SPLIT, rc=1, also no occupy. Replacement, not hunk-union.

### 3. NFC café is one occupy; STACK fold is still SUPERSEDED at mid

```bash
./tilde --json fixtures/nfc-two-paths.jsonl
# files=1  compose=PARALLEL  one composed claim
./tilde -C fixtures/trees/nfd-word fixtures/nfc-content.jsonl
# occupy=PENDING   (NFC café vs NFD café is the same line)
./tilde -C fixtures/trees/stack-mid fixtures/stack.jsonl
# occupy=SUPERSEDED   (beta2 is neither origin nor final)
```

Inverted clocks do not invent a `same-tree` of the wrong image. The object is the series after-image.

Compose: `gh api repos/cli/cli/pulls/7/comments | ./tilde -C /path/to/cli --json`
