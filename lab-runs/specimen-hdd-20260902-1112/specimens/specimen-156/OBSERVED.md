# OBSERVED

Public oven-sh/bun#40971 (merged 2026-08-30). Squash `9439a2432e5dc5ad49ce243fcba257baa2acc3db` (parent `b5d0bbc0edd90c46b29eb8273bc272a7042e584b`). Local bun was not performed on this lab host.

PR body: bun run ./a.ts with bunfig [define] serves stale output after the value changes. A second project with the same source bytes gets the first project's values. Cause: cache key is source bytes plus a features hash that never covered the define table. --drop has the same hole.

On failing_ref, hash_for_runtime_transpiler hashes 17 bools, react_compiler, and --feature flags. define_hash does not exist. VERSION 27.

Not this packet: specimen-082 bun optional-peer leftover in lockfile. specimen-090 webpack leftover contenthash. specimen-151 eo leftover transpile vs omitted trackSteps.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
