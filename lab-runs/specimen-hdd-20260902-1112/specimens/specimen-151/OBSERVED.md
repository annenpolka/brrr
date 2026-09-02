# OBSERVED

Public objectionary/eo#7628 (closed 2026-08-26). PR 7675 merge `34df04c9a5eb26c6718c9512d930c4653627d70f` (first parent `09ba1e478be7e2ef4fd1293828512ef9d05f38e6`). Local eo was not performed on this lab host.

Issue body: `-Deo.trackSteps=true` writes intermediate XMIRs only on a cache miss; the flag is not part of the cache key. A build that had it off leaves a cached result that a later build with it on takes as it is, producing no step files. Shared-cache BUILD B step files 0; private-cache CONTROL step files 10.

On failing_ref, `Transpilation.version()` formats plugin version, XSL fingerprint, locations(), coverage, superclass. `tracking.steps()` is read only when constructing the Xsline, after the cache lookup.

Not this packet: specimen-117 sbt leftover last-write zinc Analysis. specimen-075 rustc incremental fingerprint. specimen-148 buildah leftover RUN --mount from-stage.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
