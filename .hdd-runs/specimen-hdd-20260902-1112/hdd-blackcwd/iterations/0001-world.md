# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

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

# OBSERVED

Public psf/black PR 5152 squash `d246367ab471cd56298407858661d475c33b3e36` (parent `c77093e228ff21a93638b42356aa0a4d2713aa17`). Local black was not performed on this lab host.

PR body: when `srcs` is empty (`black --code`), `find_project_root` fell back to `os.getcwd()` inside `@lru_cache`. Cache key is only `(srcs, stdin_filename)`. Two calls from different directories with `srcs=()` share the leftover entry.

On failing_ref, `@lru_cache` sits on `find_project_root`. Resolved CWD is **not** part of the key. `_find_project_root_cached` is added by PR 5152.

Not this packet: specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files. specimen-132 eslint leftover plugin name@version omitted from toJSON.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref c77093e228ff21a93638b42356aa0a4d2713aa17
# src/black/files.py find_project_root @lru_cache

# public shape:
# leftover project root after black --code from a different CWD
# cache key omits resolved CWD when srcs is empty
# wrong pyproject.toml [tool.black]
```

Source-backed only. Do not execute untrusted checkouts on the host.

psf/black
  src/black/files.py
  tests/test_black.py
  pyproject.toml

RELEVANT MATERIAL

### find_project_root_failing.py

# Reduced excerpt of find_project_root on failing_ref
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

### leftover_identity_split.txt

Registry / fixture:
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

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
