# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public objectionary/eo#7628 (closed 2026-08-26). PR 7675 merge `34df04c9a5eb26c6718c9512d930c4653627d70f` (first parent `09ba1e478be7e2ef4fd1293828512ef9d05f38e6`). Local eo was not performed on this lab host.

Issue body: `-Deo.trackSteps=true` writes intermediate XMIRs only on a cache miss; the flag is not part of the cache key. A build that had it off leaves a cached result that a later build with it on takes as it is, producing no step files. Shared-cache BUILD B step files 0; private-cache CONTROL step files 10.

On failing_ref, `Transpilation.version()` formats plugin version, XSL fingerprint, locations(), coverage, superclass. `tracking.steps()` is read only when constructing the Xsline, after the cache lookup.

Not this packet: specimen-117 sbt leftover last-write zinc Analysis. specimen-075 rustc incremental fingerprint. specimen-148 buildah leftover RUN --mount from-stage.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 09ba1e478be7e2ef4fd1293828512ef9d05f38e6
# eo-maven-plugin Transpilation.version / tracking.steps

# public shape:
# leftover transpile cache after -Deo.trackSteps=true
# version() key omits steps(); locations() is present
# private cache / miss writes the step XMIRs
```

Source-backed only. Do not execute untrusted checkouts on the host.

objectionary/eo
  eo-maven-plugin/src/main/java/org/eolang/maven/Transpilation.java

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  EOLANG Transpilation.version() global transpile cache
  leftover no-step-files result after trackSteps=true

Case A (second transpile, same flags, same XSL fingerprint):
  current cache identity
  not leftover-after-flag

Case B (trackSteps flipped on, leftover cache hit):
  leftover: previous no-step-files transpile result
  steps() omitted from version() key
  shared cache

Case C (private cache / cache miss):
  fresh step XMIRs
  not leftover previous result

Case D (steps() in the cache key):
  new key after trackSteps change
  not leftover previous result

Not this packet:
  sbt leftover last-write zinc Analysis (specimen-117)
  rustc incremental fingerprint (specimen-075)
  buildah leftover RUN --mount from-stage (specimen-148)

### transpile_failing.java

// Reduced excerpt of Transpilation.version cache key on failing_ref
// eo-maven-plugin/src/main/java/org/eolang/maven/Transpilation.java
// 09ba1e478be7e2ef4fd1293828512ef9d05f38e6
// version() folds locations()/coverage/superclass. steps() omitted.
// leftover previous no-step-files result after -Deo.trackSteps=true.

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

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
