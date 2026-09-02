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
