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
