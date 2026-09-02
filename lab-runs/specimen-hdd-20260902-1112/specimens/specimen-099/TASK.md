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
