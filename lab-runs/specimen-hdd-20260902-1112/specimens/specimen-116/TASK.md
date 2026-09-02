# TASK

Coder's diff highlighter can keep the identity of a **filename-keyed highlight AST** after a later edit of the same path has a different patch body. `@pierre/diffs` keys its worker-pool cache by `cacheKey`, which the components default to the file name when unset. Leftover AST from the first diff is reused for the second; rendering throws `deletionLine and additionLine are null`.

On failing_ref `9a57dfa6424996d92daa18a8a5b96efcb1576a1a`, `parsePatchFiles` is called without a content key. Parsed `FileDiffMetadata` has no `cacheKey`. The library assigns `cacheKey = fileDiff.name`. Two consecutive `edit_files` turns on one path share leftover highlight identity.

Public report (coder/coder#27987): two user-visible bugs from `@pierre/diffs` 1.3.x (#27932) keying the singleton worker-pool highlight cache by filename:

1. Stale-AST crash: two different diff bodies for the same path shared one cache entry.
2. Truncated synthetic diffs: N same-name file entries kept entry one.

`RemoteDiffPanel` already used a timestamp-scoped prefix; chat tool renderers and `LocalDiffPanel` parsed without one.

In-tree after the repair (not on failing_ref): `parseDiffString` stamps `cacheKey` with `getContentCacheKey` (FNV-1a of name, prevName, lang, hunks, line arrays). Unchanged files hit; changed files miss.

Case A — first diff of path `foo.ts`:
  highlight AST stored under filename
  not leftover yet

Case B — second diff of `foo.ts` with different hunks, leftover cache:
  leftover: stale AST of first body
  crash on shorter additionLines/deletionLines

Case C — content-derived cacheKey (post-repair shape, not on failing_ref):
  miss
  not leftover filename identity

Case D — different path:
  unique filename key
  not this leftover

The developer wants to know which identity case B actually left in the highlight cache: leftover first-body AST for `foo.ts`, content-keyed miss, or omitted (no cache entry).
