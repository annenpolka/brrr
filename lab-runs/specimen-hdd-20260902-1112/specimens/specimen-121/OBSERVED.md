# OBSERVED

Public swiftlang/swift-package-manager PR 9144 (merged 2025-09-29) squash `1abd9a2f87e568fdfa67bd4564cea65872aaeaac` (parent `d8ae00bc06a6c5f643d5b843537a8118766c3c7c`). Cherry-pick PR 9210 onto `release/6.2`. Related issue #8981. Local SwiftPM was not performed on this lab host.

PR body: inverted `expires < now` means the cache is used only after TTL. MetadataCacheKey omits version, so leftover checksum of the previous release is written as TOFU fingerprint for the new release.

On failing_ref, `_getRawPackageVersionMetadata` keys only registry+package. Version is a function argument used to build the HTTP URL, not the cache key. `ChecksumTOFU.writeToStorage` records whatever checksum that leftover metadata supplied.

Including `version` on MetadataCacheKey and reversing the TTL predicate are **not** on the failing revision. They are added by PR 9144.

Not this packet: specimen-075 (rustc incremental fingerprint). specimen-086 (cargo rustc extra-filename). specimen-115 (go-task wildcard checksum omitting MATCH).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
