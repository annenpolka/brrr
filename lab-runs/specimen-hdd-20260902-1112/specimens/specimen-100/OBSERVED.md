# OBSERVED

Public oven-sh/bun issue 21852 (Ant59, closed 2026-07-29) and PR 36304 (robobun, merged 2026-07-29, squash `079d1d345fd1e9fc54b4e0bd36a0ce57fdcf0a48`). Failing world pinned on squash first parent `b4ee407a256ac2e4f4f3a5419387b43815cf6be7`. Related: #23739 (`-r` from root). Local bun execution was not performed on this lab host.

Issue body: Bun 1.2.20 `bun update` overwrote `catalog:` references in subpackages with literal versions (e.g. `^5.9.2`). Catalog versions in the root were not updated. Interactive update already behaved.

PR body (failing shape only): `edit_update_no_args` iterates four dependency groups of the current package.json and never looks at `catalog` / `catalogs`. Encountering `catalog:` (run from a workspace package) registers it in `updating_packages` and writes the resolved range over the `catalog:` literal.

In-tree tests for the update leftover (`describe("update")` in `catalogs.test.ts`) are **not** on the failing revision. Pre-existing `describe("basic")` catalog install tests are.

Not this packet: specimen-082 (optional-peer `packages` leftover after `bun remove`). specimen-004 / 033 / 095 npm peers/overrides. yarn 089 PnP.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
