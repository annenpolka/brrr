// Reduced excerpt of GitInputScheme::getFingerprint
// src/libfetchers/git.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Still rev-based. Optional suffixes for submodules / exportIgnore / lfs.
// narHash is not in the key.

    std::optional<std::string> getFingerprint(Store & store, const Input & input) const override
    {
        auto makeFingerprint = [&](const Hash & rev) {
            return rev.gitRev() + (getSubmodulesAttr(input) ? ";s" : "") + (getExportIgnoreAttr(input) ? ";e" : "")
                   + (getLfsAttr(input) ? ";l" : "");
        };

        if (auto rev = input.getRev())
            return makeFingerprint(*rev);
        // ... dirty-workdir branch omitted ...
        return std::nullopt;
    }
