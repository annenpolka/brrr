# DESTROYER emptyunit 4

Date: 2026-09-02 19:45 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0594 worker=destroyer-emptyunit-4

Target: `lineages/candidate-emptyunit/emptyunit` AFTER mutate-3
(`MUTATE.md` third cut: dist regroups; ingest `print(workqueue)`; 257 units
legal. Assign-loop kept from cut (1).)

sha256 `9e224d35637d45ea2f324e439f784c25c003d47c5b12cce6550e221078758627`
(24307 bytes, 650 lines, matches `MUTATE.md`). Archive HEAD.txt `4168ca2`
(`MUTATE emptyunit: dist regroups; ingest print(workqueue); 257 units`).
Worktree copy at
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-emptyunit-emptyunit/candidate-emptyunit/emptyunit`
is **byte-identical** (`cmp` rc=0). Worktree git HEAD `028817d` only records
mutation metadata on top of `4168ca2`; CLI bytes unchanged. Parent `main`
`432f954`; `git ls-tree` has no `emptyunit`. Host Python 3.14.5. `xdist` /
`pytest` specs are `None`. CLI ast imports are stdlib only
(`argparse`, `ast`, `json`, `sys`, `collections`, `pathlib`). `pytest` /
`xdist` tokens in the CLI are comments (`not a pytest collection ceiling`,
`xdist _reschedule`), not imports. unittest
`python3 tests/test_emptyunit.py -v` **39/39** archive twice (1.442s /
1.399s, rc=0) and worktree twice (1.411s / 1.394s, rc=0). No pytest-xdist
import, no pytest-xdist run, no merge onto `main`. Worktree `./demo.sh` ×2
byte-identical to each other and to archived `demo-1.log` / `demo-2.log`
(`cmp` rc=0, 7547 bytes). Archive-cwd `./demo.sh` ×2 identical to each
other; vs archived logs the only delta is the hang-log source path
(archive vs worktree). Worktree was not edited.

Prior: `destroyers/DESTROYER_emptyunit.md` KEEP (FIFO hang_risk).
`destroyers/DESTROYER_emptyunit_2.md` MUTATE. `destroyers/DESTROYER_emptyunit_3.md`
KEEP (assign-loop + dist regroup). First KEEP is **not** protection.
`destroyers/DESTROYER_reimpl-emptyunit-2.md` Honor-KILL as the **same**
leftover formula (copy, not a second style). That KILL of the copy does
not kill this parent.

Honor KILL if:

1. first-dict empty-list / dist sticker
2. THIN_WRAPPER of two greps
3. hang_risk is any empty send list without leftover empty-unit identity

Those three were host-executed. They do **not** fire. Leftover empty-unit
identity (hang if assigned send is `()`) is still the object. AST-static
work cannot cut a leftover-identity lie without becoming pytest-xdist.
Decision: **KEEP**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/emptyunit
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-emptyunit-emptyunit/candidate-emptyunit/emptyunit
SCR=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_emptyunit4_scratch
```

Independent replica in `destroyers/_emptyunit4_scratch/attack.py` does
**not** import emptyunit. No pytest. No pytest-xdist. Do not merge with
`requeue` / `reimpl-emptyunit-2`. Do not grow a LoadScopeScheduling. Do
not send THIN_WRAPPER / pytest-xdist theater back to R1.

---

## Honor KILL (did not fire)

| condition | host result | kill? |
| --- | --- | --- |
| first-dict empty-list / dist sticker (`pending and not idxs` on `next(iter(workqueue.values()))`, no dist, no second assign) | MATCH **5/8**. Misses: live-first (sticker False, CLI yes), same tests loadscope (sticker True, CLI no), owned dump forced loadscope (sticker True, CLI no). | **no** |
| THIN_WRAPPER of two greps (`any incomplete` AND `first bag all True`) | MATCH **5/8**. Same three misses as the sticker. | **no** |
| hang_risk is any empty send list **without** leftover empty-unit identity | MATCH **6/8**. Misses: pending=3 then completed-only (empty_send yes on `b.py`, CLI hang_risk no); two-live-then-done (empty_send yes on third unit, CLI hang_risk no, assigned first two lives). | **no** |

Leftover replica (flatten inner nodeids, `_split_scope`, FIFO first, plus
one more if that unit’s pending is 1 or 2, hang if any **assigned** send
is `()`) MATCH CLI hang_risk **8/8** on that battery and MATCH harvest
fields (`rc`, `hang_risk`, `would_send`, `first_assigned`, `assigned`,
`reschedule`, `hang_unit`, `scopes_n`, `pending`) **9/9** including 257
first-done. CLI AST (no import): `empty_send = len(indexes) == 0`;
`hang = any(unit['empty_send'] for unit in assigned)` after
`replacement_burst`. That is leftover empty-unit identity, not “any
empty list in the dump.”

---

## What mutate-3 KEEP still names (host-executed this pass)

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

Live-first (`unseen-live-first.rec`, rc=1) — assign-loop, not first-dict:

```text
collection	done.py::t	live.py::u
first_assigned	live.py::u
would_send	(1)
assigned	live.py::u	done.py::t
reschedule	yes
hang_unit	done.py::t
hang_risk	yes
```

JSON same shape with collection live-then-done: `would_send (0)`, same
`assigned` / `hang_unit` / `hang_risk yes`. Send indexes follow
collection; FIFO follows dump/unit insertion.

Pending=3 then completed-only: `hang_risk no`, `reschedule no`,
`hang_unit -`, `empty_send yes` on the unassigned `b.py`, rc=0.
OrderedDict `063-hang.wq`: hang, rc=1. Handwritten both-done rec:
`pending 0`, `hang_risk no`, rc=0, no `scope mismatch`. Two-live-then-done:
`assigned` first two lives, `hang_risk no` (watermark is one extra, not
a while).

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

## Attack: still first-dict / two greps / any-empty-send? No.

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

Host, four predicates vs CLI `hang_risk`:

| case | sticker | two_greps | any_empty | leftover assigned `()` | CLI hang_risk |
| --- | --- | --- | --- | --- | --- |
| owned 063 | True | True | True | True | yes |
| live-first | False | False | True | True | yes |
| same tests loadgroup | True | True | True | True | yes |
| same tests loadscope | True | True | False | False | no |
| done-first | True | True | True | True | yes |
| owned forced loadscope | True | True | False | False | no |
| pending3 loadscope | False | False | True | False | no |
| two-live-then-done | False | False | True | False | no |

sticker 5/8, two greps 5/8, any-empty 6/8, leftover **8/8**. The sticker /
two-grep misses are mutate-3: assign-loop (second empty send) and dist
regroup (loadscope joins the same keys into one unit). The any-empty
misses are leftover identity: an empty send that is **not** in the
replacement burst is not hang_risk. Dist is not a key sticker. Hang is
not “first already-grouped dict is all True.” Hang is not “any unit’s
send list is `()`.”

`empty_send` still equals `completed_only_unit` on every reported unit of
every fixture after index-error (two names, one bit). Hang_risk is that
bit on the burst, not a thicker meaning of `empty_send`. Not faked.

---

## Leftover-identity lie hunt (AST-static; no pytest-xdist)

MUTATE only if leftover-identity lie AST-static work can cut without
becoming pytest-xdist. Host:

1. **CLI AST hang formula is leftover identity.**
   `empty_send = len(indexes) == 0` is a different assign from
   `completed_only = bool(items) and (not incomplete)`.
   `hang = any(unit['empty_send'] for unit in assigned)` after
   `replacement_burst` (FIFO first; skip second if first `empty_send`;
   else one more if pending ≤ 2). That is hang-if-assigned-send-`()`,
   not hang-if-any-empty-list.

2. **AST ingest vs leftover replica.** Python `True` Name, JSON
   `true`, int `1`/`0` completed flags, caller module-shaped keys,
   loadscope `::` in params (copied xdist #1335), loadgroup `@` inside
   `[]`: leftover replica MATCH CLI hang. BinOp `1-1` as a completed
   flag is refused (`not a JSON/Python workqueue dump`), not silently
   folded. That is ingest honesty, not a leftover-identity lie.

3. **FIFO follows dump/unit insertion, not collection order.**
   Collection `done` then `live` with unit rows live-first still
   assigns live first (`hang_risk yes` via the reschedule second `()`).
   A raw workqueue dump’s OrderedDict order is the right FIFO. Reordering
   by collection first-seen would be a different object, not a cut of a
   lie.

4. **Coincidence `empty_send == completed_only` after index-error** is
   still two names, one bit. Splitting them would require hanging on
   missing incompletes (today `index-error`) or growing a send list that
   is empty while incompletes exist. That is not leftover identity; it
   is becoming the xdist `.index` exception path as hang. Do not cut.

No leftover-identity lie is sitting in the dump AST waiting to be
folded. Remaining holes are ceilings. Growing a completion-driven
`_reschedule` while-loop, `--dist=load` / `each` / `loadfile`, or a
LoadScopeScheduling is pytest-xdist theater. Do not send that back to
R1.

---

## Other host holes (ceilings, not this KILL, not a required MUTATE)

1. **Replacement vs initial burst.** Burst is first + at most one extra.
   Completions are not simulated. Two live then completed-only:
   `assigned` first two lives, `hang_risk no`. Pending=3 then
   completed-only stays `hang_risk no`. Same ceiling DESTROYER_3 listed.
   Do not grow a scheduler to close this.

2. **`would_send` names the first send.** Live-first rec: `would_send (1)`
   while `hang_unit` is the second `()`. `assigned` / `hang_unit` already
   name the burst.

3. **Ingest leftovers.** JSONL two objects, trailing commas, `/* comments */`
   refused. Duplicate JSON `collection` last-wins. Nonempty `workqueue`
   shadows filled `assigned` (empty `workqueue {}` does not). Nodeid `-`
   refused. `none` is an identity. `dist none` / `loadfile` / `each` error
   (closed enum). UTF-8 BOM JSON accepted. `/dev/null` / empty stdin rc=1.
   Completed-only nodeid missing from collection is still a hang unit
   (no index-error). Collection 8192 legal; 8193 safety-cap refused
   (labeled, not pytest).

4. **TSV identity.** A JSON nodeid containing TAB prints as two TSV
   fields (`first_assigned	a.py::t	x`). TSV collection rows still
   split on TAB.

5. **Copied xdist grouping bugs.** loadscope `rsplit("::", 1)` on
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
comprehension in `_assign_work_unit`, plus one `_reschedule`. Observable
capability lost if emptyunit vanishes: same tests change hang_risk under
loadgroup vs loadscope without the caller regrouping; the burst names
`first_assigned` vs `assigned` vs `hang_unit` vs `would_send ()`;
`print(workqueue)` OrderedDict ingest; index-error instead of hang for
missing incompletes.

That is why this is KEEP, not KILL: Honor-KILL (1)(2)(3) do not fire.
The leftover empty-unit identity (hang if assigned send is `()`) is still
real. First KEEP is not protection; this fourth pass re-hit the sticker
and the any-empty-send and they still miss. `reimpl-emptyunit-2` was
Honor-KILLed as a copy of **this** formula; the parent KEEP remains.

That is why this is KEEP, not MUTATE: leftover-identity lie AST-static
work cannot cut without becoming pytest-xdist. Do not mutate further to
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
