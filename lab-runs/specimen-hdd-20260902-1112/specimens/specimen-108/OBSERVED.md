# OBSERVED

Public npm/cli#9613 (closed 2026-06-24). PR 9632 merge `981e2498589c83859b3c9e8b92a2cc67562dc06b` (single parent / squash `696801574984ad19ffaa9a7200d7e752920a018d`). Part of #9608 linked-strategy leftovers. Local npm was not performed on this lab host.

PR body: under linked, uninstall removed the top-level symlink and `.store` entry but left the shim in `node_modules/.bin` as a dangling link. The leftover shim can break tools that enumerate `.bin`, shadow a later-installed binary of the same name, and is not healed by a subsequent `npm install`. Hoisted removes the `.bin` entry.

On failing_ref, `#cleanOrphanedStoreEntries` collects valid store keys and valid top-level link names, then `#cleanOrphanedTopLevelLinks` removes orphaned symlinks whose names do not start with `.`. `.bin` is skipped as an npm-managed dot-entry. No `binsByDir` / `#cleanStaleBinLinks`.

`#cleanStaleBinLinks` is **not** on the failing revision. It is added by PR 9632: while collecting valid top-level links, record `child.package.bin` names per `node_modules` dir; then remove `.bin` entries whose base name (after stripping `.cmd`/`.ps1`) is not provided by a surviving package, or which are dangling symlinks.

Not this packet: specimen-004 / specimen-033 (npm optional-peer leftover). specimen-082 (bun optional-peer leftover / Honor-KILL peerleft). specimen-095 (npm nested-override leftover / Honor-KILL overleft). specimen-089 (yarn leftover PnP build state). job-0394/0419 npm peer leftover (duplicate 004/082/095).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
