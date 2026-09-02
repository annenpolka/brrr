# OBSERVED

Public Homebrew/brew#23588 (closed 2026-08-20; PR merged 2026-08-21). PR 23597 merge `b62af44bc2d4173d113d07648eb78a9facb73fcf` (first parent `4f6e4df964fa22f12591ca4b27e9b52df34b9494`). Local brew was not performed on this lab host.

Issue body: test-bot used a bottle from cache even though a local patch file changed without modifying the formula.

On failing_ref, `no_diff?` only passes `formula.path`. `formula.patchlist.grep(LocalPatch)` is **not** part of the cache identity.

Not this packet: Homebrew#20936 formula_auditor revision/compatibility_version (job-0539 skip axis). Distinct leftover: bottle cache identity omits local patch files so leftover previous bottle is reused after patch change.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
