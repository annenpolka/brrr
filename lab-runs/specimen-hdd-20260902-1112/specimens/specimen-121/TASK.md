# TASK

SwiftPM's in-memory registry metadata cache can keep the identity of a **previous version's checksum** after a later resolve of a new version should fetch that version's metadata. `MetadataCacheKey` is `(registry, package)` — version is omitted. The TTL predicate is inverted (`cached.expires < .now()`), so the cache is used only *after* the 60-minute TTL, which is when a new release is most likely.

On failing_ref `d8ae00bc06a6c5f643d5b843537a8118766c3c7c`, `_getRawPackageVersionMetadata` is:

```
let cacheKey = MetadataCacheKey(registry: registry, package: package)
if let cached = self.metadataCache[cacheKey], cached.expires < .now() {
    return cached.metadata
}
```

`metadataCacheTTL` is 60*60 seconds. After expiry, leftover metadata (including checksum) is returned for any version of that package. `ChecksumTOFU.getExpectedChecksum` then `writeToStorage` that leftover checksum as the fingerprint for the *new* version under `~/Library/org.swift.swiftpm/security/fingerprints/`.

Public report (swiftlang/swift-package-manager#9144 / related #8981):

1. Keep Xcode / libSwiftPM open ≥ 1 hour after a resolve (cache populated).
2. Publish a new package version to the registry.
3. Resolve the new version.
4. Leftover: previous checksum fingerprint is stored for the new version.
5. `swift package resolve` then fails:

```
invalid registry source archive checksum 'newchecksum', expected 'previouschecksum'
```

Workaround: purge fingerprint storage. Cherry-pick of the same repair is PR 9210 on `release/6.2`.

In-tree after the repair (not on failing_ref): `MetadataCacheKey` includes `version`; predicate is `cached.expires > .now()`; test `getPackageVersionMetadataInCache` fetches 1.1.1 then 1.1.0 as distinct keys.

Case A — first fetch of version 1.1.0 within TTL:
  inverted predicate does *not* return cache
  network fetch
  not leftover (fresh metadata written)

Case B — after TTL, fetch of new version 1.1.1 with leftover cache of 1.1.0:
  leftover: 1.1.0 metadata (checksum) reused as 1.1.1
  version omitted from MetadataCacheKey
  TOFU writes previouschecksum for 1.1.1

Case C — version included in the cache key (post-repair shape, not on failing_ref):
  miss
  not leftover previous-version identity

Case D — delete fingerprint storage then resolve:
  fresh TOFU identity
  not leftover on-disk fingerprint

The developer wants to know which identity case B actually left in fingerprint storage for 1.1.1: leftover previouschecksum of 1.1.0, newchecksum of 1.1.1, or omitted (no fingerprint file).
