# TASK

`pdm lock --update-reuse` of a project that names a **local path extra** can rewrite that extra's lock identity from a portable `${PROJECT_ROOT}` URL to a **machine-absolute `file:///` URL**, even when the lock `path` field stays relative.

Public report (pdm-project/pdm#2852). Monorepo:

```
my-repo/
  app/   pyproject + pdm.lock   depends on "lib[test] @ file:///${PROJECT_ROOT}/../lib"
  lib/   pyproject
```

On failing_ref `cc17967ace76ff2fdf455106a6eb26da50685260`, first `pdm lock` writes:

```
[[package]]
name = "lib"
version = "0.1.0"
extras = ["test"]
path = "../lib"
dependencies = [
    "lib @ file:///${PROJECT_ROOT}/../lib",
    "pytest",
]
```

Immediately afterwards, `pdm lock --update-reuse` rewrites the extra line to an expanded absolute URL:

```
    "lib @ file:///mnt/c/pdm-minimal/lib",
```

`format_lockfile` only attempted `relative_to(project.root)` when `FileRequirement.path` was already absolute. Extra-require handling mutated the shared `install_requires` list (`self._data.install_requires` without a copy), so a later reuse pass saw a different URL identity than the first lock.

Case A — no extras, only a path dep `lib @ file:///${PROJECT_ROOT}/../lib`:
  `--update-reuse` keeps the variable URL
  no leftover expansion

Case B — extra `lib[test]` path dep, `pdm lock` then `pdm lock --update-reuse`:
  first lock: portable `${PROJECT_ROOT}` URL + relative `path`
  failing_ref reuse: leftover absolute `file:///...` URL next to the same relative `path`
  leftover identity: expanded URL vs portable PROJECT_ROOT URL

Case C — extra deps that are registry names (pytest), not path:
  no file URL to expand
  not this leftover

Case D — `pdm lock` without `--update-reuse` after a clean tree:
  first-write identity only
  not the reuse leftover

The developer wants to know which identity case B actually stored for the extra path dep after `--update-reuse`: leftover expanded absolute URL, the portable `${PROJECT_ROOT}` URL, or omitted.
