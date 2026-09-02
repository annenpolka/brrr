# MUTATE extraedge (applied 2026-09-02 14:00 JST)

From DESTROYER_extraedge.md. Parent HEAD `9f5f581`. Worktree
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-extraedge-extraedge`
on `specimen-hdd/candidate-extraedge-extraedge`. Commit `9ed3189`.
CLI sha256 `cb58d2e26833205b49486d65ea4de8fcb6826486473e023abaa6c0817ae49881`
(11139 bytes). Not merged to `main`. Poetry is not executed.

Keep the object: for two records of one package version, a declared extra
that did not attach its extra-edge is a miss, and the extra-edge that
appears only on the second record is named.

Do not keep `missed = declared if not resolved else []`.

## Mapping (1)

`missed_*` is declared extras whose mapped extra-edge targets are all
absent from that record’s `resolved` list.

The extras table is a record field:

```
extra	postgresql	psycopg2
```

`postgresql` vs `psycopg2` is sayable because the map says so, not
because `postgresql ∈ {psycopg2}`. README set-difference of extra names
against resolved package names is forbidden: a successful add-lock
(`declared postgresql`, `resolved psycopg2`) is not a miss.

No extras table for a declared extra is `unmapped` (rc=1), not a guessed
join. The map is owned-record data, not a poetry extras solver.

Empty resolved is the all-miss special case of that mapping, not the
definition.

## Partial extras (2)

Two declared extras and one extra-edge names the extra that still has
no target (`missed_a mysql` when only `psycopg2` attached).

## Identity gate (3)

`same_package no` is `identity mismatch`, both package/version pairs
printed, harvest columns `.`, rc=1. Extra columns on `package` /
duplicate identity or `resolved` lines are errors.

## `none` is not a list value (4)

Empty list is `.`. Extra named `none` / `-` survives. `declared<TAB>`
is declared=∅. One lexer: tab-separated names.

## Exit (5)

rc=1 on a miss, mismatch, unmapped extra, or parse error. rc=0 only
for the same package version with no missed declared extra. Forgotten
`resolved` is an error. Identity/extra dumps are capped.

## Tests (6)

Add-lock as FIRST; honest 021 `resolved typing-extensions`; two extras
one attach; different package does not fill `attached_b`; extra named
`none`; `declared	my extra` space vs tab; `-` stdin; swapped 021;
`PostgreSQL` vs `postgresql`; duplicate `resolved none` then `resolved widget`.

`python3 tests/test_extraedge.py -v` — 21 OK.

`./demo.sh` ×2 identical (`demo-1.log` cmp `demo-2.log`). Wrapper exit 0.

```
== extraedge specimen-021 owned pair ==
missed_a	postgresql
attached_b	psycopg2
exit: 1

== extraedge add-lock as FIRST (mapped extra-edge present; not a miss) ==
missed_a	.
attached_b	.
exit: 0
```
