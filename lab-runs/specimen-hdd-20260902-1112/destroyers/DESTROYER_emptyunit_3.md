# DESTROYER emptyunit 3

Date: 2026-09-02 15:40 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0364 worker=destroyer-emptyunit-3

Target: `lineages/candidate-emptyunit/emptyunit` AFTER mutate-3
(`MUTATE.md` third cut: dist regroups; ingest `print(workqueue)`; 257 units
legal. Assign-loop kept from cut (1).)

sha256 `9e224d35637d45ea2f324e439f784c25c003d47c5b12cce6550e221078758627`
(24307 bytes, matches `MUTATE.md`). Archive HEAD.txt `4168ca2` (`MUTATE
emptyunit: dist regroups; ingest print(workqueue); 257 units`). Worktree
copy at
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-emptyunit-emptyunit/candidate-emptyunit/emptyunit`
is **byte-identical** (`cmp` rc=0). Worktree git HEAD `028817d` only records
mutation metadata on top of `4168ca2`; CLI bytes unchanged. Parent `main`
`432f954`; `git ls-tree` has no `emptyunit`. Host Python 3.14.5. `xdist` /
`pytest` specs are `None`. CLI ast imports are stdlib only
(`argparse`, `ast`, `json`, `sys`, `collections`, `pathlib`). unittest
`python3 tests/test_emptyunit.py -v` 39/39 archive and worktree. No
pytest-xdist import, no pytest-xdist run, no merge onto `main`.
`demo-1.log` / `demo-2.log` byte-identical.

Prior: `destroyers/DESTROYER_emptyunit.md` KEEP (FIFO hang_risk).
`destroyers/DESTROYER_emptyunit_2.md` MUTATE. First KEEP/MUTATE is not
protection. Honor KILL if this cut is still THIN_WRAPPER of first-dict
empty-list check / dist sticker. Mutate-3 claimed assign-loop — verified
host-executed. It is **not** that wrapper. Decision: **KEEP**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/emptyunit
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-emptyunit-emptyunit/candidate-emptyunit/emptyunit
```

No pytest. No pytest-xdist. Do not merge with `requeue`. Do not grow a
LoadScopeScheduling. Do not send THIN_WRAPPER back to R1.

---

## What mutate-3 claimed, host-executed

Owned dump hang, live-first reschedule hang, pending=3 hold, handwritten
both-done not hang, hang log refused, `print(workqueue)` OrderedDict
ingests, 257 loadgroup units legal, same tests loadgroup vs loadscope
without caller regroup.

```bash
python3 "$CLI" "$FIX/063-hang.dump"; echo rc=$?
python3 "$CLI" "$FIX/unseen-live-first.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen-pending3.rec"; echo rc=$?
python3 "$CLI" "$FIX/063-hang.wq"; echo rc=$?
python3 "$CLI" "$FIX/063-hang.rec"; echo rc=$?
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

Live-first (`unseen-live-first.rec`, rc=1) — this is the assign-loop:

```text
first_assigned	live.py::u
would_send	(1)
assigned	live.py::u	done.py::t
reschedule	yes
hang_unit	done.py::t
hang_risk	yes
```

Pending=3 then completed-only: `hang_risk no`, `reschedule no`, `hang_unit -`,
rc=0. OrderedDict `063-hang.wq`: hang, rc=1. Handwritten both-done rec:
`pending 0`, `hang_risk no`, rc=0, no `scope mismatch`.

Same tests, no caller regroup:

```bash
printf '%s\n' '{"collection":["mod.py::a","mod.py::b"],"dist":"loadgroup","workqueue":{"mod.py::a":{"mod.py::a":true},"mod.py::b":{"mod.py::b":false}}}' | python3 "$CLI" -
printf '%s\n' '{"collection":["mod.py::a","mod.py::b"],"dist":"loadscope","workqueue":{"mod.py::a":{"mod.py::a":true},"mod.py::b":{"mod.py::b":false}}}' | python3 "$CLI" -
```

```text
# loadgroup  rc=1
first_assigned	mod.py::a
would_send	()
hang_risk	yes
scopes_n	2

# loadscope  rc=0
first_assigned	mod.py
would_send	(1)
hang_risk	no
scopes_n	1
```

No `scope mismatch`. 063 dump with `dist` forced to `loadscope`: one module
unit, `would_send (1)`, `hang_risk no`, rc=0. 257 loadgroup first-done:
`scopes_n 257`, `hang_risk yes`, `would_send ()`, rc=1, stderr has no
`exceeds cap`.

Caller module-shaped keys ignored: `workqueue: {"mod.py": {a: true, b: false}}`
+ `dist=loadgroup` → two units, first empty send, hang, rc=1.

---

## Attack: still first-dict empty-list / dist sticker? No.

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

That still names owned 063. It does **not** name this cut.

Host, first-dict sticker (`pending and not idxs` on `next(iter(workqueue.values()))`,
no dist, no second assign) vs CLI `hang_risk`:

| case | sticker | CLI hang_risk | match |
| --- | --- | --- | --- |
| owned 063 | True | yes | yes |
| live-first | False | yes | **no** |
| same tests loadgroup | True | yes | yes |
| same tests loadscope | True | no | **no** |
| done-first | True | yes | yes |

MATCH 3/5. The two misses are exactly mutate-3: assign-loop (second empty
send) and dist regroup (loadscope joins the same keys into one unit). Dist
is not a key sticker. Hang is not “first already-grouped dict is all True”.

Independent replica (does not import emptyunit): flatten inner nodeids,
`_split_scope` (loadgroup full nodeid / `@` after `]`; loadscope
`rsplit("::", 1)`), FIFO first, then one more if first pending ≤ 2.
`hang_risk` / `assigned` MATCH CLI on owned, live-first, loadgroup-same,
loadscope-same, forced-loadscope 063, 257 first-done (6/6). That replica
**is** the object (xdist `_split_scope` + `schedule` assign + `_reschedule`
one extra, applied to a dump). It is not DESTROYER_2’s first-dict one-liner.

`empty_send` still equals `completed_only_unit` on every reported unit of
every fixture after index-error (two names, one bit). Hang_risk is that bit
on the burst, not a thicker meaning of `empty_send`. Not faked.

---

## Other host holes (ceilings, not this KILL)

1. **Replacement vs initial burst.** xdist `schedule()` for a later node
   (replacement) calls `_reschedule` once on empty `assigned_work` → one
   unit. Live-first `hang_risk yes` models assign + one `_reschedule` on
   the dump (the `-n1` initial pair), not replacement-start. Owned 063 is
   first-assign `()` either way. Completions are still not simulated:
   pending=3 then completed-only stays `hang_risk no`. Two live then
   completed-only: `assigned` first two lives, `hang_risk no` (xdist
   `_reschedule` is one extra, not a while). Do not grow a scheduler to
   close this.

2. **`would_send` names the first send.** Live-first: `would_send (1)` while
   `hang_unit` is the second `()`. `assigned` / `hang_unit` already name
   the burst.

3. **FIFO follows dump/unit insertion, not collection order.** Collection
   `done` then `live` with unit rows live-first still assigns live first.
   A raw workqueue dump’s OrderedDict order is the right FIFO.

4. **Ingest leftovers.** JSONL two objects, trailing commas, `/* comments */`
   refused. Duplicate JSON `collection` last-wins. Nonempty `workqueue`
   shadows filled `assigned` (empty `workqueue {}` does not). Nodeid `-`
   refused. `none` is an identity. `dist none` / `loadfile` / `each` error
   (closed enum). UTF-8 BOM JSON accepted. `/dev/null` / empty stdin rc=1.
   Completed-only nodeid missing from collection is still a hang unit
   (no index-error). Collection 8192 legal; 8193 safety-cap refused
   (labeled, not pytest).

5. **TSV identity.** A JSON nodeid containing TAB prints as two TSV fields
   (`first_assigned	a.py::t	x`). TSV collection rows still split on TAB.

6. **Copied xdist grouping bugs.** loadscope `rsplit("::", 1)` on
   `m.py::test[a::b]` yields scope `m.py::test[a` (pytest-xdist #1335).
   loadgroup `@` inside `[]` stays the full nodeid (`rfind("@")` vs `]`).
   `@g` after `]` groups. Not a new join.

---

## Primitive

Reality-stripped operation: flatten a workqueue dump to `{nodeid: completed}`,
group by dist (`_split_scope`), then name whether any unit in the
replacement-start burst (FIFO first, plus one more if that unit’s pending
≤ 2) would be `send_runtest_some([])`. rc=1 on that hang.

Nearest ordinary workflow: read `print(workqueue)` and the list
comprehension in `_assign_work_unit`. Observable capability lost if
emptyunit vanishes: same tests change hang_risk under loadgroup vs
loadscope without the caller regrouping; the burst names
`first_assigned` vs `assigned` vs `hang_unit` vs `would_send ()`;
`print(workqueue)` OrderedDict ingest; index-error instead of hang for
missing incompletes.

That is why this is KEEP, not KILL: DESTROYER_2 required assign-loop and
dist-as-scheduler or a later destroyer should KILL as THIN_WRAPPER of
first-dict / sticker. Both landed, host-executed. The remaining list is
ceilings and a snapshot (no completion walk). Do not mutate further to
escape a KILL that does not apply. Do not merge onto `main`. Do not
import pytest-xdist. Do not merge with `requeue`.

Hardcoded ceiling:

- burst is first + at most one extra; not a completion-driven `_reschedule` loop
- `empty_send` coincides with `completed_only` after index-error
- dist is `loadgroup|loadscope` only
- collection safety cap 8192
- TSV does not quote TAB in nodeids
- not a LoadScopeScheduling implementation

---

KEEP
