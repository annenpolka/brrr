#!/usr/bin/env python3
"""Emit five sealed REAL_SOURCE_BACKED leftover-identity packets from 109.

Packed (unique vs 001-108; 075 not overwritten; not bazel#29298):
1) composer/composer#12417 / PR 12423: leftover abandoned state in
   installed.json vs lock. Distinct from 074/021/086.
2) microsoft/TypeScript#64025 / PR 64026: leftover tsbuildinfo
   semanticDiagnostics vs JSON source identity. Distinct from 067/075.
3) astral-sh/ruff#12264 / PR 12727: leftover cache vs nested
   pyproject.toml identity. Distinct from 001-003/107.
4) go-task/task#1795 / PR 1808: leftover wildcard fingerprint omitting
   MATCH. Distinct from 076/088/104. Packed instead of pants fingerprint
   (job-0464: no leftover-identity merged pair).
5) coder/coder PR 27987: leftover highlight cache keyed by filename not
   patch content. Distinct from 090/094. Packed instead of next.js
   webpack cache leftover (job-0465: no merged leftover-identity pair).

SKIP: conan lock leftover (job-0459: no merged pinned pair), cargo git
sparse leftover (job-0462: #11165 open), npm bundledDependencies leftover
(job-0463: #3466/#5111/#7137/#9289/#9321 still open).
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 109
PACKED = [
    ("job-0458", "scout-job-0458", "hdd-compabandon", "composer leftover abandoned in installed.json vs lock; not 074/021/086"),
    ("job-0460", "scout-job-0460", "hdd-tsbuildinfo", "ts leftover tsbuildinfo diagnostics vs JSON source; not 067/075"),
    ("job-0461", "scout-job-0461", "hdd-ruffnest", "ruff leftover cache vs nested pyproject identity; not 001-003/107"),
    ("job-0464", "scout-job-0464", "hdd-taskwild", "go-task leftover wildcard fingerprint omits MATCH; not 076/088/104"),
    ("job-0465", "scout-job-0465", "hdd-diffcache", "coder leftover highlight cache keyed by filename; not 090/094"),
]
SKIP_JOBS = {
    "job-0459": (
        "skip conan lock leftover vs recipe identity: no merged pinned "
        "failing+fixed pair (#18954/#20175/#17134 still open; #19740 is "
        "alias removal not lock leftover). not inventing refs; not 001-108"
    ),
    "job-0462": (
        "skip cargo git sparse leftover vs checkout identity: #11165 still "
        "open (no merged sparse-checkout support). not 091/099/101. packed "
        "go-task leftover wildcard fingerprint as 112 instead"
    ),
    "job-0463": (
        "skip npm bundledDependencies leftover identity: #3466/#5111/#7137/"
        "#9289/#9321 still open; no merged pinned pair. not 004/033/095. "
        "packed coder leftover highlight-cache identity as 113 instead"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: sbt zinc incremental leftover vs source identity not 076/088/104",
        "unique sbt zinc leftover",
    ),
    (
        "public OSS: coursier cache leftover vs artifact identity not 074/021",
        "unique coursier leftover",
    ),
    (
        "public OSS: meson wrap leftover vs wrap-file identity not 001-108",
        "unique meson wrap leftover",
    ),
    (
        "public OSS: eslint cache leftover vs config identity not 12264/107",
        "unique eslint cache leftover",
    ),
    (
        "public OSS: jest cache leftover vs module identity not 090/094",
        "unique jest cache leftover",
    ),
    (
        "public OSS: virtualenv leftover interpreter identity not 106/040",
        "unique virtualenv leftover",
    ),
    (
        "public OSS: pipx leftover venv identity after upgrade not 031/098",
        "unique pipx leftover",
    ),
    (
        "public OSS: prettier cache leftover vs source identity not 090/094",
        "unique prettier leftover",
    ),
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


def packet_composer(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: composer/composer
failing_ref: aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8
fixed_ref: 1a22bb197a6e62ca431928627ef232bd4d335097
source_issue: https://github.com/composer/composer/issues/12417
source_pr: https://github.com/composer/composer/pull/12423
mechanism_tags:
  - leftover-installed-json-abandoned
  - lock-vs-installed-identity
  - omitted-abandon-on-same-version
ecosystem: php-composer
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Composer's `vendor/composer/installed.json` can keep the identity of a package **as not abandoned** after `composer.lock` already records `"abandoned": true` (or a replacement name) for the same version. `composer audit` reads installed.json, so leftover omitted-abandoned identity makes audit report none.

On failing_ref `aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8`, `Transaction::calculateOperations` decides whether a present package is an update with only version / dist-ref / source-ref:

```
if ($package->getVersion() !== $presentPackageMap[$package->getName()]->getVersion() ||
    $package->getDistReference() !== $presentPackageMap[$package->getName()]->getDistReference() ||
    $package->getSourceReference() !== $presentPackageMap[$package->getName()]->getSourceReference()
) {
    $operations[] = new Operation\\UpdateOperation($source, $package);
}
```

Abandoned / replacement-package are not in that identity. Same version + same refs → no reinstall → installed.json leftover.

Public report (composer/composer#12417): `behat/transliterator` was installed before Packagist tagged it abandoned. Later `composer update` wrote `"abandoned": true` into `composer.lock`. `composer audit` still reported no abandoned package. `vendor/composer/installed.json` omitted `"abandoned"`. `rm -rf vendor && composer install` wrote abandoned into installed.json and audit failed as expected.

In-tree after the repair (not on failing_ref): `tests/Composer/Test/Fixtures/installer/install-forces-reinstall-if-abandon-changes.test`. INSTALLED has `"abandoned": "old-replacement"`, LOCK has `"abandoned": "replacement"`, same `1.0.0`. Expect `Upgrading a/a (1.0.0 => 1.0.0)` and installed.json replacement.

Case A — fresh `composer install` with lock already abandoned, empty vendor:
  installed.json written with abandoned
  no leftover omitted-abandoned identity

Case B — leftover vendor from before the abandon tag; lock now has abandoned; same version:
  leftover: installed.json omitted abandoned
  lock has abandoned
  audit reports none

Case C — `rm -rf vendor && composer install`:
  fresh identity
  not leftover sweep

Case D — version bump that is already an UpdateOperation:
  reinstall happens for version identity
  not this leftover (same-version omit)

The developer wants to know which identity case B actually left in `vendor/composer/installed.json`: leftover omitted-abandoned (lock has abandoned, installed does not), abandoned present, or omitted (no installed.json).
""",
        observed="""# OBSERVED

Public composer/composer#12417 (closed 2025-09-18). PR 12423 squash `1a22bb197a6e62ca431928627ef232bd4d335097` (parent `aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8`). Local composer was not performed on this lab host.

Issue body: lock gained `"abandoned": true` after Packagist tagged the already-installed package. installed.json omitted abandoned. audit read installed.json and reported none. Wipe vendor + install healed it.

On failing_ref, calculateOperations compares version / dist-ref / source-ref only. Abandoned and replacement-package are not that identity. Same-version leftover vendor is not an UpdateOperation.

`isAbandoned()` / `getReplacementPackage()` on CompletePackageInterface are **not** on the failing revision's update predicate. They are added by PR 12423.

Not this packet: specimen-074 (rubygems platform-fallback extra). specimen-021 (poetry lock leftover). specimen-086 (cargo rustc-fingerprint metadata). emit_086 composer classmap leftover was not the claimed 086 packet (086 is cargo). job-0458 hunt was installed.json vs lock, not classmap.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8
# src/Composer/DependencyResolver/Transaction.php calculateOperations

# public shape:
# leftover vendor installed.json omitted abandoned
# composer.lock has abandoned
# composer audit reports none
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""composer/composer
  src/Composer/DependencyResolver/Transaction.php
  tests/Composer/Test/Fixtures/installer/install-forces-reinstall-if-abandon-changes.test
""",
        source="""repository: composer/composer
issue: https://github.com/composer/composer/issues/12417
pr: https://github.com/composer/composer/pull/12423
failing_ref (squash parent / PR base): aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8
fixed_ref (squash merge): 1a22bb197a6e62ca431928627ef232bd4d335097
merged_at: 2025-09-18T09:46:16Z
pr_author: Seldaek
merged_by: Seldaek
changed_files: src/Composer/DependencyResolver/Transaction.php, tests/Composer/Test/Fixtures/installer/install-forces-reinstall-if-abandon-changes.test, tests/Composer/Test/Fixtures/installer/update-syncs-outdated.test
pr_title: Ensure packages where the abandoned state changes get reinstalled to sync up the state in installed.json
scout_note: not specimen-074/021/086. Distinct leftover: installed.json omitted abandoned while lock has abandoned. job-0458.
""",
        answer_key="""KNOWN FIX (sealed): composer/composer PR 12423 squash 1a22bb197a6e62ca431928627ef232bd4d335097.

failing_ref is squash parent aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8.

calculateOperations treated leftover same-version vendor as identity and skipped reinstall when only abandoned/replacement changed.

PR repair: also compare isAbandoned() and getReplacementPackage() on CompletePackageInterface; same-version abandon change is UpdateOperation and rewrites installed.json.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (fresh install writes abandoned vs leftover omitted abandoned vs wipe+install vs version-bump reinstall)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — lock abandoned identity and installed.json abandoned identity are different objects; same-version leftover blocked audit
ecosystem: php / composer
mechanism_family: leftover-installed-json, omitted-abandon, lock-vs-installed

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "transaction_update_predicate_failing.php": """# Reduced excerpt of Transaction::calculateOperations on failing_ref
# src/Composer/DependencyResolver/Transaction.php
# aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8
# Version / dist-ref / source-ref are the installed identity.
# Abandoned / replacement-package are not that identity.

                        if ($package->getVersion() !== $presentPackageMap[$package->getName()]->getVersion() ||
                            $package->getDistReference() !== $presentPackageMap[$package->getName()]->getDistReference() ||
                            $package->getSourceReference() !== $presentPackageMap[$package->getName()]->getSourceReference()
                        ) {
                            $operations[] = new Operation\\UpdateOperation($source, $package);
                        }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  leftover vendor/composer/installed.json
  composer.lock already has abandoned
  same version

Case A (fresh install, empty vendor):
  installed.json written with abandoned
  no leftover omitted-abandoned

Case B (leftover vendor from before abandon tag):
  leftover: installed.json omitted abandoned
  lock has abandoned
  audit reports none

Case C (rm -rf vendor && composer install):
  fresh identity
  not leftover sweep

Case D (version bump UpdateOperation):
  reinstall for version identity
  not this leftover

Not this packet:
  rubygems platform-fallback extra (specimen-074)
  poetry lock leftover (specimen-021)
  cargo rustc-fingerprint metadata (specimen-086)
""",
        },
    )


def packet_ts(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: microsoft/TypeScript
failing_ref: 5739027c9a7df24e27123f453a50c011b37717b6
fixed_ref: 13e158b131a6ec523fc6ee76376c8ff1a55451ab
source_issue: https://github.com/microsoft/TypeScript/issues/64025
source_pr: https://github.com/microsoft/TypeScript/pull/64026
mechanism_tags:
  - leftover-tsbuildinfo-diagnostics
  - json-module-shape-signature
  - semanticDiagnosticsPerFile-replay
ecosystem: typescript
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

TypeScript `--incremental` can keep the identity of a **stale diagnostic** in `tsconfig.tsbuildinfo` after the JSON module that caused it is fixed on disk. A later warm `tsc -p .` replays `semanticDiagnosticsPerFile` for the importer even though `fileInfos` already has the new JSON content-hash.

On failing_ref `5739027c9a7df24e27123f453a50c011b37717b6`, JSON modules have no declaration emit. `updateShapeSignature` uses an empty declaration as the shape signature, so a later JSON content change looks shape-equivalent. Dependents' cached diagnostics are not invalidated.

Public report (microsoft/TypeScript#64025), `incremental` + `resolveJsonModule`:

```
rm -f tsconfig.tsbuildinfo
printf '{ "title": "hello" }\\n' > data.json
tsc -p .    # 1. cold: clean

printf '{ }\\n' > data.json
tsc -p .    # 2. warm: TS2741 — correct

printf '{ "title": "fixed" }\\n' > data.json
tsc -p .    # 3. warm: STILL TS2741 — leftover diagnostic identity
            # data.json on disk has "title"

rm -f tsconfig.tsbuildinfo
tsc -p .    # 4. identical files, cache deleted: clean
```

Diff of tsbuildinfo between steps 2 and 3: `data.json` `fileInfos.version` changes; `semanticDiagnosticsPerFile` for `check.ts` still holds `TS2741` with `messageArgs: ["title", "{}", "Shape"]`.

In-tree after the repair (not on failing_ref): `json module diagnostics are cleared after fixing the json file` in `tsc/internal/execute/tsctests/tsc_test.go`. JSON files use file version as shape signature.

Case A — cold run, JSON has title:
  no leftover diagnostic
  clean

Case B — warm run after removing title:
  TS2741 is the current identity
  not leftover (source really missing title)

Case C — warm run after restoring title, leftover tsbuildinfo:
  leftover: semanticDiagnosticsPerFile still TS2741
  JSON source identity is `{ "title": "fixed" }`

Case D — delete tsbuildinfo then tsc:
  fresh identity
  not leftover replay

The developer wants to know which identity case C actually left in `tsconfig.tsbuildinfo`: leftover TS2741 for `{}` while JSON has title, diagnostics cleared, or omitted (no tsbuildinfo).
""",
        observed="""# OBSERVED

Public microsoft/TypeScript#64025 (closed 2026-09-01). PR 64026 squash `13e158b131a6ec523fc6ee76376c8ff1a55451ab` (parent `5739027c9a7df24e27123f453a50c011b37717b6`). Local tsc was not performed on this lab host.

Issue body: JSON change that *introduces* the error is detected on a warm run; only clearing is broken. 5.9.3 clears; 7.0.2 / 7.1.0-dev keep leftover TS2741 until tsbuildinfo is deleted.

On failing_ref, JSON modules used empty declaration emit as shape signature. Content-hash in fileInfos updates; dependents' semanticDiagnosticsPerFile is replayed.

Using file version as JSON shape signature is **not** on the failing revision. It is added by PR 64026 (`!ast.IsJsonSourceFile(file)` before computing dts signature).

Not this packet: specimen-067 (mypy leftover). specimen-075 (rust leftover). microsoft/TypeScript#30602 (deleted js not recreated; still open). #59851 (tsbuildinfo unportable paths; still open).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 5739027c9a7df24e27123f453a50c011b37717b6
# tsc/internal/execute/incremental/affectedfileshandler.go updateShapeSignature

# public shape:
# leftover tsbuildinfo semanticDiagnosticsPerFile TS2741
# data.json on disk has title
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""microsoft/TypeScript
  tsc/internal/execute/incremental/affectedfileshandler.go
  tsc/internal/execute/tsctests/tsc_test.go
""",
        source="""repository: microsoft/TypeScript
issue: https://github.com/microsoft/TypeScript/issues/64025
pr: https://github.com/microsoft/TypeScript/pull/64026
failing_ref (squash parent / PR base): 5739027c9a7df24e27123f453a50c011b37717b6
fixed_ref (squash merge): 13e158b131a6ec523fc6ee76376c8ff1a55451ab
merged_at: 2026-09-01T19:20:39Z
pr_author: Copilot
merged_by: jakebailey
changed_files: tsc/internal/execute/incremental/affectedfileshandler.go, tsc/internal/execute/tsctests/tsc_test.go, tsc/testdata/baselines/reference/tsc/incremental/json-module-diagnostics-are-cleared-after-fixing-the-json-file.js
pr_title: Clear stale incremental diagnostics after JSON module changes
scout_note: not specimen-067/075. Distinct leftover: tsbuildinfo semanticDiagnostics vs JSON source identity. job-0460.
""",
        answer_key="""KNOWN FIX (sealed): microsoft/TypeScript PR 64026 squash 13e158b131a6ec523fc6ee76376c8ff1a55451ab.

failing_ref is squash parent 5739027c9a7df24e27123f453a50c011b37717b6.

JSON modules used empty declaration emit as shape signature, so content changes looked shape-equivalent and leftover semanticDiagnosticsPerFile was replayed.

PR repair: skip dts signature for JSON source files; use file version as shape signature so dependents re-check.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (cold clean vs warm introduce-error vs leftover replay after fix vs delete-tsbuildinfo)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — JSON content-hash identity and leftover diagnostic identity are different objects; fileInfos updated while semanticDiagnosticsPerFile replayed
ecosystem: typescript / incremental
mechanism_family: leftover-tsbuildinfo, omitted-shape-invalidation, json-module

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "update_shape_signature_failing.go": """// Reduced excerpt of updateShapeSignature on failing_ref
// tsc/internal/execute/incremental/affectedfileshandler.go
// 5739027c9a7df24e27123f453a50c011b37717b6
// JSON files have no declaration output. Empty dts is the shape signature.
// Later JSON content changes look shape-equivalent.

	info, _ := h.program.snapshot.fileInfos.Load(file.Path())
	prevSignature := info.signature
	if !file.IsDeclarationFile && !useFileVersionAsSignature {
		update.signature = h.computeDtsSignature(file)
	}
	// Default is to use file version as signature
""",
            "leftover_identity_split.txt": """Registry / fixture:
  incremental + resolveJsonModule
  check.ts imports data.json
  tsconfig.tsbuildinfo

Case A (cold, JSON has title):
  no leftover diagnostic
  clean

Case B (warm, JSON {}):
  TS2741 is current
  not leftover

Case C (warm, JSON title restored, leftover tsbuildinfo):
  leftover: semanticDiagnosticsPerFile TS2741 for {}
  JSON source has title

Case D (delete tsbuildinfo):
  fresh identity
  not leftover replay

Not this packet:
  mypy leftover (specimen-067)
  rust leftover (specimen-075)
  TypeScript#30602 deleted js (open)
""",
        },
    )


def packet_ruff(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: astral-sh/ruff
failing_ref: 90e5bc2bd95e15086a3af81589cc2a1af298b6b2
fixed_ref: a631d600acf3fa26c744ff00909f9891365e7ed4
source_issue: https://github.com/astral-sh/ruff/issues/12264
source_pr: https://github.com/astral-sh/ruff/pull/12727
mechanism_tags:
  - leftover-ruff-cache
  - nested-pyproject-identity
  - directory-route-miss
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7200
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Ruff's cache can keep the identity of **nested-directory diagnostics** after a nested `pyproject.toml` changes which rules that directory ignores. A later `ruff check .` with cache hits leftover "ignored" identity for some files in that tree; `ruff check --no-cache` names the current nested config.

On failing_ref `90e5bc2bd95e15086a3af81589cc2a1af298b6b2`, `Resolver::add` registers only `{path}/{*filepath}`:

```
self.router.insert(format!("{path}/{{*filepath}}"), self.settings.len() - 1)
```

A query by directory misses the trailing `/`. Nested `pyproject.toml` change does not invalidate cache for files whose settings lookup missed that route.

Public report (astral-sh/ruff#12264):

```
.
├── baz
│   ├── egg
│   │   └── t3.py
│   ├── pyproject.toml
│   └── t2.py
├── pyproject.toml
└── t1.py
```

All Python files `print(name)` (F821). Both pyproject.toml `[tool.ruff.lint] ignore = ["F821"]`.

1. `ruff clean`
2. `ruff check .` — no diagnostics (ignored)
3. Comment the ignore line in `baz/pyproject.toml`
4. `ruff check .` — leftover: single diagnostic for `baz/egg/t3.py`
5. `ruff check --no-cache .` — diagnostics for `baz/t2.py` and `baz/egg/t3.py`

In-tree after the repair (not on failing_ref): `Resolver::add` also `self.router.insert(path, ...)` so the directory itself matches.

Case A — `ruff clean` then check with nested ignore present:
  no leftover
  no diagnostics

Case B — nested ignore commented, leftover cache from step 2:
  leftover: t2.py still "ignored"
  t3.py may report
  nested config identity is "do not ignore F821"

Case C — `--no-cache` after the nested change:
  current nested identity
  both t2.py and t3.py

Case D — `ruff clean` then check:
  fresh identity
  not leftover cache

The developer wants to know which identity case B actually left for `baz/`: leftover ignored-F821 cache (t2.py silent), current nested diagnostics, or omitted (no cache).
""",
        observed="""# OBSERVED

Public astral-sh/ruff#12264 (closed 2024-08-07). PR 12727 squash `a631d600acf3fa26c744ff00909f9891365e7ed4` (parent `90e5bc2bd95e15086a3af81589cc2a1af298b6b2`). Also fixes #12721. Local ruff was not performed on this lab host.

Issue body: after commenting nested ignore, cached check names only t3.py; `--no-cache` names t2.py and t3.py.

On failing_ref, Resolver::add inserts `{path}/{*filepath}` only. Directory query misses. Nested pyproject.toml is not the cache identity for files whose route missed.

Inserting the directory path itself is **not** on the failing revision. It is added by PR 12727.

Not this packet: specimen-001/002/003 (pytest assertion/collection/fixture). specimen-107 (pytest leftover cache-dir without .gitignore). ruff#1589 / PR 1595 (flake8-pytest-style settings omitted from hash; different leftover: config hash, not nested directory route).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 90e5bc2bd95e15086a3af81589cc2a1af298b6b2
# crates/ruff_workspace/src/resolver.rs Resolver::add

# public shape:
# leftover cache after nested pyproject.toml ignore change
# ruff check names t3.py only
# ruff check --no-cache names t2.py and t3.py
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""astral-sh/ruff
  crates/ruff_workspace/src/resolver.rs
""",
        source="""repository: astral-sh/ruff
issue: https://github.com/astral-sh/ruff/issues/12264
pr: https://github.com/astral-sh/ruff/pull/12727
failing_ref (squash parent / PR base): 90e5bc2bd95e15086a3af81589cc2a1af298b6b2
fixed_ref (squash merge): a631d600acf3fa26c744ff00909f9891365e7ed4
merged_at: 2024-08-07T19:53:45Z
pr_author: MichaReiser
merged_by: MichaReiser
changed_files: crates/ruff_workspace/src/resolver.rs
pr_title: Fix cache invalidation for nested pyproject.toml files
scout_note: not specimen-001/002/003/107. Distinct leftover: nested pyproject identity vs leftover cache. job-0461. not ruff#1589 config-hash leftover.
""",
        answer_key="""KNOWN FIX (sealed): astral-sh/ruff PR 12727 squash a631d600acf3fa26c744ff00909f9891365e7ed4.

failing_ref is squash parent 90e5bc2bd95e15086a3af81589cc2a1af298b6b2.

Resolver::add registered only {path}/{*filepath}; directory query missed nested settings so leftover cache kept ignored-F821 identity for some files.

PR repair: also insert the directory path itself into the router.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (clean+ignore vs leftover cache after nested change vs --no-cache vs reclean)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — nested pyproject identity and leftover cache identity are different objects; directory route miss kept ignored-F821
ecosystem: python / ruff
mechanism_family: leftover-cache, nested-config, omitted-directory-route

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "resolver_add_failing.rs": """// Reduced excerpt of Resolver::add on failing_ref
// crates/ruff_workspace/src/resolver.rs
// 90e5bc2bd95e15086a3af81589cc2a1af298b6b2
// Only {path}/{*filepath} is registered. Directory query misses.

        match self
            .router
            .insert(format!("{path}/{{*filepath}}"), self.settings.len() - 1)
        {
            Ok(()) => {}
            Err(InsertError::Conflict { .. }) => {}
            Err(_) => unreachable!("file paths are escaped before being inserted in the router"),
        }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  nested baz/pyproject.toml ignore F821
  leftover ruff cache after commenting ignore

Case A (ruff clean, nested ignore present):
  no diagnostics
  no leftover

Case B (nested ignore commented, leftover cache):
  leftover: t2.py still ignored
  t3.py may report

Case C (--no-cache after nested change):
  t2.py and t3.py
  current nested identity

Case D (ruff clean then check):
  fresh identity
  not leftover cache

Not this packet:
  pytest assertion/collection/fixture (specimen-001/002/003)
  pytest leftover cache-dir without gitignore (specimen-107)
  ruff#1589 flake8-pytest-style hash (different leftover)
""",
        },
    )


def packet_task(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: go-task/task
failing_ref: 1e2121a99f6414e3bf4565e5736a116bef10be91
fixed_ref: 48039be12cdfc6b6871dbe9f1d6977027d660889
source_issue: https://github.com/go-task/task/issues/1795
source_pr: https://github.com/go-task/task/pull/1808
mechanism_tags:
  - leftover-wildcard-fingerprint
  - omitted-match-from-cache-key
  - checksum-method
ecosystem: go
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Task's checksum fingerprint can keep the identity of a **wildcard template** after two different MATCH instantiations should be different tasks. `.task/checksum/<name>` is keyed by the template name (`build-*`), so leftover checksum from `build-foo` is reused as up-to-date for `build-bar`.

On failing_ref `1e2121a99f6414e3bf4565e5736a116bef10be91`, compiled tasks keep `Task: origTask.Task` (the pattern). `Name()` / `LocalName()` do not include MATCH. `fingerprint.IsTaskUpToDate` uses that name as the cache key. Wildcard parameter is omitted from fingerprint identity.

Public report (go-task/task#1795): automatically concat the wildcard parameter on the cache key. Discussion #1794: two wildcard instantiations share one checksum.

In-tree after the repair (not on failing_ref): `FullName` replaces `*` with MATCH; `Name()` / `LocalName()` use FullName; testdata `build-*` writes `.task/checksum/build-wildcard`.

Case A — first `task build-foo` (checksum method):
  checksum written for the template name
  not leftover yet

Case B — later `task build-bar` with leftover checksum from foo:
  leftover: up-to-date identity of foo
  MATCH bar omitted from the key

Case C — non-wildcard `build` with its own checksum file:
  unique key
  not this leftover

Case D — delete `.task/checksum` then run bar:
  fresh identity
  not leftover fingerprint

The developer wants to know which identity case B actually left in `.task/checksum/`: leftover foo checksum reused as bar, separate bar checksum, or omitted (no checksum file).
""",
        observed="""# OBSERVED

Public go-task/task#1795 (closed 2025-09-11). PR 1808 squash `48039be12cdfc6b6871dbe9f1d6977027d660889` (parent `1e2121a99f6414e3bf4565e5736a116bef10be91`). Local task was not performed on this lab host.

Issue: wildcard parameter is not on the fingerprint cache key. Two MATCH instantiations share leftover checksum identity.

On failing_ref, compiledTask copies origTask.Task as the name. MATCH is a var, not the checksum key. FullName is **not** on the failing revision. It is added by PR 1808 (`fullName` replaces `*` with MATCH; `Name()` prefers FullName).

Not this packet: specimen-076/088/104 (gradle compiler fingerprints). pants leftover fingerprint (job-0464 hunt: no leftover-identity merged pair). cargo leftover (091/099/101).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 1e2121a99f6414e3bf4565e5736a116bef10be91
# variables.go compiledTask / taskfile/ast/task.go Name

# public shape:
# leftover .task/checksum/build-* from build-foo
# task build-bar reports up-to-date
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""go-task/task
  variables.go
  taskfile/ast/task.go
  testdata/checksum/Taskfile.yml
""",
        source="""repository: go-task/task
issue: https://github.com/go-task/task/issues/1795
pr: https://github.com/go-task/task/pull/1808
failing_ref (squash parent / PR base): 1e2121a99f6414e3bf4565e5736a116bef10be91
fixed_ref (squash merge): 48039be12cdfc6b6871dbe9f1d6977027d660889
merged_at: 2025-09-11T17:33:53Z
pr_author: vmaerten
merged_by: vmaerten
changed_files: variables.go, taskfile/ast/task.go, testdata/checksum/Taskfile.yml, task_test.go
pr_title: feat: improve fingerprint, run and output with wildcard
scout_note: not specimen-076/088/104. Distinct leftover: wildcard fingerprint omits MATCH. job-0464 pants hunt had no merged leftover-identity pair; packed this instead.
""",
        answer_key="""KNOWN FIX (sealed): go-task/task PR 1808 squash 48039be12cdfc6b6871dbe9f1d6977027d660889.

failing_ref is squash parent 1e2121a99f6414e3bf4565e5736a116bef10be91.

Fingerprint cache key was the wildcard template name. MATCH instantiations shared leftover checksum.

PR repair: FullName replaces * with MATCH; Name/LocalName use FullName so checksum files split per instantiation.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (first foo checksum vs leftover foo reused as bar vs non-wildcard unique vs delete checksum)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — template-name identity and MATCH instantiation identity are different objects; leftover checksum blocked bar
ecosystem: go / task
mechanism_family: leftover-fingerprint, omitted-wildcard, checksum-key

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "compiled_task_name_failing.go": """// Reduced excerpt of compiledTask / Name on failing_ref
// variables.go / taskfile/ast/task.go
// 1e2121a99f6414e3bf4565e5736a116bef10be91
// Task name is the template. MATCH is not the checksum key.

	new := ast.Task{
		Task: origTask.Task,
		// no FullName
	}

func (t *Task) Name() string {
	if t.Label != "" {
		return t.Label
	}
	return t.Task
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  tasks:
    build-*:
      method: checksum
  leftover .task/checksum from build-foo

Case A (first build-foo):
  checksum written for template name
  not leftover yet

Case B (later build-bar, leftover foo checksum):
  leftover: up-to-date identity of foo
  MATCH bar omitted

Case C (non-wildcard build):
  unique key
  not this leftover

Case D (delete .task/checksum):
  fresh identity
  not leftover fingerprint

Not this packet:
  gradle compiler fingerprints (specimen-076/088/104)
  pants leftover fingerprint (no merged pair)
""",
        },
    )


def packet_coder(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: coder/coder
failing_ref: 9a57dfa6424996d92daa18a8a5b96efcb1576a1a
fixed_ref: df278ec0795cda3af53bae17aae5108ddcfe2d69
source_issue: https://github.com/pierrecomputer/pierre/issues/1052
source_pr: https://github.com/coder/coder/pull/27987
mechanism_tags:
  - leftover-highlight-cache
  - filename-cache-key
  - omitted-patch-content
ecosystem: typescript
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Coder's diff highlighter can keep the identity of a **filename-keyed highlight AST** after a later edit of the same path has a different patch body. `@pierre/diffs` keys its worker-pool cache by `cacheKey`, which the components default to the file name when unset. Leftover AST from the first diff is reused for the second; rendering throws `deletionLine and additionLine are null`.

On failing_ref `9a57dfa6424996d92daa18a8a5b96efcb1576a1a`, `parsePatchFiles` is called without a content key. Parsed `FileDiffMetadata` has no `cacheKey`. The library assigns `cacheKey = fileDiff.name`. Two consecutive `edit_files` turns on one path share leftover highlight identity.

Public report (coder/coder#27987): two user-visible bugs from `@pierre/diffs` 1.3.x (#27932) keying the singleton worker-pool highlight cache by filename:

1. Stale-AST crash: two different diff bodies for the same path shared one cache entry.
2. Truncated synthetic diffs: N same-name file entries kept entry one.

`RemoteDiffPanel` already used a timestamp-scoped prefix; chat tool renderers and `LocalDiffPanel` parsed without one.

In-tree after the repair (not on failing_ref): `parseDiffString` stamps `cacheKey` with `getContentCacheKey` (FNV-1a of name, prevName, lang, hunks, line arrays). Unchanged files hit; changed files miss.

Case A — first diff of path `foo.ts`:
  highlight AST stored under filename
  not leftover yet

Case B — second diff of `foo.ts` with different hunks, leftover cache:
  leftover: stale AST of first body
  crash on shorter additionLines/deletionLines

Case C — content-derived cacheKey (post-repair shape, not on failing_ref):
  miss
  not leftover filename identity

Case D — different path:
  unique filename key
  not this leftover

The developer wants to know which identity case B actually left in the highlight cache: leftover first-body AST for `foo.ts`, content-keyed miss, or omitted (no cache entry).
""",
        observed="""# OBSERVED

Public coder/coder#27987 (merged 2026-08-11). Squash `df278ec0795cda3af53bae17aae5108ddcfe2d69` (parent `9a57dfa6424996d92daa18a8a5b96efcb1576a1a`). Upstream pierrecomputer/pierre#1052 tracks the throw. Local coder UI was not performed on this lab host.

PR body: parse without cacheKey → library uses filename → leftover highlight AST for a later diff of the same path. Reproduced against shipped 1.3.3 by seeding the pool cache with a first diff and rendering a second of the same path.

On failing_ref, parsePatchFiles is unkeyed. Content checksum is **not** on the failing revision. It is added by PR 27987 (`getContentCacheKey` / `stampCacheKey`).

Not this packet: specimen-090 (webpack leftover cache). specimen-094 (vitest cache key). next.js webpack cache leftover (job-0465 hunt: no merged leftover-identity pair).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 9a57dfa6424996d92daa18a8a5b96efcb1576a1a
# parsePatchFiles without cacheKey
# @pierre/diffs FileDiff.js cacheKey = fileDiff.name

# public shape:
# leftover highlight AST for foo.ts
# second diff of foo.ts throws deletionLine/additionLine null
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""coder/coder
  site/src/components/DiffViewer (parseDiff / parsePatchFiles)
""",
        source="""repository: coder/coder
issue: https://github.com/pierrecomputer/pierre/issues/1052
pr: https://github.com/coder/coder/pull/27987
failing_ref (squash parent / PR base): 9a57dfa6424996d92daa18a8a5b96efcb1576a1a
fixed_ref (squash merge): df278ec0795cda3af53bae17aae5108ddcfe2d69
merged_at: 2026-08-11T11:22:14Z
pr_author: DanielleMaywood
merged_by: DanielleMaywood
pr_title: fix: derive diff cache keys from patch content
scout_note: not specimen-090/094. Distinct leftover: highlight cache keyed by filename not patch content. job-0465 next.js webpack cache leftover had no merged pair; packed this instead.
""",
        answer_key="""KNOWN FIX (sealed): coder/coder PR 27987 squash df278ec0795cda3af53bae17aae5108ddcfe2d69.

failing_ref is squash parent 9a57dfa6424996d92daa18a8a5b96efcb1576a1a.

Unkeyed parse defaulted cacheKey to filename. Leftover highlight AST from the first diff of a path was reused for a later different body.

PR repair: stamp cacheKey from FNV-1a of that file's render inputs (name, prevName, lang, hunks, line arrays).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (first filename store vs leftover stale AST on second body vs content-keyed miss vs different path)
reproducibility: source-backed PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — filename identity and patch-content identity are different objects; leftover AST crashed the second render
ecosystem: typescript / coder diffs
mechanism_family: leftover-highlight-cache, omitted-content-key, filename-default

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "cache_key_failing.txt": """Reduced shape of unkeyed parse on failing_ref
9a57dfa6424996d92daa18a8a5b96efcb1576a1a

parsePatchFiles(diff) → FileDiffMetadata without cacheKey
@pierre/diffs FileDiff.js: cacheKey = fileDiff.name when absent
WorkerPoolManager highlight cache keyed only by that cacheKey

Two diffs of foo.ts:
  first body stored under foo.ts
  leftover: second body hits foo.ts
  processDiffResult indexes shorter additionLines/deletionLines
  throw deletionLine and additionLine are null
""",
            "leftover_identity_split.txt": """Registry / fixture:
  two edit_files turns on foo.ts
  leftover highlight cache keyed by filename

Case A (first diff of foo.ts):
  AST stored under filename
  not leftover yet

Case B (second diff, different hunks, leftover cache):
  leftover: stale first-body AST
  crash

Case C (content-derived cacheKey):
  miss
  not leftover filename identity

Case D (different path):
  unique filename key
  not this leftover

Not this packet:
  webpack leftover cache (specimen-090)
  vitest cache key (specimen-094)
  next.js webpack cache leftover (no merged pair)
""",
        },
    )


def _claim_job(state, job_id: str, worker: str) -> None:
    job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
    if job is None:
        raise SystemExit(f"{job_id} missing")
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
        if old not in {None, worker} and not str(old).startswith("scout-coord-"):
            raise SystemExit(f"{job_id} status=CLAIMED worker={old}")
        job["worker"] = worker
        job["claimed_at"] = job.get("claimed_at") or now_jst()
        workers = state.setdefault("workers", [])
        rec = next((w for w in workers if w.get("id") == worker), None)
        if rec is None:
            workers.append({"id": worker, "status": "active", "job": job_id})
        else:
            rec["status"] = "active"
            rec["job"] = job_id
        for w in workers:
            if w.get("id") != worker and w.get("job") == job_id:
                w["status"] = "vacant"
                w["job"] = None
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')} worker={job.get('worker')}")


def _register(state, spec_id: str, trial: str, reason: str) -> None:
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
            priority_reason=reason,
            specimen=spec_id,
            lineage=trial,
            phase="cambrian",
            extra={"trial": trial},
        )


def _complete_and_enqueue(ids: list[str]) -> str:
    note = {"reason": ""}
    packets = list(zip(PACKED, ids))

    def fn(state):
        for (job_id, worker, trial, reason), spec_id in packets:
            _claim_job(state, job_id, worker)
            job = next(j for j in state["ready_jobs"] if j["id"] == job_id)
            if job.get("status") == "CLAIMED" and job.get("worker") == worker:
                complete(state, job_id, artifact=f"specimens/{spec_id} {trial}")
            _register(state, spec_id, trial, reason)
        for jid, artifact in SKIP_JOBS.items():
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
            if job is None:
                continue
            if job.get("status") == "READY":
                job["status"] = "CLAIMED"
                job["worker"] = "scout-job-0458"
                job["claimed_at"] = now_jst()
                complete(state, jid, result="skip", artifact=artifact)
            elif job.get("status") == "CLAIMED":
                complete(state, jid, result="skip", artifact=artifact)
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
            )
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        if claimed_r1:
            note["reason"] = (
                "dream.sh not launched; READY_R1_DREAM already in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
            )
        else:
            note["reason"] = (
                "dream.sh not launched from scout; READY_R1_DREAM enqueued trials="
                + ",".join(t for _, _, t, _ in PACKED)
            )
        return ids

    with_state(fn)
    return note["reason"]


def main() -> None:
    ids = [_claim_id() for _ in PACKED]
    dests = [SPECIMENS / i for i in ids]
    builders = [
        packet_composer,
        packet_ts,
        packet_ruff,
        packet_task,
        packet_coder,
    ]
    try:
        for spec_id, builder in zip(ids, builders):
            emit(builder(spec_id))
            write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(ids)
        for spec_id, packed in zip(ids, PACKED):
            print(f"{spec_id} {packed[2]} {packed[0]}")
        print(launch_note)
        print("ids=" + ",".join(ids))
    except Exception:
        for dest in dests:
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
        raise


if __name__ == "__main__":
    main()
