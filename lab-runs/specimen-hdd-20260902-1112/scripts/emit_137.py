#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets 137+.

Packed (unique vs 001-136; 075 not overwritten; not bazel#29298):
1) prisma/orm#27279 (issue prisma/prisma#27128): leftover generated
   client after schema.prisma change because `prisma generate --watch`
   reused the first-load schemaContext. Distinct from 041/043 protobuf.
2) psf/black#5152: leftover pyproject.toml identity after CWD change
   because find_project_root @lru_cache keyed (srcs, stdin_filename)
   and resolved Path.cwd() inside the cached function when srcs empty.

Already packed / SKIP:
- job-0585 pants leftover vcs_version: specimen-136 PR 17017 (do not overwrite).
- job-0586 buf leftover generated vs proto: no merged leftover-identity pair.
- job-0587 go generate leftover vs source: no merged leftover-identity pair
  (#11835 no PR; #79585 OPEN).
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 137
WORKER = "scout-coord-1935"

PACKETS = [
    {
        "trial": "hdd-prismagen",
        "builder": "packet_prisma",
        "priority_reason": (
            "prisma leftover generate --watch schemaContext after schema.prisma "
            "change; not 041/043"
        ),
    },
    {
        "trial": "hdd-blackcwd",
        "builder": "packet_black",
        "priority_reason": (
            "black leftover lru_cache project-root omits resolved CWD; not 114"
        ),
    },
]


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 180):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_prisma(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: prisma/orm
failing_ref: 23e865c5601534f14cfe5fbc097c2eb1cf4f342e
fixed_ref: 8d06a847ea4e84c70c84469b2a845e568f454e14
source_issue: https://github.com/prisma/prisma/issues/27128
source_pr: https://github.com/prisma/orm/pull/27279
mechanism_tags:
  - leftover-generated-client
  - omitted-schema-reload
  - watch-schemacontext-reuse
ecosystem: prisma
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7800
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

`prisma generate --watch` can keep the identity of a **previous generated client** after `schema.prisma` should have been a different schema. The first load builds `schemaContext` once. The watch loop regenerates from that leftover object. Current schema file identity is omitted.

On failing_ref `23e865c5601534f14cfe5fbc097c2eb1cf4f342e`:

```
const schemaResult = await getSchemaForGenerate(...)
const schemaContext = await processSchemaResult({ schemaResult, ... })
const directoryConfig = inferDirectoryConfig(schemaContext)
// ... first generate ...
const watcher = new Watcher(schemaContext.schemaRootDir)
for await (const changedPath of watcher) {
  logUpdate(`Change in ${path.relative(process.cwd(), changedPath)}`)
  generatorsWatch = await getGenerators({
    schemaContext,  // leftover first-load schema
    ...
  })
  await this.runGenerate({ generators: generatorsWatch })
}
```

Public report (prisma/prisma#27128). `prisma generate --watch`; append `model B`; leftover generated client still only `A.ts` until a non-watch `prisma generate`.

In-tree after the repair (not on failing_ref): watch loop re-runs `getSchemaForGenerate` + `processSchemaResult` + `inferDirectoryConfig`. E2E `27128-generate-watch` expects `['A.ts','B.ts']` after the append.

Case A — second watch tick, unchanged schema.prisma:
  generated client identity is current
  not leftover-after-schema-change

Case B — schema.prisma appends model B, leftover schemaContext:
  leftover: previous schema's generated client (A.ts only)
  current schema file omitted from watch generate identity
  B.ts missing

Case C — `prisma generate` without `--watch` after the append:
  current schema identity
  not leftover previous client

Case D — reload schema inside the watch loop (post-repair shape, not on failing_ref):
  generated client includes B.ts
  not leftover previous schema

The developer wants to know which identity case B actually used for the generated client after the schema.prisma change: leftover first-load schemaContext, current schema file identity, or omitted (no generate).
""",
        observed="""# OBSERVED

Public prisma/prisma#27128 (closed 2025-05-28). PR prisma/orm#27279 squash `8d06a847ea4e84c70c84469b2a845e568f454e14` (parent `23e865c5601534f14cfe5fbc097c2eb1cf4f342e`). Local prisma generate was not performed on this lab host.

Issue body: `prisma generate --watch` runs once correctly, then produces the same generated client regardless of schema.prisma changes. A second terminal `prisma generate` (no watch) writes the current client; the watch process then reverts it to the leftover first-load client.

On failing_ref, `schemaContext` is built once before the watcher. The watch loop does **not** call `getSchemaForGenerate`. That reload is added by PR 27279.

Not this packet: specimen-041 protobuf JSON unknown-fields. specimen-043 protobuf CI generated-code-drift. specimen-136 pants leftover vcs_version process cache.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 23e865c5601534f14cfe5fbc097c2eb1cf4f342e
# packages/cli/src/Generate.ts watch loop reuses leftover schemaContext

# public shape:
# leftover generated client after schema.prisma appends model B
# watch generate identity is first-load schemaContext
# generated/models stays ['A.ts'] until non-watch prisma generate
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""prisma/orm
  packages/cli/src/Generate.ts
  packages/cli/src/generate/Watcher.ts
  packages/client/tests/e2e/27128-generate-watch/prisma/schema.prisma
  packages/client/tests/e2e/27128-generate-watch/tests/main.mts
""",
        source="""repository: prisma/orm
issue: https://github.com/prisma/prisma/issues/27128
pr: https://github.com/prisma/orm/pull/27279
failing_ref (parent of squash on main): 23e865c5601534f14cfe5fbc097c2eb1cf4f342e
fixed_ref (reload schema in watch generate): 8d06a847ea4e84c70c84469b2a845e568f454e14
merged_at: 2025-05-28T17:14:02Z
pr_author: aqrln
merged_by: aqrln
changed_files: packages/cli/src/Generate.ts, packages/client/tests/e2e/27128-generate-watch/*
pr_title: fix(cli): reload the schema when generating the client in watch mode
scout_note: not 041/043 protobuf generated-drift. Distinct leftover: watch loop keeps first-load schemaContext so leftover generated client after schema.prisma change is treated as current. job-0588 was SKIP prisma/prisma unsearchable; pair is prisma/orm#27279.
""",
        answer_key="""KNOWN FIX (sealed): prisma/orm PR 27279 squash 8d06a847ea4e84c70c84469b2a845e568f454e14.

failing_ref is parent 23e865c5601534f14cfe5fbc097c2eb1cf4f342e.

prisma generate --watch reused leftover schemaContext from the first load, so leftover generated client after a schema.prisma change kept previous models.

PR repair: re-run getSchemaForGenerate + processSchemaResult + inferDirectoryConfig inside the watch loop.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged schema vs leftover watch client after append vs non-watch generate vs reload in loop)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — watcher path and schema object are different identities; leftover schemaContext stayed current after schema.prisma changed
ecosystem: prisma / generate watch
mechanism_family: leftover-generated-client, omitted-schema-reload, watch-schemacontext-reuse

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "Generate_watch_failing.ts": """// Reduced excerpt of Generate.ts watch loop on failing_ref
// packages/cli/src/Generate.ts
// 23e865c5601534f14cfe5fbc097c2eb1cf4f342e
// schemaContext loaded once. Watch generate reuses leftover object.

    const schemaResult = await getSchemaForGenerate(args['--schema'], config.schema, cwd, Boolean(postinstallCwd))
    const schemaContext = await processSchemaResult({ schemaResult, ignoreEnvVarErrors: !args['--sql'] })
    const directoryConfig = inferDirectoryConfig(schemaContext)
    // first generate uses schemaContext
    const watcher = new Watcher(schemaContext.schemaRootDir)
    for await (const changedPath of watcher) {
      logUpdate(`Change in ${path.relative(process.cwd(), changedPath)}`)
      // no getSchemaForGenerate here
      generatorsWatch = await getGenerators({
        schemaContext,
        printDownloadProgress: !watchMode,
        version: enginesVersion,
        generatorNames: args['--generator'],
        typedSql,
        registry: defaultRegistry.toInternal(),
      })
      await this.runGenerate({ generators: generatorsWatch })
    }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  prisma generate --watch
  leftover generated client after schema.prisma appends model B

Case A (second watch tick, same schema.prisma):
  current generated client identity
  not leftover-after-schema-change

Case B (schema.prisma appends model B, leftover schemaContext):
  leftover: previous schema's generated client (A.ts only)
  current schema file omitted from watch generate identity
  B.ts missing

Case C (prisma generate without --watch):
  current schema identity
  not leftover previous client

Case D (reload schema inside watch loop):
  generated client includes B.ts
  not leftover previous schema

Not this packet:
  protobuf JSON unknown-fields (specimen-041)
  protobuf CI generated-code-drift (specimen-043)
  pants leftover vcs_version process cache (specimen-136)
""",
        },
    )


def packet_black(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: psf/black
failing_ref: c77093e228ff21a93638b42356aa0a4d2713aa17
fixed_ref: d246367ab471cd56298407858661d475c33b3e36
source_issue: null
source_pr: https://github.com/psf/black/pull/5152
mechanism_tags:
  - leftover-lru-cache
  - omitted-cwd-cache-key
  - pyproject-root-identity
ecosystem: black
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

`black --code` can keep the identity of a **previous project root / pyproject.toml** after the process CWD should have been a different directory. `find_project_root` is `@lru_cache`'d on `(srcs, stdin_filename)`. When `srcs` is empty it resolves `Path.cwd()` *inside* the cached function, so CWD is omitted from the cache key.

On failing_ref `c77093e228ff21a93638b42356aa0a4d2713aa17`:

```
@lru_cache
def find_project_root(
    srcs: Sequence[str], stdin_filename: str | None = None
) -> tuple[Path, str]:
    if stdin_filename is not None:
        srcs = tuple(stdin_filename if s == "-" else s for s in srcs)
    if not srcs:
        srcs = [str(_cached_resolve(Path.cwd()))]
    path_srcs = [_cached_resolve(Path(Path.cwd(), src)) for src in srcs]
    # walk parents for .git / .hg / pyproject.toml [tool.black]
```

Public report (psf/black PR 5152). In-process `black --code` from directory A then directory B (test `test_code_option_config` / `test_code_option_parent_config` with `change_directory`): leftover cached root from A; wrong pyproject.toml.

In-tree after the repair (not on failing_ref): public `find_project_root` resolves CWD and absolute srcs first; `_find_project_root_cached` is `@lru_cache`'d only on fully-resolved paths.

Case A — second `black --code` from the same CWD:
  project-root identity is current
  not leftover-after-cwd-change

Case B — `black --code` from a different CWD, leftover lru_cache:
  leftover: previous CWD's project root / pyproject.toml
  resolved CWD omitted from cache key (srcs=())
  wrong config applied

Case C — new process (empty lru_cache) from CWD B:
  current CWD root identity
  not leftover previous directory

Case D — CWD resolved before the cache key (post-repair shape, not on failing_ref):
  each directory gets its own pyproject.toml
  not leftover previous root

The developer wants to know which identity case B actually used for the project root after the CWD change: leftover previous-CWD pyproject, current CWD identity, or omitted (no cache).
""",
        observed="""# OBSERVED

Public psf/black PR 5152 squash `d246367ab471cd56298407858661d475c33b3e36` (parent `c77093e228ff21a93638b42356aa0a4d2713aa17`). Local black was not performed on this lab host.

PR body: when `srcs` is empty (`black --code`), `find_project_root` fell back to `os.getcwd()` inside `@lru_cache`. Cache key is only `(srcs, stdin_filename)`. Two calls from different directories with `srcs=()` share the leftover entry.

On failing_ref, `@lru_cache` sits on `find_project_root`. Resolved CWD is **not** part of the key. `_find_project_root_cached` is added by PR 5152.

Not this packet: specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files. specimen-132 eslint leftover plugin name@version omitted from toJSON.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref c77093e228ff21a93638b42356aa0a4d2713aa17
# src/black/files.py find_project_root @lru_cache

# public shape:
# leftover project root after black --code from a different CWD
# cache key omits resolved CWD when srcs is empty
# wrong pyproject.toml [tool.black]
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""psf/black
  src/black/files.py
  tests/test_black.py
  pyproject.toml
""",
        source="""repository: psf/black
issue: null
pr: https://github.com/psf/black/pull/5152
failing_ref (parent of squash on main): c77093e228ff21a93638b42356aa0a4d2713aa17
fixed_ref (resolve CWD before lru_cache key): d246367ab471cd56298407858661d475c33b3e36
merged_at: 2026-06-01T16:34:38Z
pr_author: anisia19
merged_by: cobaltt7
changed_files: src/black/files.py, CHANGES.md
pr_title: fix: resolve CWD before lru_cache key in find_project_root
scout_note: not 114 ruff nested pyproject. Distinct leftover: lru_cache key omits resolved CWD so leftover project-root pyproject after CWD change is treated as current.
""",
        answer_key="""KNOWN FIX (sealed): psf/black PR 5152 squash d246367ab471cd56298407858661d475c33b3e36.

failing_ref is parent c77093e228ff21a93638b42356aa0a4d2713aa17.

find_project_root @lru_cache keyed (srcs, stdin_filename) and resolved Path.cwd() inside the cached function when srcs was empty, so leftover project-root pyproject after a CWD change stayed current.

PR repair: resolve CWD and absolute srcs before the cache key; cache only fully-resolved paths.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (same CWD vs leftover root after CWD flip vs new process vs CWD in cache key)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — CWD and srcs tuple are different identities; empty srcs omitted CWD so leftover pyproject stayed current
ecosystem: black / project-root cache
mechanism_family: leftover-lru-cache, omitted-cwd-cache-key, pyproject-root-identity

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "find_project_root_failing.py": """# Reduced excerpt of find_project_root on failing_ref
# src/black/files.py
# c77093e228ff21a93638b42356aa0a4d2713aa17
# CWD resolved inside @lru_cache. Key is (srcs, stdin_filename) only.

@lru_cache
def find_project_root(
    srcs: Sequence[str], stdin_filename: str | None = None
) -> tuple[Path, str]:
    if stdin_filename is not None:
        srcs = tuple(stdin_filename if s == "-" else s for s in srcs)
    if not srcs:
        srcs = [str(_cached_resolve(Path.cwd()))]
    path_srcs = [_cached_resolve(Path(Path.cwd(), src)) for src in srcs]
    # walk parents for .git / .hg / pyproject.toml [tool.black]
""",
            "leftover_identity_split.txt": """Registry / fixture:
  black --code from two directories in one process
  leftover project-root pyproject after CWD change

Case A (second black --code, same CWD):
  current project-root identity
  not leftover-after-cwd-change

Case B (black --code from different CWD, leftover lru_cache):
  leftover: previous CWD's project root / pyproject.toml
  resolved CWD omitted from cache key (srcs=())
  wrong config applied

Case C (new process from CWD B):
  current CWD root identity
  not leftover previous directory

Case D (CWD resolved before cache key):
  each directory gets its own pyproject.toml
  not leftover previous root

Not this packet:
  ruff leftover cache vs nested pyproject (specimen-114)
  pytest leftover cache-dir supporting files (specimen-107)
  eslint leftover plugin name@version omitted from toJSON (specimen-132)
""",
        },
    )


BUILDERS = {
    "packet_prisma": packet_prisma,
    "packet_black": packet_black,
}


def _enqueue_r1(spec_id: str, trial: str, priority_reason: str) -> str:
    note = {"reason": ""}

    def fn(state):
        ids = {s.get("id") for s in state.get("specimens") or []}
        if spec_id not in ids:
            state.setdefault("specimens", []).append({"id": spec_id})
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
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        if claimed_r1:
            note["reason"] = (
                "READY_R1_DREAM enqueued trial="
                + trial
                + "; in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
            )
        else:
            note["reason"] = f"READY_R1_DREAM enqueued trial={trial} specimen={spec_id}"
        return spec_id

    with_state(fn)
    return note["reason"]


def main() -> None:
    packed = []
    for item in PACKETS:
        spec_id = _claim_id()
        dest = SPECIMENS / spec_id
        if spec_id == "specimen-075":
            raise SystemExit("refusing to overwrite 075")
        try:
            builder = BUILDERS[item["builder"]]
            path = emit(builder(spec_id))
            seed = write_seed(SPECIMENS / spec_id)
            packed.append((spec_id, item["trial"], path, seed, item["priority_reason"]))
        except Exception:
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
            raise
    update_index()
    for spec_id, trial, path, seed, reason in packed:
        launch_note = _enqueue_r1(spec_id, trial, reason)
        print(path)
        print(seed)
        print(launch_note)
        print(f"ids={spec_id} trial={trial}")


if __name__ == "__main__":
    main()
