// Reduced excerpt of checkFingerprint on failing_ref
// DefaultConfigurationCache.kt
// e0ca283b48bc739f14140b8a61565d689758c032
// Stored rootDirs are watchable. Build location is omitted from identity.

    private
    fun ConfigurationCacheRepository.Layout.checkFingerprint(candidateEntry: CandidateEntry, rootDirs: List<File>): CheckedFingerprint {
        // Register all included build root directories as watchable hierarchies,
        // so we can load the fingerprint for build scripts and other files from included builds
        // without violating file system invariants.
        registerWatchableBuildDirectories(rootDirs)

        val classLoaderScopesInvalidationReason = checkClassLoaderScopes()
        if (classLoaderScopesInvalidationReason != null) {
            return CheckedFingerprint.Invalid(buildPath(), classLoaderScopesInvalidationReason)
        }
        // no compare of startParameter.buildTreeRootDirectory against rootDirs
        val systemPropertiesSnapshot = System.getProperties().clone()
        return checkFingerprintAgainstLoadedProperties(candidateEntry).also { result ->
            // ...
        }
    }
