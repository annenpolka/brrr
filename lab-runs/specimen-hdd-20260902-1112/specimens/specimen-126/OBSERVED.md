# OBSERVED

Public npm/cli#9659 (closed 2026-06-26). PR 9671 squash `968e42fbd62eb3a6f446466359c9431f41d76b2b` (parent `ae6dbeb12a6f4b313a28c99068e34ba834ae91d1`). Local npm was not performed on this lab host.

Issue body: root override targeting a transitive dep is silently ignored when the path crosses a file:/workspace link; lock pins the original version; no warning.

On failing_ref, Link target is queued without forwarding OverrideSet. `#repropagateOverrides` exists for store links (#9619) but runs too early for a file: link whose subtree resolves late. Forward-before-queue is **not** on the failing revision. It is added by PR 9671.

Not this packet: specimen-004/033 optional-peer leftover (npm/cli#9876). specimen-095 nested override honored only on empty-store first install; subsequent install leftover original via addEdgeIn overwrite (npm/cli#5850). npm/cli#8986 leftover after deleting overrides (open). specimen-123/124 earthly leftover CACHE --id.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
