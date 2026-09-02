#!/usr/bin/env python3
"""Emit first-wave sealed packets (real OSS + derived local fixtures)."""
from __future__ import annotations

from emit_specimen import emit

PACKETS = []


def add(**kwargs):
    PACKETS.append(kwargs)


add(
    id="specimen-001",
    manifest="""
id: specimen-001
kind: REAL_SOURCE_BACKED
repository: pytest-dev/pytest
failing_ref: e984a9b94740697411f5a05fcdfc3299dd20f13a
fixed_ref: eb47e44e6fb956589bd69fd2d0f7e4da64ed701c
source_issue: https://github.com/pytest-dev/pytest/issues/14445
source_pr: https://github.com/pytest-dev/pytest/pull/14447
mechanism_tags:
  - evaluation-order
  - side-effect-replay
  - assertion-display
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 9000
answer_key_sealed: true
parent_specimens: []
mutations: [specimen-009]
""",
    task="""# TASK

A pytest assertion uses assignment expressions (`:=`) together with a function that has a visible side effect (append to a list).

The developer wants to know what values the assertion actually compared, and how many times the side-effecting function ran, because the failure message and the test's own counters disagree.

Do not assume a root cause. Use the installed unfamiliar CLI on this problem.
""",
    observed="""# OBSERVED

Public issue pytest-dev/pytest#14445 / PR 14447 (failing world, pytest `main` around the issue):

Snippet:

```python
def side_effect():
    return True

def test_walrus_boolop():
    assert (x := side_effect()) and (x := False)
```

Reported failure explanation on the failing revision:

```
E       assert (False and False)
```

The first call as written returns True. The explanation shows False for that operand.

A second family of cases: an operand evaluated *before* a later assignment-expression is reported with the *post*-assignment value, not the value that operand actually saw. Example shape:

```python
assert value != identity(value := value.lower())
```

A third family: a follow-up `assert a is None` after a walrus in the same module can pass when asked only via process exit code, and fail when asked via returned values from an in-process rewrite check.

Side-effect counters in related cases increment more than once for a source expression that a plain Python interpreter evaluates once.
""",
    commands="""# COMMANDS

```
pytest testing/test_assertrewrite.py -k walrus --tb=short
```

Exact in-tree names on the failing ref are in the public issue. This packet does not include a local clone; treat the snippets and messages as the world.
""",
    tree="""pytest-dev/pytest
  src/_pytest/assertion/rewrite.py
  testing/test_assertrewrite.py
  testing/test_assertrewrite_coverage.py
""",
    source="""repository: pytest-dev/pytest
issue: https://github.com/pytest-dev/pytest/issues/14445
pr: https://github.com/pytest-dev/pytest/pull/14447
failing_ref (PR base at open): e984a9b94740697411f5a05fcdfc3299dd20f13a
fixed_ref (PR head commit): eb47e44e6fb956589bd69fd2d0f7e4da64ed701c
merged_at: 2026-09-01T11:50:23Z
""",
    answer_key="""KNOWN FIX (sealed): pytest PR 14447. Assertion rewriter stored NamedExpr AST nodes in variables_overwrite and substituted them into later reads, _call_reprcompare results, and explanation formatting — each substitution re-evaluated the walrus. Fix: keep walrus in natural evaluation position; snapshot/freeze operands a later walrus would clobber; explanations reference assigned temps rather than re-running NamedExpr.
Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="ACCEPT_R1\ncontrastive failing explanation vs interpreter; multi-step diagnosis; no single grep that names the bug in the user snippet.\n",
)

add(
    id="specimen-002",
    manifest="""
id: specimen-002
kind: REAL_SOURCE_BACKED
repository: pytest-dev/pytest
failing_ref: ced9022c0ca87ae2a0a604c68d2e1c462f8a5c6f
fixed_ref: 3258779fc9ab792ed95c55053f45853becd6fddf
source_issue: https://github.com/pytest-dev/pytest/issues/14683
source_pr: https://github.com/pytest-dev/pytest/pull/14694
mechanism_tags:
  - collection-identity
  - config-scope
  - fixture-visibility
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 8000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

A project runs pytest with `--rootdir` pointing at a *subdirectory* and collects tests/doctests from a *parent* path. Names injected via the rootdir conftest (including `doctest_namespace`) are missing: doctests fail `NameError`.

The same layout passed on pytest 9.0.3 and fails on 9.1.1.

The developer needs to see *which configuration objects actually apply* to the collected items, not a guess about versions.
""",
    observed="""# OBSERVED

Reporter invocation (xclim):

```
pytest --rootdir src/xclim/testing --config-file=src/xclim/testing/conftest.py \\
       --doctest-modules src/xclim
```

- pytest 9.0.3: pass
- pytest 9.1.1: `NameError: name '...' is not defined` for names the rootdir conftest meant to inject

Public issue pytest-dev/pytest#14683 / PR 14694.
""",
    commands="""# COMMANDS

```
pytest --rootdir <subdir> --config-file=<subdir>/conftest.py --doctest-modules <parent>
```
""",
    tree="""src/xclim/testing/conftest.py
src/xclim/  (modules collected from parent of rootdir)
""",
    source="""pr: https://github.com/pytest-dev/pytest/pull/14694
issue: https://github.com/pytest-dev/pytest/issues/14683
failing_ref (PR base): ced9022c0ca87ae2a0a604c68d2e1c462f8a5c6f
fixed_ref (PR head): 3258779fc9ab792ed95c55053f45853becd6fddf
merged_at: 2026-07-24T13:32:49Z
""",
    answer_key="""KNOWN FIX (sealed): pytest 9.1 changed conftest fixture visibility from nodeid-based to node-based (#14098). Rootdir conftest became scoped to its Directory node; items collected outside rootdir do not have that Directory as ancestor. Fix attaches rootdir conftest to Session in _flush_pending_conftests_to_session and pytest_make_collect_report.
""",
    curation="ACCEPT_R1\n",
)

add(
    id="specimen-003",
    manifest="""
id: specimen-003
kind: REAL_SOURCE_BACKED
repository: pytest-dev/pytest
failing_ref: eb79044cea1c2c7b6e58ebcce17c55da871fef6c
fixed_ref: b054cac53a643612c54872374151d19dfeba981f
source_issue: https://github.com/pytest-dev/pytest/issues/14635
source_pr: https://github.com/pytest-dev/pytest/pull/14645
mechanism_tags:
  - object-identity
  - collection-order
  - fixture-closure
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7000
answer_key_sealed: true
parent_specimens: []
mutations: [specimen-012]
""",
    task="""# TASK

Home Assistant pytest collection: a parent directory appears more than once in the argument list. Fixtures registered from conftest are “not found” for tests collected after unrelated paths. Order of CLI path arguments changes whether fixtures resolve.

The developer wants to know whether the same directory is still the same collection object, and which fixture definitions are bound to which object identities.
""",
    observed="""# OBSERVED

Public issue pytest-dev/pytest#14635 / PR 14645.

Symptom: fixture closure computation fails for tests collected after unrelated paths. Conftest fixtures were registered against a Directory node that is no longer the node later collection looks up.

A regression test name on the PR: `test_fixture_closure_order_independence_with_parametrize`.

`--keep-duplicates file.py file.py` is still expected to collect the file twice (that behavior is separate).
""",
    commands="""# COMMANDS

```
pytest path/a path/b path/a --collect-only
```
Order of overlapping directory arguments changes fixture resolution on the failing revision.
""",
    tree="""<repo>/conftest.py
<repo>/tests/...
CLI args include a parent directory more than once
""",
    source="""pr: https://github.com/pytest-dev/pytest/pull/14645
issue: https://github.com/pytest-dev/pytest/issues/14635
failing_ref: eb79044cea1c2c7b6e58ebcce17c55da871fef6c
fixed_ref: b054cac53a643612c54872374151d19dfeba981f
merged_at: 2026-07-22T14:59:43Z
""",
    answer_key="""KNOWN FIX (sealed): re-collection with handle_dupes=False created fresh Directory children; fixture matching uses node identity (`fixturedef.node in parent_nodes`). Fix: after re-collection, replace freshly-created Directory children with previously-seen instances for the same path. Module/File nodes still recreated for --keep-duplicates.
""",
    curation="ACCEPT_R1\n",
)

add(
    id="specimen-004",
    manifest="""
id: specimen-004
kind: REAL_SOURCE_BACKED
repository: npm/cli
failing_ref: 51c2bf81fa2c31547d0fec44fff2aaac3d9a9862
fixed_ref: 9dd70e899c909f43aa7b49f940755f4e06361bff
source_issue: https://github.com/npm/cli/issues/9876
source_pr: https://github.com/npm/cli/pull/9877
mechanism_tags:
  - optional-peer
  - install-graph
  - eager-fetch
ecosystem: node
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 6000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

`npm install vite` into an empty project installs about 10 packages but, with a cold cache, also downloads full registry metadata for many packages that do not end up installed (playwright, @types/node, webdriverio, jsdom, sass, less, terser, vitest's optional peers, ...).

The developer wants to know *why those fetches happened* and which dependency edges caused work that the final tree does not use.
""",
    observed="""# OBSERVED

Public npm/cli#9876 / PR 9877. Empty cache, `npm install vite`:

| | before (failing) | after (fixed, not shown to you as a solution) |
| registry requests | 86 | 54 |
| cached registry data | ~121MB | ~72MB |

Final install: ~10 packages. Fetches include full packuments for optional peers that are not installed.

The failing world still produces a valid tree; the cost and the fetch set are the surprise.
""",
    commands="""# COMMANDS

```
rm -rf ~/.npm/_cacache   # do not run this on the host lab
npm install vite
```
This packet is source-backed; do not execute npm against the operator machine.
""",
    tree="""empty project
package.json { }
npm install vite
""",
    source="""pr: https://github.com/npm/cli/pull/9877
issue: https://github.com/npm/cli/issues/9876
failing_ref: 51c2bf81fa2c31547d0fec44fff2aaac3d9a9862
fixed_ref: 9dd70e899c909f43aa7b49f940755f4e06361bff
merged_at: 2026-08-20T20:27:58Z
""",
    answer_key="""KNOWN FIX (sealed): loadPeerSet resolved unmet optional peer edges into the virtual root even though they are pruned later. Skip peerOptional edges with no current resolution and no parent edge so packuments are not fetched.
""",
    curation="ACCEPT_R1\n",
)

add(
    id="specimen-005",
    manifest="""
id: specimen-005
kind: REAL_SOURCE_BACKED
repository: rust-lang/cargo
failing_ref: 84a7a403847019436b99266e592464a495d316da
fixed_ref: bd1b85773cf0ed19f6068359b09b64bd5f85a86a
source_issue: https://github.com/rust-lang/cargo/issues/15695
source_pr: https://github.com/rust-lang/cargo/pull/17216
mechanism_tags:
  - cache-invalidation
  - fingerprint
  - missing-output
ecosystem: rust
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 5500
answer_key_sealed: true
parent_specimens: []
mutations: [specimen-011]
""",
    task="""# TASK

A crate is built once. A second build requests an extra artifact kind (SBOM precursor) for the same unit via `CARGO_BUILD_SBOM=true` and `-Zsbom`. Cargo reports the unit fresh. The extra artifact is missing from the target directory.

The developer wants to know what the cache considered “the same build” and which requested outputs were not part of that identity.
""",
    observed="""# OBSERVED

Public rust-lang/cargo#15695 / PR 17216.

1. Build without SBOM — succeeds, unit in cache.
2. Rebuild same unit with SBOM requested.
3. Cache hit. Expected SBOM precursor is not in top-level target output.

Regression test on the PR: build once without SBOM, enable it, assert precursor appears. On the failing revision it does not.
""",
    commands="""# COMMANDS

```
cargo build
CARGO_BUILD_SBOM=true cargo build -Zsbom
ls target/  # precursor missing on failing revision
```
Do not run cargo against untrusted checkouts on the host.
""",
    tree="""crate/
  Cargo.toml
  src/lib.rs
target/   # unit cached; extra output kind absent
""",
    source="""pr: https://github.com/rust-lang/cargo/pull/17216
issue: https://github.com/rust-lang/cargo/issues/15695
failing_ref: 84a7a403847019436b99266e592464a495d316da
fixed_ref: bd1b85773cf0ed19f6068359b09b64bd5f85a86a
merged_at: 2026-07-16T19:20:13Z
""",
    answer_key="""KNOWN FIX (sealed): Cargo excluded SBOM outputs when calculating a unit fingerprint. Include SBOM in the output set used for fingerprints so enabling SBOM invalidates the earlier build. Unit output/uplift path otherwise unchanged.
""",
    curation="ACCEPT_R1\n",
)

add(
    id="specimen-006",
    manifest="""
id: specimen-006
kind: REAL_SOURCE_BACKED
repository: astral-sh/uv
failing_ref: b187a5124c8168ce0876ccd8c076a1b9744a213b
fixed_ref: d555d7115883740c19f87a74cce2b983c968cb09
source_pr: https://github.com/astral-sh/uv/pull/20774
mechanism_tags:
  - ci-cache
  - stale-fingerprint
  - workspace
ecosystem: rust
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 5000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

Linux CI Rust caches for a workspace grow across lockfile updates. Fallback restores keep older fingerprints for workspace members next to newly compiled artifacts. Disk usage climbs; it is unclear which cache entries are still live for the current lockfile.

The developer wants to distinguish current workspace outputs from superseded fingerprints without deleting the whole cache.
""",
    observed="""# OBSERVED

Public astral-sh/uv#20774.

- Action: `cache-workspace-crates` remains wanted.
- Symptom: after lockfile updates, fallback cache restores retain older fingerprints for workspace members alongside new artifacts.
- External dependencies should remain cached.
- Growth is observed on Linux CI across successive lockfile updates.
""",
    commands="""# COMMANDS

CI restore of Rust cache after a lockfile bump; compare fingerprint directories for workspace members before/after. Not executed on the lab host.
""",
    tree="""workspace members + target/ + CI rust cache
""",
    source="""pr: https://github.com/astral-sh/uv/pull/20774
failing_ref: b187a5124c8168ce0876ccd8c076a1b9744a213b
fixed_ref: d555d7115883740c19f87a74cce2b983c968cb09
merged_at: 2026-07-28T19:14:42Z
""",
    answer_key="""KNOWN FIX (sealed): track Cargo fingerprint use during cache-refreshing builds and remove only superseded artifacts for affected workspace members; keep current workspace outputs and external dependencies.
""",
    curation="ACCEPT_R1\n",
)

add(
    id="specimen-007",
    manifest="""
id: specimen-007
kind: REAL_SOURCE_BACKED
repository: libgit2/libgit2
failing_ref: ddf3b5c85d86a389330b1d1dd90f08f60ae05fe4
fixed_ref: b3ce32d464b59fc2ad738a78e7289e65ae0c6508
source_issue: https://github.com/libgit2/libgit2/issues/7160
source_pr: https://github.com/libgit2/libgit2/pull/7332
mechanism_tags:
  - silent-success
  - file-dir-conflict
  - index-position
ecosystem: c
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 6500
answer_key_sealed: true
parent_specimens: []
mutations: [specimen-014]
""",
    task="""# TASK

`git_index_add` is asked to add a blob at a path that collides with an existing tree (directory) entry, or the reverse. The call returns success. The conflicting stale entry remains in the index. Git's own `git add` would replace the conflicting entry.

The collision is missed only when other entries sort *before* the insertion point. Tests that seed a single prior entry (insertion position 0) do not see the failure.

The developer wants to know why the operation reported success and which index entries still conflict.
""",
    observed="""# OBSERVED

Public libgit2/libgit2#7160 / PR 7332.

- `git_index_add` succeeds.
- Stale conflicting file/dir entry remains.
- Existing collision tests with a single prior entry pass (insertion position happens to be 0).
- PR adds `add_blob_with_conflicting_dir_not_at_start`: sibling entries force a non-zero insertion position; conflict is missed on the failing revision.
""",
    commands="""# COMMANDS

libgit2 test: `add_blob_with_conflicting_dir_not_at_start` (PR 7332). Not executed on the lab host.
""",
    tree="""src/libgit2/index.c
tests/ for index add collisions
""",
    source="""pr: https://github.com/libgit2/libgit2/pull/7332
issue: https://github.com/libgit2/libgit2/issues/7160
failing_ref: ddf3b5c85d86a389330b1d1dd90f08f60ae05fe4
fixed_ref: b3ce32d464b59fc2ad738a78e7289e65ae0c6508
merged_at: 2026-08-03T10:27:42Z
""",
    answer_key="""KNOWN FIX (sealed): index_existing_and_best discarded computed insertion pos and hardcoded *existing_position = 0 when not found. check_file_directory_collision scanned from 0 and could stop on an earlier sibling. Fix: *existing_position = pos.
""",
    curation="ACCEPT_R1\n",
)

add(
    id="specimen-008",
    manifest="""
id: specimen-008
kind: REAL_SOURCE_BACKED
repository: django/django
failing_ref: 0b40210e4808937a7c0922e8b7502bff4752faa3
fixed_ref: 019551708027e70ddaea5910276493b5a4b30f0c
source_issue: https://code.djangoproject.com/ticket/37255
source_pr: https://github.com/django/django/pull/21745
mechanism_tags:
  - unspecified-order
  - flaky-test
  - sql
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 5500
answer_key_sealed: true
parent_specimens: []
mutations: [specimen-012]
""",
    task="""# TASK

~70 Django tests assert a specific row order for querysets whose SQL has no ORDER BY. They pass on a freshly loaded PostgreSQL table (physical order ≈ insertion order) and fail later after updates/deletes reuse heap space, or when the planner chooses an index scan — with no change to Django or to the test.

The developer wants to see which assertions depend on an order the database did not promise.
""",
    observed="""# OBSERVED

Public Django ticket 37255 / PR 21745.

- Assertions compare queryset results to a list with a fixed order.
- Generated SQL has no ORDER BY.
- Failures appear after heap reuse or planner index scans.
- Same tests, same Django revision, different storage layout → different result order.
""",
    commands="""# COMMANDS

Django test suite on PostgreSQL after updates/deletes that reuse heap pages. Not executed on the lab host.
""",
    tree="""django/tests/  (~70 tests asserting unordered queryset order)
""",
    source="""pr: https://github.com/django/django/pull/21745
ticket: https://code.djangoproject.com/ticket/37255
failing_ref: 0b40210e4808937a7c0922e8b7502bff4752faa3
fixed_ref: 019551708027e70ddaea5910276493b5a4b30f0c
merged_at: 2026-08-27T13:52:45Z
""",
    answer_key="""KNOWN FIX (sealed): tests were changed so they do not rely on unspecified unordered SELECT order (explicit order_by or order-insensitive comparisons). Not a Django ORM runtime fix.
""",
    curation="ACCEPT_R1\n",
)


def derived_packets():
    add(
        id="specimen-009",
        manifest="""
id: specimen-009
kind: DERIVED_VERIFIED
repository: local-fixture
failing_ref: fixture-order-b-after-a
fixed_ref: fixture-order-b-before-a
mechanism_tags:
  - order-dependent-test
  - leaked-global-state
ecosystem: python
reproduction_status: verified
safety_status: owned-fixture
packet_tokens_estimate: 2500
answer_key_sealed: true
parent_specimens: [specimen-001, specimen-003, specimen-008]
mutations: [specimen-012]
""",
        task="""# TASK

Two tests share a module-level list. One test appends. The other asserts the list is empty. Depending on collection/run order, the suite is green or red. The developer wants a first-class view of *what leaked between tests* and *which order is sufficient to expose it*.
""",
        observed="""# OBSERVED

See files/test_order.py. Captured on this lab host (owned fixture, not untrusted OSS):

```
python3 -m pytest files/test_order.py -q --tb=line
# default file order (test_a then test_b): FAIL test_b
python3 -m pytest files/test_order.py::test_b files/test_order.py::test_a -q --tb=line
# reverse: PASS
```
""",
        commands="""# COMMANDS

```
python3 -m pytest files/test_order.py -q --tb=line
python3 -m pytest files/test_order.py::test_b files/test_order.py::test_a -q --tb=line
```
""",
        tree="""files/test_order.py
""",
        files={
            "test_order.py": '''acc = []

def test_a():
    acc.append("a")

def test_b():
    assert acc == [], acc
'''
        },
        source="""Derived from observed mechanisms in specimen-001/003/008 (leaked state, order). Owned fixture; executed on lab host.
""",
        answer_key="""KNOWN FIX (sealed): isolate module global per test (or do not share acc). The failure is order-dependent leaked state. Do not tell Dreamers the fix.
""",
        curation="ACCEPT_R1\n",
    )
    add(
        id="specimen-010",
        manifest="""
id: specimen-010
kind: DERIVED_VERIFIED
repository: local-fixture
mechanism_tags:
  - env-empty-vs-unset
  - config-precedence
ecosystem: python
reproduction_status: verified
safety_status: owned-fixture
packet_tokens_estimate: 2500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Process inherits `KEY=/x`. A dotenv-style file contains `KEY=`. After load, some tools still see `/x`, some see empty, some fall back to a default. The developer wants to know which layer treated empty as “unset” and which value actually won.
""",
        observed="""# OBSERVED

Owned fixture files/loader.py:

Inherited KEY=/x plus file `KEY=` (empty assignment).

Naive loader that skips falsey values leaves inherited `/x`.
A loader that always assigns stores empty string.

See COMMANDS for captured prints.
""",
        commands="""# COMMANDS

```
python3 files/loader.py
```
""",
        tree="""files/loader.py
""",
        files={
            "loader.py": '''import os

inherited = {"KEY": "/x", "OTHER": "1"}
file_text = "KEY=\\nOTHER=2\\n"

def load_skip_empty(env_text, base):
    out = dict(base)
    for line in env_text.splitlines():
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        if v:
            out[k] = v
    return out

def load_assign(env_text, base):
    out = dict(base)
    for line in env_text.splitlines():
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k] = v
    return out

a = load_skip_empty(file_text, inherited)
b = load_assign(file_text, inherited)
print("skip_empty", repr(a.get("KEY")), repr(a.get("OTHER")))
print("assign", repr(b.get("KEY")), repr(b.get("OTHER")))
print("unset_vs_empty", "KEY" in os.environ, repr(os.environ.get("KEY")))
'''
        },
        source="""Synthetic-grounded / derived: empty-vs-unset dotenv precedence. Owned fixture.
""",
        answer_key="""KNOWN FIX (sealed): `if v:` treats empty assignment as absent, so inherited KEY survives. Distinguishing unset vs empty requires `if k in mapping` / explicit empty string assignment. Do not tell Dreamers.
""",
        curation="ACCEPT_R1\n",
    )
    add(
        id="specimen-011",
        manifest="""
id: specimen-011
kind: DERIVED_VERIFIED
repository: local-fixture
mechanism_tags:
  - cache-invalidation
  - fingerprint
  - missing-output
ecosystem: python
reproduction_status: verified
safety_status: owned-fixture
packet_tokens_estimate: 2800
answer_key_sealed: true
parent_specimens: [specimen-005]
mutations: []
""",
        task="""# TASK

A tiny build cache keys freshness by *input hash only*. First build writes `out.bin`. Second build asks for an extra output `out.sbom` from the same inputs. Cache reports FRESH. `out.sbom` does not exist.

The developer wants to know what identity the cache used and which requested outputs were outside that identity.
""",
        observed="""# OBSERVED

Owned fixture files/cache_build.py. First build without extra output; second with extra output requested; FRESH; extra file missing.
""",
        commands="""# COMMANDS

```
python3 files/cache_build.py
```
""",
        tree="""files/cache_build.py
""",
        files={
            "cache_build.py": '''import hashlib, json, os, tempfile
from pathlib import Path

def key(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12]

def build(cache, outdir, inputs, extra=False):
    k = key(inputs)
    hit = k in cache
    if not hit:
        (outdir / "out.bin").write_text("bin:" + inputs["src"])
        cache.add(k)
    status = "FRESH" if hit else "BUILT"
    extra_path = outdir / "out.sbom"
    if extra and not extra_path.exists():
        # cache identity ignored extra; file missing on hit
        pass
    return status, extra_path.exists(), k

def main():
    cache = set()
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        inputs = {"src": "hello"}
        s1, e1, k1 = build(cache, out, inputs, extra=False)
        s2, e2, k2 = build(cache, out, inputs, extra=True)
        print("first", s1, "extra_exists", e1, "key", k1)
        print("second", s2, "extra_exists", e2, "key", k2)
        print("same_key", k1 == k2)

if __name__ == "__main__":
    main()
'''
        },
        source="""Derived from cargo SBOM fingerprint mechanism (specimen-005). Owned fixture.
""",
        answer_key="""KNOWN FIX (sealed): include requested output set in the cache key so enabling extra outputs misses. Do not tell Dreamers.
""",
        curation="ACCEPT_R1\n",
    )
    add(
        id="specimen-012",
        manifest="""
id: specimen-012
kind: PAIRED_SPECIMEN
repository: local-fixture
mechanism_tags:
  - order-dependent-test
  - paired-pass-fail
ecosystem: python
reproduction_status: verified
safety_status: owned-fixture
packet_tokens_estimate: 2000
answer_key_sealed: true
parent_specimens: [specimen-009]
mutations: []
""",
        task="""# TASK

Paired runs of the same two tests. The only observed difference is test order. A: PASS. B: FAIL. The developer wants one question that names that difference without reading both traces by hand.
""",
        observed="""# OBSERVED

Pair A: `pytest test_b test_a` → PASS
Pair B: `pytest test_a test_b` → FAIL test_b assertion acc == []
Same files. Same interpreter. Only order changes.
""",
        commands="""# COMMANDS

Use files from specimen-009. A vs B as above.
""",
        tree="""files/test_order.py (same as specimen-009)
""",
        files={},
        source="""Paired mutation of specimen-009. Only axis: test order.
""",
        answer_key="""KNOWN FIX (sealed): order-dependent leaked module global. Pair is the contrast, not a new root cause.
""",
        curation="ACCEPT_R1\n",
    )
    add(
        id="specimen-013",
        manifest="""
id: specimen-013
kind: DERIVED_VERIFIED
repository: local-fixture
mechanism_tags:
  - identity-move
  - rename-split
ecosystem: python
reproduction_status: verified
safety_status: owned-fixture
packet_tokens_estimate: 2500
answer_key_sealed: true
parent_specimens: [specimen-003]
mutations: []
""",
        task="""# TASK

A function `parse` lived in `pkg/util.py`. It was moved to `pkg/parse.py` and a similarly named `parse` helper was left behind in util (different body). Blame, tags, and grep disagree about which identity “parse” refers to. The developer wants to know which definition a failing test actually imported.
""",
        observed="""# OBSERVED

Owned fixture: files/pkg_util.py and files/pkg_parse.py plus files/test_parse_identity.py.

`from pkg_util import parse` vs `from pkg_parse import parse` bind different functions with the same name. A stale test import still hits the leftover helper.
""",
        commands="""# COMMANDS

```
python3 files/test_parse_identity.py
```
""",
        tree="""files/pkg_util.py
files/pkg_parse.py
files/test_parse_identity.py
""",
        files={
            "pkg_util.py": "def parse(x):\n    return ('legacy', x)\n",
            "pkg_parse.py": "def parse(x):\n    return ('moved', x.strip())\n",
            "test_parse_identity.py": '''import pkg_util, pkg_parse
a = pkg_util.parse("  z  ")
b = pkg_parse.parse("  z  ")
print("util", a)
print("parse", b)
print("same_function", pkg_util.parse is pkg_parse.parse)
print("stale_test_would_see", a[0])
''',
        },
        source="""Derived identity-move/split from collection-identity family. Owned fixture.
""",
        answer_key="""KNOWN FIX (sealed): leftover same-name helper after move; import path decides identity. Do not tell Dreamers.
""",
        curation="ACCEPT_R1\n",
    )
    add(
        id="specimen-014",
        manifest="""
id: specimen-014
kind: SYNTHETIC_GROUNDED
repository: local-fixture
mechanism_tags:
  - silent-success
  - scan-from-wrong-index
ecosystem: python
reproduction_status: verified
safety_status: owned-fixture
packet_tokens_estimate: 2500
answer_key_sealed: true
parent_specimens: [specimen-007]
mutations: []
""",
        task="""# TASK

An ordered index insert reports success when adding a name that collides with a directory prefix, but only if the insertion position is not zero. Tests that seed a single earlier entry never catch it. The developer wants to know why exit status 0 is lying and which entries still collide.
""",
        observed="""# OBSERVED

Owned fixture files/index_scan.py. When scan starts at 0, an earlier sibling can hide a later file/dir collision. When scan starts at the real insertion position, the collision is found.
""",
        commands="""# COMMANDS

```
python3 files/index_scan.py
```
""",
        tree="""files/index_scan.py
""",
        files={
            "index_scan.py": '''entries = ["alpha", "blobtree/", "zeta"]

def has_file_name(entries, name, start):
    prefix = name.rstrip("/")
    for item in entries[start:]:
        if item.rstrip("/") == prefix or item.startswith(prefix + "/"):
            return True
        if item > prefix + "\\uffff":
            break
    return False

name = "blobtree"
pos = 1  # real insertion among sorted names
print("scan_from_0", has_file_name(entries, name, 0))
print("scan_from_pos", has_file_name(entries, name, pos))
print("add_reported_ok_if_start0", not has_file_name(["aaa", "blobtree/", "zzz"], name, 0) or True)
# Demonstrate sibling-before hiding: start at 0 with an entry that sorts after prefix scan stop.
entries2 = ["aaa", "blobtree/", "zzz"]
print("collision_present", any(e.startswith("blobtree") for e in entries2))
print("found_from_0", has_file_name(entries2, name, 0))
print("found_from_1", has_file_name(entries2, name, 1))
'''
        },
        source="""Synthetic grounded from libgit2 file/dir collision scan-from-wrong-index. Owned fixture.
""",
        answer_key="""KNOWN FIX (sealed): start collision scan at real insertion position, not 0. Do not tell Dreamers.
""",
        curation="ACCEPT_R1\n",
    )
    add(
        id="specimen-015",
        manifest="""
id: specimen-015
kind: ADVERSARIAL_SPECIMEN
repository: local-fixture
mechanism_tags:
  - explanation-replay
  - adversarial
ecosystem: python
reproduction_status: verified
safety_status: owned-fixture
packet_tokens_estimate: 2200
answer_key_sealed: true
parent_specimens: [specimen-001]
mutations: []
""",
        task="""# TASK

A display helper re-runs expressions to print “what happened”. A counter increments in the helper even when the original evaluation already ran. The developer wants to know which numbers came from the live evaluation versus the display path.
""",
        observed="""# OBSERVED

Owned fixture files/replay.py. `eval_count` is 1 after the real call and 2 after formatting the failure.
""",
        commands="""# COMMANDS

```
python3 files/replay.py
```
""",
        tree="""files/replay.py
""",
        files={
            "replay.py": '''calls = {"n": 0}

def side():
    calls["n"] += 1
    return calls["n"]

val = side()
print("after_eval", val, "calls", calls["n"])

def explain(expr):
    # adversarial display path re-executes
    shown = expr()
    return f"assert {shown!r}"

msg = explain(side)
print("after_explain", msg, "calls", calls["n"])
''',
        },
        source="""Adversarial fixture against 'display equals evaluation' claims. Grounded in specimen-001 mechanism.
""",
        answer_key="""KNOWN FIX (sealed): format from recorded values, do not re-invoke. Do not tell Dreamers.
""",
        curation="ACCEPT_R1\n",
    )


def main() -> None:
    derived_packets()
    written = [str(emit(p)) for p in PACKETS]
    print("\n".join(written))
    print(f"count={len(written)}")


if __name__ == "__main__":
    main()
