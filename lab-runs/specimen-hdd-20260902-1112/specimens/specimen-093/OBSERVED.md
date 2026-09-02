# OBSERVED

Public evanw/esbuild issue 2071 (somebee, opened 2022-03-02, closed 2022-12-14). Public PR 2091 (haikyuu; closed not merged). Failing world: parent `0e126570c91f4f4a85a43be1a6b9fd7ba7ebb6ff`. Fix commit `a375b372f5a4947c3e7d2af68301190a88bf83cd` (`fix #2071: remap bytesInOutput for substitutions; closes #2091`).

Issue body (failing observables):

> When you supply a `publicPath`, the bytesInOutput value is incorrect for css files. … `bytesInOutput` of styles.css is shorter than the real output, as it does not include the `/some-long-public-path` in the calculation.

Follow-up (still failing, no publicPath required):

> `bytesInOutput` is actually incorrect whether you supply a `publicPath` or not. As long as you have a `url(...)` somewhere in your css that imports a path using file-loader. … The `bytesInOutput` are not at all affected by `--asset-names`, `--public-path` or any other option that ends up changing the urls in the output css.

Reporter: introduced in v0.12.12; not present on v0.9.7. Minimal repo `somebee/esbuild-bytes-offset-bug`.

PR 2091 body (failing identity):

> Bytes in output is based on `len(compileResult.CSS)` which is the result of the printer. And it includes the hash inside the url instead of the actual path. Example: `div{ background: url(hashthats25characterslong); }`

In-tree on the failing revision, `generateChunkCSS` records:

```
jMeta.AddString(fmt.Sprintf("... \"bytesInOutput\": %d ...",
    len(compileResult.CSS)))
```

`compileResult.CSS` still contains `url(<uniqueKey>)`. Path substitution (`substituteFinalPaths` / `breakOutputIntoPieces`) runs later for the written file and for `outputs.*.bytes`. `jsonMetadataChunkCallback` only receives `finalOutputSize` for the outer `bytes` field. `bytesInOutput` is not remapped.

Snapshot `TestMetafileVeryLongExternalPaths` on failing_ref, CSS output:

```
"out/bytesInOutput should be at least 99.css": {
  "inputs": {
    "project/bytesInOutput should be at least 99.css": {
      "bytesInOutput": 52
    }
  },
  "bytes": 196
}
```

JS file-loader sibling on the same snapshot: `"bytesInOutput": 45` for the 99-char `.file` inside the JS output (leftover uniqueKey in `len(compileResult.JS)`).

This packet is not webpack/webpack#20938 / specimen-090 (CSS module `[contenthash]` leftover after a referenced PNG filename moves; `realContentHash: false`). Not esbuild PR 504 (CSS-from-JS stub leftover in `metafile.inputs` producing invalid JSON). Not #1357 (CLI `--metafile` omitted on watch rebuilds). Not #1186 (plugin `onEnd` metafile undefined after first watch build).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
