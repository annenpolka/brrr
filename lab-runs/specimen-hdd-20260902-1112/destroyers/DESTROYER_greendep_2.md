# DESTROYER greendep 2

Date: 2026-09-02 14:52 JST (attacks) / 14:58 JST (record)
RUN_ID: specimen-hdd-20260902-1112
Target: `lineages/candidate-greendep/greendep` after job-0274 per-query mutate
(`MUTATE.md` sha256 `fa30c9a03ded1617713cf42fe3aa52193d0c10ef651b848e433b8c03cc90b857`, 6559 bytes)

Worktree `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-greendep-greendep` HEAD `8365fbe`. Parent remains `main`. rustc not invoked. No merge onto `main`.

Host `python3 -m unittest discover -s tests -v` against that cut: 16/16 OK. `demo.sh` identical. Unrelated-green attack **passed** (only owner is `false_green`).

First mutate leftover (MUTATE.md “Not faked”) still live. Decision: **MUTATE**.

CLI used for these attacks:

```text
CLI=.../lineages/candidate-greendep/greendep   # pre second-cut
```

## What still worked (first mutate)

Owned 075-poll / 075-green: `false_green` the owner, `unrecorded_changed	query	Q	dep	type_of(Error)`, rc=1.

Unrelated green (`unrelated.rec`): `false_green	typeck_of(S::poll)` only.

Global `changed	D1	D2	D3` refused. Two greens + shorthand `changed	DEP` refused.

## Holes vs DESTROYER_greendep mutation spec §2–§3, §5

### 1. Incomplete record is agreement (rc=0), not rc=2

```bash
printf 'query\ta\tgreen\ndep\ta\tx\n' | python3 "$CLI" -; echo rc=$?
printf 'query\ta\tgreen\n' | python3 "$CLI" -; echo rc=$?
```

Both:

```text
green	a
red	-
changed	-
false_green	-
unrecorded_changed	-
invalidation	-
rc=0
```

No `incomplete` row. Green + recorded deps with a forgotten `changed` line is a clean session. Spec: rc≠0 (`incomplete`), not `false_green -`.

### 2. Recorded ∩ own-changed is invalidation rc=1 (treated as miss)

1-part shorthand `changed	Y` with `dep	a	Y`:

```bash
printf 'query\ta\tgreen\ndep\ta\tY\nchanged\tY\n' | python3 "$CLI" -; echo rc=$?
```

```text
green	a
changed	query	a	dep	Y
false_green	-
unrecorded_changed	-
invalidation	query	a	dep	Y
rc=1
```

Same for 2-part `changed	a	Y`. Spec: labeled `recorded_changed_green` / `invalidation`, **not** rc=1 as if unrecorded. `rc=0` only for a complete record with no unrecorded-changed green. `unseen-recorded.rec` tests encoded rc=1.

`agree.rec` (red, recorded the changed dep) stayed rc=0 — correct for this primitive.

### 3. `-` is still a legal NAME; `true` is still red

```bash
printf 'query\t-\tgreen\nchanged\t-\tD\n' | python3 "$CLI" -
# green	- / false_green	- / unrecorded_changed	query	-	dep	D / rc=1

printf 'query\ta\ttrue\nchanged\ta\tx\n' | python3 "$CLI" -
# green	- / red	a / rc=0
```

`-` collides with the empty sentinel. `true`/`1` are red, not errors.

## Primitive after first mutate

Per-query `changed	QUERY	DEP` (or shorthand to the unique green). `false_green` = green with `set(own-changed) - set(recorded[q])` nonempty, rc=1. `invalidation` = recorded ∩ own-changed, **also rc=1**. Incomplete green is rc=0.

Unrelated-green hole is closed. Incomplete + invalidation-as-failure + `-`/color leftover remain.

Do not add rustc ingest. Do not merge into visitid.

---

MUTATE
