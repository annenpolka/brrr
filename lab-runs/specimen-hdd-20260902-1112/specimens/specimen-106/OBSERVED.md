# OBSERVED

Public pdm-project/pdm#2852 closed 2024-05-08. PR 2874 merge `931de2106b37e8dc55efb84de6bf7a704ad28842` (parent `cc17967ace76ff2fdf455106a6eb26da50685260`). Title: keep `${PROJECT_ROOT}` after `pdm lock --update-reuse`. Local PDM execution was not performed on this lab host.

On failing_ref, `format_lockfile` (src/pdm/cli/utils.py):

```
if isinstance(r, FileRequirement) and r.path and r.path.is_absolute():
    try:
        r.path = Path(os.path.normpath(r.path)).relative_to(os.path.normpath(project.root))
        r.url = backend.relative_path_to_url(r.path.as_posix())
    except ValueError:
        pass
```

Relative `path = "../lib"` skipped the rewrite. Extra-require assembly used `result = self._data.install_requires` (same list object) then appended extras, so reuse could emit an expanded URL while `path` stayed relative.

News file `news/2852.bugfix.md` is **absent** on `cc17967ace76ff2fdf455106a6eb26da50685260`. It is added by PR 2874.

Not this packet: specimen-006/022/023/102 (uv git vs directory source kinds / Poetry path inside git checkout). specimen-021 (poetry extras). specimen-031/098 (pip extras-on-link).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
