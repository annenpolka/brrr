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
