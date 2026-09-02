# OBSERVED

Public containers/buildah#4522 (closed 2023-01-18). PR 4526 merge `3f805bcd8cd2fa522d6d2fd9ecfacf71da6aa5f9` (first parent `4f8706bb3e15a18a64567e7fc3feb9a37bc2e1a4`). Local buildah was not performed on this lab host.

Issue body: RUN --mount=from=otherstage reused from cache even though otherstage changed; resulting image still prints leftover `v1`.

On failing_ref, `runStageMountPoints` records only MountPoint. Cache lookup for the RUN step does not know the source stage was freshly executed.

Not this packet: specimen-066 moby leftover. specimen-144 skaffold leftover remote digest. specimen-097 buildkit leftover git-dir cache key omitting ref.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
