# destroyer-23 — braid occupancy of the fold

Adversarial pass on **braid** (hybrid-12): compose review-suggestion strands, then occupy the **single composed after-image**. Not plait's schedule table. Not hank `--emit`.

Victim: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cbac00204512`

Report: [`DESTROYER_BRAID.md`](DESTROYER_BRAID.md) (also `lab/judges/DESTROYER_BRAID.md`). Transcript: `/tmp/destroy-braid/`.

Verdict: **mutate, do not kill.** `stack-mid` is SUPERSEDED of `beta→beta3` while plea is APPLIED of round 1. Three-round STACK cannot occupy. Covering gap-fill absorbs unclaimed drift.

## Install / run

Python 3.9+, stdlib. Does not rewrite the victim.

```bash
chmod +x ./attack.py ./demo.sh
./demo.sh
python3 ./attack.py          # fills /tmp/destroy-braid/
```

`BRAID`, `PLEA`, `HANK`, `QUIRE`, `DESTROY_ROOT` override paths.

## Examples

### 1. STACK mid-state — the object

```bash
BRAID=…/braid
$BRAID --json -C $BRAID/../fixtures/trees/stack-mid $BRAID/../fixtures/stack.jsonl
# compose=SERIES occupy=SUPERSEDED   fold beta→beta3
```

plea on the same tree: APPLIED round1 + PENDING round2.

### 2. Covering gap-fill is not "drift SUPERSEDES"

```bash
python3 ./attack.py   # trees/window-drift-mid = alpha/BETA/gamma
$BRAID -C /tmp/destroy-braid/trees/window-drift-mid \
       /tmp/destroy-braid/fixtures/window-commute.jsonl
# occupy=PENDING  composed  alpha|BETA|gamma → ALPHA|BETA|GAMMA
```

### 3. Three-round series is SPLIT (no occupy)

```bash
$BRAID /tmp/destroy-braid/fixtures/stack-three.jsonl
# compose=SPLIT occupy=—  rc=1
# plait on the same stream is SERIES
```

Exit of `./demo.sh`: 0 if victim gold + the money-shot contrast still hold.
