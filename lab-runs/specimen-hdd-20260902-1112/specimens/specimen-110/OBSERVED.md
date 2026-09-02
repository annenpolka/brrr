# OBSERVED

Public composer/composer#12417 (closed 2025-09-18). PR 12423 squash `1a22bb197a6e62ca431928627ef232bd4d335097` (parent `8fc94c5e9972d2ebb87e57711a8477392b30f299`). Local composer was not performed on this lab host.

Issue body: lock gained `"abandoned": true` for `behat/transliterator` v1.5.0 after Packagist marked it abandoned with no new version. `composer audit` still printed "No security vulnerability advisories found" and did not list the abandoned package. After deleting `vendor/` and reinstalling, audit listed the abandoned package. Diff of the two trees: leftover installed.json omitted `"abandoned": true` while lock had it.

On failing_ref, `Transaction::calculateOperations` compares version / dist reference / source reference only. Abandoned and replacement are not part of that present-vs-result identity. `composer audit` reads `vendor/composer/installed.json`.

Abandoned/replacement in the UpdateOperation predicate is **not** on the failing revision. It is added by PR 12423.

Not this packet: specimen-021 (poetry extras-reuse / lockfile-package). specimen-074 (rubygems platform-fallback-extra / frozen-lockfile-identity). specimen-080 (derived extra-ignores-marker). specimen-098 (pip leftover-base-without-extra).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
