# TASK

Task's checksum fingerprint can keep the identity of a **wildcard template** after two different MATCH instantiations should be different tasks. `.task/checksum/<name>` is keyed by the template name (`build-*`), so leftover checksum from `build-foo` is reused as up-to-date for `build-bar`.

On failing_ref `1e2121a99f6414e3bf4565e5736a116bef10be91`, compiled tasks keep `Task: origTask.Task` (the pattern). `Name()` / `LocalName()` do not include MATCH. `fingerprint.IsTaskUpToDate` uses that name as the cache key. Wildcard parameter is omitted from fingerprint identity.

Public report (go-task/task#1795): automatically concat the wildcard parameter on the cache key. Discussion #1794: two wildcard instantiations share one checksum.

In-tree after the repair (not on failing_ref): `FullName` replaces `*` with MATCH; `Name()` / `LocalName()` use FullName; testdata `build-*` writes `.task/checksum/build-wildcard`.

Case A — first `task build-foo` (checksum method):
  checksum written for the template name
  not leftover yet

Case B — later `task build-bar` with leftover checksum from foo:
  leftover: up-to-date identity of foo
  MATCH bar omitted from the key

Case C — non-wildcard `build` with its own checksum file:
  unique key
  not this leftover

Case D — delete `.task/checksum` then run bar:
  fresh identity
  not leftover fingerprint

The developer wants to know which identity case B actually left in `.task/checksum/`: leftover foo checksum reused as bar, separate bar checksum, or omitted (no checksum file).
