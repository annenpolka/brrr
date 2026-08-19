# wale

A review suggestion is a strand (span + before→after). Ancestor **plait** treated ECHO as image-identity: same `before→after` collapsed to one apply, so `return 0` at L1 and L10 became `['site1']` and left L10. **wale asks whether the strands share a locus.**

Same image at two sites is two strands. STACK / COMMUTE / JAM stay replacement-algebra, not occupancy.

| verdict | meaning |
| --- | --- |
| **COMMUTE** | disjoint *different* edits; any apply order, same tree |
| **MULTI** | same image at distinct loci; apply each (not a duplicate) |
| **STACK** | after(A) *is* before(B); only A then B |
| **ECHO** | same locus, same before→after; apply once |
| **SPLIT** | same locus, two afters; reviewers disagree |
| **SUBSUME** | outer span consumes a consistent inner |
| **JAM** | overlapping incompatible edits |
| **THREAD** | reply chain on a locus (`--remarks`) |
| **COVER** | a remark sits on a suggestion |

A file's **wale** is PARALLEL / SERIES / ECHO / MULTI / SUBSUME / SPLIT / JAMMED / THREAD. Apply schedules (`line` / `time` / `topo`) are witnesses, not the object. Pretty `applied=[…]` is the witness that ECHO ran once and MULTI ran twice.

## Install / run

Python 3.10+, stdlib only. `git` only if `--against REF`.

```bash
chmod +x ./wale ./demo.sh
./wale --help
./wale --selftest
./demo.sh
```

Exit: `0` composable (PARALLEL / SERIES / ECHO / MULTI / SUBSUME / THREAD), `1` SPLIT, `2` JAMMED, `3` error. `--report-only` forces `0`. `--json` / `--tsv` compose.

## Examples

### 1. Gold COMMUTE still commutes (cli/cli PR #7)

```bash
./wale fixtures/cli-pr7.json
```

```
wale  n=2  files=1  components=1  PARALLEL=1

pairs
  COMMUTE  command/pr.go  #333030758@347  #333031216@400  disjoint spans

wales
  PARALLEL command/pr.go  #333030758,#333031216  independent; compose in any order
```

Two suggestions, different lines, same snapshot. GitHub "outdated" never said that. Ancestor plait said it too; wale does not kill COMMUTE.

### 2. Same image at two sites is not apply-once

```bash
mkdir -p /tmp/t && printf 'return 0\nkeep\nkeep\nkeep\nkeep\nkeep\nkeep\nkeep\nkeep\nreturn 0\n' > /tmp/t/app.py
./wale -C /tmp/t fixtures/echo-dup-sites.jsonl
```

```
pairs
  MULTI    app.py  #site1@1  #site2@10  same image, distinct loci

wales
  MULTI    app.py  #site1,#site2  same image, distinct loci; apply each
          apply:line=ok,time=ok,topo=ok same-tree  applied=[site2,site1]
```

plait collapsed this to ECHO and applied `['site1']`, leaving L10 as `return 0`. wale names MULTI and applies both sites → `return 1` at L1 and L10.

### 3. Two reviewers, one line — still a split; overlap still a jam

```bash
./wale fixtures/split.jsonl   # rc=1  SPLIT
./wale fixtures/jam.jsonl     # rc=2  JAMMED
```

Same locus, two afters is disagreement. Overlapping *different* ranges are JAM. Same after at one locus is still ECHO (apply once).

Compose: `gh api …/comments | ./wale --json | jq '.components[] | {verdict,path,strands}'`
