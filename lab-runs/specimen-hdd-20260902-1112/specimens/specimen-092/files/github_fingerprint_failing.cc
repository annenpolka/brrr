// Reduced excerpt of GitArchiveInputScheme::getFingerprint
// src/libfetchers/github.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Fingerprint is the git rev. narHash is not in the key.

    std::optional<std::string> getFingerprint(Store & store, const Input & input) const override
    {
        if (auto rev = input.getRev())
            return rev->gitRev();
        else
            return std::nullopt;
    }
