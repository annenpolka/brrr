# TASK

EOLANG `Transpilation.version()` can keep the identity of a **previous transpile-cache result** after `-Deo.trackSteps=true` should have written the intermediate XMIRs of the transpile train. The cache-key fingerprint folds plugin version, bundled XSL fingerprint, `trackLocations`, `coverage`, and superclass. `tracking.steps()` is not part of that key. A later build with the flag on takes the leftover previous no-step-files result.

On failing_ref `09ba1e478be7e2ef4fd1293828512ef9d05f38e6`:

```
String version() {
    return String.format(
        "%s-%s-%b-%b-%s",
        this.version,
        new Fingerprint(
            Stream.concat(
                Arrays.stream(Transpilation.XSLS), Arrays.stream(Transpilation.IMPORTS)
            ).toArray(String[]::new)
        ).get(),
        this.tracking.locations(), this.coverage, this.superclass
    );
}
```

`TrSpy` (the writer of step XMIRs) lives inside the transform that only runs on a cache miss. `locations()` is already in the key two fields away. `steps()` is not.

Public report (objectionary/eo#7628). Run 1 default: step files 0. Run 2 `-Deo.trackSteps=true` with shared cache: step files 0. Control with a private cache: step files 10. Warm cache of the previous no-steps identity stays current.

In-tree after the repair (not on failing_ref): `version()` folds `this.tracking.steps()` as a third boolean in the key.

Case A — second transpile, same flags, same XSL fingerprint:
  cache identity is current
  not leftover-after-flag

Case B — trackSteps flipped on, leftover cache hit:
  leftover: previous no-step-files transpile result
  steps() omitted from version() key
  shared cache

Case C — private cache / cache miss:
  fresh step XMIRs
  not leftover previous result

Case D — steps() in the cache key (post-repair shape, not on failing_ref):
  new key after trackSteps change
  not leftover previous result

The developer wants to know which identity case B actually used for the transpile output after the flag change: leftover previous-cache result (steps omitted), current step-writing transform, or omitted (no cache).
