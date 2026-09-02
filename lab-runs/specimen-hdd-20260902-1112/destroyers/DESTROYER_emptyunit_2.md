# DESTROYER emptyunit 2

Date: 2026-09-02 14:17 JST

Target: `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/emptyunit`

sha256 `2e06e14b00bc311c798077baaa9e27ee0644579f6150c4eeb2ef2433cb0f5057` (matches `MUTATE.md`). unittest `python3 tests/test_emptyunit.py -v` 22/22. No pytest-xdist import, no pytest-xdist run, no merge onto `main`.

Parent: `destroyers/DESTROYER_emptyunit.md` → MUTATE. Applied cut: hang_risk is next FIFO empty send; rc=1 on hang; handwritten both-done rec refused; loadgroup grouping; ingest `{collection, workqueue}` JSON/Python dict.

This attack is the remaining holes that cut listed, plus the new dump ingest.

```
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/emptyunit
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/fixtures
```

## What still works

Owned dump hang, live-first not hang, loadscope mixed not hang, handwritten `063-hang.rec` `scope mismatch`, hang log `not a workqueue dump`, missing incomplete `index-error`, `collection none` is a nodeid, empty lists print `-`, missing file / `/dev/null` rc=1.

```
python3 "$CLI" "$FIX/063-hang.dump"
# hang_risk yes; would_send (); first_assigned testing/test_timeout.py::test_1; rc=1
```

That is the whole useful delta. Attacks below show hang_risk is a rename of “first workqueue dict is all True”, dist is a sticker on already-grouped keys, and a legal dump of 257 loadgroup tests cannot enter.

## Implementation

### 1. THIN_WRAPPER of the empty-list check

Harvest: `_assign_work_unit` builds

```
nodeids_indexes = [
    worker_collection.index(nodeid)
    for nodeid, completed in work_unit.items()
    if not completed
]
node.send_runtest_some(nodeids_indexes)
```

and hangs when that list is `[]`.

Code after MUTATE:

```
completed_only = bool(items) and not incomplete
empty_send = completed_only
...
hang = first["empty_send"]   # only if pending > 0
```

Host-executed: `empty_send` equals `completed_only_unit` on every scope of owned 063 (`yes/yes`, `no/no`) and on a three-unit dump (`no/no`, `yes/yes`, `no/no`). After index-error for missing incompletes, `send ()` iff the unit is completed-only. Two names, one bit.

Nearest ordinary workflow on the owned dump (no CLI):

```
python3 -c '
import ast,sys
d=ast.literal_eval(open(sys.argv[1]).read())
wq,c=d["workqueue"],d["collection"]
pending=sum(1 for u in wq.values() for v in u.values() if not v)
first=next(iter(wq.values()))
idxs=[c.index(n) for n,done in first.items() if not done]
print(pending, idxs, bool(pending and not idxs))
' "$FIX/063-hang.dump"
```

```
1 [] True
```

Same hang bit the CLI prints. Dist is not consulted. Grouping is already the dict keys.

### 2. Later assign is still not hang_risk (named remaining hole)

xdist `_reschedule` assigns another unit when `_pending_of(assigned) <= 2`. A replacement therefore gets FIFO first *and* FIFO second whenever the first unit has 1–2 pending tests.

Live-first + completed-only second (the MUTATE “not hang” case):

```
python3 "$CLI" "$FIX/unseen-live-first.rec"
```

```
first_assigned	live.py::u
would_send	(1)
hang_risk	no
empty_send	no          # live
empty_send	yes         # done.py::t, second unit
rc:0
```

Same shape as JSON:

```
printf '%s\n' '{"collection":["live.py::u","done.py::t"],"dist":"loadgroup","workqueue":{"live.py::u":{"live.py::u":false},"done.py::t":{"done.py::t":true}}}' | python3 "$CLI" -
```

```
would_send	(0)
hang_risk	no
rc:0
```

Under `-n1 --dist=loadgroup` the replacement is given the live unit (pending 1 ≤ 2) and then the completed-only unit as `send ()`. That is a hang. `hang_risk no` is a false negative the last mutation required. `empty_send yes` on a non-first row is not the predicate (rc stays 0).

Three units live / done / live: `hang_risk no`, middle `empty_send yes`. First pending=3 then completed-only (loadscope): still `hang_risk no`. The watermark is never simulated.

### 3. Dist is a key sticker, not a scheduler (scope mismatch / loadscope vs loadgroup)

`split_scope` is only `if scope != derived: error`. Work units are the dump keys in insertion order. The CLI does not build a queue from collection+dist.

Same two tests, caller regroups:

```
printf 'collection\tmod.py::a\tmod.py::b\ndist\tloadgroup\nunit\tmod.py::a\tmod.py::a\tdone\nunit\tmod.py::b\tmod.py::b\topen\n' | python3 "$CLI" -
# hang_risk yes / would_send () / rc=1

printf 'collection\tmod.py::a\tmod.py::b\ndist\tloadscope\nunit\tmod.py\tmod.py::a\tdone\nunit\tmod.py\tmod.py::b\topen\n' | python3 "$CLI" -
# hang_risk no / would_send (1) / rc=0
```

Flip dist on the *same* keys and you do not get the other answer. You get mismatch:

```
# 063-hang.json with dist forced to loadscope
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); d["dist"]="loadscope"; json.dump(d,sys.stdout)' "$FIX/063-hang.json" | python3 "$CLI" -
```

```
emptyunit: <stdin>: scope mismatch 'testing/test_timeout.py::test_1' != 'testing/test_timeout.py' (loadscope)
rc:1
```

loadgroup + module-shaped keys: same class of error. loadscope module key for class tests `m.py::T::a`: `scope mismatch 'm.py' != 'm.py::T'`. Handwritten both-done rec is that sticker (`063-hang.rec` line 4).

When keys are already grouped, `@group` works (`first_assigned	g`, one unit, `hang_risk no`) and two groups done-first hangs (`first_assigned	g1`, `would_send ()`). That is xdist `_split_scope`. It is also the caller writing those keys. Dist does not regroup.

`foo@bar.py::test` as full nodeid (ungrouped loadgroup spelling) is refused: derived scope is `bar.py::test`. Using the derived key is accepted. Inherited xdist `@` vs `]` rule, not a new join.

### 4. Ingest is an invented envelope, not `print(workqueue)`

MUTATE: “Ingest is a real `{collection, workqueue}` dump (JSON or Python dict).” Host:

| input | result |
| --- | --- |
| `OrderedDict([...])` repr (actual `print(workqueue)`) | `expected key<TAB>value` rc=1 |
| `print(dict(workqueue))` raw nested dict | `collection is required` rc=1 |
| envelope JSON/Python `{collection, workqueue, dist}` | owned hang named |
| `"assigned"` instead of `"workqueue"` | same hang |
| `"workqueue": {}` plus filled `"assigned"` | `no workqueue units` (empty dict wins) |
| JSON array / `{}` / missing workqueue | object/collection/workqueue errors |
| JSONL two objects, trailing comma, `/* comment */` | `not a JSON/Python workqueue dump` |
| UTF-8 BOM JSON | accepted |
| TSV `workqueue` JSON/Python field | accepted |
| unit rows then `workqueue` | `workqueue dump after unit rows` |
| `collection: [null]` / `[true]` / `[0]` | nodeids `None` / `True` / `0`, rc=0 |
| `"collection": "none"` (string) | `collection must be a list` |
| `"collection": ["none"]` | nodeid `none`, rc=0 |
| nodeid containing TAB | TSV splits `collection	a	b` |
| duplicate JSON key `"collection"` | last-wins, silent rc=0 |

`str()` on non-string collection items is a silent identity. A pdb `print(self.workqueue)` still does not ingest. The envelope already contains FIFO-ordered scopes and completed flags; the CLI reprints the empty-list check.

`dist` omitted defaults `loadgroup`. `dist none` / `load` / `loadfile` / `each` / `LoadGroup`: `dist must be loadgroup|loadscope`. Fine as a closed enum; it is not `--dist=load` semantics.

### 5. Cap refuses a legal dump

`MAX_COLLECTION = 512`, `MAX_UNITS = 256`. Host:

```
# 512 collection nodeids, 2 units: rc=0
# 513 collection: "collection exceeds cap (512)" rc=1
# 256 loadgroup units: rc=0 (and first-done is hang_risk yes)
# 257 loadgroup units: "workqueue exceeds cap (256)" rc=1
# loadscope 1 unit × 512 tests: rc=0
# loadscope 1 unit × 513 tests: collection cap, not unit cap
# TSV collection 513: same cap error
# 10k-char nodeid, count=1: rc=0 (count cap only; dumps the name)
```

Caps refuse, they do not truncate (as MUTATE said). A real `--dist=loadgroup` session with 257 tests is a legal workqueue and cannot be named. The tool is specimen-sized. 256-unit stdout is already tens of KB of per-scope reprint.

### 6. none token vs sentinel `-`

MUTATE: empty lists print `-`, not `none`; nodeid `none` is a real identity. Host confirms `collection	none` / JSON `["none"]` are identities, `completed_only	-` when none completed-only.

Nodeid literally `-`:

```
printf '%s\n' '{"collection":["-","x"],"workqueue":{"-":{"-":true},"x":{"x":false}}}' | python3 "$CLI" -
```

```
collection	-	x
completed_only	-
incomplete_scopes	x
first_assigned	-
would_send	()
hang_risk	yes
scope	-
items	-
completed	-
incomplete	-
missing	-
```

`completed_only	-` is now “the completed-only unit is named `-`”, not “none”. `incomplete	-` on that scope is the empty sentinel. Same token, two meanings, one table. `dist none` is an error, not a nodeid. That split is undocumented except by running it.

## Primitive

Reality-stripped operation: parse a caller-grouped `{scope: {nodeid: bool}}`; if pending>0 and the first dict is all completed, print `hang_risk yes` and exit 1.

Nearest ordinary workflow: the one-liner in §1, or reading `send_runtest_some`’s list comprehension on `next(iter(workqueue.values()))`. Observable capability lost if emptyunit vanishes: the TSV labels and the rec-sticker refusal. The hang bit is `pending and not idxs`. Dist/scope is `derived == key`. `empty_send` is `completed_only`.

That is why this is MUTATE, not KILL: the *question* (a completed-only unit requeued as `send ()`, and why loadgroup hangs while loadscope on the same tests does not) is still a real debugging object. This embodiment asks only “is the first already-grouped dict empty of False?” and will not ingest the object xdist actually prints.

Hardcoded ceiling:

- hang_risk = FIFO-first empty send only; `_reschedule` later `()` is `hang_risk no` rc=0
- empty_send = completed_only
- dist validates keys, does not regroup collection
- envelope dump, not `OrderedDict` / `print(workqueue)`
- collection/workqueue caps 512/256 refuse legal tables
- `-` is both empty and a legal nodeid
- `str(None)`/`str(True)`/`str(0)` become nodeids
- not a LoadScopeScheduling implementation; do not merge with `requeue`

## Mutation (what must change)

Keep the object: name a completed-only work unit that a replacement would be sent as `send_runtest_some([])`.

Do not keep a pretty-printer of `not [index for n,done in first.items() if not done]`.

1. **Assign loop, not first-only.** hang_risk must fire if any unit the replacement would actually receive is an empty send, including the `_reschedule` low-watermark (pending ≤ 2) second assign. `empty_send` means “this assign sends `()`”, not an alias of `completed_only`. Live-first + completed-only second is hang, rc=1. Owned 063 stays hang.

2. **Dist grouping is a scheduler.** Derive work units from collection+dist (`loadgroup` full nodeid / `@` after `]`; `loadscope` `rsplit("::", 1)`), or accept a raw workqueue and ignore caller scope keys. `scope mismatch` as the only loadscope-vs-loadgroup effect is a sticker. Same tests under the two dists must change hang_risk without the caller regrouping.

3. **Ingest what xdist prints.** `print(workqueue)` / `OrderedDict` plus a collection list. JSON and `dict(...)` envelopes may stay. Refuse `str()` coercion of null/bool/int nodeids. `workqueue {}` must not shadow `assigned`. Quote or refuse nodeid `-` so it cannot collide with the empty sentinel. `none` stays an identity; `dist none` stays an error.

4. **Caps.** 257 loadgroup units is a legal dump. Raise, stream, or note-and-truncate. Do not pretend a 256-scope ceiling is the pytest collection.

If the mutation cannot do (1)+(2), the object is still the empty-list check on a pre-grouped first dict, and a later destroyer should KILL as THIN_WRAPPER.

Do not merge onto `main`. Do not import pytest-xdist.

---

MUTATE
