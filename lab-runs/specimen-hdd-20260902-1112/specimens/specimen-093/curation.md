ACCEPT_R1

contrastiveness: high (never-url'd CSS moves bytesInOutput with source vs url()+file-loader leftover uniqueKey vs publicPath/long asset-names substituted bytes; outputs.bytes remapped vs inputs.bytesInOutput leftover; JS file-loader vs CSS url-token)
reproducibility: source-backed issue + public PR + pinned parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — two metafile stores disagree after substitution; uniqueKey length vs final hashed path; publicPath is config but still appears in written CSS
ecosystem: esbuild / css / file-loader
mechanism_family: leftover-uniquekey-identity, metafile-bytesInOutput, css-url-file-loader

Packet is the failing world only. Do not assume a root cause.
