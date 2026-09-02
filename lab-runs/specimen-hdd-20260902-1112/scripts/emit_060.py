#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packets specimen-060..069. Never overwrite existing."""
from __future__ import annotations

from emit_specimen import emit
from compile_seed import write_seed
from paths import SPECIMENS
from update_index import main as update_index

PACKETS = []


def add(**kwargs):
    PACKETS.append(kwargs)


add(
    id="specimen-060",
    manifest="""
id: specimen-060
kind: REAL_SOURCE_BACKED
repository: pypa/setuptools
failing_ref: bb1b38189eed960bdb4f4789926472d05e43d335
fixed_ref: 72e919a8b10aaafc041205d4e3ae0e6a2e1e5f87
source_pr: https://github.com/pypa/setuptools/pull/5293
mechanism_tags:
  - archive-entry-order
  - first-basename-match
  - nested-pyproject
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 6500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

Setuptools integration job `test_install_sdist[pip-v.LATEST]` fails while installing pip's sdist with `--no-build-isolation`.

Metadata generation dies with:

```
pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'flit_core.buildapi'
```

The sdist contains more than one file named `pyproject.toml`. `build_deps("pip", sdist)` returns an empty list, so flit-core is never installed into the venv that then tries to import the backend.

The developer wants to know *which archive member* `_read_pyproject` actually returned, and how that member relates to the project's own build-system table.
""",
    observed="""# OBSERVED

Public pypa/setuptools PR 5293. Failing world around tagged setuptools v84.0.0 integration tests after pip 26.2.1's sdist layout changed.

pip 26.2.1 sdist members (order as stored in the archive):

```
pip-26.2.1/build-project/pyproject.toml   # first basename match; no [build-system]
pip-26.2.1/pyproject.toml                 # project metadata; requires flit-core
```

`pip-26.2.1/pyproject.toml` contains:

```
[build-system]
requires = ["flit-core >=3.11,<4"]
build-backend = "flit_core.buildapi"
```

`pip-26.2.1/build-project/pyproject.toml` has no `[build-system]` table.

On the failing revision, `_read_pyproject` does:

```
contents = (
    archive.get_content(member)
    for member in archive
    if os.path.basename(archive.get_name(member)) == "pyproject.toml"
)
return next(contents, "")
```

`build_deps` then `tomllib.loads` that string and reads `info.get("build-system", {}).get("requires", [])`.

The same helper is inert for sdists that ship a single `pyproject.toml`. The pip sdist is the first popular example with a nested helper of the same basename appearing *earlier* in the archive than the project file.

CI installs the sdist with `--no-build-isolation`, so the test itself must pre-install whatever `_read_pyproject` reports. Empty requires → backend import fails before compile.

This packet does not include a local clone; treat the snippets and CI message as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
# CI job: tests / integration-test
#   test_install_sdist[pip-v.LATEST]
pytest setuptools/tests/integration/test_pip_install_sdist.py -k 'pip-v.LATEST'
# helper under study:
#   build_deps("pip", sdist_file) -> []
#   _read_pyproject(archive) -> first basename "pyproject.toml"
```

Not executed on this lab host.
""",
    tree="""pypa/setuptools
  setuptools/tests/integration/test_pip_install_sdist.py
pip-26.2.1 sdist (not in-tree)
  pip-26.2.1/build-project/pyproject.toml
  pip-26.2.1/pyproject.toml
""",
    source="""repository: pypa/setuptools
pr: https://github.com/pypa/setuptools/pull/5293
failing_ref (merge first parent): bb1b38189eed960bdb4f4789926472d05e43d335
fixed_ref (merge commit): 72e919a8b10aaafc041205d4e3ae0e6a2e1e5f87
head_sha: 1b2970113fd6cda8d4bcac5a1ef6ff865bff62ee
merged_at: 2026-08-08T18:04:59Z
merged_by: jaraco
changed_files: setuptools/tests/integration/test_pip_install_sdist.py
""",
    answer_key="""KNOWN FIX (sealed): pypa/setuptools PR 5293 merge 72e919a8b10aaafc041205d4e3ae0e6a2e1e5f87.

_read_pyproject used next() on basename==pyproject.toml, so pip 26.2.1's earlier build-project/ helper (no build-system table) won over the top-level file that requires flit-core. Repair: pick the member with the fewest '/' in its archive name (shallowest path), i.e. {name}-{version}/pyproject.toml.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (two same-basename archive members; first-in-iteration vs project root; empty requires vs flit-core)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — failure looks like a missing backend, but the real question is which nested file the archive walker treated as canonical
ecosystem: python / setuptools
mechanism_family: archive-entry-order, first-basename-match, nested-pyproject

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "read_pyproject_failing.py": '''# Reduced excerpt of _read_pyproject on failing_ref
# setuptools/tests/integration/test_pip_install_sdist.py

def _read_pyproject(archive):
    contents = (
        archive.get_content(member)
        for member in archive
        if os.path.basename(archive.get_name(member)) == "pyproject.toml"
    )
    return next(contents, "")
''',
        "sdist_members.txt": """pip-26.2.1 sdist member order (relevant names only):
pip-26.2.1/build-project/pyproject.toml
pip-26.2.1/pyproject.toml
""",
        "nested_pyproject.toml": """# pip-26.2.1/build-project/pyproject.toml — no [build-system]
[project]
name = "build-project-helper"
""",
        "root_pyproject.toml": '''# pip-26.2.1/pyproject.toml
[build-system]
requires = ["flit-core >=3.11,<4"]
build-backend = "flit_core.buildapi"
''',
    },
)

add(
    id="specimen-061",
    manifest="""
id: specimen-061
kind: REAL_SOURCE_BACKED
repository: tox-dev/tox
failing_ref: 96e2d7149291901e253abff9a090176d5716c3f1
fixed_ref: f31ebedc7e0e93516f850dbfea247355ccf198df
source_pr: https://github.com/tox-dev/tox/pull/4053
mechanism_tags:
  - hyphen-as-range
  - factor-expansion
  - silent-split
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

A tox envlist names `py313-django4-2`. Tox never creates that environment. It creates `py313-django4`, `3`, and `2` instead, and says nothing.

A second envlist `py310-1,py310-2` expands into hundreds of environments, counting down from 310.

Documented generative ranges such as `{2-4}` and `py3{10-11}` are still supposed to expand.

The same expander sits behind `-e` on the CLI, behind generative section names, and behind factor conditions.

The developer wants to know *which substrings tox treated as ranges*, and which environment names actually exist after expansion.
""",
    observed="""# OBSERVED

Public tox-dev/tox PR 4053. Failing world around `src/tox/config/loader/ini/factor.py` `expand_ranges`.

On the failing revision the expander matches:

```
( \\d+ ) - ( \\d+ )   # closed range: start-end
|
( \\d+ ) -           # right-open range: start-
|
(?<= [{,] ) - ( \\d+ )  # left-open range: -end (preceded by { or ,)
```

anywhere in the env expression, not only inside `{…}` and not only where a new factor begins.

Observed expansions (failing revision):

| written | produced |
| --- | --- |
| `py313-django4-2` | `py313-django4`, `3`, `2` (the intended name never appears) |
| `py310-1,py310-2` | a few hundred names, counting down from 310 |
| `{2-4}` | `{2,3,4}` (wanted) |
| `py3{10-11}` | `py310`, `py311` (wanted) |
| `3.10-2` | split; the dotted version-shaped name does not survive |

No error is raised. Tox proceeds with the expanded list.

This packet does not include a local clone; treat the snippets as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
tox list -e py313-django4-2
# or unit:
pytest tests/config/loader/ini/test_factor.py -k expand_ranges
```

Not executed on this lab host.
""",
    tree="""tox-dev/tox
  src/tox/config/loader/ini/factor.py
  tests/config/loader/ini/test_factor.py
  docs/reference/config.rst
""",
    source="""repository: tox-dev/tox
pr: https://github.com/tox-dev/tox/pull/4053
failing_ref (squash parent): 96e2d7149291901e253abff9a090176d5716c3f1
fixed_ref (squash commit): f31ebedc7e0e93516f850dbfea247355ccf198df
head_sha: 21819660b895acbbb650c433c8370f1d44d45a91
merged_at: 2026-08-31T18:20:42Z
merged_by: gaborbernat
changed_files: src/tox/config/loader/ini/factor.py, tests/config/loader/ini/test_factor.py, docs/reference/config.rst, docs/changelog/4053.bugfix.rst
""",
    answer_key="""KNOWN FIX (sealed): tox-dev/tox PR 4053 squash f31ebedc7e0e93516f850dbfea247355ccf198df.

expand_ranges treated any digit-hyphen-digit run as a generative range, so a factor tail such as django4-2 became 4-2. Repair: require (?<![\\w.]) before a closed/right-open range so a range may only open a factor. Left-open {-13} stays narrower ((?<=[{,])) so py3{10-11}-2,x does not swallow the trailing -2.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (py313-django4-2 silently becomes three envs; braced {2-4} still expands as documented)
reproducibility: source-backed PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — hyphen is both a factor separator and a range operator; the failure is a missing environment with no parse error
ecosystem: python / tox
mechanism_family: hyphen-as-range, factor-expansion, silent-split

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "expand_ranges_failing.py": r'''# Reduced excerpt of expand_ranges on failing_ref
# src/tox/config/loader/ini/factor.py

return re.sub(
    r"""
    (                       # outer capture group
        ( \d+ ) - ( \d+ )   # closed range: start-end
        |
        ( \d+ ) -           # right-open range: start-
        |
        (?<= [{,] ) - ( \d+ )  # left-open range: -end (preceded by { or ,)
        |
        \d+                 # single number
    )
    (?: , | \} )            # followed by comma or closing brace
    """,
    _expand,
    value,
    flags=re.VERBOSE,
)
''',
        "observed_expansions.txt": """written: py313-django4-2
produced: py313-django4 , 3 , 2
missing:  py313-django4-2

written: py310-1,py310-2
produced: hundreds of names counting down from 310

written: {2-4}
produced: {2,3,4}   (still wanted)

written: py3{10-11}
produced: py310, py311   (still wanted)
""",
    },
)

add(
    id="specimen-062",
    manifest="""
id: specimen-062
kind: REAL_SOURCE_BACKED
repository: pytest-dev/pytest-xdist
failing_ref: dd198c35710f22b1cb86b7fc00311f9b7c63d665
fixed_ref: 63f908d5ebc041654475597c3f2d6f1ee3da2c8f
source_issue: https://github.com/pytest-dev/pytest-xdist/issues/1323
source_pr: https://github.com/pytest-dev/pytest-xdist/pull/1324
mechanism_tags:
  - worker-replacement
  - hang-after-crash
  - completed-work-requeued
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

pytest-xdist with `--dist=loadgroup` hangs after a worker is replaced. Other distribution modes finish.

A two-test file, one worker, faulthandler killing the worker mid-run:

```
pytest -n1 --dist=loadgroup -o faulthandler_timeout=1 -o faulthandler_exit_on_timeout=true testing/test_timeout.py
```

Observed log, then stall:

```
replacing crashed worker gw0
collecting: 1/2 workers
collecting: 1/2 workers
2 workers [2 items]
```

The developer wants to know which work units were put back on the queue after the crash, which of those units were already completed, and why the replacement worker never finishes.
""",
    observed="""# OBSERVED

Public pytest-dev/pytest-xdist#1323 / PR 1324. LoadScopeScheduling (`src/xdist/scheduler/loadscope.py`) is shared by `--dist=loadscope` and `--dist=loadgroup`.

Reporter file:

```
def test_1():
    assert True

def test_2():
    import time
    time.sleep(5)
    assert True
```

On the failing revision, `remove_node` after a crash does:

```
# Made uncompleted work unit available again
self.workqueue.update(workload)
```

`workload` is the crashed node's entire assigned dict: scope → {nodeid: completed_bool}. `update` puts *every* scope back, including scopes whose tests are already True.

Later `_assign_work_unit` pops a scope and builds:

```
nodeids_indexes = [
    worker_collection.index(nodeid)
    for nodeid, completed in work_unit.items()
    if not completed
]
node.send_runtest_some(nodeids_indexes)
```

If the requeued unit has only completed items, `nodeids_indexes` is empty. `send_runtest_some([])` leaves the replacement worker waiting. Remote side hangs in `xdist/remote.py` around the runtest-some receive.

A PR acceptance case uses `os._exit(1)` in `test_b` after `test_a` passed, `-n1 --dist=loadgroup`. On the failing revision that suite never finishes.

This packet does not include a local clone; treat the snippets and hang as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
pytest -n1 --dist=loadgroup testing/test_timeout.py
# PR acceptance name:
#   test_loadgroup_does_not_hang_after_restart
```

Not executed on this lab host.
""",
    tree="""pytest-dev/pytest-xdist
  src/xdist/scheduler/loadscope.py
  src/xdist/remote.py
  testing/acceptance_test.py
""",
    source="""repository: pytest-dev/pytest-xdist
issue: https://github.com/pytest-dev/pytest-xdist/issues/1323
pr: https://github.com/pytest-dev/pytest-xdist/pull/1324
failing_ref (merge first parent): dd198c35710f22b1cb86b7fc00311f9b7c63d665
fixed_ref (merge commit): 63f908d5ebc041654475597c3f2d6f1ee3da2c8f
head_sha: c5a55e7f41ccf3c92c92aab565884cfedcef1b1b
merged_at: 2026-08-27T05:05:33Z
merged_by: RonnyPfannschmidt
changed_files: src/xdist/scheduler/loadscope.py, testing/acceptance_test.py, changelog/1323.bugfix.rst
""",
    answer_key="""KNOWN FIX (sealed): pytest-dev/pytest-xdist PR 1324 merge 63f908d5ebc041654475597c3f2d6f1ee3da2c8f.

remove_node requeued the whole assigned workload, including scopes whose tests were already True. The replacement then received send_runtest_some([]) and hung. Repair: requeue a scope only if any(not completed); _assign_work_unit raises RuntimeError if a unit has no pending indexes.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (loadgroup hangs after replace; other dist modes finish; empty runtest-some vs pending crashitem)
reproducibility: source-backed issue + PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — crash recovery reintroduces finished work, then the worker waits forever on an empty unit
ecosystem: python / pytest-xdist
mechanism_family: worker-replacement, hang-after-crash, completed-work-requeued

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "remove_node_failing.py": '''# Reduced excerpt of LoadScopeScheduling on failing_ref
# src/xdist/scheduler/loadscope.py

# inside remove_node, after identifying crashitem:
# Made uncompleted work unit available again
self.workqueue.update(workload)

# inside _assign_work_unit:
nodeids_indexes = [
    worker_collection.index(nodeid)
    for nodeid, completed in work_unit.items()
    if not completed
]
node.send_runtest_some(nodeids_indexes)
''',
        "hang_log.txt": """replacing crashed worker gw0
collecting: 1/2 workers
collecting: 1/2 workers
2 workers [2 items]
# suite never finishes under --dist=loadgroup
""",
    },
)

add(
    id="specimen-063",
    manifest="""
id: specimen-063
kind: REAL_SOURCE_BACKED
repository: NixOS/nix
failing_ref: 067097f63a5f8f3b63abcf99ec0146944db2d747
fixed_ref: 4750701db3802868445276c1a09c2f065a5a4bc6
source_pr: https://github.com/NixOS/nix/pull/16391
mechanism_tags:
  - detached-HEAD
  - ref-fallback
  - identity-vs-rev
ecosystem: nix
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

CI checks out a merge commit (detached HEAD) and evaluates `builtins.fetchGit` with a pinned `rev`. Fetch fails with a `narHash` mismatch. The log first says it could not read HEAD and used `master`.

```
warning: could not read HEAD ref from repo at '/workspace/build/buildkite', using 'master'
error:
       … while fetching the input 'git+file:///workspace/build/buildkite?rev=e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa'
       error: mismatch in field 'narHash' of input '{...,"narHash":"sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=","rev":"e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa",...}', got '{...,"narHash":"sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=","ref":"master","rev":"e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa",...}'
```

The two records share `rev` and `lastModified` and `revCount`. They disagree on `narHash` and on whether `ref` is present.

The developer wants to know which ref the fetcher actually resolved for a fully pinned revision, and how that ref changed the tree that was hashed.
""",
    observed="""# OBSERVED

Public NixOS/nix PR 16391. Failing world in `GitInputScheme::getDefaultRef` (`src/libfetchers/git.cc`).

On the failing revision:

```
auto head = std::visit(
    overloaded{
        [&](const std::filesystem::path & path) { return GitRepo::openRepo(path, {})->getWorkdirRef(); },
        [&](const ParsedURL & url) { return readHeadCached(settings, url.to_string(), shallow); }},
    repoInfo.location);
if (!head) {
    warn("could not read HEAD ref from repo at '%s', using 'master'", repoInfo.locationToArg());
    return "master";
}
return *head;
```

A local `git+file://` input with `rev=` still goes through this default-ref path. Detached HEAD makes `getWorkdirRef()` empty; the fallback name is the literal `master`.

The lock/input record without `ref` hashed to `sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=`. Re-fetch after guessing `master` hashed to `sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=` and inserted `"ref":"master"` while keeping the same `rev`.

In-tree `tests/functional/fetchGit.sh` already checks out a fetched rev (detached) and evaluates `builtins.fetchGit { url = ... }` without `rev`. The pinned-`rev` plus missing-HEAD warning is the CI case.

This packet does not include a local clone; treat the snippets and warning as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
nix eval --raw --expr '(builtins.fetchGit { url = $TEST_ROOT/minimal; rev = "<rev2>"; }).outPath'
# failing revision also emits:
#   could not read HEAD ref from repo at '...', using 'master'
```

Not executed on this lab host.
""",
    tree="""NixOS/nix
  src/libfetchers/git.cc
  tests/functional/fetchGit.sh
""",
    source="""repository: NixOS/nix
pr: https://github.com/NixOS/nix/pull/16391
failing_ref (merge first parent): 067097f63a5f8f3b63abcf99ec0146944db2d747
fixed_ref (merge commit): 4750701db3802868445276c1a09c2f065a5a4bc6
head_sha: c34d30cfb277ec8ac684765bde2f49f2666e47fc
merged_at: 2026-08-31T14:54:03Z
merged_by: Mic92
changed_files: src/libfetchers/git.cc, tests/functional/fetchGit.sh
""",
    answer_key="""KNOWN FIX (sealed): NixOS/nix PR 16391 merge 4750701db3802868445276c1a09c2f065a5a4bc6.

getDefaultRef treated a missing workdir ref as 'master' even when rev already identified the commit. Detached CI checkouts then fetched a different tree (narHash mismatch, extra ref field). Repair: getWorkdirRef().value_or("HEAD") for path locations so pinned inputs without an explicit ref record HEAD instead of guessing master.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (same rev, two narHashes; warning names master; lock record gains a ref field)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — a fully pinned git revision still consults HEAD, then a guessed branch name changes the hashed tree
ecosystem: nix
mechanism_family: detached-HEAD, ref-fallback, identity-vs-rev

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "getDefaultRef_failing.cc": r"""// Reduced excerpt of GitInputScheme::getDefaultRef on failing_ref
// src/libfetchers/git.cc

auto head = std::visit(
    overloaded{
        [&](const std::filesystem::path & path) { return GitRepo::openRepo(path, {})->getWorkdirRef(); },
        [&](const ParsedURL & url) { return readHeadCached(settings, url.to_string(), shallow); }},
    repoInfo.location);
if (!head) {
    warn("could not read HEAD ref from repo at '%s', using 'master'", repoInfo.locationToArg());
    return "master";
}
return *head;
""",
        "narhash_mismatch.txt": """warning: could not read HEAD ref from repo at '/workspace/build/buildkite', using 'master'
error: mismatch in field 'narHash' of input
  expected: sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=  (no ref field)
  got:      sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=  (ref=master)
rev in both records: e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa
""",
    },
)

add(
    id="specimen-064",
    manifest="""
id: specimen-064
kind: REAL_SOURCE_BACKED
repository: pre-commit/pre-commit
failing_ref: 9143fc35457adb0a2d28022b1149b131c40c0490
fixed_ref: cb63a5cb9a1f22342d7450315cb4daffe72f6c21
source_pr: https://github.com/pre-commit/pre-commit/pull/3535
mechanism_tags:
  - cgroup-v2
  - docker-in-docker
  - false-host
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 8000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

A docker language hook runs from inside a container (CI docker-in-docker / cgroup v2). pre-commit binds `-v <cwd>:/src`. The path it passes as the source is the *in-container* cwd, not the host path Docker would actually mount from.

On cgroup v1 hosts the same hook remaps cwd through `docker inspect` of the current container. On cgroup v2 it behaves as if it were not in Docker at all.

The developer wants to know which `/proc` file decided “we are / are not in Docker”, which container id (if any) was read, and which path ended up in the `-v` flag.
""",
    observed="""# OBSERVED

Public pre-commit/pre-commit PR 3535. Failing world in `pre_commit/languages/docker.py`.

On the failing revision:

```
def _is_in_docker() -> bool:
    try:
        with open('/proc/1/cgroup', 'rb') as f:
            return b'docker' in f.read()
    except FileNotFoundError:
        return False

def _get_container_id() -> str:
    with open('/proc/1/cgroup', 'rb') as f:
        for line in f.readlines():
            if line.split(b':')[1] == b'cpuset':
                return os.path.basename(line.split(b':')[2]).strip().decode()
    raise RuntimeError('Failed to find the container ID in /proc/1/cgroup.')
```

`_get_docker_path` returns the original path unless `_is_in_docker()` is true, then inspects that id and rewrites cwd through matching Mounts.

cgroup v1 `/proc/1/cgroup` (reduced) contains `docker/<64-hex>` on many controllers, including `cpuset`.

cgroup v2 `/proc/1/cgroup` is typically a single line, e.g.:

```
0::/system.slice/containerd.service
```

That line has no `docker` bytes and no `cpuset` controller field. `_is_in_docker()` is False; `_get_container_id` is not reached. `docker_cmd` therefore emits `-v <container-cwd>:/src`.

`/proc/1/mountinfo` on the same cgroup v2 container still shows a host bind of `/var/lib/docker/containers/<64-hex>/hostname` onto `/etc/hostname` (and podman overlay-containers analog).

This packet does not include a local clone; treat the snippets as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
# inside the CI container, before a docker-language hook:
cat /proc/1/cgroup
cat /proc/1/mountinfo
# hook effectively runs:
#   docker run --rm -v <cwd>:/src --workdir /src ...
```

Not executed on this lab host.
""",
    tree="""pre-commit/pre-commit
  pre_commit/languages/docker.py
  tests/languages/docker_test.py
""",
    source="""repository: pre-commit/pre-commit
pr: https://github.com/pre-commit/pre-commit/pull/3535
failing_ref (merge first parent): 9143fc35457adb0a2d28022b1149b131c40c0490
fixed_ref (merge commit): cb63a5cb9a1f22342d7450315cb4daffe72f6c21
head_sha: f80801d75a429d5eafa1d87e9f88f73b108d1890
merged_at: 2025-11-08T20:45:53Z
merged_by: asottile
changed_files: pre_commit/languages/docker.py, tests/languages/docker_test.py
""",
    answer_key="""KNOWN FIX (sealed): pre-commit/pre-commit PR 3535 merge cb63a5cb9a1f22342d7450315cb4daffe72f6c21.

_is_in_docker / _get_container_id keyed on /proc/1/cgroup containing b'docker' and a cpuset controller line. cgroup v2 has neither, so docker-in-docker path remap was skipped. Repair: parse /proc/1/mountinfo for /containers(/overlay-containers)?/<64-hex>(/userdata)?/hostname and use that id; if absent, treat as host.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (cgroup v1 remaps via inspect; cgroup v2 pretends to be the host; mountinfo still names the container id)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — “am I in Docker?” is answered from a proc file that changed shape under cgroup v2, so bind-mount rewrite silently does not happen
ecosystem: python / pre-commit
mechanism_family: cgroup-v2, docker-in-docker, false-host

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "docker_detect_failing.py": '''# Reduced excerpt on failing_ref
# pre_commit/languages/docker.py

def _is_in_docker() -> bool:
    try:
        with open('/proc/1/cgroup', 'rb') as f:
            return b'docker' in f.read()
    except FileNotFoundError:
        return False

def _get_container_id() -> str:
    with open('/proc/1/cgroup', 'rb') as f:
        for line in f.readlines():
            if line.split(b':')[1] == b'cpuset':
                return os.path.basename(line.split(b':')[2]).strip().decode()
    raise RuntimeError('Failed to find the container ID in /proc/1/cgroup.')
''',
        "cgroup_v1.excerpt": """5:cpuset:/docker/c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
1:name=systemd:/docker/c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
0::/system.slice/containerd.service
""",
        "cgroup_v2.excerpt": """0::/system.slice/containerd.service
""",
        "mountinfo_v2.hostname.excerpt": """730 721 8:3 /var/lib/docker/containers/c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7/hostname /etc/hostname rw,relatime - ext4 /dev/sda3 rw,errors=remount-ro
""",
    },
)

add(
    id="specimen-065",
    manifest="""
id: specimen-065
kind: REAL_SOURCE_BACKED
repository: moby/moby
failing_ref: 1d3cc314b614e53e4b56141dd64108a3fbec5267
fixed_ref: 69b8083c9ba419d30e60f8232e4e1dbe9e7a25db
source_issue: https://github.com/moby/moby/issues/46747
source_pr: https://github.com/moby/moby/pull/52317
mechanism_tags:
  - timer-sleep-past-deadline
  - start-interval-vs-period
  - healthcheck-cadence
ecosystem: go
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 6500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

A container healthcheck is configured with a short start period and a long start interval:

```
StartPeriod: 2s
StartInterval: 30s
Interval: 2s
Retries: 1
Test: ["CMD", "/bin/false"]
```

The container becomes `unhealthy` about 30s after start. Expected: unhealthy within one regular `Interval` after `StartPeriod` ends (~4s).

The developer wants to know which timer the health monitor actually armed while status was still `starting`, and when that timer fired relative to the end of the start period.
""",
    observed="""# OBSERVED

Public moby/moby#46747 / PR 52317. Failing world in `daemon/health.go` `monitor` → `getInterval`.

On the failing revision:

```
getInterval := func() time.Duration {
    if time.Since(started) >= startPeriod {
        return probeInterval
    }
    c.Lock()
    status := c.State.Health.Health.Status
    c.Unlock()

    if status == containertypes.Starting {
        return startInterval
    }
    return probeInterval
}
```

`monitor` does `intervalTimer := time.NewTimer(getInterval())` and later `intervalTimer.Reset(getInterval())`.

When `HealthStartPeriod` < `HealthStartInterval` and the container is still `starting`, `getInterval` returns the full `startInterval` (30s) even if only 2s of start period remain. The monitor sleeps past the start-period boundary, then eventually applies `probeInterval`.

Failing streak / `unhealthy` is computed in `handleProbeResult`: while status is `starting` and `timeSinceStart < startPeriod`, failures do not increment the streak. After the period, one failing probe with `Retries: 1` is enough.

This packet does not include a local clone; treat the snippets and timing as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
# container Healthcheck:
#   StartPeriod=2s StartInterval=30s Interval=2s Retries=1 Test=CMD /bin/false
docker inspect --format '{{.State.Health.Status}}' <id>
# failing revision: unhealthy ~30s after start
# expected: unhealthy within ~Interval after StartPeriod
```

Not executed on this lab host.
""",
    tree="""moby/moby
  daemon/health.go
""",
    source="""repository: moby/moby
issue: https://github.com/moby/moby/issues/46747
pr: https://github.com/moby/moby/pull/52317
failing_ref (merge first parent): 1d3cc314b614e53e4b56141dd64108a3fbec5267
fixed_ref (merge commit): 69b8083c9ba419d30e60f8232e4e1dbe9e7a25db
head_sha: 3e545a67d28fe34d4b9d2fb2c1678d656855197d
merged_at: 2026-09-01T14:25:08Z
merged_by: vvoland
milestone: 29.8.0
changed_files: daemon/health.go
""",
    answer_key="""KNOWN FIX (sealed): moby/moby PR 52317 merge 69b8083c9ba419d30e60f8232e4e1dbe9e7a25db.

getInterval returned the full StartInterval whenever status was still starting, even if that sleep overran StartPeriod. Repair: while starting, if startInterval > remaining start-period time, return remaining so the monitor wakes at the period boundary and then uses the regular probe interval.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (StartPeriod 2s vs StartInterval 30s; unhealthy at ~30s vs ~4s; timer armed with startInterval while starting)
reproducibility: source-backed issue + PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — two clocks (start period vs start interval) and the monitor only consults “are we past the period *now*”, not “will this sleep land past it”
ecosystem: go / moby
mechanism_family: timer-sleep-past-deadline, start-interval-vs-period, healthcheck-cadence

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "getInterval_failing.go": """// Reduced excerpt of monitor/getInterval on failing_ref
// daemon/health.go

getInterval := func() time.Duration {
    if time.Since(started) >= startPeriod {
        return probeInterval
    }
    c.Lock()
    status := c.State.Health.Health.Status
    c.Unlock()

    if status == containertypes.Starting {
        return startInterval
    }
    return probeInterval
}
""",
        "repro_timing.txt": """StartPeriod: 2s
StartInterval: 30s
Interval: 2s
Retries: 1
Test: CMD /bin/false
observed unhealthy: ~30s after start
expected unhealthy: within one Interval after StartPeriod (~4s)
""",
    },
)

add(
    id="specimen-066",
    manifest="""
id: specimen-066
kind: REAL_SOURCE_BACKED
repository: python/mypy
failing_ref: 1dab3c5f3d4cf8a3df88e5bcccfd6f3194fbd66f
fixed_ref: 44c0d9f1efc39af78da28fced51261b022252fec
source_issue: https://github.com/python/mypy/issues/21866
source_pr: https://github.com/python/mypy/pull/21888
mechanism_tags:
  - identity-loss
  - generic-substitution
  - sentinel-literal
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

A PEP 661 sentinel is passed as `dict.get`'s default. mypy infers the result as `str | sentinel` (the shared class), not `str | Unknown` (the value).

```
from typing import assert_type
from typing_extensions import sentinel

Unknown = sentinel("Unknown")

def func(d: dict[str, str]) -> None:
    var = d.get("key", Unknown)
    assert_type(var, str | Unknown)
```

```
test.py:8: error: Expression is of type "str | sentinel", not "str | Unknown"  [assert-type]
```

A sibling case: `ALIAS = MISSING` then `assert_type(ALIAS, sentinel)` passes on the failing revision, and `func(ALIAS)` is rejected as type `Sentinel` rather than `MISSING`.

The developer wants to know which identity the checker kept after substituting the TypeVar in `dict.get`, and where the literal attached to `Unknown` went.
""",
    observed="""# OBSERVED

Public python/mypy#21866 / PR 21888. Failing world around `mypy/expandtype.py` `visit_type_var` and `test-data/unit/check-sentinels.test`.

`dict.get` is overloaded with a TypeVar default. Substituting `Unknown` (an `Instance` whose `last_known_value` is the sentinel literal) hits:

```
repl = self.variables.get(t.id, t)
if isinstance(repl, ProperType) and isinstance(repl, Instance):
    # TODO: do we really need to do this?
    # If I try to remove this special-casing ~40 tests fail on reveal_type().
    return repl.copy_modified(last_known_value=None)
```

After that copy, the type prints as the fallback class name `sentinel` / `Sentinel`, not `Unknown`.

In-tree `testSentinelReassignmentIsNotTypeAlias` on the failing revision:

```
MISSING = sentinel("MISSING")
ALIAS = MISSING
assert_type(ALIAS, sentinel)
func(ALIAS)  # E: Argument 1 to "func" has incompatible type "Sentinel"; expected "int | MISSING"
```

`reveal_type` on a bare sentinel value is supposed to show the value's name (e.g. `Unknown?`), while the class `sentinel` remains the type of the constructor.

This packet does not include a local clone; treat the snippets and error as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
mypy test.py
# in-tree:
pytest mypy/test/testcheck.py -k sentinels
```

Not executed on this lab host.
""",
    tree="""python/mypy
  mypy/expandtype.py
  mypy/erasetype.py
  mypy/messages.py
  test-data/unit/check-sentinels.test
""",
    source="""repository: python/mypy
issue: https://github.com/python/mypy/issues/21866
pr: https://github.com/python/mypy/pull/21888
failing_ref (squash parent): 1dab3c5f3d4cf8a3df88e5bcccfd6f3194fbd66f
fixed_ref (squash commit): 44c0d9f1efc39af78da28fced51261b022252fec
head_sha: 1e752e217cab2e40cb732f7855fbe69844c11b14
merged_at: 2026-08-27T06:38:25Z
merged_by: sobolevn
changed_files: mypy/expandtype.py, mypy/erasetype.py, mypy/messages.py, test-data/unit/check-sentinels.test
""",
    answer_key="""KNOWN FIX (sealed): python/mypy PR 21888 squash 44c0d9f1efc39af78da28fced51261b022252fec.

TypeVar expansion and last-known-value erasure stripped Instance.last_known_value unconditionally, collapsing every PEP 661 sentinel to the shared class. Repair: if last_known_value.is_sentinel_literal(), keep the Instance as-is in expandtype, erasetype, union formatting, and error messages so dict.get(..., Unknown) stays str | Unknown.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (str|Unknown vs str|sentinel; ALIAS rejected as Sentinel; enum members already keep class identity)
reproducibility: source-backed issue + PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — a sentinel's only identity is the attached literal, and generic substitution throws that literal away
ecosystem: python / mypy
mechanism_family: identity-loss, generic-substitution, sentinel-literal

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "visit_type_var_failing.py": '''# Reduced excerpt of TypeExpander.visit_type_var on failing_ref
# mypy/expandtype.py

repl = self.variables.get(t.id, t)
if isinstance(repl, ProperType) and isinstance(repl, Instance):
    # TODO: do we really need to do this?
    # If I try to remove this special-casing ~40 tests fail on reveal_type().
    return repl.copy_modified(last_known_value=None)
return repl
''',
        "dict_get_sentinel.py": '''from typing import assert_type
from typing_extensions import sentinel

Unknown = sentinel("Unknown")

def func(d: dict[str, str]) -> None:
    var = d.get("key", Unknown)
    assert_type(var, str | Unknown)
    # failing revision:
    # error: Expression is of type "str | sentinel", not "str | Unknown"  [assert-type]
''',
    },
)

add(
    id="specimen-067",
    manifest="""
id: specimen-067
kind: REAL_SOURCE_BACKED
repository: pnpm/pnpm
failing_ref: 00cb5f977a20ab1a3858427d0309db4aab7145d4
fixed_ref: 22d0067d3786ed9892432d962428269fa91c7495
source_issue: https://github.com/pnpm/pnpm/issues/14417
source_pr: https://github.com/pnpm/pnpm/pull/14420
mechanism_tags:
  - env-name-not-shell-identifier
  - shell-shim-sanitization
  - posix-exec
ecosystem: node
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

`pnpm runtime set node --global` on Unix puts a `node` on PATH. Launching it drops environment entries whose names are not valid shell identifiers.

```
env 'TEST-VAR=123' node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
# outputs MISSING
```

The real Node binary at the managed store path, invoked the same way, prints `123`.

GitHub/Gitea/Forgejo Actions pass parameters as kebab-case env names (`INPUT-FOO`). Self-hosted runners using this `node` see those inputs as missing.

The TypeScript CLI's global Node link on Unix already preserves those names. The pacquet (Rust) Unix entry does not.

The developer wants to know which process actually exec'd Node, and which environment names survived that hop.
""",
    observed="""# OBSERVED

Public pnpm/pnpm#14417 / PR 14420. Failing world: pacquet Unix global `node` is a POSIX shell shim (`# pnpm-shim-style=context-aware`, contains `--shim 'node'`). Windows already used a native dispatcher plus sibling target file `.pnpm-shim-v1-node-target`.

POSIX (Dash) initializes shell variables from the environment only when the name is a valid identifier. Names with `-` are unspecified for inheritance into the child. The shim's `exec` therefore launches Node without `TEST-VAR`.

Direct execution of the managed binary (same inode as the store copy) inherits the full environment, including `TEST-VAR=123`.

Reporter container:

```
docker run -it --rm ghcr.io/pnpm/pnpm
pnpm runtime set node 24 -g
env 'TEST-VAR=123' node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
# MISSING
env 'TEST-VAR=123' ${REAL_NODE} -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
# 123
```

In-tree failing assertion shape (Unix): the global `node` file is readable as text and contains `--shim 'node'` / `# pnpm-shim-style=context-aware`.

This packet does not include a local clone; treat the snippets as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
pnpm runtime set node 24 -g
env 'TEST-VAR=123' node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
file "$(command -v node)"
head "$(command -v node)"
```

Not executed on this lab host.
""",
    tree="""pnpm/pnpm
  pnpm/crates/cli/src/shim_dispatch.rs
  pnpm/crates/cmd-shim/src/link_bins.rs
  pnpm/crates/cli/tests/suite/global.rs
""",
    source="""repository: pnpm/pnpm
issue: https://github.com/pnpm/pnpm/issues/14417
pr: https://github.com/pnpm/pnpm/pull/14420
failing_ref (squash parent): 00cb5f977a20ab1a3858427d0309db4aab7145d4
fixed_ref (squash commit): 22d0067d3786ed9892432d962428269fa91c7495
head_sha: f996b0f0cf7af39a10b2d1c723b74893b17bc3d1
merged_at: 2026-09-01T23:47:04Z
merged_by: zkochan
changed_files: pnpm/crates/cli/src/shim_dispatch.rs, pnpm/crates/cli/src/shim_dispatch/native_node.rs, pnpm/crates/cli/src/cli_args/global.rs, pnpm/crates/cmd-shim/src/link_bins.rs, pnpm/crates/cli/tests/suite/global_shims.rs
""",
    answer_key="""KNOWN FIX (sealed): pnpm/pnpm PR 14420 squash 22d0067d3786ed9892432d962428269fa91c7495.

Pacquet's Unix global node was a POSIX shell shim; Dash dropped env names that are not shell identifiers before exec. Repair: use the native dispatcher already used on Windows (argv0-detected, fallback path in .pnpm-shim-v1-node-target) on Unix as well, so Node inherits TEST-VAR and Actions kebab-case inputs.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (shim node loses TEST-VAR; real binary keeps it; TS CLI Unix link already preserves names)
reproducibility: source-backed issue + PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — the bug is not “env was unset” but “the name is not a shell identifier, so the shim never forwarded it”
ecosystem: node / pnpm
mechanism_family: env-name-not-shell-identifier, shell-shim-sanitization, posix-exec

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "unix_node_shim.excerpt.sh": """#!/bin/sh
# pnpm-shim-style=context-aware
# Reduced shape of the Unix global `node` entry on the failing revision.
# A POSIX shell only copies env names that are valid identifiers into
# its own variable table before exec.
exec /pnpm/global/v11/.../node_modules/node/bin/node --shim 'node' "$@"
""",
        "repro_env.txt": """env 'TEST-VAR=123' node -e 'console.log(process.env["TEST-VAR"] ?? "MISSING")'
# via PATH node (shell shim): MISSING
# via REAL_NODE (managed binary): 123
""",
    },
)

add(
    id="specimen-068",
    manifest="""
id: specimen-068
kind: REAL_SOURCE_BACKED
repository: actions/checkout
failing_ref: 12cd2235efa0937479335606d7c3ac9f6c0973b1
fixed_ref: 28802689a136bfcdb721715abd713740beecbe07
source_issue: https://github.com/actions/checkout/issues/2528
source_pr: https://github.com/actions/checkout/pull/2530
mechanism_tags:
  - regex-unescaped-path
  - git-config-unset
  - stale-includeif
ecosystem: typescript
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 6500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

`actions/checkout` v7 on a self-hosted Windows runner writes `includeIf.gitdir:...path` entries pointing at a temp credentials config:

```
includeIf.gitdir:C:/runner/_work/repo/repo/.git.path C:\\runner\\_work\\_temp\\git-credentials-.config
```

Post-job cleanup runs the equivalent of:

```
git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\\runner\\_work\\_temp\\git-credentials-.config
```

Git prints:

```
error: invalid pattern: C:\\runner\\_work\\_temp\\git-credentials-.config
```

The workflow can still conclude successfully. A later checkout on the same worktree sees the leftover `includeIf` and repeats the error.

The developer wants to know which git config *value* cleanup tried to match, whether that value was treated as a regex, and which `includeIf` entries remained.
""",
    observed="""# OBSERVED

Public actions/checkout#2528 / PR 2530. Failing world in `src/git-command-manager.ts` `tryConfigUnsetValue`.

On the failing revision:

```
args.push('--unset', configKey, configValue)
const output = await this.execGit(args, true)
return output.exitCode === 0
```

Git's `git config --unset <name> <value-pattern>` treats the third argument as a regular expression. Native Windows paths contain `\\`. `\\` is an invalid regex escape here, so git reports `error: invalid pattern` and does not remove the entry.

`tryConfigUnsetValue` passes `true` as the allow-failure flag to `execGit`, so a nonzero git exit becomes a boolean false rather than a thrown failure. Cleanup continues.

Sibling helper `tryConfigUnset` uses `--unset-all` with only the key (no value pattern).

v5.0.1 on the same runner does not take this v7 credential-layout cleanup path; no invalid-pattern message and no leftover includeIf.

This packet does not include a local clone; treat the snippets and git error as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\\runner\\_work\\_temp\\git-credentials-.config
# error: invalid pattern: C:\\runner\\_work\\_temp\\git-credentials-.config
git config --local --get-regexp includeif
```

Not executed on this lab host.
""",
    tree="""actions/checkout
  src/git-command-manager.ts
  dist/index.js
""",
    source="""repository: actions/checkout
issue: https://github.com/actions/checkout/issues/2528
pr: https://github.com/actions/checkout/pull/2530
failing_ref (squash parent): 12cd2235efa0937479335606d7c3ac9f6c0973b1
fixed_ref (squash commit): 28802689a136bfcdb721715abd713740beecbe07
head_sha: f43caed52ea5cf4d1e99a107aa92b2e9afde46cb
merged_at: 2026-07-17T17:44:41Z
merged_by: aiqiaoy
changed_files: src/git-command-manager.ts, dist/index.js
""",
    answer_key="""KNOWN FIX (sealed): actions/checkout PR 2530 squash 28802689a136bfcdb721715abd713740beecbe07.

tryConfigUnsetValue passed the Windows credentials path to git config --unset as a raw value-pattern. Git compiled it as a regex; backslashes made the pattern invalid, so includeIf entries were not removed. Repair: regexpHelper.escape(configValue) before --unset.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (Windows backslash path vs git value-regex; cleanup returns success-shaped false; leftover includeIf on next run)
reproducibility: source-backed issue + PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — cleanup looks like it matched an exact path, but git interpreted the path as a regex and then swallowed the error
ecosystem: typescript / actions
mechanism_family: regex-unescaped-path, git-config-unset, stale-includeif

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "tryConfigUnsetValue_failing.ts": """// Reduced excerpt on failing_ref
// src/git-command-manager.ts

async tryConfigUnsetValue(
  configKey: string,
  configValue: string,
  globalConfig?: boolean,
  configFile?: string
): Promise<boolean> {
  const args = ['config']
  if (configFile) {
    args.push('--file', configFile)
  } else {
    args.push(globalConfig ? '--global' : '--local')
  }
  args.push('--unset', configKey, configValue)
  const output = await this.execGit(args, true)
  return output.exitCode === 0
}
""",
        "cleanup_error.txt": """git config --local --unset includeif.gitdir:C:/runner/_work/repo/repo/.git.path C:\\runner\\_work\\_temp\\git-credentials-.config
error: invalid pattern: C:\\runner\\_work\\_temp\\git-credentials-.config
""",
    },
)

add(
    id="specimen-069",
    manifest="""
id: specimen-069
kind: REAL_SOURCE_BACKED
repository: NixOS/nix
failing_ref: aa9d7cdc4a913fc4ced56af5f12cfffbed5141d7
fixed_ref: 3ffa8b11e4720a80bc01fa502ad9a74c49f9abc1
source_pr: https://github.com/NixOS/nix/pull/16373
mechanism_tags:
  - pointer-identity
  - bind-temporary
  - silent-skip
ecosystem: nix
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 6500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

`nix flake prefetch-inputs` on a flake with 232 lock nodes (170 unique inputs) prints only about 150 `fetching` activities. A different subset is missing each run. The command still exits 0.

The walker deduplicates lock nodes by address in a `std::set<const Node *> done`. Work is queued with `std::bind`.

The developer wants to know which node identities were inserted into `done`, whether those addresses still named the same lock nodes when the worker ran, and which inputs were therefore never fetched.
""",
    observed="""# OBSERVED

Public NixOS/nix PR 16373 (`src/nix/flake-prefetch-inputs.cc`). Failing world:

```
struct State { std::set<const Node *> done; };
Sync<State> state_;

auto visit = [&](this const auto & visit, const Node & node) {
    if (!state_.lock()->done.insert(&node).second)
        return;
    // fetch lockedNode...
    for (auto & [inputName, input] : node.inputs) {
        if (auto inputNode = std::get_if<0>(&input))
            pool.enqueue(std::bind(visit, **inputNode));
    }
};

pool.enqueue(std::bind(visit, *flake.lockFile.root));
pool.process();
throw Exit(nrFailed ? 1 : 0);
```

`std::bind(visit, **inputNode)` decay-copies the `Node` argument. `visit` then takes `const Node &` bound to that copy inside the bind object. `done.insert(&node)` records the address of the copy.

When that work item finishes, a later bind object can occupy the same stack/heap address. `done.insert(&node)` then reports the new node as already visited. Those inputs are never fetched. `nrFailed` stays 0, so the process exits success.

Observed: 232 lock nodes / 170 unique inputs; ~150 `fetching` log lines; missing set changes across runs.

This packet does not include a local clone; treat the snippets as the world. Do not execute untrusted checkouts on the host.
""",
    commands="""# COMMANDS

```
nix flake prefetch-inputs
# compare logger 'fetching' activities to unique inputs in flake.lock
```

Not executed on this lab host.
""",
    tree="""NixOS/nix
  src/nix/flake-prefetch-inputs.cc
""",
    source="""repository: NixOS/nix
pr: https://github.com/NixOS/nix/pull/16373
related: https://github.com/Mic92/nixbot/issues/153
failing_ref (merge first parent): aa9d7cdc4a913fc4ced56af5f12cfffbed5141d7
fixed_ref (merge commit): 3ffa8b11e4720a80bc01fa502ad9a74c49f9abc1
head_sha: f0008d095dad1554de5f54233f8b5b3541865a89
merged_at: 2026-08-27T11:09:08Z
merged_by: xokdvium
changed_files: src/nix/flake-prefetch-inputs.cc
""",
    answer_key="""KNOWN FIX (sealed): NixOS/nix PR 16373 merge 3ffa8b11e4720a80bc01fa502ad9a74c49f9abc1.

std::bind decay-copied the Node; done.insert(&node) stored the address of that temporary. After the bind object died, a later copy could reuse the address and be treated as already visited, silently skipping fetches while still exiting 0. Repair: enqueue lambdas that capture the actual lock-graph pointer and call visit(*inputNode) / visit(*root) by reference.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (same lock file, different missing inputs each run; exit 0; done set keyed by pointer to a bind copy)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — dedup looks correct if you think &node is the lock-graph node; it is the address of a temporary
ecosystem: nix
mechanism_family: pointer-identity, bind-temporary, silent-skip

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "prefetch_failing.cc": """// Reduced excerpt on failing_ref
// src/nix/flake-prefetch-inputs.cc

struct State { std::set<const Node *> done; };
Sync<State> state_;

auto visit = [&](this const auto & visit, const Node & node) {
    if (!state_.lock()->done.insert(&node).second)
        return;
    for (auto & [inputName, input] : node.inputs) {
        if (auto inputNode = std::get_if<0>(&input))
            pool.enqueue(std::bind(visit, **inputNode));
    }
};

pool.enqueue(std::bind(visit, *flake.lockFile.root));
pool.process();
throw Exit(nrFailed ? 1 : 0);
""",
        "observed_counts.txt": """lock nodes: 232
unique inputs: 170
fetching activities: ~150
missing set: different each run
exit: 0
""",
    },
)


def next_free_ids(n: int, start: int = 61) -> list[str]:
    """Allocate unused specimen-NNN ids at or after start. Never reuse existing."""
    ids: list[str] = []
    i = start
    while len(ids) < n:
        spec_id = f"specimen-{i:03d}"
        if not (SPECIMENS / spec_id).exists():
            ids.append(spec_id)
        i += 1
        if i > 999:
            raise SystemExit("no free specimen ids")
    return ids


def main() -> None:
    written = []
    allocated = next_free_ids(len(PACKETS), start=61)
    for spec_id, packet in zip(allocated, PACKETS, strict=True):
        old = packet["id"]
        packet["id"] = spec_id
        packet["manifest"] = packet["manifest"].replace(f"id: {old}", f"id: {spec_id}", 1)
        dest = SPECIMENS / spec_id
        if dest.exists():
            raise SystemExit(f"refusing to overwrite {dest}")
        emit(packet)
        seed = write_seed(dest)
        written.append((dest, seed))
        print(dest)
        print(seed)
    update_index()
    print(f"count={len(written)}")


if __name__ == "__main__":
    main()
