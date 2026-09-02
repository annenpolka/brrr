# DESTROYER reimpl-emptyunit-2

Date: 2026-09-02 17:37 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0506 worker=destroyer-reimpl-emptyunit-2

Target: `lineages/reimpl-emptyunit-2/emptyunit`
Claim: leftover empty-unit identity as collection-index partitions;
`hang_risk` is any burst partition whose send list is `()`. Dist:
loadgroup vs loadscope. Parent `candidate-emptyunit` after
`DESTROYER_emptyunit_3` KEEP. Style `idxpart`. Specimen-063.

sha256 `3ba6d4b70a37aec60b2db926752457e9b9668948e1e51cce16e12847b797ad93`
(16020 bytes, 501 lines). Archive HEAD.txt `b1eb24f` (`Refresh
reimpl-emptyunit-2 HEAD after metadata commit.`). Worktree copy at
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/reimpl-emptyunit-2-idxpart/reimpl-emptyunit-2/emptyunit`
is **byte-identical** (`cmp` rc=0). Worktree git HEAD `b1eb24f`, branch
`specimen-hdd/reimpl-emptyunit-2-idxpart`. Parent `main` `432f954`;
`git ls-tree HEAD emptyunit` is empty. CLI bytes are **not** identical
to parent KEEP (`candidate-emptyunit` sha256
`9e224d35637d45ea2f324e439f784c25c003d47c5b12cce6550e221078758627`,
24307 bytes, 650 lines; `cmp` rc=1). Host Python 3.14.5. `xdist` /
`pytest` specs are `None`. CLI ast imports are stdlib only
(`ast`, `json`, `sys`, `collections`, `dataclasses`, `pathlib`,
`typing`). No `pytest` / `xdist` strings in the CLI. unittest
`python3 tests/test_emptyunit.py -v` 31/31 archive twice and worktree.
Candidate unittest 39/39. No pytest-xdist import, no pytest-xdist run,
no merge onto `main`. Host `demo.sh` ×2 byte-identical to each other
and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 348 lines).

Prior: `destroyers/DESTROYER_emptyunit.md` KEEP (FIFO hang_risk).
`destroyers/DESTROYER_emptyunit_2.md` MUTATE. `destroyers/DESTROYER_emptyunit_3.md`
KEEP (assign-loop + dist regroup). First KEEP of parent emptyunit is
**not** protection for this reimpl. First reimpl
(`lineages/reimpl-emptyunit/`, queue-object drain without dist regroup)
is a different failed style, not this object.

Honor KILL if:

1. THIN_WRAPPER of first-dict empty-list check / dist sticker
2. Same primitive as `candidate-emptyunit` (copy, not a second style)
3. Replica of leftover formula is byte-identical to two greps / first-dict empty

(1) and (3) do **not** fire. (2) **does**. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/reimpl-emptyunit-2/emptyunit
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/reimpl-emptyunit-2/fixtures
CA=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/emptyunit
CAFIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/reimpl-emptyunit-2-idxpart/reimpl-emptyunit-2/emptyunit
SCR=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_reimpl-emptyunit-2_scratch
```

Independent replica in `destroyers/_reimpl-emptyunit-2_scratch/attack.py`
does **not** import either emptyunit. No pytest. No pytest-xdist. Do not
merge with `candidate-emptyunit` / `requeue` / first `reimpl-emptyunit`.
Do not grow a LoadScopeScheduling. Do not send THIN_WRAPPER back to R1.
Do not mutate this copy into looking unlike the parent.

---

## What the KEEP harvest still names (this CLI)

Owned dump hang, live-first reschedule hang, pending=3 hold, handwritten
both-done not hang, hang log refused, `print(workqueue)` OrderedDict
ingests, 257 loadgroup units legal, same tests loadgroup vs loadscope
without caller regroup.

```bash
python3 "$CLI" "$FIX/063-hang.dump"; echo rc=$?
python3 "$CLI" "$FIX/unseen-live-first.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen-pending3.rec"; echo rc=$?
printf '%s\n' '{"collection":["mod.py::a","mod.py::b"],"dist":"loadgroup","workqueue":{"mod.py::a":{"mod.py::a":true},"mod.py::b":{"mod.py::b":false}}}' | python3 "$CLI" -
printf '%s\n' '{"collection":["mod.py::a","mod.py::b"],"dist":"loadscope","workqueue":{"mod.py::a":{"mod.py::a":true},"mod.py::b":{"mod.py::b":false}}}' | python3 "$CLI" -
```

Owned `063-hang.dump` (rc=1):

```text
first_assigned	testing/test_timeout.py::test_1
would_send	()
assigned	testing/test_timeout.py::test_1
reschedule	no
hang_unit	testing/test_timeout.py::test_1
hang_risk	yes
scopes_n	2
```

Live-first (`unseen-live-first.rec`, rc=1):

```text
first_assigned	live.py::u
would_send	(1)
assigned	live.py::u	done.py::t
reschedule	yes
hang_unit	done.py::t
hang_risk	yes
```

Pending=3 then completed-only: `hang_risk no`, `reschedule no`,
`hang_unit -`, rc=0. Same tests, no caller regroup: loadgroup rc=1
`would_send ()` `scopes_n 2`; loadscope rc=0 `would_send (1)`
`scopes_n 1`. That is the DESTROYER_3 KEEP object.

It is also **byte-identical** to parent KEEP on every shared fixture
stdout+rc+stderr (11/11): owned dump/json/wq, live-first, two-scopes,
pending2, pending3, mixed, handwritten 063 rec, loadscope-alldone,
loadscope-open.

---

## Honor-KILL 1: first-dict empty-list / dist sticker? No.

DESTROYER_2 §1 one-liner on the owned dump (no CLI):

```bash
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

```text
1 [] True
```

That still names owned 063. It does **not** name this CLI.

Host, first-dict sticker (`pending and not idxs` on
`next(iter(workqueue.values()))`, no dist, no second assign) and the
two-membership leftover (`any incomplete` AND `first bag all True`) vs
CLI `hang_risk`:

| case | sticker | two_greps | CLI hang_risk | match |
| --- | --- | --- | --- | --- |
| owned 063 | True | True | yes | yes |
| live-first | False | False | yes | **no** |
| same tests loadgroup | True | True | yes | yes |
| same tests loadscope | True | True | no | **no** |
| done-first | True | True | yes | yes |
| owned forced loadscope | True | True | no | **no** |
| pending3 loadscope-shaped | False | False | no | yes |

MATCH 4/7. The three misses are DESTROYER_3: assign-loop (second empty
send) and dist regroup (loadscope joins the same keys into one unit).
Dist is not a key sticker. Hang is not “first already-grouped dict is
all True”. Honor-KILL (1) and (3) do not fire.

`empty_send` still equals `completed_only_unit` on every reported unit
of every fixture after index-error (two names, one bit). Hang_risk is
that bit on the burst. Not faked. Same coincidence DESTROYER_3 already
named on the parent.

---

## Honor-KILL 2: same primitive as candidate-emptyunit. Yes.

Claimed second style (`CANDIDATE.md` / `REALITY.md`): “collection-index
partitions rather than a named-dict walk of caller-grouped keys.”

Parent KEEP after mutate-3 is **already not** a named-dict walk of
caller-grouped keys. `DESTROYER_emptyunit_3.md` primitive:

> flatten a workqueue dump to `{nodeid: completed}`, group by dist
> (`_split_scope`), then name whether any unit in the replacement-start
> burst (FIFO first, plus one more if that unit’s pending ≤ 2) would be
> `send_runtest_some([])`.

This CLI:

```python
def scope_of(nodeid, dist):
    if dist == "loadscope":
        return nodeid.rsplit("::", 1)[0]
    at, bracket = nodeid.rfind("@"), nodeid.rfind("]")
    if at != -1 and at > bracket:
        return nodeid[at + 1 :]
    return nodeid

def send_indexes(self, collection):
    return [collection.index(n.nodeid) for n in self.incompletes()]

# burst
assigned = [parts[0]]
if 1 <= parts[0].pending() <= 2 and len(parts) > 1:
    assigned.append(parts[1])
hang_risk = any(not part.send_indexes(collection) for part in assigned)
```

Parent KEEP:

```python
def split_scope(nodeid, dist):
    if dist == "loadgroup":
        if nodeid.rfind("@") > nodeid.rfind("]"):
            return nodeid.split("@")[-1]
        return nodeid
    return nodeid.rsplit("::", 1)[0]

# regroup flags by split_scope; send = collection positions of incompletes
# burst: FIFO first, plus one more if pending <= 2
hang_risk = any(unit["empty_send"] for unit in assigned)
```

`collection.index` vs `{nodeid: i}` is the same send list. `WATERMARK_LO=1`
vs “if first `empty_send`, do not reschedule” is the same burst.
Caller keys are ignored in both (`flatten_units` / `flatten_workqueue`).
Copied xdist grouping bugs match: loadscope `rsplit("::", 1)` on
`m.py::test[a::b]` vs `m.py::test[c]` is two partitions, first empty
send, hang; `@` inside `[]` stays the full nodeid.

Independent replica (flatten inner nodeids, `_split_scope`, FIFO first,
then one more if first pending is 1 or 2, hang if any assigned send is
`()`) MATCH CLI harvest fields on owned, live-first, loadgroup-same,
loadscope-same, done-first, forced-loadscope 063, pending3 (7/7) and on
every JSON subset of the compare battery (13/13). That replica **is**
the DESTROYER_3 object. It is not a new leftover identity.

Host, reimpl vs candidate harvest fields
(`rc`, `hang_risk`, `would_send`, `first_assigned`, `assigned`,
`reschedule`, `hang_unit`, `scopes_n`, `pending`):

**SAME 30/30**, including owned dump/json/wq, live-first, two-scopes,
pending2/3, mixed, handwritten 063 rec, hang log refuse, same tests
loadgroup vs loadscope, forced-loadscope 063, caller module-shaped keys,
class rsplit, `@g` group, 257 first-done, three live/done/live, two
live, missing incomplete index-error, dash nodeid refuse, `dist none`,
empty `workqueue` plus `assigned`, xdist #1335, `@` inside `[]`, FIFO
follows dump not collection, completed-only missing from collection.

Owned dump stdout is **byte-identical** to parent KEEP. All 11 shared
fixture files are stdout+rc+stderr byte-identical.

CLI source is a clean-room rewrite (dataclasses vs dicts, `eval` vs AST,
argv vs argparse, 16020 vs 24307 bytes). Constitution 13.4: independent
recovery of the same interaction is evidence of **parent** primitive
strength. It is not a second leftover-identity style. The job asked for
a second style. This is a copy of mutate-3 KEEP dressed as
“collection-index partitions.” Honor-KILL (2) fires.

Ingest differences are not a leftover join: reimpl refuses a flat
`{nodeid: bool}` workqueue (`work unit must be a dict`); candidate
accepts it. Reimpl `eval(..., {"OrderedDict": OrderedDict})` accepts
`1-1` as a completed flag; candidate AST dump refuses. Reimpl TSV has
no `workqueue` JSON field (`unknown row workqueue`); candidate does.
Hang-log needles differ (`workers [` vs `collecting:`). Those are
parser stickers. The leftover formula is the same.

---

## Other host holes (ceilings of the parent, not a mutation slot)

1. **Replacement vs initial burst.** Burst is first + at most one extra.
   Completions are not simulated. Two live then completed-only:
   `assigned` first two lives, `hang_risk no`. Pending=3 then
   completed-only stays `hang_risk no`. Same ceiling DESTROYER_3 listed.
   Do not grow a scheduler to close this.

2. **`would_send` names the first send.** Live-first: `would_send (1)`
   while `hang_unit` is the second `()`.

3. **FIFO follows dump/unit insertion, not collection order.** Collection
   `done` then `live` with unit rows live-first still assigns live first.

4. **Ingest leftovers.** JSONL two objects, trailing commas, `/* comments */`
   refused. Duplicate JSON `collection` last-wins. Nonempty `workqueue`
   shadows filled `assigned` (empty `workqueue {}` does not). Nodeid `-`
   refused. `none` is an identity. `dist none` / `loadfile` error (closed
   enum). UTF-8 BOM JSON accepted. `/dev/null` / empty stdin rc=1.
   Completed-only nodeid missing from collection is still a hang unit
   (no index-error). Collection 8192 legal; 8193 safety-cap refused
   (labeled, not pytest).

5. **TSV identity.** A JSON nodeid containing TAB prints as two TSV
   fields (`first_assigned	a.py::t	x`).

6. **Copied xdist grouping bugs.** Same as parent KEEP.

Do not mutate this reimpl to escape a KILL that applies. Growing a
thicker parser here would still be the KEEP object twice.

---

## Primitive

Reality-stripped operation: flatten a workqueue dump to
`(nodeid, completed)` in insertion order, partition by dist
(`loadgroup` full nodeid / `@` after `]`; `loadscope` `rsplit("::", 1)`),
then name whether any unit in the replacement-start burst (FIFO first,
plus one more if that partition’s pending is 1 or 2) would be
`send_runtest_some([])`. rc=1 on that hang.

That is `candidate-emptyunit` after DESTROYER_emptyunit_3. Collection
indexes are how both spell `send_runtest_some`. There is no second
leftover identity.

Nearest ordinary workflow: the DESTROYER_3 replica, or reading
`print(workqueue)` plus the list comprehension in `_assign_work_unit`
plus one `_reschedule`. Observable capability lost if *this* emptyunit
vanishes: none the parent KEEP does not already have. The parent KEEP
remains. This archive is a second PATH spelling of the same leftover.

That is why this is KILL, not KEEP: Honor-KILL (2) is “copy, not a
second style.” First KEEP of parent is not protection. Constitution 13.4
does not keep two installs of the same leftover formula.

That is why this is KILL, not MUTATE: ingest holes (flat workqueue,
`eval` arithmetic, TSV `workqueue` field) are not a leftover-identity
cut. A copy does not gain exotic features to escape. Do not mutate this
into looking unlike `candidate-emptyunit`. Do not merge onto `main`.
Do not import pytest-xdist. Do not merge with `requeue`.

Hardcoded ceiling (inherited, not a new object):

- burst is first + at most one extra; not a completion-driven `_reschedule` loop
- `empty_send` coincides with `completed_only` after index-error
- dist is `loadgroup|loadscope` only
- collection safety cap 8192
- TSV does not quote TAB in nodeids
- not a LoadScopeScheduling implementation

---

KILL
