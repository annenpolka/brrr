KNOWN FIX (sealed): composer/composer PR 12423 squash 1a22bb197a6e62ca431928627ef232bd4d335097.

failing_ref is squash parent aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8.

calculateOperations treated leftover same-version vendor as identity and skipped reinstall when only abandoned/replacement changed.

PR repair: also compare isAbandoned() and getReplacementPackage() on CompletePackageInterface; same-version abandon change is UpdateOperation and rewrites installed.json.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
