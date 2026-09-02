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
