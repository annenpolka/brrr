#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets 160+.

Packed (unique vs 001-159; 075 not overwritten; not bazel#29298):
1) crystal-lang/crystal#16810 / PR 16958:
   leftover interpreter multidispatch chain after a new concrete type
   appears, because MultidispatchKey hashed (obj_type, call_signature)
   and omitted target_def object IDs.
2) vercel/next.js#96022:
   leftover `'use cache'` after a server-component edit for cookieless
   requests, because getHmrRefreshHash on request stores read the HMR
   hash cookie and omitted the server-authored hash.
3) direnv/direnv#1532:
   leftover NIX_ATTRS_JSON_FILE / NIX_ATTRS_SH_FILE after use_nix,
   because values_to_restore omitted those names from the unset list.
4) JetBrains/kotlin#6654:
   leftover Kotlin/Native incremental cache after an external dependency
   rolled back to an already-cached version, because CacheMetadata stored
   compilerFingerprint only and omitted dependenciesFingerprint.

SKIP claimed jobs without a merged leftover-HIT pair this tick.
Never overwrite 075. Do not pack leftover-flag TSV class.
"""
from __future__ import annotations

import os
import subprocess

from compile_seed import write_seed
from emit_specimen import emit
from paths import HDD_ROOT, RUN_DIR, SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 160
WORKER = "scout-coord-2212"
SKIP_JOBS = {
    "job-0682": (
        "skip php leftover opcache vs replaced file: no merged leftover-HIT "
        "omitted-hash pair this tick (search hits were JIT/PFA, not same-mtime "
        "replace). not inventing refs; not 110"
    ),
    "job-0683": (
        "skip node leftover compile cache vs source: node#54291 is storage "
        "layout refactor, not omitted-source-hash leftover-HIT. not inventing "
        "refs; not 082/090"
    ),
    "job-0684": (
        "skip crystal leftover compile vs moved module: no merged leftover-HIT "
        "after-move pair this tick. packed crystal#16958 omitted-target_defs "
        "instead (not moved-module). not 054/154"
    ),
    "job-0695": (
        "skip direnv leftover empty vs unset JOIN: no merged empty-vs-unset "
        "JOIN pair this tick (not 010/149/150/158). packed direnv#1532 leftover "
        "NIX_ATTRS omitted-unset instead"
    ),
    "job-0699": (
        "skip go leftover object vs moved file: no merged leftover-HIT omitted-"
        "path pair this tick (hits were open/non-reproducible). not inventing "
        "refs; not 075/103"
    ),
    "job-0700": (
        "skip rollup leftover cache vs moved module: no merged leftover-HIT "
        "pair this tick. not inventing refs; not 090"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: dune leftover source digest vs omitted ctime not 154",
        "unique dune leftover digest if pinned",
    ),
    (
        "public OSS: biome leftover file map vs close eviction not 157",
        "unique biome leftover if pinned",
    ),
    (
        "public OSS: kotlin leftover incremental vs external dep hash not 104/163",
        "unique kotlin leftover if not 163",
    ),
    (
        "public OSS: zig leftover cache vs include path identity not 075",
        "unique zig leftover if pinned",
    ),
    (
        "public OSS: oxc leftover parse cache vs source identity not 090",
        "unique oxc leftover if pinned",
    ),
    (
        "public OSS: sccache leftover CPATH identity if #2798 merges",
        "unique sccache leftover if pinned merged",
    ),
    (
        "public OSS: php leftover opcache vs same-mtime replace not 110",
        "unique php opcache leftover if pinned",
    ),
    (
        "public OSS: node leftover compile cache vs strip-types identity not 082/090",
        "unique node compile-cache leftover if pinned",
    ),
]


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 200):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_crystal(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: crystal-lang/crystal
failing_ref: c9e867a6703979d8e09abd2a3c1d9a7d55ae945d
fixed_ref: ac82b6ba7dcdc83f72199e8827f68417d61b88c4
source_issue: https://github.com/crystal-lang/crystal/issues/16810
source_pr: https://github.com/crystal-lang/crystal/pull/16958
mechanism_tags:
  - leftover-multidispatch-cache
  - omitted-target-def-ids
  - interpreter-cache-key
ecosystem: crystal
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Crystal's interpreter can keep the identity of a **previous multidispatch chain** after intervening code instantiates a new concrete type that should have been part of the dispatch, because the cache key hashed `(obj_type, call_signature)` and omitted the resolved `target_def` object IDs.

On failing_ref `c9e867a6703979d8e09abd2a3c1d9a7d55ae945d`:

```
record MultidispatchKey, obj_type : Type, call_signature : CallSignature

cache_key = Context::MultidispatchKey.new(obj_type, signature)
cached_def = context.multidispatchs[cache_key]?
return cached_def if cached_def
```

Two call sites that look identical by that key can resolve to different `target_defs` once a new type lands inside the union. The second site reuses the first's leftover chain; the new type matches none of the branches and execution falls through into `raise "unreachable"`.

Public report (crystal-lang/crystal#16810). `v1 = G(M2 | C).new.as(V); v1.my_check` then `v2 = G(C).new.as(V); v2.my_check`. Expected: second call builds a 5-def chain. Actual: leftover 4-def chain, "Reached the unreachable".

In-tree after the repair (not on failing_ref): `target_def_ids` (sorted object IDs) is part of `MultidispatchKey`.

Case A — second call, no intervening new type:
  cache identity is current
  not leftover-after-new-type

Case B — intervening instantiation, leftover chain:
  leftover: previous multidispatch of the first site
  same (obj_type, signature) vs omitted target_defs
  new concrete type present

Case C — interpreter restart / empty multidispatchs:
  fresh chain
  not leftover previous defs

Case D — key includes target_def_ids (post-repair shape, not on failing_ref):
  new chain after the resolved set changes
  not leftover previous chain

The developer wants to know which identity case B actually used for the second `my_check`: leftover previous-chain (target_defs omitted from the key), current resolved set, or omitted (no cache).
""",
        observed="""# OBSERVED

Public crystal-lang/crystal#16810. PR 16958 squash `ac82b6ba7dcdc83f72199e8827f68417d61b88c4` (parent `c9e867a6703979d8e09abd2a3c1d9a7d55ae945d`). Local crystal was not performed on this lab host.

PR title: Fix interpreter multidispatch cache collision. Cache key was `(obj_type, call_signature)`; second site reused the first site's dispatch chain after a new type appeared.

On failing_ref, `Context::MultidispatchKey` has two fields. `multidispatch.cr` returns `cached_def` on that key. Newly resolved types fall through the leftover chain.

Not this packet: specimen-054 cpython. specimen-154 mix same-length rewrite omitted digest. specimen-159 gleam leftover cache after move+restore.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref c9e867a6703979d8e09abd2a3c1d9a7d55ae945d
# src/compiler/crystal/interpreter/context.cr MultidispatchKey
# src/compiler/crystal/interpreter/multidispatch.cr cache lookup

# public shape:
# leftover multidispatch chain after new concrete type
# key is (obj_type, call_signature); target_def ids omitted
# interpreter restart / miss writes a new chain
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""crystal-lang/crystal
  src/compiler/crystal/interpreter/context.cr
  src/compiler/crystal/interpreter/multidispatch.cr
  spec/compiler/interpreter/multidispatch_spec.cr
""",
        source="""repository: crystal-lang/crystal
issue: https://github.com/crystal-lang/crystal/issues/16810
pr: https://github.com/crystal-lang/crystal/pull/16958
failing_ref (parent of squash on master): c9e867a6703979d8e09abd2a3c1d9a7d55ae945d
fixed_ref (target_def_ids added to MultidispatchKey): ac82b6ba7dcdc83f72199e8827f68417d61b88c4
merged_at: 2026-05-20T15:48:57Z
pr_author: stakach
merged_by: straight-shoota
changed_files: spec/compiler/interpreter/multidispatch_spec.cr, src/compiler/crystal/interpreter/context.cr, src/compiler/crystal/interpreter/multidispatch.cr
pr_title: Fix interpreter multidispatch cache collision
scout_note: not 054/154/159. leftover multidispatch chain after new type because target_def ids omitted. unique vs 001-159.
""",
        answer_key="""KNOWN FIX (sealed): crystal-lang/crystal PR 16958 squash ac82b6ba7dcdc83f72199e8827f68417d61b88c4.

failing_ref is parent c9e867a6703979d8e09abd2a3c1d9a7d55ae945d.

MultidispatchKey was (obj_type, call_signature). Second call site reused leftover dispatch chain after a new concrete type appeared.

PR repair: add sorted target_def object IDs to the key.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (no-new-type current cache vs leftover chain after new type vs restart vs key-with-ids)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — same (obj_type, signature) JOINs two different resolved sets; two greps cannot replace
ecosystem: crystal / interpreter
mechanism_family: leftover-multidispatch-cache, omitted-target-def-ids, interpreter-cache-key

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "context_failing.cr": """# Reduced excerpt of Context::MultidispatchKey on failing_ref
# src/compiler/crystal/interpreter/context.cr
# c9e867a6703979d8e09abd2a3c1d9a7d55ae945d
# key is (obj_type, call_signature); target_def ids omitted.

record MultidispatchKey, obj_type : Type, call_signature : CallSignature
""",
            "multidispatch_failing.cr": """# Reduced excerpt of multidispatch cache lookup on failing_ref
# src/compiler/crystal/interpreter/multidispatch.cr
# leftover HIT when a later site shares obj_type+signature.

cache_key = Context::MultidispatchKey.new(obj_type, signature)
cached_def = context.multidispatchs[cache_key]?
return cached_def if cached_def
""",
            "leftover_identity_split.txt": """Registry / fixture:
  Crystal interpreter MultidispatchKey
  leftover dispatch chain after a new concrete type

Case A (no intervening new type):
  current cache identity
  not leftover-after-new-type

Case B (intervening instantiation, leftover chain):
  leftover: previous multidispatch of the first site
  same (obj_type, signature) vs omitted target_defs

Case C (interpreter restart / empty cache):
  fresh chain
  not leftover previous defs

Case D (key includes target_def_ids):
  new chain after the resolved set changes
  not leftover previous chain

Not this packet:
  cpython (specimen-054)
  mix same-length rewrite omitted digest (specimen-154)
  gleam leftover cache after move+restore (specimen-159)
""",
        },
    )


def packet_next(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: vercel/next.js
failing_ref: 70f8b678877ba69f266e1522fcfacb95cfd3c76e
fixed_ref: 286862e35bbc4fa7c023077cf794d5852063463a
source_issue: https://github.com/vercel/next.js/pull/96022
source_pr: https://github.com/vercel/next.js/pull/96022
mechanism_tags:
  - leftover-use-cache
  - omitted-server-hmr-hash
  - cookie-delivered-cache-key
ecosystem: nextjs
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 8200
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Next.js `'use cache'` in development can keep the identity of a **previous cached page / route handler** after a server-component file is edited, for any request that does not carry the HMR refresh-hash cookie, because `getHmrRefreshHash` on a request store reads `__next_hmr_refresh_hash__` from cookies and the server-authored hash is omitted from that path.

On failing_ref `70f8b678877ba69f266e1522fcfacb95cfd3c76e`:

```
export function getHmrRefreshHash(workUnitStore: WorkUnitStore): string | undefined {
  if (process.env.__NEXT_DEV_SERVER) {
    switch (workUnitStore.type) {
      case 'cache':
      case 'private-cache':
      case 'prerender':
      case 'prerender-runtime':
        return workUnitStore.hmrRefreshHash
      case 'request':
        return workUnitStore.cookies.get(NEXT_HMR_REFRESH_HASH_COOKIE)?.value
```

```
const cacheKeyParts: CacheKeyParts = hmrRefreshHash
  ? [buildId, id, args, hmrRefreshHash]
  : [buildId, id, args]
```

The HMR client writes the hash into a session cookie after a server-component reload. `curl`, a plain `fetch`, a fresh browser profile, or a second device never send that cookie. `hmrRefreshHash` is then undefined, so the key is `[buildId, id, args]` and leftover previous cache HITs. Route-handler edits on Turbopack also fail to advance the cookie.

Public report (vercel/next.js#96022). Edit a `'use cache'` page, then fetch without the cookie. Expected: miss / new content. Actual: leftover previous cached content.

In-tree after the repair (not on failing_ref): the hash is server-authored and attached via request meta; the cookie is gone.

Case A — same request after edit, HMR cookie present:
  cache key includes the new hash
  not leftover-after-edit

Case B — cookieless request after edit, leftover cache:
  leftover: previous `'use cache'` entry
  server hash omitted on the request path
  cookie absent

Case C — cold start / empty `'use cache'` store:
  fresh compute
  not leftover previous page

Case D — server-attached hash (post-repair shape, not on failing_ref):
  every client misses after an edit
  not leftover previous page

The developer wants to know which identity case B actually used after the edit without the cookie: leftover previous-page (server hash omitted), current source, or omitted (no cache).
""",
        observed="""# OBSERVED

Public vercel/next.js#96022 (merged 2026-07-22). Squash `286862e35bbc4fa7c023077cf794d5852063463a` (parent `70f8b678877ba69f266e1522fcfacb95cfd3c76e`). Local next was not performed on this lab host.

PR title: Fix stale dev `'use cache'` for cookieless requests and route handlers. Dev invalidation used a cookie-delivered HMR hash. Cookieless clients kept leftover cache after an edit.

On failing_ref, request-store `getHmrRefreshHash` reads `NEXT_HMR_REFRESH_HASH_COOKIE`. Missing cookie → `hmrRefreshHash` undefined → `cacheKeyParts` drops the hash → leftover HIT.

Not this packet: specimen-090 webpack persistent cache. specimen-156 bun define-table omitted from runtime-transpile hash. specimen-157 jest haste mock-name delete.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 70f8b678877ba69f266e1522fcfacb95cfd3c76e
# packages/next/src/server/app-render/work-unit-async-storage.external.ts getHmrRefreshHash
# packages/next/src/server/use-cache/use-cache-wrapper.ts cacheKeyParts

# public shape:
# leftover 'use cache' after edit for cookieless requests
# request path reads HMR hash cookie; server hash omitted
# cookie-bearing HMR client / miss writes new content
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""vercel/next.js
  packages/next/src/server/app-render/work-unit-async-storage.external.ts
  packages/next/src/server/use-cache/use-cache-wrapper.ts
  packages/next/src/client/dev/hot-reloader/app/hot-reloader-app.tsx
  packages/next/src/server/base-server.ts
""",
        source="""repository: vercel/next.js
issue: https://github.com/vercel/next.js/pull/96022
pr: https://github.com/vercel/next.js/pull/96022
failing_ref (parent of squash on canary): 70f8b678877ba69f266e1522fcfacb95cfd3c76e
fixed_ref (server-authored HMR hash, cookie removed): 286862e35bbc4fa7c023077cf794d5852063463a
merged_at: 2026-07-22T13:50:26Z
pr_author: unstubbable
merged_by: unstubbable
changed_files: packages/next/src/server/app-render/work-unit-async-storage.external.ts, packages/next/src/server/use-cache/use-cache-wrapper.ts, packages/next/src/client/dev/hot-reloader/app/hot-reloader-app.tsx, packages/next/src/server/base-server.ts, packages/next/src/server/request-meta.ts, test/e2e/app-dir/use-cache-dev/use-cache-dev.test.ts
pr_title: Fix stale dev `'use cache'` for cookieless requests and route handlers
scout_note: not 090/156/157. leftover 'use cache' after edit because request path omitted server HMR hash. unique vs 001-159.
""",
        answer_key="""KNOWN FIX (sealed): vercel/next.js PR 96022 squash 286862e35bbc4fa7c023077cf794d5852063463a.

failing_ref is parent 70f8b678877ba69f266e1522fcfacb95cfd3c76e.

getHmrRefreshHash on request stores read the HMR cookie. Cookieless requests omitted the server hash from cacheKeyParts and HIT leftover 'use cache' entries after an edit.

PR repair: attach a server-authored hash via request meta; stop writing the cookie.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (cookie-present current vs cookieless leftover after edit vs cold vs server-attached hash)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — cookie-absent JOIN of pre-edit cache; two greps cannot replace
ecosystem: next.js / 'use cache'
mechanism_family: leftover-use-cache, omitted-server-hmr-hash, cookie-delivered-cache-key

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "getHmrRefreshHash_failing.ts": """// Reduced excerpt of getHmrRefreshHash on failing_ref
// packages/next/src/server/app-render/work-unit-async-storage.external.ts
// 70f8b678877ba69f266e1522fcfacb95cfd3c76e
// request path reads the HMR cookie; server hash omitted.

export function getHmrRefreshHash(
  workUnitStore: WorkUnitStore
): string | undefined {
  if (process.env.__NEXT_DEV_SERVER) {
    switch (workUnitStore.type) {
      case 'cache':
      case 'private-cache':
      case 'prerender':
      case 'prerender-runtime':
        return workUnitStore.hmrRefreshHash
      case 'request':
        return workUnitStore.cookies.get(NEXT_HMR_REFRESH_HASH_COOKIE)?.value
    }
  }
  return undefined
}
""",
            "cacheKeyParts_failing.ts": """// Reduced excerpt of cacheKeyParts on failing_ref
// packages/next/src/server/use-cache/use-cache-wrapper.ts
// leftover HIT when hmrRefreshHash is undefined (no cookie).

const cacheKeyParts: CacheKeyParts = hmrRefreshHash
  ? [buildId, id, args, hmrRefreshHash]
  : [buildId, id, args]
""",
            "leftover_identity_split.txt": """Registry / fixture:
  Next.js 'use cache' / getHmrRefreshHash
  leftover previous page after edit for cookieless requests

Case A (HMR cookie present after edit):
  current cache identity (hash in key)
  not leftover-after-edit

Case B (cookieless after edit, leftover cache):
  leftover: previous 'use cache' entry
  server hash omitted on the request path

Case C (cold start / empty store):
  fresh compute
  not leftover previous page

Case D (server-attached hash):
  every client misses after an edit
  not leftover previous page

Not this packet:
  webpack persistent cache (specimen-090)
  bun define-table omitted from runtime-transpile hash (specimen-156)
  jest haste mock-name delete (specimen-157)
""",
        },
    )


def packet_direnv(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: direnv/direnv
failing_ref: e261bba8c9f9f32010d046a839ae5de5ae7dda0c
fixed_ref: 3580653d9d3a51f093ac96c85505d71b872d7cd0
source_issue: https://github.com/direnv/direnv/pull/1532
source_pr: https://github.com/direnv/direnv/pull/1532
mechanism_tags:
  - leftover-nix-attrs-env
  - omitted-unset-list
  - use-nix-restore-map
ecosystem: direnv
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7200
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

direnv `use_nix` can keep the identity of **previous Nix structured-attrs paths** (`NIX_ATTRS_JSON_FILE`, `NIX_ATTRS_SH_FILE`) after the Nix shell that created them is gone, because `values_to_restore` listed `NIX_BUILD_TOP` / `TMP*` / `terminfo` and omitted those two names from the unset/restore map.

On failing_ref `e261bba8c9f9f32010d046a839ae5de5ae7dda0c`:

```
use_nix() {
  local -A values_to_restore=(
    ["NIX_BUILD_TOP"]=${NIX_BUILD_TOP:-__UNSET__}
    ["TMP"]=${TMP:-__UNSET__}
    ["TMPDIR"]=${TMPDIR:-__UNSET__}
    ["TEMP"]=${TEMP:-__UNSET__}
    ["TEMPDIR"]=${TEMPDIR:-__UNSET__}
    ["terminfo"]=${terminfo:-__UNSET__}
  )
  direnv_load nix-shell --show-trace "$@" --run "$(join_args "$direnv" dump)"
  for key in "${!values_to_restore[@]}"; do
    local value=${values_to_restore[$key]}
    if [[ $value == __UNSET__ ]]; then
      unset "$key"
    else
      export "$key=$value"
    fi
  done
```

`NIX_ATTRS_JSON_FILE` / `NIX_ATTRS_SH_FILE` are dumped in by `nix-shell` for structuredAttrs derivations. They are not in the restore map, so they stay exported pointing at files that do not exist after the shell is destroyed. Nested non-pure shells then crash in nixpkgs stdenv setup.

Public report (direnv/direnv#1532). Enter a structuredAttrs nix shell via direnv, leave it, enter a nested non-pure shell. Expected: those vars unset. Actual: leftover previous paths.

In-tree after the repair (not on failing_ref): those two names are in `values_to_restore`.

Case A — still inside the structuredAttrs nix shell:
  current path identity
  not leftover-after-leave

Case B — after leave / nested non-pure, leftover paths:
  leftover: previous NIX_ATTRS_* paths
  names omitted from the restore/unset map
  files gone

Case C — never entered use_nix / vars never set:
  unset identity
  not leftover previous paths

Case D — names listed in values_to_restore (post-repair shape, not on failing_ref):
  unset after leave
  not leftover previous paths

The developer wants to know which identity case B actually used for `NIX_ATTRS_JSON_FILE` after leaving use_nix: leftover previous-path (omitted from restore), current unset, or omitted (never exported).
""",
        observed="""# OBSERVED

Public direnv/direnv#1532 (merged 2026-01-07). Merge `3580653d9d3a51f093ac96c85505d71b872d7cd0` (first parent `e261bba8c9f9f32010d046a839ae5de5ae7dda0c`). Local direnv was not performed on this lab host.

PR title: fix(use_nix): unset structured attribute variables. `NIX_ATTRS_JSON_FILE` / `NIX_ATTRS_SH_FILE` point at files that do not exist after the Nix shell is destroyed. stdenv setup crashes on nested non-pure shells.

On failing_ref, `use_nix` restore map has NIX_BUILD_TOP and TMP* and terminfo. Structured-attrs names are omitted. direnv dump keeps leftover exported paths.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-149 compose listed-without-equals. specimen-150 systemd `::` cwd. specimen-158 vcpkg Windows sz==0 JOIN.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref e261bba8c9f9f32010d046a839ae5de5ae7dda0c
# stdlib.sh use_nix values_to_restore

# public shape:
# leftover NIX_ATTRS_* paths after leaving use_nix
# restore map omits those names so dump keeps them
# never-entered / listed-in-map unsets
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""direnv/direnv
  stdlib.sh
""",
        source="""repository: direnv/direnv
issue: https://github.com/direnv/direnv/pull/1532
pr: https://github.com/direnv/direnv/pull/1532
failing_ref (first parent of merge on master): e261bba8c9f9f32010d046a839ae5de5ae7dda0c
fixed_ref (merge adding NIX_ATTRS_* to values_to_restore): 3580653d9d3a51f093ac96c85505d71b872d7cd0
merged_at: 2026-01-07T20:04:00Z
pr_author: hacker1024
merged_by: zimbatm
changed_files: stdlib.sh
pr_title: fix(use_nix): unset structured attribute variables
scout_note: not 010/149/150/158. leftover NIX_ATTRS paths after use_nix because restore map omitted those names. unique vs 001-159.
""",
        answer_key="""KNOWN FIX (sealed): direnv/direnv PR 1532 merge 3580653d9d3a51f093ac96c85505d71b872d7cd0.

failing_ref is first parent e261bba8c9f9f32010d046a839ae5de5ae7dda0c.

use_nix values_to_restore omitted NIX_ATTRS_JSON_FILE and NIX_ATTRS_SH_FILE. After the nix shell was gone those leftover paths stayed exported.

PR repair: add those two names to the restore/unset map.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (inside-shell current vs leftover paths after leave vs never-set vs listed-in-map)
reproducibility: source-backed PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — omitted restore-map names JOIN previous-shell identity; two greps cannot replace
ecosystem: direnv / nix
mechanism_family: leftover-nix-attrs-env, omitted-unset-list, use-nix-restore-map

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "use_nix_failing.sh": """# Reduced excerpt of use_nix on failing_ref
# stdlib.sh
# e261bba8c9f9f32010d046a839ae5de5ae7dda0c
# values_to_restore omits NIX_ATTRS_JSON_FILE / NIX_ATTRS_SH_FILE.

use_nix() {
  local -A values_to_restore=(
    ["NIX_BUILD_TOP"]=${NIX_BUILD_TOP:-__UNSET__}
    ["TMP"]=${TMP:-__UNSET__}
    ["TMPDIR"]=${TMPDIR:-__UNSET__}
    ["TEMP"]=${TEMP:-__UNSET__}
    ["TEMPDIR"]=${TEMPDIR:-__UNSET__}
    ["terminfo"]=${terminfo:-__UNSET__}
  )
  direnv_load nix-shell --show-trace "$@" --run "$(join_args "$direnv" dump)"
  for key in "${!values_to_restore[@]}"; do
    local value=${values_to_restore[$key]}
    if [[ $value == __UNSET__ ]]; then
      unset "$key"
    else
      export "$key=$value"
    fi
  done
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  direnv use_nix values_to_restore
  leftover NIX_ATTRS_* paths after leaving the nix shell

Case A (still inside structuredAttrs nix shell):
  current path identity
  not leftover-after-leave

Case B (after leave / nested non-pure, leftover paths):
  leftover: previous NIX_ATTRS_* paths
  names omitted from the restore/unset map

Case C (never entered use_nix):
  unset identity
  not leftover previous paths

Case D (names listed in values_to_restore):
  unset after leave
  not leftover previous paths

Not this packet:
  local-fixture env-empty-vs-unset (specimen-010)
  compose listed-without-equals (specimen-149)
  systemd empty :: cwd (specimen-150)
  vcpkg Windows sz==0 JOIN (specimen-158)
""",
        },
    )


def packet_kotlin(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: JetBrains/kotlin
failing_ref: a05299825cbf5d5e19df97bd7f8ec00a98716871
fixed_ref: 0a61a56593a0d6270e6e5f66d0fd31c2209429ed
source_issue: https://github.com/JetBrains/kotlin/pull/6654
source_pr: https://github.com/JetBrains/kotlin/pull/6654
mechanism_tags:
  - leftover-native-ic-cache
  - omitted-dependencies-fingerprint
  - external-dep-rollback
ecosystem: kotlin-native
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 8000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Kotlin/Native incremental compilation can keep the identity of a **previous per-file cache** after an external dependency is rolled back to a version whose cache already exists, because `CacheMetadata` stored `compilerFingerprint` / `runtimeFingerprint` and omitted a combined fingerprint of auto-cached external libraries. The dirty-file check only compared IR content hashes of source files. Existence of the old cache was enough.

On failing_ref `a05299825cbf5d5e19df97bd7f8ec00a98716871`:

```
class CacheMetadata(
    val target: KonanTarget,
    val compilerFingerprint: String,
    val runtimeFingerprint: String?,
)

val staleCompilerCacheLibraries = icedLibraries.filter { library ->
    val cache = caches[library] as? CachedLibraries.Cache.PerFile ?: return@filter false
    val anyCachedFile = File(cache.path).listFiles.firstOrNull()?.name ?: return@filter false
    (cache.getMetadata(anyCachedFile).compilerFingerprint != currentCompilerFingerprint)
}
```

Rollback of an external library to an already-cached version does not change the compiler fingerprint and does not dirty the user's source IR hashes. Leftover previous IC cache is reused; linkage/runtime see the old dependency identity.

Public report (JetBrains/kotlin#6654 / KT-87194). Change a dependency to an earlier version whose cache was already built. Expected: full rebuild of dependable caches. Actual: leftover previous cache.

In-tree after the repair (not on failing_ref): `dependenciesFingerprint` is stored and compared; mismatch forces a full rebuild. Caches without metadata (older than 2.2.20) also rebuild.

Case A — same external deps, same compiler, source unchanged:
  cache identity is current
  not leftover-after-rollback

Case B — external dep rolled back to already-cached version, leftover IC:
  leftover: previous per-file cache built against the newer dep
  dependencies fingerprint omitted
  compiler fingerprint still matches

Case C — `clean` / missing cache directory:
  fresh cache
  not leftover previous dep

Case D — dependenciesFingerprint compared (post-repair shape, not on failing_ref):
  full rebuild after rollback
  not leftover previous cache

The developer wants to know which identity case B actually used for the IC'ed library after the rollback: leftover previous-cache (deps fingerprint omitted), current dep graph, or omitted (no cache).
""",
        observed="""# OBSERVED

Public JetBrains/kotlin#6654 (merged 2026-07-14). Squash `0a61a56593a0d6270e6e5f66d0fd31c2209429ed` (parent `a05299825cbf5d5e19df97bd7f8ec00a98716871`). Local kotlin-native was not performed on this lab host.

PR title: Incremental compilation: fixed stale external caches problem. There was no check if an external library was changed (only existence of its cache). Rollback to an already-cached version reused leftover IC.

On failing_ref, stale detection compared `compilerFingerprint` only. `CacheMetadata` had no `dependenciesFingerprint`. Dirty-file analysis compared source IR hashes.

Not this packet: specimen-104 gradle incremental. specimen-075 rust incremental leftover. specimen-103 go work-sync leftover replace.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref a05299825cbf5d5e19df97bd7f8ec00a98716871
# kotlin-native/.../CacheBuilder.kt staleCompilerCacheLibraries
# kotlin-native/.../CacheSerializationSupport.kt CacheMetadata

# public shape:
# leftover Native IC cache after external dep rollback
# metadata stores compiler fingerprint; deps fingerprint omitted
# clean / miss writes a new cache
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""JetBrains/kotlin
  kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/CacheBuilder.kt
  kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/serialization/CacheSerializationSupport.kt
  kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/CachedLibraries.kt
""",
        source="""repository: JetBrains/kotlin
issue: https://github.com/JetBrains/kotlin/pull/6654
pr: https://github.com/JetBrains/kotlin/pull/6654
failing_ref (parent of squash): a05299825cbf5d5e19df97bd7f8ec00a98716871
fixed_ref (dependenciesFingerprint stored and compared): 0a61a56593a0d6270e6e5f66d0fd31c2209429ed
merged_at: 2026-07-14T17:26:08Z
pr_author: homuroll
merged_by: woainikk
changed_files: kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/CacheBuilder.kt, kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/CachedLibraries.kt, kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/CacheStorage.kt, kotlin-native/backend.native/compiler/ir/backend.native/src/org/jetbrains/kotlin/backend/konan/serialization/CacheSerializationSupport.kt
pr_title: Incremental compilation: fixed stale external caches problem
scout_note: not 104/075/103. leftover Native IC after external dep rollback because dependenciesFingerprint omitted. unique vs 001-159.
""",
        answer_key="""KNOWN FIX (sealed): JetBrains/kotlin PR 6654 squash 0a61a56593a0d6270e6e5f66d0fd31c2209429ed.

failing_ref is parent a05299825cbf5d5e19df97bd7f8ec00a98716871.

CacheMetadata stored compilerFingerprint only. Dirty-file IR hashes did not see an external dep rollback to an already-cached version. Leftover previous IC cache HIT.

PR repair: store and compare dependenciesFingerprint; rebuild when it mismatches or metadata is absent.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (same-deps current vs leftover after rollback vs clean vs fingerprint-compared)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — existence of old cache JOINs previous dep identity; two greps cannot replace
ecosystem: kotlin-native / incremental cache
mechanism_family: leftover-native-ic-cache, omitted-dependencies-fingerprint, external-dep-rollback

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "CacheMetadata_failing.kt": """// Reduced excerpt of CacheMetadata on failing_ref
// kotlin-native/.../CacheSerializationSupport.kt
// a05299825cbf5d5e19df97bd7f8ec00a98716871
// dependenciesFingerprint omitted.

class CacheMetadata(
    val target: KonanTarget,
    val compilerFingerprint: String,
    val runtimeFingerprint: String?,
)
""",
            "CacheBuilder_failing.kt": """// Reduced excerpt of stale cache detection on failing_ref
// kotlin-native/.../CacheBuilder.kt
// only compilerFingerprint is compared.

val currentCompilerFingerprint = config.distribution.compilerFingerprint
val staleCompilerCacheLibraries = icedLibraries.filter { library ->
    val cache = caches[library] as? CachedLibraries.Cache.PerFile ?: return@filter false
    val anyCachedFile = File(cache.path).listFiles.firstOrNull()?.name ?: return@filter false
    (cache.getMetadata(anyCachedFile).compilerFingerprint != currentCompilerFingerprint)
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  Kotlin/Native CacheBuilder / CacheMetadata
  leftover IC cache after external dep rollback

Case A (same deps, same compiler, source unchanged):
  current cache identity
  not leftover-after-rollback

Case B (dep rolled back to already-cached version, leftover IC):
  leftover: previous per-file cache built against the newer dep
  dependencies fingerprint omitted

Case C (clean / missing cache directory):
  fresh cache
  not leftover previous dep

Case D (dependenciesFingerprint compared):
  full rebuild after rollback
  not leftover previous cache

Not this packet:
  gradle incremental (specimen-104)
  rust incremental leftover (specimen-075)
  go work-sync leftover replace (specimen-103)
""",
        },
    )


PACKETS = [
    (None, "hdd-xtalmd", packet_crystal,
     "crystal leftover multidispatch chain omitted target_def ids; not 054/154/159"),
    (None, "hdd-nexthmr", packet_next,
     "next leftover 'use cache' after edit omitted server HMR hash; not 090/156/157"),
    (None, "hdd-dirnix", packet_direnv,
     "direnv leftover NIX_ATTRS after use_nix omitted unset; not 010/149/150/158"),
    (None, "hdd-ktnativ", packet_kotlin,
     "kotlin leftover Native IC after external dep rollback omitted deps fingerprint; not 104/075"),
]


def _claim_job(state, job_id: str, worker: str) -> None:
    job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
    if job is None:
        return
    if job.get("status") == "READY":
        job["status"] = "CLAIMED"
        job["claimed_at"] = now_jst()
        job["worker"] = worker
        workers = state.setdefault("workers", [])
        rec = next((w for w in workers if w.get("id") == worker), None)
        if rec is None:
            workers.append({"id": worker, "status": "active", "job": job_id})
        else:
            rec["status"] = "active"
            rec["job"] = job_id
    elif job.get("status") == "CLAIMED":
        old = job.get("worker")
        if old not in {None, worker} and not str(old).startswith("scout-"):
            raise SystemExit(f"{job_id} status=CLAIMED worker={old}")
        job["worker"] = worker
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')}")


def _init_trial(trial: str, seed: str) -> None:
    script = RUN_DIR / "scripts" / "init_trial.sh"
    subprocess.run([str(script), trial, seed], check=True, cwd=str(RUN_DIR))


def _complete_and_enqueue(packed: list[tuple[str | None, str, str, str]]) -> str:
    note = {"reason": ""}

    def fn(state):
        for jid, artifact in SKIP_JOBS.items():
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
            if job is None:
                continue
            if job.get("status") in {"READY", "CLAIMED"}:
                if job.get("status") == "READY":
                    _claim_job(state, jid, WORKER)
                old = job.get("worker")
                if old in {None, WORKER} or str(old).startswith("scout-"):
                    complete(state, jid, result="skip", artifact=artifact)
        ids = {s.get("id") for s in state.get("specimens") or []}
        reasons = []
        for job_id, spec_id, trial, priority_reason in packed:
            if spec_id not in ids:
                state.setdefault("specimens", []).append({"id": spec_id})
                ids.add(spec_id)
            if job_id:
                job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
                if job is not None and job.get("status") in {"READY", "CLAIMED"}:
                    if job.get("status") == "READY":
                        _claim_job(state, job_id, WORKER)
                    old = job.get("worker")
                    if old in {None, WORKER} or str(old).startswith("scout-"):
                        complete(state, job_id, result="ok", artifact=f"specimens/{spec_id}")
            already = any(
                j.get("queue") == "READY_R1_DREAM"
                and j.get("specimen") == spec_id
                and j.get("status") in {"READY", "CLAIMED"}
                for j in state.get("ready_jobs") or []
            )
            if not already:
                enqueue(
                    state,
                    "READY_R1_DREAM",
                    input_ref=f"seeds/{spec_id}.md trial={trial}",
                    expected_output="0001-dreamer.md",
                    kill_condition="15m",
                    estimated_cost="r1",
                    priority_reason=priority_reason,
                    specimen=spec_id,
                    lineage=trial,
                    phase="cambrian",
                    extra={"trial": trial},
                )
            reasons.append(f"READY_R1_DREAM trial={trial} specimen={spec_id}")
        existing_inputs = {
            j.get("input")
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_SPECIMEN_SCOUT"
        }
        for input_ref, reason in NEXT_SCOUTS:
            if input_ref in existing_inputs:
                continue
            enqueue(
                state,
                "READY_SPECIMEN_SCOUT",
                input_ref=input_ref,
                expected_output="specimens/specimen-NNN leftover-identity packet",
                kill_condition="25m no unique leftover-identity pair; skip bazel#29298; never overwrite 075",
                estimated_cost="low",
                priority_reason=reason,
                phase="cambrian",
            )
        note["reason"] = "; ".join(reasons)
        return True

    with_state(fn)
    return note["reason"]


def main() -> None:
    claimed: list[str] = []
    packed: list[tuple[str | None, str, str, str]] = []
    try:
        for job_id, trial, builder, priority_reason in PACKETS:
            spec_id = _claim_id()
            claimed.append(spec_id)
            emit(builder(spec_id))
            seed = write_seed(SPECIMENS / spec_id)
            _init_trial(trial, str(seed))
            packed.append((job_id, spec_id, trial, priority_reason))
        update_index()
        launch_note = _complete_and_enqueue(packed)
        for job_id, spec_id, trial, _ in packed:
            print(SPECIMENS / spec_id)
            print(f"seed=seeds/{spec_id}.md trial={trial} job={job_id}")
            print(f"hdd={HDD_ROOT / trial}")
        print(launch_note)
        print(f"ids={[p[1] for p in packed]} worker={WORKER} at={now_jst()}")
        for jid, artifact in SKIP_JOBS.items():
            print(f"SKIP {jid}: {artifact}")
    except Exception:
        for spec_id in claimed:
            dest = SPECIMENS / spec_id
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
        raise


if __name__ == "__main__":
    main()
