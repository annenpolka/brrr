# Hybrid: peerleft × silentadd

Date: 2026-09-02
Job: job-0300 (`hybrid-peer-silent`)
RUN_ID: specimen-hdd-20260902-1112

Verdict: **NON-JOIN / thin concat**. No binary.

Proposed join: name whether leftover-after-success is (a) a leftover
packages identity after remove, versus metadata-only mention, or (b) a
leftover file/dir collision after insert returned ok. One query, two
leftover reports.

That is two parent reports glued under the English phrase "leftover
after success". It is not a relation unavailable from concatenating
parent outputs (Constitution 13.5). Kill condition on the job was
"thin concat".

"Leftover after success" does not even mean the same mutation in both
parents. peerleft's `leftover_identity` is after **remove**: the name
was absent from `packages` in the never-installed lock and present in
`packages` after remove, while `grep` still hits the peer-metadata
mention in both. The CLI has no `operation_ok` field; rc=1 when
leftover_identity. silentadd's `silent` is after **add**: `add ok` and
a remaining file/dir collision because a directory-prefix walk from
scan start 0 prefix-breaks on an earlier sibling. rc=0 even when
`silent yes`. Opposite operations, opposite success models.

## Parents (host-executed)

`peerleft` on specimen-082 owned pair (`fixtures/082-never.rec` /
`082-after-remove.rec`, `--name no-deps`). Tests 3/3 OK. `./demo.sh`
twice, logs identical.

```
name	no-deps
packages_a	no
packages_b	yes
mentioned_a	yes
mentioned_b	yes
leftover_identity	yes
```

Never-install is `peer	no-deps` only. After remove is
`packages	no-deps` plus `peer	no-deps`. `grep no-deps` hits both
files. That is reason (a). Unseen `widget` is the same shape. Same
never vs never is `leftover_identity no` / rc=0.

`silentadd` on specimen-014 owned list (`aaa blobtree/ zzz`, name
`blobtree`, default `--scan 0`). Tests 14/14 OK. `./demo.sh` twice,
logs identical.

```
name	blobtree
index	aaa	blobtree/	zzz
insert_pos	1
scan_start	0
ordered	yes
add	ok
collision	present
remain	blobtree/	dir
hide	aaa
scan0	miss
scan_pos	hit
silent	yes
```

`--scan pos` is `add fail` / `silent no` / `hide none`. Only
`blobtree/` (insert_pos 0) is `scan0 hit` / `add fail`. Unseen `pkg`
behind `000` is `silent yes` / remain `pkg/__init__.py`. specimen-017
extra name `B` `B` is `collision absent` / `silent no`. That is
reason (b).

## Concat already names both reasons

```
python3 peerleft fixtures/082-never.rec fixtures/082-after-remove.rec --name no-deps
# leftover_identity yes / packages_a no / packages_b yes / mentioned_a yes

python3 silentadd blobtree aaa 'blobtree/' zzz
# add ok / collision present / remain blobtree/ dir / silent yes
```

A wrapper that prints `why leftover-identity` vs `why leftover-collision`
is `uniq(parent claims)`. The exclusive class reconstructs from those
two stdout blocks. Pairing a two-snapshot lock excerpt with a one-list
path index is caller-invented: no owned event is both.

## No shared object

| | peerleft | silentadd |
| --- | --- | --- |
| domain | bun.lock packages vs optionalPeers mention | ordered path index insert |
| input | two lock excerpts (`packages`/`peer` TSV) + `--name` | one path list + NAME + `--scan` |
| mutation | remove | add |
| leftover | packages slot occupied after remove | colliding `NAME/` child (or parent file) still in the list |
| success model | none (membership delta only) | `add ok` from scan-start 0 |
| nearest miss | grep hits the name in both locks | list print plus exit 0 looks like a successful add |
| time axis | never-installed vs after-remove | one list; scan 0 vs insert_pos |
| exit on leftover | rc=1 | rc=0 |

The analogical map (leftover identity after remove ≈ leftover collision
after add) fails on the owned rows. peerleft does not consult a scan
cursor. silentadd does not distinguish packages identity from metadata
mention. There is no lock-plus-path-index fixture.

Host-executed cross-apply:

- silentadd `--file fixtures/082-after-remove.rec no-deps` →
  `silent no` / `collision absent`. Lock TSV lines
  (`packages	no-deps`, `peer	no-deps`) are not a `no-deps/` dir
  prefix. The owned leftover packages identity is invisible to the
  collision walk.
- peerleft on `014-siblings.txt` / `014-only-dir.txt` `--name blobtree`
  → `expected key<TAB>value`. Path lists are not lock excerpts.
- Recoding the after-remove name as a path index
  `aaa no-deps/ zzz` does yield silentadd `silent yes`. That is a
  caller-invented git-style list, not specimen-082. The bun leftover
  is a packages slot, not a file/dir collision.

`TRANSFER_gitinc_silentadd.md` already refused the adjacent glue
"exit 0 hiding a leftover" (regex-unset leftover key vs
collision-insert). Same adjacency, still no shared object.

This is the same mashup shape as `hybrid-zerowhy` (XOR of independent
parent claims), `hybrid-emptyunit-waitoneshot`, and
`hybrid-unusedfp-lockident` ("one query, two reasons"). zerowhy was
already attacked this run as a calculator over concatenated stdout.
Do not mint another one.

## What was not done

Did not run `scripts/make_worktree.sh hybrid-leftover leftover`.
Did not invent bun or git. Did not merge onto main.

Keep the parents. Archive this note only.
