# OBSERVED

Public rust-lang/cargo#7987 / PR 16246 (avnyu; squash-merge `0101bde5602af3625c2014fec9b0c497b3e7ef1f`, 2025-12-14). Failing world pinned on merge first parent `e91b2baa632c0c7e84216c91ecfe107c37d887c1`. Local cargo execution was not performed on this lab host.

PR continues #10279. Moves git db creation into `GitSource::fetch_db`. Submodules become `GitSource` + `fetch_db` + `db.copy_to`. Recursive `update_submodules` after reset is removed because `copy_to` already recurses.

On failing_ref, `update_submodule` after init/open:
```
fetch(&mut repo, &child_remote_url, &reference, gctx, RemoteKind::GitDependency)
let obj = repo.find_object(head, None)?;
reset(&repo, &obj, gctx)?;
update_submodules(&repo, gctx, &child_remote_url)
```
No `git/db` ident for the child URL.

In-tree `dep_with_cached_submodule` (two parents, one shared submodule; assert one `git/db/dep3-*`) is **not** on the failing revision. `dep_with_submodule` after the repair asserts submodule db created once.

Not this packet: specimen-091 (cargo git checkout PathBuf `..`). specimen-007 (libgit2). cargo#17289 (checkout short-id vs core.abbrev). silentadd (git index leftover).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
