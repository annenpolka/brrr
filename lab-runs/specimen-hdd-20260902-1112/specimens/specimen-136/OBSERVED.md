# OBSERVED

Public pantsbuild/pants#16963 (closed 2022-09-27). PR 17017 merge `510f1755680d23c3d6c68815ae77ad4a4f836021` (parent `02fa93e2947789cf1f9f8c025e7ceaca01169ef2`). Local pants was not performed on this lab host.

Issue body: generated version string cached and not invalidated after amend/commit; deleting `~/.cache/pants` restores the current git describe. Maintainer: MaybeGitWorktree is uncacheable so the enclosing rule always runs; the underlying setuptools_scm process was still memoized.

On failing_ref, `VenvPexProcess` has no `cache_scope`. `ProcessCacheScope` is **not** imported on the failing revision. It is added by PR 17017.

Not this packet: specimen-075 rustc incremental false-green / next-solver anon-task. pants#23645 leftover process cache vs env is still OPEN (env without cache key). pants#18334 is process metadata, not leftover cache identity.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
