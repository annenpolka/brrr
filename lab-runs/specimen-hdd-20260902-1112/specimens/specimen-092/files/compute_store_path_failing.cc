// Reduced excerpt of Input::computeStorePath on failing_ref
// src/libfetchers/fetchers.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Store path identity is narHash, not rev.

StorePath Input::computeStorePath(Store & store) const
{
    auto narHash = getNarHash();
    if (!narHash)
        throw Error("cannot compute store path for unlocked input '%s'", to_string());
    return store.makeFixedOutputPath(
        getName(),
        FixedOutputInfo{
            .method = FileIngestionMethod::NixArchive,
            .hash = *narHash,
            .references = {},
        });
}
