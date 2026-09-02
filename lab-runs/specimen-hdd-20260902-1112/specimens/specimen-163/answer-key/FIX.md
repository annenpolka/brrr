KNOWN FIX (sealed): JetBrains/kotlin PR 6654 squash 0a61a56593a0d6270e6e5f66d0fd31c2209429ed.

failing_ref is parent a05299825cbf5d5e19df97bd7f8ec00a98716871.

CacheMetadata stored compilerFingerprint only. Dirty-file IR hashes did not see an external dep rollback to an already-cached version. Leftover previous IC cache HIT.

PR repair: store and compare dependenciesFingerprint; rebuild when it mismatches or metadata is absent.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
