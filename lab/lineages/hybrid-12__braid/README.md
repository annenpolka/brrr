# braid

plait/spar compose review-suggestion strands with each other and never read a tree. sate occupies each claim against a tree. GitHub outdated is line-identity. `git apply --check` is a boolean.

**braid first composes, then occupies the single composed after-image.** COMMUTE is one occupancy of the union. STACK is occupancy of the series fold. JAM and SPLIT exit without occupying.

Not N occupancy rows joined. Not `|` of the parent CLIs.

| compose | occupy |
| --- | --- |
| **PARALLEL** (COMMUTE) | one fate of the union after-image |
| **SERIES** (STACK) | one fate of origin→final, not each round |
| **ECHO** | one fate of the locus (apply once) |
| **SUBSUME** | one fate of the outer |
| **SPLIT** | rc=1, no occupy |
| **JAMMED** | rc=2, no occupy |

Occupancy of a *partial* apply (suggestion A landed, B did not) is **SUPERSEDED of the composed image**, not APPLIED+PENDING of the strands.

## Install / run

Python 3.9+, stdlib only. `git` only if `--against REF`.

```bash
chmod +x ./braid ./demo.sh
./braid --help
./braid --selftest
./demo.sh
```

Exit: `0` occupy-ok (or empty), `1` SPLIT, `2` JAMMED, `3` error. `--report-only` forces `0`. `--json` / `--tsv` compose.

## Examples

### 1. Two nits commute — one PENDING, not two

```bash
./braid -C fixtures/trees/commute fixtures/commute.jsonl
```

```
braid  n=2  files=1  compose=PARALLEL  occupy=PENDING
  COMMUTE  app.py  #alice@1  #bob@3  disjoint spans
  composed  alpha, beta, gamma  →  ALPHA, beta, GAMMA
  PENDING    app.py  exact-before
```

A tree where only alice has landed (`fixtures/trees/commute-a-only`) is `occupy=SUPERSEDED` of that file region. plea would print APPLIED and PENDING.

### 2. Overlap is a jam — refuse occupy

```bash
./braid fixtures/jam.jsonl
# rc=2  occupy=—  composed=[]
```

Same-span two afters (`fixtures/split.jsonl`) are SPLIT, rc=1, also no occupy. Replacement, not hunk-union.

### 3. Two review rounds — occupy the fold

```bash
./braid -C fixtures/trees/stack fixtures/stack.jsonl
# SERIES  beta → beta3  occupy=PENDING
./braid -C fixtures/trees/stack-mid fixtures/stack.jsonl
# occupy=SUPERSEDED   (beta2 is neither origin nor final)
```

Inverted clocks do not invent a `same-tree` of the wrong image. The object is the series after-image.

Compose: `gh api repos/cli/cli/pulls/7/comments | ./braid -C /path/to/cli --json`
