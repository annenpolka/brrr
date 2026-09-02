KNOWN FIX (sealed): composer/composer PR 12423 squash 1a22bb197a6e62ca431928627ef232bd4d335097.

failing_ref is squash parent 8fc94c5e9972d2ebb87e57711a8477392b30f299.

calculateOperations treated leftover installed.json as current identity using version/dist/source refs only. Same-version abandoned-state change never scheduled UpdateOperation, so installed.json kept the old (or omitted) abandoned identity while lock had the new one. composer audit reads installed.json.

PR repair: also compare CompletePackageInterface isAbandoned() and getReplacementPackage(); mismatch schedules UpdateOperation (reinstall same version) so installed.json syncs.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
