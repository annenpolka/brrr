// Reduced excerpt of Input::getAccessorUnchecked substitution fast path
// src/libfetchers/fetchers.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Store path from narHash. Cache fingerprint from getFingerprint (rev).

    if (isFinal() && getNarHash()) {
        try {
            auto storePath = computeStorePath(store);

            store.ensurePath(storePath);

            debug("using substituted/cached input '%s' in '%s'", to_string(), store.printStorePath(storePath));

            auto accessor = store.requireStoreObjectAccessor(storePath);

            accessor->fingerprint = getFingerprint(store);

            if (accessor->fingerprint) {
                settings.getCache()->upsert(
                    makeSourcePathToHashCacheKey(
                        *accessor->fingerprint, ContentAddressMethod::Raw::NixArchive, CanonPath::root),
                    {{"hash", store.queryPathInfo(storePath)->narHash.to_string(HashFormat::SRI, true)}});
            }

            accessor->setPathDisplay("«" + to_string() + "»");

            return {accessor, *this};
        } catch (Error & e) {
            debug("substitution of input '%s' failed: %s", to_string(), e.what());
        }
    }
