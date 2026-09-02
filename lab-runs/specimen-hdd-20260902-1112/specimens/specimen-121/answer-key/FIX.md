KNOWN FIX (sealed): swiftlang/swift-package-manager PR 9144 squash 1abd9a2f87e568fdfa67bd4564cea65872aaeaac.

failing_ref is squash parent d8ae00bc06a6c5f643d5b843537a8118766c3c7c.

MetadataCacheKey omitted version; inverted expires < now returned leftover metadata after TTL; ChecksumTOFU wrote that leftover checksum as the new version's fingerprint.

PR repair: add version to MetadataCacheKey; use expires > now; cherry-pick PR 9210 onto release/6.2.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
