# MUTATE pairaxis (no-op / already listed)

Date: 2026-09-02
Job: job-0327
Worker: mutate-pairaxis
Queue: READY_MUTATE (with_state, `queues=["READY_MUTATE"]`; unfiltered `claim()` would take READY_DESTROY)

Target: `lineages/candidate-pairaxis/pairaxis`
Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/pairaxis-pairaxis`
Branch: `specimen-hdd/pairaxis-pairaxis`
Commit: `2cff07700105c3ea8bd5bde6282780e1cf22aa1c`

CLI sha256 (before = after): `b6ea93737f885bd5b9b452511323db2cf88c75c1ffb1f87762ba953f1d398ba7` (2180 bytes)

Archive `pairaxis` and worktree `pairaxis/pairaxis.py` are byte-identical. No CLI patch. Not merged to `main`. Parent tree stays on `main`.

No tests directory. `./demo.sh` present.

## Leftover (DESTROYER_pairaxis.md)

KEEP as a paired-specimen lens. MUTATE later if it should refuse `only_axis multiple` without listing diffs (it already lists them).

Job input: `pairaxis refuse only_axis multiple without listing diffs`
Kill condition: `thin concat axes`

## Observation

The leftover is already listed diffs. `only_axis multiple` does not invent a single axis. It prints `n_diff` then every `diff KEY left=… right=…` row. It does not concatenate keys.

Owned demo pair (`fixtures/pair_a.rec` vs `pair_b.rec`):

```
fields 3
n_diff  2
only_axis  multiple
diff  requires_contains_extra_dep  left=true  right=false
diff  resolved_extra_deps  left=["B"]  right=[]
```

Unseen pair (`n_diff 1`) still names `only_axis recognized` and lists that one `diff`. Identical records: `only_axis none` / `n_diff 0` / rc=0. Missing file: `pairaxis: file not found` rc=2.

`lineages/TRANSFER_s072_pairaxis.md` already showed the same shape (`n_diff 4`, `only_axis multiple`, four `diff` lines). Swallowing those rows would hide the leaked objects the transfer named.

## Decision

**No-op.** Do not stop listing diffs. Do not refuse by deleting the `diff` rows. Do not concat axes into a fake `only_axis` (that is this job’s kill condition). Bytes unchanged.

A later destroyer should **KEEP** (paired-specimen lens: one axis when `n_diff==1`, every axis listed when `n_diff>1`) or **KILL** as a thin dict-diff of caller-supplied traces. That is already the primitive. This cut does not thicken it.

Does not run poetry / pytest / django. Owned records only.

## Demo

`./demo.sh` ×2 — `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.
