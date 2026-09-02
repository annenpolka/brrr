# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Cargo git dependencies with submodules can fetch a submodule into the **checkout** without a `$CARGO_HOME/git/db/<ident>` database. A second git dependency that shares that submodule URL then fetches again. After `rm -rf $CARGO_HOME/git/checkouts`, `--offline` fetch cannot reconstruct the submodule from git db.

On failing_ref `e91b2baa632c0c7e84216c91ecfe107c37d887c1`, `GitCheckout::update_submodule` does `fetch` + `reset` into the submodule working copy. It does not go through `GitSource` / `GitDatabase`. Parent git deps use `git/db`; nested submodules do not.

Case A — git dependency **without** submodules:
  `$CARGO_HOME/git/db/<dep-ident>` exists after fetch
  checkout is a copy from that db
  offline refetch after deleting checkouts can use the db

Case B — two git deps (`dep1`, `dep2`) each with the **same** submodule URL (`dep3` at `src/`):
  failing_ref: submodule fetch is per-checkout `git submodule` style
  `$CARGO_HOME/git/db` may lack a `dep3-*` entry, or each parent re-fetches the submodule network
  in-tree after the repair: `dep_with_cached_submodule` asserts `git/db/dep3-*` created once

Case C — `cargo fetch --locked` then `rm -rf git/checkouts` then `cargo fetch --offline`:
  failing_ref: submodule object not in db; offline cannot copy_to
  public #7987: submodules not cached like the parent git db

Case D — submodule already at `head_id` matching the recorded SHA:
  failing_ref still recurses `update_submodules` on that checkout; no db write

The developer wants to know which identity cargo stored for the nested submodule: leftover checkout-only (no git/db), a git/db ident shared across parents, or omitted.

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

```
# not executed on this lab host
# failing_ref e91b2baa632c0c7e84216c91ecfe107c37d887c1
# src/cargo/sources/git/utils.rs GitCheckout::update_submodule
# src/cargo/sources/git/source.rs GitSource::update (parent uses git/db)

# public shape (#7987): git dep with submodule; second fetch of same submodule
# after rm git/checkouts, --offline cannot use a submodule db
```

Source-backed only. Do not execute untrusted checkouts on the host.

rust-lang/cargo
  src/cargo/sources/git/source.rs
  src/cargo/sources/git/utils.rs
  tests/testsuite/git.rs
  $CARGO_HOME/git/db/<ident>
  $CARGO_HOME/git/checkouts/<ident>/<short-id>/

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  parent git dep uses $CARGO_HOME/git/db/<ident>
  nested submodule URL may be shared across two parents

Case A (git dep, no submodule):
  git/db exists
  checkout copied from db
  offline after rm checkouts can use db

Case B (two git deps, same submodule URL):
  failing_ref: submodule fetch per checkout
  git/db may omit submodule ident
  leftover: checkout-only submodule identity

Case C (fetch then rm checkouts then --offline):
  failing_ref: submodule not in db; offline fail
  public #7987

Case D (submodule already at recorded head_id):
  failing_ref recurses update_submodules on that checkout
  still no db write

Not this packet:
  cargo PathBuf .. (specimen-091)
  libgit2 (specimen-007)
  silentadd git index

### update_submodule_failing.rs

// Reduced excerpt of GitCheckout::update_submodule on failing_ref
// src/cargo/sources/git/utils.rs
// e91b2baa632c0c7e84216c91ecfe107c37d887c1
// Nested submodule is fetch+reset into the checkout. No GitDatabase / git/db ident.

            let reference = GitReference::Rev(head.to_string());
            gctx.shell()
                .status("Updating", format!("git submodule `{child_remote_url}`"))?;
            fetch(
                &mut repo,
                &child_remote_url,
                &reference,
                gctx,
                RemoteKind::GitDependency,
            )?;
            let obj = repo.find_object(head, None)?;
            reset(&repo, &obj, gctx)?;
            update_submodules(&repo, gctx, &child_remote_url)

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
