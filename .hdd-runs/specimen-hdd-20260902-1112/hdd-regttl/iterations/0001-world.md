# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public swiftlang/swift-package-manager PR 9144 (merged 2025-09-29) squash `1abd9a2f87e568fdfa67bd4564cea65872aaeaac` (parent `d8ae00bc06a6c5f643d5b843537a8118766c3c7c`). Cherry-pick PR 9210 onto `release/6.2`. Related issue #8981. Local SwiftPM was not performed on this lab host.

PR body: inverted `expires < now` means the cache is used only after TTL. MetadataCacheKey omits version, so leftover checksum of the previous release is written as TOFU fingerprint for the new release.

On failing_ref, `_getRawPackageVersionMetadata` keys only registry+package. Version is a function argument used to build the HTTP URL, not the cache key. `ChecksumTOFU.writeToStorage` records whatever checksum that leftover metadata supplied.

Including `version` on MetadataCacheKey and reversing the TTL predicate are **not** on the failing revision. They are added by PR 9144.

Not this packet: specimen-075 (rustc incremental fingerprint). specimen-086 (cargo rustc extra-filename). specimen-115 (go-task wildcard checksum omitting MATCH).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref d8ae00bc06a6c5f643d5b843537a8118766c3c7c
# Sources/PackageRegistry/RegistryClient.swift _getRawPackageVersionMetadata
# Sources/PackageRegistry/ChecksumTOFU.swift writeToStorage

# public shape:
# leftover metadataCache[registry,package] after TTL
# new version resolve writes previouschecksum into fingerprints/
# invalid registry source archive checksum 'newchecksum', expected 'previouschecksum'
```

Source-backed only. Do not execute untrusted checkouts on the host.

swiftlang/swift-package-manager
  Sources/PackageRegistry/RegistryClient.swift
  Sources/PackageRegistry/ChecksumTOFU.swift
  Tests/PackageRegistryTests/RegistryClientTests.swift
  ~/Library/org.swift.swiftpm/security/fingerprints/

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  in-memory metadataCache
  ChecksumTOFU fingerprints/ for new version
  leftover previouschecksum after TTL

Case A (first fetch 1.1.0 within TTL):
  inverted predicate misses
  network fetch
  not leftover

Case B (after TTL, fetch 1.1.1, leftover 1.1.0 cache):
  leftover: 1.1.0 metadata reused
  TOFU writes previouschecksum for 1.1.1
  invalid registry source archive checksum

Case C (version on MetadataCacheKey):
  miss
  not leftover previous-version identity

Case D (delete fingerprints/):
  fresh TOFU identity
  not leftover on-disk fingerprint

Not this packet:
  rustc incremental fingerprint (specimen-075)
  cargo rustc extra-filename (specimen-086)
  go-task leftover wildcard MATCH (specimen-115)

### metadata_cache_key_failing.swift

// Reduced excerpt of _getRawPackageVersionMetadata on failing_ref
// Sources/PackageRegistry/RegistryClient.swift
// d8ae00bc06a6c5f643d5b843537a8118766c3c7c
// Cache key is registry+package. Version is omitted.
// Predicate uses expires < now (inverted TTL).

        let cacheKey = MetadataCacheKey(registry: registry, package: package)
        if let cached = self.metadataCache[cacheKey], cached.expires < .now() {
            return cached.metadata
        }
        // HTTP GET .../scope/name/version
        // on 200:
        self.metadataCache[cacheKey] = (metadata: metadata, expires: .now() + Self.metadataCacheTTL)

    private struct MetadataCacheKey: Hashable {
        let registry: Registry
        let package: PackageIdentity.RegistryIdentity
        // no version
    }

    private static let metadataCacheTTL: DispatchTimeInterval = .seconds(60 * 60)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
