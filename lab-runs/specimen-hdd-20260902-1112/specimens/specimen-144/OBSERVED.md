# OBSERVED

Public GoogleContainerTools/skaffold#9248 (closed 2024-01-31) and #9279 (closed as the same lookupRemote leftover). PR 9278 squash `9ff4546df8c0d891fde32c24e0d0ef93a8c7404b` (parent `6ea9aeb818b8e371a4386bf044479f86a0a6e885`). Local skaffold was not performed on this lab host.

Issue #9279: bazel/docker artifacts; input files change; `skaffold build` still returns the previous image; `Found Remotely` after Dockerfile `RUN ls`; `--cache-artifacts=false` updates hashes.

On failing_ref, lookupRemote treats a live remote tag as a cache hit for the current input hash without comparing digests.

Not this packet: specimen-097 buildkit leftover git-dir cache key omitting ref. specimen-136 pants leftover process cache vs git hash.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
