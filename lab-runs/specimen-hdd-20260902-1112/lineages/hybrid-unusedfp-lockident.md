# Hybrid: unusedfp × lockident

Date: 2026-09-02
Job: job-0265 (`hybrid-unused-lock`)
RUN_ID: specimen-hdd-20260902-1112

Verdict: **NON-JOIN / thin concat**. No binary.

Proposed join: name whether FRESH missed because (a) an unused snapshot
key changed, or (b) a named blob was omitted from the identity hash.
One query, two reasons.

That is two parent reports glued under the English word "FRESH missed".
It is not a relation unavailable from concatenating parent outputs
(Constitution 13.5). Kill condition on the job was "thin concat".

"FRESH missed" does not even mean the same cache outcome in both
parents. unusedfp's `invalidate_unused` is a miss: the composite
snapshot identity changed because an unread key entered the hash.
lockident's `omitted` is a hit: the observed identity stayed FRESH
because a provided blob was never hashed.

## Parents (host-executed)

`unusedfp` on specimen-076 owned pair (`fixtures/076-first.env` /
`076-second.env`, `--used path`). Tests 3/3 OK. `./demo.sh` twice,
logs identical.

```
used	path
unused	idea.io.use.nio2
changed_unused	idea.io.use.nio2
all_first	cd6312a323ca
all_second	e8e424f35bd2
used_first	a963701a18cc
used_second	a963701a18cc
all_same	no
used_same	yes
invalidate_unused	yes
```

Unread `idea.io.use.nio2` entered the JSON-map identity and changed;
used `path` did not. That is reason (a). Unseen
`ORG_GRADLE_PROJECT_value` is the same shape (`invalidate_unused yes`).
Owned analog `specimens/specimen-076/files/cc_unused_prop.py` prints
the same hashes. Identity is `sha256(json.dumps(props, sort_keys=True))[:12]`
of **all** keys. Unused keys are in the hash by construction.

`lockident` on specimen-016 owned lock-omitted (`cache_lock.py`: first
BUILT / after_lock_bump FRESH, key `673767793f4a`, `same_key True`,
lock `1.0.0` → `1.0.219`):

```
blob         digest12     membership
------------ ------------ ----------
src          673767793f4a in
lock_new     324afc7759fc omitted
identity  673767793f4a
in_identity  src
omitted  lock_new
live_lock_in_identity  false
```

Live lock bytes were provided and changed; they did not hash into the
freshness key. That is reason (b). Identity is `sha256(blob_bytes)[:12]`
of **one** blob. DESTROYER cases hold: no `--blob` rc=2; unmatched
identity → `in_identity none`; empty `lock_new=` still omitted.
TRANSFER_075 (specimen-078 `gocache_buildid.py`): tests in, buildid
omitted, `live_lock_in_identity true`. Extra-output specimen-011 key
`9280cc7e16e9` is a JSON-map digest, so `--blob src=hello` is also
omitted (encoding mismatch DESTROYER already named).

unusedfp's own REALITY.md already lists lockident as nearest existing
operation, with delta `invalidate_unused yes; changed_unused
idea.io.use.nio2`. The unused-key harvest exists because lockident
does not name it.

## Concat already names both reasons

```
python3 unusedfp fixtures/076-first.env fixtures/076-second.env --used path
# invalidate_unused yes / changed_unused idea.io.use.nio2 / used_same yes

python3 lockident.py --identity 673767793f4a \
  --blob 'src=mod.rs\nfn f() {}\n' \
  --blob 'lock_new=serde = "1.0.219"\n' --live lock_new
# in_identity src / omitted lock_new / live_lock_in_identity false
```

A wrapper that prints `why unused-key` vs `why omitted-blob` is
`uniq(parent claims)`. The exclusive class reconstructs from those two
stdout blocks. Pairing a two-snapshot property map with a single
observed digest plus named blobs is caller-invented: no owned event is
both.

## No shared object

| | unusedfp | lockident |
| --- | --- | --- |
| domain | Gradle configuration-cache unused system property | cargo/go freshness key vs lock/buildid bytes |
| input | two NAME=VALUE maps + `--used` | `--identity` hex + `--blob name=bytes` |
| identity | composite JSON of all keys | per-blob sha256 prefix |
| membership | unused keys **enter** the all-hash | omitted blobs **do not** enter |
| cache outcome | miss (`invalidate_unused`) | hit (FRESH, `same_key True`) |
| time axis | first vs second snapshot | one observed key vs provided blobs |

The analogical map (over-included unread key ≈ under-included named
blob) fails on the owned rows. They are opposite membership directions
and opposite hit/miss.

Host-executed cross-apply:

- lockident on unusedfp's `all_first=cd6312a323ca` with blobs
  `path=/app` and `idea.io.use.nio2=false` → `in_identity none`. Same
  for `used_first=a963701a18cc`. Per-blob digest never equals the
  composite map digest.
- unusedfp on lockident's src+lock maps (`--used src`) →
  `invalidate_unused yes` / `changed_unused lock`. That is a false
  prediction of invalidation: the owned cache stayed FRESH because
  lock was omitted from the key.

Identity functions on the 016 bytes (host-computed): lockident src
`673767793f4a`; unusedfp all-map `aba51aa25c48`; unusedfp used-only
JSON `1e9c6550350e`. No digest is shared.

This is the same mashup shape as `hybrid-zerowhy` (XOR of independent
parent claims) and `hybrid-emptyunit-waitoneshot` ("one query, two
reasons"). zerowhy was already attacked this run as a calculator over
concatenated stdout. Do not mint another one.

## What was not done

Did not run `scripts/make_worktree.sh hybrid-unusedlock unusedlock`.
Did not invent Gradle or cargo. Did not merge onto main.

Keep the parents. Archive this note only.
