# plait

Review suggestions are strands. GitHub "outdated" is a boolean. `git apply --check` is a boolean. plea/sate occupy each claim against a *tree*. **plait asks whether the strands compose with each other.**

| verdict | meaning |
| --- | --- |
| **COMMUTE** | disjoint edits; any apply order, same tree |
| **STACK** | after(A) *is* before(B); only A then B |
| **ECHO** | same before→after; apply once |
| **SPLIT** | same before, two afters; reviewers disagree |
| **SUBSUME** | outer span consumes a consistent inner |
| **JAM** | overlapping incompatible edits |
| **THREAD** | reply chain on a locus (`--remarks`) |
| **COVER** | a remark sits on a suggestion |

A file's **plait** is PARALLEL / SERIES / ECHO / SUBSUME / SPLIT / JAMMED / THREAD. Apply schedules (`line` / `time` / `topo`) are witnesses, not the object.

## Install / run

Python 3.10+, stdlib only. `git` only if `--against REF`.

```bash
chmod +x ./plait ./demo.sh
./plait --help
./plait --selftest
./demo.sh
```

Exit: `0` composable (PARALLEL / SERIES / ECHO / SUBSUME / THREAD), `1` SPLIT, `2` JAMMED, `3` error. `--report-only` forces `0`. `--json` / `--tsv` compose.

## Examples

### 1. Will "Commit suggestion" in comment order work?

```bash
gh api repos/cli/cli/pulls/7/comments | ./plait
./plait fixtures/cli-pr7.json
```

```
plait  n=2  files=1  components=1  PARALLEL=1

pairs
  COMMUTE  command/pr.go  #333030758@347  #333031216@400  disjoint spans

plaits
  PARALLEL command/pr.go  #333030758,#333031216  independent; compose in any order
```

Two suggestions on one file, different lines, same snapshot: they commute. GitHub's "outdated" never said that.

### 2. Two review rounds stack; clock order is a lie

```bash
mkdir -p /tmp/t && printf 'alpha\nbeta\ngamma\n' > /tmp/t/app.py
./plait -C /tmp/t fixtures/stack.jsonl
```

```
plaits
  SERIES  app.py  #round1,#round2  unique apply order
          apply:line=fail,time=fail,topo=ok  different-trees
```

Round 2's before-image is round 1's after-image. Time order (round2 created_at is earlier in the fixture) fails. Topo order (image stack) yields `beta3`. plea would occupy each against HEAD independently and never say SERIES.

### 3. Two reviewers, one line — not a jam, a split

```bash
./plait fixtures/split.jsonl
```

```
pairs
  SPLIT  app.py  #alice@1  #bob@1  same before, two afters
```

Exit `1`. Overlapping *different* ranges are JAM (exit `2`). Same after is ECHO.

Compose: `gh api …/comments | ./plait --json | jq '.components[] | {verdict,path,strands}'`
