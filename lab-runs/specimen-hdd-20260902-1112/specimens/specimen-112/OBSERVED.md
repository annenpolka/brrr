# OBSERVED

Public composer/composer#12417 (closed 2025-09-18). PR 12423 squash `1a22bb197a6e62ca431928627ef232bd4d335097` (parent `aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8`). Local composer was not performed on this lab host.

Issue body: lock gained `"abandoned": true` after Packagist tagged the already-installed package. installed.json omitted abandoned. audit read installed.json and reported none. Wipe vendor + install healed it.

On failing_ref, calculateOperations compares version / dist-ref / source-ref only. Abandoned and replacement-package are not that identity. Same-version leftover vendor is not an UpdateOperation.

`isAbandoned()` / `getReplacementPackage()` on CompletePackageInterface are **not** on the failing revision's update predicate. They are added by PR 12423.

Not this packet: specimen-074 (rubygems platform-fallback extra). specimen-021 (poetry lock leftover). specimen-086 (cargo rustc-fingerprint metadata). emit_086 composer classmap leftover was not the claimed 086 packet (086 is cargo). job-0458 hunt was installed.json vs lock, not classmap.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
