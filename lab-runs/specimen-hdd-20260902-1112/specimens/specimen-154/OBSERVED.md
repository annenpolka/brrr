# OBSERVED

Public elixir-lang/elixir#11080 (merged 2021-06-28). Squash `350a909eb195ab1c0bc5ad29b7573c36ebd98377` (parent `a677d3c9efb32fe435d8fd102eb8f90272e14da1`). Local elixir/mix was not performed on this lab host.

PR body: hashing content is the right check; tests were added for same-length content change vs identical files with bumped mtime.

On failing_ref, the source record has size not digest. Stale detection is size inequality or Mix.Utils.stale? on mtimes. Same-length rewrite can keep leftover previous modules.

Not this packet: specimen-054 cpython generated-header drift. specimen-086 cargo rustc fingerprint clamped mtime. specimen-147 CDK truncated mtime fingerprint.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
